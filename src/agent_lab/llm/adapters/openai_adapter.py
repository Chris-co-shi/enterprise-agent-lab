import time
from typing import Callable, Any, Iterator

import openai.types.chat as openai_chat

from .base import BaseLLMAdapter
from agent_lab.core.response import LLMResponse, StreamStats
from agent_lab.core.exceptions import LLMException
from agent_lab.core.message import Message, MessageRole


class OpenAIAdapter(BaseLLMAdapter):
    OpenAIMessageConverter = Callable[
        [Message],
        openai_chat.ChatCompletionMessageParam,
    ]

    @staticmethod
    def _convert_system_message(
            message: Message,
    ) -> openai_chat.ChatCompletionMessageParam:
        return openai_chat.ChatCompletionSystemMessageParam(
            role="system",
            content=message.content,
        )

    @staticmethod
    def _convert_user_message(
            message: Message,
    ) -> openai_chat.ChatCompletionMessageParam:
        return openai_chat.ChatCompletionUserMessageParam(
            role="user",
            content=message.content,
        )

    @staticmethod
    def _convert_assistant_message(
            message: Message,
    ) -> openai_chat.ChatCompletionMessageParam:
        return openai_chat.ChatCompletionAssistantMessageParam(
            role="assistant",
            content=message.content,
        )

    _MESSAGE_CONVERTERS: dict[
        MessageRole,
        OpenAIMessageConverter,
    ] = {
        "system": _convert_system_message,
        "user": _convert_user_message,
        "assistant": _convert_assistant_message,
    }

    def _convert_message(self, messages: list[Message]) -> list[openai_chat.ChatCompletionMessageParam]:
        converted_messages: list[
            openai_chat.ChatCompletionMessageParam
        ] = []
        for message in messages:
            converter = self._MESSAGE_CONVERTERS.get(message.role)
            if converter is None:
                raise LLMException(
                    f"OpenAIAdapter 当前不支持消息角色: {message.role}"
                )
            converted_messages.append(
                converter(message)
            )
        return converted_messages


    def create_client(self) -> Any:
        from openai import OpenAI
        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )

    def invoke(self, messages: list[Message], **kwargs) -> LLMResponse:
        if not self._client:
            self._client = self.create_client()
        start_time = time.time()
        try:
            provider_messages  = self._convert_message(messages)
            response = self._client.chat.completions.create(
                model=self.model,
                messages = provider_messages ,
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


    def stream_invoke(self, messages: list[Message], **kwargs) -> Iterator[str]:
        if not self._client:
            self._client = self.create_client()
        start_time = time.time()
        provider_messages = self._convert_message(messages)
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=provider_messages,
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