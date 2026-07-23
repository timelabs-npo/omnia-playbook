# `log.0` → multi-NQLite

## Decision

`log.0` is the sole authoritative local record. It uses exact-byte,
length-framed, versioned JSON events. SQLite files are disposable,
independently rebuildable views.

**multi-NQLite** is a project-local label for three named SQLite projections:

1. `catalog.sqlite` — complete decoded envelope and record index;
2. `assurance.sqlite` — observations and deterministic findings;
3. `workflow.sqlite` — plans, approvals, execution receipts, verification, and
   reversal records.

The term does not claim compatibility with an external NQLite product. It does
not imply a database server, network replication, Raft, multi-primary writes,
cross-file atomic transactions, or distributed consensus.

## Why source → views

The split prevents each interface from becoming its own source of truth.

- The append record preserves one inspectable history.
- Views can optimize different questions without rewriting history.
- A broken schema, dashboard, Tribunal, 3D rig, or search index can be deleted
  and rebuilt.
- A new view does not acquire authority merely because it is convenient.
- Rebuild comparison tests projector behavior without trusting SQLite page
  layout.

Omnia, Rhea, the Tribunal, the Deterministic Lens, and future user interfaces
are therefore projections or consumers. None may write a private truth around
`log.0`.

## Exact frame

Each record is stored as:

```text
<body-byte-count>\t<compact-canonical-UTF8-JSON>\t<sha256>\n
```

The digest covers exact stored bytes:

```text
SHA256(
  "omnia-log-v1\0" ||
  previous_digest_bytes ||
  u64be(sequence) ||
  u64be(body_length) ||
  body_bytes
)
```

The first record uses 32 zero bytes as its previous digest material. The JSON
body also carries `previous_digest`; the frame digest is stored outside the
body and is exposed as `digest` by the decoder.

Canonical JSON is UTF-8, sorted by key, with no insignificant whitespace.
Records larger than 256 KiB fail before append. The exact framing prevents a
verifier from silently accepting a digest calculated over a different
serialization.

## DTS ordering

The old Rhea DTS intention was correct: wall-clock time must not decide replay
order.

In Omnia v0, the single writer assigns `sequence = previous + 1`. This is the
committed logical tick. `observed_at` remains evidence metadata and never
overrides sequence.

This is a deliberately narrow DTS:

- all readers reproduce the same committed order;
- a retry with the same UUID and identical content returns the existing tick;
- the same UUID with different content fails;
- late or inaccurate wall clocks do not reorder history.

It is not yet a full distributed Lamport protocol. The earlier Rhea
session-server code assigned `last_message_clock + 1` at server arrival without
receiving or merging producer clocks. That supplies a central sequence, but it
does not prove happens-before across offline producers, CRDT convergence, or
multi-host safety.

A distributed DTS extension must separately specify producer identity,
received clock, `max(local, received) + 1`, deterministic tie-breaking,
authentication, duplicate delivery, offline merge, membership, and recovery.
Until then, those are non-claims.

## Write path

```text
bounded collector
  → schema allowlist
  → minimize / redact
  → validate
  → one locked append writer
  → fsync exact frame
  → acknowledge sequence and digest
```

The writer, not a producer, assigns the sequence. A caller may supply a UUIDv4
for idempotency. Acknowledgement happens only after `fsync`.

The lock is local and advisory-by-protocol. A stale lock or torn final frame
blocks append. Tail truncation is not automatic; it requires an
owner-authorized recovery procedure that records the pre-repair digest and
valid byte boundary. Mid-log corruption always fails closed.

## What the digest can establish

Once a known head is trusted, the chain can detect later byte modification,
deletion inside the retained range, reordering, and forks.

It cannot establish:

- that a source told the truth;
- actor identity or authorization;
- a trusted timestamp;
- completeness of collection;
- prevention of whole-log rollback;
- legal compliance.

An attacker who can rewrite both the log and its local head can create a fresh
internally valid chain. Rollback detection needs periodic owner-signed head
anchors stored independently; that is outside v0.

## Redaction boundary

Redaction precedes append, hashing, and projection:

```text
raw observation → allowlist → redaction → safe event → log.0
```

The public policy rejects payload keys for raw output, stdout/stderr, headers,
cookies, tokens, credentials, private keys, addresses, and private topology.
A secret should become a safe fact such as `credential_present: true`, not
plaintext or an unkeyed digest.

Append-only storage conflicts with deletion and secret-spill remediation. A
tombstone does not erase leaked bytes. Production therefore requires a
separate normative quarantine, key rotation, segment replacement, retention,
and crypto-erasure policy. This remains a publication blocker.

## Projection contract

Every projection is a pure logical transition:

```text
state[n+1] = projector(projector_version, state[n], event[n+1])
```

Projectors may not consult wall clocks, networks, models, randomness, locale,
filesystem discovery, or unordered iteration. Authoritative numeric state uses
integers or explicit decimal text rather than uncontrolled floating point.

Each database records:

```text
_projection_meta(
  projection_name,
  last_seq,
  last_digest,
  projector_version,
  schema_version
)
```

A generation is created under a temporary name, replayed, checked with
`integrity_check` and `foreign_key_check`, closed, and then renamed into place.
The manifest exposes a vector watermark because the three databases are not
one atomic transaction.

SQLite file hashes are packaging checks only. Determinism is compared through
canonical semantic exports with explicit columns and stable ordering.

## Reversal and external effects

Historical records are not edited. Corrections and reversals are new typed
events. Replaying a log can rebuild local views; it cannot undo an external
side effect.

Any future executor requires:

- a plan digest bound to exact targets and operations;
- explicit owner approval and expiry;
- stable idempotency keys;
- before-state evidence;
- execution receipts;
- verification and reconciliation;
- a reversal or remediation event where technically supported.

No executor is part of v0.

## SQLite operational boundary

Published generations are local files. SQLite WAL, when later enabled for
mutable views, is not backup or replication and must not be placed on a network
filesystem. Live database files must not be copied by ordinary file-copy tools;
use the SQLite Backup API or `VACUUM INTO`.

Time Machine, cloud sync, SMB shares, and copied WAL files are continuity or
transport mechanisms, not cross-host database replication. True distribution
requires a separately reviewed protocol.
