"""Runbook matching tool for OpsAgent."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
import re


@dataclass
class Runbook:
    id: str
    title: str
    category: str
    severity: str
    tags: List[str]
    description: str
    steps: List[Dict[str, Any]]
    prerequisites: List[str]
    estimated_duration_minutes: int
    last_updated: str


# In-memory runbook store (replace with DB/Vector store in production)
RUNBOOKS: List[Runbook] = [
    Runbook(
        id="rb-001",
        title="High CPU Usage on Kubernetes Node",
        category="infrastructure",
        severity="high",
        tags=["kubernetes", "cpu", "node", "performance"],
        description="Steps to diagnose and mitigate high CPU usage on a Kubernetes node",
        steps=[
            {"step": 1, "action": "Identify affected node", "command": "kubectl top nodes --sort-by=cpu"},
            {"step": 2, "action": "Check running pods on node", "command": "kubectl get pods --all-namespaces -o wide --field-selector spec.nodeName=<NODE>"},
            {"step": 3, "action": "Find top CPU consuming pods", "command": "kubectl top pods --all-namespaces --sort-by=cpu"},
            {"step": 4, "action": "Check for runaway processes", "command": "kubectl exec <POD> -- top -b -n 1 | head -20"},
            {"step": 5, "action": "Consider pod restart or node drain", "command": "kubectl drain <NODE> --ignore-daemonsets --delete-emptydir-data"},
        ],
        prerequisites=["kubectl access", "cluster-admin or node-reader permissions"],
        estimated_duration_minutes=30,
        last_updated="2024-01-15",
    ),
    Runbook(
        id="rb-002",
        title="Database Connection Pool Exhaustion",
        category="database",
        severity="critical",
        tags=["postgresql", "connection", "pool", "exhaustion"],
        description="Resolve PostgreSQL connection pool exhaustion",
        steps=[
            {"step": 1, "action": "Check current connections", "command": "SELECT count(*) FROM pg_stat_activity;"},
            {"step": 2, "action": "Identify idle connections", "command": "SELECT pid, state, query_start, query FROM pg_stat_activity WHERE state = 'idle' ORDER BY query_start;"},
            {"step": 3, "action": "Terminate idle connections", "command": "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND query_start < NOW() - INTERVAL '10 minutes';"},
            {"step": 4, "action": "Check connection pool settings", "command": "SHOW max_connections; SHOW superuser_reserved_connections;"},
            {"step": 5, "action": "Restart application pods to reset pools", "command": "kubectl rollout restart deployment/<APP> -n <NAMESPACE>"},
        ],
        prerequisites=["PostgreSQL superuser access", "kubectl access to affected namespace"],
        estimated_duration_minutes=20,
        last_updated="2024-01-10",
    ),
    Runbook(
        id="rb-003",
        title="High Memory Usage / OOM Kills",
        category="infrastructure",
        severity="critical",
        tags=["memory", "oom", "kubernetes", "container"],
        description="Diagnose and resolve Out of Memory (OOM) kills in containers",
        steps=[
            {"step": 1, "action": "Check for OOM events", "command": "kubectl get events --all-namespaces | grep -i oom"},
            {"step": 2, "action": "Identify affected pods", "command": "kubectl get pods --all-namespaces -o jsonpath='{.items[*].status.containerStatuses[*].lastState.terminated.reason}'"},
            {"step": 3, "action": "Check memory limits vs usage", "command": "kubectl top pods --all-namespaces --sort-by=memory"},
            {"step": 4, "action": "Analyze memory profile", "command": "kubectl exec <POD> -- cat /proc/meminfo"},
            {"step": 5, "action": "Increase memory limits or optimize application", "command": "kubectl set resources deployment/<APP> -c=<CONTAINER> --limits=memory=2Gi --requests=memory=1Gi"},
        ],
        prerequisites=["kubectl access", "container metrics enabled"],
        estimated_duration_minutes=25,
        last_updated="2024-01-12",
    ),
    Runbook(
        id="rb-004",
        title="SSL/TLS Certificate Expiry",
        category="network",
        severity="medium",
        tags=["ssl", "tls", "certificate", "expiry", "security"],
        description="Handle expiring or expired SSL/TLS certificates",
        steps=[
            {"step": 1, "action": "Check certificate expiry", "command": "openssl x509 -in <CERT_FILE> -text -noout | grep 'Not After'"},
            {"step": 2, "action": "List all certificates in cluster", "command": "kubectl get certificates --all-namespaces -o custom-columns=NAME:.metadata.name,NAMESPACE:.metadata.name,EXPIRY:.status.notAfter"},
            {"step": 3, "action": "Renew certificate via cert-manager", "command": "kubectl delete secret <CERT_SECRET> -n <NAMESPACE> # cert-manager will reissue"},
            {"step": 4, "action": "Verify renewal", "command": "kubectl get certificate <CERT_NAME> -n <NAMESPACE> -o yaml"},
            {"step": 5, "action": "Restart affected ingress/controllers", "command": "kubectl rollout restart deployment/ingress-nginx-controller -n ingress-nginx"},
        ],
        prerequisites=["cert-manager installed", "kubectl access"],
        estimated_duration_minutes=15,
        last_updated="2024-01-08",
    ),
    Runbook(
        id="rb-005",
        title="Application High Error Rate (5xx)",
        category="application",
        severity="high",
        tags=["application", "5xx", "error-rate", "http"],
        description="Investigate and mitigate high 5xx error rates in applications",
        steps=[
            {"step": 1, "action": "Check error rate metrics", "command": "curl -s <PROMETHEUS>/api/v1/query?query=rate(http_requests_total{status=~\"5..\"}[5m])"},
            {"step": 2, "action": "Identify failing endpoints", "command": "kubectl logs -l app=<APP> -n <NAMESPACE> --tail=100 | grep -i error"},
            {"step": 3, "action": "Check upstream dependencies", "command": "kubectl get pods -l app=<DEPENDENCY> -n <NAMESPACE>"},
            {"step": 4, "action": "Rollback recent deployment if applicable", "command": "kubectl rollout undo deployment/<APP> -n <NAMESPACE>"},
            {"step": 5, "action": "Scale up replicas for capacity", "command": "kubectl scale deployment/<APP> --replicas=5 -n <NAMESPACE>"},
        ],
        prerequisites=["kubectl access", "Prometheus access", "deployment history"],
        estimated_duration_minutes=20,
        last_updated="2024-01-14",
    ),
]


def match_runbooks(alert: Dict[str, Any], max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Match runbooks to an alert based on category, severity, and tags.

    Returns list of matching runbooks sorted by relevance score.
    """
    triage = alert.get("triage", {})
    alert_category = triage.get("category", "").lower()
    alert_severity = triage.get("severity", "").lower()
    alert_title = alert.get("title", "").lower()
    alert_description = alert.get("description", "").lower()

    alert_text = f"{alert_title} {alert_description}"
    alert_tags = extract_tags(alert_text)

    scored_runbooks = []
    for rb in RUNBOOKS:
        score = calculate_relevance_score(
            rb, alert_category, alert_severity, alert_tags, alert_text
        )
        if score > 0:
            scored_runbooks.append((score, rb))

    # Sort by score descending
    scored_runbooks.sort(key=lambda x: x[0], reverse=True)

    # Return top matches as dicts
    results = []
    for score, rb in scored_runbooks[:max_results]:
        results.append({
            "runbook_id": rb.id,
            "title": rb.title,
            "category": rb.category,
            "severity": rb.severity,
            "tags": rb.tags,
            "description": rb.description,
            "steps": rb.steps,
            "prerequisites": rb.prerequisites,
            "estimated_duration_minutes": rb.estimated_duration_minutes,
            "last_updated": rb.last_updated,
            "relevance_score": round(score, 2),
        })

    return results


