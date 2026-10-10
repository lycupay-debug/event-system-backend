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


def on_bitable_record_changed(
    data: P2DriveFileBitableRecordChangedV1,
) -> None:
    """Log a compact event summary; never dump the complete event payload."""
    event = getattr(data, "event", None)
    if event is None:
        logger.warning("Received %s without an event body", EVENT_TYPE)
        return

    action_list = getattr(event, "action_list", None) or []
    summary: dict[str, Any] = {
        "event_type": EVENT_TYPE,
        "file_type": getattr(event, "file_type", None),
        "file_token": getattr(event, "file_token", None),
        "table_id": getattr(event, "table_id", None),
        "revision": getattr(event, "revision", None),
        "action_count": len(action_list),
        "update_time": getattr(event, "update_time", None),
    }
    logger.info("bitable_record_changed %s", json.dumps(summary, ensure_ascii=False))


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
