from typing import Any

from .base import Tool
from .response import ToolResponse


class FunctionTool(Tool):
    def run(self, arguments: dict[str, Any]) -> ToolResponse:
        pass