from abc import ABC, abstractmethod

from ..core import Message
from ..llm import LLMClient


class BaseAgent(ABC):
    def __init__(
            self,
            name: str,
            llm: LLMClient,
            system_prompt: str | None = None,
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self._history: list[Message] = []

    @abstractmethod
    def run(self, input_text: str):
        pass

    def add_message(self, message: Message):
        self._history.append(message)

    def get_history(self) -> list[Message]:
        # copy() 至少保护 list 容器本身。 不然直接返回原数组 history 会被清空
        return self._history.copy()

    def clear_history(self):
        self._history.clear()