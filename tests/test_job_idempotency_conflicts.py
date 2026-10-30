"""Idempotency must identify one exact request, including structured JSON."""
import os
import tempfile
import unittest
from dottie.jobs import JobQueue

class IdempotencyConflictTests(unittest.TestCase):
    def test_same_key_different_work_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            queue = JobQueue(os.path.join(folder, "state.db"))
            original = queue.submit("dugan", {"task": 1}, "same-key")
            self.assertEqual(original, queue.submit("dugan", {"task": 1}, "same-key"))
            with self.assertRaises(ValueError):
                queue.submit("morita", {"task": 1}, "same-key")
            with self.assertRaises(ValueError):
                queue.submit("dugan", {"task": 2}, "same-key")
            self.assertEqual(queue.claim()["id"], original)
            queue.close()

    def test_json_round_trip_does_not_create_false_conflict(self):
        with tempfile.TemporaryDirectory() as folder:
            queue = JobQueue(os.path.join(folder, "state.db"))
            payload = {"items": [1, 2], "nested": {"active": True, "value": None}}
            first = queue.submit("dugan", payload, "structured")
            self.assertEqual(first, queue.submit("dugan", payload, "structured"))
            queue.close()
