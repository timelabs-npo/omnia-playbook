# TIMELABS_CROSS_CELL_OPPORTUNITIES

| Opportunity | Source primitive | Target cells | Opportunity type | Notes |
|---|---|---|---|---|
| Event-sourcing substrate for Omnia receipts | append-only log + deterministic projectors | Omnia + Tribunal + Blueshoes | EXTRACT_PRIMITIVE | Codex `log.0` line already converges toward this; formalize with explicit projector honesty contracts. |
| SCION path-policy provider lane | path-aware trust-root and multipath controls | Blueshoes/MBSD | WRAP_AS_PROVIDER | Use as provider candidate, not doctrine replacement; evaluate sovereignty and incremental deployability. |
| Digital-twin replay gate before live mutation | replay-first safety envelope | HME + MBSD + Omnia | EXTRACT_PRIMITIVE | “Read-only → replay → bounded mutation” can become shared pre-failure gate. |
| Belief revision for Tribunal disagreements | argumentation/belief revision formalisms | Tribunal + Omnia governance | REIMPLEMENT_FROM_SPEC | Aligns with majority-not-sufficient contracts in Trae disagreement schema. |
| Chinese 标识网络 decomposition | identifier/resolution/service split | Blueshoes + MBSD + Omnia naming/identity | EXTRACT_PRIMITIVE | Distinguish human naming vs cryptographic identity vs service identity vs locator. |
| OpenBSD manipulation alphabet as canonical MBSD grammar | PF+route sockets+divert+relayd mechanisms | MBSD + Blueshoes | REUSE_DIRECTLY | Native mechanism palette enables strict authority ceilings and deterministic rollback. |
| WorldEngine provenance envelope for non-graphics cells | explicit source class + validity/freshness + stale semantics | HME + World2 + Omnia evidence model | WRAP_AS_PROVIDER | HME claims register discipline is reusable for runtime truth boundaries. |
| TUF role delegation for owner intent and authority transfer | root/targets/delegations threshold roles | Omnia + Tribunal | EXTRACT_PRIMITIVE | Useful for typed authority delegation and revocation semantics. |
| ICE/MASQUE reachability bundle | rendezvous + NAT traversal + proxy tunnel | Blueshoes + mobile/edge adapters | WRAP_AS_PROVIDER | Avoid bespoke traversal reinvention; preserve explicit policy controls. |
