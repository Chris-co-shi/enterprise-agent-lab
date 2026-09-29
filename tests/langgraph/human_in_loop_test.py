import os
from typing import Literal, TypedDict, Annotated

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.constants import END
from langgraph.graph import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import NotRequired

from langgraph.types import (
    interrupt,
    Command,
)

from langchain_core.messages import (
    AIMessage,
    ToolMessage,
    AnyMessage,
    HumanMessage,
)

from langgraph.graph import (
    StateGraph,
    START,
    add_messages,
)

from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()
inventory_db = {
    "MAT-1001": 120.0,
    "MAT-2001": 80.0,
}


@tool
def get_inventory(
        material_code: str
) -> float:
    """
    查询指定物料的当前库存。
    """

    return inventory_db.get(
        material_code,
        0.0,
    )


@tool
def update_inventory(
        material_code: str,
        quantity: float,
) -> str:
    """
    修改指定物料的库存数量。
    """

    inventory_db[material_code] = quantity

    return (
        f"{material_code} 库存已修改为 "
        f"{quantity}"
    )


tools = [
    get_inventory,
    update_inventory,
]


class AgentState(TypedDict):
    messages: Annotated[
        list[AnyMessage],
        add_messages,
    ]

    approved: NotRequired[bool]


tool_node = ToolNode(tools)

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

llm_with_tools = llm.bind_tools(
    tools
)

def route_after_agent(
        state: AgentState
) -> Literal[
    "tools",
    "review",
    "__end__"
]:
    last_message = state["messages"][-1]

    if not isinstance(
        last_message,
        AIMessage
    ):
        return END

    if not last_message.tool_calls:
        return END
    for tool_call in last_message.tool_calls:
        if (
            tool_call["name"] == "update_inventory"
        ):
            return "review"

    return "tools"

def review_node(
        state: AgentState
) -> dict[str, object]:
    last_message = state["messages"][-1]

    tool_call = next(
        tool_call
        for tool_call in last_message.tool_calls
        if tool_call["name"] == "update_inventory"
    )

    decision = interrupt({
        "type": "inventory_update_approval",
        "tool": tool_call["name"],
        "args": tool_call["args"],
        "message": "库存修改属于写操作，是否批准？"
    })

    return {
        "approved": decision == "approve"
    }

def route_after_review(
        state: AgentState
) -> Literal[
    "tools",
    "reject"
]:
    if state["approved"]:
        return "tools"

    return "reject"

def reject_node(
        state: AgentState
) -> dict[str, object]:
    last_message = state["messages"][-1]

    tool_call = next(
        tool_call
        for tool_call in last_message.tool_calls
        if tool_call["name"] == "update_inventory"
    )

    return {
        "messages":[
            ToolMessage(
                content=(
                    "人工审批拒绝"
                    "库存修改未执行"
                ),
                tool_call_id = tool_call["id"]
            )
        ]
    }

def agent_node(
        state: AgentState
) -> dict:
    print("\n===== 进入 agent_node =====")

    for index, message in enumerate(
            state["messages"]
    ):
        print(
            index,
            type(message).__name__,
            ":",
            message.content,
        )

    response = llm_with_tools.invoke(
        state["messages"]
    )

    return {
        "messages": [
            response
        ]
    }


builder = StateGraph(
    AgentState
)

builder.add_node(
    "agent",
    agent_node
)

builder.add_node(
    "tools",
    tool_node
)

builder.add_node(
    "review",
    review_node
)

builder.add_node(
    "reject",
    reject_node
)

builder.add_edge(
    START,
    "agent"
)

builder.add_conditional_edges(
    "agent",
    route_after_agent,
)

builder.add_conditional_edges(
    "review",
    route_after_review,
)

builder.add_edge(
    "tools",
    "agent"
)

builder.add_edge(
    "reject",
    "agent"
)

checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)

config = {
    "configurable": {
        "thread_id": "inventory-update-001"
    }
}

reject_config = {
    "configurable": {
        "thread_id": "inventory-update-reject-001"
    }
}



# result = graph.invoke(
#     {
#         "messages": [
#             HumanMessage(
#                 content=(
#                     "把 MAT-1001 的库存"
#                     "修改为 500"
#                 )
#             )
#         ]
#     },
#     config=config,
# )
#
# print(
#     "\n审批前库存:",
#     inventory_db["MAT-1001"]
# )
#
# result2 = graph.invoke(
#     Command(
#         resume="approve"
#     ),
#     config=config,
# )

reject_result1 = graph.invoke(
    {
        "messages": [
            HumanMessage(
                content="把 MAT-1001 的库存修改为 500"
            )
        ]
    },
    config=reject_config,
)

reject_result2 = graph.invoke(
    Command(
        resume="reject"
    ),
    config=reject_config,
)

print(
    "\n========== 恢复执行结果 =========="
)

for message in reject_result2["messages"]:
    print(
        type(message).__name__,
        ":",
        message.content,
    )


print(
    "\n审批后库存:",
    inventory_db["MAT-1001"]
)