def extract_tags(text: str) -> List[str]:
    """Extract potential tags from alert text."""
    # Common infrastructure/app keywords
    keywords = [
        "cpu", "memory", "disk", "network", "kubernetes", "pod", "node", "container",
        "postgresql", "mysql", "redis", "database", "connection", "pool",
        "ssl", "tls", "certificate", "cert", "ingress", "nginx",
        "5xx", "error", "timeout", "latency", "latency", "slow",
        "oom", "killed", "oomkilled", "outofmemory",
        "replication", "backup", "vacuum", "index",
        "dns", "firewall", "packet", "load", "balancer",
    ]
    found = []
    for kw in keywords:
        if kw in text:
            found.append(kw)
    return found


def calculate_relevance_score(
    runbook: Runbook,
    alert_category: str,
    alert_severity: str,
    alert_tags: List[str],
    alert_text: str
) -> float:
    """Calculate relevance score between 0 and 1."""
    score = 0.0

    # Category match (high weight)
    if runbook.category == alert_category:
        score += 0.4

    # Severity match (medium weight)
    severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
    rb_sev = severity_order.get(runbook.severity, 0)
    alert_sev = severity_order.get(alert_severity, 0)
    if rb_sev == alert_sev:
        score += 0.2
    elif abs(rb_sev - alert_sev) == 1:
        score += 0.1

    # Tag overlap (high weight)
    rb_tags_set = set(runbook.tags)
    alert_tags_set = set(alert_tags)
    if rb_tags_set and alert_tags_set:
        overlap = len(rb_tags_set & alert_tags_set)
        total = len(rb_tags_set | alert_tags_set)
        score += 0.3 * (overlap / total)

    # Text keyword match (low weight)
    for tag in rb_tags_set:
        if tag in alert_text:
            score += 0.02

    return min(score, 1.0)


def get_runbook_by_id(runbook_id: str) -> Optional[Dict[str, Any]]:
    """Get full runbook details by ID."""
    for rb in RUNBOOKS:
        if rb.id == runbook_id:
            return {
                "runbook_id": rb.id,
                "title": rb.title,
                "category": rb.category,
                "severity": rb.severity,
                "tags": rb.tags,
                "description": rb.description,
                "steps": rb.steps,
                "prerequisites": rb.prerequisites,
                "estimated_duration_minutes": rb.estimated_duration_minutes,
                "last_updated": rb.last_updated,
            }
    return None


def add_runbook(runbook_data: Dict[str, Any]) -> Runbook:
    """Add a new runbook to the store."""
    rb = Runbook(**runbook_data)
    RUNBOOKS.append(rb)
    return rb
