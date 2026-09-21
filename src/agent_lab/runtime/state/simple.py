from dataclasses import dataclass

from .base import AgentState

@dataclass
class SimpleState(AgentState):
    tool_iterations: int = 0