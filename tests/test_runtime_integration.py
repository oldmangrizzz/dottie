"""Integration tests for authenticated agent dispatch and durable execution."""
import os
import tempfile
import unittest
from dottie.runtime import DottieRuntime

class RuntimeIntegrationTests(unittest.TestCase):
    def test_authorized_dispatch_persists_result_and_blocks_viewer(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "dottie.db")
            runtime = DottieRuntime(path)
            owner = runtime.identity.create_user("owner", "a sufficiently long password", "owner")
            viewer = runtime.identity.create_user("viewer", "another sufficiently long password", "viewer", owner)
            runtime.register_agent("morita", lambda data: {"answer": data["number"] * 2})
            runtime.memberships.bootstrap_owner("morita", owner)
            with self.assertRaises(PermissionError):
                runtime.submit(viewer, "morita", {"number": 4}, "viewer-1")
            job_id = runtime.submit(owner, "morita", {"number": 4}, "owner-1")
            self.assertEqual(job_id, runtime.submit(owner, "morita", {"number": 4}, "owner-1"))
            outcome = runtime.run_next()
            self.assertEqual(outcome["result"], {"answer": 8})
            runtime.close()
            reopened = DottieRuntime(path)
            self.assertEqual(reopened.jobs.status(job_id)["result"], {"answer": 8})
            reopened.close()

    def test_handler_failure_is_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = DottieRuntime(os.path.join(directory, "dottie.db"))
            owner = runtime.identity.create_user("owner", "a sufficiently long password", "owner")
            def fail(_):
                raise RuntimeError("agent unavailable")
            runtime.register_agent("jones", fail)
            runtime.memberships.bootstrap_owner("jones", owner)
            job_id = runtime.submit(owner, "jones", {}, "failure-1")
            self.assertEqual(runtime.run_next()["state"], "failed")
            self.assertEqual(runtime.jobs.status(job_id)["error"], "agent unavailable")
            runtime.close()

if __name__ == "__main__":
    unittest.main()
