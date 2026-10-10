#!/usr/bin/env python3
"""Freshness-check wiring for `layout/digital/tap_distance.py` (issue #458).

Stdlib only; needs no klayout. Two groups:

* inventory: `npm run check:digital-tap-distance` is in `check:ci` and the PR
  workflow, and the nightly workflow runs the strict form independently of
  earlier step failures; the docs name it.
* `--check` semantics, with the measurement stubbed: an unchanged calculated
  result passes even when it discloses a failing verdict, a changed calculated
  result with unchanged input hashes fails, a missing module is an explicit
  skip without `--require-tools` and a failure with it, and nothing is written.
"""

from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
DIGITAL = REPO / "layout" / "digital"
STRICT = "python3 layout/digital/tap_distance.py --check --require-tools"


def _load():
    spec = importlib.util.spec_from_file_location("tap_distance_wiring", DIGITAL / "tap_distance.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["tap_distance_wiring"] = module
    spec.loader.exec_module(module)
    return module


td = _load()


class InventoryTests(unittest.TestCase):
    def test_check_ci_and_check_all_expose_the_check(self):
        scripts = json.loads((REPO / "package.json").read_text())["scripts"]
        self.assertEqual(scripts["check:digital-tap-distance"], "python3 layout/digital/tap_distance.py --check")
        self.assertIn("npm run check:digital-tap-distance", scripts["check:ci"])
        self.assertIn(STRICT, scripts["check:all"])

    def test_pr_workflow_runs_the_ordinary_form(self):
        ci = (REPO / ".github" / "workflows" / "ci.yml").read_text()
        self.assertRegex(ci, r"run: npm run check:digital-tap-distance\n")
        self.assertIn("layout/digital/tap_distance.py --check (tap-distance report freshness)", ci)

    def test_nightly_runs_strict_form_independently(self):
        text = (REPO / ".github" / "workflows" / "pdk-nightly.yml").read_text()
        m = re.search(
            r"      - name: Tap-distance report regeneration guard\n"
            r"        if: always\(\)\n"
            r"        run: (.+)\n",
            text,
        )
        self.assertIsNotNone(m, "strict nightly step missing or not under `if: always()`")
        self.assertEqual(m.group(1), STRICT)
        # after the klayout-tools install, so the module it needs is provisioned
        self.assertGreater(m.start(), text.index("Install klayout-tools"))

    def test_docs_name_the_coverage(self):
        readme = (REPO / "README.md").read_text()
        self.assertIn("npm run check:digital-tap-distance", readme)
        self.assertIn(STRICT.replace("python3 ", ""), readme)


class CheckSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.committed = json.loads((DIGITAL / "reports" / "tap-distance.json").read_text())
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.report = Path(self.tmp.name) / "tap-distance.json"
        self.report.write_text(td._dump(self.committed))
        self.before = self.report.read_bytes()

    def _main(self, fresh, *flags, klayout=object()):
        argv = ["--check", "--report", str(self.report), *flags]
        out, err = io.StringIO(), io.StringIO()
        with (
            mock.patch.object(td, "_load_klayout", return_value=klayout),
            mock.patch.object(td, "analyze", return_value=fresh),
            contextlib.redirect_stdout(out),
            contextlib.redirect_stderr(err),
        ):
            rc = td.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_current_report_passes_even_with_a_failing_verdict(self):
        rc, out, _ = self._main(copy.deepcopy(self.committed), "--require-tools")
        self.assertEqual(rc, 0)
        self.assertIn("matches a fresh run", out)
        self.assertIn(f"verdict: {self.committed['verdict']}", out)

    def test_changed_result_with_unchanged_input_hashes_fails(self):
        fresh = copy.deepcopy(self.committed)
        rule = next(r for r in fresh["rules"] if "max_distance_um" in r)
        rule["max_distance_um"] += 1.0
        self.assertEqual(fresh["input"], self.committed["input"])
        rc, _, err = self._main(fresh, "--require-tools")
        self.assertEqual(rc, 1)
        self.assertIn("is stale", err)

    def test_provenance_only_difference_is_ignored(self):
        fresh = copy.deepcopy(self.committed)
        fresh["provenance"] = {"klayout_version": "other"}
        self.assertEqual(self._main(fresh)[0], 0)

    def test_missing_module_is_an_explicit_skip_unless_required(self):
        rc, _, err = self._main(None, klayout=None)
        self.assertEqual(rc, 0)
        self.assertIn("skipping", err)
        rc, _, err = self._main(None, "--require-tools", klayout=None)
        self.assertEqual(rc, 2)
        self.assertIn("not installed", err)
        self.assertNotIn("skipping", err)

    def test_check_never_rewrites_the_report(self):
        fresh = copy.deepcopy(self.committed)
        next(r for r in fresh["rules"] if "max_distance_um" in r)["max_distance_um"] += 1.0
        self._main(fresh, "--require-tools")
        self.assertEqual(self.report.read_bytes(), self.before)


if __name__ == "__main__":
    unittest.main()
