"""
OpsAgent LangGraph definition.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import TypedDict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from langgraph.graph import StateGraph, END

# Import tool functions
from agent.tools.alert_tool import ingest_alert
from agent.tools.classification_tool import classify_incident
from agent.tools.runbook_matching_tool import match_runbook
from agent.tools.incident_updater_tool import update_incident
from agent.tools.summarization_tool import summarize_incident

from agent.src.state import IncidentState, AgentState


def parallel_processing_node(state: AgentState):
    """Process multiple alerts concurrently: ingest, classify, and match runbooks."""
    alerts = state.get("alerts", [])
    if not alerts:
        return state

    def process_single_alert(alert: dict):
        # Step 1: Ingest (call tool for side effects)
        ingest_alert(alert)
        # Step 2: Classify
        classification = classify_incident(alert)
        # Step 3: Create incident from alert and classification
        incident_id = alert.get("id")
        if not incident_id:
            import uuid
            incident_id = str(uuid.uuid4())
        incident = {
            "id": incident_id,
            "description": alert.get("description", ""),
            "severity": classification.get("severity", "medium"),
            "category": classification.get("category", "general"),
            "status": "open",
            "timestamp": alert.get("timestamp"),
        }
        # Step 4: Match runbook
        match = match_runbook(incident)
        runbook_info = {
            "runbook_id": match.get("runbook_id"),
            "runbook_path": match.get("runbook_path"),
            "incident_id": match.get("incident_id"),
        }
        return incident, runbook_info

    # Process alerts in parallel using a thread pool
    incidents_to_add = []
    runbooks_to_add = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_single_alert, alert) for alert in alerts]
        for future in as_completed(futures):
            incident, runbook_info = future.result()
            incidents_to_add.append(incident)
            runbooks_to_add.append(runbook_info)

    # Update state
    updated_incidents = state.get("incidents", []) + incidents_to_add
    updated_runbooks = state.get("runbooks", []) + runbooks_to_add
    # Set current_incident to the last processed incident (if any) for downstream routing
    current_incident = incidents_to_add[-1] if incidents_to_add else state.get("current_incident")

    return {
        **state,
        "incidents": updated_incidents,
        "runbooks": updated_runbooks,
        "current_incident": current_incident,
    }

def triage_classification_node(state: AgentState):
    """Classify and triage incoming alerts."""
    # Take the most recent alert
    if not state["alerts"]:
        return state
    latest_alert = state["alerts"][-1]
    classification = classify_incident(latest_alert)
    # Create incident from alert + classification
    incident = {
        "id": latest_alert.get("id", "inc_" + str(len(state["incidents"]) + 1)),
        "description": latest_alert.get("description", ""),
        "severity": classification.get("severity", "medium"),
        "category": classification.get("category", "general"),
        "status": "open",
        "timestamp": latest_alert.get("timestamp")
    }
    updated_incidents = state["incidents"] + [incident]
    return {**state, "incidents": updated_incidents, "current_incident": incident}

def runbook_matching_node(state: AgentState):
    """Match incident to relevant runbooks."""
    if not state["current_incident"]:
        return state
    match = match_runbook(state["current_incident"])
    # Optionally store runbook info in state; we can add to runbooks list or a field
    runbook_info = {
        "runbook_id": match.get("runbook_id"),
        "runbook_path": match.get("runbook_path"),
        "incident_id": match.get("incident_id")
    }
    # Append to runbooks list (could be more sophisticated)
    updated_runbooks = state["runbooks"] + [runbook_info]
    return {**state, "runbooks": updated_runbooks}

def incident_updater_node(state: AgentState):
    """Update incident status based on actions."""
    if not state["current_incident"]:
        return state
    # Example: after matching runbook, we could set status to "triaged"
    incident_id = state["current_incident"]["id"]
    updates = {"status": "triaged", "notes": "Runbook matched"}
    result = update_incident(incident_id, updates)
    # Update the incident in state
    updated_incidents = [
        {**inc, **updates} if inc["id"] == incident_id else inc
        for inc in state["incidents"]
    ]
    # Also update current_incident
    updated_current = {**state["current_incident"], **updates}
    return {
        **state,
        "incidents": updated_incidents,
        "current_incident": updated_current
    }

def reasoning_node(state: AgentState):
    """Agent reasoning step (e.g., ReAct)."""
    # Add a thought based on current state
    thought = f"Processed incident {state['current_incident']['id'] if state['current_incident'] else 'None'}"
    updated_thoughts = state["thoughts"] + [thought]
    # Optionally add a message
    message = {"role": "assistant", "content": thought}
    updated_messages = state["messages"] + [message]
    return {**state, "thoughts": updated_thoughts, "messages": updated_messages}


def escalation_node(state: AgentState):
    """Escalate critical incidents."""
    if not state["current_incident"]:
        return state
    incident_id = state["current_incident"]["id"]
    updates = {"status": "escalated", "notes": "Escalated due to critical severity"}
    result = update_incident(incident_id, updates)
    updated_incidents = [
        {**inc, **updates} if inc["id"] == incident_id else inc
        for inc in state["incidents"]
    ]
    updated_current = {**state["current_incident"], **updates}
    return {
        **state,
        "incidents": updated_incidents,
        "current_incident": updated_current
    }


def summarization_node(state: AgentState):
    """Summarize incident for stakeholders."""
    if not state["current_incident"]:
        return state
    summary_result = summarize_incident(state["current_incident"])
    # Store summary in state? We could add a field, but for simplicity add to thoughts/messages
    thought = f"Summary: {summary_result.get('summary', '')}"
    updated_thoughts = state["thoughts"] + [thought]
    message = {"role": "assistant", "content": thought}
    updated_messages = state["messages"] + [message]
    return {**state, "thoughts": updated_thoughts, "messages": updated_messages}

def build_graph():
    """Build the LangGraph state graph."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("parallel_processing", parallel_processing_node)
    workflow.add_node("incident_updater", incident_updater_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("escalation", escalation_node)
    workflow.add_node("summarization", summarization_node)

    # Set entry point
    workflow.set_entry_point("parallel_processing")

    # Add edges
    workflow.add_conditional_edges(
        "parallel_processing",
        lambda state: state["current_incident"]["severity"] if state["current_incident"] else "low",
        {
            "critical": "escalation",
            "high": "incident_updater",
            "medium": "incident_updater",
            "low": "incident_updater"
        }
    )
    workflow.add_edge("escalation", "summarization")
    workflow.add_edge("incident_updater", "reasoning")
    workflow.add_edge("reasoning", "summarization")
    workflow.add_edge("summarization", END)

    return workflow.compile()

# For LangGraph Studio or direct invocation
graph = build_graph()

def run_agent(incident_input: dict) -> dict:
    """Run the OpsAgent workflow on a single alert input."""
    # Initialize state
    initial_state = {
        "alerts": [incident_input] if incident_input else [],
        "incidents": [],
        "runbooks": [],
        "current_incident": None,
        "thoughts": [],
        "messages": []
    }
    result = graph.invoke(initial_state)
    return result

if __name__ == "__main__":
    # Example usage
    sample_alert = {
        "id": "alert_example",
        "source": "monitor",
        "description": "Sample alert for testing",
        "timestamp": "2026-09-03T00:00:00Z"
    }
    result = run_agent(sample_alert)
    print(result)