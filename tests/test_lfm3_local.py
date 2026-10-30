import json
import unittest
from unittest.mock import patch
from dottie.lfm3_local import LFM3LocalAdapter


class Response:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, limit=-1): return self.payload


class LFM3LocalTests(unittest.TestCase):
    def test_no_model_guessing(self):
        with self.assertRaises(ValueError):
            LFM3LocalAdapter(model="")

    def test_no_remote_endpoint(self):
        with self.assertRaises(ValueError):
            LFM3LocalAdapter(model="lfm3", endpoint="https://example.com/api/chat")

    @patch("dottie.lfm3_local.urlopen")
    def test_local_request(self, open_url):
        open_url.return_value = Response({"message": {"content": "answer"}, "model": "lfm3", "done": True})
        adapter = LFM3LocalAdapter(model="lfm3")
        result = adapter.respond(type("R", (), {"input_text": "Hello"})())
        self.assertEqual(result, "answer")
        self.assertEqual(json.loads(open_url.call_args.args[0].data)["model"], "lfm3")
        self.assertEqual(adapter.last_receipt["provider"], "ollama_local")

    @patch("dottie.lfm3_local.urlopen")
    def test_model_mismatch_fails_closed(self, open_url):
        open_url.return_value = Response({"message": {"content": "answer"}, "model": "other", "done": True})
        with self.assertRaises(ValueError):
            LFM3LocalAdapter(model="lfm3").respond(type("R", (), {"input_text": "Hello"})())


if __name__ == "__main__":
    unittest.main()
