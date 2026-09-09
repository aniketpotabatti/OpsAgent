import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.ops_agent import selection_node, action_node
from tools.runbook_matching import get_runbook_by_id

def test_selection_node_picks_highest_score():
    # Mock get_runbook_by_id to return a simple dict
    original_get = get_runbook_by_id
    def mock_get(runbook_id):
        return {"runbook_id": runbook_id, "title": f"Runbook {runbook_id}"}
    # Replace globally (simple)
    import agent.ops_agent as oa
    oa.get_runbook_by_id = mock_get
    try:
        state = {
            "runbooks": [
                {"runbook_id": "rb-001", "title": "Low", "relevance_score": 0.2},
                {"runbook_id": "rb-002", "title": "Medium", "relevance_score": 0.5},
                {"runbook_id": "rb-003", "title": "High", "relevance_score": 0.9},
            ],
            "alert": {}
        }
        result = selection_node(state)
        assert result["selected_runbook"]["runbook_id"] == "rb-003"
        assert result["error"] is None
    finally:
        oa.get_runbook_by_id = original_get

def test_selection_node_no_runbooks():
    state = {"runbooks": [], "alert": {}}
    result = selection_node(state)
    assert result["selected_runbook"] is None
    assert "No runbooks found" in result["error"]

def test_action_node_generates_actions():
    # Mock selected runbook with steps
    dummy_runbook = {
        "runbook_id": "rb-001",
        "title": "Test Runbook",
        "steps": [
            {"step": 1, "action": "Check something", "command": "echo 1"},
            {"step": 2, "action": "Do something", "command": "echo 2"},
        ]
    }
    original_get = get_runbook_by_id
    import agent.ops_agent as oa
    oa.get_runbook_by_id = lambda x: dummy_runbook if x == "rb-001" else None
    # Also mock update_incident to avoid side effects
    import tools.incident_updater as upd
    original_update = upd.update_incident
    upd.update_incident = lambda x: None
    try:
        state = {
            "selected_runbook": dummy_runbook,
            "alert": {}
        }
        result = action_node(state)
        assert len(result["actions"]) == 2
        assert result["actions"][0]["status"] == "pending"
        assert result["incident_id"] is not None
        assert result["error"] is None
    finally:
        oa.get_runbook_by_id = original_get
        upd.update_incident = original_update

if __name__ == "__main__":
    test_selection_node_picks_highest_score()
    test_selection_node_no_runbooks()
    test_action_node_generates_actions()
    print("All tests passed")