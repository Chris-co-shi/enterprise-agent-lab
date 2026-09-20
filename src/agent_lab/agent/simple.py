from ..core.exceptions import AgentException
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

        while current_iteration < self.max_tool_iterations:
            current_iteration+=1
            response = self.llm.invoke(
                messages=messages,
                tools=self.tool_registry.list_tools(),
                **kwargs
            )

            # 处理工具调用
            tool_calls = response.tool_calls
            if not tool_calls:
                # 没有工具调用，直接返回文本响应
                final_response = response.content or "抱歉，我无法回答这个问题。"
                break

            # 将助手消息添加到历史
            messages.append(Message(
                role="assistant",
                content=response.content,
                tool_calls=tool_calls
            ))

            for tool_call in tool_calls:
                tool = self.tool_registry.get(tool_call.name)
                if tool is None:
                    continue
                tool_response = tool.run(tool_call.arguments)

        if not final_response:
            raise AgentException(
                f"Agent exceeded max tool iterations: "
                f"{self.max_tool_iterations}"
            )
        return final_response


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
