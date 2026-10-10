#!/usr/bin/env python3
"""Unit tests for ``sim/tools/array_liveness_tap_phase_variants.py`` (issue #357).

The tool's ``--check`` gates two recorded verdicts from issue #87's
shipped-array experiment: the shipped-array residual
(``bound-confirmed-residual-remains``) and the xsb-on-xo path
(``unreachable``). These tests check:

1. ``classify_shipped`` and ``classify_xsb`` against hand-computed ratios and
   period swings, with each threshold (the quiet band, the bound margin, the
   excess factor, the modulation materiality) at, just below and just above;
2. ``main(["--check"])`` through synthetic variants (the record loader and the
   seed-spread calibration are patched; classification and the comparison with
   the recorded verdicts are the real ones). Each verdict is driven to a
   conflict on its own while the other still matches. Matching evidence
   returns 0, a conflict 1, an unset recorded verdict 2, and a recorded
   conclusion whose supporting variant pair has gone missing returns 1.
3. ``_load`` against an empty record directory, and its lifecycle filter
   (issue #427): a ``status: superseded`` record is skipped before the latest
   is chosen, so a superseded-only variant is ``None`` when optional and a
   ``RecordError`` when required.

Stdlib only: no ngspice, no PDK, no committed record is read.
"""

from __future__ import annotations

import contextlib
import io
import math
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SIM_DIR / "tools"))

import array_liveness_tap_phase_variants as alt  # noqa: E402
from starved_cell_jitter_energy import RecordError  # noqa: E402

REF = 3.0  # seed-spread reference at lag 1
BOUND = 20.0  # #76's upper bound on the shipped ratio
UNCHANGED = object()


def fv(label: str, sigma1: float, *, spread: float | None = 0.5, swing: float = 0.0,
       sigma_r2: float | None = 1.0) -> SimpleNamespace:
    """The attributes ``main`` and the classifiers read off a ``Variant``."""
    period = 1000.0
    return SimpleNamespace(
        label=label, key=label.split(maxsplit=1)[1], difference="synthetic",
        period=period, period_r2=1100.0, lags=[1], sigma={1: sigma1},
        sigma_r2={} if sigma_r2 is None else {1: sigma_r2}, exponent=0.5,
        spread_1=spread, n_periods=256, discarded=128,
        blocks=[period, period * (1 + swing)], block_swing=swing,
    )


def array_variants(*, shipped: float = 10.0, shipped_swing: float = 0.01, xsb: float = 1.0,
                   xsb_swing: float = 0.0, drop: tuple[str, ...] = ()):
    """The four array variants (``None`` for any named in ``drop``).

    Defaults classify as ``bound-confirmed-residual-remains`` (10x against a
    20x bound) and ``unreachable`` (1x, flat blocks).
    """
    built = {
        "1 shipped": fv("1 shipped", shipped, swing=shipped_swing),
        "2 shipped-static": fv("2 shipped-static", 1.0),
        "3 xsb": fv("3 xsb", xsb, swing=xsb_swing),
        "4 xsb-static": fv("4 xsb-static", 1.0),
    }
    return [None if k in drop else v for k, v in built.items()]


def bound_variants(bound: float = BOUND):
    return [fv("76 buffered", bound), fv("76 buf-static", 1.0)]


def keyed(variants):
    return {v.key: v for v in variants if v is not None}


