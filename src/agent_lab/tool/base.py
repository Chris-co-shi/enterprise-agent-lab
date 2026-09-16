from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

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

    @abstractmethod
    def run(
            self,
            arguments: dict[str, Any],
    ) -> ToolResponse:
        pass