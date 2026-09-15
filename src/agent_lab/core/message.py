from datetime import datetime
from typing import Optional, Any, Literal

from pydantic import BaseModel

MessageRole  = Literal["user", "assistant", "system", "tool", "summary"]

"""
基础消息类
"""
class Message(BaseModel):
     role: str = None
     content: str = None
     timestamp: datetime = None
     metadata: Optional[dict[str, Any]] = None

     def __init__(self, role: MessageRole, content: str, **kwargs):
          super().__init__(
               content = content,
               role = role,
               timestamp=kwargs.get("timestamp",datetime.now()),
               metadata = kwargs.get("metadata",{})
          )