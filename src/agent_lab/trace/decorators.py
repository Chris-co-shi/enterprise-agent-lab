from functools import wraps
from time import perf_counter

from .logger import create_trace_logger
from .context import set_current_trace, reset_current_trace
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
