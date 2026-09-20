from abc import ABC, abstractmethod

from trace.event import TraceEvent


class TraceSink(ABC):

    @abstractmethod
    def emit(self, event:TraceEvent) -> None:
        pass


class ConsoleTraceSink(TraceSink):

    def emit(self, event: TraceEvent) -> None:
        print(
            f"[TRACE] "
            f"{event.trace_id} "
            f"#{event.sequence} "
            f"{event.event_type.value} "
            f"status={event.status.value if event.status else '-'} "
            f"duration={event.duration_ms or '-'}ms "
            f"data={event.data}"
        )