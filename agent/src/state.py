from typing import TypedDict, List, Optional
from datetime import datetime

class IncidentState(TypedDict):
    id: str
    title: str
    description: str
    status: str  # open, investigating, resolved, closed
    severity: str  # low, medium, high, critical
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str]
    tags: List[str]
    runbook_steps: List[dict]

class AgentState(TypedDict):
    alerts: List[dict]
    incidents: List[IncidentState]
    runbooks: List[dict]
    current_incident: Optional[IncidentState]
    thoughts: List[str]
    messages: List[dict]
    reasoning_steps: List[dict]
    chat_history: List[dict]