from .state import AgentState
from ..core import Message
from ..agent import Agent


class AgentHarness:

    def _create_initial_state(
            self,
            # agent: Agent,
            input_text: str,
            # history: list[Message] | None = None
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
