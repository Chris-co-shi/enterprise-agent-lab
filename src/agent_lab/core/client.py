from typing import List

from openai import OpenAI
from openai.types import ChatModel
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionMessage


class LLMClient:
    def __init__(
            self,
            model: str  | ChatModel,
            api_key: str | None = None,
            base_url: str | None = None,
            timeout: int | None= 60
    ):
        self.model = model
        api_key = api_key
        base_url = base_url
        timeout = timeout

        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def think(self,
              messages: List[ChatCompletionMessageParam],
              temperature: float = 0
    ) -> ChatCompletionMessage | None:
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages=messages,
                temperature=temperature,
                stream=False
            )
            return response.choices[0].message
        except Exception as exc:
            print(f"❌ 调用LLM API时发生错误: {exc}")
            return None