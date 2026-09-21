from dataclasses import field, dataclass

from ..core import Message


@dataclass
class AgentState:

    trajectory: list[Message] = field(default_factory=list)
    # 这是本次 Agent Run 到目前为止发生的轨迹。

    step: int = 0
    # 当前 Run 已完成的外部行动轮次。
    # 同一模型响应中的多个 ToolCall 属于同一个 step。
