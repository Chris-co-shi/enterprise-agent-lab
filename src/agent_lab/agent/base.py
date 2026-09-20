from abc import ABC, abstractmethod
from typing import Optional

from ..tool.registry import ToolRegistry
from ..core import Message
from ..context import HistoryManager
from ..llm import LLMClient


class BaseAgent(ABC):
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
        self.history: HistoryManager = HistoryManager()
        self.tool_registry = tool_registry

    @abstractmethod
    def run(self, input_text: str) -> str:
        pass

    def add_message(self, message: Message):
        self.history.append(message)

    def clear_history(self):
        self.history.clear()

    def get_history(self) -> list[Message]:
        return self.history.get_history()