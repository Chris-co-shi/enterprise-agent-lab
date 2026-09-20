import os
from pathlib import Path

from dotenv import load_dotenv

from agent_lab.agent import SimpleAgent
from agent_lab.llm import LLMClient
from agent_lab.tool import ToolRegistry
from agent_lab.tool.function import FunctionTool
from agent_lab.trace import (
    configure_trace,
    TraceConfig,
    ConsoleTraceSink,
    JsonlTraceSink
)

load_dotenv()

print("cwd =", Path.cwd())
print(
    "trace file =",
    Path("logs/agent-trace.jsonl").resolve()
)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
def add(a: int, b: int) -> int:
    """两个整数相加"""
    return a + b


registry = ToolRegistry()
registry.register(
    FunctionTool(add)
)

configure_trace(
    TraceConfig(
        enabled=True,
        sinks=[
            ConsoleTraceSink(),
            JsonlTraceSink(
                PROJECT_ROOT
                / "logs"
                / "agent-trace.jsonl"
            ),
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

