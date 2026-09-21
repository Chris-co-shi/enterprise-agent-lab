from dataclasses import field, dataclass

from ..core import Message


@dataclass
class AgentState:
    messages: list[Message] = field(default_factory=list)
