#!/usr/bin/env python3
"""Unit tests for the post-route switching-activity campaign (#453).

Everything here is pure Python: synthetic VCDs, synthetic OpenSTA output and
the behavioural model. No simulator, no OpenROAD, no PDK. The properties
held:

1. The workloads are deterministic, well-formed, and each exercises the
   mechanism it is named for (checked against the behavioural model): only
   ``alarm-gated`` raises ``ht_alarm``, its steady window opens after the
   latch, and the conditioned workloads un-gate the stream.
2. A trace that cannot be activity evidence is rejected, not downgraded: an
   empty trace, a wrong DUT scope, a trace of a different netlist, a clock
   that does not toggle as declared, an empty capture window.
3. OpenSTA annotation failure is a rejection: zero annotated pins, or too
   small a fraction, and a missing summary is a parse failure rather than
   "zero".
4. The opt-in mode does not touch the default flow: ``_tcl`` without
   ``activity_block`` still emits the uniform ``set_power_activity -global``
   and extraction; with it, the session reads the existing SPEF instead.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
TB_DIR = SIM_DIR / "tb" / "digital-sta-power"
POST_ROUTE_DIR = SIM_DIR / "tb" / "trng-top-post-route"
sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(TB_DIR))
sys.path.insert(0, str(POST_ROUTE_DIR))
sys.path.insert(0, str(SIM_DIR.parent / "design" / "trng_top"))

import activity  # noqa: E402
import activity_workloads as wl  # noqa: E402
import run_sta  # noqa: E402
import trng_top as top  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_run_sta_interface_load as _tcl_fixtures  # noqa: E402


def _model_outputs(rows):
    model = top.TopLevel()
    outs = []
    for row in rows:
        kw = {k: v for k, v in row.items() if k != "rst_n"}
        outs.append(model.step(**kw))
    return outs


class WorkloadTests(unittest.TestCase):
    def test_deterministic(self):
        for name in wl.WORKLOADS:
            a, wa = wl.build(name)
            b, wb = wl.build(name)
            self.assertEqual(wl.stimulus_sha256(a), wl.stimulus_sha256(b), name)
            self.assertEqual(wa, wb, name)

    def test_workloads_are_distinct(self):
        digests = {wl.stimulus_sha256(wl.build(n)[0]) for n in wl.WORKLOADS}
        self.assertEqual(len(digests), len(wl.WORKLOADS))

    def test_windows_partition_declared_regimes(self):
        for name in wl.WORKLOADS:
            rows, win = wl.build(name)
            self.assertEqual(set(win), {"reset", "startup", "steady"})
            self.assertEqual(win["reset"][0], 0)
            self.assertLessEqual(win["reset"][1], win["startup"][0])
            self.assertLessEqual(win["startup"][1], win["steady"][0])
            self.assertEqual(win["steady"][1], len(rows))
            # Reset is rst_n low, and only there.
            for i, r in enumerate(rows):
                self.assertEqual(r["rst_n"], 0 if i < win["reset"][1] else 1, (name, i))

    def test_startup_window_covers_the_dr0002_window(self):
        _, win = wl.build("conditioned-streaming")
        self.assertGreaterEqual(win["startup"][1] - win["startup"][0],
                                wl.sc.STARTUP_SAMPLES)

    def test_only_alarm_gated_raises_ht_alarm_and_steady_is_post_latch(self):
        for name in wl.WORKLOADS:
            rows, win = wl.build(name)
            outs = _model_outputs(rows)
            first = next((i for i, o in enumerate(outs) if o.ht_alarm), None)
            if name == "alarm-gated":
                self.assertIsNotNone(first)
                self.assertLessEqual(first, win["steady"][0])
                self.assertTrue(all(o.ht_alarm for o in outs[win["steady"][0]:]))
            else:
                self.assertIsNone(first, name)

    def test_conditioned_workloads_unlock_the_stream_and_disabled_does_not(self):
        for name, streams in (("conditioned-streaming", True), ("raw-streaming", True),
                              ("disabled-clock-running", False), ("alarm-gated", False)):
            rows, _ = wl.build(name)
            valid = any(o.str_valid for o in _model_outputs(rows))
            self.assertEqual(valid, streams, name)

    def test_backpressure_never_asserts_ready(self):
        rows, _ = wl.build("backpressure")
        self.assertFalse(any(r["str_ready"] for r in rows))

    def test_pack_row_round_trips_every_field(self):
        row = wl._row(raw_bit=1, raw_valid=True, ring_bit=(1, 0), reg_sel=True,
                      reg_write=True, reg_addr=2, reg_wdata=0xDEADBEEF, str_ready=True)
        w = wl.pack_row(row)
        self.assertEqual(w & 1, 1)
        self.assertEqual((w >> 1) & 1, 1)
        self.assertEqual((w >> 3) & 3, 1)
        self.assertEqual((w >> 7) & 3, 2)
        self.assertEqual((w >> 9) & 0xFFFFFFFF, 0xDEADBEEF)
        self.assertEqual((w >> 41) & 1, 1)


def _vcd(*, scope=("tb", "dut"), insts=("u0", "u1"), cycles=4, period=1000,
         clk=True, body=True, timescale="1ps") -> str:
    lines = ["$timescale", f"\t{timescale}", "$end"]
    for s in scope:
        lines.append(f"$scope module {s} $end")
    lines.append("$var wire 1 ! clk $end")
    lines.append('$var wire 1 " d $end')
    for i, n in enumerate(insts):
        lines.append(f"$scope module {n} $end")
        lines.append(f"$var wire 1 {chr(40 + i)} ZN $end")
        lines.append("$upscope $end")
    for _ in scope:
        lines.append("$upscope $end")
    lines.append("$enddefinitions $end")
    if body:
        lines.append("#0")
        lines.append("0!")
        lines.append('0"')
        t = 0
        for c in range(cycles):
            lines.append(f"#{t + period // 2}")
            lines.append("1!" if clk else "0!")
            lines.append(f'{c % 2}"')
            lines.append(f"#{t + period}")
            lines.append("0!")
            t += period
    return "\n".join(lines) + "\n"


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.windows = {"a": (0, 2), "b": (2, 4)}
        self.ticks = activity.windows_to_ticks(self.windows, 1.0)

    def _run(self, text, insts=("u0", "u1")):
        p = self.dir / "t.vcd"
        p.write_text(text)
        s = activity.summarize_vcd(p, self.ticks)
        return activity.validate_trace(
            s, netlist_insts=set(insts), windows=self.windows,
            period_ns=1.0, total_cycles=4)

    def test_good_trace_passes_and_reports_coverage(self):
        cov = self._run(_vcd())
        self.assertEqual(cov["instances_matched"], 2)
        self.assertAlmostEqual(cov["windows"]["a"]["clk_toggles"], 4, delta=1)
        self.assertEqual(cov["xz_events"], 0)

    def test_empty_trace_rejected(self):
        with self.assertRaisesRegex(activity.ActivityError, "empty trace"):
            self._run(_vcd(body=False))

    def test_wrong_dut_scope_rejected(self):
        with self.assertRaisesRegex(activity.ActivityError, "no DUT scope"):
            self._run(_vcd(scope=("tb", "wrong")))

    def test_mismatched_netlist_rejected(self):
        with self.assertRaisesRegex(activity.ActivityError, "does not describe this netlist"):
            self._run(_vcd(insts=("u0", "other")))
        with self.assertRaisesRegex(activity.ActivityError, "does not describe this netlist"):
            self._run(_vcd(), insts=("u0", "u1", "u2"))

    def test_dead_clock_rejected(self):
        with self.assertRaisesRegex(activity.ActivityError, "clk toggled"):
            self._run(_vcd(clk=False))

    def test_trace_shorter_than_workload_rejected(self):
        with self.assertRaisesRegex(activity.ActivityError, "trace ends"):
            self._run(_vcd(cycles=1))

    def test_unparseable_timescale_rejected(self):
        with self.assertRaisesRegex(activity.ActivityError, "timescale"):
            self._run(_vcd(timescale="bogus"))

    def test_x_values_are_counted_not_hidden(self):
        text = _vcd().replace('1"', 'x"', 1)
        cov = self._run(text)
        self.assertGreaterEqual(cov["xz_events"], 1)
        self.assertGreaterEqual(cov["xz_vars"], 1)


class AnnotationTests(unittest.TestCase):
    OK = "Annotated 100 pin activities.\nvcd           100\nunannotated     0\n"

    def test_full_annotation_accepted(self):
        ann = activity.validate_annotation(activity.parse_annotation_report(self.OK))
        self.assertEqual(ann["total_pins"], 100)
        self.assertEqual(ann["annotated_fraction"], 1.0)

    def test_zero_annotated_rejected(self):
        text = "Annotated 0 pin activities.\nunannotated   100\n"
        with self.assertRaisesRegex(activity.ActivityError, "bound no VCD activity"):
            activity.validate_annotation(activity.parse_annotation_report(text))

    def test_ports_only_annotation_rejected(self):
        # The failure seen while bringing this up: a net-only dump annotates
        # the 109 top-level ports and none of the 5262 other pins.
        text = "Annotated 109 pin activities.\nvcd           109\nunannotated  5262\n"
        with self.assertRaisesRegex(activity.ActivityError, "pins annotated"):
            activity.validate_annotation(activity.parse_annotation_report(text))

    def test_fallback_pins_are_reported(self):
        text = "Annotated 995 pin activities.\nvcd           995\nunannotated     5\n"
        ann = activity.validate_annotation(activity.parse_annotation_report(text))
        self.assertEqual(ann["unannotated"], 5)

    def test_missing_summary_is_a_parse_failure(self):
        with self.assertRaisesRegex(activity.ActivityError, "no activity-annotation summary"):
            activity.parse_annotation_report("nothing here")


class DefaultFlowUnchangedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        tmp = Path(self.tmp.name)
        self.report = _tcl_fixtures._write_interregion_report(tmp, _tcl_fixtures._FAKE_ROUTES)
        self._orig = run_sta.INTERREGION_REPORT
        run_sta.INTERREGION_REPORT = self.report
        self.addCleanup(setattr, run_sta, "INTERREGION_REPORT", self._orig)
        self.corner = run_sta.Corner(liberty="tt_025C_3v30", rc="nom")
        self.pdk = _tcl_fixtures._fake_pdk_with_liberty(tmp, self.corner.liberty)
        self.spef = tmp / "x.spef"

    def _tcl(self, **kw):
        return run_sta._tcl(pdk=self.pdk, corner=self.corner, period_ns=1000.0,
                            spef_path=self.spef, bisect=False, **kw)

    def test_default_is_uniform_with_extraction(self):
        text = self._tcl()
        self.assertIn(f"set_power_activity -global -activity {run_sta.ACTIVITY}", text)
        self.assertIn("extract_parasitics", text)
        self.assertNotIn("read_vcd", text)

    def test_activity_mode_reads_the_existing_spef_and_never_sets_global_activity(self):
        text = self._tcl(activity_block=["read_vcd -scope tb/dut x.vcd"])
        self.assertIn("read_vcd -scope tb/dut x.vcd", text)
        self.assertIn(f"read_spef {self.spef}", text)
        self.assertNotIn("extract_parasitics", text)
        self.assertNotIn("set_power_activity", text)

    def test_the_15_point_matrix_is_unchanged(self):
        self.assertEqual(len(run_sta.grid(None, None)), 15)


if __name__ == "__main__":
    unittest.main()
