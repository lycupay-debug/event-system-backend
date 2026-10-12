from __future__ import annotations

import unittest
from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import patch
from uuid import UUID

from app.event_ingress import persist_event


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.result = None
        self.queries = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query, params=None):
        self.queries.append((query, params))
        if query.lstrip().startswith("INSERT"):
            self.result = self.connection.insert_result
        else:
            self.result = self.connection.existing_result

    def fetchone(self):
        return self.result

    def fetchall(self):
        if self.connection.existing_results is not None:
            return self.connection.existing_results
        return [] if self.connection.existing_result is None else [self.connection.existing_result]


class FakeConnection:
    def __init__(self, insert_result=None, existing_result=None, existing_results=None):
        self.insert_result = insert_result
        self.existing_result = existing_result
        self.existing_results = existing_results
        self.cursor_instance = FakeCursor(self)

    def cursor(self):
        return self.cursor_instance


class EventIngressTests(unittest.TestCase):
    def setUp(self):
        self.received_at = datetime(2026, 10, 12, tzinfo=timezone.utc)
        self.document = {
            "event_id": "evt_123",
            "event_type": "p2.drive.file.bitable_record_changed_v1",
            "received_at": "2026-10-12T00:00:00+00:00",
            "header": {"event_id": "evt_123"},
            "event": {"file_token": "file_test"},
        }

    def run_with_connection(self, connection):
        @contextmanager
        def fake_transaction():
            yield connection

        with patch("app.event_ingress.database.transaction", fake_transaction):
            return persist_event(self.document, source="feishu")

    def test_new_event_is_inserted_with_uuid_and_stable_dedupe_key(self):
        inbox_id = UUID("11111111-1111-4111-8111-111111111111")
        conn = FakeConnection(
            insert_result={"id": inbox_id, "status": "RECEIVED", "received_at": self.received_at}
        )

        result = self.run_with_connection(conn)

        self.assertEqual(
            result,
            {
                "accepted": True,
                "duplicate": False,
                "inbox_id": str(inbox_id),
                "status": "RECEIVED",
                "received_at": self.received_at,
            },
        )
        query, params = conn.cursor_instance.queries[0]
        self.assertIn("event_system.event_inbox", query)
        self.assertIn("ON CONFLICT DO NOTHING", query)
        self.assertIsInstance(params[0], UUID)
        self.assertEqual(params[1:5], ("feishu", "evt_123", "evt_123", self.document["event_type"]))

    def test_duplicate_returns_existing_inbox_uuid(self):
        existing_id = UUID("22222222-2222-4222-8222-222222222222")
        conn = FakeConnection(
            insert_result=None,
            existing_result={"id": existing_id, "status": "RECEIVED", "received_at": self.received_at},
        )

        result = self.run_with_connection(conn)

        self.assertTrue(result["accepted"])
        self.assertTrue(result["duplicate"])
        self.assertEqual(result["inbox_id"], str(existing_id))
        self.assertEqual(len(conn.cursor_instance.queries), 2)

    def test_conflicting_dedupe_keys_matching_different_rows_is_not_acknowledged(self):
        first = {
            "id": UUID("44444444-4444-4444-8444-444444444444"),
            "status": "RECEIVED",
            "received_at": self.received_at,
        }
        second = {
            "id": UUID("55555555-5555-4555-8555-555555555555"),
            "status": "RECEIVED",
            "received_at": self.received_at,
        }
        conn = FakeConnection(insert_result=None, existing_results=[first, second])

        with self.assertRaisesRegex(RuntimeError, "different existing rows"):
            self.run_with_connection(conn)

    def test_unresolvable_conflict_is_not_acknowledged(self):
        conn = FakeConnection(insert_result=None, existing_result=None)

        with self.assertRaisesRegex(RuntimeError, "existing row could not be resolved"):
            self.run_with_connection(conn)

    def test_missing_stable_event_id_is_rejected_before_database_access(self):
        document = {**self.document, "event_id": ""}
        with patch("app.event_ingress.database.transaction") as transaction:
            with self.assertRaisesRegex(ValueError, "stable event_id"):
                persist_event(document)
            transaction.assert_not_called()

    def test_platform_event_id_is_optional(self):
        document = {**self.document, "header": {}}
        inbox_id = UUID("33333333-3333-4333-8333-333333333333")
        conn = FakeConnection(
            insert_result={"id": inbox_id, "status": "RECEIVED", "received_at": self.received_at}
        )

        with patch("app.event_ingress.database.transaction") as transaction:
            @contextmanager
            def fake_transaction():
                yield conn
            transaction.side_effect = fake_transaction
            result = persist_event(document)

        self.assertFalse(result["duplicate"])
        self.assertIsNone(conn.cursor_instance.queries[0][1][2])


if __name__ == "__main__":
    unittest.main()
