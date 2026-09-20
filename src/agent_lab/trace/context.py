from contextvars import ContextVar

from .logger import TraceLogger

_current_trace: ContextVar[TraceLogger | None] = ContextVar(
    "current_trace",
    default=None
)


def get_current_trace() -> TraceLogger | None:
    return _current_trace.get()


def set_current_trace(trace: TraceLogger):
    return _current_trace.set(trace)


def reset_current_trace(token) -> None:
    _current_trace.reset(token)
