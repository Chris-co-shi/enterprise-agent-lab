from typing import Any
from uuid import uuid4

from .config import get_trace_config
from .event import TraceEvent, TraceStatus, TraceEventType
from .sink import TraceSink


class TraceLogger:
    def __init__(
            self,
            trace_id: str | None = None,
            sinks: list[TraceSink] | None = None
    ):
        self.trace_id = trace_id or uuid4().hex
        self._sequence = 0
        self._events: list[TraceEvent] = []
        self._sinks = sinks or []

    @property
    def events(self) -> list[TraceEvent]:
        return self._events

    def record(
            self,
            event_type: TraceEventType,
            *,
            iteration: int | None = None,
            status: TraceStatus | None = None,
            duration_ms: float | None = None,
            data: dict[str, Any] | None = None
    ) -> TraceEvent:
        self._sequence+= 1

        event = TraceEvent(
            trace_id=self.trace_id,
            sequence=self._sequence,
            event_type=event_type,
            iteration=iteration,
            status=status,
            duration_ms=duration_ms,
            data={} if data is None else dict(data),
        )

        self._events.append(event)
        for sink in self._sinks:
            sink.emit(event)
        return event


def create_trace_logger() -> TraceLogger | None:
    config = get_trace_config()

    if not config.enabled:
        return None

    return TraceLogger(
        sinks=config.sinks
    )