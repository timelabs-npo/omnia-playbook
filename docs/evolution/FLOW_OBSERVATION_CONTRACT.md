# Read-only Flow Observation fixture contract

This is an independently specified data contract for the paired Blueshoes slice.
The corpus and assertions in this repository do not import the Blueshoes producer,
normalizer or graph. Blueshoes may consume these JSON bytes and the wire schema;
it must not import this repository's Python validator or oracle implementation.

## Wire schema revision

The unreleased `FlowObservationV1` schema is widened on 2026-09-06 to permit
`null` for required `bytes_up` and `bytes_down`. Null means unavailable, while
integer zero means measured zero. Rates already allow null. Both byte properties
remain required. All previously valid V1 documents remain valid under the revised
schema. Older integer-only readers reject null-bearing documents; this is not
forward compatibility. The corpus manifest records the exact schema SHA-256.
Original Git blob: `35d7b12f2cb2f14b9fc2e672504bb19f5f7df552` at
`2be243aa0e04a2666256c7d0d566fbed5bd26eac`. Hashes use repository LF bytes,
not a platform's CRLF checkout conversion.

Wire schema compatibility and the narrower native-input application profile are
different gates. NetBSD remains a valid wire platform. The requested native
interfaces cover Darwin, Windows, Linux and OpenBSD only. JSON integers beyond
the implementation's unsigned 64-bit range are rejected by the Blueshoes profile;
JSON Schema itself has no such finite integer bound.

## Native sample profile

`NativeFlowSampleV1` is a bounded, observation-only adapter interchange DTO, not
a binary OS table dump. It carries platform, collector_scope, snapshot_id,
observed_at, declared freshness and records. Every record contains record_id,
source/destination, protocol, counters, policy, route, optional process and
display_location. No action, executor, command, capability, or helper field exists.

Process evidence contains pid, kind, birth_before and birth_after. Native platform
contracts use `darwin_start_us` (kernel process start, microseconds),
`win32_creation_100ns` (GetProcessTimes FILETIME), `linux_start_ticks` (process start
ticks in the collector's boot scope), and `openbsd_start_us` (kernel process start,
microseconds). The timestamps are exact integer evidence, never rounded to seconds.
Only matching, nonzero birth identities bracketing the actual socket sample bind
a process. Missing evidence, zero PID or rebinding yields a null process_ref.
Process references encode platform, collector scope, PID and birth. A flow ID
encodes platform, collector scope, snapshot and record ID; a reused socket tuple
across samples is a new observation, without a continuity claim.

The DTO fixture adapter always supplies fixture provenance itself. Imported wire
provenance is a source assertion, not proof of local execution. Native provenance
may only come from actual host queries. Fixture evaluation uses the manifest's
fixed clock and maximum age. Stale/unknown declarations cannot become fresh;
future timestamps become unknown and excessive age becomes stale.

## Projection expectations and authority

The graph is a stateless observation projection with process and endpoint nodes,
flow edges and complete supporting observations. It preserves provenance,
observed_at, evaluated freshness and `authority: observation_only`. Unknown process
associations remain absent. Duplicate conflicting observation IDs reject instead
of overwriting. Masked/derived display metadata never changes endpoint truth,
route evidence or graph identity. Text resembling an action remains inert display
data; action-bearing object fields reject structurally, without a keyword blacklist.

The wire/projection is not a substrate entity, execution capability or canonical
substrate receipt. No mutation is implemented or authorized by this contract.

## Gates

Portable fixture execution is reported separately from native execution. Darwin,
Linux and OpenBSD live collection are NOT_EXECUTED until native implementations
and receipts exist. Windows collection covers read-only TCP IPv4/IPv6 only;
UDP, byte/rate telemetry, route/policy detection and atomic socket identity are
NOT_EXECUTED. No fixture PASS upgrades any of these gaps.

ClashMac is only a closed-source behavioral reference at
`666OS/ClashMac@6bd4eee77ac3face93d6ba38fdc505e15a4e376e`.
No ClashMac code, assets or binaries are imported.
