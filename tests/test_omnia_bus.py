import copy
import dataclasses
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from omnia_bus_codec import (  # noqa: E402
    ABI_MINOR,
    CodecError,
    compile_bundle,
    decode_bundle,
    encode_bundle,
    load_bundle,
    mutate_for_negative_fixture,
)


class TestOmniaBus(unittest.TestCase):
    source = ROOT / "bus/fixtures/dns-macos.bundle.json"
    artifact_dir = ROOT / "artifacts/omnia-bus-v1"

    def test_rebuild_is_byte_identical_and_matches_golden_hash(self):
        first = compile_bundle(ROOT, self.source)
        second = compile_bundle(ROOT, self.source)
        committed = (self.artifact_dir / "omnia-dns-macos.omnb").read_bytes()
        self.assertEqual(first, second)
        self.assertEqual(first, committed)
        manifest = json.loads((self.artifact_dir / "manifest.json").read_text())
        golden = next(item for item in manifest["entries"] if item["path"] == "omnia-dns-macos.omnb")
        self.assertEqual(golden["sha256"], hashlib.sha256(first).hexdigest())
        self.assertEqual(golden["bytes"], len(first))

    def test_reference_decode_preserves_source_semantics(self):
        decoded = decode_bundle((self.artifact_dir / "omnia-dns-macos.omnb").read_bytes())
        self.assertEqual("1.0", decoded["abi"])
        self.assertEqual(4, decoded["record_count"])
        invariant = next(item for item in decoded["records"] if item["kind"] == "invariant")
        self.assertEqual("high", invariant["metadata"]["severity"])
        self.assertEqual(True, invariant["metadata"]["expected_state"]["resolvers_explicit"])
        self.assertEqual("applicable", invariant["states"]["applicability"])

    def test_compiler_rejects_missing_provenance(self):
        manifest = json.loads(self.source.read_text())
        manifest["documents"][0]["provenance_ids"] = []
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(CodecError, "evidence and provenance are mandatory"):
                load_bundle(ROOT, path)

    def test_compiler_rejects_source_digest_mismatch(self):
        manifest = json.loads(self.source.read_text())
        manifest["documents"][0]["evidence_ids"] = ["sha256:" + "0" * 64]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(CodecError, "lacks exact source digest"):
                load_bundle(ROOT, path)

    def test_negative_fixtures_are_reproducible_and_rejected(self):
        bundle = load_bundle(ROOT, self.source)
        for case in ("contradictory", "provenance-missing", "unsupported-version", "malformed"):
            with self.subTest(case=case):
                generated = mutate_for_negative_fixture(bundle, case)
                self.assertEqual(generated, (self.artifact_dir / f"{case}.omnb").read_bytes())
                with self.assertRaises(CodecError):
                    decode_bundle(generated)

    def test_boundary_fixture_uses_exact_uint64_values(self):
        bundle = load_bundle(ROOT, self.source)
        generated = mutate_for_negative_fixture(bundle, "boundary")
        self.assertEqual(generated, (self.artifact_dir / "boundary.omnb").read_bytes())
        decoded = decode_bundle(generated)
        self.assertEqual(0xFFFFFFFFFFFFFFFF, decoded["created_at"])
        self.assertEqual(0xFFFFFFFFFFFFFFFF, decoded["fresh_until"])

    def test_strict_no_upgrade(self):
        manifest = json.loads(self.source.read_text())
        manifest["abi_minor"] = ABI_MINOR + 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "future.json"
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(CodecError, "upgrade/downgrade is forbidden"):
                load_bundle(ROOT, path)

    def test_lossy_float_quantization_is_rejected(self):
        bundle = load_bundle(ROOT, self.source)
        metadata = copy.deepcopy(bundle.records[0].metadata)
        metadata["confidence"] = 0.5
        record = dataclasses.replace(bundle.records[0], metadata=metadata)
        with self.assertRaisesRegex(CodecError, "floats are rejected"):
            encode_bundle(dataclasses.replace(bundle, records=(record,) + bundle.records[1:]))


if __name__ == "__main__":
    unittest.main()
