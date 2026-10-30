"""Agent-private memories never appear in another agent's retrieval."""
import os
import tempfile
import unittest
from dottie.memory import ScopedMemory
from dottie.collaboration import CollaborationJournal
from dottie.aegis import AgentRegistry

class AgentMemoryIsolationTests(unittest.TestCase):
    def test_private_memory_is_siloed_despite_shared_mission(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "state.db")
            agents = AgentRegistry(path)
            memory = ScopedMemory(path)
            journal = CollaborationJournal(path)
            memory.put("agent-private", "dugan", "reflection", {"thought": "private"})
            journal.record("mission-1", ["dugan", "morita"], "worked together", {"result": "done"})
            self.assertIsNone(memory.get("agent-private", "morita", "reflection"))
            self.assertEqual(memory.get("agent-private", "dugan", "reflection"), {"thought": "private"})
            self.assertEqual(len(journal.history("morita")), 1)
            self.assertEqual(journal.history("jones"), [])
            journal.close()
            memory.close()
            agents.close()

if __name__ == "__main__":
    unittest.main()
