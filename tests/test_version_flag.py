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


class VersionSourceTest(unittest.TestCase):
    def test_shared_version_is_semver(self):
        self.assertRegex(cyber_version.__version__, r"^\d+\.\d+\.\d+$")

    def test_banners_interpolate_the_shared_version(self):
        for script in ("scifi_hud.py", "cyber_tools.py"):
            with self.subTest(script=script):
                self.assertIn("v{__version__}", read_source(script))

    def test_no_hardcoded_short_version_in_banners(self):
        pattern = re.compile(r"v4\.5(?![.\d])")
        for script in CLI_SCRIPTS:
            with self.subTest(script=script):
                self.assertIsNone(pattern.search(read_source(script)))

    def test_no_hardcoded_version_in_user_agents(self):
        pattern = re.compile(r"CyberOS[^\"]*/4\.5\"")
        for script in ("cyber_tools.py", "cyber_search.py"):
            with self.subTest(script=script):
                self.assertIsNone(pattern.search(read_source(script)))

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
