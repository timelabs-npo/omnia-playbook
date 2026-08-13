# ADR-005: OpenBSD Platform Policy

## Status
ACCEPTED

## Date
2026-08-13

## Deciders
Timelabs Owner; TRAE materialization

## Context
OpenBSD-based execution (MBSD) has a spectrum of validation confidence from unknown through Beryl-hardware tested. Skipping tiers produces phantom validation claims.

## Decision
Platform validation uses seven ordered tiers: UNKNOWN → OPENBSD_BASE_AVAILABLE → OPENBSD_PORT_AVAILABLE → MOCK_TESTED → VM_TESTED → REAL_HOST_TESTED → BERYL_TESTED. Promotion forbidden rules: (1) no tier jump without passing the intermediate tier's test gate, (2) REAL_HOST_TESTED requires reproducible CI evidence, (3) BERYL_TESTED requires signed hardware observation logs, (4) VM_TESTED cannot substitute for REAL_HOST_TESTED on driver-sensitive paths. Wi-Fi, MediaTek, and Beryl-specific paths default to UNKNOWN without corresponding observation. Kernel-modification requires an explicit validated current requirement; none exists at this time. Linux sidecars are not permitted for MBSD execution paths.

## Consequences
Positive: Validation claims are structurally tiered and auditable. Negative: BERYL_TESTED claims require hardware access; UNKNOWN default is strict. Binds: schemas/platform.schema.json tier enum, tests/platform_promotion_test.ts, MBSD adapter gates.

## Evidence
- schemas/platform.schema.json: tier enum and promotion constraints
- tests/platform_promotion_test.ts: four promotion-forbidden rules
- schemas/fixtures/valid/adapter.openbsd-sealed-brick.valid.json: MBSD tier tagging
- README.md: OpenBSD Platform Policy section
