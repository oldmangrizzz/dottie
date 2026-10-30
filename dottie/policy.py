from .contracts import Request, RoutingDecision


def decide_route(req: Request, laya_hint=None) -> RoutingDecision:
    """Deterministic authority gate, not a model's recommendation.

    LAYA may suggest relevance/urgency, but cannot create network permissions.
    Caller must separately authorize external inference and data export.
    """
    target = "local"
    if req.requires_deep_reasoning:
        if req.sensitivity != "public":
            reason = "private/internal/restricted information cannot go to remote inference"
        elif not req.external_approval:
            reason = "remote inference not expressly approved"
        elif not req.export_approval:
            reason = "external data export not separately approved"
        else:
            target = "deepseek"
            reason = "public data with two explicit permissions and deep reasoning requested"
    else:
        reason = "normal local cognition; remote not warranted"
    return RoutingDecision(target=target, reason=reason, effective_question=req.original_question, laya_hint=laya_hint)
