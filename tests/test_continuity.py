import tempfile
import unittest
from pathlib import Path
from dottie.continuity import DottieContinuity


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_identity_and_experience_survive_restart(self):
        runtime = DottieContinuity(self.root)
        runtime.establish("dottie", "baseline-v1")
        event = runtime.observe("dottie", "mission", "direct", "observed", "src")
        runtime.close()
        restarted = DottieContinuity(self.root)
        self.addCleanup(restarted.close)
        self.assertEqual(restarted.identity("dottie")["baseline_ref"], "baseline-v1")
        self.assertEqual(restarted.experiences.autobiography("dottie"), [])
        self.assertTrue(event)

    def test_no_unverified_memory_promotion(self):
        runtime = DottieContinuity(self.root)
        self.addCleanup(runtime.close)
        runtime.establish("dottie", "baseline-v1")
        event = runtime.observe("dottie", "mission", "direct", "observed", "src")
        with self.assertRaises(PermissionError):
            runtime.consolidate("dottie", event, "forged")

    def test_identity_and_memory_are_separate_for_agents(self):
        runtime = DottieContinuity(self.root)
        self.addCleanup(runtime.close)
        runtime.establish("dottie", "baseline-v1")
        runtime.establish("aegis-1", "aegis-baseline")
        event = runtime.observe("aegis-1", "mission", "direct", "agent observation", "src")
        with self.assertRaises(PermissionError):
            runtime.consolidate("dottie", event, "receipt")
        self.assertEqual(runtime.identity("dottie")["baseline_ref"], "baseline-v1")


if __name__ == "__main__":
    unittest.main()
