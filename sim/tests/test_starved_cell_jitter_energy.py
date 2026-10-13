#!/usr/bin/env python3
"""Unit tests for ``sim/tools/starved_cell_jitter_energy.py`` (issue #357).

The tool's ``--check`` rejects a starved-cell record whose lag-1 seed spread is
more than ``SPREAD_TOLERANCE`` times away from what a genuine window of that
length shows (the settling-drift signature of issue #46). ``npm run check:spec``
only shows it passes against today's corpus. These tests build small synthetic
records in a temporary directory and patch the module's ``RECORDS``,
``window_geometry`` (which would otherwise read testbench manifests) and
``derive_a`` (the plain-cell constant), then check:

1. the arithmetic against hand-computed values;
2. ``main(["--check"])`` returns non-zero for a too-tight and a too-loose seed
   spread, and zero for a spread that matches the reference;
3. ``load_variants_by_glob`` (the loader the ring-coupling and
   liveness-tap-phase variant scripts share) skips ``status: superseded``
   records before picking the latest one (issue #427), and its three callers
   still pass their own ``VARIANTS``, ``CORNER`` and ``Variant`` factory.

Stdlib only: no ngspice, no PDK.
"""

from __future__ import annotations

import contextlib
import io
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SIM_DIR / "tools"))

import starved_cell_jitter_energy as sc  # noqa: E402

N_PERIODS = 128
DISCARDED = 16
#: lag-1 relative seed spread of the synthetic plain-cell reference (5 %).
REF_SPREAD = 0.05


def _corner(temp_c: float = 27.0, vdd: float = 3.3) -> str:
    return (
        "---\nstatus: valid\ncorner:\n  process: tt\n"
        f"  voltage: {vdd}\n  temperature: {temp_c}\n---\n\n## Result\n\n"
    )


def _mean_bullet(key: str, mean: float, sd: float, seeds: int = 4) -> str:
    return f"- `{key}`: mean {mean!r} over {seeds} seeds (sd {sd!r})\n"


def jitter_text(*, spread_1: float, sigma_1: float = 1.0e-12, temp_c: float = 27.0) -> str:
    """A starved-cell record with sigma_L = sigma_1 * sqrt(L) at lags 1, 2, 4, 8."""
    text = _corner(temp_c)
    for lag in (1, 2, 4, 8):
        s = sigma_1 * math.sqrt(lag)
        text += _mean_bullet(f"sigma_{lag}", s, s * spread_1)
    text += "- `period`: 2.8e-09\n- `p_active_w`: 1e-04\n"
    return text


class StarvedCellTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for name, value in (
            ("RECORDS", self.root),
            ("window_geometry", lambda *a, **k: (DISCARDED, N_PERIODS)),
            ("derive_a", lambda: (1.79, 1.6, 2.0)),
        ):
            p = mock.patch.object(sc, name, value)
            p.start()
            self.addCleanup(p.stop)

    def write(self, name: str, text: str) -> Path:
        # Loaders now require a frontmatter lifecycle (#425); a fixture that
        # does not set one is a current (`status: valid`) record.
        if not text.startswith("---"):
            text = "---\nstatus: valid\n---\n" + text
        path = self.root / name
        path.write_text(text)
        return path

    def write_corpus(self, *, spread_1: float, noise: float = 1.0e-8) -> None:
        # Two plain-cell records, both at the 5 % reference spread.
        for i in (1, 2):
            self.write(
                f"2026-07-31-ro-inv-05stage-jitter-0{i}.md",
                _corner() + _mean_bullet("sigma_1", 1.0e-12, 1.0e-12 * REF_SPREAD),
            )
        self.write("2026-08-02-ro-ring5-starved-jitter-long-01.md",
                   jitter_text(spread_1=spread_1))
        self.write("2026-07-31-rostage-noise-01.md",
                   _corner() + f"- `inoise_dens_1g`: {noise!r}\n")

    def run_main(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = sc.main(list(args))
        return code, out.getvalue(), err.getvalue()


class ArithmeticTests(StarvedCellTestCase):
    def test_analytic_spread_is_sqrt_lag_over_two_np(self) -> None:
        self.assertAlmostEqual(sc.analytic_spread(1, 8), 0.25)  # sqrt(1/16)
        self.assertAlmostEqual(sc.analytic_spread(4, 8), 0.5)   # sqrt(4/16)

    def test_loglog_slope_recovers_the_exponent(self) -> None:
        xs = [1.0, 2.0, 4.0, 8.0]
        self.assertAlmostEqual(sc._loglog_slope(xs, [x**0.5 for x in xs]), 0.5)
        self.assertAlmostEqual(sc._loglog_slope(xs, [3.0 * x for x in xs]), 1.0)

    def test_record_spread_and_seed_count(self) -> None:
        path = self.write("r.md", _corner() + _mean_bullet("sigma_1", 2.0e-12, 1.0e-13, 8))
        rec = sc.Record(path)
        self.assertEqual(rec.seeds, 8)
        self.assertAlmostEqual(rec.spread("sigma_1"), 0.05)  # 1e-13 / 2e-12
        self.assertIsNone(rec.spread("sigma_2"))
        self.assertEqual(rec.corner, "tt/27/3.30")

    def test_record_without_a_seed_spread_reports_none(self) -> None:
        rec = sc.Record(self.write("r.md", _corner() + "- `sigma_1`: 2e-12\n"))
        self.assertIsNone(rec.spread("sigma_1"))

    def test_reference_spread_rescales_by_window_length(self) -> None:
        self.write_corpus(spread_1=REF_SPREAD)
        # Same window as the reference -> unchanged; a 4x longer one -> halved.
        ref, count, ref_np = sc.reference_spread(1, N_PERIODS)
        self.assertAlmostEqual(ref, REF_SPREAD)
        self.assertEqual((count, ref_np), (2, N_PERIODS))
        self.assertAlmostEqual(sc.reference_spread(1, 4 * N_PERIODS)[0], REF_SPREAD / 2)

    def test_reference_spread_without_plain_records_is_an_error(self) -> None:
        with self.assertRaises(sc.RecordError):
            sc.reference_spread(1, N_PERIODS)

    def test_point_matches_hand_computation(self) -> None:
        # noise 2e-8 / 1e-8 -> scale 2, so sigma_1 = 2e-12 s and sigma_L = 2e-12 sqrt(L).
        self.write_corpus(spread_1=REF_SPREAD, noise=2.0e-8)
        points, skipped = sc.load_points()
        self.assertEqual(skipped, [])
        (p,) = points
        self.assertAlmostEqual(p.sigma[1] / 2.0e-12, 1.0)
        self.assertAlmostEqual(p.exponent, 0.5)
        # kappa^2 (lag 1) = sigma_1^2 / T0 = 4e-24 / 2.8e-9
        self.assertAlmostEqual(p.kappa2_lag1 / (4.0e-24 / 2.8e-9), 1.0)
        # sigma_L^2 = 4e-24 L is exactly linear in elapsed time L*T0, so the
        # zero-intercept slope at every lag equals the lag-1 figure.
        self.assertAlmostEqual(p.kappa2_asym / p.kappa2_lag1, 1.0)
        self.assertAlmostEqual(
            p.a(p.kappa2_lag1) / (p.kappa2_lag1 * 1.0e-4 / (sc.KB * 300.15)), 1.0
        )

    def test_data_less_record_is_skipped_not_fatal(self) -> None:
        self.write_corpus(spread_1=REF_SPREAD)
        self.write("2026-08-03-ro-ring5-starved-jitter-long-02.md", _corner())
        points, skipped = sc.load_points()
        self.assertEqual(len(points), 1)
        self.assertEqual(skipped, ["2026-08-03-ro-ring5-starved-jitter-long-02"])

    def test_missing_noise_record_is_an_error(self) -> None:
        self.write_corpus(spread_1=REF_SPREAD)
        (self.root / "2026-07-31-rostage-noise-01.md").unlink()
        with self.assertRaises(sc.RecordError):
            sc.load_points()


class CheckGateTests(StarvedCellTestCase):
    def test_check_passes_when_spread_matches_the_reference(self) -> None:
        self.write_corpus(spread_1=REF_SPREAD)
        code, out, _ = self.run_main("--check")
        self.assertEqual(code, 0)
        self.assertIn("OK", out)

    def test_check_fails_on_the_settling_drift_signature(self) -> None:
        # Spread ~30x too tight, as in the array-sanity run issue #46 cites.
        self.write_corpus(spread_1=REF_SPREAD / 30)
        code, _, err = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("FAIL", err)

    def test_check_fails_when_spread_is_far_above_the_reference(self) -> None:
        self.write_corpus(spread_1=REF_SPREAD * 4)
        self.assertEqual(self.run_main("--check")[0], 1)

    def test_tolerance_boundary_is_symmetric(self) -> None:
        t = sc.SPREAD_TOLERANCE
        for spread, expected in (
            (REF_SPREAD * t * 0.9, 0), (REF_SPREAD * t * 1.1, 1),
            (REF_SPREAD / t * 1.1, 0), (REF_SPREAD / t * 0.9, 1),
        ):
            with self.subTest(spread=spread):
                self.write_corpus(spread_1=spread)
                self.assertEqual(self.run_main("--check")[0], expected)

    def test_spread_is_only_enforced_with_check(self) -> None:
        self.write_corpus(spread_1=REF_SPREAD / 30)
        self.assertEqual(self.run_main()[0], 0)

    def test_missing_corpus_is_an_error(self) -> None:
        code, _, err = self.run_main("--check")
        self.assertEqual(code, 2)
        self.assertIn("ERROR", err)

    def test_record_with_no_seed_spread_fails_the_gate(self) -> None:
        self.write_corpus(spread_1=REF_SPREAD)
        # Replace the starved record with single-seed bullets (no sd to judge).
        self.write("2026-08-02-ro-ring5-starved-jitter-long-01.md",
                   _corner() + "- `sigma_1`: 1e-12\n- `sigma_2`: 1.4e-12\n"
                   "- `period`: 2.8e-09\n- `p_active_w`: 1e-04\n")
        self.assertEqual(self.run_main("--check")[0], 1)


class VariantsByGlobLifecycleTests(StarvedCellTestCase):
    GLOB = "*-ro-array-coupling-xor-driven-[0-9]*.md"
    SPEC = [("3 xor-driven", GLOB, "rest-a", "rest-b")]

    def write_variant(self, stem: str, status: str | None, sigma_1: float) -> None:
        text = jitter_text(spread_1=REF_SPREAD, sigma_1=sigma_1)
        text = text.replace("status: valid\n",
                            "" if status is None else f"status: {status}\n", 1)
        self.write(f"{stem}.md", text)

    def load(self, **kwargs):
        return sc.load_variants_by_glob(
            self.SPEC, "tt/27/3.30", lambda label, rec, *rest: (label, rec, rest), **kwargs
        )

    def test_lexically_newer_superseded_record_is_not_selected(self) -> None:
        self.write_variant("2026-01-01-ro-array-coupling-xor-driven-01", "valid", 1e-12)
        self.write_variant("2026-01-02-ro-array-coupling-xor-driven-01", "superseded", 9e-12)
        [(label, rec, rest)] = self.load()
        self.assertEqual(label, "3 xor-driven")
        self.assertEqual(rec.stem, "2026-01-01-ro-array-coupling-xor-driven-01")
        self.assertEqual(rest, ("rest-a", "rest-b"))

    def test_historical_read_selects_the_superseded_record(self) -> None:
        self.write_variant("2026-01-01-ro-array-coupling-xor-driven-01", "valid", 1e-12)
        self.write_variant("2026-01-02-ro-array-coupling-xor-driven-01", "superseded", 9e-12)
        [(_label, rec, _rest)] = self.load(include_superseded=True)
        self.assertEqual(rec.stem, "2026-01-02-ro-array-coupling-xor-driven-01")

    def test_superseded_only_variant_is_missing_evidence(self) -> None:
        self.write_variant("2026-01-01-ro-array-coupling-xor-driven-01", "superseded", 1e-12)
        with self.assertRaisesRegex(sc.RecordError, "3 xor-driven.*no valid"):
            self.load()

    def test_body_status_line_does_not_override_frontmatter(self) -> None:
        self.write("2026-01-01-ro-array-coupling-xor-driven-01.md",
                   jitter_text(spread_1=REF_SPREAD) + "\nstatus: superseded\n")
        [(_label, rec, _rest)] = self.load()
        self.assertEqual(rec.stem, "2026-01-01-ro-array-coupling-xor-driven-01")

    def test_missing_unknown_and_duplicate_status_name_the_record(self) -> None:
        stem = "2026-01-01-ro-array-coupling-xor-driven-01"
        for status in (None, "draft", "valid\nstatus: valid"):
            with self.subTest(status=status):
                self.write_variant(stem, status, 1e-12)
                with self.assertRaisesRegex(sc.RecordError, stem):
                    self.load()


class SharedLoaderCallerTests(StarvedCellTestCase):
    """The three scripts built on ``load_variants_by_glob`` keep their own
    arguments and get the lifecycle filter by default."""

    CALLERS = ("array_coupling_variants", "array_coupling_buffer_variant",
               "liveness_tap_phase_variants")

    def test_callers_pass_their_own_variants_corner_and_factory(self) -> None:
        import importlib

        for name in self.CALLERS:
            with self.subTest(caller=name):
                mod = importlib.import_module(name)
                calls = []
                with mock.patch.object(
                    mod, "load_variants_by_glob",
                    lambda *a, **k: calls.append((a, k)) or ["sentinel"],
                ):
                    self.assertEqual(mod.load_variants(), ["sentinel"])
                self.assertEqual(calls, [((mod.VARIANTS, mod.CORNER, mod.Variant), {})])

    def test_buffer_variant_skips_a_newer_superseded_record(self) -> None:
        import array_coupling_buffer_variant as bv

        for i, (_label, glob) in enumerate(bv.VARIANTS):
            slug = glob.removeprefix("*-").split("-[0-9]")[0].removesuffix("-*.md")
            self.write(f"2026-01-01-{slug}-0{i}.md", jitter_text(spread_1=REF_SPREAD))
        self.write("2026-01-09-ro-array-coupling-xor-driven-buffered-01.md",
                   jitter_text(spread_1=REF_SPREAD, sigma_1=5e-12).replace(
                       "status: valid", "status: superseded", 1))
        by_label = {v.label: v for v in bv.load_variants()}
        self.assertEqual(list(by_label), [label for label, _glob in bv.VARIANTS])
        buffered = by_label["6 xor-driven-buffered"]
        self.assertTrue(buffered.rec.stem.startswith("2026-01-01-"))
        self.assertAlmostEqual(buffered.sigma[1], 1.0e-12)


if __name__ == "__main__":
    unittest.main()
