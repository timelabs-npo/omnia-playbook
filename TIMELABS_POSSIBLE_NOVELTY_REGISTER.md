# TIMELABS_POSSIBLE_NOVELTY_REGISTER

## Classification scale
- KNOWN
- KNOWN_COMBINATION
- KNOWN_PRIMITIVE_NEW_APPLICATION
- KNOWN_CONCEPT_DIFFERENT_IMPLEMENTATION
- POSSIBLY_NOVEL_COMBINATION
- POSSIBLY_NOVEL_PRIMITIVE
- UNKNOWN

## Register

| Timelabs primitive/candidate | Classification | Rationale |
|---|---|---|
| log.0 exact-byte append + disposable multi-view SQLite projectors | KNOWN_CONCEPT_DIFFERENT_IMPLEMENTATION | Semantically event sourcing + tamper-evident framing; implementation boundary choices are specific but concept family is established. |
| Projection honesty contract (explicit preserve/drop/aggregation declarations) | KNOWN_COMBINATION | Related ideas exist in data lineage (OpenLineage), model cards, and database view definitions. The enforcement-contract framing (deterministic replay + explicit preserve/drop as requirement) is distinctive emphasis on known concepts, not a novel combination. Downgraded per falsification pass — absence of counter-evidence in limited sweep does not establish novelty. |
| Consensus-is-evidence-not-truth governance axiom | KNOWN | Strongly represented in formal epistemics, argumentation, and adversarial verification traditions. |
| Cloud-memory-without-sovereignty constitutional role taxonomy | KNOWN_COMBINATION | Analogues in edge sovereignty and control-plane/data-plane separations; Blueshoes role taxonomy is a concrete composition. |
| OpenBSD sealed-brick bounded collection with explicit UNKNOWN escalation | KNOWN_PRIMITIVE_NEW_APPLICATION | Uses known safety principles, applied to a narrowly-scoped OpenBSD governance contract. |
| World2 ontology surgery (L0..L9 narrative boundary discipline) | KNOWN_COMBINATION | Components are known; layered world decomposition is deeply established in robotics, game engines, and OSI model. The specific layer numbering and anti-category-error framing is a distinctive arrangement of known concepts. Downgraded per falsification pass. |
| Read-only → replay → bounded mutation as cross-cell doctrine | KNOWN_COMBINATION | Deep precedent in safety engineering/canary/digital twins; novelty may come from unified multi-cell doctrine expression. |
| Chinese ontology deltas for 标识网络/算力网络 integrated into Timelabs lexicon | KNOWN_PRIMITIVE_NEW_APPLICATION | Existing traditions, newly imported into current Timelabs conceptual stack. Evidence level: INFERRED from English secondary sources only; no primary Chinese-language sources verified. Naming/identity/locator split entries are TRANSLATION_ONLY; 算力网络 and 语义通信 entries are GENUINE_DELTA. |

## Items explicitly not claimable as novel from current evidence
- policy-as-code primitives
- append-only evidence logging
- rollback-safe mutation transactions
- multipath and path-aware networking primitives
- deterministic simulation replay
