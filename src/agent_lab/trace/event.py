from datetime import datetime
from enum import Enum
from typing import Any


class TraceEventType(Enum):
    AGENT_START = "agent_start"

    LLM_REQUEST = "llm_request"

    LLM_RESPONSE = "llm_response"

    TOOL_CALL = "tool_call"

    TOOL_RESULT = "tool_result"

    AGENT_FINISH = "agent_finish"

    AGENT_ERROR = "agent_error"


class TraceStatus(Enum):
    SUCCESS = "success"

    ERROR = "error"


class TraceEvent:
    trace_id: str

    sequence: int

    event_type: TraceEventType

    # 事件发生时间
    timestamp: datetime

    # 当前 Agent Tool Loop 轮次
    iteration: int

    # success / error
    status: TraceStatus

    # 当前操作耗时
    duration_ms: float

    # 不同事件自己的数据
    data: dict[str, Any]
