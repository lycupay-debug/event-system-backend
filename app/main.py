"""Feishu Bitable record-change listener using the official Python SDK."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any

import lark_oapi as lark
from lark_oapi.api.drive.v1 import P2DriveFileBitableRecordChangedV1

from app.bitable_parser import build_structured_event
from app.event_processor import EventProcessor, derive_event_id

EVENT_TYPE = "p2.drive.file.bitable_record_changed_v1"
EVENT_PROCESSOR: EventProcessor | None = None


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
        return _to_jsonable(
            {key: item for key, item in attributes.items() if not key.startswith("_")}
        )
    return str(value)


def on_bitable_record_changed(data: P2DriveFileBitableRecordChangedV1) -> None:
    """Persist the event before handing it to the single-file processing loop."""
    event = getattr(data, "event", None)
    if event is None:
        logger.warning("Received %s without an event body", EVENT_TYPE)
        return

    event_payload = _to_jsonable(event)
    header_value = _to_jsonable(getattr(data, "header", None))
    header = header_value if isinstance(header_value, dict) else {}
    event_id = derive_event_id(header, event_payload)
    document = {
        "event_id": event_id,
        "event_type": EVENT_TYPE,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "header": header,
        "event": event_payload,
    }

    if EVENT_PROCESSOR is not None:
        EVENT_PROCESSOR.submit(document)

    logger.info(
        "bitable_record_changed %s",
        json.dumps(
            {
                **document,
                "structured": build_structured_event(event_payload),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    )


def build_event_handler() -> lark.EventDispatcherHandler:
    """Build the SDK dispatcher for the typed v2 Bitable change event."""
    return (
        lark.EventDispatcherHandler.builder("", "", lark.LogLevel.INFO)
        .register_p2_drive_file_bitable_record_changed_v1(on_bitable_record_changed)
        .build()
    )


def main() -> None:
    global EVENT_PROCESSOR

    configure_logging()
    app_id = os.getenv("LARK_APP_ID", "").strip()
    app_secret = os.getenv("LARK_APP_SECRET", "").strip()
    if not app_id or not app_secret:
        raise SystemExit(
            "Missing LARK_APP_ID or LARK_APP_SECRET. "
            "Copy .env.example to .env and configure the app credentials."
        )

    EVENT_PROCESSOR = EventProcessor()
    EVENT_PROCESSOR.start()

    event_handler = build_event_handler()
    logger.info("Starting Feishu WebSocket listener for %s", EVENT_TYPE)
    client = lark.ws.Client(
        app_id,
        app_secret,
        log_level=lark.LogLevel.INFO,
        event_handler=event_handler,
        auto_reconnect=True,
    )
    try:
        client.start()
    finally:
        if EVENT_PROCESSOR is not None:
            EVENT_PROCESSOR.stop()


if __name__ == "__main__":
    main()
