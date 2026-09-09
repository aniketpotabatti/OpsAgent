"""Base agent class for OpsAgent multi-agent system."""
from typing import Dict, Any
from langgraph.graph import StateGraph

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.graph = StateGraph(dict)

    def build_graph(self):
        """Subclasses should implement graph construction."""
        raise NotImplementedError

    def run(self, input_state: Dict[str, Any]) -> Dict[str, Any]:
        compiled = self.graph.compile()
        return compiled.invoke(input_state)