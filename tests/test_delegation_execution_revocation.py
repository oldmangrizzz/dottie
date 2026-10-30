import os
import tempfile
import unittest
from dottie.runtime import DottieRuntime

class DelegationExecutionTests(unittest.TestCase):
    def test_consent_withdrawal_prevents_queued_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = DottieRuntime(os.path.join(folder, "state.db"))
            owner = runtime.identity.create_user("owner", "correct horse battery staple", "owner")
            principal = runtime.identity.create_user("principal", "correct horse battery staple", "viewer", owner)
            helper = runtime.identity.create_user("helper", "correct horse battery staple", "researcher", owner)
            runtime.register_agent("dugan", lambda value: {"executed": True})
            runtime.memberships.bootstrap_owner("dugan", owner)
            runtime.memberships.grant("dugan", helper, "collaborator", owner)
            consent = runtime.delegations.grant(principal, helper, "dugan", ["agents:dispatch"], principal, 3600)
            job_id = runtime.submit_delegated(principal, helper, "dugan", {}, "consent-withdrawn")
            runtime.delegations.revoke(consent, principal)
            self.assertEqual(runtime.run_next()["state"], "failed")
            self.assertEqual(runtime.jobs.status(job_id)["state"], "failed")
            runtime.close()

if __name__ == "__main__":
    unittest.main()
