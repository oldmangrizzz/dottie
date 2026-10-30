"""AEGIS shared experiences require explicit participants and preserve private boundaries."""
import os
import tempfile
import unittest
from dottie.aegis import AgentRegistry
from dottie.collaboration import CollaborationJournal

class CollaborationTests(unittest.TestCase):
    def test_shared_experience_requires_participants_and_persists(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "state.db")
            agents = AgentRegistry(path)
            journal = CollaborationJournal(path)
            event_id = journal.record(
                "mission-17", ["dugan", "morita"], "resolved conflicting sources",
                {"outcome": "unresolved", "source_ids": ["doc-1", "doc-2"]})
            self.assertEqual(len(journal.history("dugan")), 1)
            self.assertEqual(len(journal.history("morita")), 1)
            self.assertEqual(journal.history("jones"), [])
            journal.close()
            reopened = CollaborationJournal(path)
            self.assertEqual(reopened.history("morita")[0]["id"], event_id)
            with self.assertRaises(ValueError):
                reopened.record("mission-18", ["dugan", "dugan"], "invalid", {})
            with self.assertRaises(LookupError):
                reopened.record("mission-18", ["dugan", "unknown"], "invalid", {})
            reopened.close()
            agents.close()

if __name__ == "__main__":
    unittest.main()
