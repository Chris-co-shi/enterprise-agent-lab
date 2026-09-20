from functools import wraps
from time import perf_counter

from .logger import create_trace_logger
from .context import set_current_trace, reset_current_trace, get_current_trace
from .event import TraceEventType, TraceStatus


def trace_agent():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            trace = create_trace_logger()
            if trace is None:
                return func(*args, **kwargs)
            token = set_current_trace(trace)
            start = perf_counter()
            try:
                trace.record(
                    TraceEventType.AGENT_START,
                    data={
                        "input": args[1] if len(args) > 1 else None
                    }
                )
                result = func(*args, **kwargs)
                trace.record(
                    TraceEventType.AGENT_FINISH,
                    status=TraceStatus.SUCCESS,
                    duration_ms=(perf_counter() - start) * 1000,
                    data={
                        "output": result
                    }
                )
                return result

            except Exception as exc:
                trace.record(
                    TraceEventType.AGENT_ERROR,
                    status=TraceStatus.ERROR,
                    duration_ms=(perf_counter() - start) * 1000,
                    data={
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                    }
                )

                raise

            finally:
                reset_current_trace(token)

        return wrapper

    return decorator


def trace_llm():
    def decorator(func):
        @wraps(func)
        def wrapper(self, messages, *args, **kwargs):
            trace = get_current_trace()

            if trace is None:
                return func(
                    self,
                    messages,
                    *args,
                    **kwargs
                )

            trace.record(
                TraceEventType.LLM_REQUEST,
                data={
                    "model": self.model,
                    "messages": messages,
                    "tools": kwargs.get("tools"),
                }
            )

            start = perf_counter()

            try:
                response = func(
                    self,
                    messages,
                    *args,
                    **kwargs
                )

                trace.record(
                    TraceEventType.LLM_RESPONSE,
                    status=TraceStatus.SUCCESS,
                    duration_ms=(perf_counter() - start) * 1000,
                    data={
                        "model": response.model,
                        "content": response.content,
                        "tool_calls": response.tool_calls,
                        "usage": response.usage,
                    }
                )

                return response

            except Exception:
                # 当前没有 LLM_ERROR EventType
                # Agent 最外层最终会记录 AGENT_ERROR
                raise

        return wrapper

    return decorator


def trace_tool():
    def decorator(func):
        @wraps(func)
        def wrapper(self, arguments, *args, **kwargs):
            trace = get_current_trace()

            if trace is None:
                return func(
                    self,
                    arguments,
                    *args,
                    **kwargs
                )

            trace.record(
                TraceEventType.TOOL_CALL,
                data={
                    "tool_name": self.name,
                    "arguments": arguments,
                }
            )

            start = perf_counter()

            try:
                response = func(
                    self,
                    arguments,
                    *args,
                    **kwargs
                )

                status = (
                    TraceStatus.SUCCESS
                    if response.status.value == "success"
                    else TraceStatus.ERROR
                )

                trace.record(
                    TraceEventType.TOOL_RESULT,
                    status=status,
                    duration_ms=(perf_counter() - start) * 1000,
                    data={
                        "tool_name": self.name,
                        "response": response,
                    }
                )

                return response

            except Exception as exc:
                trace.record(
                    TraceEventType.TOOL_RESULT,
                    status=TraceStatus.ERROR,
                    duration_ms=(perf_counter() - start) * 1000,
                    data={
                        "tool_name": self.name,
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                    }
                )

                raise

        return wrapper

    return decorator