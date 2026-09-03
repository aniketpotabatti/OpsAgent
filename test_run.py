from agent.graph import graph

if __name__ == "__main__":
    result = graph.invoke({
        "alerts": [],
        "incidents": [],
        "runbooks": [],
        "current_incident": None,
        "thoughts": [],
        "messages": []
    })
    print("Result:")
    print(result)