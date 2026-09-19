from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ToolStatus(Enum):
    """工具运行状态"""
    SUCCESS = "success"  #
    # PARTIAL = "partial" # 结果可用但存在折扣（截断、回退、部分失败）
    ERROR = "error"

@dataclass
class ToolError:
    type: Optional[str]
    messages: Optional[str]
    # retryable: bool # 暂时先不处理。我认为应该可以交给LLM 处理
    #code: str | None


@dataclass
class ToolResponse:
    status: ToolStatus

    text: str

    error_info: Optional[ToolError]

    data: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def success(cls,text: str, data: dict[str, Any]) -> 'ToolResponse':
        return cls(
            status = ToolStatus.SUCCESS,
            text = text,
            data = data,
            error_info = ToolError()
        )
    @staticmethod
    def error(cls, error_info: ToolError) -> 'ToolResponse':
        return cls(
            status=ToolStatus.ERROR,
            text="",
            data={},
            error_info=error_info
        )