"""Unit tests for the event registration and payload logging."""

import json
import unittest
from types import SimpleNamespace

from app.main import EVENT_TYPE, build_event_handler, on_bitable_record_changed


class EventHandlerTests(unittest.TestCase):
    def test_bitable_record_change_event_is_registered(self) -> None:
        handler = build_event_handler()
        self.assertIn(EVENT_TYPE, handler._processorMap)
        self.assertTrue(handler._processorMap)

    def test_callback_accepts_empty_event_without_raising(self) -> None:
        class EmptyEvent:
            event = None

        on_bitable_record_changed(EmptyEvent())  # type: ignore[arg-type]

    def test_callback_logs_action_list_and_changed_field_ids(self) -> None:
        event = SimpleNamespace(
            file_type="bitable",
            file_token="test_file_token",
            table_id="test_table_id",
            revision=7,
            update_time=1791612012,
            action_list=[
                SimpleNamespace(
                    action_type="update_record",
                    record_id="rec_test123",
                    field_ids=["fld_test456"],
                )
            ],
        )
        data = SimpleNamespace(event=event)

        with self.assertLogs("feishu_bridge.events", level="INFO") as captured:
            on_bitable_record_changed(data)  # type: ignore[arg-type]

        message = captured.output[0].split("bitable_record_changed ", 1)[1]
        payload = json.loads(message)
        self.assertEqual(payload["event_type"], EVENT_TYPE)
        self.assertEqual(payload["event"]["revision"], 7)
        self.assertEqual(
            payload["event"]["action_list"][0]["action_type"],
            "update_record",
        )
        self.assertEqual(
            payload["event"]["action_list"][0]["record_id"],
            "rec_test123",
        )
        self.assertEqual(
            payload["event"]["action_list"][0]["field_ids"],
            ["fld_test456"],
        )


if __name__ == "__main__":
    unittest.main()
