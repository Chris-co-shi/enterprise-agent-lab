from dataclasses import is_dataclass, fields
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel

from .event import TraceEvent


def serialize_value(value: Any) -> Any:
    if value is None or isinstance(
            value,
            (str, int, bool, float)
    ):
        return value

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, type):
        return value.__name__

    if isinstance(value, BaseModel):
        return serialize_value(
            value.model_dump()
        )

    if is_dataclass(value):
        return {
            field.name: serialize_value(
                getattr(value, field.name)
            )
            for field in fields(value)
        }

    if isinstance(value, dict):
        return {
            str(key): serialize_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [
            serialize_value(item)
            for item in value
        ]

    # Tool 这类普通对象
    if (
            hasattr(value, "name")
            and hasattr(value, "description")
            and hasattr(value, "parameters")
    ):
        return {
            "name": serialize_value(value.name),
            "description": serialize_value(value.description),
            "parameters": serialize_value(value.parameters),
        }

    return str(value)


def serialize_event(
        event: TraceEvent
) -> dict[str, Any]:
    return {
        "trace_id": event.trace_id,
        "sequence": event.sequence,
        "event_type": event.event_type.value,
        "timestamp": event.timestamp.isoformat(),
        "step": event.step,
        "status": (
            event.status.value
            if event.status
            else None
        ),
        "duration_ms": event.duration_ms,
        "data": serialize_value(event.data),
    }
