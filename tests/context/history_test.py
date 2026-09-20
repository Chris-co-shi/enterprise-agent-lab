from agent_lab.context import HistoryManager
from agent_lab.core import Message


history = HistoryManager()

history.append(
    Message(
        role="user",
        content="hello"
    )
)

history.append(
    Message(
        role="assistant",
        content="hi"
    )
)


print("history:")
print(history.get_history())


assert len(history.get_history()) == 2

assert history.get_history()[0].content == "hello"

assert history.get_history()[1].content == "hi"


history.clear()

assert len(history.get_history()) == 0


print("✅ HistoryManager test passed")