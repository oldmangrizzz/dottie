from .contracts import Finding
from .policy import decide_route


class DottieResearchRuntime:
    """Small injectable research harness, not a persistent intelligence.

    Model outputs NEVER acquire institutional or evidentiary status just because
    a model returned them. GEV is not contacted. No background activity.
    """

    def __init__(self, local, remote, ledger, identity):
        self.local = local
        self.remote = remote
        self.ledger = ledger
        self.identity = identity

    def assess(self, req, laya_hint=None):
        if self.ledger.contains_request(req.request_id):
            raise ValueError("Duplicate request_id is blocked to prevent duplicate inference")
        decision = decide_route(req, laya_hint=laya_hint)
        self.ledger.append("request_received", {
            "request_id": req.request_id,
            "original_question": req.original_question,
            "sensitivity": req.sensitivity,
            "evidence_refs": list(req.evidence_refs),
            "route": decision.target,
            "route_reason": decision.reason,
            "identity_id": self.identity.identity_id,
            "baseline_ref": self.identity.baseline_ref,
        })
        try:
            provider = self.remote if decision.target == "deepseek" else self.local
            response = provider.respond(req)
            if not isinstance(response, str) or not response.strip():
                raise ValueError("Empty model response")
            status = "SIMULATED_OUTPUT" if getattr(provider, "is_simulator", False) else "MODEL_OUTPUT_UNVERIFIED"
            error_type = ""
        except (ConnectionError, TimeoutError, OSError, ValueError, RuntimeError) as ex:
            response = ""
            status = "BLOCKED_PROVIDER"
            error_type = type(ex).__name__
        provider_receipt = getattr(self.remote if decision.target == "deepseek" else self.local, "last_receipt", {}) if status == "MODEL_OUTPUT_UNVERIFIED" else {}
        finding = Finding(
            request_id=req.request_id,
            original_question=req.original_question,
            identity_id=self.identity.identity_id,
            model_used=decision.target,
            response_text=response,
            claim_status=status,
            evidence_refs=req.evidence_refs,
            error_type=error_type,
        )
        self.ledger.append("finding_recorded", {
            "request_id": finding.request_id,
            "original_question": finding.original_question,
            "model_used": finding.model_used,
            "claim_status": finding.claim_status,
            "evidence_refs": list(finding.evidence_refs),
            "error_type": finding.error_type,
            "model_receipt": provider_receipt,
            "response_sha256": __import__("hashlib").sha256(finding.response_text.encode("utf-8")).hexdigest(),
        })
        return finding
