"""OpsAgent - LangGraph based incident triage and runbook assistant."""
import os
import json
import sys
from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator

# Add the parent directory to sys.path to allow imports from tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from tools.alert_ingestion import ingest_alert
from tools.triage_classification import triage_alert
from tools.runbook_matching import match_runbooks, get_runbook_by_id
from tools.incident_updater import update_incident


# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize LLM (with fallback for testing)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "dummy":
    # Fallback: a very simple mock LLM that returns a fixed response
    from langchain_core.language_models.llms import LLM
    from langchain_core.callbacks.manager import CallbackManagerForLLMRun
    from typing import Any, List, Mapping, Optional
    class MockLLM(LLM):
        def _call(self, prompt: str, stop: Optional[List[str]] = None,
                  run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any) -> str:
            return '{"summary": "mock", "recommended_action": "investigate", "confidence": 0.8}'
        @property
        def _identifying_params(self) -> Mapping[str, Any]:
            return {}
        @property
        def _llm_type(self) -> str:
            return "mock"
    llm = MockLLM()
else:
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        api_key=api_key
    )

# Prompt templates (would be loaded from files in production)
TRIAGE_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert SRE performing alert triage.
    Given the following alert information, provide a concise triage summary:
    Alert: {alert}
    Triage data: {triage}
    Respond in JSON with keys: summary, recommended_action, confidence (0-1)."""
)

RUNBOOK_PROMPT = ChatPromptTemplate.from_template(
    """You are an SRE recommending runbooks.
    Alert: {alert}
    Available runbooks: {runbooks}
    Select the most appropriate runbook(s) and explain why.
    Respond in JSON with keys: selected_runbook_ids, reasoning."""
)

SUMMARIZATION_PROMPT = ChatPromptTemplate.from_template(
    """You are an SRE creating an incident summary.
    Alert: {alert}
    Triage: {triage}
    Runbook: {runbook}
    Actions taken: {actions}
    Create a concise incident report suitable for post-mortem.
    Respond in JSON with keys: title, timeline, root_cause, resolution, lessons_learned."""
)
# State definition

from typing import TypedDict, Dict, Any, List, Optional, Annotated

class AgentState(TypedDict, total=False):
    alert: Annotated[Dict[str, Any], lambda _, new: new]
    triage: Annotated[Dict[str, Any], lambda _, new: new]
    runbooks: Annotated[List[Dict[str, Any]], lambda _, new: new]
    selected_runbook: Annotated[Optional[Dict[str, Any]], lambda _, new: new]
    actions: Annotated[List[Dict[str, Any]], lambda _, new: new]
    incident_id: Annotated[Optional[str], lambda _, new: new]
    summary: Annotated[Optional[Dict[str, Any]], lambda _, new: new]
    error: Annotated[Optional[str], lambda _, new: new]


# Node functions

def ingest_node(state: AgentState) -> AgentState:
    """Ingest alert from various sources."""
    try:
        alert = state.get("alert", {})
        if not alert:
            # If no alert provided, try to fetch from default source
            alert = ingest_alert()
        return {**state, "alert": alert, "error": None}
    except Exception as e:
        return {**state, "error": f"Ingestion failed: {str(e)}"}


def triage_node(state: AgentState) -> AgentState:
    """Perform triage classification."""
    print("DEBUG triage_node entered")
    try:
        alert = state["alert"]
        triage_result = triage_alert(alert)
        # Extract the triage part (excluding original alert fields)
        triage_info = triage_result.get("triage", {})
        print(f"DEBUG triage_info: {triage_info}")
        # Also run LLM triage for summary
        prompt = TRIAGE_PROMPT.format(alert=alert, triage=triage_info)
        print(f"DEBUG prompt: {prompt}")
        print(f"DEBUG llm type: {type(llm)}")
        if hasattr(llm, "invoke"):
            llm_response = llm.invoke(prompt)
        else:
            llm_response = llm(prompt)
        print(f"DEBUG llm_response: {llm_response}, type: {type(llm_response)}")
        # In real implementation, parse JSON properly
        llm_summary = {
            "summary": llm_response if isinstance(llm_response, str) else str(llm_response)
        }
        # Merge triage info with LLM summary
        merged_triage = {**triage_info, **llm_summary}
        print(f"DEBUG triage_node merged_triage: {merged_triage}")
        return {**state, "triage": merged_triage, "error": None}
    except Exception as e:
        import traceback
        print(f"DEBUG triage_node exception: {type(e).__name__}: {e}")
        traceback.print_exc()
        return {**state, "error": f"Triage failed: {str(e)}"}


def runbook_node(state: AgentState) -> AgentState:
    """Match runbooks to the alert."""
    try:
        alert = state["alert"]
        triage = state.get("triage", {})
        # Enrich alert with triage for matching
        enriched_alert = {**alert, "triage": triage}
        runbooks = match_runbooks(enriched_alert, max_results=3)
        return {**state, "runbooks": runbooks, "error": None}
    except Exception as e:
        return {**state, "error": f"Runbook matching failed: {str(e)}"}


def selection_node(state: AgentState) -> AgentState:
    """Select the best runbook based on relevance scoring."""
    try:
        runbooks = state.get("runbooks", [])
        if not runbooks:
            return {**state, "selected_runbook": None, "error": "No runbooks found"}
        # Sort by relevance_score descending (higher is better)
        sorted_runbooks = sorted(runbooks, key=lambda x: x.get("relevance_score", 0), reverse=True)
        best = sorted_runbooks[0]
        selected = get_runbook_by_id(best["runbook_id"])
        return {**state, "selected_runbook": selected, "error": None}
    except Exception as e:
        return {**state, "error": f"Runbook selection failed: {str(e)}"}


def action_node(state: AgentState) -> AgentState:
    """Generate actions from selected runbook."""
    try:
        runbook = state.get("selected_runbook")
        if not runbook:
            return {**state, "actions": [], "error": "No runbook selected"}

        # Create actions from runbook steps
        actions = []
        for step in runbook.get("steps", []):
            actions.append({
                "step": step.get("step"),
                "action": step.get("action"),
                "command": step.get("command"),
                "status": "pending"
            })

        # Create incident record
        incident_id = f"INC-{len(actions)}-{hash(str(runbook.get('id', '')))}"
        update_incident({
            "id": incident_id,
            "title": runbook.get("title"),
            "status": "investigating",
            "actions": actions
        })

        result = {**state, "actions": actions, "incident_id": incident_id, "error": None}
        print(f"DEBUG action_node returning: actions={len(actions)}, incident_id={incident_id}")
        return result

    except Exception as e:
        return {**state, "error": f"Action generation failed: {str(e)}"}


def summary_node(state: AgentState) -> AgentState:
    """Generate incident summary."""
    try:
        alert = state["alert"]
        triage = state.get("triage", {})
        runbook = state.get("selected_runbook", {})
        actions = state.get("actions", [])

        prompt = SUMMARIZATION_PROMPT.format(
            alert=alert,
            triage=triage,
            runbook=runbook,
            actions=actions
        )
        llm_response = llm.invoke(prompt)
        # Parse JSON response (simplified)
        summary = {
            "title": f"Incident: {alert.get('title', 'Unknown')}",
            "timeline": "To be filled",
            "root_cause": "Under investigation",
            "resolution": "Pending",
            "lessons_learned": "To be determined post-incident"
        }
        return {**state, "summary": summary, "error": None}
    except Exception as e:
        return {**state, "error": f"Summary generation failed: {str(e)}"}


def error_node(state: AgentState) -> AgentState:
    """Handle errors."""
    # In a real system, might send alerts or retry
    return state


# Define the graph

def create_ops_agent_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("ingest", ingest_node)
    workflow.add_node("triage", triage_node)
    workflow.add_node("runbook", runbook_node)
    workflow.add_node("select", selection_node)
    workflow.add_node("action", action_node)
    workflow.add_node("summary", summary_node)
    workflow.add_node("error", error_node)

    # Set entry point
    workflow.set_entry_point("ingest")

    # Add edges
    workflow.add_edge("ingest", "triage")
    workflow.add_edge("triage", "runbook")
    workflow.add_edge("runbook", "select")
    workflow.add_edge("select", "action")
    workflow.add_edge("action", "summary")
    workflow.add_edge("summary", END)

    # Error handling (simplified - in production would be more sophisticated)
    # workflow.add_edge("ingest", "error")
    # workflow.add_edge("triage", "error")
    # workflow.add_edge("runbook", "error")
    # workflow.add_edge("select", "error")
    # workflow.add_edge("action", "error")
    # workflow.add_edge("summary", "error")

    return workflow.compile()


# Global agent instance

ops_agent = create_ops_agent_graph()


def run_ops_agent(alert_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run the OpsAgent on an alert."""
    initial_state: AgentState = {
        "alert": alert_input or {},
        "triage": {},
        "runbooks": [],
        "selected_runbook": None,
        "actions": [],
        "incident_id": None,
        "summary": None,
        "error": None
    }

    result = ops_agent.invoke(initial_state)
    return result


if __name__ == "__main__":
    # Example usage
    test_alert = {
        "title": "High CPU Usage on web-01",
        "description": "CPU usage exceeds 90% for 5 minutes",
        "source": "prometheus",
        "labels": {"severity": "high", "category": "infrastructure"},
        "value": 92.5
    }

    result = run_ops_agent(test_alert)
    print("OpsAgent Result:")
    print(f"Incident ID: {result.get('incident_id')}")
    print(f"Triage: {result.get('triage', {}).get('severity')} - {result.get('triage', {}).get('category')}")
    print(f"Selected Runbook: {result.get('selected_runbook', {}).get('title') if result.get('selected_runbook') else 'None'}")
    print(f"Actions: {len(result.get('actions', []))} steps")
    print(f"Error: {result.get('error')}")
