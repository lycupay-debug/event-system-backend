"""Unit tests for the event registration; no network connection is made."""

import unittest

from app.main import EVENT_TYPE, build_event_handler, on_bitable_record_changed


class EventHandlerTests(unittest.TestCase):
    def test_bitable_record_change_event_is_registered(self) -> None:
        handler = build_event_handler()
        self.assertIn(EVENT_TYPE, [f"p2.{key[3:]}" for key in handler._processorMap])
        self.assertTrue(handler._processorMap)

    def test_callback_accepts_empty_event_without_raising(self) -> None:
        class EmptyEvent:
            event = None

        on_bitable_record_changed(EmptyEvent())  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
