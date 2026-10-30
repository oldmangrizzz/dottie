import os
import tempfile
import unittest
from dottie.runtime import DottieRuntime

class DispatchAuthorizationTests(unittest.TestCase):
    def test_revoked_membership_blocks_queued_work(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = DottieRuntime(os.path.join(folder, "state.db"))
            owner = runtime.identity.create_user("owner", "correct horse battery staple", "owner")
            worker = runtime.identity.create_user("worker", "correct horse battery staple", "researcher", owner)
            runtime.register_agent("dugan", lambda payload: {"executed": True})
            runtime.memberships.bootstrap_owner("dugan", owner)
            runtime.memberships.grant("dugan", worker, "collaborator", owner)
            job = runtime.submit(worker, "dugan", {}, "revoked-worker")
            runtime.memberships.revoke("dugan", worker, owner)
            self.assertEqual(runtime.run_next()["state"], "failed")
            self.assertEqual(runtime.jobs.status(job)["state"], "failed")
            runtime.close()

if __name__ == "__main__":
    unittest.main()
