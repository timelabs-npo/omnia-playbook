# ADR-007: Degraded and Offline Semantics

## Status
ACCEPTED

## Date
2026-08-13

## Deciders
Timelabs Owner; TRAE materialization

## Context
Every dependency eventually degrades or goes offline. Silent success under failure produces false posture claims.

## Decision
Every dependency root — DNS, cloud, identity, rendezvous, control plane, and every provider family — MUST declare explicit degraded and offline behavior in its schema and adapter implementation. Offline result MUST NOT be PASS. Unknown semantics are restricted to ERROR, UNKNOWN, or FAIL only — no implicit PASS under unspecified conditions. Degraded semantics MUST NEVER silently resolve to PASS; a degraded dependency that cannot produce bounded evidence must yield UNKNOWN or ESCALATE.

## Consequences
Positive: False PASS is structurally prevented; failure modes are explicit and auditable. Negative: Requires behavioral declaration for every dependency; some valid edge cases may surface as UNKNOWN/ESCALATE. Binds: all adapter schemas, tests/degraded_semantics_test.ts, provider family contracts.

## Evidence
- schemas/provider.schema.json: degraded/offline declaration fields
- tests/degraded_semantics_test.ts: PASS-under-offline forbidden tests
- schemas/fixtures/valid/: degraded-offline fixture set
- README.md: Degraded and Offline Semantics section
