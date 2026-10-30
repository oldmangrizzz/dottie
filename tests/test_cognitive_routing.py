import unittest
from dottie.contracts import Request
from dottie.policy import decide_route


def request(**kwargs):
    defaults = dict(request_id="r1", original_question="question", input_text="question",
                    sensitivity="public", requires_deep_reasoning=True)
    defaults.update(kwargs)
    return Request(**defaults)


class CognitiveRoutingTests(unittest.TestCase):
    def test_default_is_lfm3_local(self):
        decision = decide_route(request(requires_deep_reasoning=False))
        self.assertEqual(decision.target, "local")

    def test_laya_cannot_grant_cloud_access(self):
        decision = decide_route(request(), laya_hint={"route": "deepseek", "authorized": True})
        self.assertEqual(decision.target, "local")

    def test_both_permissions_needed(self):
        self.assertEqual(decide_route(request(external_approval=True)).target, "local")
        self.assertEqual(decide_route(request(export_approval=True)).target, "local")

    def test_authorized_public_deep_request_routes_cloud(self):
        decision = decide_route(request(external_approval=True, export_approval=True))
        self.assertEqual(decision.target, "deepseek")

    def test_private_data_stays_local(self):
        decision = decide_route(request(sensitivity="private", external_approval=True, export_approval=True))
        self.assertEqual(decision.target, "local")


if __name__ == "__main__":
    unittest.main()
