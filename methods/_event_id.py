from __future__ import annotations

import re

_EVENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,180}$")


def normalize_event_id(event_id: str) -> str:
    """Validate an event ID before using it as a filename component."""
    if not isinstance(event_id, str) or not _EVENT_ID_PATTERN.fullmatch(event_id):
        raise ValueError("event_id must contain only letters, digits, underscores, or hyphens")
    return event_id
