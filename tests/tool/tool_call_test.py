from agent_lab.core import Message
from agent_lab.llm.llm import LLMClient
from agent_lab.tool.function import FunctionTool
from agent_lab.tool.registry import ToolRegistry


def add(a: int, b: int = 1) -> int:
    """两个整数相加"""
    return a + b


registry = ToolRegistry()
registry.register(FunctionTool(add))

llm = LLMClient(
    model="deepseek-flash",
    api_key="sk-64a957090b9f4bccb874413b4ebb36e1",
    base_url="https://api.deepseek.com/v1"
)

response = llm.invoke(
    [
        Message(
            role="user",
            content="请必须使用 add 工具计算 12 + 8"
        )
    ],
    tools=registry.list_tools()
)

print("content:", response.content)
print("tool_calls:", response.tool_calls)