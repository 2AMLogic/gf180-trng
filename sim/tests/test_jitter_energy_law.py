#!/usr/bin/env python3
"""Unit tests for ``sim/tools/jitter_energy_law.py`` (issue #357).

``npm run check:spec`` runs ``jitter_energy_law.py --check`` against the
committed corpus, which only shows the gate passes *today*. These tests pin
both halves of the contract on small synthetic record sets written to a
temporary directory (the module's ``RECORDS`` and ``GRID_POINTS`` attributes
are patched; no committed record is read or copied):

1. the arithmetic -- ``Point`` and ``derive_a`` against hand-computed values;
2. the gate -- ``main(["--check"])`` exits non-zero when the invariant's
   spread exceeds ``MAX_SPREAD`` (or the record families are inconsistent or
   missing), and zero when it does not.

Stdlib only: no ngspice, no PDK.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SIM_DIR / "tools"))

import jitter_energy_law as jel  # noqa: E402


def _record(temp_c: float, vdd: float, **values: float) -> str:
    bullets = "\n".join(f"- `{k}`: {v!r}" for k, v in values.items())
    return (
        "corner:\n  process: tt\n"
        f"  voltage: {vdd}\n  temperature: {temp_c}\n\n{bullets}\n"
    )


def write_grid_point(
    root: Path,
    nn: int,
    *,
    power_w: float = 1.0e-4,
    sigma_1: float = 1.0e-12,
    noise: float = 2.0e-8,
    period: float = 1.0e-9,
    temp_c: float = 27.0,
    power_temp_c: float | None = None,
) -> None:
    """Write the three record families for grid point ``nn``."""
    (root / f"{jel.JITTER.format(nn=nn)}.md").write_text(
        _record(temp_c, 3.3, sigma_1=sigma_1)
    )
    (root / f"{jel.STAGE_NOISE.format(nn=nn)}.md").write_text(
        _record(temp_c, 3.3, inoise_dens_1g=noise)
    )
    (root / f"{jel.POWER.format(nn=nn)}.md").write_text(
        _record(
            temp_c if power_temp_c is None else power_temp_c,
            3.3,
            period=period,
            p_active_w=power_w,
            c_eff_node_f=1.0e-14,
        )
    )


class GridTestCase(unittest.TestCase):
    """Points ``jitter_energy_law`` at a temporary two-point grid."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for patch in (
            mock.patch.object(jel, "RECORDS", self.root),
            mock.patch.object(jel, "GRID_POINTS", range(1, 3)),
        ):
            patch.start()
            self.addCleanup(patch.stop)

    def run_main(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = jel.main(list(args))
        return code, out.getvalue(), err.getvalue()


class PointArithmeticTests(GridTestCase):
    def test_point_matches_hand_computation(self) -> None:
        # noise 2e-8 / injected 1e-8      -> scale 2
        # sigma_1 = 1e-12 * 2             = 2e-12 s
        # kappa^2 = (2e-12)^2 / 1e-9      = 4e-15 s
        # a       = 4e-15 * 1e-4 / (kB * 300.15 K)
        write_grid_point(self.root, 1)
        p = jel.Point(1)
        self.assertAlmostEqual(p.scale, 2.0)
        self.assertAlmostEqual(p.sigma_1 / 2.0e-12, 1.0)
        self.assertAlmostEqual(p.kappa2 / 4.0e-15, 1.0)
        self.assertAlmostEqual(p.temp_k, 300.15)
        expected_a = 4.0e-19 / (1.380649e-23 * 300.15)
        self.assertAlmostEqual(p.a / expected_a, 1.0)
        self.assertEqual(p.corner, "tt/27/3.30")

    def test_q_is_kappa2_t_over_period_squared(self) -> None:
        write_grid_point(self.root, 1)
        # Q(T_s) = kappa^2 * T_s / T0^2 = 4e-15 * 1e-6 / 1e-18 = 4e-3
        self.assertAlmostEqual(jel.Point(1).q(1.0e-6) / 4.0e-3, 1.0)

    def test_derive_a_is_mean_min_max(self) -> None:
        pts = [SimpleNamespace(a=v) for v in (1.0, 2.0, 6.0)]
        self.assertEqual(jel.derive_a(pts), (3.0, 1.0, 6.0))

    def test_derive_a_reads_the_grid_when_not_given_points(self) -> None:
        write_grid_point(self.root, 1, power_w=1.0e-4)
        write_grid_point(self.root, 2, power_w=3.0e-4)  # a is proportional to P
        mean_a, lo, hi = jel.derive_a()
        self.assertAlmostEqual(hi / lo, 3.0)
        self.assertAlmostEqual(mean_a / lo, 2.0)

    def test_mismatched_corner_between_families_is_rejected(self) -> None:
        write_grid_point(self.root, 1, temp_c=27.0, power_temp_c=85.0)
        with self.assertRaises(jel.RecordError):
            jel.Point(1)

    def test_missing_record_is_rejected(self) -> None:
        with self.assertRaises(jel.RecordError):
            jel.Point(1)


class CheckGateTests(GridTestCase):
    def test_check_passes_when_spread_is_within_limit(self) -> None:
        write_grid_point(self.root, 1, power_w=1.0e-4)
        write_grid_point(self.root, 2, power_w=1.5e-4)  # spread 1.5x < 1.60x
        code, out, _ = self.run_main("--check")
        self.assertEqual(code, 0)
        self.assertIn("OK", out)

    def test_check_fails_when_spread_exceeds_limit(self) -> None:
        write_grid_point(self.root, 1, power_w=1.0e-4)
        write_grid_point(self.root, 2, power_w=2.0e-4)  # spread 2.0x > 1.60x
        code, _, err = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("FAIL", err)

    def test_spread_just_inside_and_just_outside_the_limit(self) -> None:
        write_grid_point(self.root, 1, power_w=1.0e-4)
        write_grid_point(self.root, 2, power_w=1.0e-4 * (jel.MAX_SPREAD - 0.01))
        self.assertEqual(self.run_main("--check")[0], 0)
        write_grid_point(self.root, 2, power_w=1.0e-4 * (jel.MAX_SPREAD + 0.01))
        self.assertEqual(self.run_main("--check")[0], 1)

    def test_spread_is_only_enforced_with_check(self) -> None:
        write_grid_point(self.root, 1, power_w=1.0e-4)
        write_grid_point(self.root, 2, power_w=5.0e-4)
        self.assertEqual(self.run_main()[0], 0)

    def test_incomplete_record_families_are_an_error(self) -> None:
        write_grid_point(self.root, 1)  # point 2 is absent
        code, _, err = self.run_main("--check")
        self.assertEqual(code, 2)
        self.assertIn("ERROR", err)


if __name__ == "__main__":
    unittest.main()
