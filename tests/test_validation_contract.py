import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATE = ROOT / "scripts" / "validate.sh"


class TestValidationContract(unittest.TestCase):
    def _run(self, root: Path, *args: str):
        return subprocess.run(
            ["/bin/bash", str(root / "scripts" / "validate.sh"), *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_current_structure_passes_with_stock_macos_bash(self):
        result = self._run(ROOT, "--structure-only")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Required repository structure passed", result.stdout)

    def test_missing_current_required_path_fails_clearly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "omnia-playbook"
            shutil.copytree(ROOT, copied_root, ignore=shutil.ignore_patterns(".git"))
            (copied_root / "foundation" / "dns.md").unlink()

            result = self._run(copied_root, "--structure-only")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("Missing required path: foundation/dns.md", result.stderr)

    def test_missing_openbsd_playbook_path_fails_clearly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "omnia-playbook"
            shutil.copytree(ROOT, copied_root, ignore=shutil.ignore_patterns(".git"))
            shutil.rmtree(copied_root / "playbooks" / "openbsd-sealed-brick")

            result = self._run(copied_root, "--structure-only")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("Missing required path: playbooks/openbsd-sealed-brick", result.stderr)

    def test_future_check_domains_are_not_required(self):
        script = VALIDATE.read_text(encoding="utf-8")
        for future_domain in (
            "checks/routing",
            "checks/connectivity",
            "checks/certificates",
            "checks/secrets",
            "checks/system",
        ):
            self.assertNotIn(future_domain, script)

    def test_bash_4_mapfile_is_not_used(self):
        script = VALIDATE.read_text(encoding="utf-8")
        self.assertNotIn("mapfile", script)

    def test_unknown_option_fails_with_usage(self):
        result = self._run(ROOT, "--not-a-real-option")
        self.assertEqual(2, result.returncode)
        self.assertIn("Unknown option: --not-a-real-option", result.stderr)
        self.assertIn("Usage:", result.stderr)


    def test_missing_adapter_manifest_fails_ambiguous_taxonomy(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "omnia-playbook"
            shutil.copytree(ROOT, copied_root, ignore=shutil.ignore_patterns(".git"))
            (copied_root / "adapters" / "apple" / "adapter.json").unlink()

            structure_result = self._run(copied_root, "--structure-only")
            artifacts_result = self._run(copied_root, "--artifacts-only")

        self.assertNotEqual(0, structure_result.returncode)
        self.assertNotEqual(0, artifacts_result.returncode)
        combined = f"{structure_result.stderr}\n{artifacts_result.stdout}\n{artifacts_result.stderr}"
        self.assertIn("adapters/apple/adapter.json", combined)

    def test_supported_adapter_without_validated_capability_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "omnia-playbook"
            shutil.copytree(ROOT, copied_root, ignore=shutil.ignore_patterns(".git"))
            manifest_path = copied_root / "adapters" / "macos" / "adapter.json"
            import json as _json
            manifest = _json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["validated_capability_ids"] = []
            manifest_path.write_text(_json.dumps(manifest, indent=2), encoding="utf-8")

            result = self._run(copied_root, "--artifacts-only")

        self.assertNotEqual(0, result.returncode)
        combined = f"{result.stdout}\n{result.stderr}"
        self.assertIn("validated_capability_ids", combined)

    def test_unimplemented_adapter_cannot_be_supported_tier(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            copied_root = Path(temp_dir) / "omnia-playbook"
            shutil.copytree(ROOT, copied_root, ignore=shutil.ignore_patterns(".git"))
            manifest_path = copied_root / "adapters" / "apple" / "adapter.json"
            import json as _json
            manifest = _json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["support_tier"] = "supported"
            manifest_path.write_text(_json.dumps(manifest, indent=2), encoding="utf-8")

            result = self._run(copied_root, "--artifacts-only")

        self.assertNotEqual(0, result.returncode)
        combined = f"{result.stdout}\n{result.stderr}"
        self.assertIn(
            "requires status=VALIDATED",
            combined,
            "support_tier=supported with UNIMPLEMENTED status must fail taxonomy consistency checks.",
        )


if __name__ == "__main__":
    unittest.main()
