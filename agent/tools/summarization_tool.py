"""
Summarization tool for OpsAgent.
"""

import os
import json
from agent.tools.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate

def load_prompt(prompt_name: str) -> str:
    """Load a prompt from the prompts directory."""
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", f"{prompt_name}.txt")
    try:
        with open(prompt_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def summarize_incident(incident_data: dict) -> dict:
    """
    Summarize incident details using prompt engineering.
    Uses LLM call with summarization prompt.
    """
    incident_id = incident_data.get("id", "unknown")
    description = incident_data.get("description", "")
    severity = incident_data.get("severity", "unknown")
    category = incident_data.get("category", "unknown")
    actions = incident_data.get("actions_taken", [])
    runbook_id = incident_data.get("runbook_id", "unknown")
    
    # Load the summarization prompt
    prompt_template = load_prompt("summarization_prompt")
    if not prompt_template:
        # Fallback to template-based if prompt missing
        return _fallback_summarize(incident_data)
    
    # Format prompt with incident data
    formatted_prompt = prompt_template.format(
        incident_id=incident_id,
        description=description,
        severity=severity,
        category=category,
        actions=", ".join(actions) if actions else "No specific actions recorded",
        runbook_id=runbook_id
    )
    
    try:
        # Initialize LLM via factory (OpenAI, Anthropic, or Gemini)
        llm = get_llm(temperature=0)
        # Call LLM
        result = llm.invoke(formatted_prompt)
        # Expect result.content to be a JSON string with summary
        parsed = json.loads(result.content)
        summary = parsed.get("summary", "")
    except Exception as e:
        # If LLM fails (missing API key, etc.), fallback to template-based
        print(f"LLM summarization failed: {e}. Falling back to template-based.")
        return _fallback_summarize(incident_data)
    
    return {
        "status": "summarized",
        "incident_id": incident_id,
        "summary": summary,
        "message": "Incident summarized successfully via LLM"
    }

def _fallback_summarize(incident_data: dict) -> dict:
    """Template-based summarization fallback."""
    incident_id = incident_data.get("id", "unknown")
    description = incident_data.get("description", "")
    severity = incident_data.get("severity", "unknown")
    category = incident_data.get("category", "unknown")
    actions = incident_data.get("actions_taken", [])
    runbook_id = incident_data.get("runbook_id", "unknown")
    
    actions_str = ", ".join(actions) if actions else "No specific actions recorded"
    summary = (
        f"Incident {incident_id} ({severity} severity, {category} category) "
        f"was addressed using runbook {runbook_id}. "
        f"Actions taken: {actions_str}. "
        f"Description: {description[:100]}..."
    )
    
    return {
        "status": "summarized",
        "incident_id": incident_id,
        "summary": summary,
        "message": "Incident summarized successfully (fallback template-based)"
    }

# LangChain tool wrapper example:
# from langchain.tools import Tool
# summarize_tool = Tool(
#     name="summarize_incident",
#     func=summarize_incident,
#     description="Summarize an incident for stakeholder communication"
# )