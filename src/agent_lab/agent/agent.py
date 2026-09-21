from typing import Optional

from ..tool import ToolRegistry
from ..llm import LLMClient


class Agent:
    def __init__(
            self,
            name: str,
            llm: LLMClient,
            system_prompt: Optional[str] = None,
            tool_registry: Optional['ToolRegistry'] = None
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.tool_registry = tool_registry
