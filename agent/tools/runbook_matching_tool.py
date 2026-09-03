"""
Runbook matching tool for OpsAgent.
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

def match_runbook(incident_data: dict) -> dict:
    """
    Match incident to relevant runbook using prompt engineering.
    Uses LLM call with runbook matching prompt.
    """
    description = incident_data.get("description", "")
    category = incident_data.get("category", "general")
    severity = incident_data.get("severity", "medium")
    
    # Load the runbook matching prompt
    prompt_template = load_prompt("runbook_matching_prompt")
    if not prompt_template:
        # Fallback to rule-based if prompt missing
        return _fallback_match(incident_data)
    
    # Format prompt with incident data
    formatted_prompt = prompt_template.format(
        incident_description=description,
        category=category,
        severity=severity
    )
    
    try:
        # Initialize LLM via factory (OpenAI, Anthropic, or Gemini)
        llm = get_llm(temperature=0)
        # Call LLM
        result = llm.invoke(formatted_prompt)
        # Expect result.content to be a JSON string with runbook_id and optionally runbook_path
        parsed = json.loads(result.content)
        runbook_id = parsed.get("runbook_id")
        runbook_path = parsed.get("runbook_path")
        # If runbook_path not provided, construct from id
        if not runbook_path:
            runbook_path = f"runbooks/{runbook_id}.yaml"
    except Exception as e:
        # If LLM fails (missing API key, etc.), fallback to rule-based
        print(f"LLM runbook matching failed: {e}. Falling back to rule-based.")
        return _fallback_match(incident_data)
    
    return {
        "status": "matched",
        "incident_id": incident_data.get("id", "unknown"),
        "runbook_id": runbook_id,
        "runbook_path": runbook_path,
        "message": "Runbook matched successfully via LLM"
    }

def _fallback_match(incident_data: dict) -> dict:
    """Rule-based matching fallback."""
    description = incident_data.get("description", "").lower()
    category = incident_data.get("category", "general")
    severity = incident_data.get("severity", "medium")
    
    if category == "network":
        runbook_id = "network_connectivity"
        runbook_path = "runbooks/network_connectivity.yaml"
    elif category == "security":
        runbook_id = "security_incident"
        runbook_path = "runbooks/security_incident.yaml"
    elif category == "hardware":
        runbook_id = "hardware_failure"
        runbook_path = "runbooks/hardware_failure.yaml"
    elif category == "software":
        runbook_id = "software_bug"
        runbook_path = "runbooks/software_bug.yaml"
    else:
        runbook_id = "general_troubleshooting"
        runbook_path = "runbooks/general_troubleshooting.yaml"
    
    # Adjust based on severity
    if severity == "critical":
        runbook_id = f"{runbook_id}_critical"
        runbook_path = f"runbooks/{runbook_id}.yaml"
    
    return {
        "status": "matched",
        "incident_id": incident_data.get("id", "unknown"),
        "runbook_id": runbook_id,
        "runbook_path": runbook_path,
        "message": "Runbook matched successfully (fallback rule-based)"
    }

# LangChain tool wrapper example:
# from langchain.tools import Tool
# match_tool = Tool(
#     name="match_runbook",
#     func=match_runbook,
#     description="Match an incident to a relevant runbook"
# )