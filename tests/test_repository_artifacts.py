import json
import subprocess
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path):
    result = subprocess.run(
        [
            "ruby",
            "-e",
            'require "yaml"; require "json"; puts JSON.generate(YAML.safe_load(File.read(ARGV[0]), aliases: false))',
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


class TestRepositoryArtifacts(unittest.TestCase):
    def test_adapter_manifests_exist_match_schema_and_declare_ontology(self):
        adapter_schema = json.loads((ROOT / "schemas" / "adapter.schema.json").read_text(encoding="utf-8"))
        adapter_validator = Draft202012Validator(adapter_schema)
        adapter_dirs = sorted(p.name for p in (ROOT / "adapters").iterdir() if p.is_dir())
        manifest_files = sorted((ROOT / "adapters").rglob("adapter.json"))
        self.assertEqual(
            adapter_dirs,
            sorted({path.parent.name for path in manifest_files}),
            "Every adapter directory must declare adapter.json manifest; ambiguous taxonomy without manifest is a failure.",
        )
        supported_adapters = set()
        for manifest in manifest_files:
            with self.subTest(manifest=manifest.relative_to(ROOT)):
                doc = json.loads(manifest.read_text(encoding="utf-8"))
                errors = list(adapter_validator.iter_errors(doc))
                self.assertEqual([], errors)
                self.assertTrue(
                    doc["id"].startswith(f"adapter-{manifest.parent.name}"),
                    "Adapter manifest id must match its directory prefix to avoid ambiguous taxonomy.",
                )
                ontology = doc["ontology"]
                self.assertIn("type", ontology)
                self.assertIn("platform_vendor", ontology)
                self.assertIn("platform_name", ontology)
                self.assertIn("vendor_name", ontology)
                declared_ids = {cap["id"] for cap in doc["declared_capabilities"]}
                validated = doc.get("validated_capability_ids", [])
                for cap in doc["declared_capabilities"]:
                    for evidence_ref in cap["evidence"]["references"]:
                        self.assertTrue(
                            (ROOT / evidence_ref).exists(),
                            f"Adapter capability {cap['id']} evidence reference missing: {evidence_ref}",
                        )
                    for source in cap["sources"]:
                        self.assertTrue((ROOT / source).exists())
                if doc["support_tier"] == "supported":
                    self.assertEqual("VALIDATED", doc["status"])
                    self.assertTrue(validated, "Supported adapters require at least one validated capability mapping.")
                    self.assertTrue(all(cap_id in declared_ids for cap_id in validated))
                    for cap_id in validated:
                        cap = next(c for c in doc["declared_capabilities"] if c["id"] == cap_id)
                        self.assertEqual("supported", cap["support_tier"])
                        self.assertEqual("VALIDATED", cap["status"])
                    supported_adapters.add(manifest.parent.name)
                else:
                    self.assertEqual(
                        [],
                        validated,
                        "Unsupported/advisory adapters must not declare validated_capability_ids.",
                    )
                if doc["status"] == "UNIMPLEMENTED":
                    self.assertNotEqual("supported", doc["support_tier"])
                    self.assertFalse(validated)

    def test_environment_files_match_schema_and_existing_adapters(self):
        schema = json.loads((ROOT / "schemas" / "environment.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)

        for env_file in sorted((ROOT / "environments").rglob("environment.json")):
            with self.subTest(env_file=env_file.relative_to(ROOT)):
                doc = json.loads(env_file.read_text(encoding="utf-8"))
                errors = list(validator.iter_errors(doc))
                self.assertEqual([], errors)
                for adapter in doc["adapters"]:
                    self.assertTrue((ROOT / "adapters" / adapter).exists())
                    manifest_path = ROOT / "adapters" / adapter / "adapter.json"
                    self.assertTrue(manifest_path.exists(), "Referenced adapters must have machine-readable manifests.")
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    self.assertEqual(
                        "supported",
                        manifest["support_tier"],
                        "Environments must only reference supported (manifest-declared) adapters.",
                    )

    def test_check_and_invariant_files_match_schema_and_cross_references(self):
        check_schema = json.loads((ROOT / "schemas" / "check.schema.json").read_text(encoding="utf-8"))
        invariant_schema = json.loads((ROOT / "schemas" / "invariant.schema.json").read_text(encoding="utf-8"))
        check_validator = Draft202012Validator(check_schema)
        invariant_validator = Draft202012Validator(invariant_schema)

        check_docs = {}
        for check_file in sorted((ROOT / "checks").rglob("chk-*.yaml")):
            with self.subTest(check_file=check_file.relative_to(ROOT)):
                doc = load_yaml(check_file)
                errors = list(check_validator.iter_errors(doc))
                self.assertEqual([], errors)
                self.assertTrue((ROOT / doc["remediation_playbook"]).exists())
                check_docs[doc["id"]] = doc

        for invariant_file in sorted((ROOT / "checks").rglob("invariant-*.yaml")):
            with self.subTest(invariant_file=invariant_file.relative_to(ROOT)):
                doc = load_yaml(invariant_file)
                errors = list(invariant_validator.iter_errors(doc))
                self.assertEqual([], errors)
                self.assertTrue((ROOT / doc["remediation"]["playbook"]).exists())
                for source in doc["sources"]:
                    self.assertTrue((ROOT / source).exists())
                for check_id in doc["check"]["ids"]:
                    self.assertIn(check_id, check_docs)

    def test_openbsd_sealed_brick_artifacts_exist(self):
        self.assertTrue((ROOT / "adapters" / "openbsd" / "README.md").exists())
        self.assertTrue((ROOT / "playbooks" / "openbsd-sealed-brick" / "README.md").exists())
        self.assertTrue((ROOT / "checks" / "openbsd" / "invariant-openbsd-sealed-brick.yaml").exists())
        self.assertTrue((ROOT / "checks" / "openbsd" / "chk-openbsd-v0-collection-boundary.yaml").exists())
        self.assertTrue((ROOT / "environments" / "openbsd-sealed-brick" / "environment.json").exists())


if __name__ == "__main__":
    unittest.main()
