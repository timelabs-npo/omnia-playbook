# OpenBSD Sealed-Brick Playbook

This playbook defines a sealed controller appliance architecture on OpenBSD with no web-admin plane and the smallest practical service surface. It does **not** claim invulnerability. The goal is measurable hardening, deterministic execution, bounded evidence collection, and explicit recovery.

## Architecture

- OpenBSD base-system interfaces are the control surface: `pf`, `pfctl`, `ifconfig`, `route`, `rcctl`, `sysctl`, and canonical configuration files.
- There is no LuCI-style or OpenWrt-style web administration replica.
- The appliance does not expose every tunable. Deterministic policy is the execution gate.
- The management plane is intentionally narrow: local console plus an optional local utility on exactly one trusted admin workstation.
- Advisory workers may observe bounded events and disagree, but they are advisory only.

## Bootstrap Sequence

1. Install OpenBSD with only the services required for routing, filtering, and the chosen recovery channel.
2. Define the management interface in `/etc/hostname.if` and the default route in `/etc/mygate`.
3. Install a deny-by-default `pf.conf` with an explicitly preserved management path.
4. Enable only required base services via `rcctl`; leave web-facing admin services disabled.
5. Confirm read-only baseline collection from the v0 boundary in [adapters/openbsd/README.md](../../adapters/openbsd/README.md).
6. Prepare rollback artifacts for `pf.conf`, `hostname.if`, `mygate`, and any enabled network service configs.
7. Rehearse offline syntax validation before any approved live change.

## Admin-Client Boundary

The optional admin utility exists on one trusted admin workstation only. It must let the sovereign user inspect:

- input
- transformation
- decision
- result
- rollback artifact
- receipt

The appliance itself remains sealed. The admin utility has no standing right to widen policy, bypass the deterministic gate, or hide intermediate state from the user.

## Six-Worker Sandbox Model

Up to six small advisory workers may observe bounded events and produce recommendations. Their sandbox rules are fixed:

- no root
- no `pf` or `pfctl` mutation authority
- no policy-widening authority
- no unrestricted egress
- no direct write path to appliance configuration
- disagreement is allowed and expected; deterministic policy decides

`UNKNOWN` is not `PASS`. `FAIL` or `ERROR` aborts the workflow. No worker may loop with unbounded retry.

## Evidence Path

The evidence path is:

1. allowlisted bounded collection
2. minimize and redact
3. validate against a strict contract
4. write through a single-writer DTS
5. append to `log.0`
6. rebuild named SQLite views from the append-only log
7. reserve future signed policy gating as a later step

The v0 deliverable in this repository stops at the bounded collection contract and playbook/reporting structure. It does not implement a signed policy gate yet.

## Hardening Targets

Measure hardening instead of claiming perfect safety:

- no web-admin listener present
- only explicitly enabled services appear in `rcctl ls on`
- management path is documented and preserved through rollback
- packet-filter syntax validates before a live window
- read-only collection remains within the allowlisted v0 boundary
- evidence handling keeps secrets and private topology out of committed artifacts

## Failure Modes

Treat these as first-class failure conditions:

- loss of management path
- packet-filter rule rejection or unintended lockout
- route replacement that breaks return traffic
- resolver change that obscures or misroutes control traffic
- advisory-worker disagreement with no deterministic decision
- missing rollback artifact
- evidence contract failure

`UNKNOWN`, `FAIL`, and `ERROR` block progression. They do not degrade to `PASS`.

## Recovery

1. Stop at the first blocking result.
2. Use console or other approved out-of-band access.
3. Restore the last known-good network and `pf` artifacts.
4. Reconfirm interface state, route state, and packet-filter state from the base system.
5. Re-run only the bounded read-only collection needed to verify recovery.
6. Append a recovery receipt to the evidence log and operator report.

## Rollback

Rollback is file-oriented and deterministic:

- restore the last approved `pf.conf`
- restore the last approved `hostname.if`
- restore the last approved `/etc/mygate`
- restore any approved service config that participated in the change
- verify management reachability before any further step

Never widen policy as an emergency shortcut without explicit owner approval.

## Explicit Non-Goals

- building a web-admin plane
- exposing every OpenBSD tunable in a UI
- granting advisory workers mutation authority
- claiming the appliance is invulnerable
- storing secrets, private addresses, or private hostnames in repository evidence
- implementing the future signed policy gate in this v0
