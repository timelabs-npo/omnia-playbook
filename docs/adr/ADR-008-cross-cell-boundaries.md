# ADR-008: Cross-Cell Boundaries

## Status
ACCEPTED

## Date
2026-08-13

## Deciders
Timelabs Owner; TRAE materialization

## Context
As the system grows, megacomponents that collapse distinct concerns are the primary threat to determinism, auditability, and independent replaceability.

## Decision
Megacomponent prohibition: Omnia ≠ Blueshoes ≠ MBSD ≠ HME ≠ Rheknel. Integration across cells happens exclusively via typed contracts and evidence payloads — no internal API calls across cell boundaries. No code copy across cells; shared logic must live in explicitly versioned common libraries with independent tests. No silent reuse of semantics across boundaries; each cell re-declares the semantics it consumes. Eight independently replaceable dimensions: naming, identity, location, reachability, path discovery, path selection, authorization, execution.

## Consequences
Positive: Each cell is independently testable, deployable, and replaceable; boundary violations are structurally detectable. Negative: Contract churn requires coordinated schema versioning; shared logic extraction has overhead. Binds: directory structure under src/ per cell, schemas/cell_contract.schema.json, tests/cell_boundary_test.ts.

## Evidence
- schemas/cell_contract.schema.json: typed cross-cell contracts
- tests/cell_boundary_test.ts: megacomponent prohibition tests
- src/: cell-isolated directory layout
- README.md: Cross-Cell Boundaries section
