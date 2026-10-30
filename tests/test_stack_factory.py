import unittest
from unittest.mock import patch
from dottie.stack_factory import build_cognitive_stack


class CognitiveStackFactoryTests(unittest.TestCase):
    def test_missing_model_tag_rejected(self):
        with self.assertRaises(ValueError):
            build_cognitive_stack({"LFM3_MODEL": "", "OLLAMA_CLOUD_MODEL": "deepseek", "OLLAMA_API_KEY": "secret"})

    def test_missing_cloud_key_rejected(self):
        with self.assertRaises(ValueError):
            build_cognitive_stack({"LFM3_MODEL": "lfm3", "OLLAMA_CLOUD_MODEL": "deepseek", "OLLAMA_API_KEY": ""})

    def test_builds_both_providers(self):
        stack = build_cognitive_stack({"LFM3_MODEL": "lfm3", "OLLAMA_CLOUD_MODEL": "deepseek", "OLLAMA_API_KEY": "secret"})
        self.assertEqual(stack.local.model, "lfm3")
        self.assertEqual(stack.remote.model, "deepseek")
        self.assertNotIn("secret", repr(stack))

    def test_laya_is_optional_and_cannot_authorize(self):
        stack = build_cognitive_stack({"LFM3_MODEL": "lfm3", "OLLAMA_CLOUD_MODEL": "deepseek", "OLLAMA_API_KEY": "secret"},
                                      laya_advisor=lambda req: {"attention": 0.7, "authorized": True})
        self.assertEqual(stack.laya.inspect(object()), {"attention": 0.7})


if __name__ == "__main__":
    unittest.main()
