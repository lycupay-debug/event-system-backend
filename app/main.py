"""Feishu Bitable record-change listener using the official Python SDK.

The service receives events only. Business processing and n8n forwarding are
intentionally out of scope until real event delivery has been verified.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any

import lark_oapi as lark
from lark_oapi.api.drive.v1 import P2DriveFileBitableRecordChangedV1

EVENT_TYPE = "p2.drive.file.bitable_record_changed_v1"


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stdout,
    )


logger = logging.getLogger("feishu_bridge.events")


def _to_jsonable(value: Any) -> Any:
    """Convert SDK models and nested values to JSON-compatible data."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(item) for item in value]

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        try:
            return _to_jsonable(to_dict())
        except Exception:
            pass

    attributes = getattr(value, "__dict__", None)
    if isinstance(attributes, dict):
        public_attributes = {
            key: item
            for key, item in attributes.items()
            if not key.startswith("_")
        }
        return _to_jsonable(public_attributes)

    return str(value)


def _decode_field_value(value: Any) -> Any:
    """Decode Feishu's JSON-encoded field_value while preserving unknown data."""
    if not isinstance(value, str):
        return value
    if value == "":
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def _field_map(values: Any) -> dict[str, dict[str, Any]]:
    """Index before/after field entries by field_id; list order is not stable."""
    if not isinstance(values, list):
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for item in values:
        if not isinstance(item, dict):
            continue
        field_id = item.get("field_id")
        if not isinstance(field_id, str) or not field_id:
            continue
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
                    {
                        "field_id": field_id,
                        "before": before_value,
                        "after": after_value,
                    }
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


def on_bitable_record_changed(
    data: P2DriveFileBitableRecordChangedV1,
) -> None:
    """Log both the original event and parsed changes."""
    event = getattr(data, "event", None)
    if event is None:
        logger.warning("Received %s without an event body", EVENT_TYPE)
        return

    event_payload = _to_jsonable(event)
    payload = {
        "event_type": EVENT_TYPE,
        "event": event_payload,
        "structured": build_structured_event(event_payload),
    }
    logger.info(
        "bitable_record_changed %s",
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
    )


def build_event_handler() -> lark.EventDispatcherHandler:
    """Build the SDK dispatcher for the typed v2 Bitable change event."""
    return (
        lark.EventDispatcherHandler.builder("", "", lark.LogLevel.INFO)
        .register_p2_drive_file_bitable_record_changed_v1(on_bitable_record_changed)
        .build()
    )


def main() -> None:
    configure_logging()

    app_id = os.getenv("LARK_APP_ID", "").strip()
    app_secret = os.getenv("LARK_APP_SECRET", "").strip()
    if not app_id or not app_secret:
        raise SystemExit(
            "Missing LARK_APP_ID or LARK_APP_SECRET. "
            "Copy .env.example to .env and configure the app credentials."
        )

    event_handler = build_event_handler()
    logger.info("Starting Feishu WebSocket listener for %s", EVENT_TYPE)

    client = lark.ws.Client(
        app_id,
        app_secret,
        log_level=lark.LogLevel.INFO,
        event_handler=event_handler,
        auto_reconnect=True,
    )
    # start() blocks while the SDK maintains the persistent connection.
    client.start()


if __name__ == "__main__":
    main()
