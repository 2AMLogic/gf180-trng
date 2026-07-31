#!/usr/bin/env python3
"""Unit tests for sim/harness/testbench.py -- the testbench contract that
rejects fragments trying to own what the harness owns."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import testbench  # noqa: E402


class TestbenchLoadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def _write(self, netlist: str, manifest: dict | None = None) -> Path:
        """Lay out sim/tb/<slug>/ the way sim/README.md specifies."""
        tb_dir = self.dir / "an-experiment"
        tb_dir.mkdir(parents=True, exist_ok=True)
        (tb_dir / "x.spice").write_text(netlist)
        base = {"name": "x", "netlist": "x.spice", "measure": {"vout": "v(out)"}}
        base.update(manifest or {})
        (tb_dir / "tb.json").write_text(json.dumps(base))
        return tb_dir

    def test_loads_a_valid_manifest(self):
        tb = testbench.load(self._write("v1 out 0 dc {vdd_val}\n"))
        self.assertEqual(tb.slug, "x")
        self.assertEqual(tb.measure, {"vout": "v(out)"})
        self.assertEqual(tb.temperatures_c, (-40.0, 27.0, 125.0))
        self.assertFalse(tb.stochastic)

    def test_loads_by_manifest_path_too(self):
        tb_dir = self._write("v1 out 0 dc {vdd_val}\n")
        tb = testbench.load(tb_dir / "tb.json")
        self.assertEqual(tb.slug, "x")

    def test_discover_finds_testbench_dirs(self):
        self._write("v1 out 0 dc {vdd_val}\n")
        found = testbench.discover(self.dir)
        self.assertEqual([p.name for p in found], ["an-experiment"])

    def test_rejects_netlists_that_pin_the_temperature(self):
        with self.assertRaises(ValueError) as ctx:
            testbench.load(self._write("v1 out 0 dc 3.3\n.temp 27\n"))
        self.assertIn(".temp", str(ctx.exception))

    def test_rejects_netlists_that_include_models_themselves(self):
        with self.assertRaises(ValueError):
            testbench.load(self._write('.lib "models" typical\nv1 out 0 dc 3.3\n'))

    def test_rejects_netlists_with_control_block(self):
        with self.assertRaises(ValueError):
            testbench.load(self._write("v1 out 0 dc 3.3\n.control\nrun\n.endc\n"))

    def test_rejects_netlists_that_include_other_files(self):
        with self.assertRaises(ValueError):
            testbench.load(self._write('.include "sneaky.spice"\nv1 out 0 dc 3.3\n'))

    def test_rejects_a_manifest_without_measurements(self):
        with self.assertRaises(ValueError):
            testbench.load(self._write("v1 out 0 dc 3.3\n", {"measure": {}}))

    def test_rejects_non_alnum_measurement_names(self):
        with self.assertRaises(ValueError):
            testbench.load(
                self._write("v1 out 0 dc 3.3\n", {"measure": {"bad name!": "v(out)"}})
            )

    def test_missing_netlist_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            testbench.load(self._write("v1 out 0 dc 3.3\n", {"netlist": "missing.spice"}))

    def test_stochastic_flag_follows_analysis_type(self):
        tb = testbench.load(
            self._write("v1 out 0 dc 3.3\n", {"analysis_type": "mc", "default_runs": 3})
        )
        self.assertTrue(tb.stochastic)

    def test_the_repo_smoke_testbench_is_valid(self):
        tb = testbench.load(SIM_DIR / "tb" / "smoke-op")
        self.assertEqual(tb.corners, ("tt",))
        self.assertIn("vout", tb.measure)

    def test_the_repo_corner_sanity_testbench_is_valid(self):
        tb = testbench.load(SIM_DIR / "tb" / "corner-sanity-nfet-id")
        self.assertEqual(tb.corners, ("mos",))
        self.assertIn("id", tb.measure)

    def test_the_repo_mismatch_seed_testbench_is_stochastic(self):
        tb = testbench.load(SIM_DIR / "tb" / "nfet-mismatch-seed")
        self.assertTrue(tb.stochastic)
        self.assertEqual(tb.default_runs, 3)
        self.assertEqual(tb.extra_lib_sections, ("statistical",))


if __name__ == "__main__":
    unittest.main()
