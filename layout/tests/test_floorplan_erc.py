#!/usr/bin/env python3
"""Tests for the whole-block supply ERC over the composed floorplan
(`layout/floorplan/erc_supply.py`, issue #447).

Two groups:

* Tool-free: the committed `reports/erc-supply.json` must pin the committed
  GDS and spec by hash, and `floorplan.py`'s check path must fail when it
  does not. These run on every `npm run test:layout`.
* Negative/positive controls through the real, pinned `klt erc` (0.6.0),
  against a small synthetic stream drawn on the real layer numbers and run
  with the real committed spec. The composed stream itself takes minutes per
  run, so the controls mutate a tiny stand-in in a temp dir (never a
  committed file). They skip unless the `klt` on PATH reports exactly the
  pinned version; on a host with a different klt, put a pinned shim first:
  `uvx --from "klayout-tools==0.6.0" klt`.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "design"))

from layout.floorplan import erc_supply  # noqa: E402
from layout.floorplan import floorplan  # noqa: E402

_GDSII = REPO_ROOT / "layout" / "testcells" / "gdsii.py"
_spec = importlib.util.spec_from_file_location("_gdsii_for_erc_tests", _GDSII)
gdsii = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gdsii
_spec.loader.exec_module(gdsii)

Rect, Label = gdsii.Rect, gdsii.Label
METALS = (34, 36, 42, 46, 81)
VIAS = (35, 38, 40, 41)


def _stack(x: float, y: float, w: float = 2.0) -> list:
    """Metal1..Metal5 pads at (x, y) joined by Via1..Via4."""
    rects = [Rect(m, 0, x, y, x + w, y + w) for m in METALS]
    rects += [Rect(v, 0, x + 0.5, y + 0.5, x + 1.5, y + 1.5) for v in VIAS]
    return rects


def build_stand_in(path: str, *, drop_label=None, drop_second_stack_via=None,
                   bridge=None) -> None:
    """One flat cell: a Metal1-Metal5 stack per declared supply with its
    trunk label on Metal4 (46/10), a gate on vss, and a second vss stack
    (labelled `vss` on Metal1) strapped to the first on Metal4."""
    rects: list = []
    labels: list = []
    for i, net in enumerate(erc_supply.DECLARED_SUPPLIES):
        rects += _stack(i * 10, 0)
        if net != drop_label:
            labels.append(Label(46, 10, i * 10 + 1, 1, net))
    # a gate (poly over active) contacted to the vss Metal1 pad
    rects += [Rect(22, 0, 40, 5, 44, 8), Rect(30, 0, 41.5, 4, 42.3, 9),
              Rect(33, 0, 41.5, 8.2, 42.3, 8.9), Rect(34, 0, 41.2, 8, 42.6, 9.2)]
    second = _stack(40, 20)
    if drop_second_stack_via is not None:
        second = [r for r in second if r.layer != drop_second_stack_via]
    rects += second
    labels.append(Label(34, 10, 41, 21, "vss"))
    rects.append(Rect(46, 0, 40.5, 2, 41.5, 21))  # the Metal4 strap
    if bridge:  # a Metal4 bar (x0, x1) across the trunks it spans
        rects.append(Rect(46, 0, bridge[0], 0.5, bridge[1], 1.5))
    gdsii.write_gds(path, "stand_in", [("top", rects, labels)])


def _pinned_klt_available() -> bool:
    if shutil.which("klt") is None:
        return False
    try:
        done = subprocess.run(["klt", "--version"], capture_output=True,
                              text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    return re.fullmatch(r"klt\s+0\.6\.0(\+\S+)?", (done.stdout or done.stderr).strip()) is not None


def run_erc_on(gds: str) -> dict:
    done = subprocess.run(
        ["klt", "erc", gds, str(erc_supply.SPEC), "--top", "top",
         "--findings-only", "--format", "json"],
        capture_output=True, text=True, timeout=600, cwd=str(REPO_ROOT),
    )
    return json.loads(done.stdout)


class SpecShapeTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads(erc_supply.SPEC.read_text())

    def test_pin_matches_signoff(self):
        text = (REPO_ROOT / "signoff" / "check.py").read_text()
        pin = re.search(r'^KLT_PIN = "([^"]+)"', text, re.MULTILINE).group(1)
        self.assertEqual(erc_supply.KLT_PIN, pin)

    def test_one_supply_net_per_physical_supply(self):
        nets = self.spec["nets"]
        self.assertEqual([n["name"] for n in nets], list(erc_supply.DECLARED_SUPPLIES))
        self.assertTrue(all(n["kind"] == "supply" for n in nets))
        # no second spelling of a supply, and no substrate net merged in
        names = {n["name"].lower() for n in nets}
        self.assertNotIn("vsubs", names)
        self.assertNotIn("vddr", names)

    def test_metal1_to_metal5_stack(self):
        stack = self.spec["stackup"]
        self.assertEqual(stack[0]["role"], "gate")
        self.assertEqual([s["name"] for s in stack[1:]],
                         ["Metal1", "Metal2", "Metal3", "Metal4", "Metal5"])
        self.assertEqual([v["name"] for v in self.spec["vias"] if v["name"].startswith("Via")],
                         ["Via1", "Via2", "Via3", "Via4"])
        labelled = {s["label_layer"] for s in stack if "label_layer" in s}
        self.assertIn("46/10", labelled)  # the trunk labels interregion.py draws

    def test_unexpressible_ties_and_substrate_are_disclosed(self):
        self.assertNotIn("ties", self.spec)
        self.assertEqual(self.spec["ties_disclosure"]["kind"], "unexpressible")
        self.assertIn("substrate", self.spec["ties_disclosure"]["reason"])


class FreshnessTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(erc_supply.REPORT.read_text())

    def test_committed_report_is_current_and_clean(self):
        self.assertEqual(erc_supply.freshness_problems(), [])

    def test_changed_stream_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            gds = Path(tmp) / "s.gds"
            gds.write_bytes(erc_supply.GDS.read_bytes() + b"\0\0")
            problems = erc_supply.report_problems(self.report, gds=gds)
        self.assertTrue(any("input.content_hash" in p for p in problems), problems)

    def test_changed_spec_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.json"
            spec.write_text(erc_supply.SPEC.read_text().replace('"vss"', '"vss" ', 1))
            problems = erc_supply.report_problems(self.report, spec=spec)
        self.assertTrue(any("spec.content_hash" in p for p in problems), problems)

    def test_findings_fail(self):
        bad = copy.deepcopy(self.report)
        bad["erc_status"] = "violations"
        bad["erc_finding_count"] = 1
        bad["erc_findings"] = [{"rule": "erc.supply_short"}]
        self.assertTrue(any("not clean" in p for p in erc_supply.report_problems(bad)))

    def test_zero_coverage_supply_fails(self):
        bad = copy.deepcopy(self.report)
        bad["erc_coverage"]["checked"] = [
            c for c in bad["erc_coverage"]["checked"] if '"vddd"' not in c]
        problems = erc_supply.report_problems(bad)
        self.assertTrue(any("'vddd'" in p and "coverage" in p for p in problems), problems)

    def test_skipped_coverage_fails(self):
        bad = copy.deepcopy(self.report)
        bad["erc_coverage"]["skipped"] = [{"id": "x", "reason": "y"}]
        self.assertTrue(any("skipped" in p for p in erc_supply.report_problems(bad)))

    def test_wrong_klt_version_fails(self):
        bad = copy.deepcopy(self.report)
        bad["provenance"]["klt_version"] = "0.7.0"
        self.assertTrue(any("klt_version" in p for p in erc_supply.report_problems(bad)))

    def test_dropped_disclosure_fails(self):
        bad = copy.deepcopy(self.report)
        bad["ties_disclosure"] = None
        self.assertTrue(any("ties_disclosure" in p for p in erc_supply.report_problems(bad)))

    def test_missing_report_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            problems = erc_supply.freshness_problems(Path(tmp) / "absent.json")
        self.assertTrue(problems and "missing" in problems[0])

    def test_floorplan_check_path_fails_on_stale_report(self):
        with mock.patch.object(erc_supply, "freshness_problems",
                               return_value=["stale for the test"]):
            with mock.patch("builtins.print"):
                rc = floorplan.main([])
        self.assertEqual(rc, floorplan.EXIT_FAIL)

    def test_project_report_trims_but_keeps_supply_coverage(self):
        native = {
            "gates": [{"gate_id": "gate0"}], "coverage": {"scope": "antenna"},
            "gate_count": 1, "erc_findings": [], "erc_finding_count": 0,
            "erc_status": "clean",
            "erc_coverage": {"checked": ['erc.floating_gate:["gate0"]',
                                         'erc.net_connectivity:["vss"]'],
                             "skipped": []},
        }
        out = erc_supply.project_report(native)
        self.assertNotIn("gates", out)
        self.assertNotIn("coverage", out)
        self.assertEqual(out["erc_coverage"]["checked"], ['erc.net_connectivity:["vss"]'])
        self.assertEqual(out["erc_coverage"]["floating_gate_checked_count"], 1)
        self.assertEqual(native["erc_coverage"]["checked"][0], 'erc.floating_gate:["gate0"]')


@unittest.skipUnless(_pinned_klt_available(),
                     "needs the pinned klt (0.6.0) first on PATH")
class KltControlTests(unittest.TestCase):
    def _run(self, **kw) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            gds = str(Path(tmp) / "stand_in.gds")
            build_stand_in(gds, **kw)
            return run_erc_on(gds)

    @staticmethod
    def _rules(result: dict) -> list:
        return sorted({(f["rule"], f.get("net")) for f in result["erc_findings"]})

    def test_baseline_is_clean_with_every_supply_computed(self):
        result = self._run()
        self.assertEqual(result["erc_status"], "clean", result["erc_findings"])
        checked = set(result["erc_coverage"]["checked"])
        for net in erc_supply.DECLARED_SUPPLIES:
            self.assertIn(f'erc.net_connectivity:["{net}"]', checked)

    def test_shared_vss_over_two_stacks_is_one_island(self):
        # the baseline's second vss stack is a distinct labelled pad joined
        # on Metal4: no finding means the shared net resolved to one island
        self.assertEqual(self._rules(self._run()), [])

    def test_opened_join_is_unconnected_net(self):
        # Via1 removed from the second vss stack: its Metal1-labelled pad is
        # no longer on the Metal4 strap, so `vss` resolves to two islands.
        rules = self._rules(self._run(drop_second_stack_via=35))
        self.assertEqual(rules, [("erc.unconnected_net", "vss")])

    def test_metal_bridge_between_distinct_supplies_is_supply_short(self):
        for span, shorted in (((1.9, 11.1), {"vddr1", "vddr2"}),
                              ((21.9, 31.1), {"vdd", "vddd"})):
            rules = self._rules(self._run(bridge=span))
            named = {n for r, n in rules if r == "erc.supply_short"}
            self.assertTrue(named and named <= shorted, rules)
            self.assertFalse([r for r, _ in rules if r != "erc.supply_short"], rules)

    def test_missing_trunk_label_is_not_a_pass(self):
        result = self._run(drop_label="vddd")
        self.assertEqual(result["erc_status"], "violations")
        self.assertIn(("erc.unconnected_net", "vddd"), self._rules(result))


if __name__ == "__main__":
    unittest.main()
