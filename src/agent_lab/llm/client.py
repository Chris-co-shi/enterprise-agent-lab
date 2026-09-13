from typing import Literal, TypedDict

import httpx


class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str

class OllamaClient:
    def __init__(
            self,
            model: str = "qwen3.5:4b",
            base_url: str = "http://127.0.0.1:11434",
            timeout: float = 120.0
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def chat(self, messages: list[Message]):
        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "think": False,
                },
                timeout=self.timeout
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Failed to call Ollama: {exc}"
            ) from exc
        data = response.json()

        content = data.get("message", {}).get("content")

        if not isinstance(content, str):
            raise RuntimeError(
                f"Unexpected Ollama response: {data}"
            )

        return content
