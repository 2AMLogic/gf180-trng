#!/usr/bin/env python3
"""Unit tests for ``sim/tools/array_sizing.py`` (issue #357).

``array_sizing.py --check`` guards DR-0007 §2's sizing inequality and the
DR-0010 jitter-energy constant. ``npm run check:spec`` shows it passes against
today's corpus; these tests show it *fails* when it should, on small synthetic
record sets in a temporary directory (``RECORDS`` is patched; the design
netlist ring count and the re-derivation of ``a`` are patched too, so no
committed record, netlist or ngspice is involved).

Two halves: the arithmetic against hand-computed values, and ``main(["--check"])``
returning non-zero on a violating set and zero on a satisfying one.
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

import array_sizing as sizing  # noqa: E402
import jitter_energy_law  # noqa: E402

KT_300 = sizing.KB * 300.15  # 27 degC


def array_record_text(*, period: float, temp_c: float = 27.0, vdd: float = 3.3,
                      i_ring: float = 1.0e-4, rings: int = 2) -> str:
    bullets = {}
    for i in range(1, rings + 1):
        bullets[f"period_r{i}"] = period
        bullets[f"i_r{i}_a"] = -i_ring  # supply current is recorded negative
    bullets.update(
        i_tree_a=-2.0e-5, e_cycle_r1_j=1.0e-12, c_eff_node_r1_f=1.0e-14,
        ring_swing_v=3.2, xo_swing_v=3.3, xo_trans_per_s=1.0e8,
    )
    body = "\n".join(f"- `{k}`: {v!r}" for k, v in bullets.items())
    return (
        "---\nstatus: valid\ncorner:\n  process: tt\n"
        f"  voltage: {vdd}\n  temperature: {temp_c}\n---\n\n## Result\n\n{body}\n"
    )


def fake_point(corner: str, stem: str):
    return SimpleNamespace(rec=SimpleNamespace(corner=corner, stem=stem))


class DedupeByCornerTests(unittest.TestCase):
    def test_distinct_corners_are_all_kept(self) -> None:
        pts = [fake_point("tt/27/3.30", "x-ro-array-core-power-01"),
               fake_point("ss/125/2.97", "x-ro-array-core-power-02")]
        self.assertEqual(sizing.dedupe_by_corner(pts), pts)

    def test_full_grid_family_wins_regardless_of_order(self) -> None:
        power = fake_point("tt/27/3.30", "x-ro-array-core-power-01")
        pvtq = fake_point("tt/27/3.30", "x-ro-array-core-pvt-q-01")
        self.assertEqual(sizing.dedupe_by_corner([power, pvtq]), [pvtq])
        self.assertEqual(sizing.dedupe_by_corner([pvtq, power]), [pvtq])

    def test_same_family_duplicate_keeps_the_first(self) -> None:
        a = fake_point("tt/27/3.30", "x-ro-array-core-power-01")
        b = fake_point("tt/27/3.30", "x-ro-array-core-power-02")
        self.assertEqual(sizing.dedupe_by_corner([a, b]), [a])


class ArrayPointArithmeticTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def point(self, text: str, a: float = sizing.A_JITTER_ENERGY):
        path = self.root / "2026-01-01-ro-array-core-power-01.md"
        # Records must carry a lifecycle status (#425).
        path.write_text(text)
        return sizing.ArrayPoint(sizing.Record(path), a=a)

    def test_ring_count_and_powers_are_read_off_the_record(self) -> None:
        p = self.point(array_record_text(period=1.0e-9, rings=3))
        self.assertEqual(p.n, 3)
        self.assertEqual(p.currents, [1.0e-4] * 3)  # magnitudes
        self.assertAlmostEqual(p.p_rings / (3 * 1.0e-4 * 3.3), 1.0)
        self.assertAlmostEqual(p.p_total / (p.p_rings + 2.0e-5 * 3.3), 1.0)

    def test_g_matches_hand_computation(self) -> None:
        # Per ring: a * kT / P / T0^2, with P = 1e-4 A * 3.3 V and T0 = 1 ns.
        p = self.point(array_record_text(period=1.0e-9, rings=2), a=2.0)
        per_ring = 2.0 * KT_300 / (1.0e-4 * 3.3) / (1.0e-9) ** 2
        self.assertAlmostEqual(p.g / (2 * per_ring), 1.0)

    def test_q_array_and_max_rate(self) -> None:
        p = self.point(array_record_text(period=1.0e-9, rings=2))
        self.assertAlmostEqual(p.q_array(500.0), p.g / 500.0)
        # R_max is where Q_array(1/R) == M * Q_H0.
        self.assertAlmostEqual(
            p.q_array(p.max_rate_bps()) / (sizing.MARGIN_M * sizing.Q_H0), 1.0
        )

    def test_corner_label_and_kelvin(self) -> None:
        p = self.point(array_record_text(period=1.0e-9, temp_c=-40.0, vdd=2.97))
        self.assertEqual(p.rec.corner, "tt/-40/2.97")
        self.assertAlmostEqual(p.rec.temp_k, 233.15)


class CheckGateTests(unittest.TestCase):
    """``main`` against a synthetic corpus: shipped array = 2 rings."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.patch(sizing, "RECORDS", self.root)
        self.patch(sizing, "shipped_ring_count", lambda: 2)
        self.set_derived(sizing.A_JITTER_ENERGY)

    def patch(self, obj, name, value) -> None:
        p = mock.patch.object(obj, name, value)
        p.start()
        self.addCleanup(p.stop)

    def set_derived(self, a: float | None) -> None:
        self.patch(
            sizing, "derived_law_constant",
            lambda: (a, "synthetic" if a is not None else "could not be re-derived"),
        )

    def write(self, name: str, text: str) -> None:
        (self.root / name).write_text(text)

    def run_main(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = sizing.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_check_passes_when_inequality_holds_at_every_corner(self) -> None:
        # g ~ 45, so Q_array(500 bps) ~ 0.09 >> M * Q_H0 = 6e-3.
        self.write("2026-01-01-ro-array-core-power-01.md", array_record_text(period=1.0e-9))
        self.write("2026-01-01-ro-array-core-pvt-q-01.md",
                   array_record_text(period=1.0e-9, temp_c=125.0, vdd=2.97))
        code, out, _ = self.run_main("--check")
        self.assertEqual(code, 0)
        self.assertIn("OK", out)

    def test_check_fails_when_one_corner_violates_the_inequality(self) -> None:
        self.write("2026-01-01-ro-array-core-power-01.md", array_record_text(period=1.0e-9))
        # A slow ring at another corner: g ~ 0.45, Q_array ~ 9e-4 < 6e-3.
        self.write("2026-01-01-ro-array-core-pvt-q-01.md",
                   array_record_text(period=1.0e-8, temp_c=125.0, vdd=2.97))
        code, _, err = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("tt/125/2.97", err)

    def test_check_depends_on_the_rate(self) -> None:
        self.write("2026-01-01-ro-array-core-power-01.md", array_record_text(period=1.0e-9))
        self.assertEqual(self.run_main("--check", "--rate", "500")[0], 0)
        self.assertEqual(self.run_main("--check", "--rate", "1e6")[0], 1)

    def test_check_fails_when_stated_constant_drifts_from_derivation(self) -> None:
        self.write("2026-01-01-ro-array-core-power-01.md", array_record_text(period=1.0e-9))
        self.set_derived(sizing.A_JITTER_ENERGY * (1 + 2 * sizing.A_TOLERANCE))
        code, _, err = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("drifted", err)

    def test_check_tolerates_drift_within_tolerance(self) -> None:
        self.write("2026-01-01-ro-array-core-power-01.md", array_record_text(period=1.0e-9))
        self.set_derived(sizing.A_JITTER_ENERGY * (1 + sizing.A_TOLERANCE / 2))
        self.assertEqual(self.run_main("--check")[0], 0)

    def test_check_fails_when_derivation_cannot_run(self) -> None:
        self.write("2026-01-01-ro-array-core-power-01.md", array_record_text(period=1.0e-9))
        self.set_derived(None)
        code, _, err = self.run_main("--check")
        self.assertEqual(code, 2)
        self.assertIn("FAIL", err)

    def test_unpatched_derivation_failure_is_reported_not_swallowed(self) -> None:
        # Restore the real derived_law_constant, but give the law an empty corpus.
        self.patch(sizing, "derived_law_constant", self._real_derived)
        self.write("2026-01-01-ro-array-core-power-01.md", array_record_text(period=1.0e-9))
        empty = tempfile.TemporaryDirectory()
        self.addCleanup(empty.cleanup)
        with mock.patch.object(jitter_energy_law, "RECORDS", Path(empty.name)):
            value, note = sizing.derived_law_constant()
        self.assertIsNone(value)
        self.assertIn("could not be re-derived", note)

    _real_derived = staticmethod(sizing.derived_law_constant)

    def test_check_rejects_an_overridden_constant(self) -> None:
        self.write("2026-01-01-ro-array-core-power-01.md", array_record_text(period=1.0e-9))
        self.assertEqual(self.run_main("--check", "--a", "3.0")[0], 2)

    def test_records_of_a_different_array_size_are_excluded(self) -> None:
        # Only a 3-ring record exists; the shipped array has 2 rings.
        self.write("2026-01-01-ro-array-core-power-01.md",
                   array_record_text(period=1.0e-9, rings=3))
        code, _, err = self.run_main("--check")
        self.assertEqual(code, 2)
        self.assertIn("no record measures the shipped 2-ring array", err)

    def test_no_records_is_an_error(self) -> None:
        self.assertEqual(self.run_main("--check")[0], 2)

    def test_variant_testbench_records_are_not_read_as_shipped(self) -> None:
        # A -BUFFERED variant slug must not match the shipped-array glob, even
        # though its numbers would violate the inequality.
        self.write("2026-01-01-ro-array-core-power-01.md", array_record_text(period=1.0e-9))
        self.write("2026-01-01-ro-array-core-power-BUFFERED-01.md",
                   array_record_text(period=1.0e-7, temp_c=125.0))
        self.assertEqual(self.run_main("--check")[0], 0)


if __name__ == "__main__":
    unittest.main()