class ClassifyShippedTests(unittest.TestCase):
    def ship(self, ratio: float, *, swing: float = 0.01, spread: float | None = 0.5,
             bound: float = BOUND):
        by_key = keyed([fv("1 shipped", ratio, spread=spread, swing=swing),
                        fv("2 shipped-static", 1.0)])
        return alt.classify_shipped(by_key, bound, REF)

    def test_thresholds_are_the_ratified_ones(self) -> None:
        self.assertEqual(alt.NULL_TOLERANCE, 3.0)
        self.assertEqual(alt.EXCESS_FACTOR, 10.0)
        self.assertEqual(alt.MODULATION_MATERIAL, 0.003)
        self.assertEqual(alt.BOUND_MARGIN, 0.10)

    def test_ratio_at_the_bound_violates_it(self) -> None:
        self.assertEqual(self.ship(20.0)[0], "bound-violated")

    def test_ratio_above_the_bound_violates_it(self) -> None:
        self.assertEqual(self.ship(25.0)[0], "bound-violated")

    def test_ratio_inside_the_margin_is_not_separated(self) -> None:
        self.assertEqual(self.ship(19.0)[0], "bound-not-separated")

    def test_ratio_just_below_the_bound_is_not_separated(self) -> None:
        self.assertEqual(self.ship(math.nextafter(20.0, 0.0))[0], "bound-not-separated")

    def test_ratio_exactly_at_the_margin_edge_is_separated(self) -> None:
        edge = BOUND * (1.0 - alt.BOUND_MARGIN)  # 18.0
        self.assertEqual(self.ship(edge)[0], "bound-confirmed-residual-remains")

    def test_ratio_just_above_the_margin_edge_is_not_separated(self) -> None:
        edge = BOUND * (1.0 - alt.BOUND_MARGIN)
        self.assertEqual(self.ship(math.nextafter(edge, 100.0))[0], "bound-not-separated")

    def test_ratio_in_the_quiet_band_is_confirmed_quiet(self) -> None:
        self.assertEqual(self.ship(1.5)[0], "bound-confirmed-quiet")

    def test_quiet_band_boundary_is_inclusive(self) -> None:
        self.assertEqual(self.ship(3.0)[0], "bound-confirmed-quiet")

    def test_ratio_just_above_the_quiet_band_has_a_residual(self) -> None:
        self.assertEqual(self.ship(3.01)[0], "bound-confirmed-residual-remains")

    def test_mid_ratio_is_residual_remains(self) -> None:
        self.assertEqual(self.ship(10.0)[0], "bound-confirmed-residual-remains")

    def test_margin_outranks_the_quiet_band_for_a_small_bound(self) -> None:
        # 2.4x against a 2.5x bound: inside the 10 % margin, and also <= 3x.
        self.assertEqual(self.ship(2.4, bound=2.5)[0], "bound-not-separated")

    def test_swing_at_materiality_corroborates_the_residual(self) -> None:
        _, text = self.ship(10.0, swing=0.003)
        self.assertIn("agrees", text)
        self.assertNotIn("BELOW it", text)

    def test_swing_just_below_materiality_does_not_corroborate(self) -> None:
        verdict, text = self.ship(10.0, swing=0.00299)
        self.assertEqual(verdict, "bound-confirmed-residual-remains")
        self.assertIn("BELOW it", text)

    def test_spread_collapse_is_reported_in_the_residual_rationale(self) -> None:
        cut = alt.DETERMINISTIC_SPREAD_FRACTION * REF
        self.assertIn("(deterministic)", self.ship(10.0, spread=cut)[1])
        self.assertIn("(not collapsed)", self.ship(10.0, spread=cut * 1.01)[1])
        self.assertIn("(not collapsed)", self.ship(10.0, spread=None)[1])


