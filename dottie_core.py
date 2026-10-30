"""Bounded, deterministic authority and evidence primitives for Dottie."""
from dataclasses import dataclass
from hashlib import sha256

@dataclass(frozen=True)
class Capability:
    actor: str
    actions: frozenset[str]

def authorize(capability: Capability, action: str) -> bool:
    """Only explicitly granted actions are permitted."""
    return action in capability.actions

def evidence_record(source_id: str, content: str, status: str) -> dict:
    allowed = {"verified", "calculated", "user-reported", "disputed"}
    if status not in allowed:
        raise ValueError("unsupported evidence status")
    if not source_id.strip():
        raise ValueError("source identifier required")
    return {"source_id": source_id, "digest": sha256(content.encode("utf-8")).hexdigest(), "status": status}

def reconcile_claims(claims: list[dict]) -> dict:
    """Never silently resolve contradictory claims."""
    values = {str(item["value"]) for item in claims}
    return {"state": "unresolved" if len(values) > 1 else "consistent",
            "sources": [item["source_id"] for item in claims]}
