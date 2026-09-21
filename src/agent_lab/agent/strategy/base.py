from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ...core import Message
from ...runtime.state import AgentState

if TYPE_CHECKING:
    from ...runtime.runtime import AgentRuntime
    from ..agent import Agent


class AgentStrategy(ABC):

    @abstractmethod
    def create_state(
            self,
            messages: list[Message]
    ) -> AgentState:
        """
        创建状态
        """
        pass

    @abstractmethod
    def run(
            self,
            runtime: "AgentRuntime",
            agent: "Agent",
            state: AgentState,
            **kwargs
    ) -> str:
        pass
