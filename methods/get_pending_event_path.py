from __future__ import annotations

from pathlib import Path

from methods._event_id import normalize_event_id


def get_pending_event_path(event_id: str) -> Path:
    """Return the relative JSON path for a durably received, pending event."""
    return Path("data") / "pending_events" / f"{normalize_event_id(event_id)}.json"
