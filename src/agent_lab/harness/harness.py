from .state import AgentState
from ..core import Message
from ..agent import Agent



class AgentHarness:

    def _create_initial_state(
            self,
            agent: Agent,
            input_text: str,
            history: list[Message] | None = None
    ) -> AgentState:
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
        messages.append(
            Message(
                role="user",
                content=input_text
            )
        )
        return AgentState(
            messages=messages
        )


