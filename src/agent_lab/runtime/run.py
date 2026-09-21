from dataclasses import field, dataclass
from uuid import uuid4

from .state import AgentState

@dataclass
class AgentRun:
    run_id: str = field(default_factory=lambda: uuid4().hex)

    state: AgentState = field(default_factory=AgentState)
