#!/usr/bin/env python3
"""Deterministic Omnia -> Rheknel compact-bus encoder and reference decoder."""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any, Iterable

import yaml
from yaml.constructor import ConstructorError
from yaml.events import AliasEvent


MAGIC = b"OMNA"
ABI_MAJOR = 1
ABI_MINOR = 0
HEADER_SIZE = 128
FLAGS = 0x00000003  # canonical ordering + exact integer/domain encoding
FRAME_DIGEST_OFFSET = 84
FRAME_DIGEST_SIZE = 32
MAX_DEPTH = 64
MAX_SOURCE_SIZE = 4 * 1024 * 1024
EVIDENCE_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
PROVENANCE_RE = re.compile(r"^git:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}:.+$")

KIND_CODES = {"invariant": 1, "check": 2}
KIND_NAMES = {value: key for key, value in KIND_CODES.items()}

STATE_DOMAINS = {
    "consistency": ({"unknown": 0, "pass": 1, "fail": 2, "error": 3}, 0, 0x3),
    "applicability": (
        {"unknown": 0, "applicable": 1, "not_applicable": 2, "error": 3},
        2,
        0x3,
    ),
    "verifiability": (
        {"unknown": 0, "verified": 1, "unverified": 2, "error": 3},
        4,
        0x3,
    ),
    "reliability": (
        {"unknown": 0, "reliable": 1, "degraded": 2, "unreliable": 3, "error": 4},
        6,
        0x7,
    ),
}

TAG_NULL = 0
TAG_FALSE = 1
TAG_TRUE = 2
TAG_UINT = 3
TAG_SINT = 4
TAG_STRING = 5
TAG_ARRAY = 6
TAG_MAP = 7


class CodecError(ValueError):
    """Input or wire-format violation."""


class NoDatesSafeLoader(yaml.SafeLoader):
    """SafeLoader variant that leaves ISO dates as strings."""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
        mapping: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in mapping
            except TypeError as exc:
                raise ConstructorError("while constructing a mapping", node.start_mark, "unhashable key", key_node.start_mark) from exc
            if duplicate:
                raise ConstructorError("while constructing a mapping", node.start_mark, f"duplicate key {key!r}", key_node.start_mark)
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


NoDatesSafeLoader.yaml_implicit_resolvers = copy.deepcopy(yaml.SafeLoader.yaml_implicit_resolvers)
for first_char, resolvers in list(NoDatesSafeLoader.yaml_implicit_resolvers.items()):
    NoDatesSafeLoader.yaml_implicit_resolvers[first_char] = [
        item for item in resolvers if item[0] != "tag:yaml.org,2002:timestamp"
    ]


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise CodecError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def _load_json(data: str | bytes) -> Any:
    return json.loads(data, object_pairs_hook=_reject_duplicate_pairs)


@dataclasses.dataclass(frozen=True)
class Record:
    kind: str
    record_id: str
    path: str
    states: dict[str, str]
    assessed_at: int
    fresh_until: int
    evidence_ids: tuple[str, ...]
    provenance_ids: tuple[str, ...]
    metadata: dict[str, Any]


@dataclasses.dataclass(frozen=True)
class Bundle:
    bundle_id: str
    target_platform: str
    created_at: int
    fresh_until: int
    records: tuple[Record, ...]
    source_digest: bytes


def _uleb(value: int) -> bytes:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise CodecError(f"ULEB128 requires a non-negative integer, got {value!r}")
    output = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            output.append(byte | 0x80)
        else:
            output.append(byte)
            return bytes(output)


def _read_uleb(data: bytes, offset: int, limit: int | None = None) -> tuple[int, int]:
    end = len(data) if limit is None else min(limit, len(data))
    value = 0
    shift = 0
    for _ in range(10):
        if offset >= end:
            raise CodecError("truncated ULEB128")
        byte = data[offset]
        offset += 1
        if shift == 63 and (byte & 0xFE):
            raise CodecError("ULEB128 exceeds uint64")
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, offset
        shift += 7
    raise CodecError("overlong ULEB128")


def _require_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise CodecError(f"{name} must be a non-empty NUL-free string")
    value.encode("utf-8")
    return value


