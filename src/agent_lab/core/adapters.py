import time
from abc import ABC, abstractmethod
from typing import Optional, Any, Iterator
from .response import LLMResponse, StreamStats
from .exceptions import LLMException

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
    def invoke(self, messages: list[dict], **kwargs) -> LLMResponse:
        pass

    """抽象流式调用方法"""
    @abstractmethod
    def stream_invoke(self, messages: list[dict], **kwargs) -> Iterator[str]:
        pass


class OpenAIAdapter(BaseLLMAdapter):
    # def __init__(
    #         self,
    #         model: str,
    #         base_url: Optional[str],
    #         api_key: str,
    #         timeout: int
    # ):
    #     super().__init__(model, base_url, api_key, timeout)
    #     self.last_stats = None

    def create_client(self) -> Any:
        from openai import OpenAI
        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )

    def invoke(self, messages: list[dict], **kwargs) -> LLMResponse:
        if not self._client:
            self._client = self.create_client()
        start_time = time.time()

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages = messages,
                **kwargs
            )
            latency_ms = int((time.time() - start_time) * 1000)
            # 提取关键信息
            choice = response.choices[0]
            content = choice.message.content or ""
            reasoning_content = None
            # 判断是否包含推理过程信息
            if hasattr(choice.message, 'reasoning_content'):
                reasoning_content = choice.message.reasoning_content
            elif hasattr(choice, 'reasoning_content'):
                reasoning_content = choice.reasoning_content

            usage = {}
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            return LLMResponse(
                content = content,
                model=self.model,
                latency_ms=latency_ms,
                usage=usage,
                reasoning_content = reasoning_content
            )
        except Exception as exc:
            raise LLMException(f"OpenAI API 调用失败:{str(exc)}")


    def stream_invoke(self, messages: list[dict], **kwargs) -> Iterator[str]:
        if not self._client:
            self._client = self.create_client()
        start_time = time.time()
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                **kwargs
            )
            collected_content = []
            reasoning_content = None
            usage = {}
            for chunk in response:
                choices = getattr(chunk, "choices", None)
                if choices:
                    delta = getattr(choices[0],"delta", None)
                    if delta is not None:
                        # 提取内容
                        content = getattr(delta, "content", None)
                        if content:
                            collected_content.append(content)
                            yield content
                            # Thinking model的推理过程
                        reasoning_delta = getattr(delta, "reasoning_content", None)
                        if reasoning_delta:
                            if reasoning_content is None:
                                reasoning_content = ""
                            reasoning_content += reasoning_delta
                if hasattr(chunk, "usage") and chunk.usage:
                    usage = {
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "completion_tokens": chunk.usage.completion_tokens,
                        "total_tokens": chunk.usage.total_tokens,
                    }
            latency_ms = int((time.time() - start_time) * 1000)
            # 返回统计信息（存储到适配器，供外部获取）
            self.last_stats = StreamStats(
                model=self.model,
                usage=usage,
                latency_ms=latency_ms,
                reasoning_content=reasoning_content
            )
        except Exception as exc:
            raise LLMException(f"OpenAI API 调用失败:{str(exc)}")




def create_adapter(
        api_key: str,
        base_url: Optional[str],
        timeout: int,
        model: str
) -> BaseLLMAdapter:
    # 目前默认使用OpenAI的方式创建 LLM客户端,后续如果有需要在进行扩展
    return OpenAIAdapter(api_key=api_key,base_url=base_url,timeout=timeout, model=model)