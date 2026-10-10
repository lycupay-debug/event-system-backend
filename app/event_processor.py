from __future__ import annotations

import hashlib
import json
import logging
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.bitable_parser import build_structured_event
from core.json_store import JSONStore
from methods.get_parse_history_path import get_parse_history_path
from methods.get_pending_event_path import get_pending_event_path
from methods.get_task_path import get_task_path

logger = logging.getLogger("feishu_bridge.processor")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def derive_event_id(header: dict[str, Any] | None, event: dict[str, Any]) -> str:
    """Prefer the platform event ID; use a stable digest when it is unavailable."""
    candidate = header.get("event_id") if isinstance(header, dict) else None
    if isinstance(candidate, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,180}", candidate):
        return candidate
    canonical = json.dumps({"header": header or {}, "event": event}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class EventProcessor:
    """Persist incoming events first, then process pending files on one worker."""

    def __init__(self, base_dir: str | Path | None = None, poll_seconds: float = 1.0) -> None:
        self.project_root = Path(base_dir).resolve() if base_dir is not None else Path(__file__).resolve().parent.parent
        self.store = JSONStore(self.project_root)
        self.poll_seconds = poll_seconds
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="event-processor", daemon=True)
        self._thread.start()
        self._wake.set()

    def stop(self, timeout: float = 5.0) -> None:
        self._stop.set()
        self._wake.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)

    def submit(self, event_document: dict[str, Any]) -> str:
        event_id = event_document.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("event_document is missing event_id")
        relative_path = get_pending_event_path(event_id)
        self.store.save(relative_path, event_document)
        self._wake.set()
        logger.info("EVENT_PERSISTED event_id=%s path=%s", event_id, relative_path.as_posix())
        return event_id

    def process_pending_once(self) -> int:
        pending_dir = self.project_root / "data" / "pending_events"
        if not pending_dir.exists():
            return 0
        processed = 0
        for pending_path in sorted(pending_dir.glob("*.json")):
            event_id = pending_path.stem
            history_path = get_parse_history_path(event_id)
            try:
                if (self.project_root / history_path).exists():
                    pending_path.unlink(missing_ok=True)
                    continue
                document = self.store.load(pending_path.relative_to(self.project_root))
                event = document.get("event")
                if not isinstance(event, dict):
                    raise ValueError("pending event is missing an event object")
                structured = build_structured_event(event)
                task = {
                    "event_id": event_id,
                    "event_type": document.get("event_type"),
                    "received_at": document.get("received_at"),
                    "status": "pending",
                    "structured": structured,
                }
                task_path = get_task_path(event_id)
                self.store.save(task_path, task)
                history = {
                    "event_id": event_id,
                    "event_type": document.get("event_type"),
                    "received_at": document.get("received_at"),
                    "parsed_at": utc_now(),
                    "status": "parsed",
                    "source": "websocket",
                    "task_path": task_path.as_posix(),
                    "event": event,
                    "structured": structured,
                }
                self.store.save(history_path, history)
                pending_path.unlink(missing_ok=True)
                processed += 1
                logger.info("EVENT_PARSED event_id=%s task_path=%s history_path=%s", event_id, task_path.as_posix(), history_path.as_posix())
            except Exception:
                logger.exception("EVENT_PROCESS_FAILED event_id=%s path=%s", event_id, pending_path)
        return processed

    def _run(self) -> None:
        while not self._stop.is_set():
            self._wake.wait(self.poll_seconds)
            self._wake.clear()
            self.process_pending_once()
