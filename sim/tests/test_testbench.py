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

    def test_rejects_the_inc_abbreviation(self):
        with self.assertRaises(ValueError):
            testbench.load(self._write('.inc "sneaky.spice"\nv1 out 0 dc 3.3\n'))

    def test_captures_fragment_and_dut_bytes_once(self):
        dut = self.dir / "dut.spice"
        dut.write_bytes(b".subckt c a\n.ends\n")
        d = self._write("v1 out 0 dc 3.3\n", {"design_netlist": str(dut)})
        tb = testbench.load(d)
        dut.write_text("* edited\n")
        (d / "x.spice").write_text("* edited\n")
        self.assertEqual(tb.netlist_bytes, b"v1 out 0 dc 3.3\n")
        self.assertEqual(tb.design_netlist_bytes, b".subckt c a\n.ends\n")
        self.assertEqual(tb.dut_netlist_bytes, tb.design_netlist_bytes)

    def test_fragment_is_its_own_dut_when_no_design_netlist(self):
        tb = testbench.load(self._write("v1 out 0 dc 3.3\n"))
        self.assertEqual(tb.dut_netlist_bytes, tb.netlist_bytes)
        self.assertEqual([n for n, _ in tb.input_snapshots()], [testbench.FRAGMENT_SNAPSHOT_NAME])

    def _dut_tb(self, dut_text: str, extra: dict[str, str] | None = None) -> Path:
        dutdir = self.dir / "dutdir"
        dutdir.mkdir(exist_ok=True)
        dut = dutdir / "dut.spice"
        dut.write_text(dut_text)
        for name, text in (extra or {}).items():
            (dutdir / name).write_text(text)
        return self._write("v1 out 0 dc 3.3\n", {"design_netlist": str(dut)})

    def test_dut_sibling_includes_are_captured_transitively(self):
        d = self._dut_tb(
            '.include "a.spice"\n', {"a.spice": '.inc b.spice\n* a\n', "b.spice": "* b\n"}
        )
        tb = testbench.load(d)
        (self.dir / "dutdir" / "b.spice").write_text("* edited\n")
        self.assertEqual(
            dict(tb.design_dependencies), {"a.spice": b".inc b.spice\n* a\n", "b.spice": b"* b\n"}
        )
        names = [n for n, _ in tb.input_snapshots()]
        self.assertEqual(names[:2], [testbench.FRAGMENT_SNAPSHOT_NAME, testbench.DUT_SNAPSHOT_NAME])
        self.assertEqual(set(names[2:]), {"a.spice", "b.spice"})

    def test_rejects_unsupported_dut_include_forms(self):
        cases = {
            "absolute": '.include "/etc/models.spice"',
            "parent": '.include "../x.spice"',
            "subdir": '.include "sub/x.spice"',
            "lib": '.lib "m.lib" tt',
            "missing": '.include "nope.spice"',
        }
        for label, line in cases.items():
            with self.subTest(label):
                d = self._dut_tb(f"* dut\n{line}\n")
                with self.assertRaisesRegex((ValueError, FileNotFoundError), r"dut\.spice(:2:|: DUT netlists must not contain.*\n  line 2:)"):
                    testbench.load(d)

    def test_unsupported_include_error_is_actionable(self):
        with self.assertRaisesRegex(ValueError, r"dut\.spice:2: .*\n.*bare file name"):
            testbench.load(self._dut_tb('* dut\n.include "../x.spice"\n'))

    def test_rejects_forbidden_directive_inside_a_dut_dependency(self):
        d = self._dut_tb('.include "a.spice"\n', {"a.spice": ".temp 27\n"})
        with self.assertRaisesRegex(ValueError, r"a\.spice.*\n\s+line 1: \.temp"):
            testbench.load(d)

    def test_rejects_include_cycles(self):
        d = self._dut_tb(
            '.include "a.spice"\n', {"a.spice": '.include "b.spice"\n', "b.spice": '.include "a.spice"\n'}
        )
        with self.assertRaisesRegex(ValueError, "cycle"):
            testbench.load(d)

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

    # -- design_netlist: a testbench whose DUT lives in design/ ------------

    def test_dut_netlist_defaults_to_the_fragment_itself(self):
        """With no design_netlist, netlist.path in the record is the fragment."""
        tb = testbench.load(self._write("v1 out 0 dc 3.3\n"))
        self.assertIsNone(tb.design_netlist)
        self.assertEqual(tb.dut_netlist, tb.netlist)

    def test_design_netlist_resolves_repo_relative(self):
        tb = testbench.load(
            self._write(
                "v1 out 0 dc 3.3\n", {"design_netlist": "design/ro_array_core.spice"}
            )
        )
        self.assertIsNotNone(tb.design_netlist)
        self.assertEqual(tb.design_netlist.name, "ro_array_core.spice")
        # The record's netlist.path/sha must point at the DUT, not the fragment.
        self.assertEqual(tb.dut_netlist, tb.design_netlist)
        self.assertNotEqual(tb.dut_netlist, tb.netlist)

    def test_missing_design_netlist_raises(self):
        with self.assertRaises(FileNotFoundError):
            testbench.load(
                self._write("v1 out 0 dc 3.3\n", {"design_netlist": "design/nope.spice"})
            )

    def test_the_repo_array_testbenches_name_their_dut(self):
        for slug in ("ro-array-core-power", "ro-array-sanity-jitter", "rostage-noise"):
            with self.subTest(slug=slug):
                tb = testbench.load(SIM_DIR / "tb" / slug)
                self.assertIsNotNone(
                    tb.design_netlist, f"{slug} must instantiate a design/ cell"
                )
                self.assertEqual(tb.dut_netlist, tb.design_netlist)

    def test_caveats_default_to_empty(self):
        tb = testbench.load(self._write("v1 out 0 dc 3.3\n"))
        self.assertEqual(tb.caveats, ())

    def test_caveats_are_loaded_from_the_manifest(self):
        tb = testbench.load(
            self._write("v1 out 0 dc 3.3\n", {"caveats": ["not a rate measurement", "ideal clock"]})
        )
        self.assertEqual(tb.caveats, ("not a rate measurement", "ideal clock"))

    def test_analysis_type_defaults_to_op(self):
        tb = testbench.load(self._write("v1 out 0 dc {vdd_val}\n"))
        self.assertEqual(tb.analysis_type, "op")

    def test_each_supported_analysis_type_loads(self):
        for kind in testbench.SUPPORTED_ANALYSIS_TYPES:
            with self.subTest(kind=kind):
                tb = testbench.load(
                    self._write("v1 out 0 dc {vdd_val}\n", {"analysis_type": kind})
                )
                self.assertEqual(tb.analysis_type, kind)
                self.assertEqual(tb.stochastic, kind in ("tran-noise", "mc"))

    def test_stochastic_types_are_a_subset_of_supported_types(self):
        self.assertLessEqual(
            set(testbench.STOCHASTIC_ANALYSIS_TYPES),
            set(testbench.SUPPORTED_ANALYSIS_TYPES),
        )

    def test_misspelled_stochastic_types_are_rejected_at_load(self):
        for bad in ("tran-niose", "Tran-Noise", "tran_noise", "monte-carlo", "mcc", ""):
            with self.subTest(bad=bad):
                tb_dir = self._write(
                    "v1 out 0 dc {vdd_val}\n", {"analysis_type": bad}
                )
                with self.assertRaises(ValueError) as ctx:
                    testbench.load(tb_dir)
                msg = str(ctx.exception)
                self.assertIn("tb.json", msg)
                self.assertIn(repr(bad), msg)
                self.assertIn("tran-noise", msg)
                self.assertIn("op", msg)

    def test_non_string_analysis_types_are_rejected_at_load(self):
        for bad in (None, 1, 1.5, True, ["mc"], {"type": "mc"}):
            with self.subTest(bad=bad):
                tb_dir = self._write(
                    "v1 out 0 dc {vdd_val}\n", {"analysis_type": bad}
                )
                with self.assertRaises(ValueError) as ctx:
                    testbench.load(tb_dir)
                self.assertIn(repr(bad), str(ctx.exception))
                self.assertIn("supported types", str(ctx.exception))

    def test_every_committed_manifest_loads(self):
        for tb_dir in testbench.discover(SIM_DIR / "tb"):
            with self.subTest(tb=tb_dir.name):
                tb = testbench.load(tb_dir)
                self.assertIn(tb.analysis_type, testbench.SUPPORTED_ANALYSIS_TYPES)

    def test_the_sampler_testbenches_declare_their_method_limits(self):
        """The two testbenches whose records would otherwise overstate what
        they measured -- a bitstream captured well above the target rate, and
        a cell characterized without its entropy source -- must carry that
        limit in the manifest so every minted record repeats it. sim/README.md:
        "an unstated limit is a defect"."""
        for slug in ("sampler-array-digitize", "sampler-dff-setup-hold"):
            with self.subTest(slug=slug):
                tb = testbench.load(SIM_DIR / "tb" / slug)
                self.assertTrue(tb.caveats, f"{slug} must declare its method limits")


if __name__ == "__main__":
    unittest.main()
