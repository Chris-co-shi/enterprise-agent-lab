import time
from abc import ABC, abstractmethod
from typing import Optional, Any, Iterator, Callable


from ...core import Message, LLMResponse, StreamStats

class BaseLLMAdapter(ABC):
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

    """抽象出创建客户端的方式"""
    @abstractmethod
    def create_client(self) -> Any:
        pass

    """抽象非流式调用方法"""
    @abstractmethod
    def invoke(self, messages: list[Message], **kwargs) -> LLMResponse:
        pass

    """抽象流式调用方法"""
    @abstractmethod
    def stream_invoke(self, messages: list[Message], **kwargs) -> Iterator[str]:
        pass

    @abstractmethod
    def _convert_message(
            self,
            messages: list[Message]
    ) -> Any:
        pass