from agent_lab.core import Message
from agent_lab.llm import LLMClient

if __name__ == '__main__':
    client = LLMClient(
        model="qwen3.5:4b",
        api_key="test-key",
        base_url="http://127.0.0.1:11434/v1"
    )
    messages = [
        Message(
            role="system",
            content="你是一个 AI Agent 助手。",
        ),
        Message(
            role="user",
            content="你是谁？",
        ),
    ]
    result = client.invoke(
        messages=messages,
        temperature=0.1
    )
    print(f"result = {result}")
    # for chunk in result:
    #     pass