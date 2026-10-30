"""Delegated assistant access must be explicit, limited, and revocable."""
import os
import tempfile
import unittest
from dottie.delegation import Delegations
from dottie.identity import IdentityStore
from dottie.aegis import AgentRegistry

class DelegationTests(unittest.TestCase):
    def test_consent_scope_expiry_and_revocation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "dottie.sqlite")
            identities = IdentityStore(path)
            registry = AgentRegistry(path)
            owner = identities.create_user("owner", "long secure owner password", "owner")
            father = identities.create_user("father", "long secure father password", "viewer", owner)
            assistant = identities.create_user("assistant", "long secure assistant password", "researcher", owner)
            delegations = Delegations(path)
            with self.assertRaises(PermissionError):
                delegations.grant(father, assistant, "dugan", ["calendar:read"], authorized_by=owner, ttl_seconds=3600)
            delegation_id = delegations.grant(father, assistant, "dugan", ["calendar:read"], authorized_by=father, ttl_seconds=3600)
            self.assertTrue(delegations.allowed(father, assistant, "dugan", "calendar:read"))
            self.assertFalse(delegations.allowed(father, assistant, "dugan", "calendar:write"))
            self.assertFalse(delegations.allowed(father, assistant, "morita", "calendar:read"))
            delegations.revoke(delegation_id, authorized_by=father)
            self.assertFalse(delegations.allowed(father, assistant, "dugan", "calendar:read"))
            delegations.close()
            registry.close()
            identities.close()

if __name__ == "__main__":
    unittest.main()
