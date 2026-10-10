#!/usr/bin/env python3
"""Tests for `layout/digital/tap_distance.py` (issue #448).

Two groups:

* stdlib-only: the committed report is pinned to the committed stream
  (SHA-256) and to the committed spec, and never reports an unsupported rule
  as a pass. No klayout needed.
* geometry fixtures (need the `klayout` Python module, skipped without it):
  small synthetic streams that exercise the check on a compliant tap
  arrangement, an over-limit gap, and a nearby tap wired to the wrong supply.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

LAYOUT_DIR = Path(__file__).resolve().parents[1]
DIGITAL = LAYOUT_DIR / "digital"


def _load():
    spec = importlib.util.spec_from_file_location("tap_distance", DIGITAL / "tap_distance.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["tap_distance"] = module
    spec.loader.exec_module(module)
    return module


td = _load()
SPEC = json.loads((DIGITAL / "tap-distance-spec.json").read_text())
REPORT = json.loads((DIGITAL / "reports" / "tap-distance.json").read_text())
db = td._load_klayout()


class CommittedReportTests(unittest.TestCase):
    def test_report_is_pinned_to_committed_stream_and_spec(self):
        self.assertEqual(
            REPORT["input"]["gds_sha256"],
            hashlib.sha256((DIGITAL / "trng_top.gds").read_bytes()).hexdigest(),
        )
        self.assertEqual(
            REPORT["input"]["spec_sha256"],
            hashlib.sha256((DIGITAL / "tap-distance-spec.json").read_bytes()).hexdigest(),
        )

    def test_every_spec_rule_has_an_explicit_status(self):
        got = {r["id"]: r["status"] for r in REPORT["rules"]}
        self.assertEqual(set(got), {r["id"] for r in SPEC["rules"]})
        self.assertTrue(set(got.values()) <= {"pass", "fail", "not_applicable", "unsupported"})

    def test_unsupported_rules_never_pass(self):
        for rule in SPEC["rules"]:
            if rule["kind"] == "unsupported":
                status = {r["id"]: r["status"] for r in REPORT["rules"]}[rule["id"]]
                self.assertEqual(status, "unsupported", rule["id"])
        if any(r["status"] == "unsupported" for r in REPORT["rules"]):
            self.assertNotEqual(REPORT["verdict"], "pass")

    def test_measured_rules_state_limit_and_distance(self):
        for r in REPORT["rules"]:
            if r["kind"] == "max_tap_distance":
                self.assertEqual(r["limit_um"], 15)
                self.assertIn("max_distance_um", r)
                self.assertIn("worst_groups", r)
                self.assertIn("coverage_profile", r)


# ---------------------------------------------------------------- fixtures

LAYER = {name: tuple(int(p) for p in spec.split("/")) for name, spec in SPEC["layers"].items() if isinstance(spec, str)}


def _build(path: Path, *, ntap_x: float, ptap_x: float, wrong_ntap_x: float | None = None, dnwell: bool = False):
    """One PMOS in an Nwell, one NMOS outside it, rails and taps.

    `ntap_x` / `ptap_x`: left edge (um) of the VDD-side N+ tap and the
    VSS-side P+ tap. `wrong_ntap_x`: an additional N+ well tap wired to the
    VSS rail instead of the VDD rail (a tap that is near but on the wrong
    supply).
    """
    ly = db.Layout()
    ly.dbu = 0.001
    top = ly.create_cell("fixture")

    def box(name_or_ld, x0, y0, x1, y1):
        ld = LAYER[name_or_ld] if isinstance(name_or_ld, str) else name_or_ld
        top.shapes(ly.layer(*ld)).insert(db.DBox(x0, y0, x1, y1))

    def label(ld, text, x, y):
        top.shapes(ly.layer(*ld)).insert(db.DText(text, x, y))

    box("dualgate", -5, -15, 60, 15)
    box("nwell", 0, 0, 50, 6)
    # PMOS body inside the Nwell
    box("comp", 2, 1, 6, 5)
    box("pplus", 1, 0.5, 7, 5.5)
    box("poly2", 3.8, 0.5, 4.2, 5.5)
    # NMOS outside the Nwell
    box("comp", 2, -9, 6, -6)
    box("nplus", 1, -9.5, 7, -5.5)
    box("poly2", 3.8, -9.5, 4.2, -5.5)
    # rails (Metal1) with the same text convention as the digital block
    box((34, 0), 0, 6.5, 55, 7.5)  # VDD
    box((34, 0), 0, -5, 55, -4)  # VSS
    label((34, 10), "VDD", 1, 7)
    label((34, 10), "VSS", 1, -4.5)

    def ntap(x, rail):
        box("comp", x, 2, x + 1, 3)
        box("nplus", x - 0.3, 1.7, x + 1.3, 3.3)
        box("contact", x + 0.3, 2.3, x + 0.7, 2.7)
        if rail == "VDD":
            box((34, 0), x, 2, x + 1, 7.5)
        else:
            box((34, 0), x, -5, x + 1, 3)

    ntap(ntap_x, "VDD")
    if wrong_ntap_x is not None:
        ntap(wrong_ntap_x, "VSS")
    # P+ substrate tap outside the Nwell, wired to the VSS rail
    box("comp", ptap_x, -9, ptap_x + 1, -8)
    box("pplus", ptap_x - 0.3, -9.3, ptap_x + 1.3, -7.7)
    box("contact", ptap_x + 0.3, -8.7, ptap_x + 0.7, -8.3)
    box((34, 0), ptap_x, -9, ptap_x + 1, -4)
    if dnwell:
        box("dnwell", -2, -2, 52, 8)
    ly.write(str(path))
    return path


def _rule(report, rule_id):
    return next(r for r in report["rules"] if r["id"] == rule_id)


@unittest.skipIf(db is None, "klayout Python module not installed")
class FixtureTests(unittest.TestCase):
    def _run(self, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            gds = _build(Path(tmp) / "fx.gds", **kw)
            return td.analyze(gds, SPEC)

    def test_compliant_taps_pass_but_verdict_is_not_a_blanket_pass(self):
        rep = self._run(ntap_x=12, ptap_x=12)
        for rid in ("LU.3", "LU.4"):
            r = _rule(rep, rid)
            self.assertEqual(r["status"], "pass", rid)
            self.assertLess(r["max_distance_um"], 15)
            self.assertGreater(r["max_distance_um"], 9)  # left edge ~10 um from the tap
            self.assertEqual(r["tap_identity"]["on_required_rail"], 1)
        # unsupported guideline rules are present, so the run is incomplete
        self.assertEqual(rep["verdict"], "incomplete")
        self.assertEqual(_rule(rep, "LU.7")["status"], "unsupported")
        self.assertEqual(_rule(rep, "LU.1")["status"], "not_applicable")

    def test_over_limit_gap_fails_with_a_worst_location(self):
        rep = self._run(ntap_x=36, ptap_x=36)
        for rid in ("LU.3", "LU.4"):
            r = _rule(rep, rid)
            self.assertEqual(r["status"], "fail", rid)
            self.assertGreater(r["max_distance_um"], 15)
            self.assertLess(r["max_distance_um"], 36)
            self.assertTrue(r["worst_groups"][0]["worst_locations"])
        self.assertEqual(rep["verdict"], "fail")

    def test_nearby_tap_on_wrong_supply_is_excluded(self):
        rep = self._run(ntap_x=36, ptap_x=12, wrong_ntap_x=8)
        r = _rule(rep, "LU.4")
        self.assertEqual(r["tap_identity"]["on_required_rail"], 1)
        self.assertEqual(r["tap_identity"]["on_other_rail"], 1)
        # geometry alone would be satisfied by the near (VSS-wired) tap ...
        self.assertLess(r["geometry_only_max_distance_um"], 15)
        # ... but it ties the well to the wrong rail, so the rule fails.
        self.assertEqual(r["status"], "fail")
        self.assertGreater(r["max_distance_um"], 15)

    def test_dnwell_makes_outside_dnwell_rules_unsupported_not_pass(self):
        rep = self._run(ntap_x=12, ptap_x=12, dnwell=True)
        self.assertEqual(_rule(rep, "LU.4")["status"], "unsupported")
        self.assertEqual(_rule(rep, "LU.1")["status"], "unsupported")
        self.assertNotEqual(rep["verdict"], "pass")


if __name__ == "__main__":
    unittest.main()
