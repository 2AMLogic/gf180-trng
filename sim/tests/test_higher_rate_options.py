#!/usr/bin/env python3
"""Unit tests for ``sim/tools/higher_rate_options.py`` (issue #629).

The arithmetic is checked against hand-computed values, the law is checked to
be self-consistent (sizing by ring count and by the ``(*)`` power floor agree),
and ``--check`` is shown both to pass on the committed corpus and to fail when
a quoted figure no longer reproduces. No ngspice, no PDK.
"""

from __future__ import annotations

import contextlib
import io
import math
import sys
import unittest
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SIM_DIR / "tools"))

import array_sizing as sizing  # noqa: E402
import higher_rate_options as hro  # noqa: E402

NEED = sizing.MARGIN_M * sizing.Q_H0  # 6e-3


class ArithmeticTests(unittest.TestCase):
    def test_rings_needed_hand_values(self) -> None:
        # N * g / R >= 6e-3  ->  N >= 6e-3 * R / g
        self.assertEqual(hro.rings_needed(1000.0, 6.0), 1)
        self.assertEqual(hro.rings_needed(1000.0, 3.0), 2)
        self.assertEqual(hro.rings_needed(1001.0, 3.0), 3)
        self.assertEqual(hro.rings_needed(1e6, 8.0), 750)

    def test_rings_needed_is_never_zero(self) -> None:
        self.assertEqual(hro.rings_needed(1.0, 1e9), 1)

    def test_power_floor_matches_ring_count_sizing(self) -> None:
        # one ring of power P and period T0 has g = a kT / (P T0^2); the (*)
        # floor for the rate that ring exactly meets must equal P.
        a, temp_k, p, t0 = 7.0, 300.0, 50e-6, 8e-9
        g = a * sizing.KB * temp_k / (p * t0 * t0)
        rate_edge = g / NEED
        floor = hro.ring_power_floor(rate_edge, p * t0, a, temp_k)
        self.assertAlmostEqual(floor / p, 1.0, places=9)

    def test_power_floor_is_linear_in_rate_and_square_in_energy(self) -> None:
        base = hro.ring_power_floor(1e3, 1e-12, 7.0, 300.0)
        self.assertAlmostEqual(hro.ring_power_floor(4e3, 1e-12, 7.0, 300.0) / base, 4.0)
        self.assertAlmostEqual(hro.ring_power_floor(1e3, 2e-12, 7.0, 300.0) / base, 4.0)

    def test_tree_power_reproduces_the_single_measured_gate(self) -> None:
        # N = 2: one xor2 toggling at the XOR-node rate 2r
        e, r = 1e-13, 2e8
        self.assertAlmostEqual(hro.tree_power(2, e, r), e * 2 * r)
        self.assertEqual(hro.tree_power(1, e, r), 0.0)
        self.assertAlmostEqual(hro.tree_power(8, e, r), e * r * 8 * 3)

    def test_root_interval(self) -> None:
        self.assertAlmostEqual(hro.root_interval_s(4, 2.5e8), 1e-9)

    def test_trim_resolution(self) -> None:
        # 3 fs at 15 ps/fF is 0.2 aF
        self.assertAlmostEqual(hro.trim_resolution_f(3e-15, 15e-12 / 1e-15) * 1e18, 0.2)


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.s = hro.study()

    def test_uses_the_starved_cell_constant_not_the_plain_one(self) -> None:
        self.assertEqual(self.s["a"], hro.A_STARVED)
        self.assertNotEqual(hro.A_STARVED, sizing.A_JITTER_ENERGY)
        for p in hro.array_points():
            self.assertEqual(p.a, hro.A_STARVED)

    def test_shipped_array_edge_reproduces_array_sizing(self) -> None:
        pts = sizing.dedupe_by_corner(
            [p for p in (sizing.ArrayPoint(r, a=hro.A_STARVED) for r in sizing.load_array_records())
             if p.n == sizing.shipped_ring_count()])
        worst = min(pts, key=lambda p: p.g)
        self.assertAlmostEqual(self.s["rate_shipped_bps"], worst.max_rate_bps())

    def test_ring_count_grows_linearly_with_rate(self) -> None:
        n = [self.s["options"][("A", r)]["n"] for r in hro.TARGETS_BPS]
        self.assertEqual(n, sorted(n))
        self.assertTrue(math.isclose(n[2] / n[1], 4.0, rel_tol=0.01))

    def test_check_passes_on_committed_corpus(self) -> None:
        self.assertEqual(hro.check(self.s), [])

    def test_check_fails_on_a_stale_quoted_ring_count(self) -> None:
        stale = dict(hro.QUOTED)
        stale[("A", 1e6)] = dict(stale[("A", 1e6)], n=1)
        with mock.patch.object(hro, "QUOTED", stale):
            errors = hro.check(self.s)
        self.assertTrue(any("N:" in e for e in errors), errors)

    def test_check_fails_on_a_stale_quoted_scalar(self) -> None:
        stale = dict(hro.QUOTED_SCALARS, rate_shipped_bps=651.0)
        with mock.patch.object(hro, "QUOTED_SCALARS", stale):
            errors = hro.check(self.s)
        self.assertTrue(any("rate_shipped_bps" in e for e in errors), errors)

    def test_check_fails_when_the_constant_drifts(self) -> None:
        with mock.patch.object(hro, "derived_a", return_value=11.77):
            errors = hro.check(self.s)
        self.assertTrue(any("A_STARVED" in e for e in errors), errors)

    def test_main_check_exit_codes(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(hro.main(["--check"]), 0)
            with mock.patch.object(hro, "derived_a", return_value=1.79), \
                    contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(hro.main(["--check"]), 1)


if __name__ == "__main__":
    unittest.main()
