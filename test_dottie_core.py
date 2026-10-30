import unittest
from dottie_core import Capability, authorize, evidence_record, reconcile_claims

class CoreTests(unittest.TestCase):
    def test_read_only_cannot_write(self):
        self.assertFalse(authorize(Capability("aegis", frozenset({"read"})), "write"))

    def test_explicit_permission(self):
        self.assertTrue(authorize(Capability("aegis", frozenset({"read"})), "read"))

    def test_evidence_has_digest(self):
        record = evidence_record("doc-1", "claim", "verified")
        self.assertEqual(len(record["digest"]), 64)

    def test_invalid_status_rejected(self):
        with self.assertRaises(ValueError):
            evidence_record("doc-1", "claim", "certain")

    def test_conflicts_remain_unresolved(self):
        result = reconcile_claims([{"source_id":"a","value":1},{"source_id":"b","value":2}])
        self.assertEqual(result["state"], "unresolved")
        self.assertEqual(result["sources"], ["a","b"])

if __name__ == "__main__":
    unittest.main()
