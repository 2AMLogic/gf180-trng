#!/usr/bin/env python3
"""Unit tests for ``sim/tools/liveness_tap_phase_variants.py`` (issue #357).

The tool's ``--check`` gates two recorded verdicts from issue #76's
liveness-tap experiment: the clk-locked question (``clk-locked``) and the
buffer question (``reduced``). These tests check:

1. ``classify`` and ``classify_buffer`` against hand-computed ratios, spreads
   and period swings, including each threshold at, just below and just above;
2. ``main(["--check"])`` through synthetic variants (the record loader and the
   seed-spread calibration are patched; classification and the comparison with
   the recorded verdicts are the real ones). Each of the two verdicts is
   driven to a conflict on its own while the other still matches: matching
   evidence returns 0, a conflict 1, an unset recorded verdict 2.

Stdlib only: no ngspice, no PDK, no committed record is read.
"""

from __future__ import annotations

import contextlib
import io
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SIM_DIR / "tools"))

import liveness_tap_phase_variants as ltp  # noqa: E402
from starved_cell_jitter_energy import RecordError  # noqa: E402

REF = 3.0  # seed-spread reference at lag 1; the deterministic cut is REF / 3 = 1.0


def fv(label: str, sigma1: float, *, period: float = 1000.0, spread: float | None = 0.5,
       swing: float = 0.0) -> SimpleNamespace:
    """The attributes ``main`` and the classifiers read off a ``Variant``."""
    return SimpleNamespace(
        label=label, key=label.split()[1], difference="synthetic", period=period,
        lags=[1], sigma={1: sigma1}, exponent=0.5, exponent_tail=0.5,
        spread_1=spread, n_periods=512, discarded=256, startup_sigma={1: sigma1},
        blocks=[period, period * (1 + swing)], block_swing=swing,
    )


def deck(*, clocked: float = 20.0, spread: float | None = 0.5, gap_period: float = 1050.0,
         buffered: float = 5.0, swing_before: float = 0.03, swing_after: float = 0.01):
    """Six variants (lag-1 sigma of the references is 1.0).

    Defaults classify as ``clk-locked`` (ratio 20, spread 0.5 <= 1.0) and
    ``reduced`` (20x -> 5x, swing 3 % -> 1 %).
    """
    return [
        fv("1 control", 1.0),
        fv("2 clk-high", 1.0),
        fv("3 clk-low", 1.0, period=gap_period),
        fv("4 clocked", clocked, spread=spread, swing=swing_before),
        fv("5 buffered", buffered, swing=swing_after),
        fv("6 buf-static", 1.0),
    ]


def by_key(variants):
    return {v.key: v for v in variants}


