from dataclasses import dataclass, replace
from typing import Tuple


@dataclass(frozen=True)
class IdentityBinding:
    identity_id: str
    baseline_ref: str
    mode: str = "simulation"
    active_model: str = "unbound"

    def __post_init__(self):
        if not self.identity_id.strip() or not self.baseline_ref.strip():
            raise ValueError("Identity and baseline reference are required")
        if self.mode not in ("simulation", "live"):
            raise ValueError("Invalid identity binding mode")
        if self.mode == "live":
            raise ValueError("Live GrizOS identity binding is not implemented by this prototype")

    def with_model(self, model: str):
        return replace(self, active_model=model)


@dataclass(frozen=True)
class Request:
    request_id: str
    original_question: str
    input_text: str
    sensitivity: str = "private"
    requires_deep_reasoning: bool = False
    external_approval: bool = False
    export_approval: bool = False
    evidence_refs: Tuple[str, ...] = ()
    allow_external_action: bool = False

    def __post_init__(self):
        if (not isinstance(self.request_id, str) or not self.request_id.strip()
                or not isinstance(self.original_question, str) or not self.original_question.strip()):
            raise ValueError("Nonempty string request ID and exact original question required")
        for field in ("requires_deep_reasoning", "external_approval", "export_approval", "allow_external_action"):
            if type(getattr(self, field)) is not bool:
                raise TypeError(field + " must be a JSON boolean, never a string or number")
        if self.sensitivity not in ("public", "internal", "private", "restricted"):
            raise ValueError("Invalid sensitivity class")
        if not isinstance(self.input_text, str):
            raise ValueError("Input text must be a string")
        if self.allow_external_action:
            raise ValueError("Prototype is read-only; external actions are unavailable")
        if not isinstance(self.evidence_refs, (list, tuple)) or any(
            not isinstance(ref, str) or not ref.strip() for ref in self.evidence_refs
        ):
            raise TypeError("evidence_refs must be a list or tuple of nonempty strings")
        object.__setattr__(self, "evidence_refs", tuple(self.evidence_refs))


@dataclass(frozen=True)
class RoutingDecision:
    target: str
    reason: str
    effective_question: str
    laya_hint: dict | None = None


@dataclass(frozen=True)
class Finding:
    request_id: str
    original_question: str
    identity_id: str
    model_used: str
    response_text: str
    claim_status: str
    evidence_refs: Tuple[str, ...]
    error_type: str = ""
