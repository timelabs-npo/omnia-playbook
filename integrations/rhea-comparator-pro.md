# Rhea Comparator Pro — Omnia integration contract

**Status:** proposed alpha integration  
**Target repository:** `timelabs-npo/rhea-comparator-pro`  
**License:** MIT  
**Initial device plane:** macOS + WD external volume + iPhone control surface; Windows CLI/daemon binaries

## Purpose

Rhea Comparator Pro is the filesystem/state-plane implementation of the General Common Comparator concept. It exposes one immutable causal namespace through platform-specific projections rather than pretending one kernel driver can operate identically on every OS.

## Non-negotiable invariants

1. Published refs point only to durable immutable objects.
2. One object ID never denotes two byte sequences.
3. Concurrent mutations are never silently discarded.
4. Wall-clock time is display metadata, not proof of causality.
5. Network or kernel-facing requests are explicitly bounded.
6. Consumer cloud drives are replicas unless they pass conditional-ref authority tests.
7. No device is reported online without successful transport authentication.

## Omnia execution chain

```text
capability
  → registered operation
  → local/platform adapter
  → bounded observation or explicit mutation
  → normalization
  → redaction
  → validation
  → hash-chained log.0 evidence
```

Observation and mutation capabilities remain separate. An observer cannot move a ref; a control operation cannot present itself as passive observation.

## Registered operations

| Operation | Capability | Mutation boundary | Evidence |
|---|---|---|---|
| `op-rhea-status` | observe | none | metadata-only status |
| `op-rhea-verify` | observe | none; reads reachable objects | verification result |
| `op-wd-vault-init` | control | creates only selected `/Volumes/.../RheaVault` metadata | repository initialization |
| `op-nebulavault-inventory` | observe | read-only bundle inspection | signed/hashable inventory directory |
| `op-rhea-pause` | control | persists operator sync-admission intent; does not rewrite refs | control event |
| `op-rhea-resume` | control | persists operator sync-admission intent; does not rewrite refs | control event |

The authoritative machine-readable capability and operation descriptors live in the Comparator repository under `omnia/`.

## Initial authority split

```text
WD/local filesystem       durable immutable objects + local refs
SQLite/binary journals    local mutation/outbox durability
Rhea daemon               bounded authenticated control API + SSE invalidations
CockroachDB                optional later distributed ref/fencing authority
Redis / Valkey             optional invalidation pulse only; never authority
S3 / Azure                 later immutable object replicas/authority candidates
Google Drive / iCloud      downstream replica/backup only until conformance proof
GitHub                     code, playbooks, prompts, release provenance
```

CockroachDB and Redis are deliberately not required for the first working binary. The first vertical slice must survive and verify locally before any distributed dependency is added.

## Agent branch contract

Codex, Trae, Copilot, and suagent workers receive a task ID, allowed paths, byte/time budget, required tests, and a non-authoritative agent ref:

```text
refs/agent/codex/<task-id>
refs/agent/trae/<task-id>
refs/agent/suagent/<task-id>
refs/device/<device-id>
refs/main
```

Workers cannot promote `main`. Promotion is a separately reviewed comparator/controller operation.

## Security boundary for the physical-phone alpha

- Loopback HTTP may run without a token for local development.
- Non-loopback listeners require a 256-bit token.
- Plaintext LAN control is disabled unless the operator explicitly selects a development-only override.
- Persistent or external testing requires TLS or a certificate-bound private mesh.
- Discovery is never authentication.
- Existing simulated mesh status from other Rhea prototypes must not be imported as connectivity evidence.

## Acceptance gate

The integration is eligible to move from proposed to active only when:

1. `go test -race ./...`, `go vet ./...`, and the release smoke test pass.
2. macOS and iOS targets typecheck/build in Xcode on the target Mac.
3. A real WD volume is initialized without formatting or deleting unrelated data.
4. A physical iPhone authenticates, reads exact repository/device IDs, persists pause/resume intent, and receives a zero-error verification report.
5. NebulaVault is inventoried from `/Users/sa/Applications/NebulaVault.app`; no feature is called fused merely because the old bundle displays it.
6. TestFlight archive/upload is completed with the actual signing and App Store Connect records.

## Product rule

The commit graph and reachable manifests define filesystem truth. Provider directory listings, Redis pulses, UI state, and agent assertions are hints or projections—not authority.