class ClassifyXsbTests(unittest.TestCase):
    def xsb(self, ratio: float, *, swing: float = 0.0, sigma_r2: float | None = 1.0):
        by_key = keyed([fv("3 xsb", ratio, swing=swing, sigma_r2=sigma_r2),
                        fv("4 xsb-static", 1.0)])
        return alt.classify_xsb(by_key, REF)

    def test_flat_null_ratio_is_unreachable(self) -> None:
        self.assertEqual(self.xsb(1.0)[0], "unreachable")

    def test_unreachable_boundary_on_ratio_is_inclusive(self) -> None:
        self.assertEqual(self.xsb(3.0, swing=0.00299)[0], "unreachable")

    def test_ratio_just_above_null_is_marginal(self) -> None:
        self.assertEqual(self.xsb(3.01, swing=0.0)[0], "marginal")

    def test_swing_at_materiality_is_not_unreachable(self) -> None:
        self.assertEqual(self.xsb(1.0, swing=0.003)[0], "marginal")

    def test_swing_just_below_materiality_is_unreachable(self) -> None:
        self.assertEqual(self.xsb(1.0, swing=0.00299)[0], "unreachable")

    def test_ratio_at_excess_reaches_the_ring(self) -> None:
        self.assertEqual(self.xsb(10.0)[0], "reaches")

    def test_ratio_just_below_excess_is_marginal(self) -> None:
        self.assertEqual(self.xsb(9.99)[0], "marginal")

    def test_reaches_does_not_need_a_material_swing(self) -> None:
        self.assertEqual(self.xsb(15.0, swing=0.0)[0], "reaches")

    def test_ring_two_ratio_is_reported_and_may_be_absent(self) -> None:
        by_key = keyed([fv("3 xsb", 1.0, sigma_r2=4.0), fv("4 xsb-static", 1.0)])
        by_key["xsb"].sigma_r2 = {1: 4.0}
        by_key["xsb-static"].sigma_r2 = {1: 2.0}
        self.assertIn("ring 2: 2.00x", alt.classify_xsb(by_key, REF)[1])
        self.assertIn("ring 2: nanx", self.xsb(1.0, sigma_r2=None)[1])


