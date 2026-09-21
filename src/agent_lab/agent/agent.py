from typing import Optional

from .strategy import AgentStrategy
from ..tool import ToolRegistry
from ..core import Message
from ..context import HistoryManager
from ..llm import LLMClient


class Agent:
    def __init__(
            self,
            name: str,
            llm: LLMClient,
            strategy: AgentStrategy,
            system_prompt: Optional[str] = None,
            tool_registry: Optional['ToolRegistry'] = None
    ):
        self.name = name
        self.llm = llm
        self.strategy = strategy
        self.system_prompt = system_prompt
        self.tool_registry = tool_registry
