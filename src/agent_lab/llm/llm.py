from typing import Optional, Iterator

from .adapters import create_adapter
from ..core.exceptions import LLMException
from ..core.response import LLMResponse, StreamStats
from ..core.message import Message


class LLMClient:
    """统一的 LLM 调用入口。

    对外使用框架内部的 Message / LLMResponse，具体 Provider 协议与 SDK
    由 Adapter 层负责处理。
    """

    def __init__(
            self,
            model: Optional[str] = None,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            timeout: int = 60,
            temperature: float = 0.7,
            max_tokens: Optional[int] = None,
            **kwargs
    ):
        """初始化 LLM 客户端。

        Args:
            model: 模型名称。
            api_key: Provider API 密钥。OpenAI-compatible 服务也需要提供非空值。
            base_url: Provider 服务地址。
            timeout: 请求超时时间，单位秒。
            temperature: 默认采样温度。
            max_tokens: 默认最大输出 Token 数；None 表示不在此处显式限制。
            **kwargs: 预留的额外初始化参数。
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs

        if not model:
            raise LLMException("必须提供模型名称")
        if not api_key:
            raise LLMException("必须提供API密钥")
        if not base_url:
            raise LLMException("必须提供服务地址")

        self._adapter = create_adapter(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            model=model
        )
        self.last_call_stats: Optional[StreamStats] = None

    def think(self, messages: list[Message], temperature: Optional[float] = None) -> Iterator[str]:
        """以流式方式调用模型，并逐块返回文本内容。"""
        print(f"🧠 正在调用 {self.model} 模型...")

        # 组合本次调用参数；显式传入的 temperature 优先于客户端默认值。
        kwargs = {
            "temperature": temperature if temperature is not None else self.temperature,
        }
        if self.max_tokens:
            kwargs["max_tokens"] = self.max_tokens

        try:
            print("✅ 大语言模型响应成功:")
            for chunk in self._adapter.stream_invoke(messages, **kwargs):
                print(chunk, end="", flush=True)
                yield chunk
            print()

            # Adapter 在流式调用结束后保存统计信息，LLMClient 对外暴露统一入口。
            if hasattr(self._adapter, 'last_stats'):
                self.last_call_stats = self._adapter.last_stats

        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            raise

    def invoke(self, messages: list[Message], **kwargs) -> LLMResponse:
        """以非流式方式调用模型并返回完整 LLMResponse。

        Args:
            messages: 框架内部消息列表。
            **kwargs: 本次调用参数，例如 temperature、max_tokens 等。

        Returns:
            包含模型输出、Token 使用量、耗时及可选推理内容的 LLMResponse。

        Example:
            response = llm.invoke([
                Message(role="user", content="你好")
            ])
            print(response.content)
            print(response.usage)
            print(response.latency_ms)
        """
        # 本次调用参数优先覆盖客户端默认值。
        call_kwargs = {
            "temperature": kwargs.pop("temperature", self.temperature),
        }
        if self.max_tokens:
            call_kwargs["max_tokens"] = kwargs.pop("max_tokens", self.max_tokens)
        call_kwargs.update(kwargs)

        return self._adapter.invoke(messages, **call_kwargs)
