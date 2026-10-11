from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from app.event_processor import EventProcessor
from methods.get_parse_history_path import get_parse_history_path
from methods.get_pending_event_path import get_pending_event_path


class N8NForwardingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.processor = EventProcessor(
            base_dir=self.root,
            webhook_url="https://n8n.example.test/webhook/ingress",
            webhook_token="test-token",
        )

    def tearDown(self) -> None:
        self.processor.stop()
        self.temp_dir.cleanup()

    def sample_document(self, event_id: str = "evt_forward_001") -> dict:
        return {
            "event_id": event_id,
            "event_type": "p2.drive.file.bitable_record_changed_v1",
            "received_at": "2026-10-10T00:00:00+00:00",
            "header": {"event_id": event_id},
            "event": {"file_token": "test_file", "table_id": "test_table", "action_list": []},
        }

    @staticmethod
    def accepted_response(event_id: str) -> MagicMock:
        response = MagicMock()
        response.status = 200
        response.read.return_value = json.dumps(
            {"ok": True, "accepted": True, "event_id": event_id}
        ).encode("utf-8")
        return response

    def test_successful_forward_sends_expected_body_and_removes_outbox(self) -> None:
        document = self.sample_document()
        self.processor.submit(document)

        with patch("app.event_processor.urlopen", return_value=self.accepted_response(document["event_id"])) as mocked:
            self.assertEqual(self.processor.process_pending_once(), 1)

        request = mocked.call_args.args[0]
        self.assertEqual(request.full_url, "https://n8n.example.test/webhook/ingress")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("X-bridge-token"), "test-token")
        self.assertEqual(json.loads(request.data.decode("utf-8")), {
            "event_id": document["event_id"],
            "event_type": document["event_type"],
            "event": document["event"],
        })
        self.assertFalse((self.root / get_pending_event_path(document["event_id"])).exists())
        self.assertFalse((self.root / "data" / "pending_n8n" / f'{document["event_id"]}.json').exists())
        self.assertTrue((self.root / get_parse_history_path(document["event_id"])).exists())

    def test_network_failure_keeps_source_and_outbox_for_retry(self) -> None:
        document = self.sample_document()
        self.processor.submit(document)

        with patch("app.event_processor.urlopen", side_effect=URLError("offline")):
            self.assertEqual(self.processor.process_pending_once(), 0)

        outbox_path = self.root / "data" / "pending_n8n" / f'{document["event_id"]}.json'
        pending_path = self.root / get_pending_event_path(document["event_id"])
        history_path = self.root / get_parse_history_path(document["event_id"])
        outbox = json.loads(outbox_path.read_text(encoding="utf-8"))

        self.assertTrue(outbox_path.exists())
        self.assertTrue(pending_path.exists())
        self.assertTrue(history_path.exists())
        self.assertEqual(outbox["attempts"], 1)
        self.assertEqual(outbox["last_error"], "URLError")
        self.assertIsNotNone(outbox["next_attempt_at"])

    def test_mismatched_acknowledgement_keeps_outbox(self) -> None:
        document = self.sample_document()
        self.processor.submit(document)
        with patch("app.event_processor.urlopen", return_value=self.accepted_response("another-event")):
            self.assertEqual(self.processor.process_pending_once(), 0)

        self.assertTrue((self.root / "data" / "pending_n8n" / f'{document["event_id"]}.json').exists())
        self.assertTrue((self.root / get_pending_event_path(document["event_id"])).exists())

    def test_partial_forwarding_configuration_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            EventProcessor(base_dir=self.root, webhook_url="https://n8n.example.test/webhook/ingress", webhook_token="")

    def test_forwarding_disabled_preserves_existing_local_processing(self) -> None:
        processor = EventProcessor(base_dir=self.root, webhook_url="", webhook_token="")
        document = self.sample_document("evt_local_only")
        processor.submit(document)
        self.assertEqual(processor.process_pending_once(), 1)
        self.assertTrue((self.root / get_parse_history_path(document["event_id"])).exists())
        self.assertFalse((self.root / "data" / "pending_n8n" / f'{document["event_id"]}.json').exists())


if __name__ == "__main__":
    unittest.main()
