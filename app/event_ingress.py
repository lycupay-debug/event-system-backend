"""Durable PostgreSQL ingress for externally received events.

This module is intentionally not wired into the live listener until the
event_system.event_inbox schema and its transaction protocol are reviewed and
deployed. A successful return means the inbox transaction committed.
"""
from __future__ import annotations

from typing import Any
from uuid import uuid4

from psycopg.types.json import Jsonb

from app import database


def persist_event(event_document: dict[str, Any], *, source: str = "feishu") -> dict[str, Any]:
    """Persist an event idempotently and return the durable inbox identity.

    event_document.event_id is the stable deduplication key already derived
    by the ingress adapter. header.event_id is stored separately when the
    platform supplied it. The inbox UUID is generated only for the attempted
    new row; duplicate deliveries return the UUID of the existing row.
    """
    if not isinstance(event_document, dict):
        raise TypeError("event_document must be a dictionary")
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")

    event_id = event_document.get("event_id")
    event_type = event_document.get("event_type")
    if not isinstance(event_id, str) or not event_id:
        raise ValueError("event_document is missing a stable event_id")
    if not isinstance(event_type, str) or not event_type:
        raise ValueError("event_document is missing event_type")

    header = event_document.get("header")
    header = header if isinstance(header, dict) else {}
    platform_event_id = header.get("event_id")
    if not isinstance(platform_event_id, str) or not platform_event_id:
        platform_event_id = None

    attempted_inbox_id = uuid4()
    with database.transaction() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO event_system.event_inbox
                    (id, source, source_event_id, dedupe_key, event_type, payload)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING id, status, received_at
                """,
                (
                    attempted_inbox_id,
                    source,
                    platform_event_id,
                    event_id,
                    event_type,
                    Jsonb(event_document),
                ),
            )
            inserted = cur.fetchone()
            if inserted is not None:
                return {
                    "accepted": True,
                    "duplicate": False,
                    "inbox_id": str(inserted["id"]),
                    "status": inserted["status"],
                    "received_at": inserted["received_at"],
                }

            # ON CONFLICT can be triggered by either unique dedupe constraint.
            # Resolve the winner in the same transaction; never acknowledge an
            # unresolved conflict as successful persistence.
            cur.execute(
                """
                SELECT id, status, received_at
                FROM event_system.event_inbox
                WHERE source = %s
                  AND (
                      dedupe_key = %s
                      OR (%s IS NOT NULL AND source_event_id = %s)
                  )
                """,
                (source, event_id, platform_event_id, platform_event_id),
            )
            matches = cur.fetchall()
            if not matches:
                raise RuntimeError("Inbox insert conflicted but the existing row could not be resolved")

            matched_ids = {str(row["id"]) for row in matches}
            if len(matched_ids) != 1:
                raise RuntimeError(
                    "Inbox deduplication conflict matched different existing rows; refusing acknowledgement"
                )

            existing = matches[0]
            return {
                "accepted": True,
                "duplicate": True,
                "inbox_id": str(existing["id"]),
                "status": existing["status"],
                "received_at": existing["received_at"],
            }
