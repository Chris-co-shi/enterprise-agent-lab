from typing import Literal

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END


class GraphState(TypedDict):
    value: int


def increase(state: GraphState) -> dict[str, int]:
    print("increase receive:", state)

    return {
        "value": state["value"] + 1
    }


def multiply(state: GraphState) -> dict[str, int]:
    print("multiply receive:", state)

    return {
        "value": state["value"] * 10
    }


def even(state: GraphState) -> dict:
    print("even receive:", state)
    return {}

def odd(state: GraphState) -> dict:
    print("odd receive:", state)
    return {}

def route_value(state: GraphState) -> Literal["even","odd"]:
    if state["value"] % 2 == 0:
        return "even"
    return "odd"

# 1. 创建 Graph Builder
builder = StateGraph(GraphState)

# 2. 注册 Node
builder.add_node("increase", increase)
builder.add_node("even", even)
builder.add_node("odd", odd)

# 3. 定义执行路径
# builder.add_edge(START, "increase")
# builder.add_edge("increase", "multiply")
# builder.add_edge("multiply", END)
builder.add_edge(START, "increase")
builder.add_conditional_edges(
    "increase",
    route_value
)
builder.add_edge("even", END)
builder.add_edge("odd", END)

# 4. 编译 Graph
graph = builder.compile()

# 5. 执行
result = graph.invoke({
    "value": 2
})

print("result:", result)