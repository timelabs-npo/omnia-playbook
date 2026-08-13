# BLUESHOES REPRESENTATION V0 — Omnia Handoff (2026-08-13)

## Status: FROZEN OMNIA INPUTS; REPRESENTATION PHASE BEGIN

## Central Question
> How do heterogeneous observations of actual network reality become a canonical, replayable, typed representation without prematurely deciding truth, policy, or action?

## Inherited Input Contracts from Omnia v1 (MUST preserve exactly)
1. 6-sentence architecture: Omnia constrains / Decision evaluates / Tribunal advises / Blueshoes represents / MBSD executes / Providers testify.
2. Naming ≠ Identity ≠ Location ≠ Locator Discovery ≠ Reachability ≠ Path Discovery ≠ Path Selection ≠ Multipath ≠ Authorization ≠ Execution Authority — each independently replaceable dimension (ADR-008).
3. Evidence semantic separations: Observation ≠ Claim ≠ Evidence ≠ Truth; Trust ≠ Authorization ≠ Mutation Authority; Consensus ≠ Truth; Memory ≠ Truth; Specified ≠ Implemented ≠ Deployed ≠ Locally Observed.
4. Omnia providers are replaceable contracts (15 families enumerated in provider_capability.schema.json): DNS, GNS, SCION, BGP_OPENBGPD, RPKI, LOCAL_OBSERVATION, ACTIVE_PROBE, LIBP2P_LIKE_DISCOVERY, QUIC_PATH_OBSERVATION, MBSD_OPENBSD_OBSERVATION, WIREGUARD_OBSERVATION, MDNS_DNS_SD, ICE_STUN_TURN, MASQUE_TUNNEL, FUTURE_PROVIDER. Blueshoes MAY NOT hard-code any of these as the only source.
5. Representation must explicitly support contradictory observations preserved simultaneously (collapse to single truth is Omnia policy/decision phase, NOT Blueshoes representation).
6. Omnia evidence 4-tier privacy model (PUBLIC / PRIVATE / LOCAL_ONLY_RAW / DERIVED_BOOLEAN) MUST be preserved in Blueshoes provenance tags; LOCAL_ONLY_RAW must_not_leave_host applies identically to Blueshoes.
7. OpenBSD 7-tier support honesty (UNKNOWN→BERYL_TESTED; promotion_forbidden 4 rules; Wi-Fi/MediaTek/Beryl defaults to UNKNOWN without signed observation logs) applies to Blueshoes physical-collection adapters.
8. Megacomponent boundary: Blueshoes != Omnia != MBSD != HME != Rheknel. Interaction via typed contracts only. No code copy across cells (enforced by Omnia tests/test_architecture_boundaries.py TestMegacomponentBoundary).
9. Degraded/offline semantics MUST be declared for every Blueshoes provider-dependency root; offline result MUST NOT silently become PASS/TRUE (inherited from ADR-007 + provider_capability.schema.json).
10. Canonical representation MUST be deterministically serializable and hashable for HME replay.

## Purpose
Own the deterministic transformation: raw heterogeneous observations → normalization → typed network/world facts → provenance-bearing canonical representation → deterministic frames / replay.

## Non-Goals (hard; fail build if violated)
1. Blueshoes V0 does NOT perform network mutation (no PF rule writes, no BGP reconfig, no route injection).
2. Blueshoes V0 does NOT collapse contradictory observations into a single resolved value (that decision belongs to Omnia policy/decision kernel).
3. Blueshoes V0 does NOT become a visualization or UI renderer (visualization is a PROJECTION).
4. Blueshoes V0 does NOT implement a new wire protocol (no network-visible changes beyond Omnia-approved read-only collection contracts).
5. Blueshoes V0 does NOT grant authority or approve actions or mutate FAIL→PASS on its own (Tribunal advisory ceiling applies to Blueshoes identically).
6. Blueshoes V0 does NOT re-implement DNS/SCION/GNS/BGP protocols in-process; it consumes provider outputs per Omnia provider_capability contracts.
7. Blueshoes V0 is NOT another Omnia v2 — stop condition for Omnia expansion already reached; Blueshoes extends on a separate representation axis.

## Representation Primitives Vocabulary (24)
```
Node                  — observed compute/network endpoint identifier
Interface             — physical or logical interface identifier on a Node
Identity              — cryptographic or namespace-bound identity (≠ Naming ≠ Location)
Name                  — human-readable or DNS/GNS/SCION name record
Service               — named service identity/endpoint tuple
Locator               — routable or reachable locator (IP / SCION-ISD-AS / GNS key / mDNS target)
Route                 — routing table / RIB entry / next-hop chain
Path                  — end-to-end observed or available path or SCION path vector
Flow                  — 5-tuple flow / connection record / observed packet stream
Connection            — established connection / QUIC stream / TCP conn state
ProviderObservation   — single-sourced observation plus provider_id + timestamp + evidence_tier
ReachabilityObservation — boolean or ranked reachability result plus probe context
TrustClaim            — signed or attributed trust assertion (≠ truth, recorded only)
PolicyReference       — pointer to Omnia policy/invariant (not replicated locally)
NetworkCondition      — normalized link/router/service condition (up/down/degraded/flapping)
Failure               — detected failure + scope + provenance + timestamp
Dependency            — dependency graph edge (root → required + degraded/offline contract)
Time                  — monotonic-clock or wall-clock timestamp + source (provider/host)
Provenance            — origin record: provider, observation_id, collector, tier, privacy_tier tag
Confidence            — numerical or enum confidence + derivation (LOW/MEDIUM/HIGH with explicit meaning or 0/1)
Contradiction         — two+ mutually-exclusive observations preserved together with refs
```
Notes: (a) Primitives may share a single typed representation module/file if logical grouping is consistent. (b) No primitive may hard-code a specific provider's protocol as the sole source for its slot.

