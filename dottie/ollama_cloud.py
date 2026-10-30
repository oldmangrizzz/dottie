"""Bounded Ollama Cloud chat adapter.

No model name inference, no token persistence, no unapproved fallback.
The routing policy must authorize outbound requests before calling this adapter.
"""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OllamaCloudAdapter:
    is_simulator = False

    def __init__(self, model, api_key, endpoint="https://ollama.com/api/chat", timeout=45):
        if not isinstance(model, str) or not model.strip():
            raise ValueError("Exact configured Ollama model tag required")
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("Ollama Cloud API key required")
        if endpoint != "https://ollama.com/api/chat":
            raise ValueError("Only the approved Ollama Cloud endpoint is supported")
        if type(timeout) not in (int, float) or not 0 < timeout <= 120:
            raise ValueError("Invalid timeout")
        self.model = model
        self._api_key = api_key
        self.endpoint = endpoint
        self.timeout = timeout
        self.last_receipt = {}

    def respond(self, req):
        self.last_receipt = {}
        if not isinstance(req.input_text, str) or not req.input_text.strip():
            raise ValueError("Nonempty input text required")
        body = json.dumps({"model": self.model, "stream": False,
                           "messages": [{"role": "user", "content": req.input_text}]}).encode("utf-8")
        request = Request(self.endpoint, data=body, headers={
            "Authorization": "Bearer " + self._api_key,
            "Content-Type": "application/json",
        }, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read(8_000_001)
        except HTTPError as exc:
            raise ConnectionError("Ollama Cloud HTTP error " + str(exc.code)) from None
        except (URLError, TimeoutError, OSError):
            raise ConnectionError("Ollama Cloud connection failed") from None
        if len(raw) > 8_000_000:
            raise ValueError("Oversized Ollama response")
        try:
            payload = json.loads(raw)
            content = payload["message"]["content"]
            actual_model = payload.get("model")
            if actual_model != self.model:
                raise ValueError("Ollama response model differs from requested model")
            if payload.get("done") is not True:
                raise ValueError("Ollama response incomplete")
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Ollama returned empty content")
        except (TypeError, KeyError, json.JSONDecodeError) as exc:
            raise ValueError("Malformed Ollama Cloud response") from exc
        self.last_receipt = {"provider": "ollama_cloud", "model": self.model,
                             "endpoint": "ollama.com/api/chat", "done": True}
        return content
