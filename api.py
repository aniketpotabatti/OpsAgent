"""
Optional FastAPI endpoint for OpsAgent.
Run with: uvicorn api:app --reload
"""
import os
import sys

# Try importing FastAPI modules, but handle ImportError gracefully
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    _fastapi_available = True
except ImportError:  # pragma: no cover
    _fastapi_available = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.ops_agent import run_ops_agent

if _fastapi_available:
    app = FastAPI(title="OpsAgent API", description="Incident triage and runbook assistant")

    class AlertRequest(BaseModel):
        title: str
        description: str
        source: str = "unknown"
        labels: dict = {}
        value: float | None = None

    @app.post("/analyze")
    async def analyze_alert(alert: AlertRequest):
        """
        Analyze an alert and return triage, runbook selection, actions, and summary.
        """
        alert_dict = alert.dict()
        # Remove None values
        if alert_dict.get("value") is None:
            del alert_dict["value"]
        try:
            result = run_ops_agent(alert_dict)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    async def health():
        return {"status": "ok"}

else:  # pragma: no cover
    # Provide a helpful message when fastapi is not installed
    def app(*args, **kwargs):  # type: ignore
        raise RuntimeError(
            "FastAPI is not installed. Install it with `pip install fastapi uvicorn` to use the API endpoint."
        )