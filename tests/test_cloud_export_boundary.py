import unittest
from unittest.mock import patch
from dottie.ollama_cloud import OllamaCloudAdapter


class CloudExportBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.adapter = OllamaCloudAdapter(model="configured-tag", api_key="secret")

    @patch("dottie.ollama_cloud.urlopen")
    def test_private_request_never_reaches_network(self, network):
        req = type("R", (), {"input_text": "private", "sensitivity": "private",
                              "external_approval": True, "export_approval": True})()
        with self.assertRaises(PermissionError):
            self.adapter.respond(req)
        network.assert_not_called()

    @patch("dottie.ollama_cloud.urlopen")
    def test_missing_permissions_never_reach_network(self, network):
        req = type("R", (), {"input_text": "public", "sensitivity": "public",
                              "external_approval": False, "export_approval": False})()
        with self.assertRaises(PermissionError):
            self.adapter.respond(req)
        network.assert_not_called()


if __name__ == "__main__":
    unittest.main()
