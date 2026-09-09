"""Alert ingestion tool for OpsAgent."""
from typing import Dict, Any
import json

def ingest_alert(alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest and validate incoming alert data.
    
    Args:
        alert_data: Raw alert from monitoring system
        
    Returns:
        Normalized alert structure
    """
    normalized = {
        "alert_id": alert_data.get("id", ""),
        "source": alert_data.get("source", "unknown"),
        "severity": alert_data.get("severity", "unknown"),
        "title": alert_data.get("title", ""),
        "description": alert_data.get("description", ""),
        "timestamp": alert_data.get("timestamp", ""),
        "labels": alert_data.get("labels", {}),
        "annotations": alert_data.get("annotations", {}),
        "raw_payload": alert_data
    }
    return normalized

def parse_prometheus_alert(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Prometheus Alertmanager webhook format."""
    alerts = payload.get("alerts", [])
    normalized_alerts = []
    for alert in alerts:
        normalized = {
            "alert_id": alert.get("fingerprint", ""),
            "source": "prometheus",
            "severity": alert.get("labels", {}).get("severity", "unknown"),
            "title": alert.get("labels", {}).get("alertname", ""),
            "description": alert.get("annotations", {}).get("description", ""),
            "timestamp": alert.get("startsAt", ""),
            "labels": alert.get("labels", {}),
            "annotations": alert.get("annotations", {}),
            "raw_payload": alert
        }
        normalized_alerts.append(normalized)
    return {"alerts": normalized_alerts}