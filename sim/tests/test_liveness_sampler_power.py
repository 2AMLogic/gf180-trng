#!/usr/bin/env python3
"""Offline tests for the liveness-sampler active-power term (issue #463).

No ngspice, no PDK, no ``klt``, no network. They cover:

1. the whole-block ledger inventory: every instance ``design/sampler_core.spice``
   instantiates maps to exactly one required ledger term, a ledger that drops
   the liveness term is REJECTED (a missing term), and one that claims an
   instance twice is REJECTED (double counting);
2. the liveness arithmetic on synthetic raw charges where the answer is known by
   construction (clock subtraction, sign convention, array-loading delta);
3. the committed request matching the declared grid, and the deck restating the
   shipped sampler_core wiring port for port;
4. the committed measured record re-derived from its own raw report slice, so
   a record can never disagree with the arithmetic that claims to produce it;
5. the idle scope (whole ``sampler_core``) and that ``--with-taps`` never adds
   the historical liveness constant on top of the shipped term.
"""

from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
import json
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR / "tools"))

import liveness_sampler_power as lsp  # noqa: E402
import power_rollup as pr  # noqa: E402

DECK = SIM_DIR / "tb" / "sampler-core-liveness-active" / lsp.DECK


def raw_measurements(*, q_sr=1.0e-13, q_sv=2.0e-14, q_arr=6.0e-11, q_ctl=5.8e-11,
                     window=2.6e-8, vdd=3.3) -> dict[str, float]:
    """Raw .meas values (volts on the 1 nF integrators, negative as the sense
    sources report charge delivered) for one synthetic unit."""
    v: dict[str, float] = {}
    for win in ("1", "2", "c1", "c2"):
        v[f"t{win}a"] = 1.0e-8
        v[f"t{win}b"] = 1.0e-8 + window

    def put(node: str, win: str, q: float) -> None:
        v[f"{node}_{win}a"] = 0.0
        v[f"{node}_{win}b"] = -q / lsp.CQ

    for node, win in lsp.CHARGES:
        if node in ("qs1", "qs2"):
            q = q_sr
        elif node == "qsv":
            q = q_sv
        elif node in ("q1", "q2", "qt"):
            q = q_arr
        elif node in ("cq1i", "cq2i", "cqt"):
            q = q_ctl
        else:
            q = 1e-14
        put(node, win, q)
    return v


class DerivationTests(unittest.TestCase):
    def test_clock_term_is_removed_by_the_in_run_xsv_subtraction(self):
        v = raw_measurements(q_sr=1.0e-13, q_sv=2.0e-14, window=2.0e-8)
        d = lsp.derive(v, 3.3, q_clk_c=8e-15)
        self.assertAlmostEqual(d["q_data1_c"], 8.0e-14)
        self.assertAlmostEqual(d["q_per_transition1_c"], 8.0e-14 / 8)
        self.assertAlmostEqual(d["i_data_a"], 2 * 8.0e-14 / 2.0e-8)

    def test_power_is_vdd_times_data_plus_two_clock_terms(self):
        v = raw_measurements(window=2.0e-8)
        d = lsp.derive(v, 3.0, q_clk_c=8e-15)
        want = 3.0 * (d["i_data_a"] + 2 * 1e6 * 8e-15)
        self.assertAlmostEqual(lsp.live_power(d, 1e6), want)
        # the data term does not move with the sample clock; only the clock term does
        self.assertGreater(lsp.live_power(d, 2e6), lsp.live_power(d, 1e6))
        self.assertAlmostEqual(lsp.live_power(d, 2e6) - lsp.live_power(d, 1e6), 3.0 * 2 * 1e6 * 8e-15)

    def test_loading_delta_is_tapped_minus_control_and_signed(self):
        v = raw_measurements(q_arr=6.0e-11, q_ctl=5.8e-11, window=2.0e-8)
        d = lsp.derive(v, 3.3, q_clk_c=8e-15)
        self.assertAlmostEqual(d["dp_load_w"], 3.3 * 3 * (6.0e-11 - 5.8e-11) / 2.0e-8)
        v = raw_measurements(q_arr=5.8e-11, q_ctl=6.0e-11, window=2.0e-8)
        self.assertLess(lsp.derive(v, 3.3, q_clk_c=8e-15)["dp_load_w"], 0)

    def test_missing_raw_measurement_is_rejected_not_defaulted(self):
        v = raw_measurements()
        del v["qs1_1b"]
        with self.assertRaises(lsp.DerivationError):
            lsp.derive(v, 3.3)

    def test_degenerate_window_is_rejected(self):
        v = raw_measurements()
        v["t1b"] = v["t1a"]
        with self.assertRaises(lsp.DerivationError):
            lsp.derive(v, 3.3)

    def test_a_sampler_that_draws_no_more_than_tied_d_is_flagged(self):
        d = lsp.derive(raw_measurements(q_sr=1.0e-14, q_sv=2.0e-14), 3.3, q_clk_c=8e-15)
        self.assertTrue(lsp.checks(d))

    def test_every_derived_input_is_requested_from_the_simulator(self):
        names = {m["name"] for m in lsp.measurements()}
        needed = set(raw_measurements())
        self.assertLessEqual(needed, names, "derive() reads a name the request never measures")


