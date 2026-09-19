from agent_lab.core import Message
from agent_lab.llm import LLMClient

if __name__ == '__main__':
    client = LLMClient(
        model="deepseek-flash",
        api_key="sk-64a957090b9f4bccb874413b4ebb36e1",
        base_url="https://api.deepseek.com/v1"
    )
    messages = [
        # Message(
        #     role="system",
        #     content="你是一个 AI Agent 助手。",
        # ),
        Message(
            role="user",
            content="你好可以帮我解决一些关于Rust的学习计划吗？",
        ),
    ]
    result = client.invoke(
        messages=messages,
        temperature=0.1
    )
    print(f"result = {result}")
    # for chunk in result:
    #     pass