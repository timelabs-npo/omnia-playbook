# Cross-platform maintenance semantics

Status: proposed semantic contract for deep red-teaming. This document does not grant execution authority.

## Purpose

Normalize desktop-maintenance discoveries from platform-specific sources such as Kudu into one semantic proposal type before any Omnia runtime or adapter may act on them.

The same user-facing intent must retain the same semantic meaning across `darwin`, `win32`, and `linux`; only the adapter and platform evidence may differ.

## Core invariant

A maintenance source may discover or recommend an operation, but it cannot authorize that operation. Every normalized proposal must carry `effect.authority = proposal_only`.

A destructive effect requires a later independent policy decision plus an execution receipt from the system that actually performed the effect. Neither a rule match, HTTP success, UI state, model consensus, nor elevated privilege is evidence that the destructive effect is authorized or complete.

## Normal form

All imported maintenance dialects are translated into `schemas/maintenance-proposal.schema.json`.

The normal form separates:

- source provenance from target identity;
- semantic intent from platform implementation;
- observation from destructive effect;
- risk from authority;
- proposal from policy decision;
- policy decision from execution receipt.

## Platform rule

`darwin`, `win32`, and `linux` adapters may use different OS primitives, path syntaxes, APIs, privilege systems, and recovery mechanisms. They must not change the meaning of the normalized intent or manufacture missing evidence.

Examples:

- `observe_browser_cache` means observation on every platform; it cannot silently become deletion on one platform.
- `propose_reclaim` is still proposal-only even if the source rule marks a target safe or requires administrator privileges.
- unresolved target identity, stale observation, failed scope validation, or unknown recovery evidence must remain explicit and non-authorizing.

## Red-team obligations

At minimum, validators must attack:

1. authority escalation (`proposal_only` -> execute);
2. path/scope substitution and symlink/reparse-point races;
3. platform drift where equivalent rules produce different semantic effects;
4. stale rule provenance or changed upstream revisions;
5. missing age/recency checks;
6. privilege confusion (`needsAdmin` interpreted as permission);
7. user-data misclassification as cache;
8. absent recovery/recreate evidence;
9. UI or transport success substituted for execution receipt;
10. duplicate/replayed proposals with changed targets;
11. arbitrary shell/action fields escaping the normalized schema;
12. model-generated proposals attempting to bypass host policy.

## Relationship to Omnia

`omnia-playbook` owns requirements, normalization contracts and independent validation semantics. It does not become Omnia's runtime state-transition authority.

Omnia may consume a validated maintenance proposal, but mutation must remain behind Omnia's own typed policy/state/receipt boundary.
