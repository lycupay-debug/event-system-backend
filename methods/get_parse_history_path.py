from __future__ import annotations

from pathlib import Path

from methods._event_id import normalize_event_id


def get_parse_history_path(event_id: str) -> Path:
    """Return the relative JSON path for a completed event history record."""
    return Path("data") / "parse_history" / f"{normalize_event_id(event_id)}.json"
