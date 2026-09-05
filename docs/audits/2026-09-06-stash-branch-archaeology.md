# Stash propagation and branch archaeology: omnia-playbook

This documentation-only record routes archival evidence to its relevant repository. Snapshot: **2026-09-06, Europe/Moscow**, before the documentation branches created by this pass. Every comparison below uses fixed commit IDs.

The canonical archive is [rhea-project/stash](https://github.com/timelabs-npo/rhea-project/blob/3316bae0770744238099c25ae34e76e7ad4af8b4/stash/README.md). It is a normal Git branch named `stash`, separate from local `refs/stash`. Its 37 archive files total **361,824 bytes**; this pass reconstructed their UTF-8 bytes locally, verified each Git blob SHA-1 and size, and verified SHA-256 after disk readback. The four content-addressed original reports also match the SHA-256 encoded in their paths and total **115,053 bytes**.

The [original collection manifest](https://github.com/timelabs-npo/rhea-project/blob/3316bae0770744238099c25ae34e76e7ad4af8b4/stash/runs/2026-09-06-cloud-001/manifest.json) still records **41 pending items/groups** and `PARTIAL_WD_UNAVAILABLE`. That is the original cloud capture's state, not a statement that this Windows host lacks filesystem access. Mirroring the published archive does not collect the binaries, source trees, VM disks or histories merely named in those reports. Those pending artifacts were not captured in this pass.

At the six inspected main tips, no blob matches any of the 37 `stash/` archive blobs. This is exact-content evidence, not proof that no paraphrases, links or equivalent implementation exist. The propagation proposed here is a pinned documentation pointer and repository-specific findings; implementation adoption remains a separate change.

## Repository findings and routing

The [append-only capacity assessment](https://github.com/timelabs-npo/rhea-project/blob/3316bae0770744238099c25ae34e76e7ad4af8b4/stash/docs/experience/OMNIA_APPEND_ONLY.md) inspected `c9220eee388bba1b4d256d0a6ebd241cf5060102`. Current main `0b2edc1085482c576afa694d7310d34ac6cd87f0` is two commits ahead, changing only `README.md` and `docs/readme/hero.svg`. Thus those changes do not add the missing storage mechanisms identified by that assessment. [Baseline-to-main changes](https://github.com/timelabs-npo/omnia-playbook/compare/c9220eee388bba1b4d256d0a6ebd241cf5060102...0b2edc1085482c576afa694d7310d34ac6cd87f0).

That main-only assessment does not cover all branch work. [PR #3](https://github.com/timelabs-npo/omnia-playbook/pull/3), `codex/council-readiness`, contains `scripts/log0.py`, log/projection schemas and tests. [PR #4](https://github.com/timelabs-npo/omnia-playbook/pull/4), `trae/a0l-audit`, contains platform contracts, ADRs, validators and `reports/RECONCILIATION_MAIN_TRAE_CODEX_COPILOT.md`. Both are open drafts. Review overlap and salvage useful pieces before implementing a new register from the main-only gap list. Presence of those files does not establish durable append-only storage or successful execution.

[PR #7](https://github.com/timelabs-npo/omnia-playbook/pull/7), `integration/rhea-link-v1@7a233147423dd350fcdcc8aa2709c0091df5bb02`, contains the legacy OMNA ABI producer. Six `.omnb` fixtures plus `SHA256SUMS` and `manifest.json` have matching Git blobs in Rheknel's corresponding branch (renamed to `tests/fixtures/OMNIA_SHA256SUMS` and `omnia-manifest.json`). This verifies fixture identity, not runtime compatibility or v2 qualification.

[PR #8](https://github.com/timelabs-npo/omnia-playbook/pull/8), Comparator contract `42c704e90068cb23abebf94d83eed93ed51b7060`, is a sibling of #7: one commit ahead and two behind it, with common base `c9220eee...`. Its only branch-side file is `integrations/rhea-comparator-pro.md`; it does not inherit #7's ABI implementation. [Pinned sibling comparison](https://github.com/timelabs-npo/omnia-playbook/compare/7a233147423dd350fcdcc8aa2709c0091df5bb02...42c704e90068cb23abebf94d83eed93ed51b7060). A legacy integration would need an explicit combined baseline; clean-slate v2 does not automatically require this ABI.

[PR #9](https://github.com/timelabs-npo/omnia-playbook/pull/9) (maintenance) pairs by subject with [Omnia Vault #2](https://github.com/timelabs-npo/omnia-vault/pull/2). [PR #10](https://github.com/timelabs-npo/omnia-playbook/pull/10) (Flow) pairs with [Blueshoes #9](https://github.com/timelabs-npo/Blueshoes/pull/9). These are draft contracts and adoption documents in this snapshot.

Use the [36-technique index](https://github.com/timelabs-npo/rhea-project/blob/3316bae0770744238099c25ae34e76e7ad4af8b4/stash/docs/experience/techniques.json) for selective reuse. The smallest next code change is a scoped reconciliation of the existing log0/audit branches and archive record requirements, with its own behavioral verification; copying the whole stash branch would not implement those requirements.

## Branch ledger

Pinned main: `0b2edc1085482c576afa694d7310d34ac6cd87f0`. Ahead/behind counts measure commit ancestry relative to that main. They do not measure missing patches, successful tests or merge readiness. Historical merged PRs can refer to older heads, or contain content integrated without the original ancestry.

| Branch | Pinned head | Ahead / behind main | PR evidence |
| --- | --- | --- | --- |
| `codex/council-readiness` | [`0b348b0ffed6`](https://github.com/timelabs-npo/omnia-playbook/commit/0b348b0ffed6ce73f3135f1c9e591968668d63bc) | 3 / 2 | [#3](https://github.com/timelabs-npo/omnia-playbook/pull/3) open draft |
| `copilot/create-infrastructure-playbook-repo` | [`fab811736821`](https://github.com/timelabs-npo/omnia-playbook/commit/fab811736821a3e9c49c3fac7d38bb2ddd093b28) | 0 / 8 | [#2](https://github.com/timelabs-npo/omnia-playbook/pull/2) merged |
| `copilot/timelabs-semantic-neighbour-excavation` | [`4687fc18692b`](https://github.com/timelabs-npo/omnia-playbook/commit/4687fc18692b7fc4599adf0b4fcbe7e9593708df) | 5 / 2 | [#6](https://github.com/timelabs-npo/omnia-playbook/pull/6) open draft |
| `evolution/maintenance-semantic-redteam-v1` | [`35c21e2a5631`](https://github.com/timelabs-npo/omnia-playbook/commit/35c21e2a56310870090ef927f8f7bfadfcc761aa) | 6 / 2 | [#9](https://github.com/timelabs-npo/omnia-playbook/pull/9) open draft |
| `evolution/network-flow-semantic-redteam-v1` | [`2be243aa0e04`](https://github.com/timelabs-npo/omnia-playbook/commit/2be243aa0e04a2666256c7d0d566fbed5bd26eac) | 3 / 2 | [#10](https://github.com/timelabs-npo/omnia-playbook/pull/10) open draft |
| `integration/rhea-link-v1` | [`7a233147423d`](https://github.com/timelabs-npo/omnia-playbook/commit/7a233147423dd350fcdcc8aa2709c0091df5bb02) | 2 / 2 | [#7](https://github.com/timelabs-npo/omnia-playbook/pull/7) open |
| `integrations/rhea-comparator-pro` | [`42c704e90068`](https://github.com/timelabs-npo/omnia-playbook/commit/42c704e90068cb23abebf94d83eed93ed51b7060) | 1 / 2 | [#8](https://github.com/timelabs-npo/omnia-playbook/pull/8) open draft |
| `main` | [`0b2edc108548`](https://github.com/timelabs-npo/omnia-playbook/commit/0b2edc1085482c576afa694d7310d34ac6cd87f0) | 0 / 0 | none in retrieved PR history |
| `trae/a0l-audit` | [`ca52ba266856`](https://github.com/timelabs-npo/omnia-playbook/commit/ca52ba2668566bc6c9d60b23c945029cf94c5432) | 12 / 2 | [#4](https://github.com/timelabs-npo/omnia-playbook/pull/4) open draft |

## Verification limits

All branch lists and PR lists fit within the 100-item first page. Comparisons cover every non-main branch. The checkpoint branch's explicit no-common-ancestor response is recorded as unrelated history. Recursive trees used for content identity checks were not truncated. GitHub comparison file lists can stop at 300 files; a 300-entry list is not a complete large-branch diff. No broad patch-equivalence analysis of the older Rhea histories was performed.

This pass used GitHub metadata, pinned trees, selected documents and local archive hashing. Component tests, builds, deployment checks, production runtime checks and pending WD artifact collection were not run. The archive's published Drive and scheduler receipts were read as historical records; those external states were not reverified or changed.
