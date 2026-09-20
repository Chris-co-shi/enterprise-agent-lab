import os
from dotenv import load_dotenv

from agent import SimpleAgent
from agent_lab.llm import LLMClient
load_dotenv()


llm = LLMClient(
    model="deepseek-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

agent = SimpleAgent(
    name="simple-agent",
    llm=llm,
    system_prompt="你是一个简洁的助手。"
)

result = agent.run("你好，简单介绍一下你自己。")

print("result:", result)
print("history:", agent.get_history())

assert result
assert len(agent.get_history()) == 2
assert agent.get_history()[0].role == "user"
assert agent.get_history()[1].role == "assistant"