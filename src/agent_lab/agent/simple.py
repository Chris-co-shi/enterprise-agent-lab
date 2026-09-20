from ..tool.response import ToolResponse, ToolError,ToolStatus
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
            max_tool_iterations: int = 5  #最大工具调用轮次
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
        tools = (
            self.tool_registry.list_tools()
            if self.tool_registry
            else []
        )

        for current_iteration in range(
                self.max_tool_iterations + 1
        ):
            response = self.llm.invoke(
                messages=messages,
                tools=tools,
                **kwargs
            )

            # 处理工具调用
            tool_calls = response.tool_calls
            if not tool_calls:
                # 没有工具调用，直接返回文本响应
                final_response = response.content or ""
                self.add_message(
                    Message(
                        role="user",
                        content=input_text
                    )
                )
                self.add_message(
                    Message(
                        role="assistant",
                        content=final_response
                    )
                )
                return final_response

            if current_iteration >= self.max_tool_iterations:
                raise AgentException(
                    f"Agent exceeded max tool iterations: "
                    f"{self.max_tool_iterations}"
                )
            # 记录 LLM 发起的 ToolCall
            # 注意：这里只加入本次 working messages，
            # 不提交到长期 History
            messages.append(Message(
                role="assistant",
                content=response.content,
                tool_calls=tool_calls
            ))

            for tool_call in tool_calls:
                tool = self.tool_registry.get(tool_call.name)
                # Tool 不存在，也统一转换成 ToolResponse.ERROR
                if tool is None:
                    tool_response = ToolResponse.error(
                        error_info=ToolError(
                            type="ToolNotFound",
                            message=(
                                f"Tool '{tool_call.name}' "
                                f"not found"
                            )
                        )
                    )
                else:
                    tool_response = tool.run(
                        tool_call.arguments
                    )

                # 将 ToolResponse 转成给 LLM 看的文本
                if tool_response.status == ToolStatus.SUCCESS:
                    tool_content = tool_response.text
                else:
                    error = tool_response.error_info
                    tool_content = (
                        f"Tool execution failed: "
                        f"{error.type if error else 'UnknownError'} - "
                        f"{error.message if error else 'unknown error'}"
                    )

                messages.append(
                    Message(
                        role="tool",
                        content=tool_content,
                        tool_call_id=tool_call.id
                    )
                )
        raise AgentException(
            "Agent terminated unexpectedly"
        )

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
