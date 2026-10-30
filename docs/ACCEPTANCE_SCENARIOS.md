# Dottie Hill — executable acceptance scenarios (public-safe)

These scenarios are implementation-neutral and contain no private GMRI source. Each scenario must be automated against the actual implementation before it can be marked TESTED.

## Authorization
- Given a worker with read-only capability, when it requests a write, then the write is denied, the target remains unchanged, and an audit event records the denial.
- Given retrieved content containing instructions to elevate privilege, when processed, then the worker retains its original authority.

## Evidence
- Given two contradictory source claims, when synthesized, then both source identifiers survive and the conclusion is unresolved.
- Given a source revision, when its digest changes, then the original digest and prior citation remain available.
- Given a stale source, when presented, then its age and freshness limitation are visible.

## Memory
- Given Dottie-private and AEGIS-agent scopes containing distinct canary values, when each agent queries the other scope, then the canary is absent and access is logged.
- Given mission closure, when another mission retrieves context, then closed-mission private context is not returned without explicit authorization.

## Execution
- Given a repeated dispatch identifier, when submitted twice, then at most one side effect occurs and both requests resolve to the same recorded job.
- Given a worker interrupted after dispatch, when restarted, then durable state identifies whether execution completed; unknown completion is not silently retried.
- Given a failed tool call, when reporting, then the action is classified failed rather than completed.
- Given model fallback, when the preferred model is unavailable, then fallback retains the same capability ceiling.

## Connectivity
- Given WAN interruption, when connectivity returns, then pending jobs reconcile without duplicate side effects.
- Given a GEV write, when checking integration, then the test reads the exact written record back from the live GEV service; a mock cannot satisfy this gate.

## QA and release
- Given each acceptance test, when run, then record implementation revision, environment, input fixture, expected outcome, actual outcome, timestamp, and result.
- A failed or unrun test cannot be labeled TESTED, INTEGRATED, or OPERATIONAL.
- No private dossier, prompts, credentials, or staged harness may be published while this repository remains public.

## Execution order
1. Locate the private staged v0.5 harness and identify its actual test runner.
2. Convert these scenarios into failing tests in the private implementation.
3. Implement minimal passing behavior, rerun focused tests, then the full suite.
4. Verify live GEV and restart/WAN behavior separately; record receipts.
