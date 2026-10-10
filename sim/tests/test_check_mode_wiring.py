#!/usr/bin/env python3
"""Every sim tool with a ``--check`` mode must have a stated enforcement path.

``check:spec`` in package.json is a hand-maintained chain of ``--check`` tools;
a tool left out of it silently stops being enforced (issues #400, #405, #432).
This test enumerates ``sim/tools/*.py``, finds the scripts that define a
``--check`` argparse option, and requires each to be either

(a) invoked by a ``check:*`` script in package.json, or
(b) listed in ``UNWIRED_ALLOWLIST`` below with a one-line reason.

It also requires allowlist entries to stay truthful (the tool still defines
``--check`` and is still not wired), and that every ``npm run check:*`` that
.github/workflows/ci.yml names exists in package.json. Stdlib only.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "sim" / "tools"
PACKAGE = REPO_ROOT / "package.json"
CI_YML = REPO_ROOT / ".github" / "workflows" / "ci.yml"

# Tools with a --check mode that deliberately are NOT in a check:* script.
# tool file name -> why it is safe to leave out.
UNWIRED_ALLOWLIST = {
    "fs_sf_capture.py": "needs ngspice/PDK to run; committed-request drift is covered by test_fs_sf_capture.py",
    "supply_ripple.py": "needs ngspice/PDK to run; emit --check drift is covered by test_supply_ripple.py",
    "raw_min_entropy_estimate.py": "needs ngspice-derived raw data; --check is run by test_raw_min_entropy_estimate.py",
    "liveness_sampler_power.py": "needs ngspice/PDK to run; emit --check drift is covered by test_liveness_sampler_power.py",
}

# `add_argument("--check"` / `add_argument(\n "--check"`; prose mentions of
# --check (docstrings, --check-env subprocess calls) do not match.
CHECK_ARG = re.compile(r"""add_argument\(\s*["']--check["']""")


def defines_check(source: str) -> bool:
    return bool(CHECK_ARG.search(source))


def check_tools(tools_dir: Path = TOOLS_DIR) -> set[str]:
    return {p.name for p in tools_dir.glob("*.py") if defines_check(p.read_text())}


def wired_tools(scripts: dict[str, str]) -> set[str]:
    """Names of sim/tools scripts invoked by any ``check:*`` package script."""
    found: set[str] = set()
    for name, cmd in scripts.items():
        if name.startswith("check:"):
            found.update(re.findall(r"sim/tools/([\w-]+\.py)", cmd))
    return found


def unaccounted(tools: set[str], wired: set[str], allowlist: dict[str, str]) -> list[str]:
    return sorted(tools - wired - set(allowlist))


class CheckModeWiring(unittest.TestCase):
    def setUp(self) -> None:
        self.scripts = json.loads(PACKAGE.read_text())["scripts"]

    def test_heuristic_finds_known_tools(self) -> None:
        tools = check_tools()
        self.assertIn("power_rollup.py", tools)  # wired
        self.assertIn("supply_ripple.py", tools)  # subcommand option
        self.assertNotIn("corner_sanity_check.py", tools)  # only mentions --check-env

    def test_every_check_tool_is_wired_or_allowlisted(self) -> None:
        missing = unaccounted(check_tools(), wired_tools(self.scripts), UNWIRED_ALLOWLIST)
        self.assertEqual(
            missing,
            [],
            "sim tools define --check but are neither run by a check:* script in "
            "package.json nor listed in UNWIRED_ALLOWLIST (with a reason) in this file",
        )

    def test_unwired_tool_is_detected(self) -> None:
        # The guard itself: a hypothetical new --check tool must be reported.
        src = 'p.add_argument(\n    "--check", action="store_true")\n'
        self.assertTrue(defines_check(src))
        self.assertEqual(unaccounted({"new_tool.py"}, wired_tools(self.scripts), UNWIRED_ALLOWLIST), ["new_tool.py"])

    def test_allowlist_is_not_stale(self) -> None:
        tools, wired = check_tools(), wired_tools(self.scripts)
        for name, reason in UNWIRED_ALLOWLIST.items():
            self.assertTrue(reason.strip(), f"{name}: allowlist entry needs a reason")
            self.assertIn(name, tools, f"{name}: no longer defines --check; drop it from the allowlist")
            self.assertNotIn(name, wired, f"{name}: now wired in package.json; drop it from the allowlist")

    def test_ci_npm_scripts_exist(self) -> None:
        ci = CI_YML.read_text()
        referenced = set(re.findall(r"^\s*run:\s*npm run ([\w:-]+)", ci, re.M))
        self.assertTrue(referenced)
        for script in sorted(referenced):
            self.assertIn(script, self.scripts, f"ci.yml runs `npm run {script}` but package.json lacks it")


if __name__ == "__main__":
    unittest.main()
