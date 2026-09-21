# TIMELABS_EVIDENCE_GOVERNANCE_NEIGHBOURS

## Motif: “Omnia constrains; Tribunal decides; runtime executes; providers testify.”

### Semantic equivalents
- **PDP/PEP architectures:** policy decision point separated from enforcement point.
- **Safety-kernel/supervisory-control architectures:** constrained action set + high-integrity supervisor.
- **Event-sourcing + append-only logs:** authoritative sequence with rebuildable views.
- **Transparency logs:** append-only witness structures for tamper evidence.
- **Supply-chain provenance frameworks:** signed attestations and threshold trust.

## Comparative decomposition

| Timelabs role | Neighbour abstraction | Representative systems |
|---|---|---|
| Constraint authority | policy language + PDP | OPA, Cedar |
| Decision/arbitration | argumentation + evidence tiering | Dung-style frameworks, adversarial evaluation protocols |
| Execution runtime | bounded executor with rollback contracts | transaction-safe network mutation patterns, canary/rollback systems |
| Testimony/evidence provider | attestation and provenance emitters | in-toto, SLSA attestations, transparency logs |
| Source-of-record | append-only log with deterministic replay | event sourcing, ledger-like transparency systems |

## Governance tensions surfaced
1. **Consensus cannot be terminal authority** without reproducibility tiers (already explicit in Blueshoes protocol).
2. **Cloud mirrors can silently become authority** unless role classifications are enforced (Cloud Constitution solves this explicitly).
3. **Replayability and truth are distinct:** deterministic replay proves consistency, not correctness of upstream observations.
