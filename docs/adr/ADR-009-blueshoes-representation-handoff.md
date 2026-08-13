# ADR-009: Blueshoes Representation Handoff

## Status
ACCEPTED

## Date
2026-08-13

## Deciders
Timelabs Owner; TRAE materialization

## Context
Omnia v1 must establish a structurally complete baseline before Blueshoes takes over representation duties. The handoff point must be unambiguous.

## Decision
Omnia v1 is structurally complete when all of the following hold: semantics are coherent, authority is bounded, evidence contracts are explicit, deterministic boundary is enforced, provider model implemented, Tribunal advisory ceiling in place, repository validation reproducible, and GitHub repository state reflects reality. At handoff, Blueshoes owns the pipeline: raw observation → typed network/world facts → canonical provenance representation → deterministic frames. Twenty-four representation primitives are enumerated in the Blueshoes schema. Representation ≠ decision ≠ visualization/renderer — each remains independently replaceable. The first Blueshoes milestone is read-only: it consumes evidence and produces frames without mutating decision state.

## Consequences
Positive: Clean handoff boundary; representation layer cannot silently influence decisions. Negative: Two-layer (Omnia decision + Blueshoes representation) coordination cost; read-only milestone delays mutation capability. Binds: schemas/blueshoes.schema.json 24 primitives, tests/blueshoes_handoff_test.ts, milestone gating in CI.

## Evidence
- schemas/blueshoes.schema.json: 24 representation primitives, read-only milestone flag
- tests/blueshoes_handoff_test.ts: v1 structural-completeness gates
- README.md: Blueshoes Representation Handoff section
- .github/workflows/: v1 reproducible validation CI
