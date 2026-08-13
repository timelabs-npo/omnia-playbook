import json
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "checks" / "openbsd" / "inspect_openbsd_v0.sh"


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


class TestOpenBsdContract(unittest.TestCase):
    def _write_mock_command(self, directory: Path, name: str, body: str):
        path = directory / name
        path.write_text("#!/bin/sh\nset -eu\n" + body, encoding="utf-8")
        path.chmod(0o755)

    def _run_with_openbsd_mocks(self, mode: str):
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_dir = Path(temp_dir)
            self._write_mock_command(mock_dir, "uname", 'printf "OpenBSD 7.6 GENERIC.MP#1 amd64\\n"\n')
            self._write_mock_command(
                mock_dir,
                "ifconfig",
                '/bin/cat <<\'EOF\'\n'
                'em0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> mtu 1500\n'
                '    lladdr aa:bb:cc:dd:ee:ff\n'
                '    inet 192.0.2.10 netmask 0xffffff00 broadcast 192.0.2.255\n'
                'em1: flags=8802<BROADCAST,SIMPLEX,MULTICAST> mtu 1500\n'
                '    lladdr 11:22:33:44:55:66\n'
                '    inet6 2001:db8::10 prefixlen 64\n'
                'EOF\n',
            )
            self._write_mock_command(
                mock_dir,
                "route",
                '/bin/cat <<\'EOF\'\n'
                'Routing tables\n'
                '\n'
                'Internet:\n'
                'Destination        Gateway            Flags   Refs      Use   Mtu  Prio Iface\n'
                'default            192.0.2.1          UGS        0        0     -     8 em0\n'
                '192.0.2/24         link#1             UC         1        0     -     4 em0\n'
                'EOF\n',
            )
            self._write_mock_command(
                mock_dir,
                "pfctl",
                'case "${1:-}" in\n'
                '  -s)\n'
                '    [ "${2:-}" = "info" ] || exit 1\n'
                '    /bin/cat <<\'EOF\'\n'
                'Status: Enabled for 2 days 00:00:00           Debug: Urgent\n'
                'EOF\n'
                '    ;;\n'
                '  -sr)\n'
                '    /bin/cat <<\'EOF\'\n'
                'block in all\n'
                'pass out on em0 inet from 192.0.2.10 to any keep state\n'
                'EOF\n'
                '    ;;\n'
                '  -sn)\n'
                '    /bin/cat <<\'EOF\'\n'
                'match out on em0 from 192.0.2.0/24 to any nat-to 198.51.100.20\n'
                'EOF\n'
                '    ;;\n'
                '  *) exit 1 ;;\n'
                'esac\n',
            )
            self._write_mock_command(
                mock_dir,
                "rcctl",
                '/bin/cat <<\'EOF\'\n'
                'sshd\n'
                'unbound\n'
                'EOF\n',
            )
            self._write_mock_command(
                mock_dir,
                "sysctl",
                'printf "net.inet.ip.forwarding=1\\n"\n',
            )
            self._write_mock_command(
                mock_dir,
                "cat",
                '/bin/cat <<\'EOF\'\n'
                'search corp.example\n'
                'nameserver 198.51.100.53\n'
                'nameserver 2001:db8::53\n'
                'EOF\n',
            )

            env = os.environ.copy()
            env["PATH"] = str(mock_dir) + os.pathsep + env["PATH"]
            env["OPENBSD_V0_FORCE_PLATFORM"] = "OpenBSD"

            return subprocess.run(
                ["/bin/bash", str(SCRIPT), mode],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )

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
        self.assertIn("public_output=minimized_posture_only", result.stdout)
        self.assertIn("private_inspection=explicit_only", result.stdout)

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

    def test_collect_mode_minimizes_public_output(self):
        result = self._run_with_openbsd_mocks("--collect")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("output_mode=public_minimized", result.stdout)
        self.assertIn("interface_count=2", result.stdout)
        self.assertIn("pf_rule_count=2", result.stdout)
        self.assertIn("pf_nat_rule_count=1", result.stdout)
        self.assertIn("service_enabled_count=2", result.stdout)
        self.assertIn("resolver_entry_count=2", result.stdout)
        self.assertIn("resolver_search_domain_present=true", result.stdout)
        self.assertIn("pf_enabled=true", result.stdout)
        self.assertIn("default_route_present=true", result.stdout)
        self.assertIn("kernel_forwarding_enabled=true", result.stdout)
        self.assertIn("result=PASS", result.stdout)

        for sensitive_value in (
            "em0",
            "em1",
            "192.0.2.10",
            "192.0.2.1",
            "192.0.2.255",
            "198.51.100.20",
            "198.51.100.53",
            "2001:db8::10",
            "2001:db8::53",
            "aa:bb:cc:dd:ee:ff",
            "11:22:33:44:55:66",
            "corp.example",
            "block in all",
            "pass out on",
            "match out on",
        ):
            with self.subTest(sensitive_value=sensitive_value):
                self.assertNotIn(sensitive_value, result.stdout)

    def test_inspect_private_mode_warns_before_raw_output(self):
        result = self._run_with_openbsd_mocks("--inspect-private")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("LOCAL SENSITIVE OUTPUT", result.stdout)
        self.assertIn("DO NOT UPLOAD OR APPEND TO LOG.0", result.stdout)
        self.assertIn("192.0.2.10", result.stdout)
        self.assertIn("aa:bb:cc:dd:ee:ff", result.stdout)
        self.assertIn("corp.example", result.stdout)
        self.assertIn("match out on em0", result.stdout)

    def test_machine_readable_check_does_not_use_private_mode(self):
        doc = load_yaml(ROOT / "checks" / "openbsd" / "chk-openbsd-v0-collection-boundary.yaml")
        command = doc.get("command", "")
        self.assertIn("--collect", command)
        self.assertNotIn("--inspect-private", command)
        # The forbidden_actions prose may describe --inspect-private as a boundary,
        # but the machine-readable operational command must never reference it.

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
