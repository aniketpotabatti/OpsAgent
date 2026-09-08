"""Incident updater tool for OpsAgent."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid


class IncidentStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentPriority(str, Enum):
    P1 = "P1"  # Critical
    P2 = "P2"  # High
    P3 = "P3"  # Medium
    P4 = "P4"  # Low
    P5 = "P5"  # Info
    

@dataclass
class Incident:
    id: str
    alert_id: str
    title: str
    description: str
    severity: str
    category: str
    status: IncidentStatus
    priority: IncidentPriority
    assignee: Optional[str]
    created_at: str
    updated_at: str
    acknowledged_at: Optional[str] = None
    resolved_at: Optional[str] = None
    closed_at: Optional[str] = None
    runbook_id: Optional[str] = None
    runbook_steps_completed: List[int] = field(default_factory=list)
    notes: List[Dict[str, Any]] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)


# In-memory incident store (replace with DB in production)
INCIDENTS: Dict[str, Incident] = {}


def create_incident(alert: Dict[str, Any], runbook_id: Optional[str] = None) -> Incident:
    """Create a new incident from an alert."""
    triage = alert.get("triage", {})

    # Map triage severity to incident priority
    severity_to_priority = {
        "critical": IncidentPriority.P1,
        "high": IncidentPriority.P2,
        "medium": IncidentPriority.P3,
        "low": IncidentPriority.P4,
        "info": IncidentPriority.P5,
    }

    incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    now = datetime.utcnow().isoformat()

    incident = Incident(
        id=incident_id,
        alert_id=alert.get("id", f"alert-{uuid.uuid4().hex[:8]}"),
        title=alert.get("title", "Untitled Incident"),
        description=alert.get("description", ""),
        severity=triage.get("severity", "unknown"),
        category=triage.get("category", "unknown"),
        status=IncidentStatus.OPEN,
        priority=severity_to_priority.get(triage.get("severity", "info"), IncidentPriority.P5),
        assignee=None,
        created_at=now,
        updated_at=now,
        runbook_id=runbook_id,
        timeline=[{
            "timestamp": now,
            "event": "incident_created",
            "details": f"Incident created from alert: {alert.get('title', 'Unknown')}",
        }]
    )

    INCIDENTS[incident_id] = incident
    return incident


def get_incident(incident_id: str) -> Optional[Incident]:
    """Get incident by ID."""
    return INCIDENTS.get(incident_id)


def update_incident_status(incident_id: str, status: IncidentStatus, user: Optional[str] = None) -> Optional[Incident]:
    """Update incident status with timeline entry."""
    incident = INCIDENTS.get(incident_id)
    if not incident:
        return None

    now = datetime.utcnow().isoformat()
    old_status = incident.status
    incident.status = status
    incident.updated_at = now

    # Update specific timestamps
    if status == IncidentStatus.ACKNOWLEDGED and not incident.acknowledged_at:
        incident.acknowledged_at = now
    elif status == IncidentStatus.RESOLVED and not incident.resolved_at:
        incident.resolved_at = now
    elif status == IncidentStatus.CLOSED and not incident.closed_at:
        incident.closed_at = now

    incident.timeline.append({
        "timestamp": now,
        "event": "status_changed",
        "details": f"Status changed from {old_status.value} to {status.value}",
        "user": user,
    })

    return incident


def assign_incident(incident_id: str, assignee: str, user: Optional[str] = None) -> Optional[Incident]:
    """Assign incident to a user."""
    incident = INCIDENTS.get(incident_id)
    if not incident:
        return None

    now = datetime.now(timezone.utc).isoformat()
    old_assignee = incident.assignee
    incident.assignee = assignee
    incident.updated_at = now

    incident.timeline.append({
        "timestamp": now,
        "event": "assigned",
        "details": f"Assigned to {assignee}" + (f" (was {old_assignee})" if old_assignee else ""),
        "user": user,
    })

    return incident


def add_incident_note(incident_id: str, note: str, user: Optional[str] = None) -> Optional[Incident]:
    """Add a note to an incident."""
    incident = INCIDENTS.get(incident_id)
    if not incident:
        return None

    now = datetime.utcnow().isoformat()
    incident.notes.append({
        "timestamp": now,
        "note": note,
        "user": user,
    })
    incident.updated_at = now

    incident.timeline.append({
        "timestamp": now,
        "event": "note_added",
        "details": f"Note added by {user or 'system'}",
        "user": user,
    })

    return incident


def complete_runbook_step(incident_id: str, step_number: int, user: Optional[str] = None) -> Optional[Incident]:
    """Mark a runbook step as completed."""
    incident = INCIDENTS.get(incident_id)
    if not incident:
        return None

    if step_number not in incident.runbook_steps_completed:
        incident.runbook_steps_completed.append(step_number)
        incident.runbook_steps_completed.sort()

    now = datetime.utcnow().isoformat()
    incident.updated_at = now

    incident.timeline.append({
        "timestamp": now,
        "event": "runbook_step_completed",
        "details": f"Runbook step {step_number} completed",
        "user": user,
    })

    # Auto-resolve if all steps completed (simplified logic)
    if incident.runbook_id:
        # In real implementation, check against actual runbook steps
        pass

    return incident


def link_runbook(incident_id: str, runbook_id: str, user: Optional[str] = None) -> Optional[Incident]:
    """Link a runbook to an incident."""
    incident = INCIDENTS.get(incident_id)
    if not incident:
        return None

    now = datetime.utcnow().isoformat()
    incident.runbook_id = runbook_id
    incident.updated_at = now

    incident.timeline.append({
        "timestamp": now,
        "event": "runbook_linked",
        "details": f"Runbook {runbook_id} linked to incident",
        "user": user,
    })

    return incident


def list_incidents(
    status: Optional[IncidentStatus] = None,
    assignee: Optional[str] = None,
    priority: Optional[IncidentPriority] = None,
    limit: int = 50
) -> List[Incident]:
    """List incidents with optional filters."""
    incidents = list(INCIDENTS.values())

    if status:
        incidents = [i for i in incidents if i.status == status]
    if assignee:
        incidents = [i for i in incidents if i.assignee == assignee]
    if priority:
        incidents = [i for i in incidents if i.priority == priority]

    # Sort by priority then created_at
    priority_order = {p: i for i, p in enumerate(IncidentPriority)}
    incidents.sort(key=lambda x: (priority_order.get(x.priority, 99), x.created_at))

    return incidents[:limit]


def get_incident_summary(incident_id: str) -> Optional[Dict[str, Any]]:
    """Get a summary of an incident for reporting."""
    incident = INCIDENTS.get(incident_id)
    if not incident:
        return None

    return {
        "id": incident.id,
        "title": incident.title,
        "severity": incident.severity,
        "category": incident.category,
        "status": incident.status.value,
        "priority": incident.priority.value,
        "assignee": incident.assignee,
        "created_at": incident.created_at,
        "updated_at": incident.updated_at,
        "runbook_id": incident.runbook_id,
        "steps_completed": len(incident.runbook_steps_completed),
        "notes_count": len(incident.notes),
        "timeline_events": len(incident.timeline),
    }
