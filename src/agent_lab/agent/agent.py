from llm import LLMClient
from tool.registry import ToolRegistry
from .base import BaseAgent


class Agent(BaseAgent):

    def __init__(
            self,
            name: str,
            llm: LLMClient,
            tool_registry: ToolRegistry | None = None, # 因为 Agent 即使没有工具，也应该能退化成普通 LLM Agent。
            system_prompt: str | None = None,
            max_iterations: int = 5
    ):
        super().__init__(
            name = name,
            llm=llm,
            system_prompt=system_prompt
        )
        self.tool_registry = tool_registry
        self.max_iterations = max_iterations


    def run(self, input_text: str):
        pass