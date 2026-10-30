"""Exercise the real command-line worker entry point."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from dottie.__main__ import load_handler, main
from dottie.runtime import DottieRuntime

class WorkerCLITests(unittest.TestCase):
    def test_load_handler_rejects_invalid_reference(self):
        with self.assertRaises(ValueError):
            load_handler("invalid")
        with self.assertRaises(ValueError):
            load_handler("os:not-valid")

    def test_cli_executes_queued_job(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "state.sqlite")
            runtime = DottieRuntime(path)
            owner = runtime.identity.create_user("owner", "a sufficiently long password", "owner")
            runtime.register_agent("calculator", lambda data: data)
            job_id = runtime.submit(owner, "calculator", {"value": 5}, "cli-1")
            runtime.close()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = main(["--database", path, "--agent", "calculator=json:loads", "--once"])
            self.assertEqual(status, 1)
            self.assertEqual(json.loads(output.getvalue())["state"], "failed")
            runtime = DottieRuntime(path)
            self.assertEqual(runtime.jobs.status(job_id)["state"], "failed")
            runtime.close()

if __name__ == "__main__":
    unittest.main()
