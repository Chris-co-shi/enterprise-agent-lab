from core import MessageRole
from ..core import Message
from ..llm import LLMClient
from ..tool.registry import ToolRegistry
from .base import BaseAgent


class SimpleAgent(BaseAgent):

    def __init__(
            self,
            name: str,
            llm: LLMClient,
            tool_registry: ToolRegistry | None = None,  # 因为 Agent 即使没有工具，也应该能退化成普通 LLM Agent。
            system_prompt: str | None = None,
            max_tool_iterations: int = 5  # 最大循环数量
    ):
        super().__init__(
            name=name,
            llm=llm,
            system_prompt=system_prompt,
            tool_registry=tool_registry
        )
        self.max_tool_iterations = max_tool_iterations

    def run(self, input_text: str):
        pass

    def _build_messages(self, input_text: str) -> list[Message]:
        """构建消息列表"""
        messages = []

        Message(
            role="system",
            content=self.system_prompt,

        )
        messages.extend(self.get_history())

        messages.append(Message(
            role="user",
            content=input_text
        ))
        return messages
