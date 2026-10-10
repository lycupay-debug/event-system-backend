from __future__ import annotations

import json
from typing import Any


def _decode_field_value(value: Any) -> Any:
    """Decode JSON-encoded field values while preserving unknown values."""
    if not isinstance(value, str):
        return value
    if value == "":
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def _field_map(values: Any) -> dict[str, dict[str, Any]]:
    """Index before/after field entries by field ID."""
    if not isinstance(values, list):
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for item in values:
        if not isinstance(item, dict):
            continue
        field_id = item.get("field_id")
        if isinstance(field_id, str) and field_id:
            indexed[field_id] = item
    return indexed


def build_structured_event(event_payload: dict[str, Any]) -> dict[str, Any]:
    """Build changed-field details without discarding the original event."""
    actions = event_payload.get("action_list")
    structured_actions: list[dict[str, Any]] = []

    if isinstance(actions, list):
        for action_item in actions:
            if not isinstance(action_item, dict):
                continue
            before_map = _field_map(action_item.get("before_value"))
            after_map = _field_map(action_item.get("after_value"))
            field_ids = list(dict.fromkeys([*before_map.keys(), *after_map.keys()]))
            changes: list[dict[str, Any]] = []

            for field_id in field_ids:
                before_item = before_map.get(field_id, {})
                after_item = after_map.get(field_id, {})
                before_value = _decode_field_value(before_item.get("field_value"))
                after_value = _decode_field_value(after_item.get("field_value"))
                if before_value == after_value:
                    continue
                changes.append(
                    {"field_id": field_id, "before": before_value, "after": after_value}
                )

            structured_actions.append(
                {
                    "action": action_item.get("action"),
                    "record_id": action_item.get("record_id"),
                    "changes": changes,
                }
            )

    return {
        "file_token": event_payload.get("file_token"),
        "table_id": event_payload.get("table_id"),
        "revision": event_payload.get("revision"),
        "update_time": event_payload.get("update_time"),
        "operator_id": event_payload.get("operator_id"),
        "actions": structured_actions,
    }
