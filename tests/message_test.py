from agent_lab.core import Message, ToolCall


tool_call = ToolCall(
    id="call_001",
    name="add",
    arguments={
        "a": 12,
        "b": 8
    }
)

assistant_message = Message(
    role="assistant",
    tool_calls=[tool_call]
)

tool_message = Message(
    role="tool",
    content="20",
    tool_call_id="call_001"
)

print(assistant_message)
print(tool_message)