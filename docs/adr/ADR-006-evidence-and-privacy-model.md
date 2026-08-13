# ADR-006: Evidence and Privacy Model

## Status
ACCEPTED

## Date
2026-08-13

## Deciders
Timelabs Owner; TRAE materialization

## Context
Network observation spans from universally sharable public records to host-local raw captures that must never leave the host. A tiered model prevents accidental leakage.

## Decision
Evidence privacy has four non-promotable tiers: PUBLIC_EVIDENCE, PRIVATE_EVIDENCE, LOCAL_ONLY_RAW_OBSERVATION, DERIVED_BOOLEAN_POSTURE. Twelve leakage-audit channels are declared: (1) decision receipts, (2) Tribunal advisory output, (3) log files, (4) error messages, (5) telemetry payloads, (6) debug dumps, (7) cache artifacts, (8) rendered visualization, (9) ESCALATE tickets, (10) CI artifacts, (11) inter-cell messages, (12) crash reports. LOCAL_ONLY_RAW_OBSERVATION has must_not_leave_host:true enforced at schema and code-generation layers. Redaction is not considered comprehensive unless explicitly tested per channel.

## Consequences
Positive: Raw observations cannot accidentally escape host; tier downgrade (e.g., LOCAL→DERIVED) is the only allowed direction. Negative: Requires per-channel audit tests; raw-data debugging is intentionally constrained. Binds: schemas/evidence.schema.json privacy tier, tests/evidence_leakage_test.ts.

## Evidence
- schemas/evidence.schema.json: privacy tier enum and non-promotion constraints
- tests/evidence_leakage_test.ts: 12-channel audit tests
- README.md: Evidence and Privacy Model section
