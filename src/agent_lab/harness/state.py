from dataclasses import field, dataclass

from ..core import Message


@dataclass
class AgentState:

    trajectory: list[Message] = field(default_factory=list)
    # 这是本次 Agent Run 到目前为止发生的轨迹。
