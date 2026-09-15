from agent_lab.core import LLMClient

if __name__ == '__main__':
    client = LLMClient(
        model="qwen3.5:4b",
        api_key="test-key",
        base_url="http://127.0.0.1:11434/v1"
    )
    messages = [
        {
            "role": "user",
            "content": "你是谁"
        }
    ]
    result = client.think(
        messages=messages,
        temperature=0.1
    )