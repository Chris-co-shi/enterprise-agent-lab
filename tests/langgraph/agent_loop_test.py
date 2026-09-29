import os
from typing import TypedDict, Annotated, Literal

from dotenv import load_dotenv
from langchain_core.messages import (
    AnyMessage, AIMessage, ToolMessage, HumanMessage, SystemMessage
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.constants import END, START
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import (
    ToolNode,
    tools_condition,
)
load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[
        list[AnyMessage],
        add_messages,
    ]


@tool
def get_inventory(
        material_code: str
) -> float:
    """
    查询 物料库存
    """
    inventory_db = {
        "MAT-1001": 120.00,
        "MAT-2001": 80.00,
    }

    return inventory_db.get(material_code, 0.00)


llm = ChatOpenAI(
    model=os.getenv(
        "MINI_MAX_MODEL",
        "MiniMax-M3"
    ),
    api_key=os.getenv(
        "MINI_MAX_API_KEY",
        "xxxx"
    ),
    base_url=os.getenv(
        "MINIMAX_BASE_URL",
        "https://api.minimax.cn/v1"
    ),
)

tools = [
    get_inventory
]
# 官方注册方式
tool_node = ToolNode(
    tools
)

llm_with_tools = llm.bind_tools(tools)


def agent_node(
        state: AgentState
) -> dict:
    """
    State
     ↓
    取 messages
     ↓
    LLM
     ↓
    得到 AIMessage
     ↓
    写回 State
    """
    print("\n进入 agent_node")

    print("\n----- 当前 State.messages -----")

    for index, message in enumerate(
            state["messages"]
    ):
        print(
            index,
            type(message).__name__,
            "content =",
            message.content,
        )

        if isinstance(
                message,
                AIMessage
        ):
            print(
                "tool_calls =",
                message.tool_calls,
            )

        if isinstance(
                message,
                ToolMessage
        ):
            print(
                "tool_call_id =",
                message.tool_call_id,
            )

    print("------------------------------")

    response = llm_with_tools.invoke(
        state["messages"]
    )

    print(
        "LLM content: ",
        response.content
    )

    print(
        "LLM tool_calls",
        response.tool_calls
    )

    return {
        "messages": [
            response
        ]
    }


def should_continue(
        state: AgentState
) -> Literal["tools", "__end__"]:
    """
    最后一条消息
    ↓
是不是 AIMessage
    ↓
有没有 tool_calls
    """
    last_message = state[
        "messages"
    ][-1]

    if (
            isinstance(
                last_message,
                AIMessage
            ) and last_message.tool_calls
    ):
        return "tools"
    return END


# def tool_node(
#         state: AgentState
# ) -> dict:
#     """
#         AIMessage
#  ↓
# tool_calls[0]
#  ↓
# {
#     name
#     args
#     id
# }
#  ↓
# get_inventory.invoke(args)
#  ↓
# 120
#  ↓
# ToolMessage
#
#     """
#
#     print("\n进入 tool_node")
#
#     last_message = state[
#         "messages"
#     ][-1]
#
#     tool_call = (
#         last_message
#         .tool_calls[0]
#     )
#
#     print(
#         "ToolCall",
#         tool_call
#     )
#
#     result = get_inventory.invoke(
#         tool_call["args"]
#     )
#
#     print(
#         "Tool result:",
#         result
#     )
#
#     tool_message = ToolMessage(
#         content=str(result),
#         tool_call_id=tool_call["id"],
#     )
#
#     update = {
#         "messages": [
#             tool_message
#         ]
#     }
#
#     print(
#         "tool_node 即将返回:",
#         update
#     )
#
#     return update


builder = StateGraph(AgentState)

# 注册节点。但是这里都会有 xpected type '_Node[NodeInputT ≤: TypedDictLikeV1 | TypedDictLikeV2 | DataclassLike | BaseModel] | _NodeWithConfig[NodeInputT ≤: 这种告警
builder.add_node(
    "agent",
    agent_node
)
builder.add_node(
    "tools",
    tool_node
)

# 设置入口
builder.add_edge(
    START,
    "agent"
)
# 最重要的 条件入口 Conditional Edge
builder.add_conditional_edges(
    "agent",
    tools_condition
)

builder.add_edge(
    "tools",
    "agent"
)

graph = builder.compile()

for event in graph.stream(
    {"messages": [
        # SystemMessage(
        #     content=(
        #         "你是一个制造业库存助手"
        #         "所有库存数据必须以工具返回作为唯一事实来源"
        #         "禁止自行编造库存数据、仓库、时间等信息"
        #         "工具没有返回的字段，不得自行补充"
        #     )
        # ),
        HumanMessage(
            content=(
                "分别查询 MAT-1001 和 MAT-2001 的当前库存，"
                "并告诉我哪个物料库存更高。"
            )
        )
    ]
    }
):
    print(
        "\n Graph Event:",
        event
    )