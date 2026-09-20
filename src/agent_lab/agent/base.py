from abc import ABC, abstractmethod

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

    @abstractmethod
    def run(self, input_text: str):
        pass
