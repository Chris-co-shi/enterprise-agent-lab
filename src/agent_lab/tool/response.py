from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from pygments.lexer import default


class ToolStatus(Enum):
    """工具运行状态"""
    SUCCESS = "success" #
    # PARTIAL = "partial" # 结果可用但存在折扣（截断、回退、部分失败）
    ERROR = "error"
@dataclass
class ToolResponse:
    status: ToolStatus

    text: str

    data: dict[str, Any] = field(default_factory=dict)

    # error_info: Optional[dict[str, Any]]