## HME Interface Target (read-only)
Canonical frame pipeline MUST be able to feed:
1. Omnia evidence evaluation (PROVIDER_OBSERVATION typed-evidence inputs)
2. Deterministic replay (two successive serialization passes → byte-identical digests; see export_runtime_bundle.py pattern)
3. HME / WorldEngine multi-interpreter conformance tests (A-G scenarios per test_multi_interpreter_conformance.py pattern)
4. CLI/text inspection (stable field names, canonical field ordering)
5. Visualization (external, as PROJECTION)
6. Future topology UI (external, as PROJECTION)
7. Future World 2.0 manifestation (external, as PROJECTION)
Network is NOT the visualization. Visualization is a PROJECTION of represented network state.

## Blueshoes Representation Contract Requirements (13)
1. Canonical serialization format (JSON/CBOR both acceptable; MUST define field ordering rules)
2. Stable field semantics (no silent breaking changes within a major version)
3. Explicit semantic versioning of representation frame schema
4. Provenance for every represented value (per-primitive provenance links)
5. Monotonic timestamps plus explicit clock source identifier
6. Unknown state as a first-class enum (not NULL or omitted)
7. Contradictory observations preserved as first-class Contradiction primitives (not resolved inside Blueshoes)
8. No hidden truth promotion: tier_non_promotion rules enforced structurally
9. Deterministic hashing: SHA-256 of canonical serialization (identical inputs → identical digest)
10. Replayability: deterministic frame stream must be byte-identical on re-run
11. Bounded extensibility: explicit versioned extension slots; unrecognized extensions MUST fail closed for safety-critical fields
12. Provider neutrality: same primitive type populated from any of the 15 families
13. Explicit degraded/offline contract for every provider dependency root

## Representation Is Not Decision — Example preserved state
```
DNS provider:         service X → locator A
GNS provider:         service X → identity B
SCION provider:       path P available
active probe:         locator A UNREACHABLE
local cache:          locator A PREVIOUSLY reachable
```
Blueshoes V0 MUST preserve all five simultaneously. MUST NOT collapse them into `X = A`. Collapse = violation of non-goal #2.

## Deterministic Acceptance Tests (minimum 8)
1. Two successive canonicalization passes on identical raw input → byte-identical digest.
2. Contradictory DNS vs GNS vs SCION vs probe vs cache observations all preserved simultaneously; none suppressed.
3. LOCAL_ONLY_RAW privacy tier tag causes serialization to external consumer to emit zero raw-bytes (only tier + hash of raw + provenance).
4. Provider neutrality: same Service primitive, populated from each of 3 distinct provider families, validates against same representation schema without schema changes.
5. Unknown first-class state: no value represented as NULL — every slot has either VALID / UNKNOWN / MISSING_PROVIDER / CONTRADICTORY enum.
6. Degraded-offline declared for each dependency root; offline fallback produces OFFLINE enum result; never PASSES silently.
7. HME conformance: frame serialized → 2 independent interpreters (Python stdlib JSON + alternate JSON/CBOR impl) produce identical hash.
8. Megacomponent boundary: Blueshoes V0 tree contains zero files named omnia_*_kernel.*, mbsd_*driver.*, rheknel*, hme_world_engine.* across .py/.c/.h/.go/.rs/.js/.ts suffixes.

## First Read-Only PoC Vertical (no router mutation required)
```
preserved Blueshoes raw observation
  → normalization + provider_id + timestamp + privacy_tier tag
  → canonical NetworkCondition + ProviderObservation + Contradiction primitives
  → deterministic SHA-256 serialization / hash
  → HME-compatible replay / multi-interpreter conformance
```
Starter data suggestion: Use 4+ contradictory sources (DNS / GNS-name / SCION-path / probe) for one canonical service identifier name.

## Explicit Prohibitions on Uncontrolled Mutation (fail closed)
- No PF/BGP/WireGuard/interface write hooks in Blueshoes V0 tree
- No Omnia FAIL→PASS mutation inside Blueshoes code
- No code copied from Omnia schemas verbatim; reference by schema URL/id only
- No Linux runtime sidecar required for OpenBSD/MBSD execution
- No kernel modification references or plans within Blueshoes V0 scope (per Omnia: no current validated requirement justifies kernel modification)

## Links to Omnia v1 Source Artefacts
- ADR-009: docs/adr/ADR-009-blueshoes-representation-handoff.md
- Deterministic decision kernel: schemas/deterministic_decision_kernel.schema.json
- Provider capability contracts (15 families): schemas/provider_capability.schema.json
- Tribunal advisory ceiling (role/authority boundaries): schemas/tribunal_advisory_ceiling.schema.json
- Evidence privacy tier (4-tier + 12 leakage audits): schemas/evidence_privacy_tier.schema.json
- OpenBSD support honesty (7 tiers): schemas/openbsd_support_tier.schema.json
- Megacomponent boundary tests: tests/test_architecture_boundaries.py
- Semantic-neighbours gate + reuse decisions: reports/SEMANTIC_NEIGHBOURS_MATRIX.md + reports/REUSE_DECISION_REGISTER.md
- Reconciliation table: reports/RECONCILIATION_MAIN_TRAE_CODEX_COPILOT.md
