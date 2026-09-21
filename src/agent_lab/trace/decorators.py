import inspect
from functools import wraps
from time import perf_counter

from trace.context import get_current_trace

from .context import (
    reset_current_trace,
    set_current_trace,
)
from .event import TraceEventType, TraceStatus
from .logger import create_trace_logger


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
            start = perf_counter()

            try:
                trace.record(
                    TraceEventType.RUN_START,
                    data={
                        "agent": (
                            getattr(agent, "name", None)
                            if agent is not None
                            else None
                        ),
                        "input": input_text,
                    }
                )
                result = func(*args, **kwargs)

                trace.record(
                    TraceEventType.RUN_FINISH,
                    status=TraceStatus.SUCCESS,
                    duration_ms=(
                                        perf_counter() - start
                                ) * 1000,
                    data={
                        "output": result
                    }
                )

                return result
            except Exception as exc:
                trace.record(
                    TraceEventType.RUN_ERROR,
                    status=TraceStatus.ERROR,
                    duration_ms=(
                                        perf_counter() - start
                                ) * 1000,
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

            trace.record(
                TraceEventType.MODEL_REQUEST,
                step=step,
                data={
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
                        if agent is not None
                        else None
                    ),
                }
            )
            start = perf_counter()
            try:
                response = func(*args, **kwargs)
                trace.record(
                    TraceEventType.MODEL_RESPONSE,
                    step=step,
                    status=TraceStatus.SUCCESS,
                    duration_ms=(
                                        perf_counter() - start
                                ) * 1000,
                    data={
                        "model": response.model,
                        "content": response.content,
                        "tool_calls": response.tool_calls,
                        "usage": response.usage,
                    }
                )
                return response
            except Exception as exc:
                trace.record(
                    TraceEventType.MODEL_RESPONSE,
                    step=step,
                    status=TraceStatus.ERROR,
                    duration_ms=(
                                        perf_counter() - start
                                ) * 1000,
                    data={
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                    }
                )

                raise

        return wrapper

    return decorator