class ClassifyTests(unittest.TestCase):
    def test_thresholds_are_the_ratified_ones(self) -> None:
        self.assertEqual(ltp.NULL_TOLERANCE, 3.0)
        self.assertEqual(ltp.EXCESS_FACTOR, 10.0)
        self.assertEqual(ltp.MODULATION_MATERIAL, 0.003)
        self.assertEqual(ltp.DETERMINISTIC_SPREAD_FRACTION, 1.0 / 3.0)

    def clk(self, **kw) -> str:
        return ltp.classify(by_key(deck(**kw)), REF)[0]

    def test_large_deterministic_excess_is_clk_locked(self) -> None:
        self.assertEqual(self.clk(clocked=20.0, spread=0.5), "clk-locked")

    def test_excess_boundary_is_inclusive(self) -> None:
        self.assertEqual(self.clk(clocked=10.0, spread=0.5), "clk-locked")

    def test_ratio_just_below_excess_is_quiet(self) -> None:
        self.assertEqual(self.clk(clocked=9.99, spread=0.5), "quiet")

    def test_spread_exactly_at_the_deterministic_cut_counts(self) -> None:
        cut = ltp.DETERMINISTIC_SPREAD_FRACTION * REF
        self.assertEqual(self.clk(clocked=20.0, spread=cut), "clk-locked")

    def test_spread_just_above_the_cut_is_excess_not_attributed(self) -> None:
        cut = ltp.DETERMINISTIC_SPREAD_FRACTION * REF
        self.assertEqual(self.clk(clocked=20.0, spread=cut * 1.01), "excess-not-attributed")

    def test_missing_spread_is_never_deterministic(self) -> None:
        self.assertEqual(self.clk(clocked=20.0, spread=None), "excess-not-attributed")

    def test_no_excess_and_apart_endpoints_is_quiet_without_the_endpoint_claim(self) -> None:
        verdict, rationale = ltp.classify(by_key(deck(clocked=2.0, gap_period=1050.0)), REF)
        self.assertEqual(verdict, "quiet")
        self.assertIn("does not reach the excess band", rationale)

    def test_close_endpoints_and_null_ratio_is_quiet_on_the_endpoint_claim(self) -> None:
        verdict, rationale = ltp.classify(by_key(deck(clocked=3.0, gap_period=1002.0)), REF)
        self.assertEqual(verdict, "quiet")
        self.assertIn("costs its ring nothing measurable", rationale)

    def test_endpoint_gap_at_materiality_is_not_close(self) -> None:
        # 3/1000 == MODULATION_MATERIAL exactly: not "< MODULATION_MATERIAL".
        verdict, rationale = ltp.classify(by_key(deck(clocked=3.0, gap_period=1003.0)), REF)
        self.assertEqual(verdict, "quiet")
        self.assertIn("does not reach the excess band", rationale)

    def test_ratio_just_above_null_with_close_endpoints_is_not_the_first_quiet(self) -> None:
        _, rationale = ltp.classify(by_key(deck(clocked=3.01, gap_period=1002.0)), REF)
        self.assertIn("does not reach the excess band", rationale)

    def test_endpoint_gap_is_symmetric_in_which_rail_is_faster(self) -> None:
        _, rationale = ltp.classify(by_key(deck(clocked=3.0, gap_period=998.0)), REF)
        self.assertIn("costs its ring nothing measurable", rationale)


class ClassifyBufferTests(unittest.TestCase):
    def buf(self, **kw) -> str:
        return ltp.classify_buffer(by_key(deck(**kw)), REF)[0]

    def test_quiet_buffered_pair_with_flat_blocks_is_removed(self) -> None:
        self.assertEqual(self.buf(clocked=20.0, buffered=1.5, swing_after=0.001), "removed")

    def test_removed_sigma_boundary_is_inclusive(self) -> None:
        self.assertEqual(self.buf(clocked=20.0, buffered=3.0, swing_after=0.001), "removed")

    def test_sigma_just_above_null_is_not_removed(self) -> None:
        # 3.01 < 20/3, so it is "reduced" instead.
        self.assertEqual(self.buf(clocked=20.0, buffered=3.01, swing_after=0.001), "reduced")

    def test_swing_at_materiality_is_not_removed(self) -> None:
        self.assertEqual(self.buf(clocked=20.0, buffered=1.5, swing_after=0.003), "reduced")

    def test_swing_just_below_materiality_is_removed(self) -> None:
        self.assertEqual(self.buf(clocked=20.0, buffered=1.5, swing_after=0.00299), "removed")

    def test_sigma_falling_by_more_than_three_is_reduced(self) -> None:
        self.assertEqual(self.buf(clocked=30.0, buffered=9.99, swing_after=0.03), "reduced")

    def test_sigma_falling_by_exactly_three_is_not_reduced(self) -> None:
        self.assertEqual(self.buf(clocked=30.0, buffered=10.0, swing_before=0.03,
                                  swing_after=0.03), "not-removed")

    def test_swing_falling_by_more_than_three_alone_is_reduced(self) -> None:
        self.assertEqual(self.buf(clocked=30.0, buffered=30.0, swing_before=0.03,
                                  swing_after=0.0099), "reduced")

    def test_swing_falling_by_exactly_three_alone_is_not_reduced(self) -> None:
        self.assertEqual(self.buf(clocked=30.0, buffered=30.0, swing_before=0.03,
                                  swing_after=0.01), "not-removed")

    def test_no_improvement_is_not_removed(self) -> None:
        self.assertEqual(self.buf(clocked=20.0, buffered=20.0, swing_before=0.03,
                                  swing_after=0.03), "not-removed")


