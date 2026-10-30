import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from dottie.ollama_cloud import OllamaCloudAdapter


class FakeResponse:
    def __init__(self, data):
        self.data = json.dumps(data).encode("utf-8")
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, limit=-1): return self.data


class OllamaCloudTests(unittest.TestCase):
    def test_missing_credentials_fail_closed(self):
        with self.assertRaises(ValueError):
            OllamaCloudAdapter(model="configured-tag", api_key="")

    def test_no_model_tag_guessing(self):
        with self.assertRaises(ValueError):
            OllamaCloudAdapter(model="", api_key="secret")

    @patch("dottie.ollama_cloud.urlopen")
    def test_request_and_receipt(self, open_url):
        open_url.return_value = FakeResponse({"message": {"content": "result"}, "model": "configured-tag", "done": True})
        client = OllamaCloudAdapter(model="configured-tag", api_key="secret")
        result = client.respond(type("Request", (), {"input_text": "Question"})())
        self.assertEqual(result, "result")
        sent = open_url.call_args.args[0]
        self.assertEqual(json.loads(sent.data)["model"], "configured-tag")
        self.assertEqual(sent.get_header("Authorization"), "Bearer secret")
        self.assertNotIn("secret", str(client.last_receipt))

    @patch("dottie.ollama_cloud.urlopen")
    def test_wrong_model_response_rejected(self, open_url):
        open_url.return_value = FakeResponse({"message": {"content": "result"}, "model": "unexpected", "done": True})
        with self.assertRaises(ValueError):
            OllamaCloudAdapter(model="configured-tag", api_key="secret").respond(type("Request", (), {"input_text": "Q"})())

    @patch("dottie.ollama_cloud.urlopen")
    def test_http_error_does_not_leak_credentials(self, open_url):
        open_url.side_effect = HTTPError("https://ollama.com/api/chat", 401, "denied", {}, None)
        client = OllamaCloudAdapter(model="configured-tag", api_key="secret")
        with self.assertRaises(ConnectionError) as caught:
            client.respond(type("Request", (), {"input_text": "Q"})())
        self.assertNotIn("secret", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
