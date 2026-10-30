import unittest
from dottie.hyperweave_bridge import Connection, CrossDimensionalBridge


class CrossDimensionalBridgeTests(unittest.TestCase):
    def setUp(self):
        self.bridge = CrossDimensionalBridge(
            lambda principal, scope, action: principal == "dottie" and scope == "mission-a"
        )

    def test_cross_dimension_path_preserves_evidence(self):
        self.bridge.connect("dottie", "mission-a", Connection("claim", "event", "temporal", "src-1"))
        self.bridge.connect("dottie", "mission-a", Connection("event", "source", "evidentiary", "src-2"))
        paths = self.bridge.traverse("dottie", "mission-a", "claim")
        self.assertEqual(len(paths), 2)
        self.assertEqual([e.evidence_ref for e in paths[-1]], ["src-1", "src-2"])
        self.assertEqual(paths[-1][0].status, "association")

    def test_cross_agent_read_denied(self):
        with self.assertRaises(PermissionError):
            self.bridge.traverse("aegis-1", "mission-a", "claim")

    def test_cross_scope_read_denied(self):
        with self.assertRaises(PermissionError):
            self.bridge.traverse("dottie", "mission-b", "claim")

    def test_cross_scope_write_denied(self):
        with self.assertRaises(PermissionError):
            self.bridge.connect("aegis-1", "mission-a", Connection("a", "b", "semantic", "src"))

    def test_cycle_is_bounded(self):
        self.bridge.connect("dottie", "mission-a", Connection("a", "b", "semantic", "src"))
        self.bridge.connect("dottie", "mission-a", Connection("b", "a", "causal", "src"))
        self.assertEqual(len(self.bridge.traverse("dottie", "mission-a", "a", 10)), 1)


if __name__ == "__main__":
    unittest.main()
