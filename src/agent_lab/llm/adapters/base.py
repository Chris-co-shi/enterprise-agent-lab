import time
from abc import ABC, abstractmethod
from typing import Optional, Any, Iterator


from ...core import Message, LLMResponse


class BaseLLMAdapter(ABC):
    """LLM Provider 适配器抽象基类。

    Adapter 负责把框架内部的 Message 转换为 Provider 请求协议，
    调用具体 SDK，并将 Provider 返回结果转换回框架内部响应模型。
    """

    def __init__(
            self,
            model: str,
            base_url: Optional[str],
            api_key: str,
            timeout: int
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.model = model
        self._client = None

    @abstractmethod
    def create_client(self) -> Any:
        """创建具体 Provider 的 SDK 客户端。"""
        pass

    @abstractmethod
    def invoke(self, messages: list[Message], **kwargs) -> LLMResponse:
        """执行非流式模型调用并返回统一 LLMResponse。"""
        pass

    @abstractmethod
    def stream_invoke(self, messages: list[Message], **kwargs) -> Iterator[str]:
        """执行流式模型调用并逐块返回文本内容。"""
        pass

    @abstractmethod
    def _convert_messages(
            self,
            messages: list[Message]
    ) -> Any:
        """将框架内部 Message 列表转换为当前 Provider 的消息协议。"""
        pass
