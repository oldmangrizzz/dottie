"""Cross-agent messages must not smuggle tool commands or private state."""
import os
import tempfile
import unittest
from dottie.aegis import AgentRegistry
from dottie.messaging import AgentMessages

class NaturalLanguageBoundaryTests(unittest.TestCase):
    def test_message_is_addressed_and_plain_text_only(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "state.db")
            registry = AgentRegistry(path)
            messages = AgentMessages(path)
            msg_id = messages.send("dugan", "morita", "Please review the evidence summary.")
            inbox = messages.inbox("morita")
            self.assertEqual(inbox[0]["id"], msg_id)
            self.assertEqual(inbox[0]["text"], "Please review the evidence summary.")
            self.assertEqual(messages.inbox("jones"), [])
            with self.assertRaises(TypeError):
                messages.send("dugan", "morita", {"tool": "execute", "args": []})
            with self.assertRaises(ValueError):
                messages.send("dugan", "morita", "hello\x00world")
            messages.close()
            registry.close()

if __name__ == "__main__":
    unittest.main()
