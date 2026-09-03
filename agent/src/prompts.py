INCIDENT_ANALYSIS_PROMPT = """
You are an expert incident response analyst. Given the following incident details, provide a concise analysis and suggested next steps.

Incident Title: {title}
Description: {description}
Severity: {severity}
Tags: {tags}

Analysis:
"""

RUNBOOK_GENERATION_PROMPT = """
Generate a step-by-step runbook for resolving the following incident.

Incident: {title}
Details: {description}
Current Status: {status}

Runbook:
"""