class MainCheckTests(unittest.TestCase):
    def run_main(self, variants, argv=("--check",), *, recorded=None, recorded_buffer=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        patches = {
            "load_variants": lambda: variants,
            "reference_spread": lambda lag, n: (REF, 3, 512),
        }
        # ``None`` is a meaningful value for the recorded verdicts, so a sentinel
        # distinguishes "leave the shipped constant alone" from "unset it".
        if recorded is not UNCHANGED:
            patches["RECORDED_VERDICT"] = recorded
        if recorded_buffer is not UNCHANGED:
            patches["RECORDED_BUFFER_VERDICT"] = recorded_buffer
        with contextlib.ExitStack() as stack:
            for name, value in patches.items():
                stack.enter_context(mock.patch.object(ltp, name, value))
            stack.enter_context(contextlib.redirect_stdout(stdout))
            stack.enter_context(contextlib.redirect_stderr(stderr))
            code = ltp.main(list(argv))
        return code, stdout.getvalue(), stderr.getvalue()

    def check(self, variants, **kw):
        kw.setdefault("recorded", UNCHANGED)
        kw.setdefault("recorded_buffer", UNCHANGED)
        return self.run_main(variants, **kw)

    def test_recorded_conclusions_are_the_expected_ones(self) -> None:
        self.assertEqual(ltp.RECORDED_VERDICT, "clk-locked")
        self.assertEqual(ltp.RECORDED_BUFFER_VERDICT, "reduced")

    def test_matching_verdicts_return_zero(self) -> None:
        code, out, err = self.check(deck())
        self.assertEqual(code, 0)
        self.assertIn("verdict: CLK-LOCKED", out)
        self.assertIn("REDUCED", out)
        self.assertIn("OK:", out)
        self.assertEqual(err, "")

    def test_clk_verdict_conflict_alone_returns_one(self) -> None:
        # Running clk no longer moves sigma; the buffer pair still reads "reduced"
        # (1x -> 0.2x with a 1 % residual swing).
        code, out, err = self.check(deck(clocked=1.0, buffered=0.2, swing_before=0.03))
        self.assertEqual(code, 1)
        self.assertIn("verdict: QUIET", out)
        self.assertIn("REDUCED", out)
        self.assertIn("the clk-locked question as 'quiet'", err)
        self.assertNotIn("the buffer question", err)

    def test_buffer_verdict_conflict_alone_returns_one(self) -> None:
        code, out, err = self.check(deck(buffered=20.0, swing_after=0.03))
        self.assertEqual(code, 1)
        self.assertIn("verdict: CLK-LOCKED", out)
        self.assertIn("the buffer question as 'not-removed'", err)
        self.assertNotIn("the clk-locked question", err)

    def test_both_conflicts_are_both_reported(self) -> None:
        code, _, err = self.check(deck(clocked=1.0, buffered=20.0, swing_before=0.03,
                                       swing_after=0.03))
        self.assertEqual(code, 1)
        self.assertIn("the clk-locked question", err)
        self.assertIn("the buffer question", err)

    def test_clk_verdict_conflicts_when_spread_is_not_collapsed(self) -> None:
        code, _, err = self.check(deck(spread=2.0))
        self.assertEqual(code, 1)
        self.assertIn("'excess-not-attributed'", err)

    def test_unset_clk_verdict_returns_two(self) -> None:
        code, _, err = self.check(deck(), recorded=None)
        self.assertEqual(code, 2)
        self.assertIn("the clk-locked question is unset", err)

    def test_unset_buffer_verdict_returns_two(self) -> None:
        code, _, err = self.check(deck(), recorded_buffer=None)
        self.assertEqual(code, 2)
        self.assertIn("the buffer question is unset", err)

    def test_matching_clk_verdict_does_not_hide_an_unset_buffer_verdict(self) -> None:
        code, _, _ = self.check(deck(), recorded="clk-locked", recorded_buffer=None)
        self.assertEqual(code, 2)

    def test_without_check_a_conflict_is_not_gated(self) -> None:
        code, _, err = self.check(deck(clocked=1.0), argv=())
        self.assertEqual(code, 0)
        self.assertEqual(err, "")

    def test_loader_failure_returns_two(self) -> None:
        def boom():
            raise RecordError("no record")

        stderr = io.StringIO()
        with mock.patch.object(ltp, "load_variants", boom), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(stderr):
            code = ltp.main(["--check"])
        self.assertEqual(code, 2)
        self.assertIn("ERROR: no record", stderr.getvalue())


UNCHANGED = object()


if __name__ == "__main__":
    unittest.main()
