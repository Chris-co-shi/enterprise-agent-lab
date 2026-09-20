from typing import Any

from agent_lab.tool.function import FunctionTool
from agent_lab.tool.response import ToolStatus


def add(a: int , b: int = 1):
    """两个整数相加"""
    return a+ b

def calculate_order(
        material_code: str,
        quantity: int,
        price: float,
        discount: float = 0.0,
        urgent: bool = False,
) -> dict[str, Any]:
    """计算订单金额"""

    if quantity <= 0:
        raise ValueError("quantity must be greater than 0")

    total = quantity * price * (1 - discount)

    return {
        "material_code": material_code,
        "quantity": quantity,
        "price": price,
        "total": total,
        "urgent": urgent,
    }


def divide(a: float, b: float) -> float:
    """除法计算"""

    return a / b


def test_function_metadata():
    tool = FunctionTool(add)

    assert tool.name == "add"
    assert tool.description == "两个整数相加"

    assert len(tool.parameters) == 2

    a = tool.parameters[0]
    b = tool.parameters[1]

    assert a.name == "a"
    assert a.annotation is int
    assert a.required is True
    assert a.default is None

    assert b.name == "b"
    assert b.annotation is int
    assert b.required is False
    assert b.default == 1

def test_function_use_default_argument():
    tool = FunctionTool(add)

    response = tool.run({
        "a": 10
    })

    assert response.status == ToolStatus.SUCCESS
    assert response.data["result"] == 11

def test_complex_function():
    tool = FunctionTool(calculate_order)

    response = tool.run({
        "material_code": "MAT001",
        "quantity": 10,
        "price": 20.0,
        "discount": 0.1,
        "urgent": True,
    })

    assert response.status == ToolStatus.SUCCESS

    assert response.data["material_code"] == "MAT001"
    assert response.data["quantity"] == 10
    assert response.data["total"] == 180.0
    assert response.data["urgent"] is True

def test_business_error():
    tool = FunctionTool(calculate_order)

    response = tool.run({
        "material_code": "MAT001",
        "quantity": -1,
        "price": 20.0,
    })

    assert response.status == ToolStatus.ERROR
    assert response.error_info is not None
    assert response.error_info.type == "ValueError"
    assert response.error_info.message == "quantity must be greater than 0"


def test_runtime_error():
    tool = FunctionTool(divide)

    response = tool.run({
        "a": 10,
        "b": 0,
    })

    assert response.status == ToolStatus.ERROR
    assert response.error_info is not None
    assert response.error_info.type == "ZeroDivisionError"

def test_missing_required_argument():
    tool = FunctionTool(add)

    response = tool.run({})

    assert response.status == ToolStatus.ERROR
    assert response.error_info is not None
    assert response.error_info.type == "TypeError"