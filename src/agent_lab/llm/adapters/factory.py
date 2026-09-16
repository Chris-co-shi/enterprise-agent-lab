from .base import BaseLLMAdapter
from .openai_adapter import OpenAIAdapter


def create_adapter(
    api_key: str,
    base_url: str | None,
    timeout: int,
    model: str,
) -> BaseLLMAdapter:
    return OpenAIAdapter(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
        model=model,
    )