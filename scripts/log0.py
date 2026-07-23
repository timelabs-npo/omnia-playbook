#!/usr/bin/env python3
"""Append, verify, and project Omnia log.0 records using only Python stdlib."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Sequence


ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "schemas" / "sql"
PROJECTOR_VERSION = 1
SCHEMA_VERSION = 1
FRAME_DOMAIN = b"omnia-log-v1\0"
GENESIS_DIGEST = bytes(32)
EVENT_KINDS = {
    "observation",
    "finding",
    "plan",
    "approval",
    "execution",
    "verification",
    "reversal",
}
STATUSES = {"PASS", "FAIL", "UNKNOWN", "ERROR"}
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
SUBJECT_REF_RE = re.compile(r"^[A-Za-z0-9._:/-]+$")
PUBLIC_FORBIDDEN_KEYS = {
    "address",
    "addresses",
    "authorization",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "email",
    "header",
    "headers",
    "hostname",
    "interface",
    "ip",
    "ips",
    "password",
    "private_key",
    "raw",
    "raw_output",
    "resolver_addresses",
    "search_domains",
    "secret",
    "stderr",
    "stdout",
    "token",
}
MAX_EVENT_BYTES = 256 * 1024
MAX_LENGTH_FIELD_BYTES = 12


class LogError(ValueError):
    """Raised when an event or log violates the log.0 contract."""


class TornTailError(LogError):
    """Raised when the final frame is incomplete and no mid-log bytes follow it."""

    def __init__(self, offset: int, valid_bytes: int) -> None:
        super().__init__(
            f"torn final frame at byte {offset}; "
            f"{valid_bytes} preceding bytes are valid; append is blocked"
        )
        self.offset = offset
        self.valid_bytes = valid_bytes


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def canonical_json_bytes(value: Any) -> bytes:
    return canonical_json(value).encode("utf-8")


def calculate_frame_digest(
    previous_digest: str | None,
    sequence: int,
    body_bytes: bytes,
) -> str:
    previous = GENESIS_DIGEST if previous_digest is None else bytes.fromhex(previous_digest)
    material = b"".join(
        (
            FRAME_DOMAIN,
            previous,
            sequence.to_bytes(8, "big", signed=False),
            len(body_bytes).to_bytes(8, "big", signed=False),
            body_bytes,
        )
    )
    return hashlib.sha256(material).hexdigest()


def encode_frame(event_without_digest: dict[str, Any]) -> tuple[bytes, str]:
    body_bytes = canonical_json_bytes(event_without_digest)
    if len(body_bytes) > MAX_EVENT_BYTES:
        raise LogError(f"event body exceeds {MAX_EVENT_BYTES} bytes")
    digest = calculate_frame_digest(
        event_without_digest["previous_digest"],
        event_without_digest["sequence"],
        body_bytes,
    )
    return str(len(body_bytes)).encode("ascii") + b"\t" + body_bytes + b"\t" + digest.encode(
        "ascii"
    ) + b"\n", digest


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_utc_seconds(value: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise LogError(
            "observed_at must be UTC with whole seconds: YYYY-MM-DDTHH:MM:SSZ"
        ) from exc


def require_uuid4(value: Any, label: str) -> str:
    try:
        parsed = uuid.UUID(str(value))
    except (ValueError, AttributeError) as exc:
        raise LogError(f"{label} must be a UUIDv4") from exc
    if parsed.version != 4 or str(parsed) != str(value).lower():
        raise LogError(f"{label} must be a canonical lowercase UUIDv4")
    return str(parsed)


def walk_keys(value: Any) -> Iterator[str]:
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key).lower()
            yield from walk_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from walk_keys(nested)


def validate_common(event: dict[str, Any]) -> None:
    if event.get("kind") not in EVENT_KINDS:
        raise LogError(f"unsupported kind: {event.get('kind')!r}")
    if event.get("status") not in STATUSES:
        raise LogError(f"unsupported status: {event.get('status')!r}")

    observed_at = event.get("observed_at")
    if not isinstance(observed_at, str):
        raise LogError("observed_at must be a string")
    require_utc_seconds(observed_at)

    source = event.get("source")
    if not isinstance(source, dict) or set(source) != {"adapter", "collector", "version"}:
        raise LogError("source must contain exactly adapter, collector, and version")
    for key, maximum in (("adapter", 80), ("collector", 120), ("version", 40)):
        value = source[key]
        if not isinstance(value, str) or not value or len(value) > maximum:
            raise LogError(
                f"source.{key} must be a non-empty string up to {maximum} characters"
            )

    subject = event.get("subject")
    if not isinstance(subject, dict) or set(subject) != {"type", "ref"}:
        raise LogError("subject must contain exactly type and ref")
    if not isinstance(subject["type"], str) or not 1 <= len(subject["type"]) <= 40:
        raise LogError("subject.type must be a non-empty string up to 40 characters")
    if (
        not isinstance(subject["ref"], str)
        or not 1 <= len(subject["ref"]) <= 160
        or not SUBJECT_REF_RE.fullmatch(subject["ref"])
    ):
        raise LogError("subject.ref contains unsupported characters or length")

    if not isinstance(event.get("payload"), dict):
        raise LogError("payload must be an object")

    redaction = event.get("redaction")
    if (
        not isinstance(redaction, dict)
        or set(redaction) != {"policy", "applied"}
        or not isinstance(redaction["policy"], str)
        or not redaction["policy"]
        or len(redaction["policy"]) > 80
        or redaction["applied"] is not True
    ):
        raise LogError("redaction must contain a policy and applied=true")

    if redaction["policy"] == "omnia-public-v1":
        forbidden = sorted(set(walk_keys(event["payload"])) & PUBLIC_FORBIDDEN_KEYS)
        if forbidden:
            raise LogError(
                "omnia-public-v1 payload contains forbidden keys: " + ", ".join(forbidden)
            )


def validate_draft(draft: dict[str, Any]) -> None:
    required = {"observed_at", "kind", "status", "source", "subject", "payload", "redaction"}
    allowed = required | {"event_id"}
    if not required <= set(draft) or not set(draft) <= allowed:
        missing = sorted(required - set(draft))
        extra = sorted(set(draft) - allowed)
        raise LogError(f"draft fields mismatch; missing={missing}, extra={extra}")
    if "event_id" in draft:
        require_uuid4(draft["event_id"], "event_id")
    validate_common(draft)


def validate_stored_event(
    event: dict[str, Any],
    expected_sequence: int,
    previous: str | None,
    exact_body: bytes,
) -> None:
    required = {
        "schema_version",
        "event_id",
        "sequence",
        "observed_at",
        "kind",
        "status",
        "source",
        "subject",
        "payload",
        "redaction",
        "previous_digest",
        "digest",
    }
    if set(event) != required:
        missing = sorted(required - set(event))
        extra = sorted(set(event) - required)
        raise LogError(f"stored event fields mismatch; missing={missing}, extra={extra}")
    if event["schema_version"] != SCHEMA_VERSION:
        raise LogError(f"unsupported schema_version at sequence {expected_sequence}")
    require_uuid4(event["event_id"], f"event_id at sequence {expected_sequence}")
    if event["sequence"] != expected_sequence:
        raise LogError(
            f"sequence discontinuity: expected {expected_sequence}, got {event['sequence']!r}"
        )
    if event["previous_digest"] != previous:
        raise LogError(f"previous_digest mismatch at sequence {expected_sequence}")
    if not isinstance(event["digest"], str) or not DIGEST_RE.fullmatch(event["digest"]):
        raise LogError(f"invalid digest syntax at sequence {expected_sequence}")
    unsigned = dict(event)
    supplied_digest = unsigned.pop("digest")
    if canonical_json_bytes(unsigned) != exact_body:
        raise LogError(f"non-canonical JSON body at sequence {expected_sequence}")
    calculated = calculate_frame_digest(previous, expected_sequence, exact_body)
    if supplied_digest != calculated:
        raise LogError(f"digest mismatch at sequence {expected_sequence}")
    validate_common(event)


def _read_exact(handle: Any, count: int) -> bytes:
    chunks: list[bytes] = []
    remaining = count
    while remaining:
        chunk = handle.read(remaining)
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    previous: str | None = None
    valid_bytes = 0
    with path.open("rb") as handle:
        while True:
            frame_offset = handle.tell()
            first = handle.read(1)
            if first == b"":
                return events

            length_field = bytearray(first)
            while not length_field.endswith(b"\t"):
                if len(length_field) > MAX_LENGTH_FIELD_BYTES:
                    raise LogError(f"invalid length field at byte {frame_offset}")
                byte = handle.read(1)
                if byte == b"":
                    raise TornTailError(frame_offset, valid_bytes)
                length_field.extend(byte)

            length_text = bytes(length_field[:-1])
            if (
                not length_text.isdigit()
                or length_text.startswith(b"0")
                or int(length_text) > MAX_EVENT_BYTES
            ):
                raise LogError(f"invalid body length at byte {frame_offset}")
            body_length = int(length_text)
            body = _read_exact(handle, body_length)
            if len(body) != body_length:
                raise TornTailError(frame_offset, valid_bytes)
            separator = _read_exact(handle, 1)
            digest_bytes = _read_exact(handle, 64)
            newline = _read_exact(handle, 1)
            if len(separator) != 1 or len(digest_bytes) != 64 or len(newline) != 1:
                raise TornTailError(frame_offset, valid_bytes)
            if separator != b"\t" or newline != b"\n":
                raise LogError(f"invalid frame delimiters at byte {frame_offset}")
            try:
                digest = digest_bytes.decode("ascii")
                decoded = body.decode("utf-8")
                event = json.loads(decoded)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise LogError(f"invalid event body at byte {frame_offset}: {exc}") from exc
            if not isinstance(event, dict):
                raise LogError(f"event body at byte {frame_offset} is not an object")
            event["digest"] = digest
            validate_stored_event(event, len(events) + 1, previous, body)
            events.append(event)
            previous = digest
            valid_bytes = handle.tell()


@contextmanager
def single_writer_lock(log_path: Path) -> Iterator[None]:
    lock_path = Path(f"{log_path}.lock")
    try:
        lock_path.mkdir()
    except FileExistsError as exc:
        raise LogError(
            f"writer lock exists: {lock_path}; inspect the log tail before owner-approved recovery"
        ) from exc
    try:
        (lock_path / "owner.json").write_text(
            canonical_json({"pid": os.getpid(), "log": str(log_path)}) + "\n",
            encoding="utf-8",
        )
        yield
    finally:
        owner_file = lock_path / "owner.json"
        if owner_file.exists():
            owner_file.unlink()
        lock_path.rmdir()


def _draft_from_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": event["event_id"],
        "observed_at": event["observed_at"],
        "kind": event["kind"],
        "status": event["status"],
        "source": event["source"],
        "subject": event["subject"],
        "payload": event["payload"],
        "redaction": event["redaction"],
    }


def _write_all(file_descriptor: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        written = os.write(file_descriptor, view)
        if written <= 0:
            raise OSError("append returned no progress")
        view = view[written:]


def append_event(log_path: Path, draft: dict[str, Any]) -> dict[str, Any]:
    validate_draft(draft)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with single_writer_lock(log_path):
        events = read_events(log_path)
        requested_id = draft.get("event_id")
        if requested_id is not None:
            for existing in events:
                if existing["event_id"] != requested_id:
                    continue
                if _draft_from_event(existing) == draft:
                    return existing
                raise LogError(f"event_id {requested_id} already exists with different content")

        sequence = len(events) + 1
        previous = events[-1]["digest"] if events else None
        event_without_digest = {
            "schema_version": SCHEMA_VERSION,
            "event_id": requested_id or str(uuid.uuid4()),
            "sequence": sequence,
            "observed_at": draft["observed_at"],
            "kind": draft["kind"],
            "status": draft["status"],
            "source": draft["source"],
            "subject": draft["subject"],
            "payload": draft["payload"],
            "redaction": draft["redaction"],
            "previous_digest": previous,
        }
        frame, digest = encode_frame(event_without_digest)
        event = {**event_without_digest, "digest": digest}
        validate_stored_event(event, sequence, previous, canonical_json_bytes(event_without_digest))

        descriptor = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            _write_all(descriptor, frame)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    return event


def initialize_database(path: Path, schema_name: str) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA trusted_schema = OFF")
    connection.execute("PRAGMA synchronous = FULL")
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.executescript((SQL_DIR / f"{schema_name}.sql").read_text(encoding="utf-8"))
    return connection


def update_projection_meta(
    connection: sqlite3.Connection,
    projection_name: str,
    events: Sequence[dict[str, Any]],
) -> None:
    connection.execute(
        """
        INSERT INTO _projection_meta(
            projection_name, last_seq, last_digest, projector_version, schema_version
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            projection_name,
            len(events),
            events[-1]["digest"] if events else None,
            PROJECTOR_VERSION,
            SCHEMA_VERSION,
        ),
    )


