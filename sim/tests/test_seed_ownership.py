#!/usr/bin/env python3
"""Offline tests: the harness alone owns the seed of a stochastic run (#566)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import corners, runner, testbench  # noqa: E402
from tests.test_runner import fake_pdk  # noqa: E402


class SeedOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def make(self, *, analysis_type="tran-noise", options=(), fragment="r1 out 0 1k\n",
             analyses=("tran 1n 1u",), dut=None, extra=None) -> Path:
        d = self.root / "tb"
        d.mkdir(exist_ok=True)
        (d / "x.spice").write_text(fragment)
        manifest = {
            "name": "x", "netlist": "x.spice", "measure": {"v": "v(out)"},
            "analysis_type": analysis_type, "options": list(options),
            "analyses": list(analyses),
        }
        manifest.update(extra or {})
        (d / "tb.json").write_text(json.dumps(manifest))
        return d

    def assertRejected(self, needle: str, **kw):
        with self.assertRaises(ValueError) as cm:
            testbench.load(self.make(**kw))
        self.assertIn("seeds are owned by the harness", str(cm.exception))
        self.assertIn(needle, str(cm.exception))

    def test_manifest_option_seed_rejected(self):
        self.assertRejected("options[1]", options=["reltol=1e-5", "seed=999"])
        self.assertRejected("options[0]", options=["RELTOL=1e-5 Seed = 3"])

    def test_fragment_seed_forms_rejected(self):
        for line in (".option seed=5", ".OPTIONS reltol=1e-4 seed=7",
                     ".option reltol=1e-4\n+ seed=7", ".option seed=random"):
            self.assertRejected("x.spice", fragment=f"r1 out 0 1k\n{line}\n")

    def test_analysis_seed_commands_rejected(self):
        for cmd in ("setseed 4", "set rndseed=4", "unset rndseed",
                    "option seed=4", "tran 1n 1u\nsetseed 9"):
            self.assertRejected("analyses[0]", analyses=[cmd])

    def test_mc_type_is_covered(self):
        self.assertRejected("options[0]", analysis_type="mc", options=["seed=1"])

    def test_non_seed_content_accepted(self):
        tb = testbench.load(self.make(
            options=["reltol=1e-5", "method=gear"],
            fragment="* seed=3 in a comment\nr1 out 0 1k ; .option seed=4\n"
                     ".option reltol=1e-4\n.param seedling=1\n",
            analyses=["tran 1n 1u", "set numdgt=8"],
        ))
        self.assertEqual(runner.plan_runs(tb, [1, 2]), [(1, 0), (2, 1)])

    def test_deterministic_testbench_not_checked(self):
        tb = testbench.load(self.make(analysis_type="op", options=["seed=999"]))
        self.assertEqual(runner.plan_runs(tb, None), [(None, 0)])

    def test_hand_built_dut_and_transitive_include_rejected(self):
        d = self.make()
        dut = self.root / "dut.spice"
        dut.write_text('.include "dep.spice"\nr2 a b 1\n')
        (self.root / "dep.spice").write_text(".options seed=11\n")
        tb = testbench.load(d)
        tb.design_netlist = dut
        with self.assertRaises(ValueError) as cm:
            runner.plan_runs(tb, [1])
        self.assertIn("dep.spice", str(cm.exception))
        self.assertIn("line 1", str(cm.exception))

    def test_hand_built_captured_bytes_rejected(self):
        tb = testbench.load(self.make())
        tb.design_netlist = self.root / "dut.spice"
        tb.design_netlist_bytes = b"r2 a b 1\n"
        tb.design_dependencies = (("dep.spice", b"* ok\n.option seed=2\n"),)
        with self.assertRaises(ValueError) as cm:
            runner.plan_runs(tb, [1])
        self.assertIn("dep.spice", str(cm.exception))

    def test_hand_built_options_rejected_by_plan_and_compose(self):
        tb = testbench.load(self.make())
        tb.options = ("seed=999",)
        with self.assertRaises(ValueError):
            runner.plan_runs(tb, [1])
        pdk = fake_pdk(self.root / "gf180mcuD")
        point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]
        with self.assertRaises(ValueError):
            runner.compose_deck(tb, pdk, point, seed=1)

    def test_rejection_precedes_workdir_creation(self):
        tb = testbench.load(self.make())
        tb.options = ("seed=999",)
        pdk = fake_pdk(self.root / "gf180mcuD")
        point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]
        work = self.root / "work"
        with self.assertRaises(ValueError):
            runner.run_point(tb, pdk, point, work, [1])
        self.assertFalse(work.exists())

    def test_committed_testbenches_still_load(self):
        for d in testbench.discover(SIM_DIR / "tb"):
            testbench.load(d)


if __name__ == "__main__":
    unittest.main()
