from ..tool import ToolResponse, ToolError, ToolStatus
from .state import AgentState
from ..core import Message, LLMResponse, ToolCall
from ..agent import Agent
from ..trace.decorators import trace_run, trace_model

class AgentHarness:

    def __init__(
            self,
            max_steps: int = 10
    ):
        self.max_steps = max_steps

    def _create_initial_state(
            self,
            input_text: str,
    ) -> AgentState:
        """
        创建 Run State
        """
        return AgentState(
            trajectory=[
                Message(
                    role="user",
                    content=input_text
                )
            ]
        )

    def _build_messages(
            self,
            agent: Agent,
            state: AgentState,
            history: list[Message] | None = None
    ) -> list[Message]:
        """
        为一次 LLM invocation 构造 Context
        """
        messages: list[Message] = []
        if agent.system_prompt:
            messages.append(
                Message(
                    role="system",
                    content=agent.system_prompt
                )
            )
        if history:
            messages.extend(history)
        messages.extend(state.trajectory)
        return messages

    @trace_model()
    def _invoke_model(
            self,
            agent: Agent,
            state: AgentState,
            history: list[Message] | None = None,
            **kwargs
    ) -> LLMResponse:
        messages = self._build_messages(
            agent=agent,
            state=state,
            history=history,
        )
        tools = (
            agent.tool_registry.list_tools()
            if agent.tool_registry
            else []
        )
        return agent.llm.invoke(
            messages=messages,
            tools=tools,
            **kwargs,
        )

    def _execute_tool_call(
            self,
            agent: Agent,
            tool_call: ToolCall,
    ) -> ToolResponse:
        registry = agent.tool_registry

        if registry is None:
            return ToolResponse.error(
                ToolError(
                    type="ToolNotFound",
                    message=f"Tool '{tool_call.name}' not found"
                )
            )

        tool = registry.get(tool_call.name)

        if tool is None:
            return ToolResponse.error(
                ToolError(
                    type="ToolNotFound",
                    message=f"Tool '{tool_call.name}' not found"
                )
            )

        return tool.run(tool_call.arguments)

    def _record_model_response(
            self,
            state: AgentState,
            response: LLMResponse,
    ):
        state.trajectory.append(
            Message(
                role="assistant",
                content=response.content,
                tool_calls=response.tool_calls,
            )
        )

    def _record_tool_response(
            self,
            state: AgentState,
            tool_call: ToolCall,
            response: ToolResponse,
    ):
        if response.status == ToolStatus.SUCCESS:
            content = response.text
        else:
            error = response.error_info
            content = (
                "Tool execution failed: "
                f"{error.type if error else 'UnknownError'} - "
                f"{error.message if error else 'unknown error'}"
            )
        state.trajectory.append(
            Message(
                role="tool",
                content=content,
                tool_call_id=tool_call.id
            )
        )
