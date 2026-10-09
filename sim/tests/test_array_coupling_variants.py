#!/usr/bin/env python3
"""Unit tests for ``sim/tools/array_coupling_variants.py`` (issue #357).

The tool's ``--check`` gates the recorded verdict of issue #51's ring-to-ring
coupling experiment (``coupling``). ``npm run check:spec`` shows only that
today's corpus still classifies that way. These tests show the gate *fails*
when it should:

1. ``classify`` against hand-computed ratio sets, including both thresholds
   (``NULL_TOLERANCE`` and ``EXCESS_FACTOR``) at, just below and just above;
2. ``main(["--check"])`` driven through synthetic variants (the record loader,
   the sanity-record reader and the seed-spread calibration are patched; the
   classification and the comparison against ``RECORDED_VERDICT`` are the real
   ones): matching evidence returns 0, conflicting evidence 1, an unset
   recorded verdict 2.

Stdlib only: no ngspice, no PDK, no committed record is read.
"""

from __future__ import annotations

import contextlib
import io
import math
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SIM_DIR / "tools"))

import array_coupling_variants as acv  # noqa: E402
from starved_cell_jitter_energy import RecordError  # noqa: E402

LABELS = ("1 control", "2 xor-static", "3 xor-driven", "4 rings-only")


def fake_variant(label: str, sigma1: float, *, period: float = 3.0e-9,
                 period_r2: float | None = None) -> SimpleNamespace:
    """The attributes ``main`` reads off a ``Variant``, with one lag."""
    beat = abs(1.0 / period - 1.0 / period_r2) if period_r2 else None
    return SimpleNamespace(
        label=label, difference="synthetic", period=period, period_r2=period_r2,
        lags=[1], sigma={1: sigma1}, exponent=0.5, exponent_tail=0.5,
        spread_1=0.01, n_periods=512, discarded=256,
        startup_lags=[1], startup_sigma={1: sigma1}, startup_period=period,
        startup_exponent=0.5, startup_spread_1=0.01, beat_hz=beat,
    )


def fake_sanity() -> SimpleNamespace:
    return SimpleNamespace(
        stem="synthetic-sanity", period=3.0e-9, lags=[1], sigma={1: 23.2e-12},
        exponent=0.5, spread_1=0.003,
    )


def variants_with_ratios(static: float, driven: float, rings: float) -> list[SimpleNamespace]:
    """Control sigma 1.0, so each ratio is its variant's lag-1 sigma."""
    return [
        fake_variant(LABELS[0], 1.0),
        fake_variant(LABELS[1], static),
        fake_variant(LABELS[2], driven, period_r2=3.1e-9),
        fake_variant(LABELS[3], rings, period_r2=3.1e-9),
    ]


def ratios(static: float, driven: float, rings: float) -> dict[str, float]:
    return {"2 xor-static": static, "3 xor-driven": driven, "4 rings-only": rings}


class ClassifyTests(unittest.TestCase):
    def verdict(self, static: float, driven: float, rings: float) -> str:
        return acv.classify(ratios(static, driven, rings))[0]

    def test_thresholds_are_the_ratified_ones(self) -> None:
        # Guard the fixtures below, which are written against these values.
        self.assertEqual(acv.NULL_TOLERANCE, 3.0)
        self.assertEqual(acv.EXCESS_FACTOR, 10.0)

    def test_only_the_driven_variant_moving_is_coupling(self) -> None:
        self.assertEqual(self.verdict(1.06, 28.6, 1.0), "coupling")

    def test_coupling_boundaries_are_inclusive(self) -> None:
        # driven == EXCESS_FACTOR, static == rings == NULL_TOLERANCE
        self.assertEqual(self.verdict(3.0, 10.0, 3.0), "coupling")

    def test_driven_just_below_excess_is_neither(self) -> None:
        self.assertEqual(self.verdict(1.0, 9.99, 1.0), "neither")

    def test_static_just_above_null_is_neither(self) -> None:
        self.assertEqual(self.verdict(3.01, 28.6, 1.0), "neither")

    def test_rings_just_above_null_is_neither(self) -> None:
        self.assertEqual(self.verdict(1.0, 28.6, 3.01), "neither")

    def test_static_load_alone_at_excess_is_load(self) -> None:
        self.assertEqual(self.verdict(10.0, 1.0, 1.0), "load")

    def test_static_just_below_excess_is_not_load(self) -> None:
        self.assertNotEqual(self.verdict(9.99, 1.0, 1.0), "load")

    def test_rings_only_at_excess_is_numerical(self) -> None:
        self.assertEqual(self.verdict(1.0, 28.6, 10.0), "numerical")

    def test_rings_just_below_excess_is_not_numerical(self) -> None:
        self.assertNotEqual(self.verdict(1.0, 28.6, 9.99), "numerical")

    def test_load_outranks_numerical_and_coupling(self) -> None:
        self.assertEqual(self.verdict(12.0, 30.0, 12.0), "load")

    def test_numerical_outranks_coupling(self) -> None:
        self.assertEqual(self.verdict(1.0, 30.0, 12.0), "numerical")

    def test_nothing_moving_is_neither(self) -> None:
        verdict, rationale = acv.classify(ratios(1.0, 1.0, 1.0))
        self.assertEqual(verdict, "neither")
        self.assertIn("NEITHER", rationale)

    def test_rationale_names_its_verdict(self) -> None:
        for args, word in (((1.0, 30.0, 1.0), "COUPLING"), ((20.0, 1.0, 1.0), "LOAD"),
                           ((1.0, 30.0, 20.0), "NUMERICAL")):
            self.assertIn(word, acv.classify(ratios(*args))[1])


