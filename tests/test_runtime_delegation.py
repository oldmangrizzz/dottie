"""Delegated dispatch integration against persistent runtime components."""
import os
import tempfile
import unittest
from dottie.runtime import DottieRuntime

class DelegatedRuntimeTests(unittest.TestCase):
    def test_delegation_requires_consent_and_membership(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = DottieRuntime(os.path.join(folder, "state.db"))
            owner = runtime.identity.create_user("owner", "secure owner password 123", "owner")
            principal = runtime.identity.create_user("principal", "secure principal password 123", "viewer", owner)
            helper = runtime.identity.create_user("helper", "secure helper password 123", "researcher", owner)
            runtime.register_agent("dugan", lambda payload: {"received": payload})
            runtime.memberships.bootstrap_owner("dugan", owner)
            with self.assertRaises(PermissionError):
                runtime.submit_delegated(principal, helper, "dugan", {"request": "help"}, "k1")
            runtime.memberships.grant("dugan", helper, "collaborator", owner)
            with self.assertRaises(PermissionError):
                runtime.submit_delegated(principal, helper, "dugan", {"request": "help"}, "k1")
            delegation = runtime.delegations.grant(
                principal, helper, "dugan", ["agents:dispatch"], principal, 3600)
            job_id = runtime.submit_delegated(principal, helper, "dugan", {"request": "help"}, "k1")
            self.assertEqual(runtime.run_next()["result"], {"received": {"request": "help"}})
            self.assertEqual(runtime.jobs.status(job_id)["state"], "completed")
            runtime.delegations.revoke(delegation, principal)
            with self.assertRaises(PermissionError):
                runtime.submit_delegated(principal, helper, "dugan", {}, "k2")
            runtime.close()

if __name__ == "__main__":
    unittest.main()
