from __future__ import annotations

from pathlib import Path

from methods._event_id import normalize_event_id


def get_task_path(event_id: str) -> Path:
    """Return the relative JSON path for an event task file."""
    return Path("data") / "task_list" / f"{normalize_event_id(event_id)}.json"
