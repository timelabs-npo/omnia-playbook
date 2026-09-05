# Omnia Vault evolution link

Status: semantic red-team linkage; no runtime gate is promoted by this document.

This playbook branch is the semantic reconciliation companion to the Kudu → Omnia evolution branch.

## Local branch / PR

- Repository: `timelabs-npo/omnia-playbook`
- Branch: `evolution/maintenance-semantic-redteam-v1`
- Draft PR: `#9`
- Prior head before this linkage commit: `9921ece3bc33dfe9f0a3a8c3985e522d75b0411a`
- Baseline: `c9220eee388bba1b4d256d0a6ebd241cf5060102`

## Companion Omnia branch / PR

- Repository: `timelabs-npo/omnia-vault`
- Branch: `evolution/kudu-omnia-v1`
- Draft PR: `#2`
- Companion head observed after its linkage commit: `ada2d783a3b688cb5352634d6202a45a5124273c`
- Frozen Omnia baseline: `f5995536fede02d403f0525ff9093996457efecb`

## Source dialect lock

- Kudu upstream: `AdventDevInc/kudu@92dbc52336ad9c9eb2968a180d22c72670de3b45`

## Reconciliation rule

The playbook owns semantic normal forms, cross-platform equivalence, fixtures and independent adversarial checks. It never turns `proposal_only` into execution authority.

The companion Omnia branch may consume only a frozen playbook contract revision. Any translator or adapter change that changes semantic meaning requires a new playbook revision and independent revalidation before runtime integration.
