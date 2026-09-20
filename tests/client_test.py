import os
from dotenv import load_dotenv
from agent_lab.core import Message
from agent_lab.llm import LLMClient
load_dotenv()
if __name__ == '__main__':
    client = LLMClient(
        model="deepseek-flash",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
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