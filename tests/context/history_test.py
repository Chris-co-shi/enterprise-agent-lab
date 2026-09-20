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
print(history.get())


assert len(history.get()) == 2

assert history.get()[0].content == "hello"

assert history.get()[1].content == "hi"


history.clear()

assert len(history.get()) == 0


print("✅ HistoryManager test passed")