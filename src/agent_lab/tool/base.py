from abc import ABC
from typing import Any


class Tool(ABC):

    def __init__(
            self,
            name: str,
            description: str,
            parameters: dict[str, Any]
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
