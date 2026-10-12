"""Integration tests for the first PostgreSQL event/scheduler schema segment.

The write test uses a transaction configured to roll back, leaving no durable rows.
"""
from __future__ import annotations

import unittest
from uuid import uuid4

from app import database


EXPECTED_TABLES = {
    "events",
    "tasks",
    "idempotency_keys",
    "resource_locks",
}


class EventSchedulerSchemaTests(unittest.TestCase):
    def test_schema_tables_and_indexes_exist(self) -> None:
        tables = database.fetch_all(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """,
            ("bridge",),
        )
        self.assertEqual({row["table_name"] for row in tables}, EXPECTED_TABLES)

        indexes = database.fetch_all(
            """
            SELECT tablename, indexname
            FROM pg_indexes
            WHERE schemaname = %s
            """,
            ("bridge",),
        )
        index_names = {row["indexname"] for row in indexes}
        self.assertTrue({
            "events_status_received_idx",
            "events_type_received_idx",
            "tasks_ready_idx",
            "tasks_event_idx",
            "tasks_resource_status_idx",
            "idempotency_expiry_idx",
            "resource_locks_lease_idx",
        }.issubset(index_names))

    def test_application_role_owns_schema_tables(self) -> None:
        owners = database.fetch_all(
            """
            SELECT tablename, tableowner
            FROM pg_tables
            WHERE schemaname = %s
            """,
            ("bridge",),
        )
        self.assertEqual({row["tablename"] for row in owners}, EXPECTED_TABLES)
        self.assertEqual({row["tableowner"] for row in owners}, {"app_runtime"})

    def test_event_task_idempotency_and_lock_relationships(self) -> None:
        event_id = "schema_test_" + uuid4().hex
        resource_key = "schema-test-resource-" + uuid4().hex

        with database.connect() as conn:
            with conn.transaction(force_rollback=True):
                event = conn.execute(
                    """
                    INSERT INTO bridge.events (event_id, source_app, event_type, payload)
                    VALUES (%s, %s, %s, %s)
                    RETURNING event_id, status
                    """,
                    (event_id, "test", "schema.test", {"test": True}),
                ).fetchone()
                self.assertEqual(event["event_id"], event_id)
                self.assertEqual(event["status"], "received")

                task = conn.execute(
                    """
                    INSERT INTO bridge.tasks (event_id, task_type, resource_key, payload)
                    VALUES (%s, %s, %s, %s)
                    RETURNING task_id, status
                    """,
                    (event_id, "schema.test", resource_key, {"step": 1}),
                ).fetchone()
                self.assertEqual(task["status"], "queued")

                key = conn.execute(
                    """
                    INSERT INTO bridge.idempotency_keys
                        (scope, idempotency_key, request_hash, owner_task_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING status, owner_task_id
                    """,
                    ("schema-test", event_id, "test-hash", task["task_id"]),
                ).fetchone()
                self.assertEqual(key["status"], "processing")
                self.assertEqual(key["owner_task_id"], task["task_id"])

                lock = conn.execute(
                    """
                    INSERT INTO bridge.resource_locks
                        (resource_key, owner_task_id, acquired_at, lease_until, fencing_token)
                    VALUES (%s, %s, clock_timestamp(), clock_timestamp() + interval '30 seconds', 1)
                    RETURNING resource_key, owner_task_id, fencing_token
                    """,
                    (resource_key, task["task_id"]),
                ).fetchone()
                self.assertEqual(lock["resource_key"], resource_key)
                self.assertEqual(lock["owner_task_id"], task["task_id"])
                self.assertEqual(lock["fencing_token"], 1)


if __name__ == "__main__":
    unittest.main()
