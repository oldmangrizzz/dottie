# HYPERWEAVE: Dottie cognitive substrate

Status: architecture contract, not deployed integration.

## Cross-multidimensional

The system must represent **within-dimension** relationships (semantic, temporal, causal, evidentiary, contextual, and agent-specific) and **cross-dimension** traversals between them. A traversal may discover a hypothesis, but must never automatically promote an association to an established fact.

## Non-negotiable boundaries

1. Every asserted fact carries a stable source reference, validity interval, observation time, and scope.
2. Evidence and inference are distinct object types. Inference stores its premises, method, and uncertainty.
3. Contradictory assertions remain separately addressable. A repair operation cannot erase evidence.
4. Scope authorization must be enforced by the trusted service, not a caller-supplied filter.
5. Dottie autobiographical, GMRI institutional, AEGIS shared, per-agent, mission, evidence, and GEV state remain independently governed.
6. Agent retrieval does not silently become autobiographical memory.
7. Historical reconstruction distinguishes *valid time* from *recorded time*.
8. All automated changes require a reviewable audit trail, idempotency, and rollback.
9. An association across dimensions is a candidate connection, not proof of causation.
10. Personal medical information and confidential research data must not enter this public repository.

## Proposed interfaces

- `ingest_evidence(principal, assertion, source, valid_interval)` -> immutable evidence receipt
- `connect(principal, typed_roles, dimensions, provenance)` -> typed hyperedge
- `traverse(principal, seeds, dimensions, as_of_valid, as_of_recorded)` -> evidence/inference-separated paths
- `propose_hypothesis(principal, premises, method)` -> explicitly unverified hypothesis
- `review_contradictions(principal, time_window)` -> competing claims with source lineage
- `checkpoint(principal)` -> verifiable integrity snapshot

These are **design contracts**, not existing callable APIs.

## Integration plan

1. Validate the staged v0.5 Dottie/AEGIS harness and identify its actual memory/orchestration extension points before changing its runtime.
2. Implement authorization and bitemporal evidence storage in a separately tested module.
3. Add cross-dimensional traversal with path provenance and cycle/limit guards.
4. Connect via a narrow Dottie adapter; preserve agent identities and memory scopes.
5. Validate GEV synchronization, WAN loss, restarts, contradictory sources, stale retrieval, cross-agent leakage, duplicate dispatch, and interrupted jobs.
6. Promote only after independent QA and a rollback demonstration.

## Current repository reality

At the time of this commit, the public repository README states the staged v0.5 harness and AEGIS integration are not present here. This document therefore does not claim live Dottie/GEV integration, operational agent cognition, or production readiness.
