import tempfile
import unittest
from pathlib import Path
from dottie.identity_store import IdentityStore


class IdentityStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "identity.sqlite"
        self.store = IdentityStore(self.path)

    def test_identity_survives_restart(self):
        self.store.establish("dottie", "baseline-v1")
        self.store.close()
        store = IdentityStore(self.path)
        self.addCleanup(store.close)
        self.assertEqual(store.read("dottie")["baseline_ref"], "baseline-v1")

    def test_identity_cannot_be_silently_rewritten(self):
        self.store.establish("dottie", "baseline-v1")
        with self.assertRaises(ValueError):
            self.store.establish("dottie", "baseline-v2")
        self.assertEqual(self.store.read("dottie")["baseline_ref"], "baseline-v1")

    def test_model_switch_does_not_change_identity(self):
        self.store.establish("dottie", "baseline-v1")
        self.store.record_model("dottie", "lfm3")
        self.store.record_model("dottie", "deepseek")
        self.assertEqual(self.store.read("dottie")["baseline_ref"], "baseline-v1")
        self.assertEqual(self.store.read("dottie")["active_model"], "deepseek")

    def test_unknown_identity_fails_closed(self):
        with self.assertRaises(KeyError):
            self.store.read("unknown")


if __name__ == "__main__":
    unittest.main()