class MainCheckTests(unittest.TestCase):
    def run_main(self, variants, bound=None, argv=("--check",), *,
                 shipped_recorded=UNCHANGED, xsb_recorded=UNCHANGED):
        bound = bound_variants() if bound is None else bound
        patches = {
            "load_variants": lambda: (variants, bound),
            "reference_spread": lambda lag, n: (REF, 3, 512),
        }
        # ``None`` is a meaningful recorded value ("unset"), hence the sentinel.
        if shipped_recorded is not UNCHANGED:
            patches["RECORDED_SHIPPED_VERDICT"] = shipped_recorded
        if xsb_recorded is not UNCHANGED:
            patches["RECORDED_XSB_VERDICT"] = xsb_recorded
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.ExitStack() as stack:
            for name, value in patches.items():
                stack.enter_context(mock.patch.object(alt, name, value))
            stack.enter_context(contextlib.redirect_stdout(stdout))
            stack.enter_context(contextlib.redirect_stderr(stderr))
            code = alt.main(list(argv))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_recorded_conclusions_are_the_expected_ones(self) -> None:
        self.assertEqual(alt.RECORDED_SHIPPED_VERDICT, "bound-confirmed-residual-remains")
        self.assertEqual(alt.RECORDED_XSB_VERDICT, "unreachable")

    def test_matching_verdicts_return_zero(self) -> None:
        code, out, err = self.run_main(array_variants())
        self.assertEqual(code, 0)
        self.assertIn("shipped-array residual: BOUND-CONFIRMED-RESIDUAL-REMAINS", out)
        self.assertIn("xsb-on-xo path: UNREACHABLE", out)
        self.assertIn("OK:", out)
        self.assertEqual(err, "")

    def test_shipped_conflict_alone_returns_one(self) -> None:
        code, out, err = self.run_main(array_variants(shipped=1.5))
        self.assertEqual(code, 1)
        self.assertIn("BOUND-CONFIRMED-QUIET", out)
        self.assertIn("the shipped-array residual as 'bound-confirmed-quiet'", err)
        self.assertNotIn("the xsb-on-xo path", err)

    def test_shipped_bound_violation_returns_one(self) -> None:
        code, _, err = self.run_main(array_variants(shipped=25.0))
        self.assertEqual(code, 1)
        self.assertIn("'bound-violated'", err)

    def test_xsb_conflict_alone_returns_one(self) -> None:
        code, out, err = self.run_main(array_variants(xsb=15.0))
        self.assertEqual(code, 1)
        self.assertIn("xsb-on-xo path: REACHES", out)
        self.assertIn("the xsb-on-xo path as 'reaches'", err)
        self.assertNotIn("the shipped-array residual", err)

    def test_marginal_xsb_returns_one(self) -> None:
        code, _, err = self.run_main(array_variants(xsb_swing=0.01))
        self.assertEqual(code, 1)
        self.assertIn("'marginal'", err)

    def test_both_conflicts_are_both_reported(self) -> None:
        code, _, err = self.run_main(array_variants(shipped=1.5, xsb=15.0))
        self.assertEqual(code, 1)
        self.assertIn("the shipped-array residual", err)
        self.assertIn("the xsb-on-xo path", err)

    def test_unset_shipped_verdict_returns_two(self) -> None:
        code, _, err = self.run_main(array_variants(), shipped_recorded=None)
        self.assertEqual(code, 2)
        self.assertIn("the shipped-array residual is unset", err)

    def test_unset_xsb_verdict_returns_two(self) -> None:
        code, _, err = self.run_main(array_variants(), xsb_recorded=None)
        self.assertEqual(code, 2)
        self.assertIn("the xsb-on-xo path is unset", err)

    def test_unset_verdict_outranks_missing_evidence(self) -> None:
        code, _, _ = self.run_main(array_variants(drop=("2 shipped-static",)),
                                   shipped_recorded=None)
        self.assertEqual(code, 2)

    def test_missing_shipped_static_fails_the_shipped_conclusion_only(self) -> None:
        code, out, err = self.run_main(array_variants(drop=("2 shipped-static",)))
        self.assertEqual(code, 1)
        self.assertIn("NOT YET RUN", out)
        self.assertIn("the shipped-array residual has a recorded conclusion", err)
        self.assertIn("no longer on file", err)
        self.assertNotIn("the xsb-on-xo path has a recorded conclusion", err)

    def test_missing_xsb_clocked_fails_the_xsb_conclusion_only(self) -> None:
        code, _, err = self.run_main(array_variants(drop=("3 xsb",)))
        self.assertEqual(code, 1)
        self.assertIn("the xsb-on-xo path has a recorded conclusion", err)
        self.assertNotIn("the shipped-array residual has a recorded conclusion", err)

    def test_missing_xsb_static_fails_the_xsb_conclusion_only(self) -> None:
        code, _, err = self.run_main(array_variants(drop=("4 xsb-static",)))
        self.assertEqual(code, 1)
        self.assertIn("the xsb-on-xo path has a recorded conclusion", err)
        self.assertNotIn("the shipped-array residual has a recorded conclusion", err)

    def test_both_pairs_missing_fails_both_conclusions(self) -> None:
        code, _, err = self.run_main(
            array_variants(drop=("2 shipped-static", "3 xsb", "4 xsb-static")))
        self.assertEqual(code, 1)
        self.assertIn("the shipped-array residual has a recorded conclusion", err)
        self.assertIn("the xsb-on-xo path has a recorded conclusion", err)

    def test_missing_shipped_deck_returns_two_even_without_check(self) -> None:
        for argv in (("--check",), ()):
            code, _, err = self.run_main(array_variants(drop=("1 shipped",)), argv=argv)
            self.assertEqual(code, 2)
            self.assertIn("has no record at this corner", err)

    def test_without_check_a_missing_pair_is_not_gated(self) -> None:
        code, _, err = self.run_main(array_variants(drop=("2 shipped-static",)), argv=())
        self.assertEqual(code, 0)
        self.assertEqual(err, "")

    def test_bound_is_taken_from_the_76_pair(self) -> None:
        # Against a 10.5x bound the default 10x shipped ratio is inside the margin.
        code, _, err = self.run_main(array_variants(), bound=bound_variants(10.5))
        self.assertEqual(code, 1)
        self.assertIn("'bound-not-separated'", err)

    def test_loader_failure_returns_two(self) -> None:
        def boom():
            raise RecordError("no record")

        stderr = io.StringIO()
        with mock.patch.object(alt, "load_variants", boom), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(stderr):
            code = alt.main(["--check"])
        self.assertEqual(code, 2)
        self.assertIn("ERROR: no record", stderr.getvalue())


