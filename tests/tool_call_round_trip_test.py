import os
from dotenv import load_dotenv
from agent_lab.core import Message
from agent_lab.llm.llm import LLMClient
from agent_lab.tool.function import FunctionTool
from agent_lab.tool.registry import ToolRegistry

load_dotenv()
def add(a: int, b: int = 1) -> int:
    """两个整数相加"""
    return a - b


# -------------------------
# 1. 注册 Tool
# -------------------------

registry = ToolRegistry()

registry.register(
    FunctionTool(add)
)


# -------------------------
# 2. 创建 LLM
# -------------------------

llm = LLMClient(
    model="deepseek-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


# -------------------------
# 3. 第一轮：让模型决定调用工具
# -------------------------

messages = [
    Message(
        role="user",
        content="请使用 add 工具计算 12 + 8，不要自己直接计算。"
    )
]

first_response = llm.invoke(
    messages,
    tools=registry.list_tools(),
)

print("\n=== 第一轮 LLM ===")
print("content:", first_response.content)
print("tool_calls:", first_response.tool_calls)


assert first_response.tool_calls, \
    "第一轮模型没有返回 tool_calls"


# -------------------------
# 4. 把 assistant tool_call 放回上下文
# -------------------------

messages.append(
    Message(
        role="assistant",
        content=first_response.content,
        tool_calls=first_response.tool_calls,
    )
)


# -------------------------
# 5. 执行模型请求的工具
# -------------------------

for tool_call in first_response.tool_calls:

    print("\n=== 执行工具 ===")
    print("tool:", tool_call.name)
    print("arguments:", tool_call.arguments)

    tool = registry.get(tool_call.name)

    assert tool is not None, \
        f"找不到工具: {tool_call.name}"

    tool_response = tool.run(
        tool_call.arguments
    )

    print("tool_response:", tool_response)

    # -------------------------
    # 6. Tool 结果写回上下文
    # -------------------------

    messages.append(
        Message(
            role="tool",
            content=tool_response.text,
            tool_call_id=tool_call.id,
        )
    )


# -------------------------
# 7. 第二轮：让模型根据工具结果回答
# -------------------------

second_response = llm.invoke(
    messages,
    tools=registry.list_tools(),
)

print("\n=== 第二轮 LLM ===")
print("content:", second_response.content)
print("tool_calls:", second_response.tool_calls)


# -------------------------
# 8. 验证
# -------------------------

# assert not second_response.tool_calls, \
#     "第二轮模型仍然要求调用工具"
#
# assert second_response.content, \
#     "第二轮没有返回最终回答"

print("\n✅ Tool Calling Round Trip 测试成功")