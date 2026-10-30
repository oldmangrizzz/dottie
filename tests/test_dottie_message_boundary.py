"""Dottie cannot bypass the inter-agent message boundary."""
import os
import tempfile
import unittest
from dottie.aegis import AgentRegistry
from dottie.messaging import AgentMessages

class DottieBoundaryTests(unittest.TestCase):
    def test_dottie_and_aegis_use_same_message_transport(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "state.db")
            registry = AgentRegistry(path)
            messages = AgentMessages(path)
            outbound = messages.send("dottie", "dugan", "Please summarize the mission evidence.")
            inbound = messages.send("dugan", "dottie", "I found two conflicting sources.")
            self.assertEqual(messages.inbox("dugan")[0]["id"], outbound)
            self.assertEqual(messages.inbox("dottie")[0]["id"], inbound)
            with self.assertRaises(TypeError):
                messages.send("dottie", "dugan", {"execute": "shell"})
            messages.close()
            registry.close()

if __name__ == "__main__":
    unittest.main()