def check_database(connection: sqlite3.Connection, name: str) -> None:
    integrity = connection.execute("PRAGMA integrity_check").fetchone()
    if integrity != ("ok",):
        raise LogError(f"{name} integrity_check failed: {integrity!r}")
    foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_keys:
        raise LogError(f"{name} foreign_key_check failed: {foreign_keys!r}")


def semantic_digest(connection: sqlite3.Connection, queries: Sequence[str]) -> str:
    logical_rows: list[Any] = []
    for query in queries:
        logical_rows.append(connection.execute(query).fetchall())
    return hashlib.sha256(canonical_json_bytes(logical_rows)).hexdigest()


def project_events(log_path: Path, output_dir: Path) -> dict[str, Any]:
    events = read_events(log_path)
    if output_dir.exists():
        raise LogError(f"output directory already exists: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent))
    connections: dict[str, sqlite3.Connection] = {}
    try:
        for name in ("catalog", "assurance", "workflow"):
            connections[name] = initialize_database(temp_dir / f"{name}.sqlite", name)

        for event in events:
            event_json = canonical_json(event)
            payload_json = canonical_json(event["payload"])
            connections["catalog"].execute(
                """
                INSERT INTO events(
                    sequence, event_id, observed_at, kind, status, source_adapter,
                    subject_type, subject_ref, previous_digest, digest, event_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["sequence"],
                    event["event_id"],
                    event["observed_at"],
                    event["kind"],
                    event["status"],
                    event["source"]["adapter"],
                    event["subject"]["type"],
                    event["subject"]["ref"],
                    event["previous_digest"],
                    event["digest"],
                    event_json,
                ),
            )
            if event["kind"] in {"observation", "finding"}:
                connections["assurance"].execute(
                    """
                    INSERT INTO evidence(
                        event_id, sequence, observed_at, evidence_kind, status,
                        source_adapter, subject_type, subject_ref, payload_json, event_digest
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event["event_id"],
                        event["sequence"],
                        event["observed_at"],
                        event["kind"],
                        event["status"],
                        event["source"]["adapter"],
                        event["subject"]["type"],
                        event["subject"]["ref"],
                        payload_json,
                        event["digest"],
                    ),
                )
            else:
                connections["workflow"].execute(
                    """
                    INSERT INTO workflow_events(
                        event_id, sequence, observed_at, workflow_kind, status,
                        subject_type, subject_ref, payload_json, event_digest
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event["event_id"],
                        event["sequence"],
                        event["observed_at"],
                        event["kind"],
                        event["status"],
                        event["subject"]["type"],
                        event["subject"]["ref"],
                        payload_json,
                        event["digest"],
                    ),
                )

        for name, connection in connections.items():
            update_projection_meta(connection, name, events)
            connection.commit()
            check_database(connection, name)

        semantic_digests = {
            "catalog.sqlite": semantic_digest(
                connections["catalog"],
                (
                    "SELECT projection_name,last_seq,last_digest,projector_version,schema_version "
                    "FROM _projection_meta ORDER BY projection_name",
                    "SELECT sequence,event_id,observed_at,kind,status,source_adapter,subject_type,"
                    "subject_ref,previous_digest,digest,event_json FROM events ORDER BY sequence",
                ),
            ),
            "assurance.sqlite": semantic_digest(
                connections["assurance"],
                (
                    "SELECT projection_name,last_seq,last_digest,projector_version,schema_version "
                    "FROM _projection_meta ORDER BY projection_name",
                    "SELECT event_id,sequence,observed_at,evidence_kind,status,source_adapter,"
                    "subject_type,subject_ref,payload_json,event_digest "
                    "FROM evidence ORDER BY sequence",
                ),
            ),
            "workflow.sqlite": semantic_digest(
                connections["workflow"],
                (
                    "SELECT projection_name,last_seq,last_digest,projector_version,schema_version "
                    "FROM _projection_meta ORDER BY projection_name",
                    "SELECT event_id,sequence,observed_at,workflow_kind,status,subject_type,"
                    "subject_ref,payload_json,event_digest FROM workflow_events ORDER BY sequence",
                ),
            ),
        }
        for connection in connections.values():
            connection.close()
        connections.clear()

        database_files = ("catalog.sqlite", "assurance.sqlite", "workflow.sqlite")
        watermark = {
            name.removesuffix(".sqlite"): len(events) for name in database_files
        }
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "projector_version": PROJECTOR_VERSION,
            "source_log_sha256": file_digest(log_path),
            "event_count": len(events),
            "last_event_digest": events[-1]["digest"] if events else None,
            "vector_watermark": watermark,
            "files": {
                name: {
                    "packaging_sha256": file_digest(temp_dir / name),
                    "semantic_sha256": semantic_digests[name],
                }
                for name in database_files
            },
        }
        (temp_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.rename(temp_dir, output_dir)
        return manifest
    except Exception:
        for connection in connections.values():
            connection.close()
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        raise


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LogError(f"cannot load JSON object from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise LogError(f"JSON value in {path} is not an object")
    return value


def command_append(args: argparse.Namespace) -> int:
    event = append_event(args.log, load_json_object(args.event))
    print(json.dumps(event, indent=2, sort_keys=True))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    events = read_events(args.log)
    result = {
        "valid": True,
        "event_count": len(events),
        "last_event_digest": events[-1]["digest"] if events else None,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def command_project(args: argparse.Namespace) -> int:
    manifest = project_events(args.log, args.output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    append_parser = subparsers.add_parser("append", help="append one validated draft event")
    append_parser.add_argument("--log", required=True, type=Path)
    append_parser.add_argument("--event", required=True, type=Path)
    append_parser.set_defaults(handler=command_append)

    verify_parser = subparsers.add_parser("verify", help="verify framing, sequence, and digest chain")
    verify_parser.add_argument("--log", required=True, type=Path)
    verify_parser.set_defaults(handler=command_verify)

    project_parser = subparsers.add_parser(
        "project", help="create a new generation of named SQLite read models"
    )
    project_parser.add_argument("--log", required=True, type=Path)
    project_parser.add_argument("--output-dir", required=True, type=Path)
    project_parser.set_defaults(handler=command_project)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.handler(args)
    except LogError as exc:
        print(f"log.0 error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
