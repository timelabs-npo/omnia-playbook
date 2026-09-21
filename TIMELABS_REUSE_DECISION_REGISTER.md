# TIMELABS_REUSE_DECISION_REGISTER

## Decision classes
- REUSE_DIRECTLY
- WRAP_AS_PROVIDER
- EXTRACT_PRIMITIVE
- REIMPLEMENT_FROM_SPEC
- BENCHMARK
- HISTORICAL_PRIOR_ART
- REJECT
- UNKNOWN

## Register

| System / Mechanism | Decision | Why (falsifiable) |
|---|---|---|
| OpenBSD PF states/tables/anchors/route-to/reply-to/divert | REUSE_DIRECTLY | Already native to target substrate; MBSD can implement OBSERVE/CLASSIFY/STEER/FAILOVER without importing foreign kernel dataplanes. |
| WireGuard | REUSE_DIRECTLY | Mature audited tunnel primitive; supports explicit, reversible overlay paths; no need to reinvent base encrypted tunnel. |
| OPA (Rego) | WRAP_AS_PROVIDER | Matches policy decision surface for constraints/authority envelopes; keep Omnia-specific receipt/provenance layers external. |
| Cedar | WRAP_AS_PROVIDER | Typed authorization language useful for explicit owner intent and bounded action authorizations. |
| Sigstore Rekor transparency log primitive | WRAP_AS_PROVIDER | Append-only transparency log with inclusion proofs maps to receipt/provenance chain. |
| in-toto layout model | BENCHMARK | in-toto layouts target build-step attestation; applicability to general Timelabs evidence receipts requires comparative evaluation before adoption. |
| TUF delegation and rollback protections | EXTRACT_PRIMITIVE | Role delegation, threshold signatures, freeze/rollback notions are directly reusable without adopting full software-update surface. |
| Event Sourcing + deterministic projectors | EXTRACT_PRIMITIVE | Direct semantic ancestor for `log.0` + disposable projections; can be narrowed to Timelabs contracts. |
| SCION path semantics | BENCHMARK | Valuable comparator for path-aware trust roots; direct integration requires major control-plane assumptions outside current scope. |
| HIP/LISP/ILNP | BENCHMARK | Clarify identity/location decomposition options; deployment constraints and ecosystem maturity vary. |
| NDN/CCNx | BENCHMARK | Tests host-centric assumption and naming alternatives; high conceptual value, low immediate drop-in compatibility. |
| Linux eBPF/XDP/nftables | BENCHMARK | Required contrast for mechanism palette; not import target for OpenBSD-first MBSD runtime. |
| VPP/DPDK/P4 | BENCHMARK | Useful for capability boundaries/performance baselines; not required for first bounded mutation doctrine. |
| Majority-vote-only tribunal | REJECT | Violates Timelabs “consensus is evidence, not truth” and Blueshoes anti-consensus invariant unless grounded in reproducible evidence tiers. |
| Fully cloud-authoritative runtime state | REJECT | Contradicts edge sovereignty invariant (falsifiable via cloud outage safety test). |
| 算力网络 compute-aware routing primitive | EXTRACT_PRIMITIVE | Genuine Chinese-origin emphasis: compute-routing as first-class path-selection factor, with distinct research depth beyond Western edge-computing framing. |
| 标识网络 naming/identity/locator split vocabulary | HISTORICAL_PRIOR_ART | Naming/identity/locator separation already exists in HIP, LISP, ILNP, DNS-SD. Chinese emphasis provides useful vocabulary but not a novel decomposition. Reclassified from EXTRACT_PRIMITIVE. |

## Unknown bucket (needs deeper dismantling)
- GNUnet/GNS deep comparison against Timelabs trust-root + naming goals.
- MBSD-specific code-level capabilities (repository not in sampled visible set).
- Formal belief-revision algorithm choice for Tribunal disagreement closure.
