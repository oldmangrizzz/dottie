"""A reclaimed job must reject completion by its former worker."""
import os
import tempfile
import unittest
from dottie.jobs import JobQueue

class LeaseFencingTests(unittest.TestCase):
    def test_stale_worker_cannot_finish_or_fail_reclaimed_job(self):
        with tempfile.TemporaryDirectory() as folder:
            queue = JobQueue(os.path.join(folder, "jobs.db"))
            job_id = queue.submit("dugan", {"task": "research"}, "mission-1")
            first = queue.claim()
            queue.db.execute("UPDATE jobs SET lease_until=0 WHERE id=?", (job_id,))
            second = queue.claim()
            self.assertNotEqual(first["lease_token"], second["lease_token"])
            with self.assertRaises(PermissionError):
                queue.finish(job_id, {"stale": True}, first["lease_token"])
            with self.assertRaises(PermissionError):
                queue.fail(job_id, "stale failure", lease_token=first["lease_token"])
            queue.finish(job_id, {"current": True}, second["lease_token"])
            self.assertEqual(queue.status(job_id)["result"], {"current": True})
            queue.close()

if __name__ == "__main__":
    unittest.main()