def _require_epoch(value: Any, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 0xFFFFFFFFFFFFFFFF:
        raise CodecError(f"{name} must be an exact uint64 epoch-second integer")
    return value


def _validate_value(value: Any, path: str = "$", depth: int = 0) -> None:
    if depth > MAX_DEPTH:
        raise CodecError(f"metadata nesting exceeds {MAX_DEPTH} at {path}")
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if not -(1 << 63) <= value <= (1 << 64) - 1:
            raise CodecError(f"integer outside int64/uint64 domain at {path}")
        return
    if isinstance(value, float):
        raise CodecError(f"floats are rejected rather than quantized lossily at {path}")
    if isinstance(value, str):
        if "\x00" in value:
            raise CodecError(f"NUL is forbidden in strings at {path}")
        value.encode("utf-8")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_value(item, f"{path}[{index}]", depth + 1)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or "\x00" in key:
                raise CodecError(f"map keys must be NUL-free strings at {path}")
            key.encode("utf-8")
            _validate_value(item, f"{path}.{key}", depth + 1)
        return
    raise CodecError(f"unsupported metadata type {type(value).__name__} at {path}")


def _load_document(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    if len(raw) > MAX_SOURCE_SIZE:
        raise CodecError(f"source exceeds {MAX_SOURCE_SIZE} bytes: {path}")
    try:
        if path.suffix == ".json":
            value = _load_json(raw)
        elif path.suffix in {".yaml", ".yml"}:
            if any(isinstance(event, AliasEvent) for event in yaml.parse(raw, Loader=NoDatesSafeLoader)):
                raise CodecError(f"YAML aliases are rejected: {path}")
            value = yaml.load(raw, Loader=NoDatesSafeLoader)
        else:
            raise CodecError(f"unsupported source extension: {path}")
    except (json.JSONDecodeError, yaml.YAMLError, UnicodeDecodeError) as exc:
        raise CodecError(f"cannot parse {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CodecError(f"source document must be an object: {path}")
    _validate_value(value)
    return value, raw


def _state_word(states: dict[str, str]) -> int:
    if not isinstance(states, dict) or set(states) != set(STATE_DOMAINS):
        raise CodecError(f"states must contain exactly {sorted(STATE_DOMAINS)}")
    word = 0
    for name, (domain, shift, _mask) in STATE_DOMAINS.items():
        value = states[name]
        if value not in domain:
            raise CodecError(f"unsupported {name} state: {value!r}")
        word |= domain[value] << shift
    return word


def _state_dict(word: int) -> dict[str, str]:
    if word & 0xFE00:
        raise CodecError("reserved state bits are non-zero")
    output: dict[str, str] = {}
    for name, (domain, shift, mask) in STATE_DOMAINS.items():
        code = (word >> shift) & mask
        reverse = {value: key for key, value in domain.items()}
        if code not in reverse:
            raise CodecError(f"undefined {name} state code {code}")
        output[name] = reverse[code]
    return output


def _source_digest(sources: Iterable[tuple[str, bytes]]) -> bytes:
    digest = hashlib.sha256()
    digest.update(b"omnia-source-v1\x00")
    for path, raw in sorted(sources, key=lambda item: item[0].encode("utf-8")):
        path_bytes = path.encode("utf-8")
        digest.update(struct.pack(">I", len(path_bytes)))
        digest.update(path_bytes)
        digest.update(struct.pack(">Q", len(raw)))
        digest.update(raw)
    return digest.digest()


def load_bundle(root: Path, manifest_path: Path) -> Bundle:
    root = root.resolve()
    manifest_path = manifest_path.resolve()
    manifest = _load_json(manifest_path.read_text(encoding="utf-8"))
    required = {
        "schema",
        "abi_major",
        "abi_minor",
        "bundle_id",
        "target_platform",
        "created_at",
        "fresh_until",
        "documents",
    }
    if set(manifest) != required:
        raise CodecError(f"manifest fields must be exactly {sorted(required)}")
    if manifest["schema"] != "omnia.rheknel.bundle-source/v1":
        raise CodecError("unsupported bundle-source schema")
    if (manifest["abi_major"], manifest["abi_minor"]) != (ABI_MAJOR, ABI_MINOR):
        raise CodecError("compiler only emits ABI 1.0; upgrade/downgrade is forbidden")
    bundle_id = _require_text(manifest["bundle_id"], "bundle_id")
    target_platform = _require_text(manifest["target_platform"], "target_platform")
    created_at = _require_epoch(manifest["created_at"], "created_at")
    fresh_until = _require_epoch(manifest["fresh_until"], "fresh_until")
    if fresh_until < created_at:
        raise CodecError("bundle fresh_until precedes created_at")
    if not isinstance(manifest["documents"], list) or not manifest["documents"]:
        raise CodecError("documents must be a non-empty array")

    records: list[Record] = []
    source_items: list[tuple[str, bytes]] = []
    seen_ids: set[str] = set()
    for index, entry in enumerate(manifest["documents"]):
        if not isinstance(entry, dict):
            raise CodecError(f"documents[{index}] must be an object")
        expected = {
            "path",
            "kind",
            "assessed_at",
            "fresh_until",
            "states",
            "evidence_ids",
            "provenance_ids",
        }
        if set(entry) != expected:
            raise CodecError(f"documents[{index}] fields must be exactly {sorted(expected)}")
        relative = _require_text(entry["path"], f"documents[{index}].path")
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise CodecError(f"source path escapes repository: {relative}")
        source_path = (root / relative_path).resolve()
        try:
            source_path.relative_to(root)
        except ValueError as exc:
            raise CodecError(f"source path escapes repository: {relative}") from exc
        metadata, raw = _load_document(source_path)
        kind = entry["kind"]
        if kind not in KIND_CODES:
            raise CodecError(f"unsupported record kind: {kind!r}")
        record_id = _require_text(metadata.get("id"), f"{relative}.id")
        if record_id in seen_ids:
            raise CodecError(f"contradictory/duplicate record id: {record_id}")
        seen_ids.add(record_id)
        if kind == "invariant" and not isinstance(metadata.get("check"), dict):
            raise CodecError(f"invariant lacks check metadata: {relative}")
        if kind == "check" and not isinstance(metadata.get("invariant"), str):
            raise CodecError(f"check lacks invariant reference: {relative}")
        evidence_ids = tuple(entry["evidence_ids"]) if isinstance(entry["evidence_ids"], list) else ()
        provenance_ids = tuple(entry["provenance_ids"]) if isinstance(entry["provenance_ids"], list) else ()
        if not evidence_ids or not provenance_ids:
            raise CodecError(f"evidence and provenance are mandatory for {record_id}")
        for name, values in (("evidence_ids", evidence_ids), ("provenance_ids", provenance_ids)):
            if len(values) != len(set(values)):
                raise CodecError(f"{name} must be unique for {record_id}")
            for value in values:
                _require_text(value, f"{record_id}.{name}")
        if any(EVIDENCE_RE.fullmatch(value) is None for value in evidence_ids):
            raise CodecError(f"evidence IDs must be lowercase sha256:<64-hex> for {record_id}")
        if any(PROVENANCE_RE.fullmatch(value) is None or not value.endswith(":" + relative) for value in provenance_ids):
            raise CodecError(f"provenance IDs must bind git repo, 40-hex commit, and source path for {record_id}")
        evidence_ids = tuple(sorted(evidence_ids, key=lambda value: value.encode("utf-8")))
        provenance_ids = tuple(sorted(provenance_ids, key=lambda value: value.encode("utf-8")))
        actual_evidence = f"sha256:{hashlib.sha256(raw).hexdigest()}"
        if actual_evidence not in evidence_ids:
            raise CodecError(f"{record_id} evidence_ids lacks exact source digest {actual_evidence}")
        assessed_at = _require_epoch(entry["assessed_at"], f"{record_id}.assessed_at")
        record_fresh_until = _require_epoch(entry["fresh_until"], f"{record_id}.fresh_until")
        if assessed_at > created_at or record_fresh_until < assessed_at:
            raise CodecError(f"invalid assessment freshness interval for {record_id}")
        states = entry["states"]
        _state_word(states)
        records.append(
            Record(
                kind=kind,
                record_id=record_id,
                path=relative,
                states=dict(states),
                assessed_at=assessed_at,
                fresh_until=record_fresh_until,
                evidence_ids=evidence_ids,
                provenance_ids=provenance_ids,
                metadata=metadata,
            )
        )
        source_items.append((relative, raw))

    invariant_ids = {record.record_id for record in records if record.kind == "invariant"}
    for record in records:
        if record.kind == "check" and record.metadata["invariant"] not in invariant_ids:
            raise CodecError(f"check {record.record_id} references absent invariant")
    records.sort(key=lambda record: (record.record_id.encode("utf-8"), record.path.encode("utf-8")))
    return Bundle(
        bundle_id=bundle_id,
        target_platform=target_platform,
        created_at=created_at,
        fresh_until=fresh_until,
        records=tuple(records),
        source_digest=_source_digest(source_items),
    )


def _collect_strings(value: Any, strings: set[str]) -> None:
    if isinstance(value, str):
        strings.add(value)
    elif isinstance(value, list):
        for item in value:
            _collect_strings(item, strings)
    elif isinstance(value, dict):
        for key, item in value.items():
            strings.add(key)
            _collect_strings(item, strings)


def _encode_value(value: Any, string_ids: dict[str, int], depth: int = 0) -> bytes:
    if depth > MAX_DEPTH:
        raise CodecError("metadata nesting limit exceeded")
    if value is None:
        return bytes([TAG_NULL])
    if value is False:
        return bytes([TAG_FALSE])
    if value is True:
        return bytes([TAG_TRUE])
    if isinstance(value, int):
        if value >= 0:
            return bytes([TAG_UINT]) + _uleb(value)
        zigzag = ((-value) << 1) - 1
        return bytes([TAG_SINT]) + _uleb(zigzag)
    if isinstance(value, str):
        return bytes([TAG_STRING]) + _uleb(string_ids[value])
    if isinstance(value, list):
        return bytes([TAG_ARRAY]) + _uleb(len(value)) + b"".join(
            _encode_value(item, string_ids, depth + 1) for item in value
        )
    if isinstance(value, dict):
        items = sorted(value.items(), key=lambda item: item[0].encode("utf-8"))
        output = bytearray([TAG_MAP])
        output.extend(_uleb(len(items)))
        for key, item in items:
            output.extend(_uleb(string_ids[key]))
            output.extend(_encode_value(item, string_ids, depth + 1))
        return bytes(output)
    raise CodecError(f"unsupported value during encoding: {type(value).__name__}")


def encode_bundle(bundle: Bundle, *, validate_semantics: bool = True) -> bytes:
    if validate_semantics:
        if not bundle.records:
            raise CodecError("bundle must contain records")
        seen: set[str] = set()
        for record in bundle.records:
            if record.record_id in seen:
                raise CodecError(f"duplicate record id: {record.record_id}")
            seen.add(record.record_id)
            if not record.evidence_ids or not record.provenance_ids:
                raise CodecError(f"evidence/provenance missing for {record.record_id}")
            _state_word(record.states)
            _validate_value(record.metadata)

    strings: set[str] = {bundle.bundle_id, bundle.target_platform}
    for record in bundle.records:
        strings.update((record.record_id, record.path))
        strings.update(record.evidence_ids)
        strings.update(record.provenance_ids)
        _collect_strings(record.metadata, strings)
    ordered_strings = sorted(strings, key=lambda value: value.encode("utf-8"))
    if len(ordered_strings) > 0xFFFF:
        raise CodecError("string table exceeds uint16 count")
    string_ids = {value: index for index, value in enumerate(ordered_strings)}
    string_section = bytearray()
    for value in ordered_strings:
        encoded = value.encode("utf-8")
        string_section.extend(_uleb(len(encoded)))
        string_section.extend(encoded)

    record_section = bytearray()
    for record in bundle.records:
        metadata = _encode_value(record.metadata, string_ids)
        body = bytearray([KIND_CODES[record.kind]])
        body.extend(struct.pack(">H", _state_word(record.states)))
        body.extend(_uleb(string_ids[record.record_id]))
        body.extend(_uleb(string_ids[record.path]))
        body.extend(_uleb(record.assessed_at))
        body.extend(_uleb(record.fresh_until))
        body.extend(_uleb(len(record.evidence_ids)))
        for evidence_id in record.evidence_ids:
            body.extend(_uleb(string_ids[evidence_id]))
        body.extend(_uleb(len(record.provenance_ids)))
        for provenance_id in record.provenance_ids:
            body.extend(_uleb(string_ids[provenance_id]))
        body.extend(_uleb(len(metadata)))
        body.extend(metadata)
        record_section.extend(_uleb(len(body)))
        record_section.extend(body)

    strings_offset = HEADER_SIZE
    records_offset = strings_offset + len(string_section)
    total_size = records_offset + len(record_section)
    if total_size > 0xFFFFFFFF:
        raise CodecError("bundle exceeds uint32 wire size")
    header = bytearray(HEADER_SIZE)
    struct.pack_into(
        ">4sBBHIIIHHIIIQQ32s32sII4s",
        header,
        0,
        MAGIC,
        ABI_MAJOR,
        ABI_MINOR,
        HEADER_SIZE,
        total_size,
        FLAGS,
        0,
        len(bundle.records),
        len(ordered_strings),
        strings_offset,
        records_offset,
        len(record_section),
        bundle.created_at,
        bundle.fresh_until,
        bundle.source_digest,
        bytes(FRAME_DIGEST_SIZE),
        string_ids[bundle.bundle_id],
        string_ids[bundle.target_platform],
        bytes(4),
    )
    output = header + string_section + record_section
    digest = hashlib.sha256(output).digest()
    output[FRAME_DIGEST_OFFSET : FRAME_DIGEST_OFFSET + FRAME_DIGEST_SIZE] = digest
    return bytes(output)


def compile_bundle(root: Path, manifest_path: Path) -> bytes:
    return encode_bundle(load_bundle(root, manifest_path))


def decode_bundle(data: bytes, *, require_semantics: bool = True) -> dict[str, Any]:
    if len(data) < HEADER_SIZE:
        raise CodecError("truncated header")
    unpacked = struct.unpack_from(">4sBBHIIIHHIIIQQ32s32sII4s", data, 0)
    (
        magic,
        major,
        minor,
        header_size,
        total_size,
        flags,
        reserved0,
        record_count,
        string_count,
        strings_offset,
        records_offset,
        records_size,
        created_at,
        fresh_until,
        source_digest,
        frame_digest,
        bundle_sid,
        target_sid,
        reserved_tail,
    ) = unpacked
    if magic != MAGIC:
        raise CodecError("bad magic")
    if (major, minor) != (ABI_MAJOR, ABI_MINOR):
        raise CodecError("unsupported ABI; exact 1.0 required")
    if header_size != HEADER_SIZE or flags != FLAGS or reserved0 or reserved_tail != bytes(4):
        raise CodecError("unsupported header flags/reserved fields")
    if total_size != len(data):
        raise CodecError("declared total_size mismatch")
    if strings_offset != HEADER_SIZE or not strings_offset <= records_offset <= total_size:
        raise CodecError("invalid section offsets")
    if records_offset + records_size != total_size:
        raise CodecError("invalid record section size")
    zeroed = data[:FRAME_DIGEST_OFFSET] + bytes(FRAME_DIGEST_SIZE) + data[FRAME_DIGEST_OFFSET + FRAME_DIGEST_SIZE :]
    if hashlib.sha256(zeroed).digest() != frame_digest:
        raise CodecError("frame SHA-256 mismatch")

    strings: list[str] = []
    cursor = strings_offset
    for _ in range(string_count):
        size, cursor = _read_uleb(data, cursor, records_offset)
        if size > records_offset - cursor:
            raise CodecError("truncated string")
        try:
            value = data[cursor : cursor + size].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CodecError("invalid UTF-8 string") from exc
        if "\x00" in value:
            raise CodecError("NUL in string table")
        strings.append(value)
        cursor += size
    if cursor != records_offset or bundle_sid >= len(strings) or target_sid >= len(strings):
        raise CodecError("invalid string table boundary/reference")

    def decode_value(offset: int, limit: int, depth: int = 0) -> tuple[Any, int]:
        if depth > MAX_DEPTH or offset >= limit:
            raise CodecError("invalid metadata nesting/truncation")
        tag = data[offset]
        offset += 1
        if tag == TAG_NULL:
            return None, offset
        if tag == TAG_FALSE:
            return False, offset
        if tag == TAG_TRUE:
            return True, offset
        if tag == TAG_UINT:
            return _read_uleb(data, offset, limit)
        if tag == TAG_SINT:
            zigzag, offset = _read_uleb(data, offset, limit)
            return (-(zigzag // 2) - 1 if zigzag & 1 else zigzag // 2), offset
        if tag == TAG_STRING:
            sid, offset = _read_uleb(data, offset, limit)
            if sid >= len(strings):
                raise CodecError("metadata string reference out of range")
            return strings[sid], offset
        if tag == TAG_ARRAY:
            count, offset = _read_uleb(data, offset, limit)
            values = []
            for _ in range(count):
                value, offset = decode_value(offset, limit, depth + 1)
                values.append(value)
            return values, offset
        if tag == TAG_MAP:
            count, offset = _read_uleb(data, offset, limit)
            values = {}
            last_key: bytes | None = None
            for _ in range(count):
                sid, offset = _read_uleb(data, offset, limit)
                if sid >= len(strings):
                    raise CodecError("map key reference out of range")
                key = strings[sid]
                key_bytes = key.encode("utf-8")
                if last_key is not None and key_bytes <= last_key:
                    raise CodecError("map keys are not strictly canonical")
                last_key = key_bytes
                value, offset = decode_value(offset, limit, depth + 1)
                values[key] = value
            return values, offset
        raise CodecError(f"unknown metadata tag {tag}")

    records = []
    cursor = records_offset
    seen_ids: set[str] = set()
    for _ in range(record_count):
        body_size, body = _read_uleb(data, cursor, total_size)
        end = body + body_size
        if end > total_size or body + 3 > end:
            raise CodecError("truncated record")
        kind_code = data[body]
        body += 1
        if kind_code not in KIND_NAMES:
            raise CodecError("unknown record kind")
        state_word = struct.unpack_from(">H", data, body)[0]
        body += 2
        record_sid, body = _read_uleb(data, body, end)
        path_sid, body = _read_uleb(data, body, end)
        assessed_at, body = _read_uleb(data, body, end)
        record_fresh_until, body = _read_uleb(data, body, end)
        evidence_count, body = _read_uleb(data, body, end)
        evidence_ids = []
        for _ in range(evidence_count):
            sid, body = _read_uleb(data, body, end)
            if sid >= len(strings):
                raise CodecError("evidence string reference out of range")
            evidence_ids.append(strings[sid])
        provenance_count, body = _read_uleb(data, body, end)
        provenance_ids = []
        for _ in range(provenance_count):
            sid, body = _read_uleb(data, body, end)
            if sid >= len(strings):
                raise CodecError("provenance string reference out of range")
            provenance_ids.append(strings[sid])
        metadata_size, body = _read_uleb(data, body, end)
        metadata_end = body + metadata_size
        if metadata_end > end:
            raise CodecError("truncated metadata")
        metadata, body = decode_value(body, metadata_end)
        if body != metadata_end or metadata_end != end:
            raise CodecError("non-canonical trailing record bytes")
        if record_sid >= len(strings) or path_sid >= len(strings):
            raise CodecError("record string reference out of range")
        record_id = strings[record_sid]
        if require_semantics and record_id in seen_ids:
            raise CodecError(f"contradictory duplicate record id: {record_id}")
        seen_ids.add(record_id)
        if require_semantics and (not evidence_ids or not provenance_ids):
            raise CodecError(f"evidence/provenance missing for {record_id}")
        records.append(
            {
                "kind": KIND_NAMES[kind_code],
                "id": record_id,
                "path": strings[path_sid],
                "states": _state_dict(state_word),
                "assessed_at": assessed_at,
                "fresh_until": record_fresh_until,
                "evidence_ids": evidence_ids,
                "provenance_ids": provenance_ids,
                "metadata": metadata,
            }
        )
        cursor = end
    if cursor != total_size:
        raise CodecError("record count/section boundary mismatch")
    return {
        "abi": f"{major}.{minor}",
        "bundle_id": strings[bundle_sid],
        "target_platform": strings[target_sid],
        "created_at": created_at,
        "fresh_until": fresh_until,
        "source_sha256": source_digest.hex(),
        "frame_sha256": frame_digest.hex(),
        "record_count": record_count,
        "string_count": string_count,
        "records": records,
    }


def mutate_for_negative_fixture(bundle: Bundle, case: str) -> bytes:
    """Generate deterministic invalid fixtures; not exposed by the compiler CLI."""
    if case == "contradictory":
        duplicate = dataclasses.replace(bundle.records[0], states={**bundle.records[0].states, "consistency": "fail"})
        return encode_bundle(dataclasses.replace(bundle, records=bundle.records + (duplicate,)), validate_semantics=False)
    if case == "provenance-missing":
        first = dataclasses.replace(bundle.records[0], provenance_ids=())
        return encode_bundle(dataclasses.replace(bundle, records=(first,) + bundle.records[1:]), validate_semantics=False)
    if case == "boundary":
        first = dataclasses.replace(bundle.records[0], assessed_at=0, fresh_until=0xFFFFFFFFFFFFFFFF)
        return encode_bundle(dataclasses.replace(bundle, created_at=0xFFFFFFFFFFFFFFFF, fresh_until=0xFFFFFFFFFFFFFFFF, records=(first,) + bundle.records[1:]))
    if case == "unsupported-version":
        output = bytearray(encode_bundle(bundle))
        output[5] = ABI_MINOR + 1
        return bytes(output)
    if case == "malformed":
        return encode_bundle(bundle)[:-1]
    raise CodecError(f"unknown negative fixture case: {case}")
