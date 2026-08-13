# ADR-001: Concern Separation

## Status
ACCEPTED

## Date
2026-08-13

## Deciders
Timelabs Owner; TRAE materialization

## Context
Omnia evaluates network posture claims through multiple cooperating components. Without explicit bounded authority, cross-cell overreach silently invalidates determinism and auditability.

## Decision
The architecture enforces a six-sentence separation: Omnia constrains, Decision evaluates, Tribunal advises, Blueshoes represents, MBSD executes, Providers testify. Each cell holds distinct bounded authority with no silent cross-cell authority granted. Cell contracts are typed and evidence-only; no cell may impersonate or exercise another cell's authority.

## Consequences
Positive: Deterministic audit trails, independently replaceable cells, authority violations are structurally detectable. Negative: Integration overhead between cells, additional contract maintenance. Binds: all schemas under schemas/ must declare cell ownership; all tests under tests/ must not cross cell authority boundaries.

## Evidence
- schemas/decision.schema.json: cell ownership fields
- schemas/fixtures/valid/adapter.openbsd-sealed-brick.valid.json: provider cell boundary
- README.md: Architecture Overview section
- schemas/tribunal.schema.json: advisory-only role declarations
