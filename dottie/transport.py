"""Bounded natural-language transport envelopes.

Messages are untrusted text. They are never executable instructions or grants.
"""
from dataclasses import dataclass

MAX_MESSAGE_CHARS = 16000

@dataclass(frozen=True)
class NaturalLanguageEnvelope:
    sender: str
    recipient: str
    text: str
    purpose: str = "collaboration"

    def __post_init__(self):
        if not all(isinstance(v, str) and v.strip() for v in (self.sender, self.recipient, self.purpose)):
            raise ValueError("sender, recipient, and purpose required")
        if self.sender == self.recipient:
            raise ValueError("sender and recipient must differ")
        if not isinstance(self.text, str):
            raise TypeError("inter-agent content must be natural-language text")
        if not self.text.strip() or len(self.text) > MAX_MESSAGE_CHARS:
            raise ValueError("message is empty or exceeds maximum size")
        if any(ord(c) < 32 and c not in "\n\t" for c in self.text):
            raise ValueError("control characters forbidden")

    def as_record(self):
        return {"sender": self.sender, "recipient": self.recipient,
                "text": self.text, "purpose": self.purpose}
