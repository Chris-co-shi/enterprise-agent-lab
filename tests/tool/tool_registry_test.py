import pytest

from agent_lab.tool.function import FunctionTool
from agent_lab.tool.registry import ToolRegistry
from agent_lab.core.exceptions import ToolException


def add(a: int, b: int = 1) -> int:
    return a + b


def divide(a: float, b: float) -> float:
    return a / b


def test_register_and_get_tool():
    registry = ToolRegistry()
    tool = FunctionTool(add)

    registry.register(tool)

    result = registry.get("add")

    assert result is tool


def test_get_not_exists_tool():
    registry = ToolRegistry()

    result = registry.get("not_exists")

    assert result is None


def test_list_tools():
    registry = ToolRegistry()

    add_tool = FunctionTool(add)
    divide_tool = FunctionTool(divide)

    registry.register(add_tool)
    registry.register(divide_tool)

    tools = registry.list_tools()

    assert len(tools) == 2
    assert add_tool in tools
    assert divide_tool in tools


def test_duplicate_register():
    registry = ToolRegistry()

    registry.register(FunctionTool(add))

    with pytest.raises(ToolException):
        registry.register(FunctionTool(add))


def test_unregister():
    registry = ToolRegistry()
    tool = FunctionTool(add)

    registry.register(tool)

    registry.unregister("add")

    assert registry.get("add") is None


def test_unregister_not_exists():
    registry = ToolRegistry()

    registry.unregister("not_exists")

    assert registry.get("not_exists") is None