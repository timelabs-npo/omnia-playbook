import importlib.util
import json
import sqlite3
import tempfile
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("omnia_log0", ROOT / "scripts" / "log0.py")
assert SPEC is not None and SPEC.loader is not None
LOG0 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LOG0)


def draft(event_id=None, payload=None):
    value = {
        "observed_at": "2026-07-24T00:00:00Z",
        "kind": "observation",
        "status": "UNKNOWN",
        "source": {"adapter": "test", "collector": "fixture", "version": "1"},
        "subject": {"type": "system", "ref": "fixture:one"},
        "payload": payload if payload is not None else {"count": 1},
        "redaction": {"policy": "omnia-public-v1", "applied": True},
    }
    if event_id is not None:
        value["event_id"] = event_id
    return value


class TestLogZero(unittest.TestCase):
    def test_golden_exact_byte_frame_digest(self):
        event_without_digest = {
            "schema_version": 1,
            "event_id": "123e4567-e89b-42d3-a456-426614174000",
            "sequence": 1,
            **draft(),
            "previous_digest": None,
        }
        frame, digest = LOG0.encode_frame(event_without_digest)
        self.assertEqual(
            "17724eed6b861779b84f49aa129f41d5586b3c72c866dbf497efd4a095740d9a",
            digest,
        )
        self.assertTrue(frame.startswith(b"373\t{"))
        self.assertTrue(frame.endswith(digest.encode("ascii") + b"\n"))

    def test_append_verify_and_lost_ack_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "log.0"
            event_id = str(uuid.uuid4())
            requested = draft(event_id)

            first = LOG0.append_event(log_path, requested)
            size_after_first = log_path.stat().st_size
            retried = LOG0.append_event(log_path, requested)

            self.assertEqual(first, retried)
            self.assertEqual(size_after_first, log_path.stat().st_size)
            self.assertEqual([first], LOG0.read_events(log_path))

    def test_conflicting_duplicate_event_id_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "log.0"
            event_id = str(uuid.uuid4())
            LOG0.append_event(log_path, draft(event_id))

            with self.assertRaisesRegex(LOG0.LogError, "different content"):
                LOG0.append_event(log_path, draft(event_id, {"count": 2}))

    def test_uppercase_uuid_is_not_canonical(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "log.0"
            with self.assertRaisesRegex(LOG0.LogError, "canonical lowercase UUIDv4"):
                LOG0.append_event(log_path, draft(str(uuid.uuid4()).upper()))
            self.assertFalse(log_path.exists())

    def test_tamper_and_torn_tail_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            valid_log = directory_path / "valid.log.0"
            LOG0.append_event(valid_log, draft())
            original = valid_log.read_bytes()

            tampered = directory_path / "tampered.log.0"
            tampered.write_bytes(original.replace(b'"count":1', b'"count":2', 1))
            with self.assertRaisesRegex(LOG0.LogError, "digest mismatch"):
                LOG0.read_events(tampered)

            torn = directory_path / "torn.log.0"
            torn.write_bytes(original[:-10])
            with self.assertRaises(LOG0.TornTailError):
                LOG0.read_events(torn)
            with self.assertRaises(LOG0.TornTailError):
                LOG0.append_event(torn, draft())

    def test_public_redaction_policy_rejects_sensitive_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "log.0"
            with self.assertRaisesRegex(LOG0.LogError, "forbidden keys"):
                LOG0.append_event(log_path, draft(payload={"token": "do-not-store"}))
            self.assertFalse(log_path.exists())

    def test_projection_generations_have_equal_semantic_digests(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            log_path = directory_path / "log.0"
            LOG0.append_event(log_path, draft(str(uuid.uuid4())))
            finding = draft(str(uuid.uuid4()), {"rule": "fixture-rule"})
            finding["kind"] = "finding"
            finding["status"] = "PASS"
            LOG0.append_event(log_path, finding)
            plan = draft(str(uuid.uuid4()), {"plan_digest": "sha256:fixture"})
            plan["kind"] = "plan"
            LOG0.append_event(log_path, plan)

            first = LOG0.project_events(log_path, directory_path / "generation-a")
            second = LOG0.project_events(log_path, directory_path / "generation-b")

            first_semantic = {
                name: metadata["semantic_sha256"]
                for name, metadata in first["files"].items()
            }
            second_semantic = {
                name: metadata["semantic_sha256"]
                for name, metadata in second["files"].items()
            }
            self.assertEqual(first_semantic, second_semantic)
            self.assertEqual(
                {"catalog": 3, "assurance": 3, "workflow": 3},
                first["vector_watermark"],
            )

            for name in ("catalog", "assurance", "workflow"):
                connection = sqlite3.connect(
                    directory_path / "generation-a" / f"{name}.sqlite"
                )
                try:
                    meta = connection.execute(
                        "SELECT last_seq,last_digest,projector_version,schema_version "
                        "FROM _projection_meta"
                    ).fetchone()
                finally:
                    connection.close()
                self.assertEqual((3, first["last_event_digest"], 1, 1), meta)

            manifest = json.loads(
                (directory_path / "generation-a" / "manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(first, manifest)


if __name__ == "__main__":
    unittest.main()
