from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.event_processor import EventProcessor, derive_event_id
from core.json_store import JSONStore
from methods.get_parse_history_path import get_parse_history_path
from methods.get_pending_event_path import get_pending_event_path
from methods.get_task_path import get_task_path


class EventProcessorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.processor = EventProcessor(base_dir=self.root, poll_seconds=0.01)

    def tearDown(self) -> None:
        self.processor.stop()
        self.temp_dir.cleanup()

    def sample_document(self, event_id: str = "evt_test_001") -> dict:
        return {
            "event_id": event_id,
            "event_type": "p2.drive.file.bitable_record_changed_v1",
            "received_at": "2026-10-10T00:00:00+00:00",
            "header": {"event_id": event_id},
            "event": {
                "file_token": "test_file",
                "table_id": "test_table",
                "action_list": [
                    {
                        "action": "record_edited",
                        "record_id": "rec_test",
                        "before_value": [{"field_id": "fld_name", "field_value": '"old"'}],
                        "after_value": [{"field_id": "fld_name", "field_value": '"new"'}],
                    }
                ],
            },
        }

    def test_paths_are_relative_linux_paths_and_use_event_id(self) -> None:
        self.assertEqual(get_pending_event_path("evt_1").as_posix(), "data/pending_events/evt_1.json")
        self.assertEqual(get_task_path("evt_1").as_posix(), "data/task_list/evt_1.json")
        self.assertEqual(get_parse_history_path("evt_1").as_posix(), "data/parse_history/evt_1.json")

    def test_path_methods_reject_traversal(self) -> None:
        with self.assertRaises(ValueError):
            get_task_path("../outside")

    def test_submit_persists_event_before_processing(self) -> None:
        event_id = self.processor.submit(self.sample_document())
        pending = self.root / get_pending_event_path(event_id)
        self.assertTrue(pending.is_file())
        self.assertEqual(json.loads(pending.read_text(encoding="utf-8"))["event_id"], event_id)

    def test_process_writes_task_and_history_then_removes_pending_file(self) -> None:
        document = self.sample_document()
        self.processor.submit(document)
        self.assertEqual(self.processor.process_pending_once(), 1)

        task_path = self.root / get_task_path(document["event_id"])
        history_path = self.root / get_parse_history_path(document["event_id"])
        pending_path = self.root / get_pending_event_path(document["event_id"])
        task = json.loads(task_path.read_text(encoding="utf-8"))
        history = json.loads(history_path.read_text(encoding="utf-8"))

        self.assertEqual(task["event_id"], document["event_id"])
        self.assertEqual(task["status"], "pending")
        self.assertEqual(task["structured"]["actions"][0]["changes"][0]["after"], "new")
        self.assertEqual(history["status"], "parsed")
        self.assertEqual(history["event"], document["event"])
        self.assertFalse(pending_path.exists())

    def test_duplicate_event_is_not_parsed_twice(self) -> None:
        document = self.sample_document()
        self.processor.submit(document)
        self.assertEqual(self.processor.process_pending_once(), 1)
        history_path = self.root / get_parse_history_path(document["event_id"])
        original_history = history_path.read_text(encoding="utf-8")

        self.processor.submit(document)
        self.assertEqual(self.processor.process_pending_once(), 0)
        self.assertEqual(history_path.read_text(encoding="utf-8"), original_history)
        self.assertFalse((self.root / get_pending_event_path(document["event_id"])).exists())

    def test_pending_file_can_be_recovered_by_a_new_processor(self) -> None:
        document = self.sample_document()
        self.processor.submit(document)
        restarted = EventProcessor(base_dir=self.root)
        self.assertEqual(restarted.process_pending_once(), 1)
        self.assertTrue((self.root / get_parse_history_path(document["event_id"])).is_file())

    def test_json_store_replaces_complete_json(self) -> None:
        store = JSONStore(self.root)
        store.save("data/sample.json", {"version": 1, "value": "old"})
        store.save("data/sample.json", {"version": 2, "value": "new"})
        self.assertEqual(store.load("data/sample.json"), {"version": 2, "value": "new"})
        self.assertEqual(list((self.root / "data").glob("*.tmp")), [])

    def test_event_id_fallback_is_stable(self) -> None:
        event = {"file_token": "file", "table_id": "table"}
        first = derive_event_id({}, event)
        second = derive_event_id({}, event)
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("sha256_"))


if __name__ == "__main__":
    unittest.main()
