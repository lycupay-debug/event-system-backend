"""PostgreSQL repository for durable cross-App event intake and state transitions."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.database import using_connection


_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "received": {"processing", "failed"},
    "processing": {"processed", "failed", "dead_letter"},
    "failed": {"received", "dead_letter"},
    "processed": set(),
    "dead_letter": set(),
}


def record_event(
    event_id: str,
    source_app: str,
    event_type: str,
    payload: dict[str, Any],
    *,
    received_at: datetime | str | None = None,
    connection: Connection[Any] | None = None,
) -> bool:
    """Insert an event once. Return False when the event_id already exists."""
    if not event_id or len(event_id) > 180:
        raise ValueError("event_id must contain 1 to 180 characters")
    if not source_app or len(source_app) > 80:
        raise ValueError("source_app must contain 1 to 80 characters")
    if not event_type or len(event_type) > 200:
        raise ValueError("event_type must contain 1 to 200 characters")
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dictionary")

    with using_connection(connection) as conn, conn.cursor(row_factory=dict_row) as cur:
        if received_at is None:
            cur.execute(
                """
                INSERT INTO bridge.events (event_id, source_app, event_type, payload)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
                RETURNING event_id
                """,
                (event_id, source_app, event_type, Jsonb(payload)),
            )
        else:
            cur.execute(
                """
                INSERT INTO bridge.events (event_id, source_app, event_type, payload, received_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
                RETURNING event_id
                """,
                (event_id, source_app, event_type, Jsonb(payload), received_at),
            )
        return cur.fetchone() is not None


def get_event(
    event_id: str,
    *,
    connection: Connection[Any] | None = None,
) -> dict[str, Any] | None:
    """Return an event record, including its JSON payload, or None when absent."""
    with using_connection(connection) as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT * FROM bridge.events WHERE event_id = %s", (event_id,))
        return cur.fetchone()


def list_events(
    status: str = "received",
    *,
    limit: int = 100,
    connection: Connection[Any] | None = None,
) -> list[dict[str, Any]]:
    """List events in one state in stable receive order."""
    if status not in _ALLOWED_TRANSITIONS:
        raise ValueError("unsupported event status")
    if not 1 <= limit <= 1000:
        raise ValueError("limit must be between 1 and 1000")
    with using_connection(connection) as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT *
            FROM bridge.events
            WHERE status = %s
            ORDER BY received_at, event_id
            LIMIT %s
            """,
            (status, limit),
        )
        return list(cur.fetchall())


def transition_event(
    event_id: str,
    expected_status: str,
    new_status: str,
    *,
    error_type: str | None = None,
    connection: Connection[Any] | None = None,
) -> bool:
    """Compare-and-set an event state; return False if the state no longer matches."""
    if expected_status not in _ALLOWED_TRANSITIONS:
        raise ValueError("unsupported expected event status")
    if new_status not in _ALLOWED_TRANSITIONS[expected_status]:
        raise ValueError(f"event transition {expected_status!r} -> {new_status!r} is not allowed")
    if new_status == "failed" and not error_type:
        raise ValueError("error_type is required when marking an event failed")
    if error_type is not None and len(error_type) > 200:
        raise ValueError("error_type must not exceed 200 characters")

    with using_connection(connection) as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE bridge.events
            SET status = %s,
                attempts = attempts + CASE WHEN %s = 'processing' THEN 1 ELSE 0 END,
                last_error = CASE WHEN %s = 'failed' THEN %s ELSE NULL END,
                processed_at = CASE WHEN %s = 'processed' THEN clock_timestamp() ELSE processed_at END,
                updated_at = clock_timestamp()
            WHERE event_id = %s AND status = %s
            """,
            (new_status, new_status, new_status, error_type, new_status, event_id, expected_status),
        )
        return cur.rowcount == 1
