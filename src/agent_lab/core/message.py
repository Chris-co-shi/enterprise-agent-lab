from datetime import datetime
from typing import Optional, Any, Literal

from pydantic import BaseModel, Field

MessageRole  = Literal["user", "assistant", "system", "tool", "summary"]

"""
基础消息类
"""
class Message(BaseModel):
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