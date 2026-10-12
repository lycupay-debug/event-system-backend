"""Tests for the PostgreSQL operation interface.

Integration tests require DATABASE_URL and only use read-only metadata queries
or a temporary table that is dropped automatically.
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

    def test_table_metadata_api(self) -> None:
        tables = database.list_tables()
        self.assertIsInstance(tables, list)
        for table in tables[:1]:
            columns = database.describe_table(table["table_name"], schema=table["table_schema"])
            self.assertIsInstance(columns, list)
            self.assertTrue(columns)


if __name__ == "__main__":
    unittest.main()
