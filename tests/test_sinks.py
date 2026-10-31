"""Unit tests for RedshiftSink record formatting (no Redshift connection needed)."""

from __future__ import annotations

import json
from types import SimpleNamespace

from target_redshift.sinks import RedshiftSink

SCHEMA = {
    "properties": {
        "id": {"type": ["string"]},
        "obj": {"type": ["object", "null"]},
        "arr": {"type": ["array", "null"], "items": {"type": "string"}},
        # tap-postgres JSON/JSONB columns: every type, loaded as VARCHAR but serialised like objects
        "jsonb": {"type": ["string", "number", "integer", "array", "object", "boolean"]},
    }
}


def _format(records: list[dict]) -> list[dict]:
    stub = SimpleNamespace(schema=SCHEMA, conformed_schema=SCHEMA, conform_record=lambda record: record)
    return RedshiftSink.format_records_as_csv(stub, records)  # type: ignore[arg-type]


def test_text_none_in_json_values_is_kept() -> None:
    """Text "None" inside object/array values must survive serialisation."""
    record = {
        "id": "xNonex",
        "obj": {"id": "xNonex", "nested": {"pi": "pi_3TZmolIpYlPRShsd1uNonenv"}, "missing": None},
        "arr": ["xNonex", "None"],
        "jsonb": ["OTHER", "None of your business"],
    }
    (row,) = _format([record])
    loaded = {key: row[key] if key == "id" else json.loads(row[key]) for key in record}
    assert loaded == record  # noqa: S101
