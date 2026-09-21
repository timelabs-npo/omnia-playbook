# CONTRADICTION AND DOWNGRADE REGISTER

> Falsification pass on semantic-neighbour excavation artifacts (PR #6).
> Generated: 2026-08-13. This register is adversarial self-audit, not acceptance.
> **Stop condition:** PR remains draft with unresolved uncertainties preserved.

## Methodology

For each classification (REUSE_DIRECTLY, WRAP_AS_PROVIDER, EXTRACT_PRIMITIVE, PRIOR_ART_ONLY, POSSIBLY_NOVEL, UNKNOWN/UNRESOLVED):

1. Identify the **exact primitive** being classified, separate from whole system/project.
2. Provide **strongest primary source** for the claim.
3. State **evidence level**: SPECIFIED / IMPLEMENTED / REPRODUCED / DEPLOYED / OBSERVED_LOCALLY / INFERRED / UNKNOWN.
4. **Search for contradictory evidence** and record findings.
5. **Downgrade** any claim stronger than its evidence.
6. Distinguish: *not found in this sweep* vs *probably novel*; *no current requirement* vs *kernel work eliminated*; *provider reuse* vs *ontology adoption*.
7. For Chinese ontology entries: distinguish translation-only from genuine ontology delta.

---

## Evidence level definitions

| Level | Meaning |
|---|---|
| DEPLOYED | Running in production, externally verifiable |
| REPRODUCED | Independently reproduced by Timelabs or third party |
| IMPLEMENTED | Code/artifact exists in Timelabs repositories |
| SPECIFIED | Schema, doc, or RFC exists; no running implementation confirmed |
| OBSERVED_LOCALLY | Seen in local repo scan but not independently verified |
| INFERRED | Concluded from secondary sources or structural reasoning |
| UNKNOWN | No evidence located in this sweep |

---

## 1. REUSE_DECISION_REGISTER audit

### 1.1 OpenBSD PF — REUSE_DIRECTLY

- **Exact primitive:** PF packet filter state tables, anchors, route-to, reply-to, divert-to mechanisms.
- **Strongest source:** OpenBSD pf.conf(5) man pages; OpenBSD source tree `sys/net/pf*.c`.
- **Evidence level for Timelabs use:** INFERRED — MBSD repository was not visible in the sampled set. The claim that PF "already" supplies the surgery alphabet is conditional on MBSD actually targeting OpenBSD, which is SPECIFIED in Blueshoes docs but UNKNOWN at implementation level.
- **Contradictory evidence sought:** PF is mature and deployed (OpenBSD itself). However, the claim "no importing foreign kernel dataplanes" presumes MBSD scope decisions that are not evidenced in visible repos.
- **Verdict:** DOWNGRADE evidence level from implicit DEPLOYED to INFERRED for Timelabs context. PF itself is DEPLOYED globally, but Timelabs' use of it is INFERRED from Blueshoes architectural docs. Classification REUSE_DIRECTLY remains defensible *if* MBSD targets OpenBSD, which is SPECIFIED but not IMPLEMENTED in visible evidence.
- **Distinction:** This is *provider reuse* (PF as mechanism), not *ontology adoption* (PF does not define Timelabs governance semantics).

### 1.2 WireGuard — REUSE_DIRECTLY

- **Exact primitive:** Encrypted tunnel with key-based peer identity.
- **Strongest source:** WireGuard whitepaper (Donenfeld, 2017); Linux/OpenBSD kernel implementations.
- **Evidence level for Timelabs use:** INFERRED — No Timelabs code imports or configures WireGuard. Blueshoes docs reference overlay tunnels generically.
- **Contradictory evidence sought:** WireGuard itself is DEPLOYED globally. But "REUSE_DIRECTLY" implies drop-in use; WireGuard alone does not provide policy-aware path selection, identity federation, or authority ceilings that Timelabs requires around it.
- **Verdict:** Classification is *slightly overstated*. REUSE_DIRECTLY is accurate for the raw tunnel primitive. The surrounding governance (authority ceiling, policy control, rollback) requires WRAP_AS_PROVIDER semantics. **No downgrade of classification**, but add qualifier: reuse is for tunnel primitive only; integration envelope is additional work.

### 1.3 OPA (Rego) — WRAP_AS_PROVIDER

- **Exact primitive:** Rego policy language + OPA decision engine (PDP).
- **Strongest source:** OPA documentation (openpolicyagent.io); CNCF graduated project.
- **Evidence level for Timelabs use:** INFERRED — No OPA integration exists in any visible Timelabs repo.
- **Contradictory evidence sought:** OPA is DEPLOYED in industry. However, OPA's data model (JSON documents + Rego) may not natively express Timelabs evidence-tier and receipt semantics. The "wrap" framing assumes OPA can be used behind Timelabs-specific receipt/provenance layers, which is plausible but UNVERIFIED.
- **Verdict:** Classification defensible. Evidence level for Timelabs integration: INFERRED. No downgrade required but note: wrapping OPA still requires specifying the Timelabs-OPA contract boundary, which is currently UNSPECIFIED.

### 1.4 Cedar — WRAP_AS_PROVIDER

- **Exact primitive:** Cedar typed authorization policy language.
- **Strongest source:** Cedar language specification (cedar-policy.com); AWS open-source release.
- **Evidence level for Timelabs use:** INFERRED — No Cedar integration in visible repos.
- **Contradictory evidence sought:** Cedar and OPA serve similar PDP roles. The register lists both without stating selection criteria or mutual exclusion. This is not contradictory but is an UNRESOLVED decision point.
- **Verdict:** Classification defensible. Add note: OPA vs Cedar selection is UNRESOLVED; both listed as candidates without evidence of comparative evaluation.

### 1.5 in-toto + Sigstore Rekor — WRAP_AS_PROVIDER

- **Exact primitive:** Software supply-chain attestation layouts (in-toto) + transparency log (Rekor).
- **Strongest source:** in-toto specification (in-toto.io); Sigstore documentation (sigstore.dev).
- **Evidence level for Timelabs use:** INFERRED — No Timelabs code references in-toto or Rekor.
- **Contradictory evidence sought:** in-toto targets software supply chain, not general-purpose evidence receipts. Mapping it to Timelabs "receipt/provenance chain" may be a category stretch — in-toto layouts are about build steps, not runtime governance evidence.
- **Verdict:** **DOWNGRADE specificity.** The *transparency log* primitive (append-only, signed entries, inclusion proofs) maps well. The *in-toto layout* model is narrower than Timelabs evidence receipts. Classification should note: transparency-log primitive is WRAP_AS_PROVIDER; in-toto layout model requires BENCHMARK before deciding applicability to non-build evidence chains.

### 1.6 TUF delegation — EXTRACT_PRIMITIVE

- **Exact primitive:** Role-based key delegation, threshold signatures, freeze/rollback attack protections.
- **Strongest source:** TUF specification (theupdateframework.io).
- **Evidence level for Timelabs use:** INFERRED — No TUF integration in visible Timelabs repos.
- **Contradictory evidence sought:** TUF's delegation model is DEPLOYED in real systems (PyPI, Docker Content Trust). The extraction claim is defensible. However, TUF's root-of-trust model assumes a centralized repository publisher, which may conflict with Timelabs' edge-sovereignty constraint if applied naively.
- **Verdict:** Classification defensible with caveat: edge-sovereignty compatibility requires verification. Evidence level: INFERRED.

### 1.7 Event Sourcing — EXTRACT_PRIMITIVE

- **Exact primitive:** Append-only event stream as authoritative record; derived views rebuilt from replay.
- **Strongest source:** Martin Fowler's Event Sourcing pattern; Greg Young's CQRS/ES corpus; industry usage.
- **Evidence level for Timelabs use:** IMPLEMENTED — Codex branch has `log0` code and docs.
- **Contradictory evidence sought:** Event sourcing is well-established. The `log.0` implementation adds specific boundary choices (exact-byte framing, SQLite projectors, projection-honesty contracts). These *implementation details* are genuinely Timelabs-specific, but the *pattern* is established.
- **Verdict:** Classification accurate. Evidence level IMPLEMENTED is correct for Codex branch artifacts.

### 1.8 SCION — BENCHMARK

- **Exact primitive:** Path-aware forwarding with ISD trust-root partitioning.
- **Strongest source:** Perrig et al., SCION: A Secure Internet Architecture (Springer, 2017); scion.org.
- **Evidence level for Timelabs use:** INFERRED — No SCION integration or evaluation in visible repos.
- **Contradictory evidence sought:** SCION is DEPLOYED (SCIONLab, SWITCH network). Classifying as BENCHMARK rather than WRAP_AS_PROVIDER is reasonable given deployment complexity, but the register doesn't document *why* SCION can't be wrapped.
- **Verdict:** Classification defensible. Add note: the BENCHMARK classification reflects deployment complexity, not architectural incompatibility. This is a "no current requirement justifies work" finding, NOT "kernel work eliminated."

### 1.9 HIP/LISP/ILNP — BENCHMARK

- **Exact primitive:** Identity-locator split mechanisms (various protocol-level approaches).
- **Strongest source:** RFC 7401 (HIPv2), RFC 9300/9301 (LISP), RFC 6740 (ILNP).
- **Evidence level for Timelabs use:** INFERRED.
- **Contradictory evidence sought:** These are IETF standards-track/experimental, with varying deployment. HIP has limited deployment; LISP has Cisco deployment; ILNP is research-stage. Grouping them as equivalent "BENCHMARK" items hides significant maturity differences.
- **Verdict:** Classification defensible at coarse level. **Note:** maturity variance is flattened. LISP (DEPLOYED by Cisco) vs ILNP (RESEARCH) are not equivalent evidence levels.

### 1.10 NDN/CCNx — BENCHMARK

- **Exact primitive:** Named-data networking; name-based routing and in-network caching.
- **Strongest source:** NDN project (named-data.net); CCNx specifications.
- **Evidence level for Timelabs use:** INFERRED.
- **Contradictory evidence sought:** NDN remains primarily research-deployed (NSF testbed). "Low immediate drop-in compatibility" is accurate. However, NDN's naming model is conceptually relevant to Timelabs' identity/naming discussions and the Chinese 标识网络 decomposition.
- **Verdict:** Classification defensible. Cross-reference to Chinese ontology delta is noted but not explored.

### 1.11 Linux eBPF/XDP/nftables — BENCHMARK

- **Exact primitive:** Programmable packet processing in Linux kernel.
- **Strongest source:** Linux kernel documentation; Cilium project.
- **Evidence level for Timelabs use:** INFERRED — Noted as contrast, not import target.
- **Contradictory evidence sought:** If MBSD ever targets Linux alongside OpenBSD, this classification would need revision. Currently accurate given OpenBSD-first stance.
- **Verdict:** Classification defensible, contingent on MBSD platform decision (SPECIFIED for OpenBSD, not IMPLEMENTED).

### 1.12 Chinese 标识网络/算力网络 decompositions — EXTRACT_PRIMITIVE

- **Exact primitive:** Three-way separation of naming/identity/locator (标识网络); compute-as-routing-factor (算力网络).
- **Strongest source claimed:** CAICT whitepapers, Chinese networking research papers (no specific citations given).
- **Evidence level:** INFERRED from English-language secondary descriptions. **No primary Chinese-language sources cited.**
- **Contradictory evidence sought:**
  - The three-way naming/identity/locator split is ALSO present in non-Chinese literature (HIP, LISP, ILNP all address identity-locator separation; DNS-SD addresses naming). The characterization as a distinctly *Chinese* ontology delta is **overstated** — the decomposition exists in Western networking literature too.
  - 算力网络 (compute-aware networking) has genuine Chinese-specific research emphasis (China Mobile, China Telecom whitepapers), but the concept overlaps with edge computing and CDN-like compute placement in Western literature.
- **Verdict:** **DOWNGRADE.** The naming/identity/locator split is NOT a Chinese ontology delta — it is a universal networking concern with Chinese *emphasis* but not Chinese *origin*. 算力网络 has stronger claim to being a genuine vocabulary delta. Separate these two claims.
- **Translation vs ontology delta:** The lexicon entries for 标识/定位/命名 are primarily TRANSLATION of existing English networking concepts into Chinese. The 算力网络 entry represents a genuine ONTOLOGY DELTA where Chinese research has a distinct emphasis.

### 1.13 Majority-vote-only tribunal — REJECT

- **Exact primitive:** Pure majority-vote governance mechanism.
- **Evidence level:** SPECIFIED — Blueshoes Tribunal protocol explicitly rejects this.
- **Verdict:** Classification accurate and well-evidenced from Timelabs' own docs.

### 1.14 Fully cloud-authoritative runtime state — REJECT

- **Exact primitive:** Cloud as sole authority over runtime state.
- **Evidence level:** SPECIFIED — Blueshoes Cloud Constitution explicitly prevents this.
- **Verdict:** Classification accurate and well-evidenced.

---

## 2. POSSIBLE_NOVELTY_REGISTER audit

### 2.1 Projection honesty contract — POSSIBLY_NOVEL_COMBINATION

- **Exact primitive:** Explicit declaration of what a derived view preserves, drops, or aggregates from source, coupled with deterministic replay invariant.
- **Strongest source:** Codex branch `projection-honesty.schema.json` (SPECIFIED).
- **Evidence level:** SPECIFIED — Schema exists; no implementation or adoption confirmed.
- **Contradictory evidence sought:**
  - Data lineage systems (Apache Atlas, OpenLineage, dbt) track transformations and their effects. OpenLineage facets explicitly declare input/output schemas and transformations.
  - ML model cards (Mitchell et al., 2019) declare what training data was used/excluded.
  - Database view definitions inherently specify projection semantics.
  - **However:** these systems describe *what happened*; Timelabs' projection-honesty frames it as a *contract* (what MUST be preserved/dropped). The contract framing is less common.
- **Verdict:** Classification is **slightly overstated.** The concept of declaring transformation semantics is KNOWN (data lineage, model cards). The specific *contract* shape (deterministic replay + explicit preserve/drop declarations as a *requirement* rather than *observation*) is a KNOWN_COMBINATION with a distinctive emphasis, not POSSIBLY_NOVEL_COMBINATION. **DOWNGRADE** from POSSIBLY_NOVEL_COMBINATION to KNOWN_COMBINATION with qualifier: the enforcement-contract framing is distinctive but not clearly novel.
- **Distinction:** "Not found as an enforced contract in this sweep" ≠ "probably novel." Absence of a specific search hit does not establish novelty.

### 2.2 Consensus-is-evidence-not-truth — KNOWN

- **Exact primitive:** Consensus treated as evidential weight, not terminal authority.
- **Strongest source:** Blueshoes TRIBUNAL_PROTOCOL.md; epistemology literature (Popper, Lakatos).
- **Evidence level:** SPECIFIED in Timelabs docs; DEPLOYED in epistemology/science methodology.
- **Verdict:** Classification accurate. No contradictory evidence.

### 2.3 Cloud-memory-without-sovereignty — KNOWN_COMBINATION

- **Exact primitive:** Cloud as cache/mirror with no runtime authority.
- **Strongest source:** Blueshoes CLOUD_CONSTITUTION.md.
- **Evidence level:** SPECIFIED.
- **Contradictory evidence sought:** Edge computing architectures (MEC, fog computing, ETSI MEC) have similar sovereignty patterns. Military/avionics disconnected operations doctrine is deeply established.
- **Verdict:** Classification accurate. Well-precedented.

### 2.4 OpenBSD sealed-brick bounded collection — KNOWN_PRIMITIVE_NEW_APPLICATION

- **Exact primitive:** OpenBSD governance contract with UNKNOWN escalation.
- **Strongest source:** Trae branch `invariant-openbsd-sealed-brick.yaml`.
- **Evidence level:** SPECIFIED.
- **Contradictory evidence sought:** "Sealed" computing concepts exist (TPM sealed storage, OpenBSD pledge/unveil). The *governance contract wrapper* is Timelabs-specific application.
- **Verdict:** Classification defensible. Note: "new application" claim is contingent on the specific governance contract shape, which is SPECIFIED but not IMPLEMENTED or DEPLOYED.

### 2.5 World2 ontology surgery (L0..L9) — POSSIBLY_NOVEL_COMBINATION

- **Exact primitive:** Layered decomposition of world representation with explicit anti-category-error discipline.
- **Strongest source:** HME `ONTOLOGY_SURGERY.md`.
- **Evidence level:** SPECIFIED.
- **Contradictory evidence sought:**
  - Robotics has well-established perception pipelines (sense → fuse → estimate → plan → act).
  - Game engines have layered architectures (physics → animation → rendering).
  - OSI model provides layered decomposition for networking.
  - The specific L0..L9 numbering and "anti-category-error" framing appears Timelabs-specific, but the *concept* of layered world decomposition is deeply established.
- **Verdict:** **DOWNGRADE** from POSSIBLY_NOVEL_COMBINATION to KNOWN_COMBINATION. Layered world decomposition is established. The specific layer numbering and claims-register integration is a distinctive *arrangement*, not a novel *combination*. The anti-category-error discipline is a *governance overlay* on a known pattern.

### 2.6 Read-only → replay → bounded mutation doctrine — KNOWN_COMBINATION

- **Exact primitive:** Progressive trust escalation from observation to intervention.
- **Strongest source:** Safety engineering (shadow mode, canary, blue-green deployments).
- **Evidence level:** SPECIFIED as cross-cell doctrine.
- **Verdict:** Classification accurate. Deeply precedented in safety-critical systems engineering.

### 2.7 Chinese ontology deltas imported into Timelabs — KNOWN_PRIMITIVE_NEW_APPLICATION

- **Exact primitive:** Chinese technical vocabulary imported into Timelabs conceptual stack.
- **Evidence level:** INFERRED — Based on English-language secondary descriptions, not primary Chinese sources.
- **Contradictory evidence sought:** See §1.12. The naming/identity/locator split is not uniquely Chinese. 算力网络 has stronger claim.
- **Verdict:** **DOWNGRADE evidence level** from implied KNOWN to INFERRED. Chinese lexicon entries should be flagged as TRANSLATION_ONLY vs GENUINE_DELTA. See §1.12 for detailed analysis.

---

## 3. PRIMITIVE_INVENTORY evidence-level audit

### 3.1 Evidence level spot-checks

| Primitive | Claimed evidence state | Audit finding | Action |
|---|---|---|---|
| Invariant | IMPLEMENTED | Confirmed: `schemas/invariant.schema.json` exists on main branch | ✓ No change |
| Read-only diagnostic check | IMPLEMENTED | Confirmed: `schemas/check.schema.json`, `scripts/diagnose.sh` exist | ✓ No change |
| Adapter separation | SPECIFIED | Confirmed: `adapters/` directory exists with subdirs | ✓ No change |
| Authority ceiling | SPECIFIED | Source is Trae branch — not on current branch. Cannot verify independently | ⚠ Add note: cross-branch reference, not independently verified |
| Unknown-is-not-pass | SPECIFIED | Source is Trae branch — not on current branch | ⚠ Same caveat |
| Contract-first ingress | SPECIFIED | Source is Codex branch — not on current branch | ⚠ Same caveat |
| log.0 | IMPLEMENTED | Source is Codex branch — not on current branch | **DOWNGRADE** to SPECIFIED for main-branch evidence. IMPLEMENTED on Codex branch (not merged) |
| Projection honesty | SPECIFIED | Source is Codex branch | ⚠ Cross-branch reference |
| Tribunal verdict lattice | SPECIFIED | Source is Blueshoes repo — cross-repo reference | ⚠ Not independently verified in this sweep |
| Evidence tier hierarchy | SPECIFIED | Source is Blueshoes repo | ⚠ Same caveat |
| Deterministic pose replay | REPRODUCED | Source is HME repo | **REQUIRES VERIFICATION**: REPRODUCED is a strong claim. Was this independently reproduced? By whom? Under what conditions? |
| State membrane + dwell hysteresis | IMPLEMENTED | Source is HME repo | ⚠ Cross-repo, not verified |
| World-state frame with provenance | IMPLEMENTED | Source is HME repo | ⚠ Cross-repo, not verified |

### 3.2 Systemic issue: cross-branch and cross-repo evidence

The Primitive Inventory cites evidence from:
- **Codex branch** (`origin/codex/council-readiness`) — not merged to main
- **Trae branch** (`origin/trae/a0l-audit`) — not merged to main
- **Blueshoes repo** (`timelabs-npo/Blueshoes`) — separate repository
- **HME repo** (`serg-alexv/hme`) — separate repository, personal namespace

**Finding:** Evidence levels for cross-branch/cross-repo primitives should be explicitly qualified as "claimed at source; not independently verified in this sweep." The Inventory currently presents these as equivalent to locally-verified evidence.

**Recommendation:** Add a column or footnote marking evidence provenance scope (LOCAL_BRANCH / CROSS_BRANCH / CROSS_REPO) to distinguish verification confidence.

---

## 4. SEMANTIC_GRAPH audit

### 4.1 Edge direction and completeness

- Edge convention is documented: `from --relation--> to`.
- Graph has 22 nodes and 19 edges. For 7 Timelabs primitives and 15 external nodes, the graph is **sparse** — many plausible relationships are absent (e.g., no edge between Tribunal and TUF delegation, despite the cross-cell opportunity register noting this connection).
- **Finding:** Graph is a partial sketch, not a complete map. This is acceptable for a draft but should be noted.

### 4.2 Semantic accuracy of edges

- `P_blueshoes_bounded_mutation → S_openbsd_pf: implements` — This claims OpenBSD PF *implements* bounded mutation. PF provides *mechanisms for* bounded mutation but does not implement the Timelabs bounded-mutation contract. **DOWNGRADE** relation to `partially_overlaps` or `enables`.
- `P_tribunal_disagreement → S_argumentation: formalizes` — This claims Tribunal *formalizes* argumentation frameworks. Direction should arguably be reversed: argumentation frameworks *formalize the concepts that* Tribunal applies. The current direction implies Tribunal provides formalization *to* argumentation theory, which is backwards.

---

## 5. CHINESE_CONCEPT_LEXICON audit

### 5.1 Translation vs genuine ontology delta

| Term | Classification | Rationale |
|---|---|---|
| 意图 (Intent) | TRANSLATION_ONLY | Direct translation; intent-driven networking exists in English literature (IETF IBN) |
| 约束 (Constraint) | TRANSLATION_ONLY | Direct translation |
| 策略 (Policy) | TRANSLATION_ONLY | Direct translation |
| 权限上限 (Authority ceiling) | TRANSLATION_ONLY | Direct translation of Timelabs concept into Chinese |
| 标识 (Identifier) | PARTIAL_DELTA | The *separation* of 标识 from 定位 and 命名 is emphasized more in Chinese networking literature, but the concept exists in English (LISP, HIP) |
| 算力网络 (Compute network) | GENUINE_DELTA | Compute-aware routing as first-class network primitive has significantly more research depth in Chinese literature than English equivalents |
| 具身智能 (Embodied intelligence) | PARTIAL_DELTA | Broader usage in Chinese than English RL-focused "world model" framing; genuine vocabulary expansion |
| 世界模型 (World model) | PARTIAL_DELTA | Chinese usage couples with embodied intelligence more tightly |
| 语义通信 (Semantic communication) | GENUINE_DELTA | Active Chinese research area (6G) with distinctive theoretical framing |
| 确定性网络 (Deterministic networking) | TRANSLATION_ONLY | Direct mapping to DetNet/TSN standards |
| All remaining terms | TRANSLATION_ONLY | Standard technical translations |

### 5.2 Primary source verification

**Finding:** No Chinese-language primary sources are cited in the lexicon. All entries appear derived from English-language summaries of Chinese research. The "Example source tradition" column contains genre references (e.g., "意图驱动网络白皮书 traditions") but no specific paper, standard number, or URL.

**Recommendation:** For the GENUINE_DELTA entries (算力网络, 语义通信), specific primary sources should be added:
- 算力网络: CCSA TC3 standards work; China Mobile Research Institute whitepapers (e.g., "Computing-Aware Networking" whitepaper series)
- 语义通信: Tong Wen et al., "Semantic Communication" survey papers; IMT-2030 contributions

These are currently INFERRED from English secondary sources and should be marked as such until primary verification.

---

## 6. Cross-cutting findings

### 6.1 Distinctions required by problem statement

| Required distinction | Finding |
|---|---|
| "Not found in this sweep" vs "probably novel" | Projection honesty and World2 L0..L9 are classified as POSSIBLY_NOVEL but evidence is "not found in this sweep." Both downgraded to KNOWN_COMBINATION. Absence of counter-evidence in a limited sweep does not establish novelty. |
| "No current requirement justifies kernel work" vs "kernel work eliminated" | SCION, HIP/LISP/ILNP, NDN are classified BENCHMARK. This correctly reflects "no current requirement," not "eliminated." But the register text doesn't make this distinction explicit. |
| "Provider reuse" vs "ontology adoption" | OPA/Cedar are correctly framed as provider reuse. Chinese lexicon entries blur this: some are ontology adoption (算力网络 concepts) vs provider reuse (none — no Chinese *provider* is recommended for reuse). |
| Chinese translation vs ontology delta | See §5.1. Majority of lexicon entries are TRANSLATION_ONLY. Genuine deltas limited to 算力网络 and 语义通信 (and partially 具身智能/世界模型). |

### 6.2 Material impacts on Timelabs systems

| System | Material finding | Impact |
|---|---|---|
| Omnia | No contradictions found. Governance/evidence primitives are well-grounded in established patterns. | LOW — confirms rather than changes direction |
| Blueshoes | Edge sovereignty framing is KNOWN_COMBINATION (established in avionics/military). Not novel but well-applied. | LOW — validation, not change |
| MBSD | MBSD repository was NOT VISIBLE in this sweep. All MBSD-related classifications are INFERRED. | **HIGH** — entire MBSD evidence basis is unverifiable from available sources |
| HME/World2 | "Deterministic pose replay: REPRODUCED" is a strong claim lacking verification details. L0..L9 novelty downgraded. | MEDIUM — claims need evidence support |
| Rhea/Tribunal | Formal argumentation algorithm selection remains UNRESOLVED. Semantic graph edge direction for Tribunal↔argumentation is questionable. | MEDIUM — unresolved design decision |
| World 2.0 | Ontology surgery novelty downgraded. Chinese vocabulary expansion is partially translation-only. | LOW-MEDIUM — recalibrate expectations |

---

## 7. Validation status

| Check | Result | Notes |
|---|---|---|
| `make validate` | FAIL | Pre-existing: missing `checks/routing`, `checks/connectivity`, `checks/certificates`, `checks/secrets`, `checks/system` directories. NOT caused by PR #6. |
| `make test` | PASS (3 tests) | Schema validation tests pass. |
| `make diagnose` | PASS | DNS invariant check passes. |
| `make report` | PASS | Report generated successfully. |
| Internal markdown links | PASS | No broken links. |

**Note:** The `make validate` failure is pre-existing and outside the scope of PR #6. The PR's own validation checklist items ("Validate schemas and fixtures", "Run make validate") are partially unachievable due to this pre-existing gap.

---

## 8. Summary of downgrades

| Artifact | Item | Original claim | Downgraded to | Reason |
|---|---|---|---|---|
| Reuse Register | in-toto + Sigstore Rekor | WRAP_AS_PROVIDER (unified) | WRAP_AS_PROVIDER (transparency log) + BENCHMARK (in-toto layout) | in-toto layout model is narrower than Timelabs evidence receipts |
| Reuse Register | Chinese 标识网络 decomposition | EXTRACT_PRIMITIVE (as Chinese delta) | Split: naming/identity/locator split is universal (not Chinese delta); 算力网络 is genuine delta | Naming/identity/locator split exists in HIP/LISP/ILNP |
| Novelty Register | Projection honesty contract | POSSIBLY_NOVEL_COMBINATION | KNOWN_COMBINATION (distinctive emphasis) | Data lineage, model cards, view definitions cover similar ground |
| Novelty Register | World2 ontology surgery L0..L9 | POSSIBLY_NOVEL_COMBINATION | KNOWN_COMBINATION (distinctive arrangement) | Layered world decomposition deeply established |
| Novelty Register | Chinese ontology deltas | KNOWN_PRIMITIVE_NEW_APPLICATION (implied from verified sources) | INFERRED (from English secondary sources) | No primary Chinese sources cited |
| Primitive Inventory | log.0 | IMPLEMENTED | SPECIFIED (on main); IMPLEMENTED (on unmerged Codex branch) | Code exists on unmerged branch only |
| Primitive Inventory | Deterministic pose replay | REPRODUCED | REPRODUCED (UNVERIFIED) | Reproduction conditions not documented |
| Semantic Graph | bounded_mutation → openbsd_pf | `implements` | Should be `enables` or `partially_overlaps` | PF provides mechanisms, not the Timelabs contract |
| Semantic Graph | tribunal → argumentation | `formalizes` | Direction questionable: argumentation formalizes concepts Tribunal uses | Edge direction implies Tribunal contributes to argumentation theory |

---

## 9. Unresolved uncertainties (explicitly preserved)

1. **MBSD repository evidence gap:** All MBSD-related classifications are based on Blueshoes/Omnia docs, not MBSD code. Until MBSD repo is inspected, classifications are INFERRED at best.
2. **OPA vs Cedar selection:** Both listed as WRAP_AS_PROVIDER candidates without comparative evaluation criteria or selection decision.
3. **Formal argumentation algorithm choice:** Listed as NEXT EXCAVATION in Executive doc. No algorithm identified, no selection criteria defined.
4. **Deterministic pose replay reproduction details:** Claimed REPRODUCED but no reproduction protocol, conditions, or independent verifier documented.
5. **Chinese primary sources:** All Chinese ontology entries are based on English-language secondary descriptions. Genuine deltas (算力网络, 语义通信) need primary-source verification.
6. **GNUnet/GNS comparison:** Listed as UNKNOWN, remains UNKNOWN.
7. **Cross-branch evidence durability:** Multiple primitives' evidence levels depend on unmerged branches (Codex, Trae). If those branches are abandoned, evidence levels collapse.
8. **Semantic graph completeness:** Graph is intentionally sparse but does not declare its incompleteness.
9. **Projection honesty novelty:** Downgraded to KNOWN_COMBINATION, but a deeper literature search specifically targeting *enforced projection contracts* (vs observational lineage) could potentially re-upgrade. This search was not performed.
10. **in-toto applicability to non-build evidence:** Classified as needing BENCHMARK; no benchmark criteria defined.

---

## Appendix: Sweep limitations

- This falsification pass was conducted against artifacts visible in the PR #6 branch of `omnia-playbook`.
- Cross-repo evidence (Blueshoes, HME, Rhea, MBSD) was NOT independently re-verified; assessments rely on claims made in the artifacts.
- Chinese-language primary source verification was NOT performed (no access to CNKI, Wanfang, or CCSA standards databases in this sweep).
- Literature searches were constrained to knowledge available to the reviewer; systematic database searches (IEEE Xplore, ACM DL, arXiv) were not performed.
- The falsification pass is itself subject to reviewer bias and limited sweep scope. Independent review is required.
