from typing import Optional, Iterator

from .adapters import create_adapter
from ..core.exceptions import LLMException
from ..core.response import LLMResponse, StreamStats
from ..core.message import Message
class LLMClient:
    """
    统一LLM客户端

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
        """
        初始化客户端
        参数优先级：传入参数 > 环境变量
        :param model: 大模型名称
        :param api_key: api 密钥
        :param base_url: 服务地址
        :param timeout: 客户端超时时间
        :param temperature: 温度 默认0.7
        :param max_tokens: 最大tokens 数量
        :param kwargs:
        """
        # self.last_call_stats = None
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs
        # self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
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
        print(f"🧠 正在调用 {self.model} 模型...")
        # 准备参数
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
            print()  # 换行

            # 保存统计信息
            if hasattr(self._adapter, 'last_stats'):
                self.last_call_stats = self._adapter.last_stats

        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            raise

    def invoke(self, messages: list[Message], **kwargs) -> LLMResponse:
        """
        非流式调用LLM，返回完整响应对象。

        Args:
            messages: 消息列表
            **kwargs: 其他参数（temperature, max_tokens等）

        Returns:
            LLMResponse: 包含内容、统计信息、推理过程（thinking model）的响应对象

        Example:
            response = llm.invoke([{"role": "user", "content": "你好"}])
            print(response.content)  # 回复内容
            print(response.usage)    # token使用量
            print(response.latency_ms)  # 耗时
            if response.reasoning_content:  # thinking model的推理过程
                print(response.reasoning_content)
        """
        # 合并参数
        call_kwargs = {
            "temperature": kwargs.pop("temperature", self.temperature),
        }
        if self.max_tokens:
            call_kwargs["max_tokens"] = kwargs.pop("max_tokens", self.max_tokens)
        call_kwargs.update(kwargs)

        return self._adapter.invoke(messages, **call_kwargs)
