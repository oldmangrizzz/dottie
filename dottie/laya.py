"""LAYA advisory boundary: signals are not permissions.

This adapter normalizes advisory results. It cannot dispatch tools, mutate
identity, authorize cloud inference or promote evidence.
"""


class LAYAAdvisory:
    def __init__(self, advisor):
        if not callable(advisor):
            raise TypeError("LAYA advisor must be callable")
        self._advisor = advisor

    def inspect(self, request):
        signal = self._advisor(request)
        if not isinstance(signal, dict):
            raise ValueError("LAYA advisory must return a mapping")
        allowed = {}
        for field in ("attention", "urgency", "context_tags"):
            if field in signal:
                allowed[field] = signal[field]
        if "context_tags" in allowed:
            tags = allowed["context_tags"]
            if not isinstance(tags, (list, tuple)) or any(not isinstance(t, str) for t in tags):
                raise ValueError("Invalid context tags")
            allowed["context_tags"] = tuple(tags)
        for field in ("attention", "urgency"):
            if field in allowed and (type(allowed[field]) not in (int, float) or not 0 <= allowed[field] <= 1):
                raise ValueError("Invalid bounded LAYA signal")
        return allowed
