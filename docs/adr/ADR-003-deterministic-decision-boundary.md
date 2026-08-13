# ADR-003: Deterministic Decision Boundary

## Status
ACCEPTED

## Date
2026-08-13

## Deciders
Timelabs Owner; TRAE materialization

## Context
Decision output must be machine-auditable and reproduceable across runs. Ambiguous outputs or override paths silently break posture guarantees.

## Decision
Decision cell outputs are strictly the five-value enum: PASS, FAIL, UNKNOWN, ERROR, ESCALATE. Fail-closed hard rules: (1) missing required evidence → FAIL, (2) conflicting evidence with no resolution path → FAIL, (3) expired or revoked identity material → FAIL, (4) constraint violation → FAIL, (5) provider offline without degraded declaration → FAIL, (6) cross-cell authority impersonation → FAIL, (7) schema validation error on receipt → FAIL. Four-dimensional receipt pinning: (a) schema version, (b) provider evidence hashes, (c) constraint rule set version, (d) decision function version. rheknel default state is CANDIDATE_UNVALIDATED, never hard-coded. NL/LLM components cannot grant authority or override FAIL.

## Consequences
Positive: Reproducible decisions, fail-closed by default, audit receipts are cryptographically verifiable. Negative: Requires exhaustive evidence declaration; some edge cases yield ESCALATE requiring human review. Binds: schemas/decision.schema.json outputs, tests/decision_fail_closed_test.ts, all receipt generators.

## Evidence
- schemas/decision.schema.json: output enum and receipt structure
- tests/decision_fail_closed_test.ts: seven hard-rule test cases
- schemas/fixtures/valid/decision.receipt.valid.json: 4-dim pinning
- README.md: Deterministic Boundary section