class GridTests(unittest.TestCase):
    def test_committed_request_matches_the_declared_grid(self):
        self.assertEqual(lsp.cmd_emit(check=True), 0)

    def test_grid_is_the_27_point_pvt_grid(self):
        req = lsp.build_request()
        procs = [p["name"] for p in req["corners"]["process"]]
        self.assertEqual(sorted(procs), ["ff", "ss", "tt"])
        self.assertEqual(lsp.n_units(), 27)

    def test_only_selects_a_single_declared_point(self):
        req = lsp.build_request("ff/-40/3.63")
        self.assertEqual([p["name"] for p in req["corners"]["process"]], ["ff"])
        self.assertEqual(req["corners"]["temperature_c"], [-40])
        self.assertEqual(req["corners"]["supply_v"]["vsupply"], [3.63])
        with self.assertRaises(ValueError):
            lsp.build_request("ff/-40/3.00")

    def test_a_local_run_of_the_whole_grid_is_refused(self):
        self.assertEqual(lsp.cmd_run("/nonexistent-never-created", "local", "klt"), 2)


class DeckWiringTests(unittest.TestCase):
    """The deck restates sampler_core's wiring to split supplies; pin it."""

    @staticmethod
    def instances(text: str) -> dict[str, list[str]]:
        return {ln.split()[0]: ln.split() for ln in text.splitlines()
                if re.match(r"^x(sb|sv|sr1|sr2|dut)\b", ln)}

    def test_deck_instances_match_the_shipped_netlist(self):
        ship = self.instances((REPO_ROOT / "design" / "sampler_core.spice").read_text())
        deck = self.instances(DECK.read_text())
        for inst in ("xsb", "xsv", "xsr1", "xsr2", "xdut"):
            self.assertIn(inst, deck)
            self.assertEqual(deck[inst][-1], ship[inst][-1], f"{inst}: different cell")
        # data inputs: the nets the shipped design feeds each flop
        self.assertEqual(deck["xsb"][1], ship["xsb"][1])      # xo
        self.assertEqual(deck["xsr1"][1], ship["xsr1"][1])    # ro1
        self.assertEqual(deck["xsr2"][1], ship["xsr2"][1])    # ro2
        # xsv: D and its supply pin are one net in both
        self.assertEqual(deck["xsv"][1], deck["xsv"][5])
        self.assertEqual(ship["xsv"][1], ship["xsv"][5])
        # output nets of the array
        self.assertEqual(deck["xdut"][7:10], ship["xdut"][7:10])


class InventoryTests(unittest.TestCase):
    def test_every_shipped_instance_has_exactly_one_required_term(self):
        inv = pr.inventory_check(pr.shipped_instances())
        self.assertEqual(pr.inventory_problems(inv), [])
        for inst in ("xdut", "xsb", "xsv", "xsr1", "xsr2"):
            self.assertEqual(len(inv["mapping"][inst]), 1, inst)

    def test_the_liveness_flops_are_shipped_and_required(self):
        insts = pr.shipped_instances()
        self.assertEqual(insts["xsr1"], "sampler_dff")
        self.assertEqual(insts["xsr2"], "sampler_dff")
        term = next(t for t in pr.LEDGER_TERMS if t["name"] == "liveness")
        self.assertTrue(term["required"])
        self.assertEqual(set(term["covers"]), {"xsr1", "xsr2"})

    def test_a_ledger_missing_the_liveness_term_is_rejected(self):
        terms = [t for t in pr.LEDGER_TERMS if t["name"] != "liveness"]
        inv = pr.inventory_check(pr.shipped_instances(), terms)
        self.assertEqual(inv["uncovered"], ["xsr1", "xsr2"])
        self.assertTrue(pr.inventory_problems(inv))

    def test_an_optional_term_does_not_count_as_coverage(self):
        terms = [dict(t, required=False) if t["name"] == "liveness" else t for t in pr.LEDGER_TERMS]
        self.assertEqual(pr.inventory_check(pr.shipped_instances(), terms)["uncovered"], ["xsr1", "xsr2"])

    def test_double_counting_an_instance_is_detected(self):
        terms = list(pr.LEDGER_TERMS) + [
            {"name": "all_samplers", "covers": ("xsb", "xsv", "xsr1", "xsr2"), "required": True, "evidence": "x"}]
        inv = pr.inventory_check(pr.shipped_instances(), terms)
        self.assertEqual(sorted(inv["double_counted"]), ["xsb", "xsr1", "xsr2", "xsv"])
        self.assertTrue(pr.inventory_problems(inv))

    def test_a_stale_cover_naming_no_instance_is_detected(self):
        terms = list(pr.LEDGER_TERMS) + [
            {"name": "ghost", "covers": ("xsr3",), "required": True, "evidence": "x"}]
        self.assertEqual(pr.inventory_check(pr.shipped_instances(), terms)["unknown"], ["ghost:xsr3"])

    def test_a_new_cell_in_the_netlist_is_reported_uncovered(self):
        insts = dict(pr.shipped_instances(), xsr3="sampler_dff")
        self.assertEqual(pr.inventory_check(insts)["uncovered"], ["xsr3"])

    def test_check_fails_on_an_uncovered_instance(self):
        # --check wires inventory_problems into its exit status
        src = (SIM_DIR / "tools" / "power_rollup.py").read_text()
        self.assertIn("problems += inventory_problems(inv)", src)


