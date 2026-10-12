"""Tests for the PostgreSQL operation interface.

Integration tests require DATABASE_URL and only use read-only metadata queries
or temporary tables that are dropped automatically.
"""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app import database


class DatabaseInterfaceTests(unittest.TestCase):
    def test_connect_rejects_missing_database_url_without_leaking_secrets(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "^DATABASE_URL is not configured$"):
                database.connect()

    def test_connection_metadata(self) -> None:
        info = database.inspect_connection()
        self.assertTrue(info["database"])
        self.assertTrue(info["user"])
        self.assertTrue(info["server_version"])
        self.assertIsInstance(info["is_superuser"], bool)

    def test_crud_round_trip_uses_temporary_table(self) -> None:
        result = database.probe_write()
        self.assertEqual(result["insert"], "passed")
        self.assertEqual(result["select"], "passed")
        self.assertEqual(result["update"], "passed")
        self.assertEqual(result["delete"], "passed")
        self.assertFalse(result["persistent_objects_created"])

    def test_batch_query_and_column_metadata_use_temporary_table(self) -> None:
        with database.transaction() as conn:
            database.execute(
                """
                CREATE TEMPORARY TABLE db_interface_batch_probe (
                    id integer PRIMARY KEY,
                    value text NOT NULL
                ) ON COMMIT DROP
                """,
                connection=conn,
            )
            database.execute_many(
                "INSERT INTO pg_temp.db_interface_batch_probe (id, value) VALUES (%s, %s)",
                [(1, "one"), (2, "two"), (3, "three")],
                connection=conn,
            )
            rows = database.fetch_all(
                "SELECT id, value FROM pg_temp.db_interface_batch_probe ORDER BY id",
                connection=conn,
            )
            self.assertEqual([row["value"] for row in rows], ["one", "two", "three"])
            temp_schema = database.fetch_one(
                "SELECT nspname FROM pg_namespace WHERE oid = pg_my_temp_schema()",
                connection=conn,
            )
            self.assertIsNotNone(temp_schema)
            columns = database.describe_table(
                "db_interface_batch_probe",
                schema=temp_schema["nspname"],
                connection=conn,
            )
            self.assertEqual([column["column_name"] for column in columns], ["id", "value"])

    def test_table_metadata_api(self) -> None:
        tables = database.list_tables()
        self.assertIsInstance(tables, list)


if __name__ == "__main__":
    unittest.main()
