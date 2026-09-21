import inspect
from contextlib import contextmanager
from functools import wraps
from time import perf_counter
from typing import Any, Iterator

from .logger import TraceLogger

from .context import (
    get_current_trace,
    reset_current_trace,
    set_current_trace,
)
from .event import TraceEventType, TraceStatus
from .logger import create_trace_logger


@contextmanager
def _trace_operation(
        trace: TraceLogger,
        start_event: TraceEventType,
        end_event: TraceEventType,
        *,
        error_event: TraceEventType | None = None,
        step: int | None = None,
        start_data: dict[str, Any] | None = None,
) -> Iterator[dict[str, Any]]:
    """
        Trace 公共执行模板。

        负责：
        - start event
        - duration
        - success event
        - exception event

        调用方只负责补充成功结果 data/status。
    """
    trace.record(
        start_event,
        step=step,
        data=start_data
    )

    start = perf_counter()

    result = {
        "status": TraceStatus.SUCCESS,
        "data": {},
    }

    try:
        yield result
    except Exception as exc:
        trace.record(
            error_event or end_event,
            step=step,
            status=TraceStatus.ERROR,
            duration_ms=(perf_counter() - start) * 1000,
            data={
                "error_type": type(exc).__name__,
                "message": str(exc),
            }
        )

        raise
    else:
        trace.record(
            end_event,
            step=step,
            status=result["status"],
            duration_ms=(perf_counter() - start) * 1000,
            data=result["data"],
        )


def trace_run():
    def decorator(func):
        signature = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            trace = create_trace_logger()

            # Trace 被关闭时，不影响正常业务执行
            if trace is None:
                return func(*args, **kwargs)

            # 按参数名绑定，而不是依赖 args[1] / args[2]
            bound = signature.bind_partial(
                *args,
                **kwargs
            )
            agent = bound.arguments.get("agent")
            input_text = bound.arguments.get("input_text")
            token = set_current_trace(trace)

            try:
                with _trace_operation(
                        trace=trace,
                        start_event=TraceEventType.RUN_START,
                        end_event=TraceEventType.RUN_FINISH,
                        error_event=TraceEventType.RUN_ERROR,
                        start_data={
                            "agent": (
                                    getattr(agent, "name", None)
                                    if agent is not None
                                    else None
                            ),
                            "input": input_text
                        }
                ) as trace_result:
                    result = func(*args, **kwargs)
                    trace_result["data"] = {
                        "output": result,
                    }
                    return result
            finally:
                reset_current_trace(token)

        return wrapper

    return decorator

def trace_model():
    def decorator(func):
        signature = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            trace = get_current_trace()

            if trace is None:
                return func(*args, **kwargs)

            bound = signature.bind_partial(
                *args,
                **kwargs
            )

            agent = bound.arguments.get("agent")
            state = bound.arguments.get("state")

            step = (
                getattr(state, "step", None)
                if state is not None
                else None
            )

            with _trace_operation(
                    trace=trace,
                    start_event=TraceEventType.MODEL_REQUEST,
                    end_event=TraceEventType.MODEL_RESPONSE,
                    step=step,
                    start_data={
                        "agent": (
                                getattr(agent, "name", None)
                                if agent is not None
                                else None
                        ),
                        "model": (
                                getattr(
                                    getattr(agent, "llm", None),
                                    "model",
                                    None,
                                )
                        ),
                    },
            ) as trace_result:
                response = func(*args, **kwargs)

                trace_result["data"] = {
                    "model": response.model,
                    "content": response.content,
                    "tool_calls": response.tool_calls,
                    "usage": response.usage,
                }
                return response
        return wrapper
    return decorator

def trace_tool():
    def decorator(func):
        signature = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            trace = get_current_trace()

            if trace is None:
                return func(*args, **kwargs)

            bound = signature.bind_partial(
                *args,
                **kwargs
            )

            agent = bound.arguments.get("agent")
            tool_call = bound.arguments.get("tool_call")

            tool_call_id = (
                getattr(tool_call, "id", None)
                if tool_call is not None
                else None
            )

            tool_name = (
                getattr(tool_call, "name", None)
                if tool_call is not None
                else None
            )

            arguments = (
                getattr(tool_call, "arguments", None)
                if tool_call is not None
                else None
            )

            with _trace_operation(
                    trace=trace,
                    start_event=TraceEventType.TOOL_CALL,
                    end_event=TraceEventType.TOOL_RESULT,
                    start_data={
                        "agent": (
                            getattr(agent, "name", None)
                            if agent is not None
                            else None
                        ),
                        "tool_call_id": tool_call_id,
                        "tool_name": tool_name,
                        "arguments": arguments,
                    },
            ) as trace_result:

                response = func(*args, **kwargs)

                tool_status = getattr(
                    getattr(response, "status", None),
                    "value",
                    None,
                )

                trace_result["status"] = (
                    TraceStatus.SUCCESS
                    if tool_status == "success"
                    else TraceStatus.ERROR
                )

                trace_result["data"] = {
                    "tool_call_id": tool_call_id,
                    "tool_name": tool_name,
                    "tool_status": tool_status,
                    "text": getattr(response, "text", None),
                    "error_info": getattr(
                        response,
                        "error_info",
                        None,
                    ),
                }

                return response

        return wrapper

    return decorator
