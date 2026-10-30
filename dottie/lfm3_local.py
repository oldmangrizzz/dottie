"""Local-only Ollama adapter for an explicitly installed LFM-3 model.

Never silently fall back to remote inference.
"""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LFM3LocalAdapter:
    is_simulator = False

    def __init__(self, model, endpoint="http://127.0.0.1:11434/api/chat", timeout=45):
        if not isinstance(model, str) or not model.strip():
            raise ValueError("Explicit installed LFM-3 model tag required")
        if endpoint != "http://127.0.0.1:11434/api/chat":
            raise ValueError("Only loopback Ollama endpoint allowed")
        if type(timeout) not in (int, float) or not 0 < timeout <= 120:
            raise ValueError("Invalid timeout")
        self.model, self.endpoint, self.timeout = model, endpoint, timeout
        self.last_receipt = {}

    def respond(self, req):
        self.last_receipt = {}
        if not isinstance(req.input_text, str) or not req.input_text.strip():
            raise ValueError("Nonempty input required")
        data = json.dumps({"model": self.model, "stream": False,
                           "messages": [{"role": "user", "content": req.input_text}]}).encode("utf-8")
        request = Request(self.endpoint, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read(8_000_001)
        except HTTPError as exc:
            raise ConnectionError("Local Ollama HTTP error " + str(exc.code)) from None
        except (URLError, TimeoutError, OSError):
            raise ConnectionError("Local Ollama unavailable") from None
        if len(raw) > 8_000_000:
            raise ValueError("Oversized local model response")
        try:
            payload = json.loads(raw)
            content = payload["message"]["content"]
            if payload.get("model") != self.model or payload.get("done") is not True:
                raise ValueError("Local model mismatch or incomplete response")
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Empty local model response")
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("Malformed local model response") from exc
        self.last_receipt = {"provider": "ollama_local", "model": self.model, "endpoint": "loopback", "done": True}
        return content
