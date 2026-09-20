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

    def run(self, input_text: str, **kwargs) -> str:
        messages = self._build_messages(input_text)
        # tool = (
        #     self.tool_registry.list_tools() if self.tool_registry else None
        # )
        # 如果没有启用工具调用，直接返回 LLM 响应
        if not self.tool_registry or not self.tool_registry.list_tools():
            response = self.llm.invoke(messages, **kwargs)
            response_text = response.content if hasattr(response, 'content') else str(response)
            self.add_message(Message(role="user", content=input_text))
            self.add_message(Message(role="assistant", content=response_text))
            return response_text

        current_iteration = 0
        final_response = ""

        while current_iteration <= self.max_tool_iterations:
            current_iteration+=1
            try:
                self.llm.invoke(
                    messages = messages,
                    tools = self.tool_registry.list_tools()
                )
            except Exception as exc:
                break
            # 处理工具调用
            tool_calls = response.tool_calls


    def _build_messages(self, input_text: str) -> list[Message]:
        """构建消息列表"""
        messages = []
        if self.system_prompt:
            messages.append(Message(
                role="system",
                content=self.system_prompt,
            ))

        messages.extend(self.get_history())

        messages.append(Message(
            role="user",
            content=input_text
        ))
        return messages
