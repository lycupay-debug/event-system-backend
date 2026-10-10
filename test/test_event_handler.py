"""Unit tests for event registration, raw logging, and structured change parsing."""

import json
import unittest
from types import SimpleNamespace

from app.main import (
    EVENT_TYPE,
    build_event_handler,
    build_structured_event,
    on_bitable_record_changed,
)


class EventHandlerTests(unittest.TestCase):
    def test_bitable_record_change_event_is_registered(self) -> None:
        handler = build_event_handler()
        self.assertIn(EVENT_TYPE, handler._processorMap)
        self.assertTrue(handler._processorMap)

    def test_callback_accepts_empty_event_without_raising(self) -> None:
        class EmptyEvent:
            event = None

        on_bitable_record_changed(EmptyEvent())  # type: ignore[arg-type]

    def test_callback_logs_raw_and_structured_payloads(self) -> None:
        event = SimpleNamespace(
            file_type="bitable",
            file_token="test_file_token",
            table_id="test_table_id",
            revision=7,
            update_time=1791612012,
            action_list=[
                SimpleNamespace(
                    action="record_edited",
                    record_id="rec_test123",
                    before_value=[
                        SimpleNamespace(
                            field_id="fld_unchanged",
                            field_value='[{"type":"text","text":"423424"}]',
                            field_identity_value=None,
                        ),
                        SimpleNamespace(
                            field_id="fld_changed",
                            field_value="",
                            field_identity_value=None,
                        ),
                    ],
                    after_value=[
                        SimpleNamespace(
                            field_id="fld_changed",
                            field_value='[{"text":"你好啊啊","type":"text"}]',
                            field_identity_value=None,
                        ),
                        SimpleNamespace(
                            field_id="fld_unchanged",
                            field_value='[{"type":"text","text":"423424"}]',
                            field_identity_value=None,
                        ),
                    ],
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
        self.assertEqual(payload["event"]["action_list"][0]["action"], "record_edited")
        self.assertEqual(payload["event"]["action_list"][0]["record_id"], "rec_test123")

        changes = payload["structured"]["actions"][0]["changes"]
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["field_id"], "fld_changed")
        self.assertIsNone(changes[0]["before"])
        self.assertEqual(changes[0]["after"], [{"text": "你好啊啊", "type": "text"}])

    def test_structured_event_handles_invalid_nested_json(self) -> None:
        structured = build_structured_event(
            {
                "action_list": [
                    {
                        "action": "record_edited",
                        "record_id": "rec_invalid",
                        "before_value": [{"field_id": "fld", "field_value": "old"}],
                        "after_value": [{"field_id": "fld", "field_value": "not-json"}],
                    }
                ]
            }
        )
        changes = structured["actions"][0]["changes"]
        self.assertEqual(changes, [{"field_id": "fld", "before": "old", "after": "not-json"}])

    def test_missing_field_on_one_side_is_treated_as_empty(self) -> None:
        structured = build_structured_event(
            {
                "action_list": [
                    {
                        "action": "record_edited",
                        "record_id": "rec_added",
                        "before_value": [],
                        "after_value": [{"field_id": "fld_new", "field_value": '"value"'}],
                    }
                ]
            }
        )
        self.assertEqual(
            structured["actions"][0]["changes"],
            [{"field_id": "fld_new", "before": None, "after": "value"}],
        )


if __name__ == "__main__":
    unittest.main()
