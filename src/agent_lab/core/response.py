from dataclasses import dataclass, field
from typing import Optional

"""
   统一的LLM的响应对象
   包含响应内容、推理过程（thinking model）、token使用统计、耗时等信息
"""
@dataclass
class LLMResponse:

    content: str
    """回复内容"""

    model: str
    """实际使用的模型名称"""

    usage: dict[str, int] = field(default_factory=dict)
    """Token使用统计: {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}"""

    latency_ms: int = 0
    """调用耗时 单位毫秒"""

    reasoning_content: Optional[str] = None
    """推理过程 不是每次都有"""

    def __str__(self):
        return self.content

"""
        流式调用的统计信息
        在流式调用结束后可通过 llm.last_call_stats 获取
"""
@dataclass
class StreamStats:

    model: str
    """实际使用的模型名称"""

    usage: dict[str, int] = field(default_factory=dict)
    """Token使用统计"""

    latency_ms: int = 0
    """调用耗时（毫秒）"""

    reasoning_content: Optional[str] = None
    """推理过程（仅thinking model）"""

    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = {
            "model": self.model,
            "usage": self.usage,
            "latency_ms": self.latency_ms,
        }
        if self.reasoning_content:
            result["reasoning_content"] = self.reasoning_content
        return result