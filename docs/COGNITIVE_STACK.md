# Dottie cognitive stack — user-confirmed target

**Target:** LAYA + LFM-3 + DeepSeek V4.1 Flash via Ollama Cloud.

## Boundaries

- **LAYA:** cognition/attention/priority signals; does not grant permissions.
- **LFM-3:** default low-latency local reasoning/conversation path. Exact installed model tag and endpoint are deployment configuration, not inferred.
- **DeepSeek V4.1 Flash:** deeper reasoning path through the user's existing Ollama Cloud setup. Exact Ollama model identifier must be confirmed from the configured service; the name is not assumed to be an API tag.
- **GrizOS authority:** checks data sensitivity, outbound consent, tool permissions and routing independently of model suggestions.
- **Evidence:** all model output remains unverified until evidence-backed adjudication; GEV write integration is separate.

## Request path

1. Preserve original request, actor, sensitivity, provenance, and mission scope.
2. LAYA supplies optional attention/urgency guidance.
3. Deterministic policy selects LFM-3 local path or approved DeepSeek cloud path.
4. Adapter executes with a recorded model ID, endpoint category, timestamps, and error status.
5. Evidence ledger records request, route, output hash and receipts; no model may self-verify claims.
6. Dottie synthesizes without promoting retrieved mission context into autobiography.

## Integration requirements

- Ollama Cloud is already set up by the user. Do **not** repeat account onboarding.
- Read the actual configured model names from the environment/service before enabling live calls.
- Keep credentials outside GitHub, logs, and model prompts.
- Run offline, outage, stale-context, cross-agent isolation, duplicate dispatch, and outbound-data tests.
- No live inference or GEV operational claim until those tests pass.

**Status:** architecture contract; existing branch is a research harness, not yet an operational deployed stack.
