import tempfile
import unittest
from pathlib import Path
from dottie.experience_store import ExperienceStore


class ExperienceStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "experience.sqlite"
        self.store = ExperienceStore(self.path)
        self.addCleanup(self.store.close)

    def test_observation_does_not_auto_promote(self):
        self.store.record("dottie", "mission-1", "retrieved", "report", "source-1")
        self.assertEqual(self.store.autobiography("dottie"), [])

    def test_authorized_promotion_requires_specific_receipt(self):
        event = self.store.record("dottie", "mission-1", "direct", "observed", "source-1")
        with self.assertRaises(PermissionError):
            self.store.promote("dottie", event, "")
        self.store.promote("dottie", event, "review-receipt-1")
        self.assertEqual(len(self.store.autobiography("dottie")), 1)

    def test_cross_agent_isolation(self):
        event = self.store.record("aegis-1", "mission-1", "direct", "agent observation", "source-2")
        with self.assertRaises(PermissionError):
            self.store.promote("dottie", event, "receipt")
        self.assertEqual(self.store.autobiography("dottie"), [])

    def test_promotion_persists_restart(self):
        event = self.store.record("dottie", "mission-1", "direct", "observed", "source-1")
        self.store.promote("dottie", event, "review-receipt-1")
        self.store.close()
        store = ExperienceStore(self.path)
        self.addCleanup(store.close)
        self.assertEqual(store.autobiography("dottie")[0]["review_receipt"], "review-receipt-1")

    def test_retrieved_information_cannot_be_promoted(self):
        event = self.store.record("dottie", "mission-1", "retrieved", "report", "source-1")
        with self.assertRaises(PermissionError):
            self.store.promote("dottie", event, "receipt")


if __name__ == "__main__":
    unittest.main()
