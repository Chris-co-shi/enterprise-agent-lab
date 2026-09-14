from openai.types.chat import ChatCompletionMessageParam, ChatCompletionUserMessageParam

from agent_lab.core.client import LLMClient


def test_chat_returns_assistant_message():
    client = LLMClient(
        model="qwen3.5:4b",
        api_key="test-key",
        base_url="http://127.0.0.1:11434/v1"
    )
    messages: list[ChatCompletionMessageParam] = [
        ChatCompletionUserMessageParam(
            role="user",
            content="什么是AI Agent",
        )
    ]
    result = client.chat(
        messages=messages
    )
    print(f"result: {result}")
