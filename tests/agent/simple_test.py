import os

from dotenv import load_dotenv

from agent_lab.agent import SimpleAgent
from agent_lab.llm import LLMClient
from agent_lab.tool import ToolRegistry
from agent_lab.tool.function import FunctionTool
from trace.config import configure_trace, TraceConfig
from trace.sink import ConsoleTraceSink

load_dotenv()

def add(a: int, b: int) -> int:
    """两个整数相加"""
    print(f"add tool called: a={a}, b={b}")
    return a - b




registry = ToolRegistry()
registry.register(
    FunctionTool(add)
)

configure_trace(
    TraceConfig(
        enabled=True,
        sinks=[
            ConsoleTraceSink()
        ]
    )
)

llm = LLMClient(
    model="deepseek-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

agent = SimpleAgent(
    name="calculator-agent",
    llm=llm,
    tool_registry=registry,
    system_prompt="需要计算时优先使用提供的工具。"
)




result = agent.run(
    "请使用工具计算 12 + 8。"
)

# print("result:", result)
# print("history:", agent.get_history())
#
# assert result
# assert "20" in result
# assert len(agent.get_history()) == 2