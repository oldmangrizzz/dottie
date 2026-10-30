"""Regression tests for persistent queue, identity and evidence boundaries."""
import os
import tempfile
import unittest
from dottie.jobs import JobQueue
from dottie.identity import IdentityStore
from dottie.evidence import EvidenceLedger

class DurableSystemsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "state.sqlite")

    def tearDown(self):
        self.tmp.cleanup()

    def test_queue_idempotency_and_reopen(self):
        q = JobQueue(self.path)
        first = q.submit("agent-a", {"task": 1}, "request-1")
        self.assertEqual(first, q.submit("agent-a", {"task": 1}, "request-1"))
        q.close()
        q = JobQueue(self.path)
        job = q.claim()
        self.assertEqual(job["id"], first)
        q.finish(first, {"ok": True}, job["lease_token"])
        self.assertEqual(q.status(first)["result"], {"ok": True})
        self.assertIsNone(q.claim())
        q.close()

    def test_queue_expired_lease_recovery(self):
        q = JobQueue(self.path)
        job_id = q.submit("agent-a", {}, "request-2")
        self.assertEqual(q.claim(0.001)["id"], job_id)
        q.db.execute("UPDATE jobs SET lease_until=0 WHERE id=?", (job_id,))
        self.assertEqual(q.claim()["attempts"], 2)
        q.close()

    def test_identity_owner_and_restricted_reviewer(self):
        store = IdentityStore(self.path)
        owner = store.create_user("owner", "correct horse battery staple", "owner")
        self.assertEqual(store.authenticate("owner", "correct horse battery staple"), owner)
        self.assertIsNone(store.authenticate("owner", "incorrect password"))
        reviewer = store.create_user("reviewer", "long password for review", "reviewer", owner)
        self.assertTrue(store.allowed(reviewer, "evidence:read"))
        self.assertFalse(store.allowed(reviewer, "users:manage"))
        with self.assertRaises(PermissionError):
            store.create_user("another", "long password for review", "researcher", reviewer)
        store.close()

    def test_evidence_preserves_conflicts_and_detects_mutation(self):
        ledger = EvidenceLedger(self.path)
        ledger.append("claim", "source-1", "original", "verified", {"value": 1})
        ledger.append("claim", "source-2", "different", "disputed", {"value": 2})
        result = ledger.reconcile("claim")
        self.assertEqual(result["state"], "unresolved")
        self.assertTrue(ledger.verify_source(result["records"][0], "original"))
        self.assertFalse(ledger.verify_source(result["records"][0], "tampered"))
        ledger.close()

if __name__ == "__main__":
    unittest.main()
