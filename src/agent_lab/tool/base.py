from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from ..trace import trace_tool
from .response import ToolResponse


class ToolParameter(BaseModel):
    name: str
    annotation: Any
    description: str
    required: bool = False
    default: Any = None


class Tool(ABC):
    def __init__(
            self,
            name: str,
            description: str,
            parameters: list[ToolParameter]
    ):
        self.name = name
        self.description = description
        self.parameters = parameters

    @trace_tool()
    def run(self,
            arguments: dict[str, Any]) -> ToolResponse:
        return self._run(arguments)

    @abstractmethod
    def _run(
            self,
            arguments: dict[str, Any],
    ) -> ToolResponse:
        pass