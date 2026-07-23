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


if __name__ == "__main__":
    unittest.main()
