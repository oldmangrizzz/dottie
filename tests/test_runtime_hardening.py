"""Runtime authorization and job failure behavior."""
import os
import tempfile
import unittest
from dottie.runtime import DottieRuntime

class RuntimeHardeningTests(unittest.TestCase):
    def test_unknown_agent_handler_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = DottieRuntime(os.path.join(folder, "state.db"))
            with self.assertRaises(LookupError):
                runtime.register_agent("unregistered", lambda value: value)
            runtime.close()

    def test_stale_lease_error_does_not_overwrite_reclaimed_job(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = DottieRuntime(os.path.join(folder, "state.db"))
            owner = runtime.identity.create_user("owner", "a long owner password", "owner")
            runtime.memberships.bootstrap_owner("dugan", owner)
            def handler(payload):
                runtime.jobs.db.execute("UPDATE jobs SET lease_until=0 WHERE state='running'")
                return {"ok": True}
            runtime.register_agent("dugan", handler)
            job_id = runtime.submit(owner, "dugan", {"task": "work"}, "request-1")
            outcome = runtime.run_next()
            self.assertEqual(outcome["state"], "lease_lost")
            self.assertEqual(runtime.jobs.status(job_id)["state"], "running")
            runtime.close()

if __name__ == "__main__":
    unittest.main()
