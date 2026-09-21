import inspect
from functools import wraps
from time import perf_counter

from trace.context import set_current_trace
from trace.event import TraceEventType
from trace.logger import create_trace_logger


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
