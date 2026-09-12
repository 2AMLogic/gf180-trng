#!/usr/bin/env python3
"""Unit tests for ``sim/tb/digital-sta-power/max_transition_probe.py`` (#237).

The probe itself needs ``openroad`` and the gf180mcu PDK; everything it does
*with* what OpenROAD returns does not, and that half is what decides
``sim/characterization-digital-sta-area-power.md`` section 2a's verdict. So
this file covers, with neither tool installed:

1. **Parsing.** A violating pin is attributed to its net, per-net driver and
   load-count metadata is carried through, the worst setup slack of a path
   *through* a violating pin is read off ``report_checks``' own summary
   format, and the violating instances' power share is the ratio of two
   separately-delimited ``report_power`` blocks -- not of one block parsed
   twice.
2. **The derived constraint.** ``pnr_corner_target()`` is the arithmetic
   behind the one actionable number section 2a quotes (the
   ``set_max_transition`` the place-and-route corner would have to state for
   every corner to come out clean). It is checked here against a synthetic
   grid whose answer is known by construction, so a regression in it cannot
   hide behind the committed design's own numbers.
3. **The gate.** ``check()`` has to fail for each distinct way the accepted
   residual could stop being the accepted residual -- a new net, a trunk-net
   hit, a path that stops closing, a growing power share, a moved sibling
   check -- and has to pass when none of them happened. Each is exercised
   separately, because a gate that only fails "somehow" cannot tell a
   reviewer which assumption broke.

The probe's *measurements* (that OpenSTA names those pins at those corners at
all) are gated by ``max_transition_probe.py --check``, which needs the PDK and
so cannot run here -- the same split ``test_run_sta_interface_load.py`` draws
against ``sdc_treatment_probe.py --check``.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

TB_DIR = Path(__file__).resolve().parents[1] / "tb" / "digital-sta-power"
SIM_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(TB_DIR))

import max_transition_probe as probe  # noqa: E402


def _log(
    *,
    limit: float = 6.0,
    slack: float = -1.5930,
    violations: int = 3,
    setup_s: float = 35.853504e-9,
    hold_s: float = 1.234e-9,
    pins: tuple[tuple[str, str], ...] = (
        ("u_interface/_2227_/S", "u_interface/_1190_"),
        ("u_interface/_2228_/S", "u_interface/_1190_"),
        ("u_conditioner/_300_/A1", "u_conditioner/_095_"),
    ),
    nets: tuple[tuple[str, int, str, str], ...] = (
        ("u_interface/_1190_", 33, "u_interface/_2212_/ZN",
         "gf180mcu_fd_sc_mcu9t5v0__nor2_2"),
        ("u_conditioner/_095_", 14, "u_conditioner/_209_/ZN",
         "gf180mcu_fd_sc_mcu9t5v0__xnor2_1"),
    ),
    through: bool = True,
    instance_w: tuple[float, ...] = (1.0e-5, 5.0e-6),
    total_w: float = 1.0e-3,
    cap_violations: int = 5,
    max_fanout: int = 201,
) -> str:
    """One OpenROAD log in exactly the shape ``_tcl()`` produces."""
    lines = [
        "OpenROAD 26Q3-1510-g6cb3f2b704 ",
        f"PROBE max_slew_limit_ns {limit}",
        f"PROBE max_slew_slack_ns {slack}",
        f"PROBE max_slew_violations {violations}",
        f"PROBE worst_setup_slack_s {setup_s}",
        f"PROBE worst_hold_slack_s {hold_s}",
        f"PROBE max_capacitance_violations {cap_violations}",
        "PROBE max_capacitance_limit 0.3869999945163727",
        "PROBE max_capacitance_slack -0.13743992149829865",
        f"PROBE max_net_fanout {max_fanout}",
        "PROBE nets_over_fanout_threshold 77",
        "PROBE_MAXFANOUTNET rst_n",
        f"PROBE violator_pins_parsed {len(pins)}",
    ]
    lines += [f"PROBE_PIN {pin} net {net}" for pin, net in pins]
    lines += [
        f"PROBE_NET {net} pins {count} driver {driver} master {master}"
        for net, count, driver, master in nets
    ]
    lines.append("PROBE_THROUGH_BEGIN")
    if through:
        lines += [
            "Startpoint                           Endpoint            Slack",
            "--------------------------------------------------------------",
            "u_interface/_2847_/Q (gf180mcu_fd_sc_mcu9t5v0__dffq_1) "
            f"u_interface/_2606_/D (gf180mcu_fd_sc_mcu9t5v0__dffq_1)   "
            f"{setup_s * 1e9:.6f}",
            "",
        ]
    lines.append("PROBE_THROUGH_END")
    lines.append(f"PROBE violating_instances {len(instance_w)}")
    lines.append("PROBE_POWER_BEGIN")
    if instance_w:
        lines += [
            "         Internal        Switching          Leakage            Total",
            "            Power            Power            Power            Power (Watts)",
            "--------------------------------------------------------------------",
        ]
        for i, w in enumerate(instance_w):
            lines.append(
                f" 1.0000000000e-07 1.0000000000e-07 1.0000000000e-11 "
                f"{w:.10e} u_inst/_{i:04d}_"
            )
    lines.append("PROBE_POWER_END")
    lines += [
        "PROBE_TOTALPOWER_BEGIN",
        "Group                        Internal        Switching          Leakage            Total",
        "----------------------------------------------------------------------------",
        f"Total                5.0000000000e-04 5.0000000000e-04 1.0000000000e-08 "
        f"{total_w:.10e} 100.0%",
        "PROBE_TOTALPOWER_END",
    ]
    return "\n".join(lines) + "\n"


class ParseTests(unittest.TestCase):
    def test_worst_slew_is_limit_minus_slack(self):
        # OpenSTA reports slack; the slew is what scales across corners, and
        # the whole pnr_corner_target derivation is built on it.
        got = probe.parse(_log(limit=6.0, slack=-1.5930))
        self.assertAlmostEqual(got["worst_slew_ns"], 7.5930, places=6)

    def test_violating_pins_are_counted_per_net(self):
        got = probe.parse(_log())
        by_net = {n["net"]: n for n in got["nets"]}
        self.assertEqual(by_net["u_interface/_1190_"]["violating_pins"], 2)
        self.assertEqual(by_net["u_conditioner/_095_"]["violating_pins"], 1)

    def test_net_metadata_is_carried_through(self):
        by_net = {n["net"]: n for n in probe.parse(_log())["nets"]}
        entry = by_net["u_interface/_1190_"]
        self.assertEqual(entry["pins_on_net"], 33)
        self.assertEqual(entry["driver_pin"], "u_interface/_2212_/ZN")
        self.assertEqual(entry["driver_master"],
                         "gf180mcu_fd_sc_mcu9t5v0__nor2_2")

    def test_nets_are_ordered_by_load_count(self):
        nets = probe.parse(_log())["nets"]
        self.assertEqual([n["pins_on_net"] for n in nets], [33, 14])

    def test_through_slack_is_read_from_the_summary_row(self):
        got = probe.parse(_log(setup_s=35.853504e-9))
        self.assertAlmostEqual(
            got["worst_setup_slack_through_violators_ns"], 35.853504, places=6
        )

    def test_a_clean_corner_reports_no_through_path_rather_than_zero(self):
        # None, not 0.0: "no path through a violating pin" and "a path with
        # zero slack" are opposite findings and must not share an encoding.
        got = probe.parse(_log(violations=0, pins=(), nets=(), through=False,
                               instance_w=()))
        self.assertIsNone(got["worst_setup_slack_through_violators_ns"])
        self.assertEqual(got["nets"], [])
        self.assertEqual(got["violating_power_share"], 0.0)

    def test_power_share_is_instances_over_total(self):
        got = probe.parse(_log(instance_w=(1.0e-5, 5.0e-6), total_w=1.0e-3))
        self.assertAlmostEqual(got["violating_instance_power_w"], 1.5e-5)
        self.assertAlmostEqual(got["total_power_w"], 1.0e-3)
        self.assertAlmostEqual(got["violating_power_share"], 0.015)

    def test_the_total_row_is_not_read_as_an_instance_row(self):
        # The two report_power forms have the same numeric shape and differ
        # only by which block they are in; a parser that scanned the whole log
        # would fold the design total into the violating instances' sum.
        got = probe.parse(_log(instance_w=(1.0e-5,), total_w=1.0e-3))
        self.assertAlmostEqual(got["violating_instance_power_w"], 1.0e-5)

    def test_sibling_checks_are_carried_through(self):
        got = probe.parse(_log(cap_violations=5, max_fanout=201))
        self.assertEqual(got["max_capacitance_violations"], 5)
        self.assertEqual(got["max_net_fanout"], 201)
        self.assertEqual(got["max_fanout_net"], "rst_n")

    def test_a_log_with_no_metrics_is_an_error_not_an_empty_result(self):
        with self.assertRaises(probe.run_sta.StaError):
            probe.parse("OpenROAD 26Q3\nsome unrelated output\n")


def _row(liberty: str, rc: str, limit: float, slew: float) -> dict:
    return {
        "corner": {"liberty": liberty, "rc": rc, "label": f"{liberty}/rc-{rc}"},
        "max_slew_limit_ns": limit,
        "max_slew_slack_ns": limit - slew,
        "worst_slew_ns": slew,
        "max_slew_violations": 1 if slew > limit else 0,
        "worst_setup_slack_ns": 30.0,
        "worst_setup_slack_through_violators_ns": 30.0 if slew > limit else None,
        "violating_power_share": 0.01 if slew > limit else 0.0,
        "max_capacitance_violations": 0,
        "max_net_fanout": 201,
        "nets": (
            [{"net": "u_interface/_1190_", "pins_on_net": 33,
              "driver_pin": "u_interface/_2212_/ZN", "driver_master": "nor2_2",
              "violating_pins": 1}]
            if slew > limit else []
        ),
    }


class PnrCornerTargetTests(unittest.TestCase):
    def test_target_is_the_tightest_corners_scaled_requirement(self):
        # Two corners, one interconnect deck. The P&R corner produces a 10 ns
        # slew; the other produces 5 ns against a 4 ns limit, so it needs to
        # come down by 5/4 -- and the P&R corner has to come down by the same
        # factor, to 8 ns. Known by construction, not read off the design.
        rows = [
            _row(probe.PNR_CORNER, "nom", limit=13.2, slew=10.0),
            _row("ff_125C_3v60", "nom", limit=4.0, slew=5.0),
        ]
        target = probe.pnr_corner_target(rows)
        self.assertEqual(target["binding_corner"], "ff_125C_3v60/rc-nom")
        self.assertAlmostEqual(target["required_set_max_transition_ns"], 8.0)
        self.assertAlmostEqual(target["fraction_of_library_limit"], 8.0 / 13.2)

    def test_the_pnr_corner_requires_exactly_its_own_limit(self):
        rows = [_row(probe.PNR_CORNER, "nom", limit=13.2, slew=14.0)]
        target = probe.pnr_corner_target(rows)
        self.assertAlmostEqual(target["required_set_max_transition_ns"], 13.2)

    def test_corners_are_paired_within_their_own_interconnect_deck(self):
        # The parasitic corner is an axis of its own: comparing a `max`-deck
        # slew against a `min`-deck one would mix two different wire models
        # into a single ratio.
        rows = [
            _row(probe.PNR_CORNER, "min", limit=13.2, slew=10.0),
            _row(probe.PNR_CORNER, "max", limit=13.2, slew=20.0),
            _row("ff_125C_3v60", "max", limit=4.0, slew=5.0),
        ]
        target = probe.pnr_corner_target(rows)
        binding = next(r for r in target["requirements"]
                       if r["corner"] == "ff_125C_3v60/rc-max")
        self.assertAlmostEqual(binding["slew_vs_pnr_corner"], 5.0 / 20.0)
        self.assertAlmostEqual(binding["required_pnr_slew_ns"], 16.0)

    def test_no_pnr_corner_in_the_grid_yields_no_target(self):
        # A single-corner probe run has nothing to scale against; reporting a
        # target from it would be inventing the cross-corner ratio.
        self.assertEqual(
            probe.pnr_corner_target([_row("tt_025C_3v30", "max", 6.0, 7.6)]), {}
        )


def _result(rows=None, **over) -> dict:
    rows = rows if rows is not None else [
        _row(probe.PNR_CORNER, "nom", limit=13.2, slew=14.0),
        _row("tt_025C_3v30", "nom", limit=6.0, slew=7.1),
    ]
    result = {
        "corners": rows,
        "violating_nets": sorted({n["net"] for r in rows for n in r["nets"]}),
        "violating_corner_count": sum(
            1 for r in rows if r["max_slew_violations"]
        ),
        "trunk_ports": ["clk", "raw_bit", "rst_n"],
    }
    result.update(over)
    return result


class CheckTests(unittest.TestCase):
    """Each way the accepted residual can stop being the accepted residual."""

    def setUp(self) -> None:
        self._recorded = dict(probe.RECORDED)
        probe.RECORDED.update({
            "violating_nets": ("u_interface/_1190_",),
            "violating_corners": 2,
            "worst_setup_slack_through_violators_ns": 30.0,
            "power_share_max": 0.01,
            "max_capacitance_violations": 0,
            "max_net_fanout": 201,
        })

    def tearDown(self) -> None:
        probe.RECORDED.clear()
        probe.RECORDED.update(self._recorded)

    def test_the_recorded_state_passes(self):
        self.assertEqual(probe.check(_result()), [])

    def test_a_new_violating_net_fails(self):
        rows = _result()["corners"]
        rows[1]["nets"] = [dict(rows[1]["nets"][0], net="u_alu/_777_")]
        fails = probe.check(_result(rows))
        self.assertTrue(any("u_alu/_777_" in f for f in fails), fails)

    def test_a_recorded_net_that_stops_violating_also_fails(self):
        # Good news that still makes the document wrong.
        rows = [_row(probe.PNR_CORNER, "nom", limit=13.2, slew=10.0),
                _row("tt_025C_3v30", "nom", limit=6.0, slew=5.0)]
        fails = probe.check(_result(rows))
        self.assertTrue(any("no longer violate" in f for f in fails), fails)

    def test_a_violating_pin_on_a_trunk_net_fails(self):
        rows = _result()["corners"]
        rows[1]["nets"] = [dict(rows[1]["nets"][0], net="raw_bit")]
        fails = probe.check(_result(rows))
        self.assertTrue(any("trunk net" in f for f in fails), fails)

    def test_a_path_that_stops_closing_setup_fails(self):
        rows = _result()["corners"]
        rows[1]["worst_setup_slack_through_violators_ns"] = -0.5
        fails = probe.check(_result(rows))
        self.assertTrue(any("fails setup" in f for f in fails), fails)

    def test_a_grown_power_share_fails(self):
        rows = _result()["corners"]
        rows[1]["violating_power_share"] = 0.25
        fails = probe.check(_result(rows))
        self.assertTrue(any("total power" in f for f in fails), fails)

    def test_a_moved_sibling_capacitance_check_fails(self):
        rows = _result()["corners"]
        rows[0]["max_capacitance_violations"] = 9
        fails = probe.check(_result(rows))
        self.assertTrue(any("max_capacitance" in f for f in fails), fails)

    def test_a_moved_worst_fanout_fails(self):
        rows = _result()["corners"]
        for row in rows:
            row["max_net_fanout"] = 12
        fails = probe.check(_result(rows))
        self.assertTrue(any("12 loads" in f for f in fails), fails)

    def test_corners_disagreeing_on_fanout_fails_louder(self):
        # Fanout is topology: a spread across corners means the corners did
        # not read the same DEF, which invalidates every other row too.
        rows = _result()["corners"]
        rows[0]["max_net_fanout"] = 12
        fails = probe.check(_result(rows))
        self.assertTrue(any("did not all read the same DEF" in f
                            for f in fails), fails)


class RecordedTableTests(unittest.TestCase):
    """The pinned table has to describe the design this repository committed."""

    def test_the_recorded_nets_name_a_module_and_a_signal(self):
        for net in probe.RECORDED["violating_nets"]:
            self.assertIn("/", net, net)

    def test_the_recorded_residual_still_closes_setup(self):
        # The entire accepted-risk argument is that these paths have margin;
        # a RECORDED table that pinned a negative number would be pinning a
        # failure as the expected state.
        self.assertGreater(
            probe.RECORDED["worst_setup_slack_through_violators_ns"], 0.0
        )

    def test_the_pnr_corner_matches_the_build_flows_own(self):
        # `pnr_corner_target` is only meaningful if it names the deck
        # `layout/digital/build.py` actually implements at.
        build = (SIM_DIR.parent / "layout" / "digital" / "build.py").read_text()
        self.assertIn(f'CORNER = "{probe.PNR_CORNER}"', build)


if __name__ == "__main__":
    unittest.main()
