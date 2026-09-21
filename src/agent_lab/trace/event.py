from dataclasses import field, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class TraceEventType(Enum):
    RUN_START = "run_start"

    MODEL_REQUEST = "model_request"
    MODEL_RESPONSE = "model_response"

    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"

    RUN_FINISH = "run_finish"
    RUN_ERROR = "run_error"


class TraceStatus(Enum):
    SUCCESS = "success"

    ERROR = "error"


@dataclass
class TraceEvent:
    trace_id: str

    sequence: int

    event_type: TraceEventType

    # 事件发生时间
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # 当前 Agent Tool Loop 轮次
    step: int | None = None

    # success / error
    status: TraceStatus | None = None

    # 当前操作耗时
    duration_ms: float | None = None

    # 不同事件自己的数据
    data: dict[str, Any] = field(default_factory=dict)
