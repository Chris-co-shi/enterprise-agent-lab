import os
from pathlib import Path
from dotenv import load_dotenv

from agent_lab.agent import Agent
from agent_lab.harness import AgentHarness
from agent_lab.llm import LLMClient
from agent_lab.tool import ToolRegistry
from agent_lab.tool.function import FunctionTool
from agent_lab.trace import (
    configure_trace,
    TraceConfig,
    ConsoleTraceSink,
    JsonlTraceSink,
)

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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

def add(a: int, b: int) -> int:
    """计算两个整数之和"""
    return a + b


registry = ToolRegistry()
registry.register(
    FunctionTool(add)
)

llm = LLMClient(
    model="deepseek-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)

agent = Agent(
    name="calculator-agent",
    llm=llm,
    tool_registry=registry,
    system_prompt="你是计算助手。需要计算时必须优先调用工具。",
)

harness = AgentHarness(
    max_steps=5
)

result = harness.run(
    agent=agent,
    input_text="请使用工具计算 12 + 8。",
)

print("result:", result)