"""Verify independent AEGIS membership isolation against the real SQLite stores."""
import os
import tempfile
import unittest
from dottie.aegis import AgentRegistry
from dottie.identity import IdentityStore
from dottie.memberships import AgentMemberships

class MembershipIntegrationTests(unittest.TestCase):
    def test_independent_agent_memberships_and_revocation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "dottie.sqlite")
            registry = AgentRegistry(path)
            identities = IdentityStore(path)
            owner = identities.create_user("owner", "a sufficiently long password", "owner")
            researcher = identities.create_user("researcher", "another sufficiently long password", "researcher", owner)
            observer = identities.create_user("observer", "a third sufficiently long password", "viewer", owner)
            memberships = AgentMemberships(path)
            self.assertEqual(len(registry.list_agents()), 5)
            memberships.bootstrap_owner("dugan", owner)
            memberships.grant("dugan", researcher, "collaborator", owner)
            memberships.grant("dugan", observer, "observer", owner)
            self.assertTrue(memberships.allowed("dugan", researcher, "dispatch"))
            self.assertFalse(memberships.allowed("morita", researcher, "dispatch"))
            self.assertTrue(memberships.allowed("dugan", observer, "read"))
            self.assertFalse(memberships.allowed("dugan", observer, "dispatch"))
            with self.assertRaises(PermissionError):
                memberships.grant("dugan", observer, "operator", researcher)
            memberships.revoke("dugan", researcher, owner)
            self.assertFalse(memberships.allowed("dugan", researcher, "dispatch"))
            memberships.close()
            reopened = AgentMemberships(path)
            self.assertFalse(reopened.allowed("dugan", researcher, "dispatch"))
            self.assertTrue(reopened.allowed("dugan", observer, "read"))
            reopened.close()
            identities.close()
            registry.close()

if __name__ == "__main__":
    unittest.main()
