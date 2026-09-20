from typing import Any

from pydantic import TypeAdapter


def python_type_to_json_schema(
        annotation: Any
) -> dict[str, Any]:
    return TypeAdapter(annotation).json_schema()