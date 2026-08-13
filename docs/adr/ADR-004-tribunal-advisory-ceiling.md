# ADR-004: Tribunal Advisory Ceiling

## Status
ACCEPTED

## Date
2026-08-13

## Deciders
Timelabs Owner; TRAE materialization

## Context
LLM-backed components offer interpretive value but must not cross into authority grants or decision overrides. A hard ceiling prevents advisory output from becoming de facto authority.

## Decision
Tribunal role is strictly: ADVISORY, UNCERTAINTY, HYPOTHESIS, DISAGREEMENT ANALYSIS. Seven permitted operations: (1) flag evidence gaps, (2) note ambiguity in interpretation, (3) propose alternative evidence paths, (4) summarize disagreement vectors, (5) annotate receipts with contextual notes, (6) suggest ESCALATE conditions, (7) produce human-readable explanations. Seven forbidden operations: (1) change PASS/FAIL output, (2) grant authority to any cell, (3) override fail-closed rules, (4) mutate evidence, (5) suppress ERROR conditions, (6) bypass constraint checks, (7) act as an identity provider. FAIL may never become PASS via Tribunal output. LLM is advisory-ceiling only.

## Consequences
Positive: Advisory value retained without authority creep; Tribunal output is auditable as a separate dimension. Negative: Tribunal cannot resolve genuine stalemates without ESCALATE to human. Binds: schemas/tribunal.schema.json role enum, tests/tribunal_ceiling_test.ts.

## Evidence
- schemas/tribunal.schema.json: role enum and output constraints
- tests/tribunal_ceiling_test.ts: seven forbidden-operation tests
- README.md: Tribunal Advisory Ceiling section
