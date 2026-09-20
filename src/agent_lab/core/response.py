from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ToolCall:
    """统一的工具调用对象"""
    id: str
    name: str
    arguments: str


@dataclass
class LLMResponse:
    """统一的 LLM 非流式响应对象。

    包含模型输出内容、实际模型名称、Token 使用统计、调用耗时，
    以及部分 reasoning model 可能返回的推理内容。
    """

    content: Optional[str]
    """模型回复内容。"""

    model: str
    """实际使用的模型名称。"""

    tool_calls: list[ToolCall] = field(default_factory=list)

    usage: dict[str, int] = field(default_factory=dict)
    """Token 使用统计，例如 prompt_tokens、completion_tokens、total_tokens。"""

    latency_ms: int = 0
    """调用耗时，单位毫秒。"""

    reasoning_content: Optional[str] = None
    """可选的模型推理内容，并非所有 Provider 或模型都会返回。"""

    def __str__(self):
        return self.content

    def __repr__(self):
        """返回便于调试的响应摘要。"""
        parts = [
            f"LLMResponse(model={self.model}",
            f"latency={self.latency_ms}ms",
            f"tokens={self.usage.get('total_tokens', 0)}",
        ]
        if self.reasoning_content:
            parts.append("has_reasoning=True")
        parts.append(f"content_length={len(self.content)})")
        return ", ".join(parts)


@dataclass
class StreamStats:
    """流式 LLM 调用结束后的统计信息。

    LLMClient 在流式调用完成后通过 last_call_stats 暴露该对象。
    """

    model: str
    """实际使用的模型名称。"""

    usage: dict[str, int] = field(default_factory=dict)
    """Token 使用统计。"""

    latency_ms: int = 0
    """完整流式调用耗时，单位毫秒。"""

    reasoning_content: Optional[str] = None
    """可选的模型推理内容。"""

    def to_dict(self) -> dict:
        """转换为普通字典。"""
        result = {
            "model": self.model,
            "usage": self.usage,
            "latency_ms": self.latency_ms,
        }
        if self.reasoning_content:
            result["reasoning_content"] = self.reasoning_content
        return result
