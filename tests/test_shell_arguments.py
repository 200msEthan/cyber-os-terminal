"""Run the actual profiles with Python replaced by an argument recorder."""

import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("cyber-kill", ["8130"], ["--kill-port", "8130"]),
    ("cyber-kill", ["8131", "--force"], ["--kill-port", "8131", "--force"]),
    ("cyber-ports", [], ["--ports", "127.0.0.1", "--range", "common"]),
    ("cyber-ports", ["localhost"], ["--ports", "localhost", "--range", "common"]),
    ("cyber-ports", ["localhost", "22,80", "--help"],
     ["--ports", "localhost", "--range", "22,80", "--help"]),
    ("cyber-find", ["some file", "dir with spaces", "--help"],
     ["--files", "some file", "--dir", "dir with spaces", "--help"]),
]
for command, option, value in [
    ("recon", "--recon", "example.com"),
    ("ssl", "--ssl", "github.com"),
    ("headers", "--headers", "https://example.com/a?x=1&y=2"),
    ("hash", "--hash", "a quoted ' value"),
    ("decode", "--decode", "a b"),
    ("keygen", "--keygen", "32"),
    ("fim", "--fim", "dir with spaces"),
    ("secrets", "--secrets", "dir with spaces"),
    ("nmap", "--nmap", "localhost"),
]:
    CASES.append(("cyber-" + command, [value, "--help"], [option, value, "--help"]))


class ShellArgumentsTest(unittest.TestCase):
    def check_posix(self, shell):
        if os.name == "nt":
            self.skipTest("Run POSIX profiles on a POSIX host")
        executable = shutil.which(shell)
        if not executable:
            self.skipTest(shell + " is not installed")
        with tempfile.TemporaryDirectory() as tmp:
            # Normalize checkout line endings, without modifying the profile's code.
            profile = Path(tmp) / "cyberpunk_shell.sh"
            profile.write_text((ROOT / profile.name).read_text(encoding="utf-8"),
                               encoding="utf-8")
            script = 'export CYBER_HUD_SHOWN=1\nsource "$1"\n'
            script += 'python3() { printf "%s\\0" "$@"; printf "\\n"; }\n'
            script += "\n".join(shlex.join([command, *args]) for command, args, _ in CASES)
            result = subprocess.run([executable, "-i", "-c", script, "shell-test", str(profile)],
                                    capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), len(CASES), result.stdout)
        for line, (command, args, expected) in zip(lines, CASES):
            with self.subTest(shell=shell, command=command, args=args):
                actual = line.rstrip(b"\0").decode().split("\0")
                self.assertEqual(actual[1:], expected)

    def test_bash(self):
        self.check_posix("bash")

    def test_zsh(self):
        self.check_posix("zsh")

    def test_powershell(self):
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            self.skipTest("PowerShell is not installed")
        script = """
$ErrorActionPreference = 'Stop'
$env:CYBER_HUD_SHOWN = '1'
. $env:CYBER_TEST_PROFILE
function capture-python { ConvertTo-Json -Compress -InputObject @($args) }
$PythonExe = 'capture-python'
foreach ($case in (ConvertFrom-Json $env:CYBER_TEST_CASES)) {
    $callArgs = @($case[1])
    & $case[0] @callArgs
}
"""
        env = dict(os.environ, CYBER_TEST_PROFILE=str(ROOT / "cyberpunk_profile.ps1"),
                   CYBER_TEST_CASES=json.dumps(CASES))
        result = subprocess.run([shell, "-NoProfile", "-NonInteractive", "-Command", script],
                                capture_output=True, text=True, encoding="utf-8", env=env, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), len(CASES), result.stdout)
        for line, (command, args, expected) in zip(lines, CASES):
            with self.subTest(command=command, args=args):
                if command == "cyber-kill" and "--force" not in args:
                    expected = [*expected, "--force"]
                self.assertEqual([str(value) for value in json.loads(line)[1:]], expected)


if __name__ == "__main__":
    unittest.main()
