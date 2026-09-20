from .base import Tool
from ..core.exceptions import ToolException


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """注册工具"""
        if tool.name in self._tools:
            raise ToolException(
                f"Tool '{tool.name}' already exists"
            )

        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        """卸载工具"""
        # if name not in self._tool:
        #     raise ToolException(
        #         f"Tool '{name}' dont exists"
        #     )
        # 这里可以做成幂等
        self._tools.pop(name, None)

    def get(self, name: str) -> Tool | None:
        """根据名称获取工具"""
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())
