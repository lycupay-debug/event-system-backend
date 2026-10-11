from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.bitable_parser import build_structured_event
from core.json_store import JSONStore
from methods.get_parse_history_path import get_parse_history_path
from methods.get_pending_event_path import get_pending_event_path
from methods.get_task_path import get_task_path

logger = logging.getLogger("feishu_bridge.processor")
EVENT_TYPE = "p2.drive.file.bitable_record_changed_v1"


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
    """Persist incoming events first, then parse and forward them on one worker.

    Forwarding uses a durable local outbox and at-least-once delivery. The receiver
    should deduplicate by event_id before performing any non-idempotent side effects.
    """

    def __init__(
        self,
        base_dir: str | Path | None = None,
        poll_seconds: float = 1.0,
        webhook_url: str | None = None,
        webhook_token: str | None = None,
        request_timeout: float = 10.0,
    ) -> None:
        self.project_root = Path(base_dir).resolve() if base_dir is not None else Path(__file__).resolve().parent.parent
        self.store = JSONStore(self.project_root)
        self.poll_seconds = poll_seconds
        self.webhook_url = os.getenv("N8N_WEBHOOK_URL", "").strip() if webhook_url is None else webhook_url.strip()
        self.webhook_token = os.getenv("N8N_WEBHOOK_TOKEN", "").strip() if webhook_token is None else webhook_token.strip()
        if bool(self.webhook_url) != bool(self.webhook_token):
            raise ValueError("N8N_WEBHOOK_URL and N8N_WEBHOOK_TOKEN must be configured together")
        self.request_timeout = request_timeout
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def forwarding_enabled(self) -> bool:
        return bool(self.webhook_url and self.webhook_token)

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

    def _outbox_path(self, event_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,180}", event_id):
            raise ValueError("event_id contains unsupported path characters")
        return Path("data") / "pending_n8n" / f"{event_id}.json"

    def _create_outbox(self, event_id: str, document: dict[str, Any]) -> None:
        payload = {
            "event_id": event_id,
            "event_type": document.get("event_type"),
            "event": document.get("event"),
        }
        self.store.save(
            self._outbox_path(event_id),
            {
                "event_id": event_id,
                "payload": payload,
                "attempts": 0,
                "next_attempt_at": None,
                "created_at": utc_now(),
            },
        )
        logger.info("N8N_OUTBOX_PERSISTED event_id=%s", event_id)

    def _deliver_outbox(self, event_id: str) -> bool:
        relative_path = self._outbox_path(event_id)
        absolute_path = self.project_root / relative_path
        if not absolute_path.is_file():
            return True
        if not self.forwarding_enabled:
            logger.error("N8N_FORWARD_CONFIG_MISSING event_id=%s; outbox retained", event_id)
            return False

        outbox = self.store.load(relative_path)
        next_attempt_at = outbox.get("next_attempt_at")
        if isinstance(next_attempt_at, str) and next_attempt_at:
            try:
                due = datetime.fromisoformat(next_attempt_at)
                if due > datetime.now(timezone.utc):
                    return False
            except ValueError:
                pass

        body = json.dumps(outbox["payload"], ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        request = Request(
            self.webhook_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Bridge-Token": self.webhook_token,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.request_timeout) as response:
                status = getattr(response, "status", 200)
                response_body = response.read()
            if not 200 <= status < 300:
                raise RuntimeError(f"unexpected HTTP status {status}")
            receipt = json.loads(response_body.decode("utf-8"))
            if not isinstance(receipt, dict) or receipt.get("accepted") is not True or receipt.get("event_id") != event_id:
                raise RuntimeError("webhook acknowledgement did not match event_id")
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, RuntimeError) as exc:
            attempts = int(outbox.get("attempts", 0)) + 1
            delay_seconds = min(300, 2 ** min(attempts, 8))
            outbox["attempts"] = attempts
            outbox["last_error"] = type(exc).__name__
            outbox["next_attempt_at"] = (datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)).isoformat()
            self.store.save(relative_path, outbox)
            logger.warning(
                "N8N_FORWARD_FAILED event_id=%s attempt=%s retry_in_seconds=%s error_type=%s",
                event_id,
                attempts,
                delay_seconds,
                type(exc).__name__,
            )
            return False

        absolute_path.unlink(missing_ok=True)
        logger.info("N8N_FORWARD_ACCEPTED event_id=%s http_status=%s", event_id, status)
        return True

    def process_pending_once(self) -> int:
        pending_dir = self.project_root / "data" / "pending_events"
        if not pending_dir.exists():
            return 0
        processed = 0
        for pending_path in sorted(pending_dir.glob("*.json")):
            event_id = pending_path.stem
            history_path = get_parse_history_path(event_id)
            try:
                outbox_path = self.project_root / self._outbox_path(event_id)
                if (self.project_root / history_path).exists():
                    if outbox_path.exists() and not self._deliver_outbox(event_id):
                        continue
                    pending_path.unlink(missing_ok=True)
                    continue

                document = self.store.load(pending_path.relative_to(self.project_root))
                event = document.get("event")
                if not isinstance(event, dict):
                    raise ValueError("pending event is missing an event object")

                structured = build_structured_event(event)
                task_path = get_task_path(event_id)
                task = {
                    "event_id": event_id,
                    "event_type": document.get("event_type"),
                    "received_at": document.get("received_at"),
                    "status": "pending",
                    "structured": structured,
                }
                self.store.save(task_path, task)

                # Persist the delivery intent before parse history and before removing
                # the source event. A process crash can therefore recover the send.
                if self.forwarding_enabled and not outbox_path.exists():
                    self._create_outbox(event_id, document)

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

                if outbox_path.exists() and not self._deliver_outbox(event_id):
                    continue
                pending_path.unlink(missing_ok=True)
                processed += 1
                logger.info(
                    "EVENT_PARSED event_id=%s task_path=%s history_path=%s",
                    event_id,
                    task_path.as_posix(),
                    history_path.as_posix(),
                )
            except Exception:
                logger.exception("EVENT_PROCESS_FAILED event_id=%s path=%s", event_id, pending_path)
        return processed

    def _run(self) -> None:
        while not self._stop.is_set():
            self._wake.wait(self.poll_seconds)
            self._wake.clear()
            self.process_pending_once()
