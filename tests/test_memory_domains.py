import unittest

from dottie.memory import MemoryDomains


class MemoryDomainTests(unittest.TestCase):
    def test_owner_can_read_own_memory(self):
        memory = MemoryDomains()
        memory.add_private("dottie", "baseline")
        self.assertEqual(memory.read_private("dottie", "dottie"), ["baseline"])

    def test_agent_cannot_read_another_agent(self):
        memory = MemoryDomains()
        memory.add_private("aegis-1", "private")
        with self.assertRaises(PermissionError):
            memory.read_private("aegis-2", "aegis-1")

    def test_retrieved_context_does_not_become_autobiographical(self):
        memory = MemoryDomains()
        memory.provide_context("dottie", "retrieved report")
        self.assertEqual(memory.read_context("dottie"), ["retrieved report"])
        self.assertEqual(memory.read_private("dottie", "dottie"), [])

    def test_promotion_is_denied_even_with_token(self):
        memory = MemoryDomains()
        with self.assertRaises(PermissionError):
            memory.promote_private("dottie", "new fact", permission_token="untrusted")


if __name__ == "__main__":
    unittest.main()
