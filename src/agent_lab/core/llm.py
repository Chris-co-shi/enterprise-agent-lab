from typing import Optional, Iterator

from agent_lab.core.adapters import create_adapter
# from .adapters import create_adapter
from .exceptions import LLMException
from .response import StreamStats

class LLMClient:
    """
    统一LLM客户端

    """
    def __init__(
            self,
            model: Optional[str] = None,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            timeout: Optional[int] = None,
            temperature: float = 0.7,
            max_tokens: Optional[int] = None,
            **kwargs
    ):
        """
        初始化客户端
        参数优先级：传入参数 > 环境变量
        :param model: 大模型名称
        :param api_key: api 密钥
        :param base_url: 服务地址
        :param timeout: 客户端超时时间
        :param temperature: 温度 默认0.7
        :param max_tokens: 最大tokens 数量
        :param kwargs:
        """
        # self.last_call_stats = None
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs
        # self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        if not model:
            raise LLMException("必须提供模型名称（model参数或LLM_MODEL_ID环境变量）")
        if not api_key:
            raise LLMException("必须提供API密钥（api_key参数或LLM_API_KEY环境变量）")
        if not base_url:
            raise LLMException("必须提供服务地址（base_url参数或LLM_BASE_URL环境变量）")

        self._adapter = create_adapter(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            model=model
        )
        self.last_call_stats: Optional[StreamStats] = None

    def think(self, messages: list[dict[str, str]], temperature: Optional[float] = None) -> Iterator[str]:
        print(f"🧠 正在调用 {self.model} 模型...")

        # 准备参数
        kwargs = {
            "temperature": temperature if temperature is not None else self.temperature,
        }
        if self.max_tokens:
            kwargs["max_tokens"] = self.max_tokens
        try:
            print("✅ 大语言模型响应成功:")
            for chunk in self._adapter.stream_invoke(messages, **kwargs):
                print(chunk, end="", flush=True)
                yield chunk
            print()  # 换行

            # 保存统计信息
            if hasattr(self._adapter, 'last_stats'):
                self.last_call_stats = self._adapter.last_stats

        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            raise

if __name__ == '__main__':
    client = LLMClient(
        model="qwen3.5:4b",
        api_key="test-key",
        base_url="http://127.0.0.1:11434/v1"
    )
    messages = [
        {
            "role": "user",
            "content": "你是谁"
        }
    ]
    result = client.think(
        messages=messages,
        temperature=0.1
    )
    # print(f"result: {result.content}")