import platform
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "checks" / "openbsd" / "inspect_openbsd_v0.sh"


class TestOpenBsdContract(unittest.TestCase):
    def test_contract_mode_is_safe_and_descriptive(self):
        result = subprocess.run(
            ["/bin/bash", str(SCRIPT), "--contract"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("contract_version=v0", result.stdout)
        self.assertIn("read_only=true", result.stdout)
        self.assertIn("policy_gate=deterministic", result.stdout)
        self.assertIn("unknown_is_not_pass=true", result.stdout)
        self.assertIn("allowlisted_commands=uname,ifconfig,route,pfctl,rcctl,sysctl,cat", result.stdout)

    def test_collect_mode_is_unsupported_off_openbsd(self):
        if platform.system() == "OpenBSD":
            self.skipTest("This contract test only asserts the non-OpenBSD behavior in CI and local dev shells.")

        result = subprocess.run(
            ["/bin/bash", str(SCRIPT), "--collect"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("Unsupported platform:", result.stderr)

    def test_script_does_not_contain_mutating_commands(self):
        script_text = SCRIPT.read_text(encoding="utf-8")
        for forbidden in (
            "pfctl -f",
            "pfctl -e",
            "pfctl -d",
            "route add",
            "route delete",
            "rcctl set",
            "sysctl -w",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, script_text)


if __name__ == "__main__":
    unittest.main()
