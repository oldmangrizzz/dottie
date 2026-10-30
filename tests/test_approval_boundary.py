import tempfile
import unittest
from pathlib import Path
from dottie.experience_store import ExperienceStore


class ApprovalBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "exp.sqlite"

    def test_no_validator_denies_promotion(self):
        store = ExperienceStore(self.path)
        self.addCleanup(store.close)
        event = store.record("dottie", "mission", "direct", "observed", "src")
        with self.assertRaises(PermissionError):
            store.promote("dottie", event, "arbitrary-string")

    def test_invalid_receipt_denied(self):
        store = ExperienceStore(self.path, approval_validator=lambda owner, event, receipt: False)
        self.addCleanup(store.close)
        event = store.record("dottie", "mission", "direct", "observed", "src")
        with self.assertRaises(PermissionError):
            store.promote("dottie", event, "forged")

    def test_valid_receipt_permits_promotion(self):
        store = ExperienceStore(self.path, approval_validator=lambda owner, event, receipt:
                                (owner, receipt) == ("dottie", "approved-receipt"))
        self.addCleanup(store.close)
        event = store.record("dottie", "mission", "direct", "observed", "src")
        store.promote("dottie", event, "approved-receipt")
        self.assertEqual(len(store.autobiography("dottie")), 1)


if __name__ == "__main__":
    unittest.main()
