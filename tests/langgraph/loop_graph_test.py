from typing import Literal

from langgraph.constants import START, END
from typing_extensions import TypedDict
from langgraph.graph import StateGraph


class RouteState(TypedDict):
    request_type: str
    result: str

def route_node(state: RouteState) -> dict:
    return {}


def inventory_node(state: RouteState):
    return {
        "result":"库存处理完成"
    }

def work_order_node(state: RouteState) -> dict:
    return {
        "result": "工单处理完成"
    }

def chat_node(state: RouteState):
    return {
        "result": "普通对话完成"
    }

def route_request(state: RouteState) -> Literal["inventory","work_order","chat"]:
    request_type = state["request_type"]
    if request_type == "inventory":
        return "inventory"

    if request_type == "work_order":
        return "work_order"

    return "chat"


builder = StateGraph(RouteState)


builder.add_node("route", route_node)

builder.add_node(
    "inventory",
    inventory_node
)

builder.add_node(
    "work_order",
    work_order_node
)

builder.add_node(
    "chat",
    chat_node
)

builder.add_edge(
    START,
    "route"
)

builder.add_conditional_edges(
    "route",
    route_request
)

builder.add_edge(
    "inventory",
    END
)
builder.add_edge(
    "work_order",
    END
)
builder.add_edge(
    "chat",
    END
)

graph = builder.compile()

for chunk in graph.stream(
        {
            "request_type":"inventory",
            "result":"",
        },
        stream_mode="updates"
):
    print(chunk)