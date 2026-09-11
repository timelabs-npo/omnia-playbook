# Guides

These guides explain how to use the playbook as an AI helper's reference. They describe responsibilities and review methods. Their presence does not install an agent, connect a host, or authorize a change.

- [Current technical reset](../adapters/timelabs/omnia-vault/reviews/2026-09-12/technical-reset/README.md): the governing refinement package; implementation is locked and every macOS prototype is discarded as the baseline.
- [AI helper guide](ai-helper.md): turn a request and observations into a bounded task with clear results.
- [Foundation](../foundation/): state what should remain true.
- [Platform adapters](../adapters/): map a requirement to the platform that can implement it.
- [Checks](../checks/): read-only observations; the current implemented slice is DNS.
- [Diagnostic playbooks](../playbooks/diagnostics/): interpret observations before proposing a repair.
- [Local agent boundary](../local-agent/README.md): requirements for any separately authorized host access.
- [Contribution rules](../CONTRIBUTING.md): validation, read-only checks, and safe repository content.

The [repository README](../README.md) records the current executable scope and verification limits. A document, code inspection, screenshot, process state, or successful command exit is evidence of its own result, not proof of an entire product or network guarantee.

## Current technical refinement

Read the [technical contract](../adapters/timelabs/omnia-vault/reviews/2026-09-12/technical-reset/TECHNICAL_CONTRACT.md), [LIT admission gate](../adapters/timelabs/omnia-vault/reviews/2026-09-12/technical-reset/LIT_GATE.md), [network contract](../adapters/timelabs/omnia-vault/reviews/2026-09-12/technical-reset/NETWORK_CONTRACT.md) and [requirements register](../adapters/timelabs/omnia-vault/reviews/2026-09-12/technical-reset/REQUIREMENTS.md) before using earlier material. No macOS/product implementation is admitted during this phase. LIT oracle work and engine qualification follow their separate prerequisite gates. The LIT candidate remains not frozen, with no admitted engine or compliant reset receipts.

Network continuity is the current critical workstream, not a reduction of the full beta. All requested providers, sync and archive outcomes remain in scope. Earlier architecture, layouts, repair instructions and numerical proposals do not become accepted requirements merely because they appear in a supporting document.

## Historical desktop correction review

The earlier 12 September 2026 material is a sanitized source-review snapshot and correction task. It describes historical findings and acceptance cases; it does not claim that the product was corrected, deployed, or passed those cases. Its implementation directions are superseded by the technical reset.

- [Superseded correction task](../adapters/timelabs/omnia-vault/reviews/2026-09-12/CORRECTION_TASK.md): historical repair directions; do not execute them as the current task.
- [UI inventory](../adapters/timelabs/omnia-vault/reviews/2026-09-12/UI_INVENTORY.md): visible functions, their effects and proposed labels.
- [Native pane review](../adapters/timelabs/omnia-vault/reviews/2026-09-12/NATIVE_PANE_REVIEW.md): the actual settings surface and its control routes.
- [Backend review](../adapters/timelabs/omnia-vault/reviews/2026-09-12/BACKEND_REVIEW.md): command behavior, measurements, maintenance and archive-use limits.
- [Extra command review](../adapters/timelabs/omnia-vault/reviews/2026-09-12/EXTRA_COMMAND_REVIEW.md): command surfaces that can remain reachable without visible buttons.
- [Network facts](../adapters/timelabs/omnia-vault/reviews/2026-09-12/NETWORK_FACTS.md): primary-source boundaries for network claims.
- [Review scope and acceptance](../adapters/timelabs/omnia-vault/reviews/2026-09-12/REVIEW_SCOPE.md): evidence examined, limits and checks still to perform.

## Supporting continuity requirements

These documents describe intended behavior and acceptance contracts. They do not install providers, authorize an operation, or represent an active sync, archive, or maintenance engine. Preserve all requested provider scope while tracking each adapter's actual capabilities and acceptance separately.

Use them for supporting requirements and research, subject to the reset's latest decisions. In particular, earlier requirements to preserve prototype surfaces or start another layout do not survive the reset.

- [Technical specification](requirements/continuity/technical-spec.md).
- [Monitor and action registry](requirements/continuity/registry.md).
- [State and data contracts](requirements/continuity/uml-contracts.md).

- [Provider and reference-tool notes](../adapters/continuity/references.md) — source-backed differences and limits, kept under adapters.
