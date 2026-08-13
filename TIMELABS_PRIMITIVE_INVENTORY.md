# TIMELABS_PRIMITIVE_INVENTORY

## Scope and evidence boundary
- Primary local evidence: `omnia-playbook` current branch (`c9220ee`) plus open branch lines `origin/codex/council-readiness` and `origin/trae/a0l-audit`.
- Cross-repo evidence: `timelabs-npo/Blueshoes`, `serg-alexv/hme` (WorldEngine/World2), `timelabs-npo/.github`, `timelabs-npo/rhea-project` READMEs/docs sampled.
- This inventory records primitives independently of repository ownership.

## Primitive inventory (atomized)

| Primitive | Family | Minimal definition | Current Timelabs evidence | Evidence state |
|---|---|---|---|---|
| Invariant | Governance | Normative rule over expected state and severity | `schemas/invariant.schema.json`; `checks/dns/invariant-dns-explicit-resolvers.yaml` | IMPLEMENTED |
| Read-only diagnostic check | Governance/Execution | Platform-scoped observation contract with pass/fail semantics | `schemas/check.schema.json`; `scripts/diagnose.sh`; `checks/dns/*` | IMPLEMENTED |
| Adapter separation | Architecture | Vendor/platform mapping isolated from invariant definition | `README.md`; `foundation/*`; `adapters/*` | SPECIFIED |
| Deterministic report artifact | Evidence | Timestamped machine+human diagnostics from same observation | `scripts/report.sh` JSON+MD outputs | IMPLEMENTED |
| Authority ceiling | Governance/Safety | Explicit cap on runtime mutation authority | `local-agent/ssh-policy.md`; Trae branch OpenBSD invariant/check authority blocks | SPECIFIED |
| Unknown-is-not-pass semantics | Governance | Missing/contradictory evidence maps to UNKNOWN/ERROR instead of PASS | Trae branch `invariant-openbsd-sealed-brick.yaml` | SPECIFIED |
| Contract-first ingress | Governance | Versioned input contract gates execution before collection | Codex branch `fail-fast-policy.md` | SPECIFIED |
| Append-only local source record (`log.0`) | Evidence | Exact-byte framed event chain as authoritative local record | Codex branch `docs/architecture/log0-multi-nqlite.md`; `scripts/log0.py` | SPECIFIED (main branch); IMPLEMENTED (unmerged Codex branch) |
| Projection honesty | Evidence epistemics | Every derived view declares what is preserved vs dropped | Codex branch `projection-honesty.schema.json` | SPECIFIED |
| Replay over committed sequence | Determinism | Logical sequence order outranks wall-clock ordering | Codex branch `log0-multi-nqlite.md` | SPECIFIED |
| Disposable projections (catalog/assurance/workflow) | Data architecture | Rebuildable derived stores with watermarks, non-authoritative | Codex branch `schemas/sql/*.sql` + docs | SPECIFIED |
| Fail-fast policy machine | Control | PASS/FAIL/UNKNOWN/ERROR gate with bounded retry and stop | Codex branch `fail-fast-policy.md` | SPECIFIED |
| Tribunal verdict lattice | Governance | APPROVE/REVISE/FLAG/REJECT outcome set | Blueshoes `docs/TRIBUNAL_PROTOCOL.md` | SPECIFIED |
| Evidence tier hierarchy (E0..E6) | Evidence epistemics | Weighting of claims by reproducibility and adversarial tests | Blueshoes `docs/TRIBUNAL_PROTOCOL.md` | SPECIFIED |
| Consensus-is-not-truth rule | Epistemics | Agreement is weak evidence unless independently reproduced | Blueshoes `docs/TRIBUNAL_PROTOCOL.md`; `.github/profile/README.md` | SPECIFIED |
| Edge sovereignty invariant | Architecture/governance | Cloud may mirror/archive but cannot become runtime authority | Blueshoes `docs/CLOUD_CONSTITUTION.md` | SPECIFIED |
| Atomic network mutation transaction | Networking safety | Snapshot → apply → validate → rollback bounded by timeout | Blueshoes `docs/rfcs/0002-rollback-model.md` | SPECIFIED |
| LLM boundary (advisory only) | Agent governance | AI may suggest/analyze, but not mutate edge runtime directly | Blueshoes `docs/rfcs/0001-runtime-doctrine.md` | SPECIFIED |
| World-state frame with provenance class | World model | Explicit source-labelled world frames (SIM/LIVE/REPLAY/STALE) | HME `CLAIMS.md`, `architecture/SYSTEM.md` | IMPLEMENTED |
| Layered world transformation (L0..L9) | World model epistemics | Separate observation/features/state/pose/render/narrative layers | HME `ONTOLOGY_SURGERY.md` | SPECIFIED |
| Deterministic pose replay | Simulation determinism | Same input schedule yields byte-identical pose traces across runtimes | HME `frontier/world-engine-v0.1/README.md` | REPRODUCED (UNVERIFIED — reproduction protocol and independent verifier not documented; cross-repo claim) |
| State membrane + dwell hysteresis | Agent/world dynamics | Temporal boundary operator preventing flicker transitions | HME `WORLDMATH.md` | IMPLEMENTED |
| Evidence chain for world output | Evidence | Hash-linked frame/run-level evidence for replay assertions | HME `WORLDMATH.md`; `%LOCALAPPDATA%/World2/world-state.json` claim | SPECIFIED |
| Owner pre-failure operational intent | Governance | Declared service/capability intent before incidents | Trae `owner_operational_intent.schema.json` | SPECIFIED |
| Disagreement resolution contract | Multi-agent governance | Explicit evidence-first dispute resolution; majority not sufficient | Trae `disagreement_resolution.schema.json` | SPECIFIED |

## Cross-family motifs observed
1. **Authoritative local log + disposable projections** appears in Omnia codex line and Blueshoes cloud constitution.
2. **Bounded mutation with rollback and human override** appears in Blueshoes doctrine and Omnia/Trae authority-ceiling artifacts.
3. **Consensus demoted below reproducibility** appears in Tribunal protocol and organizational profile statements.
4. **World representation split from narrative claims** appears strongly in HME claims register + ontology surgery.

## Primitive saturation notes
- Saturation reached for currently visible Timelabs evidence/governance primitives in repositories sampled.
- Saturation not reached for MBSD-specific kernel/runtime internals (repository not visible in sampled org list).
