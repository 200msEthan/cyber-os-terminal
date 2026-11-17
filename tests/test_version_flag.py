"""Tests for the shared version constant and the `--version` CLI flag."""

import re
import subprocess
import sys
import unittest
from pathlib import Path

import cyber_version

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPTS = ("scifi_hud.py", "cyber_tools.py", "cyber_search.py", "cyber_vision.py")


def read_source(name: str) -> str:
    return (REPO_ROOT / name).read_text(encoding="utf-8")


BANNER_BRANDS = ("CYBER-OS //", "CYBER-DECK //", "NEURAL COCKPIT")
SHORT_VERSION = re.compile(r"(?<![A-Za-z])v\d+\.\d+(?![.\d])")
USER_AGENT_VERSION = re.compile(r"\bCyberOS[\w-]*/\d+(?:\.\d+)+(?![\w.])")


def hardcoded_banner_version(source: str):
    for line in source.splitlines():
        if any(brand in line for brand in BANNER_BRANDS):
            match = SHORT_VERSION.search(line)
            if match:
                return match
    return None


class VersionSourceTest(unittest.TestCase):
    def test_shared_version_is_semver(self):
        self.assertRegex(cyber_version.__version__, r"^\d+\.\d+\.\d+$")

    def test_banners_interpolate_the_shared_version(self):
        for script in ("scifi_hud.py", "cyber_tools.py"):
            with self.subTest(script=script):
                self.assertIn("v{__version__}", read_source(script))
        with self.subTest(script="cyber_vision.py"):
            self.assertIn("__CYBER_VERSION__", read_source("cyber_vision.py"))

    def test_no_hardcoded_short_version_in_banners(self):
        for script in CLI_SCRIPTS:
            with self.subTest(script=script):
                self.assertIsNone(hardcoded_banner_version(read_source(script)))

    def test_no_hardcoded_version_in_user_agents(self):
        for script in CLI_SCRIPTS:
            with self.subTest(script=script):
                self.assertIsNone(USER_AGENT_VERSION.search(read_source(script)))

    def test_banner_check_ignores_unrelated_versions(self):
        source = 'protocol = "TLSv1.3"\n# Another tool uses v9.9\n'
        self.assertIsNone(hardcoded_banner_version(source))
        self.assertIsNone(hardcoded_banner_version('"CYBER-OS // TLSv1.3"'))

    def test_banner_check_rejects_hardcoded_brand_versions(self):
        for brand in BANNER_BRANDS:
            with self.subTest(brand=brand):
                self.assertIsNotNone(hardcoded_banner_version(f'"{brand} v9.9"'))
                self.assertIsNone(hardcoded_banner_version(f'f"{brand} v{{__version__}}"'))

    def test_user_agent_check_rejects_any_numeric_version(self):
        for value in ("CyberOS/9.9", "CyberOS-Recon/5.0", "CyberOS-SecAudit/12.34.56"):
            with self.subTest(value=value):
                self.assertIsNotNone(USER_AGENT_VERSION.search(value))
        self.assertIsNone(USER_AGENT_VERSION.search("CyberOS/{__version__}"))

    @unittest.skipIf(tomllib is None, "tomllib requires Python 3.11+")
    def test_pyproject_reads_version_dynamically(self):
        with open(REPO_ROOT / "pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
        self.assertIn("version", pyproject["project"].get("dynamic", []))
        self.assertNotIn("version", pyproject["project"])
        self.assertEqual(
            pyproject["tool"]["setuptools"]["dynamic"]["version"]["attr"],
            "cyber_version.__version__",
        )


class VersionFlagTest(unittest.TestCase):
    def test_all_cli_entry_points_support_version_flag(self):
        for script in CLI_SCRIPTS:
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, str(REPO_ROOT / script), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=REPO_ROOT,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(cyber_version.__version__, result.stdout)


if __name__ == "__main__":
    unittest.main()
