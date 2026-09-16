from datetime import datetime
from typing import Optional, Any, Literal

from pydantic import BaseModel, Field

MessageRole  = Literal["user", "assistant", "system", "tool", "summary"]


class Message(BaseModel):
     """框架内部统一消息模型。

     Message 用于在 Agent、上下文管理、LLM 调用及后续 Tool 交互之间传递消息，
     不直接依赖任何具体模型 Provider 的消息协议。
     """

     role: MessageRole
     content: str = None
     timestamp: datetime = Field(default_factory=datetime.now)
     metadata: Optional[dict[str, Any]] = None

     def __init__(self, role: MessageRole, content: str, **kwargs):
          super().__init__(
               content = content,
               role = role,
               timestamp=kwargs.get("timestamp",datetime.now()),
               metadata = kwargs.get("metadata",{})
          )
