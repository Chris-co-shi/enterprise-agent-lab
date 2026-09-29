import os
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import (
    START,
    StateGraph,
)
from langgraph.graph.message import add_messages
from langgraph.prebuilt import (
    ToolNode,
    tools_condition,
)
from langgraph.checkpoint.memory import InMemorySaver


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
    查询指定物料的当前库存。
    """

    inventory_db = {
        "MAT-1001": 120.0,
        "MAT-2001": 80.0,
    }

    return inventory_db.get(
        material_code,
        0.0,
    )


tools = [
    get_inventory,
]
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

# graph = builder.compile()

checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)

config1 = {
    "configurable": {
        "thread_id": "inventory-user-001"
    }
}
config2 = {
    "configurable": {
        "thread_id": "inventory-user-002"
    }
}

result1 = graph.invoke(
    {
        "messages": [
            HumanMessage(
                content="查询 MAT-1001 当前库存是多少？"
            )
        ]
    },
    config=config1,
)

# result2 = graph.invoke(
#     {
#         "messages": [
#             HumanMessage(
#                 content="那 MAT-2001 呢？"
#             )
#         ]
#     },
#     config=config2,
# )

# print("\n===== 第一次调用结果 =====")
# for message in result1["messages"]:
#     print(
#         type(message).__name__,
#         ":",
#         message.content,
#     )
#
#
# print("\n===== 第二次调用结果 =====")
# for message in result2["messages"]:
#     print(
#         type(message).__name__,
#         ":",
#         message.content,
#     )



def print_snapshot(snapshot) -> None:

    print("\n========== StateSnapshot ==========")

    print(
        "thread_id:",
        snapshot.config["configurable"]["thread_id"],
    )

    print(
        "checkpoint_id:",
        snapshot.config["configurable"]["checkpoint_id"],
    )

    print(
        "created_at:",
        snapshot.created_at,
    )

    print(
        "next:",
        snapshot.next,
    )

    print(
        "metadata:",
        snapshot.metadata,
    )

    print("\nmessages:")

    for index, message in enumerate(
            snapshot.values["messages"]
    ):
        print(
            f"[{index}]",
            type(message).__name__,
            ":",
            message.content,
        )

        if hasattr(
                message,
                "tool_calls"
        ) and message.tool_calls:
            print(
                "    tool_calls:",
                message.tool_calls,
            )

        if isinstance(
                message,
                ToolMessage
        ):
            print(
                "    tool_call_id:",
                message.tool_call_id,
            )

    print("===================================")

snapshot = graph.get_state(
    config1
)

print_snapshot(snapshot)


print(
    "\n========== Checkpoint History =========="
)

history = graph.get_state_history(
    config1
)

for index, snapshot in enumerate(history):
    print(
        f"\n------------Snapshot {index} ----------"
    )

    print(
        "step:",
        snapshot.metadata.get("step")
        if snapshot.metadata
        else None,
    )

    print(
        "checkpoint_id:",
        snapshot.config[
            "configurable"
        ].get("checkpoint_id"),
    )

    print(
        "next:",
        snapshot.next
    )

    messages = snapshot.values.get(
        "messages",
        []
    )

    print(
        "messages count:",
        len(messages)
    )

    if messages:
        last_message = messages[-1]
        print(
            "last message:",
            type(last_message).__name__,
            ":",
            last_message.content
        )

