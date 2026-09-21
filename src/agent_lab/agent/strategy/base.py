from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ...runtime import AgentState
from ...core import Message

if TYPE_CHECKING:
    from ...runtime import AgentRuntime
    from ..base import BaseAgent


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

    def run(
            self,
            runtime: "AgentRuntime",
            agent: "BaseAgent",
            state: AgentState,
            **kwargs
    ) -> str:
        pass
