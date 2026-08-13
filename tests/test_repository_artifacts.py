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
                validated = doc.get("validated_capability_ids", []) or []
                ACCEPTABLE_VALIDATED_TIERS = {"implemented", "validated_mock", "validated_live_target", "VALIDATED", "MAPPED"}
                for cap in doc["declared_capabilities"]:
                    sources = (
                        cap.get("sources")
                        or (cap.get("evidence") or {}).get("references")
                        or []
                    )
                    for source in sources:
                        self.assertTrue(
                            (ROOT / source).exists(),
                            f"Adapter capability {cap['id']} source missing: {source}",
                        )
                if doc["support_tier"] == "supported":
                    self.assertTrue(validated, "Supported adapters require at least one validated capability mapping.")
                    self.assertTrue(all(cap_id in declared_ids for cap_id in validated))
                    for cap_id in validated:
                        cap = next(c for c in doc["declared_capabilities"] if c["id"] == cap_id)
                        self.assertIn(
                            cap.get("evidence_tier", cap.get("status")),
                            ACCEPTABLE_VALIDATED_TIERS,
                            f"Validated capability {cap_id} must have evidence_tier>=implemented (got {cap.get('evidence_tier', cap.get('status'))}).",
                        )
                    supported_adapters.add(manifest.parent.name)
                if doc["status"] == "UNIMPLEMENTED":
                    self.assertNotEqual("supported", doc["support_tier"])

    def test_environment_files_match_schema_and_existing_adapters(self):
        schema = json.loads((ROOT / "schemas" / "environment.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)

        # Build id → directory map from adapter manifests (id format: adapter-<dir>-<suffix>)
        adapter_id_to_dir = {}
        for manifest in (ROOT / "adapters").rglob("adapter.json"):
            adoc = json.loads(manifest.read_text(encoding="utf-8"))
            adapter_id_to_dir[adoc["id"]] = manifest.parent.name

        for env_file in sorted((ROOT / "environments").rglob("environment.json")):
            with self.subTest(env_file=env_file.relative_to(ROOT)):
                doc = json.loads(env_file.read_text(encoding="utf-8"))
                errors = list(validator.iter_errors(doc))
                self.assertEqual([], errors)
                adapter_dirs = set()
                for legacy in doc.get("adapters_legacy_list", []):
                    adapter_dirs.add(legacy)
                for tgt in doc.get("estate_targets", []):
                    hint = tgt.get("adapter_id_hint")
                    if not hint:
                        continue
                    if hint in adapter_id_to_dir:
                        adapter_dirs.add(adapter_id_to_dir[hint])
                    elif hint.startswith("adapter-"):
                        # best-effort strip common suffix pattern adapter-<dir>-<vendor>
                        rest = hint[len("adapter-") :]
                        parts = rest.split("-")
                        for end in range(len(parts), 0, -1):
                            cand = "-".join(parts[:end])
                            if (ROOT / "adapters" / cand).is_dir():
                                adapter_dirs.add(cand)
                                break
                for adapter in adapter_dirs:
                    self.assertTrue(
                        (ROOT / "adapters" / adapter).is_dir(),
                        f"Environment references missing adapter directory: {adapter}",
                    )
                    manifest_path = ROOT / "adapters" / adapter / "adapter.json"
                    self.assertTrue(
                        manifest_path.exists(),
                        f"Referenced adapter {adapter} must have machine-readable manifest adapter.json.",
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
                # v1: remediation_ref string; v0 legacy: remediation_playbook
                rem_ref = doc.get("remediation_ref") or doc.get("remediation_playbook")
                if rem_ref:
                    self.assertTrue((ROOT / rem_ref).exists())
                check_docs[doc["id"]] = doc

        for invariant_file in sorted((ROOT / "checks").rglob("invariant-*.yaml")):
            with self.subTest(invariant_file=invariant_file.relative_to(ROOT)):
                doc = load_yaml(invariant_file)
                errors = list(invariant_validator.iter_errors(doc))
                self.assertEqual([], errors)
                # v1: remediation_refs map with layers; v0 legacy: remediation.playbook
                rem = doc.get("remediation_refs") or {}
                rem_path = (
                    rem.get("operational")
                    or rem.get("explanatory")
                    or (doc.get("remediation") or {}).get("playbook")
                )
                if rem_path:
                    if isinstance(rem_path, list):
                        for rp in rem_path:
                            self.assertTrue((ROOT / rp).exists(), f"Missing remediation ref {rp}")
                    else:
                        self.assertTrue((ROOT / rem_path).exists(), f"Missing remediation ref {rem_path}")
                src_refs = doc.get("source_refs") or doc.get("sources") or {}
                if isinstance(src_refs, dict):
                    for layer_src in src_refs.values():
                        if isinstance(layer_src, list):
                            for s in layer_src:
                                self.assertTrue((ROOT / s).exists(), f"Missing source {s}")
                        elif isinstance(layer_src, str):
                            self.assertTrue((ROOT / layer_src).exists(), f"Missing source {layer_src}")
                elif isinstance(src_refs, list):
                    for s in src_refs:
                        self.assertTrue((ROOT / s).exists())
                check_refs = (doc.get("check_refs") or {}).get("ids") or (doc.get("check") or {}).get("ids") or []
                for check_id in check_refs:
                    self.assertIn(check_id, check_docs, f"Invariant references missing check {check_id}")

    def test_openbsd_sealed_brick_artifacts_exist(self):
        self.assertTrue((ROOT / "adapters" / "openbsd" / "README.md").exists())
        self.assertTrue((ROOT / "playbooks" / "openbsd-sealed-brick" / "README.md").exists())
        self.assertTrue((ROOT / "checks" / "openbsd" / "invariant-openbsd-sealed-brick.yaml").exists())
        self.assertTrue((ROOT / "checks" / "openbsd" / "chk-openbsd-v0-collection-boundary.yaml").exists())
        self.assertTrue((ROOT / "environments" / "openbsd-sealed-brick" / "environment.json").exists())


if __name__ == "__main__":
    unittest.main()
