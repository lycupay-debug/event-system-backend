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
        except Exception:  # Fall back to public instance attributes below.
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


def on_bitable_record_changed(
    data: P2DriveFileBitableRecordChangedV1,
) -> None:
    """Log the full event body, including the action list and changed field IDs."""
    event = getattr(data, "event", None)
    if event is None:
        logger.warning("Received %s without an event body", EVENT_TYPE)
        return

    event_payload = _to_jsonable(event)
    payload = {
        "event_type": EVENT_TYPE,
        "event": event_payload,
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
