#!/usr/bin/env python3
"""Unit tests for issue #233's interface-load treatment in
``sim/tb/digital-sta-power/run_sta.py``.

DR-0025 scoped a full-chip parasitic extraction (#232) away from the six
inter-region trunks that terminate on the abstracted ``digital`` region and
handed the question of what those trunks' own Metal4 RC does to `digital`'s
own STA to this issue instead. Two things need checking with no PDK and no
``openroad`` on the runner, which is exactly what this file covers:

1. **Derivation, not transcription.** The six ports and their trunk lengths
   must come from ``layout/floorplan/reports/interregion.json`` at call
   time -- so a future floorplan/routing change (#222-style) is caught by a
   changed number here, not silently missed by a hand-copied constant. This
   is tested against a synthetic report with deliberately different numbers
   from the committed one, not just against the committed report (which
   would not distinguish "reads the file" from "reads the file once and
   memorized the answer").
2. **Bus-notation pin names.** The DEF's actual port names for the two
   liveness-tap nets are ``ring_bit[0]``/``ring_bit[1]``, not the
   interregion net names ``ring_bit1``/``ring_bit2`` -- read off each
   route's own ``digital`` endpoint, not string-derived from the net name.

3. **The stated transition is in the deck's own convention.** A transition
   time means nothing without the thresholds it is measured between, and
   ``SlewConvention`` reads them (plus ``slew_derate_from_library``) from the
   liberty deck rather than assuming 30/70 or a derate of 1. The arithmetic
   is checked here against hand-worked values; that the *tool* reads a stated
   transition in that same domain is checked by
   ``sim/tb/digital-sta-power/sdc_treatment_probe.py --check``, which needs
   ``openroad`` and the PDK and so cannot run here.

The generated SDC's own choice of ``set_input_transition`` over ``set_load``
(see ``run_sta.py``'s module docstring for why) is exercised by asserting
what ``_tcl()`` emits for a synthetic PDK/corner -- with no PDK or
``openroad`` needed, since ``_tcl()`` only formats strings, save for the one
liberty deck it reads its slew convention from, which these tests supply as a
synthetic file.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TB_DIR = Path(__file__).resolve().parents[1] / "tb" / "digital-sta-power"
SIM_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(TB_DIR))

import run_sta  # noqa: E402


#: Just enough of a liberty header for ``liberty_slew_convention()``. The real
#: decks declare all three (30/70 % thresholds, derate 0.5); these tests use
#: deliberately different numbers where the point is that the value is read
#: rather than assumed.
_LIBERTY_HEADER = """library (synthetic) {{
  time_unit : 1ns ;
  slew_derate_from_library : {derate} ;
  slew_lower_threshold_pct_fall : {lo} ;
  slew_lower_threshold_pct_rise : {lo} ;
  slew_upper_threshold_pct_fall : {hi} ;
  slew_upper_threshold_pct_rise : {hi} ;
  nom_process : 1 ;
  nom_temperature : 25 ;
  nom_voltage : 3.3 ;
}}
"""


class _FakePdk:
    """Just enough of ``harness.pdk.Pdk`` for ``_tcl()``. Every path but the
    liberty deck is only ever formatted into the generated Tcl, never opened;
    the liberty deck is opened, for its slew convention, so a synthetic one is
    written into place under ``path``."""

    def __init__(self, path: Path, variant: str = "gf180mcuD"):
        self.path = str(path)
        self.variant = variant
        self.version = "fake"


def _fake_pdk_with_liberty(tmp_dir: Path, corner: str, *, lo=30, hi=70,
                           derate=0.5) -> _FakePdk:
    root = tmp_dir / "pdk" / "gf180mcuD"
    lib_dir = root / "libs.ref" / run_sta.CELL_LIBRARY / "lib"
    lib_dir.mkdir(parents=True, exist_ok=True)
    (lib_dir / f"{run_sta.CELL_LIBRARY}__{corner}.lib").write_text(
        _LIBERTY_HEADER.format(lo=lo, hi=hi, derate=derate)
    )
    return _FakePdk(root)


def _write_interregion_report(tmp_dir: Path, routes: list[dict]) -> Path:
    path = tmp_dir / "interregion.json"
    path.write_text(json.dumps({"routes": routes}))
    return path


#: A synthetic report with two `digital`-facing trunks at trunk lengths that
#: do not appear anywhere in the real, committed
#: `layout/floorplan/reports/interregion.json` -- if a test against this
#: fixture ever produced the *committed* file's numbers, that would mean the
#: code path under test is not actually reading `report_path`.
_FAKE_ROUTES = [
    {
        "net": "fake_clk",
        "chip_pin": True,
        "trunk_length_um": 111.11,
        "endpoints": [
            {"region": "digital", "pin": "fake_clk"},
            {"region": "combiner_sampler", "pin": "fake_clk"},
        ],
    },
    {
        "net": "fake_bus",
        "chip_pin": False,
        "trunk_length_um": 222.22,
        "endpoints": [
            {"region": "combiner_sampler", "pin": "fake_bus"},
            {"region": "digital", "pin": "fake_bus[3]"},
        ],
    },
    {
        # Not digital-facing at all -- must be excluded.
        "net": "ring_only",
        "chip_pin": False,
        "trunk_length_um": 999.99,
        "endpoints": [
            {"region": "ring1", "pin": "ro"},
            {"region": "combiner_sampler", "pin": "rn1"},
        ],
    },
]

#: The convention every `gf180mcu_fd_sc_mcu9t5v0` deck declares.
_GF180_CONVENTION = run_sta.SlewConvention(lower_pct=30.0, upper_pct=70.0, derate=0.5)


class DigitalFacingTrunksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.report_path = _write_interregion_report(Path(self.tmp.name), _FAKE_ROUTES)

    def test_reads_synthetic_report_not_the_committed_one(self):
        """A synthetic report with fabricated lengths must be reflected
        verbatim -- proves this is a live read of `report_path`, not a
        memorized/hardcoded table."""
        trunks = run_sta.digital_facing_trunks(self.report_path)
        by_net = {t.net: t for t in trunks}
        self.assertEqual(set(by_net), {"fake_clk", "fake_bus"})
        self.assertEqual(by_net["fake_clk"].trunk_length_um, 111.11)
        self.assertEqual(by_net["fake_bus"].trunk_length_um, 222.22)
        # Neither fabricated length nor the excluded route's length collides
        # with anything the real interregion.json contains, by construction.
        real = json.loads(run_sta.INTERREGION_REPORT.read_text())
        real_lengths = {r["trunk_length_um"] for r in real["routes"]}
        self.assertNotIn(111.11, real_lengths)
        self.assertNotIn(222.22, real_lengths)

    def test_excludes_routes_with_no_digital_endpoint(self):
        trunks = run_sta.digital_facing_trunks(self.report_path)
        self.assertNotIn("ring_only", {t.net for t in trunks})

    def test_def_pin_from_endpoint_not_from_net_name(self):
        """`fake_bus`'s DEF pin is bus-notation (`fake_bus[3]`), read off the
        `digital` endpoint's own `pin` field -- exactly the mismatch the DEF's
        real `ring_bit[0]`/`ring_bit[1]` pins have against the interregion
        net names `ring_bit1`/`ring_bit2`."""
        trunks = run_sta.digital_facing_trunks(self.report_path)
        by_net = {t.net: t for t in trunks}
        self.assertEqual(by_net["fake_bus"].def_pin, "fake_bus[3]")
        self.assertEqual(by_net["fake_clk"].def_pin, "fake_clk")

    def test_chip_pin_flag_is_carried_through(self):
        trunks = run_sta.digital_facing_trunks(self.report_path)
        by_net = {t.net: t for t in trunks}
        self.assertTrue(by_net["fake_clk"].chip_pin)
        self.assertFalse(by_net["fake_bus"].chip_pin)


class InterfaceTrunkArithmeticTests(unittest.TestCase):
    """Cross-check `InterfaceTrunk`'s derived properties against DR-0025's
    own worked numbers for the real, committed six trunks (spec/decision-
    records/DR-0025-full-chip-pex-scope.md's table), not just against the
    formula restated."""

    def test_matches_dr0025_estimates_for_the_committed_six(self):
        # (net, DR-0025's own quoted estimate C in fF, R in ohm)
        expected = {
            "raw_bit": (30.8, 157),
            "raw_valid": (26.2, 134),
            "clk": (20.7, 106),
            "ring_bit1": (20.1, 103),
            "rst_n": (19.9, 102),
            "ring_bit2": (15.6, 80),
        }
        trunks = {t.net: t for t in run_sta.digital_facing_trunks()}
        self.assertEqual(set(trunks), set(expected))
        for net, (c_ff, r_ohm) in expected.items():
            trunk = trunks[net]
            self.assertAlmostEqual(trunk.cap_fF, c_ff, delta=0.1)
            self.assertAlmostEqual(trunk.res_ohm, r_ohm, delta=1.0)

    def test_rc_is_a_time_in_ns(self):
        """1 ohm * 1 fF is 1e-15 s, i.e. 1e-6 ns."""
        trunk = run_sta.InterfaceTrunk("n", "p", False, 100.0)
        self.assertAlmostEqual(
            trunk.rc_ns, 1e-6 * trunk.res_ohm * trunk.cap_fF, places=12
        )

    def test_transition_uses_the_decks_own_convention(self):
        """30/70 % with derate 0.5 is ln(7/3)/0.5 ~= 1.6946 * R * C -- and a
        deck declaring 10/90 % with no derate gets the ln(9) figure instead,
        from the same trunk. The convention is read, not assumed."""
        trunk = run_sta.InterfaceTrunk("n", "p", False, 500.0)
        self.assertAlmostEqual(_GF180_CONVENTION.rc_factor, 1.694596, places=5)
        self.assertAlmostEqual(
            trunk.transition_ns(_GF180_CONVENTION),
            1.694596 * trunk.rc_ns,
            places=8,
        )
        ten_ninety = run_sta.SlewConvention(lower_pct=10.0, upper_pct=90.0, derate=1.0)
        self.assertAlmostEqual(
            trunk.transition_ns(ten_ninety), trunk.transition_10_90_ns, places=12
        )

    def test_10_90_reference_is_ln9_rc(self):
        trunk = run_sta.InterfaceTrunk("n", "p", False, 300.0)
        self.assertAlmostEqual(
            trunk.transition_10_90_ns, 2.1972246 * trunk.rc_ns, places=10
        )

    def test_transition_is_positive_and_scales_with_length_squared(self):
        short = run_sta.InterfaceTrunk("n", "p", False, 100.0)
        long = run_sta.InterfaceTrunk("n", "p", False, 500.0)
        self.assertGreater(short.transition_ns(_GF180_CONVENTION), 0.0)
        # RC scales as length^2 (both R and C are linear in length), so a 5x
        # longer trunk must be a great deal worse, never better or equal.
        self.assertGreater(
            long.transition_ns(_GF180_CONVENTION),
            short.transition_ns(_GF180_CONVENTION) * 20,
        )

    def test_ring_bit_pin_names_are_bus_notation(self):
        """The DEF's real pin names for these two nets (verified against
        `layout/digital/trng_top.def`'s own `PINS` section) are bus notation,
        not the interregion net name -- a `get_ports` built from the net name
        directly would silently match nothing."""
        trunks = {t.net: t for t in run_sta.digital_facing_trunks()}
        self.assertEqual(trunks["ring_bit1"].def_pin, "ring_bit[0]")
        self.assertEqual(trunks["ring_bit2"].def_pin, "ring_bit[1]")


class SlewConventionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _lib(self, **kwargs) -> Path:
        path = Path(self.tmp.name) / "synthetic.lib"
        path.write_text(_LIBERTY_HEADER.format(**kwargs))
        return path

    def test_reads_thresholds_and_derate_from_the_deck(self):
        conv = run_sta.liberty_slew_convention(self._lib(lo=20, hi=80, derate=0.25))
        self.assertEqual((conv.lower_pct, conv.upper_pct, conv.derate), (20, 80, 0.25))

    def test_missing_attribute_raises_rather_than_defaulting(self):
        """A silent default here would put an unsourced constant into every
        recorded result."""
        path = Path(self.tmp.name) / "nothresholds.lib"
        path.write_text("library (x) {\n  time_unit : 1ns ;\n}\n")
        with self.assertRaises(run_sta.StaError):
            run_sta.liberty_slew_convention(path)

    def test_the_committed_gf180_decks_declare_30_70_and_derate_half(self):
        """Skipped without a PDK install: this is the one assertion here that
        is about the real decks rather than the parser."""
        pdk = run_sta.resolve_pdk()
        if pdk is None:
            self.skipTest("no gf180mcu PDK install found")
        for corner in run_sta.LIBERTY_CORNERS:
            path = run_sta.liberty_path(pdk, corner)
            if not path.is_file():
                self.skipTest(f"liberty deck {path.name} not installed")
            conv = run_sta.liberty_slew_convention(path)
            self.assertEqual(
                (conv.lower_pct, conv.upper_pct, conv.derate), (30.0, 70.0, 0.5),
                f"{corner} declares a different slew convention",
            )


class TclGenerationTests(unittest.TestCase):
    """`_tcl()` formats path strings and reads exactly one file -- the corner's
    liberty deck, for its slew convention -- so it can run with a synthetic
    PDK tree and no `openroad`."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)
        self.report_path = _write_interregion_report(self.tmp_path, _FAKE_ROUTES)
        self._orig_report = run_sta.INTERREGION_REPORT
        run_sta.INTERREGION_REPORT = self.report_path
        self.addCleanup(setattr, run_sta, "INTERREGION_REPORT", self._orig_report)
        self.corner = run_sta.Corner(liberty="tt_025C_3v30", rc="nom")
        self.pdk = _fake_pdk_with_liberty(self.tmp_path, self.corner.liberty)

    def _tcl(self) -> str:
        return run_sta._tcl(
            pdk=self.pdk, corner=self.corner, period_ns=50.0,
            spef_path=self.tmp_path / "x.spef", bisect=False,
        )

    def test_emits_set_input_transition_per_trunk(self):
        text = self._tcl()
        trunks = run_sta.digital_facing_trunks(self.report_path)
        self.assertEqual(len(trunks), 2)
        for trunk in trunks:
            expected = (
                f"set_input_transition {trunk.transition_ns(_GF180_CONVENTION):.6f} "
                f"[get_ports {{{trunk.def_pin}}}]"
            )
            self.assertIn(expected, text)

    def test_stated_transition_follows_the_decks_convention(self):
        """The same trunk against a deck declaring 10/90 % and no derate must
        be stated as a different number -- otherwise the factor is hardcoded
        somewhere rather than read."""
        pdk_10_90 = _fake_pdk_with_liberty(
            self.tmp_path / "alt", self.corner.liberty, lo=10, hi=90, derate=1.0
        )
        text = run_sta._tcl(
            pdk=pdk_10_90, corner=self.corner, period_ns=50.0,
            spef_path=self.tmp_path / "x.spef", bisect=False,
        )
        trunk = run_sta.digital_facing_trunks(self.report_path)[0]
        self.assertIn(f"set_input_transition {trunk.transition_10_90_ns:.6f} ", text)
        self.assertNotIn(
            f"set_input_transition {trunk.transition_ns(_GF180_CONVENTION):.6f} ", text
        )

    def test_never_emits_set_load_for_interface_load_ports(self):
        """`set_load` on an unconstrained top-level input port with no
        `set_driving_cell` is a no-op (see `sdc_treatment_probe.py`) -- this
        locks in that the generated SDC does not regress to it."""
        import re

        text = self._tcl()
        for trunk in run_sta.digital_facing_trunks(self.report_path):
            pattern = re.compile(
                r"^set_load\b.*\[get_ports\s*\{?" + re.escape(trunk.def_pin) + r"\}?\]",
                re.M,
            )
            self.assertIsNone(
                pattern.search(text),
                f"unexpected set_load on interface-load port {trunk.def_pin!r}",
            )

    def test_max_slew_checks_are_reported(self):
        text = self._tcl()
        self.assertIn("report_check_types -max_slew -violators", text)
        self.assertIn("STA_MAX_SLEW_VIOLATORS_BEGIN", text)
        self.assertIn("STA_MAX_SLEW_VIOLATORS_END", text)
        self.assertIn("STA_METRIC max_slew_limit_ns", text)
        self.assertIn("STA_METRIC max_slew_slack_ns", text)
        self.assertIn("STA_METRIC max_slew_violations", text)

    def test_emits_the_trunk_nets_pin_list(self):
        """The by-net attribution in `interface_load_max_slew_violations()`
        needs OpenSTA's own pin list for each trunk net."""
        text = self._tcl()
        for trunk in run_sta.digital_facing_trunks(self.report_path):
            self.assertIn(f"get_pins -of_objects [get_nets {{{trunk.def_pin}}}]", text)
            self.assertIn(f'puts "STA_IFACE_PIN {trunk.def_pin} ', text)


class MaxSlewViolatorParsingTests(unittest.TestCase):
    _TRUNKS = [
        run_sta.InterfaceTrunk("clk", "clk", True, 353.78),
        run_sta.InterfaceTrunk("raw_bit", "raw_bit", False, 524.77),
    ]

    def test_parses_violator_pin_names(self):
        log = (
            "some preamble\n"
            "STA_MAX_SLEW_VIOLATORS_BEGIN\n"
            "max slew\n\n"
            "Pin u_interface/_2227_/S ^\n"
            "max slew    6.00\n"
            "slew        7.13\n"
            "----------------\n"
            "Slack      -1.13 (VIOLATED)\n"
            "STA_MAX_SLEW_VIOLATORS_END\n"
            "trailer\n"
        )
        self.assertEqual(
            run_sta._parse_max_slew_violators(log), {"u_interface/_2227_/S"}
        )

    def test_empty_block_is_not_a_violation(self):
        log = "STA_MAX_SLEW_VIOLATORS_BEGIN\nSTA_MAX_SLEW_VIOLATORS_END\n"
        self.assertEqual(run_sta._parse_max_slew_violators(log), set())

    def test_missing_block_is_not_a_violation(self):
        self.assertEqual(run_sta._parse_max_slew_violators("no markers here"), set())

    def test_parses_the_trunk_net_pin_lists(self):
        log = (
            "STA_IFACE_PIN clk clkbuf_0_clk/I\n"
            "STA_IFACE_PIN raw_bit u_interface/_2577_/I1\n"
            "STA_IFACE_PIN raw_bit u_interface/_2491_/I1\n"
        )
        self.assertEqual(
            run_sta._parse_iface_pins(log),
            {
                "clk": {"clkbuf_0_clk/I"},
                "raw_bit": {"u_interface/_2577_/I1", "u_interface/_2491_/I1"},
            },
        )

    def test_violation_at_a_load_pin_is_attributed_to_its_trunk(self):
        """The false negative this attribution exists to avoid: OpenSTA names
        the *load* pins of an over-slewed net, never the input port that
        stated the slew, so matching port names against the violator list
        alone would report zero violations for a violating trunk."""
        log = (
            "STA_IFACE_PIN raw_bit u_interface/_2577_/I1\n"
            "STA_IFACE_PIN clk clkbuf_0_clk/I\n"
            "STA_MAX_SLEW_VIOLATORS_BEGIN\n"
            "Pin u_interface/_2577_/I1 ^\n"
            "Slack -0.10 (VIOLATED)\n"
            "STA_MAX_SLEW_VIOLATORS_END\n"
        )
        self.assertEqual(
            run_sta.interface_load_max_slew_violations(log, self._TRUNKS),
            {"raw_bit"},
        )

    def test_violation_on_an_unrelated_pin_is_not_attributed_to_a_trunk(self):
        log = (
            "STA_IFACE_PIN raw_bit u_interface/_2577_/I1\n"
            "STA_MAX_SLEW_VIOLATORS_BEGIN\n"
            "Pin u_health_test/_9_/Z ^\n"
            "Slack -0.10 (VIOLATED)\n"
            "STA_MAX_SLEW_VIOLATORS_END\n"
        )
        self.assertEqual(
            run_sta.interface_load_max_slew_violations(log, self._TRUNKS), set()
        )

    def test_a_violation_named_at_the_port_itself_still_counts(self):
        log = (
            "STA_MAX_SLEW_VIOLATORS_BEGIN\n"
            "Pin clk ^\n"
            "Slack -0.5 (VIOLATED)\n"
            "STA_MAX_SLEW_VIOLATORS_END\n"
        )
        self.assertEqual(
            run_sta.interface_load_max_slew_violations(log, self._TRUNKS), {"clk"}
        )


if __name__ == "__main__":
    unittest.main()
