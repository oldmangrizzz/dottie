"""GEV event shape preview only; NEVER posts to live GEV or canonical state."""


def project_finding(finding):
    return {
        "event_type": "finding.proposed",
        "identity_id": finding.identity_id,
        "request_id": finding.request_id,
        "original_question": finding.original_question,
        "status": finding.claim_status,
        "source_refs": list(finding.evidence_refs),
        "canonical_state": False,
        "read_only": True,
        "live_gev_write": False,
    }
