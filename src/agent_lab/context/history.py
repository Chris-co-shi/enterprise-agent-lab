from ..core import Message


class HistoryManager:
    """历史管理器

        特性：
        - 只追加，不编辑（缓存友好）


        用法示例：
        ```python
        manager = HistoryManager(min_retain_rounds=10)

        # 追加消息
        manager.append(Message("hello", "user"))
        manager.append(Message("hi", "assistant"))

        # 获取历史
        history = manager.get_history()

        ```
    """

    def __init__(self):
        """
        初始化 历史管理器
        """
        self._history: list[Message] = []

    def append(self, message: Message):
        self._history.append(message)

    def get_history(self) -> list[Message]:
        # copy() 至少保护 list 容器本身。 不然直接返回原数组 history 会被清空
        return self._history.copy()

    def clear(self):
        self._history.clear()
