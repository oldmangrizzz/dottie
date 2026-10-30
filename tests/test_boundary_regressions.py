"""Regression tests for Dottie evidence and authority primitives."""
import unittest
from dottie_core import Capability, authorize, evidence_record, reconcile_claims

class BoundaryRegressions(unittest.TestCase):
    def test_empty_capability_denies(self):
        self.assertFalse(authorize(Capability("aegis", frozenset()), "read"))

    def test_ungranted_publish_denies(self):
        self.assertFalse(authorize(Capability("aegis", frozenset({"read"})), "publish"))

    def test_blank_source_rejected(self):
        with self.assertRaises(ValueError):
            evidence_record("  ", "content", "verified")

    def test_digest_changes_with_content(self):
        a = evidence_record("source", "original", "verified")
        b = evidence_record("source", "mutated", "verified")
        self.assertNotEqual(a["digest"], b["digest"])

    def test_equal_claims_consistent(self):
        claims = [{"source_id": "a", "value": 1}, {"source_id": "b", "value": 1}]
        self.assertEqual(reconcile_claims(claims)["state"], "consistent")

    def test_conflict_preserves_all_sources(self):
        claims = [{"source_id": "a", "value": "yes"}, {"source_id": "b", "value": "no"}]
        self.assertEqual(reconcile_claims(claims)["sources"], ["a", "b"])
        self.assertEqual(reconcile_claims(claims)["state"], "unresolved")

if __name__ == "__main__":
    unittest.main()
