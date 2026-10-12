"""Integration tests for durable event repository behavior."""
from __future__ import annotations

import unittest
from uuid import uuid4

from app import event_repository
from app.database import connect


class EventRepositoryTests(unittest.TestCase):
    def test_idempotent_insert_and_compare_and_set_transitions(self) -> None:
        event_id = "repository_test_" + uuid4().hex
        payload = {"header": {"event_id": event_id}, "event": {"test": True}}

        with connect() as conn:
            with conn.transaction(force_rollback=True):
                conn.execute("SET LOCAL ROLE app_runtime")
                self.assertTrue(
                    event_repository.record_event(
                        event_id,
                        "feishu",
                        "repository.test",
                        payload,
                        connection=conn,
                    )
                )
                self.assertFalse(
                    event_repository.record_event(
                        event_id,
                        "feishu",
                        "repository.test",
                        {"different": True},
                        connection=conn,
                    )
                )

                stored = event_repository.get_event(event_id, connection=conn)
                self.assertIsNotNone(stored)
                self.assertEqual(stored["payload"], payload)
                self.assertEqual(stored["status"], "received")
                self.assertEqual(stored["attempts"], 0)

                self.assertTrue(
                    event_repository.transition_event(
                        event_id, "received", "processing", connection=conn
                    )
                )
                self.assertFalse(
                    event_repository.transition_event(
                        event_id, "received", "processing", connection=conn
                    )
                )
                self.assertTrue(
                    event_repository.transition_event(
                        event_id, "processing", "processed", connection=conn
                    )
                )

                stored = event_repository.get_event(event_id, connection=conn)
                self.assertEqual(stored["status"], "processed")
                self.assertEqual(stored["attempts"], 1)
                self.assertIsNotNone(stored["processed_at"])

    def test_failed_transition_requires_error_type(self) -> None:
        with self.assertRaisesRegex(ValueError, "error_type is required"):
            event_repository.transition_event("missing", "processing", "failed")

    def test_terminal_state_cannot_be_reopened(self) -> None:
        with self.assertRaisesRegex(ValueError, "not allowed"):
            event_repository.transition_event("missing", "processed", "received")

    def test_list_limit_is_bounded(self) -> None:
        with self.assertRaisesRegex(ValueError, "between 1 and 1000"):
            event_repository.list_events(limit=1001)


if __name__ == "__main__":
    unittest.main()
