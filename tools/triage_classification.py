"""Triage classification tool for OpsAgent."""
from typing import Dict, Any, Literal
from enum import Enum

class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
    UNKNOWN = "unknown"

class AlertCategory(str, Enum):
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    DATABASE = "database"
    NETWORK = "network"
    SECURITY = "security"
    PERFORMANCE = "performance"
    UNKNOWN = "unknown"

def classify_severity(alert: Dict[str, Any]) -> AlertSeverity:
    """Classify alert severity based on labels and content."""
    severity_str = alert.get("severity", "").lower()
    
    severity_map = {
        "critical": AlertSeverity.CRITICAL,
        "high": AlertSeverity.HIGH,
        "medium": AlertSeverity.MEDIUM,
        "low": AlertSeverity.LOW,
        "info": AlertSeverity.INFO,
        "warning": AlertSeverity.MEDIUM,
        "error": AlertSeverity.HIGH,
    }
    
    return severity_map.get(severity_str, AlertSeverity.UNKNOWN)

def classify_category(alert: Dict[str, Any]) -> AlertCategory:
    """Classify alert category based on labels and source."""
    labels = alert.get("labels", {})
    source = alert.get("source", "").lower()
    title = alert.get("title", "").lower()
    description = alert.get("description", "").lower()
    
    # Check labels first
    if "category" in labels:
        cat_str = labels["category"].lower()
        cat_map = {
            "infra": AlertCategory.INFRASTRUCTURE,
            "infrastructure": AlertCategory.INFRASTRUCTURE,
            "app": AlertCategory.APPLICATION,
            "application": AlertCategory.APPLICATION,
            "db": AlertCategory.DATABASE,
            "database": AlertCategory.DATABASE,
            "network": AlertCategory.NETWORK,
            "security": AlertCategory.SECURITY,
            "perf": AlertCategory.PERFORMANCE,
            "performance": AlertCategory.PERFORMANCE,
        }
        if cat_str in cat_map:
            return cat_map[cat_str]
    
    # Infer from source
    if "prometheus" in source or "node" in source or "kube" in source:
        return AlertCategory.INFRASTRUCTURE
    if "postgres" in source or "mysql" in source or "redis" in source:
        return AlertCategory.DATABASE
    if "nginx" in source or "haproxy" in source:
        return AlertCategory.NETWORK
    
    # Infer from title/description keywords
    text = f"{title} {description}"
    if any(kw in text for kw in ["cpu", "memory", "disk", "load", "oom", "killed"]):
        return AlertCategory.INFRASTRUCTURE
    if any(kw in text for kw in ["connection", "timeout", "latency", "slow", "5xx", "error rate"]):
        return AlertCategory.APPLICATION
    if any(kw in text for kw in ["deadlock", "replication", "backup", "vacuum", "index"]):
        return AlertCategory.DATABASE
    if any(kw in text for kw in ["dns", "tls", "certificate", "firewall", "packet"]):
        return AlertCategory.NETWORK
    if any(kw in text for kw in ["unauthorized", "breach", "intrusion", "vulnerability", "cve"]):
        return AlertCategory.SECURITY
    
    return AlertCategory.UNKNOWN

def triage_alert(alert: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform full triage classification on an alert.
    
    Returns enriched alert with severity, category, priority, and routing info.
    """
    severity = classify_severity(alert)
    category = classify_category(alert)
    
    # Calculate priority (1-5, where 1 is highest)
    priority_map = {
        AlertSeverity.CRITICAL: 1,
        AlertSeverity.HIGH: 2,
        AlertSeverity.MEDIUM: 3,
        AlertSeverity.LOW: 4,
        AlertSeverity.INFO: 5,
    }
    priority = priority_map.get(severity, 5)
    
    # Determine if escalation is needed
    needs_escalation = severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]
    
    # Suggested response time (in minutes)
    sla_map = {
        AlertSeverity.CRITICAL: 15,
        AlertSeverity.HIGH: 60,
        AlertSeverity.MEDIUM: 240,
        AlertSeverity.LOW: 1440,
        AlertSeverity.INFO: 10080,
    }
    sla_minutes = sla_map.get(severity, 1440)
    
    return {
        **alert,
        "triage": {
            "severity": severity.value,
            "category": category.value,
            "priority": priority,
            "needs_escalation": needs_escalation,
            "sla_minutes": sla_minutes,
            "classified_at": __import__("datetime").datetime.utcnow().isoformat(),
        }
    }