class VariantArithmeticTests(unittest.TestCase):
    def test_beat_hz_is_the_difference_of_ring_frequencies(self) -> None:
        # 1/2e-9 = 5e8 Hz, 1/4e-9 = 2.5e8 Hz -> beat 2.5e8 Hz.
        v = acv.Variant.__new__(acv.Variant)
        v.period, v.period_r2 = 2.0e-9, 4.0e-9
        self.assertTrue(math.isclose(v.beat_hz, 2.5e8, rel_tol=1e-12))

    def test_beat_hz_is_symmetric_and_absent_without_a_second_ring(self) -> None:
        v = acv.Variant.__new__(acv.Variant)
        v.period, v.period_r2 = 4.0e-9, 2.0e-9
        self.assertTrue(math.isclose(v.beat_hz, 2.5e8, rel_tol=1e-12))
        v.period_r2 = None
        self.assertIsNone(v.beat_hz)


class MainCheckTests(unittest.TestCase):
    def run_main(self, variants, argv=("--check",), *, recorded="coupling"):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.ExitStack() as stack:
            for name, value in (
                ("load_variants", lambda: variants),
                ("SanityRun", lambda path: fake_sanity()),
                ("reference_spread", lambda lag, n: (0.06, 3, 512)),
                ("RECORDED_VERDICT", recorded),
            ):
                stack.enter_context(mock.patch.object(acv, name, value))
            stack.enter_context(contextlib.redirect_stdout(stdout))
            stack.enter_context(contextlib.redirect_stderr(stderr))
            code = acv.main(list(argv))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_matching_verdict_returns_zero(self) -> None:
        code, out, _ = self.run_main(variants_with_ratios(1.06, 28.6, 1.0))
        self.assertEqual(code, 0)
        self.assertIn("verdict: COUPLING", out)
        self.assertIn("OK:", out)

    def test_conflicting_verdict_returns_one(self) -> None:
        # The driven variant no longer moves: the evidence now says "neither".
        code, out, err = self.run_main(variants_with_ratios(1.06, 1.0, 1.0))
        self.assertEqual(code, 1)
        self.assertIn("verdict: NEITHER", out)
        self.assertIn("FAIL", err)
        self.assertIn("'neither'", err)

    def test_load_verdict_conflicts_with_recorded_coupling(self) -> None:
        code, _, err = self.run_main(variants_with_ratios(12.0, 28.6, 1.0))
        self.assertEqual(code, 1)
        self.assertIn("'load'", err)

    def test_numerical_verdict_conflicts_with_recorded_coupling(self) -> None:
        code, _, err = self.run_main(variants_with_ratios(1.0, 28.6, 12.0))
        self.assertEqual(code, 1)
        self.assertIn("'numerical'", err)

    def test_unset_recorded_verdict_returns_two(self) -> None:
        code, _, err = self.run_main(variants_with_ratios(1.06, 28.6, 1.0), recorded=None)
        self.assertEqual(code, 2)
        self.assertIn("RECORDED_VERDICT is unset", err)

    def test_unset_verdict_is_reported_even_when_evidence_conflicts(self) -> None:
        code, _, _ = self.run_main(variants_with_ratios(1.0, 1.0, 1.0), recorded=None)
        self.assertEqual(code, 2)

    def test_without_check_a_conflict_is_reported_but_not_gated(self) -> None:
        code, out, err = self.run_main(variants_with_ratios(1.0, 1.0, 1.0), argv=())
        self.assertEqual(code, 0)
        self.assertIn("verdict: NEITHER", out)
        self.assertEqual(err, "")

    def test_loader_failure_returns_two(self) -> None:
        def boom():
            raise RecordError("no record")

        stderr = io.StringIO()
        with mock.patch.object(acv, "load_variants", boom), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(stderr):
            code = acv.main(["--check"])
        self.assertEqual(code, 2)
        self.assertIn("ERROR: no record", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
