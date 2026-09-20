import json
from abc import ABC, abstractmethod
from pathlib import Path

from .event import TraceEvent
from .serializer import serialize_event


class TraceSink(ABC):

    @abstractmethod
    def emit(self, event: TraceEvent) -> None:
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


class JsonlTraceSink(TraceSink):

    def __init__(
            self,
            path: str | Path
    ):
        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def emit(
            self,
            event: TraceEvent
    ) -> None:
        payload = serialize_event(event)

        with self.path.open(
                "a",
                encoding="utf-8"
        ) as file:
            file.write(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                )
            )
            file.write("\n")
