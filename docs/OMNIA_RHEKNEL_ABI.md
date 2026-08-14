# Omnia ↔ Rheknel binary ABI 1.0

Status: normative for ABI `1.0`. Producer: Omnia. Consumer/verdict owner: Rheknel.

This is a typed byte boundary between the two existing repositories. It does not create an orchestrator, daemon, RPC service, or third authority.

## Exact-version rule

The header carries one-byte major and minor versions. A 1.0 consumer accepts exactly `(1, 0)`. It must reject older, newer, or partially understood versions with `UNSUPPORTED_VERSION`; it must not upgrade, downgrade, negotiate, reinterpret, or ignore unknown flags. The only legal migration is an explicitly implemented new encoder/decoder pair with new golden vectors.

## Header

All fixed-width integers are unsigned big-endian. The header is exactly 128 bytes.

| Offset | Size | Field | ABI 1.0 rule |
| ---: | ---: | --- | --- |
| 0 | 4 | magic | ASCII `OMNA` |
| 4 | 1 | ABI major | `1` |
| 5 | 1 | ABI minor | `0` |
| 6 | 2 | header size | `128` |
| 8 | 4 | total size | exact file size |
| 12 | 4 | flags | exactly `0x00000003` |
| 16 | 4 | reserved | zero |
| 20 | 2 | record count | non-zero |
| 22 | 2 | string count | non-zero |
| 24 | 4 | string-section offset | `128` |
| 28 | 4 | record-section offset | checked boundary |
| 32 | 4 | record-section size | ends at total size |
| 36 | 8 | created at | exact Unix epoch seconds |
| 44 | 8 | fresh until | exact Unix epoch seconds |
| 52 | 32 | source SHA-256 | digest defined below |
| 84 | 32 | frame SHA-256 | whole frame with this field zeroed |
| 116 | 4 | bundle-id string ID | in range |
| 120 | 4 | target-platform string ID | in range |
| 124 | 4 | reserved | zero |

The source digest is:

```text
SHA256(
  "omnia-source-v1\0" ||
  for each source path in ascending UTF-8 byte order:
    u32be(path_byte_length) || path_utf8 ||
    u64be(raw_file_byte_length) || raw_file_bytes
)
```

This commits to exact source bytes and paths. Each record also carries the source file's `sha256:<hex>` evidence ID and a repository/commit/path provenance ID.

## String and record sections

The string table is unique and sorted by raw UTF-8 bytes. An entry is `ULEB128(byte length) || UTF-8 bytes`. NUL and invalid UTF-8 are rejected. Record and metadata references are zero-based string IDs.

Records are sorted by record ID then source path, both in UTF-8 byte order. Each record is:

```text
ULEB128(body_size)
u8 kind                         # 1 invariant, 2 check
u16be packed_states
ULEB128(id_string_id)
ULEB128(source_path_string_id)
ULEB128(assessed_at_epoch_s)
ULEB128(fresh_until_epoch_s)
ULEB128(evidence_count) + evidence string IDs
ULEB128(provenance_count) + provenance string IDs
ULEB128(metadata_size) + typed metadata value
```

Evidence and provenance counts must both be non-zero. Their string IDs are strictly increasing, so duplicates and non-canonical order are rejected. ABI 1.0 evidence IDs are lowercase `sha256:<64-hex>` values. Provenance IDs are `git:owner/repository@<40-hex-commit>:<source-path>` and the path must exactly match the record's source path. Duplicate record IDs are contradictory and rejected even when their payloads match.

## Exact compaction and information-loss guarantee

ABI 1.0 performs domain coding, not lossy compression:

- record kinds are exact one-byte enumerations;
- the four state domains use nine meaningful bits in one 16-bit word; all seven spare bits must be zero;
- non-negative integers use canonical ULEB128; signed integers use exact ZigZag + ULEB128;
- timestamps must be integer epoch seconds at the source boundary; fractional timestamps are rejected, never rounded;
- strings are deduplicated but their UTF-8 bytes remain exact;
- map keys are sorted, while array order remains exact;
- metadata values use tags: null `0`, false `1`, true `2`, unsigned integer `3`, signed integer `4`, string reference `5`, array `6`, map `7`;
- floating-point input is rejected because ABI 1.0 has no lossless cross-platform float contract.

For the admitted JSON/YAML value domain (null, boolean, int64/uint64, UTF-8 string, array, string-keyed map), decoding reproduces the same typed value graph. YAML presentation details such as comments, indentation, anchors, and key order are not semantic payload; exact raw source bytes remain committed by the source digest and per-file evidence IDs.

No field is rounded, truncated, normalized to natural language, or silently discarded.

## State domains

| Bits | Domain | Codes |
| --- | --- | --- |
| 0–1 | consistency | 0 unknown, 1 pass, 2 fail, 3 error |
| 2–3 | applicability | 0 unknown, 1 applicable, 2 not-applicable, 3 error |
| 4–5 | verifiability | 0 unknown, 1 verified, 2 unverified, 3 error |
| 6–8 | reliability | 0 unknown, 1 reliable, 2 degraded, 3 unreliable, 4 error |
| 9–15 | reserved | must be zero |

Freshness is evaluated from a caller-supplied `now_epoch_s`; the decoder never reads a clock. A bundle or record is fresh through its `fresh_until` second and stale when `now_epoch_s > fresh_until`.

## Deterministic verdict mapping

Rheknel owns the final verdict. ABI framing never grants authority.

| Condition | Bus status | Rheknel verdict |
| --- | --- | --- |
| exact frame, fresh, ≥1 applicable record, all applicable records pass/verified/reliable | OK | OK |
| explicit consistency fail, unverified, unreliable, or duplicate/contradictory ID | semantic rejection | REJECT |
| stale, unknown applicability/state, degraded reliability, or no applicable record | insufficient current assurance | ESCALATE |
| malformed/bounds/hash/version/reserved/state-code failure; missing evidence/provenance | contract error | ERROR |

Not-applicable records are preserved and structurally validated but are neutral for the target-specific pass calculation. An `ERROR`, `ESCALATE`, or `REJECT` verdict never reaches an action callback.

## Limits and failure handling

The portable consumer is allocation-free and rejects frames larger than 16 MiB, more than 4096 records, more than 65535 strings, overlong/non-canonical ULEB128, invalid offsets, invalid UTF-8, metadata deeper than 64 levels, unknown tags/kinds/state codes, trailing bytes, frame-digest mismatch, invalid/missing evidence or provenance, and duplicate IDs. The producer additionally rejects source files above 4 MiB, YAML aliases, duplicate JSON/YAML keys, non-string map keys, and unsupported value types.

## Platform boundary

The decoder uses C99 fixed-width types and byte reads; it does not cast packed structs, depend on host endianness, allocate, execute shell commands, or call Linux APIs. The CLI's OpenBSD compatibility path enters `pledge("stdio rpath", NULL)` before reading and reduces to `pledge("stdio", NULL)` afterward.

As inspected at `timelabs-npo/mbsd@a970e76ee41104e80aea8a1782a8053da2a3e116`, MBSD is currently OpenWrt 23.05.4/Linux for MediaTek MT7981, not an OpenBSD-derived target. ABI 1.0 therefore makes no MBSD/OpenBSD compatibility claim. An MBSD build claim requires its actual OpenWrt SDK/toolchain and is tracked separately from OpenBSD verification.
