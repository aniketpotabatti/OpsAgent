import sys
sys.path.append('.')
from agent.graph import build_graph

def test_graph():
    graph = build_graph()
    initial_state = {
        "alerts": [
            {
                "id": "alert_1",
                "description": "Security breach detected on server",
                "timestamp": "2026-09-03T00:00:00Z"
            }
        ],
        "incidents": [],
        "runbooks": [],
        "current_incident": None,
        "thoughts": [],
        "messages": []
    }
    try:
        result = graph.invoke(initial_state)
        print("Graph execution completed")
        # Print some relevant info
        print("Number of alerts:", len(result.get("alerts", [])))
        print("Number of incidents:", len(result.get("incidents", [])))
        if result.get("incidents"):
            inc = result["incidents"][-1]
            print("Last incident:", inc)
        print("Number of thoughts:", len(result.get("thoughts", [])))
        if result.get("thoughts"):
            print("Last thought:", result["thoughts"][-1])
    except Exception as e:
        print("Error during graph execution:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_graph()