class IdleScopeAndTapsTests(unittest.TestCase):
    def test_the_idle_measurement_spans_the_whole_sampler_core(self):
        self.assertEqual(pr.IDLE_SCOPE, "sampler_core")
        deck = (SIM_DIR / "tb" / "sampler-core-idle-leakage" / "tb_sampler_core_idle_leakage.sp").read_text()
        self.assertRegex(deck, r"(?m)^xdutA .* sampler_core$")
        self.assertRegex(deck, r"(?m)^xdutB .* sampler_core$")

    def test_no_liveness_constant_is_added_to_any_total(self):
        self.assertFalse(hasattr(pr, "TAP_LIVENESS_W"))
        self.assertEqual(pr.HISTORICAL_TAP_LIVENESS_W, 81.3e-6)
        src = (SIM_DIR / "tools" / "power_rollup.py").read_text()
        uses = [ln for ln in src.splitlines() if "HISTORICAL_TAP_LIVENESS_W" in ln and "+=" in ln]
        self.assertEqual(uses, [])

    def test_with_taps_adds_only_the_metastability_hybrid(self):
        def worst(*extra: str) -> float:
            out = subprocess.run([sys.executable, str(SIM_DIR / "tools" / "power_rollup.py"), "--no-digital", *extra],
                                 capture_output=True, text=True, check=True).stdout
            m = re.search(r"Worst active corner: \S+\s+-> ([\d.]+) uW", out)
            return float(m.group(1))
        self.assertAlmostEqual(worst("--with-taps") - worst(), pr.TAP_META_W * 1e6, delta=0.2)

    def test_attempt_records_can_never_be_read_as_a_measured_corner(self):
        self.assertFalse(fnmatch.fnmatch("2026-10-10-sampler-core-liveness-active-attempt-01.md", pr.LIVENESS_GLOB))
        self.assertTrue(fnmatch.fnmatch("2026-10-10-sampler-core-liveness-active-01.md", pr.LIVENESS_GLOB))


class LedgerTermTests(unittest.TestCase):
    class _Rec:
        def __init__(self, values, vdd):
            self.values, self.vdd, self.stem = values, vdd, "fake"

    def test_flops_and_array_loading_are_separate_and_sum_once(self):
        rec = self._Rec({"i_data_a": 6e-6, "dp_load_w": -2e-6}, 3.0)
        out = pr.liveness_active(rec, 1e6, 8e-15)
        self.assertAlmostEqual(out["p_flops_w"], 3.0 * (6e-6 + 2 * 1e6 * 8e-15))
        self.assertAlmostEqual(out["dp_load_w"], -2e-6)
        self.assertAlmostEqual(out["p_total_w"], out["p_flops_w"] + out["dp_load_w"])

    def test_rollup_and_tool_agree_on_the_flop_power(self):
        v = raw_measurements(window=2.0e-8)
        d = lsp.derive(v, 3.3, q_clk_c=8e-15)
        rec = self._Rec({"i_data_a": d["i_data_a"], "dp_load_w": d["dp_load_w"]}, 3.3)
        self.assertAlmostEqual(pr.liveness_active(rec, 1e6, 8e-15)["p_flops_w"], lsp.live_power(d, 1e6))


class CommittedRecordTests(unittest.TestCase):
    def test_measured_records_rederive_from_their_own_raw_slice(self):
        recs = sorted((SIM_DIR / "records").glob(pr.LIVENESS_GLOB))
        self.assertTrue(recs, "no measured liveness record is committed")
        for path in recs:
            with self.subTest(record=path.stem):
                rec = pr.Record(path)
                raw = SIM_DIR / "records" / "raw" / path.stem / "report-unit.json"
                unit = json.loads(raw.read_text())["corner"]
                row = lsp.analyse_report({"corners": [unit]})[0]
                self.assertEqual(row["verdict"], "OK", row.get("problems"))
                self.assertEqual(rec.corner, row["corner"].rsplit("/", 1)[0] + "/" + f"{row['vdd']:.2f}")
                for key in lsp.RECORD_FIELDS:
                    self.assertAlmostEqual(rec.values[key] / row[key], 1.0, places=5, msg=key)
                self.assertGreater(rec.values["i_data_a"], 0)

    def test_the_rollup_reads_the_committed_record(self):
        lives = pr.by_corner(pr.load(pr.LIVENESS_GLOB))
        self.assertGreaterEqual(len(lives), 1)
        for corner, rec in lives.items():
            self.assertEqual(rec.corner, corner)
            out = pr.liveness_active(rec, 1e6, 8e-15)
            self.assertGreater(out["p_flops_w"], 0)


if __name__ == "__main__":
    unittest.main()
