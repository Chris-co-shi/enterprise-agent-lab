from datetime import datetime
from typing import Optional, Any, Literal

from pydantic import BaseModel, Field

from .response import ToolCall

MessageRole = Literal["user", "assistant", "system", "tool", "summary"]


class Message(BaseModel):
    """框架内部统一消息模型。

    Message 用于在 Agent、上下文管理、LLM 调用及后续 Tool 交互之间传递消息，
    不直接依赖任何具体模型 Provider 的消息协议。
    """

    role: MessageRole
    content: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    tool_call_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)
