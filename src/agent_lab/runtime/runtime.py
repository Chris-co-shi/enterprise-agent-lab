from ..core import Message
from .run import AgentRun
from .state import AgentState
from ..trace import trace_agent
from ..agent import BaseAgent


def _create_agent_state(
        agent: BaseAgent,
        input_text:str
) -> AgentState:
    messages: list[Message] = []

    if agent.system_prompt:
        messages.append(Message(
            role="system",
            content=agent.system_prompt
        ))

    messages.extend(agent.get_history())

    messages.append(
        Message(
            role="user",
            content=input_text
        )
    )

    return AgentState(
        messages=messages
    )


class AgentRuntime:

    @trace_agent()
    def run(
            self,
            agent: BaseAgent,
            input_text: str,
            **kwargs
    ):
        agent_run = AgentRun(
            state=_create_agent_state(agent, input_text)
        )

        state = agent_run.state

        tools = (
            agent.tool_registry.list_tools()
            if agent.tool_registry
            else []
        )

        while True:
            response = agent.llm.invoke(
                messages=state.messages,
                tools = tools,
                **kwargs
            )

            tool_calls = response.tool_calls

            if not tool_calls:
                final_response = response.content or ""
                # 当前 Simple Strategy：
                # 没有 ToolCall 就认为任务完成。
                state.messages.append(
                    Message(
                        role="assistant",
                        content=final_response
                    )
                )
                # History 暂时仍然沿用 Agent 上的实现，
                # 下一阶段再拆 Session / History。
                agent.add_message(Message(
                    role="user",
                    content=input_text
                ))
                return final_response

