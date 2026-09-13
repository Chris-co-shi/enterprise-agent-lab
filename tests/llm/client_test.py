from src.agent_lab.llm.client import OllamaClient

client = OllamaClient()

messages = [
    {
        "role": "system",
        "content": "你是一名简洁、准确的 AI 助手。",
    },
    {
        "role": "user",
        "content": "用一句话解释什么是 AI Agent。",
    },
]

response = client.chat(messages)

print(response)