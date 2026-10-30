"""AEGIS relationships persist independently of models and remain reciprocal."""
import os
import tempfile
import unittest
from dottie.aegis import AgentRegistry
from dottie.relationships import AgentRelationships

class RelationshipsTests(unittest.TestCase):
    def test_friendship_is_reciprocal_and_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "state.db")
            agents = AgentRegistry(path)
            relations = AgentRelationships(path)
            relations.befriend("dugan", "morita", "We trust each other's judgment")
            self.assertTrue(relations.are_friends("dugan", "morita"))
            self.assertTrue(relations.are_friends("morita", "dugan"))
            self.assertEqual(relations.friends("dugan")[0]["agent_id"], "morita")
            relations.close()
            relations = AgentRelationships(path)
            self.assertTrue(relations.are_friends("morita", "dugan"))
            relations.end_friendship("morita", "dugan")
            self.assertFalse(relations.are_friends("dugan", "morita"))
            relations.close()
            agents.close()

    def test_invalid_or_self_relationship_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "state.db")
            agents = AgentRegistry(path)
            relations = AgentRelationships(path)
            with self.assertRaises(ValueError):
                relations.befriend("dugan", "dugan", "same identity")
            with self.assertRaises(LookupError):
                relations.befriend("dugan", "unknown", "not an agent")
            relations.close()
            agents.close()

if __name__ == "__main__":
    unittest.main()
