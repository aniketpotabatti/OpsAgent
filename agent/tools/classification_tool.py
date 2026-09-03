"""
Triage classification tool for OpsAgent.
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

def classify_incident(incident_data: dict) -> dict:
    """
    Classify incident severity and category using prompt engineering.
    Uses LLM call with triage prompt.
    """
    description = incident_data.get("description", "")
    
    # Load the triage prompt
    prompt_template = load_prompt("triage_prompt")
    if not prompt_template:
        # Fallback to keyword-based if prompt missing
        return _fallback_classify(incident_data)
    
    # Format prompt with incident description
    formatted_prompt = prompt_template.format(alert_description=description)
    
    try:
        # Initialize LLM via factory (OpenAI, Anthropic, or Gemini)
        llm = get_llm(temperature=0)
        # Call LLM
        result = llm.invoke(formatted_prompt)
        # Expect result.content to be a JSON string with severity and category
        parsed = json.loads(result.content)
        severity = parsed.get("severity", "medium")
        category = parsed.get("category", "general")
    except Exception as e:
        # If LLM fails (missing API key, etc.), fallback to keyword-based
        print(f"LLM classification failed: {e}. Falling back to keyword-based.")
        return _fallback_classify(incident_data)
    
    return {
        "status": "classified",
        "incident_id": incident_data.get("id", "unknown"),
        "severity": severity,
        "category": category,
        "suggested_runbook": f"runbook_{category}.yaml",
        "message": "Incident classified successfully via LLM"
    }

def _fallback_classify(incident_data: dict) -> dict:
    """Keyword-based classification fallback."""
    description = incident_data.get("description", "").lower()
    if "network" in description or "latency" in description or "connection" in description:
        category = "network"
        severity = "high"
    elif "security" in description or "breach" in description or "virus" in description or "malware" in description:
        category = "security"
        severity = "critical"
    elif "hardware" in description or "server" in description or "disk" in description or "memory" in description:
        category = "hardware"
        severity = "medium"
    elif "software" in description or "application" in description or "bug" in description or "crash" in description:
        category = "software"
        severity = "medium"
    else:
        category = "general"
        severity = "low"
    if "down" in description or "outage" in description:
        severity = "high"
    return {
        "status": "classified",
        "incident_id": incident_data.get("id", "unknown"),
        "severity": severity,
        "category": category,
        "suggested_runbook": f"runbook_{category}.yaml",
        "message": "Incident classified successfully (fallback keyword-based)"
    }

# LangChain tool wrapper example:
# from langchain.tools import Tool
# classify_tool = Tool(
#     name="classify_incident",
#     func=classify_incident,
#     description="Classify an incident for triage"
# )