class LoadTests(unittest.TestCase):
    SPEC = ("1 shipped", "????-??-??-array-liveness-tap-phase-clocked-*.md",
            Path("tb.json"), "synthetic")

    def test_optional_variant_without_a_record_is_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(alt, "RECORDS", Path(tmp)):
            self.assertIsNone(alt._load(self.SPEC, required=False))

    def test_required_variant_without_a_record_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(alt, "RECORDS", Path(tmp)):
            with self.assertRaises(RecordError):
                alt._load(self.SPEC)


class LoadLifecycleTests(unittest.TestCase):
    SPEC = LoadTests.SPEC
    STEM = "2026-01-0{day}-array-liveness-tap-phase-clocked-01"

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for name, value in (
            ("RECORDS", self.root),
            # The real Variant reads a testbench manifest; the record is what
            # selection is about, so the factory hands it straight back.
            ("Variant", lambda label, rec, manifest, difference: rec),
        ):
            p = mock.patch.object(alt, name, value)
            p.start()
            self.addCleanup(p.stop)

    def write(self, day: int, status: str | None, *, body: str = "") -> str:
        stem = self.STEM.format(day=day)
        head = "---\n" + ("" if status is None else f"status: {status}\n")
        (self.root / f"{stem}.md").write_text(
            head + "corner:\n  process: tt\n  voltage: 3.3\n  temperature: 27\n---\n\n"
            + body + "- `sigma_1`: 1e-12\n- `period`: 2.8e-09\n"
        )
        return stem

    def test_lexically_newer_superseded_record_is_not_selected(self) -> None:
        valid = self.write(1, "valid")
        self.write(2, "superseded")
        for required in (True, False):
            with self.subTest(required=required):
                self.assertEqual(alt._load(self.SPEC, required=required).stem, valid)

    def test_historical_read_selects_the_superseded_record(self) -> None:
        self.write(1, "valid")
        newer = self.write(2, "superseded")
        self.assertEqual(alt._load(self.SPEC, include_superseded=True).stem, newer)

    def test_superseded_only_optional_variant_is_none(self) -> None:
        self.write(1, "superseded")
        self.assertIsNone(alt._load(self.SPEC, required=False))

    def test_superseded_only_required_variant_raises(self) -> None:
        self.write(1, "superseded")
        with self.assertRaisesRegex(RecordError, "1 shipped.*no valid"):
            alt._load(self.SPEC)

    def test_body_status_line_does_not_override_frontmatter(self) -> None:
        stem = self.write(1, "valid", body="Quoted:\n\nstatus: superseded\n\n")
        self.assertEqual(alt._load(self.SPEC).stem, stem)

    def test_missing_unknown_and_duplicate_status_name_the_record(self) -> None:
        for status in (None, "draft", "valid\nstatus: valid"):
            with self.subTest(status=status):
                stem = self.write(1, status)
                for required in (True, False):
                    with self.assertRaisesRegex(RecordError, stem):
                        alt._load(self.SPEC, required=required)

    def test_load_variants_passes_the_historical_option_through(self) -> None:
        seen = []
        with mock.patch.object(alt, "_load", lambda spec, **kw: seen.append(kw)):
            alt.load_variants()
            alt.load_variants(include_superseded=True)
        n_opt, n_req = len(alt.VARIANTS), len(alt.BOUND_VARIANTS)
        self.assertEqual(
            seen,
            [{"required": False, "include_superseded": False}] * n_opt
            + [{"include_superseded": False}] * n_req
            + [{"required": False, "include_superseded": True}] * n_opt
            + [{"include_superseded": True}] * n_req,
        )


if __name__ == "__main__":
    unittest.main()
