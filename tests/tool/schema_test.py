from agent_lab.core.schema import python_type_to_json_schema


def test_int_schema():
    schema = python_type_to_json_schema(int)

    assert schema == {
        "type": "integer"
    }


def test_string_schema():
    schema = python_type_to_json_schema(str)

    assert schema == {
        "type": "string"
    }


def test_list_schema():
    schema = python_type_to_json_schema(list[str])

    assert schema == {
        "type": "array",
        "items": {
            "type": "string"
        }
    }


def test_optional_schema():
    schema = python_type_to_json_schema(str | None)

    print(schema)