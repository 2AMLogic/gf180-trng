#!/usr/bin/env python3
"""Unit tests for ``sim/tools/worst_corner_entropy.py`` (#396).

That tool is the ``entropy`` gate in ``npm run check:spec``: ``--check`` exits
non-zero unless the records still support the stated entropy-binding corner,
the covered PVT grid is complete, and the two array record families agree
where they overlap. Its only other test runs it as a subprocess against the
real corpus, which proves the gate passes today but not that it can fail.

Two halves, the same contract as ``layout/tests/test_verify.py``:

1. The arithmetic helpers (``_binom_tail``, ``_norm_cdf``, ``_cv``,
   ``grid_coverage``, ``report_family_agreement``) against values worked out
   by hand.
2. The gate itself. The record loader and the pieces of ``main`` that read
   unrelated records (Monte Carlo sections, the ring count, the starved-cell
   constants) are patched to a synthetic 27-corner record set, and
   ``main(["--check"])`` must return 0 for the consistent set and non-zero
   once any one of three invariants is broken: a grid corner is missing, the
   two record families disagree by more than ``FAMILY_AGREEMENT_TOL``, or the
   minimum-Q corner is not ``MEASURED_MIN_Q_CORNER``.

3. Lifecycle filtering (issue #427) in the two Monte Carlo readers that glob
   records themselves: ``report_mc_ro_freq`` and ``_sampler_offset`` read
   synthetic records from a temporary directory and must skip a record whose
   frontmatter says ``status: superseded``, unless asked for a historical read.

Needs no ngspice, no PDK, and reads nothing under ``sim/records/``.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SIM_DIR / "tools"))

import worst_corner_entropy as wce  # noqa: E402

RINGS = 2
#: The three corners the older ``ro-array-core-power`` family also measures.
SHARED = ("tt/27/3.30", "ff/-40/3.63", "ss/-40/3.63")
_PROC_SLOWNESS = {"tt": 1.0, "ff": 0.8, "ss": 1.3}


class FakeRecord:
    """The slice of ``array_sizing.Record`` that the tool reads."""

    def __init__(self, family: str, process: str, temp_c: float, vdd: float,
                 period_scale: float = 1.0) -> None:
        self.process, self.temp_c, self.vdd = process, temp_c, vdd
        self.temp_k = temp_c + 273.15
        self.stem = f"2026-01-01-ro-array-core-{family}-001-{self.corner}"
        # Slower at ss and when hot, faster at high supply. With a constant
        # ring current, P = I*V grows with V, so Q = a*kT/(P*T0^2) is smallest
        # at the hot, slow, high-supply corner: ss/125/3.63.
        period = (1e-9 * _PROC_SLOWNESS[process] * (1 + (temp_c + 40) / 300)
                  * (1 + (3.63 - vdd) * 0.01) * period_scale)
        self.values = {
            "period_r1": period, "period_r2": period * 1.06,
            "i_r1_a": 1e-4, "i_r2_a": 1e-4, "i_tree_a": 5e-5,
            "e_cycle_r1_j": 1e-13, "c_eff_node_r1_f": 1e-14,
            "ring_swing_v": 3.0, "xo_swing_v": 3.0, "xo_trans_per_s": 1e8,
            "p_total_w": 1e-3,
        }

    @property
    def corner(self) -> str:
        return f"{self.process}/{self.temp_c:.0f}/{self.vdd:.2f}"


def grid_records(skip: str | None = None, scale_for: dict[str, float] | None = None
                 ) -> list[FakeRecord]:
    scale_for = scale_for or {}
    out = []
    for proc in wce.GRID_PROCESSES:
        for t in wce.GRID_TEMPS_C:
            for v in wce.GRID_SUPPLIES_V:
                rec = FakeRecord("pvt-q", proc, t, v)
                if rec.corner == skip:
                    continue
                if rec.corner in scale_for:
                    rec = FakeRecord("pvt-q", proc, t, v, scale_for[rec.corner])
                out.append(rec)
    return out


def power_records(drift: float = 0.0) -> list[FakeRecord]:
    """The older three-point family; ``drift`` perturbs its periods and currents."""
    out = []
    for corner in SHARED:
        proc, t, v = corner.split("/")
        rec = FakeRecord("power", proc, float(t), float(v))
        for key in wce.AGREEMENT_KEYS:
            if key in rec.values:
                rec.values[key] *= 1.0 + drift
        out.append(rec)
    return out


def run_check(pvt_q: list[FakeRecord], power: list[FakeRecord]) -> tuple[int, str, str]:
    """Run ``main(["--check"])`` against synthetic record families."""

    def fake_load(glob: str) -> list[FakeRecord]:
        if glob == wce.PVT_Q_GLOB:
            return pvt_q
        if glob == wce.POWER_GLOB:
            return power
        raise AssertionError(f"unexpected record glob {glob!r}")

    out, err = io.StringIO(), io.StringIO()
    with contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch.object(wce, "load", fake_load))
        stack.enter_context(mock.patch.object(wce, "shipped_ring_count", lambda: RINGS))
        stack.enter_context(mock.patch.object(wce, "starved_cell_constants",
                                              lambda: (1.8, 1.9)))
        for name in ("report_mc_ro_freq", "report_mc_sampler_offset", "report_bias_margins"):
            stack.enter_context(mock.patch.object(wce, name, lambda *a, **k: None))
        stack.enter_context(contextlib.redirect_stdout(out))
        stack.enter_context(contextlib.redirect_stderr(err))
        code = wce.main(["--check"])
    return code, out.getvalue(), err.getvalue()


class ArithmeticTests(unittest.TestCase):
    def test_binom_tail_edges(self) -> None:
        self.assertEqual(wce._binom_tail(10, 0, 0.3), 1.0)
        self.assertEqual(wce._binom_tail(10, -5, 0.3), 1.0)
        self.assertEqual(wce._binom_tail(10, 11, 0.3), 0.0)

    def test_binom_tail_hand_sums(self) -> None:
        # Bin(3, 1/2), X >= 2: (3 + 1) / 8
        self.assertAlmostEqual(wce._binom_tail(3, 2, 0.5), 0.5)
        # Bin(4, 1/2), X >= 3: (4 + 1) / 16
        self.assertAlmostEqual(wce._binom_tail(4, 3, 0.5), 0.3125)
        # Bin(2, 0.1), X >= 1: 1 - 0.9^2
        self.assertAlmostEqual(wce._binom_tail(2, 1, 0.1), 0.19)
        # k = n: p^n
        self.assertAlmostEqual(wce._binom_tail(5, 5, 0.2), 0.2**5)

    def test_norm_cdf(self) -> None:
        self.assertEqual(wce._norm_cdf(0.0), 0.5)
        self.assertAlmostEqual(wce._norm_cdf(1.0), 0.8413447, places=6)
        self.assertAlmostEqual(wce._norm_cdf(-1.96) + wce._norm_cdf(1.96), 1.0)

    def test_cv(self) -> None:
        # mean 2, sample sd 1 (n - 1 denominator)
        self.assertAlmostEqual(wce._cv([1.0, 2.0, 3.0]), 0.5)
        self.assertEqual(wce._cv([4.0, 4.0, 4.0]), 0.0)
        self.assertEqual(wce._cv([7.0]), 0.0)

    def test_grid_coverage_complete_and_missing(self) -> None:
        def coverage(records: list[FakeRecord]) -> tuple[int, list[str]]:
            with mock.patch.object(wce, "load", lambda glob: records), \
                    mock.patch.object(wce, "shipped_ring_count", lambda: RINGS):
                return wce.grid_coverage()

        self.assertEqual(coverage(grid_records()), (27, []))
        self.assertEqual(coverage(grid_records(skip="ss/125/3.63")), (26, ["ss/125/3.63"]))

    def test_grid_coverage_ignores_other_ring_counts(self) -> None:
        # A record of a superseded array size must not count as coverage.
        with mock.patch.object(wce, "load", lambda glob: grid_records()), \
                mock.patch.object(wce, "shipped_ring_count", lambda: RINGS + 1):
            self.assertEqual(wce.grid_coverage(), (0, [
                f"{p}/{t:.0f}/{v:.2f}" for p in wce.GRID_PROCESSES
                for t in wce.GRID_TEMPS_C for v in wce.GRID_SUPPLIES_V]))

    def _agreement(self, power: list[FakeRecord]) -> float:
        def fake_load(glob: str) -> list[FakeRecord]:
            return grid_records() if glob == wce.PVT_Q_GLOB else power

        with mock.patch.object(wce, "load", fake_load), \
                contextlib.redirect_stdout(io.StringIO()):
            return wce.report_family_agreement()

    def test_family_agreement_is_largest_relative_difference(self) -> None:
        self.assertEqual(self._agreement(power_records()), 0.0)
        # new = old / 1.05 is not a clean fraction; use old = new * 1.25 so
        # |new - old| / old = 0.25 / 1.25 = 0.2 exactly.
        self.assertAlmostEqual(self._agreement(power_records(drift=0.25)), 0.2)

    def test_family_agreement_no_shared_points(self) -> None:
        self.assertEqual(self._agreement([]), 0.0)


class GateTests(unittest.TestCase):
    def test_consistent_set_passes(self) -> None:
        code, out, err = run_check(grid_records(), power_records())
        self.assertEqual(code, 0, err)
        self.assertIn(f"OK: {wce.MEASURED_MIN_Q_CORNER} minimizes Q", out)
        self.assertIn("27/27 points measured", out)
        self.assertEqual(err, "")

    def test_family_agreement_within_tolerance_passes(self) -> None:
        drift = wce.FAMILY_AGREEMENT_TOL / 4
        code, _out, err = run_check(grid_records(), power_records(drift=drift))
        self.assertEqual(code, 0, err)

    def test_missing_grid_corner_fails(self) -> None:
        code, out, err = run_check(grid_records(skip="tt/27/3.30"), power_records())
        self.assertNotEqual(code, 0)
        self.assertIn("covered PVT grid is incomplete (26/27)", err)
        self.assertIn("tt/27/3.30", err)
        self.assertNotIn("OK:", out)

    def test_families_disagreeing_beyond_tolerance_fails(self) -> None:
        drift = wce.FAMILY_AGREEMENT_TOL * 3
        code, out, err = run_check(grid_records(), power_records(drift=drift))
        self.assertNotEqual(code, 0)
        self.assertIn("two array record families differ", err)
        self.assertNotIn("OK:", out)

    def test_wrong_minimum_q_corner_fails(self) -> None:
        # Speed the stated binding corner up 2x (Q ~ 1/T0^2): another corner
        # now has the smallest Q.
        records = grid_records(scale_for={wce.MEASURED_MIN_Q_CORNER: 0.5})
        code, out, err = run_check(records, power_records())
        self.assertNotEqual(code, 0)
        self.assertIn("measured minimum-Q corner is not the stated", err)
        self.assertIn("DOES NOT MATCH", out)
        self.assertNotIn("OK:", out)

    def test_wrong_minimum_corner_is_only_failure(self) -> None:
        records = grid_records(scale_for={wce.MEASURED_MIN_Q_CORNER: 0.5})
        _code, _out, err = run_check(records, power_records())
        self.assertNotIn("incomplete", err)
        self.assertNotIn("record families differ", err)


def _frontmatter(status: str | None, *, extra: str = "") -> str:
    head = "---\n" + (f"status: {status}\n" if status is not None else "")
    return head + extra + "---\n\n"


class LifecycleTestCase(unittest.TestCase):
    """A temporary repo root holding ``sim/records`` and its raw logs."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.records = self.root / "sim" / "records"
        self.records.mkdir(parents=True)
        for name, value in (("REPO_ROOT", self.root), ("RECORDS", self.records)):
            p = mock.patch.object(wce, name, value)
            p.start()
            self.addCleanup(p.stop)


class McFreqLifecycleTests(LifecycleTestCase):
    def write_mc_freq(self, stem: str, status: str | None, *, body: str = "") -> None:
        raw_rel = f"sim/records/raw/{stem}"
        raw = self.root / raw_rel
        raw.mkdir(parents=True)
        for i, (p1, p2) in enumerate(((2.0e-9, 1.9e-9), (2.02e-9, 1.89e-9))):
            (raw / f"seed{i}.log").write_text(f"m_period_r1 = {p1!r}\nm_period_r2 = {p2!r}\n")
        text = _frontmatter(status, extra=f"raw:\n  path: {raw_rel}/\n") + body
        (self.records / f"{stem}.md").write_text(text)

    def report(self, **kwargs) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            wce.report_mc_ro_freq(**kwargs)
        return out.getvalue()

    def test_superseded_record_is_omitted_by_default(self) -> None:
        self.write_mc_freq("2026-01-01-ro-array-core-mc-freq-01", "valid")
        self.write_mc_freq("2026-01-02-ro-array-core-mc-freq-01", "superseded")
        out = self.report()
        self.assertIn("2026-01-01-ro-array-core-mc-freq-01: 2 mismatch seeds", out)
        self.assertNotIn("2026-01-02-ro-array-core-mc-freq-01", out)

    def test_historical_read_lists_superseded_records(self) -> None:
        self.write_mc_freq("2026-01-01-ro-array-core-mc-freq-01", "valid")
        self.write_mc_freq("2026-01-02-ro-array-core-mc-freq-01", "superseded")
        out = self.report(include_superseded=True)
        self.assertIn("2026-01-01-ro-array-core-mc-freq-01: 2 mismatch seeds", out)
        self.assertIn("2026-01-02-ro-array-core-mc-freq-01: 2 mismatch seeds", out)

    def test_superseded_only_family_reports_no_valid_record(self) -> None:
        self.write_mc_freq("2026-01-01-ro-array-core-mc-freq-01", "superseded")
        out = self.report()
        self.assertIn("no valid sim/records/*-ro-array-core-mc-freq-[0-9]*.md", out)
        self.assertNotIn("mismatch seeds", out)

    def test_body_status_line_does_not_override_frontmatter(self) -> None:
        self.write_mc_freq("2026-01-01-ro-array-core-mc-freq-01", "valid",
                           body="Quoted from an older record:\n\nstatus: superseded\n")
        self.assertIn("2 mismatch seeds", self.report())

    def test_unreadable_lifecycle_names_the_record(self) -> None:
        for status in (None, "draft"):
            with self.subTest(status=status):
                for old in self.records.glob("*.md"):
                    old.unlink()
                stem = f"2026-01-01-ro-array-core-mc-freq-0{1 if status is None else 2}"
                self.write_mc_freq(stem, status)
                with self.assertRaisesRegex(RuntimeError, stem):
                    self.report()

    def test_duplicate_status_names_the_record(self) -> None:
        stem = "2026-01-01-ro-array-core-mc-freq-01"
        self.write_mc_freq(stem, "valid\nstatus: valid")
        with self.assertRaisesRegex(RuntimeError, f"{stem}.*exactly one"):
            self.report()


class SamplerOffsetLifecycleTests(LifecycleTestCase):
    CORNER = "tt/27/3.30"

    def write_offset(self, stem: str, status: str | None, mean: float, *,
                     body: str = "") -> None:
        corner = "corner:\n  process: tt\n  temperature: 27\n  voltage: 3.30\n"
        text = (_frontmatter(status, extra=corner) + body
                + f"- `dtrip_v`: mean {mean!r} over 30 seeds (sd 0.01, 1% of mean)\n")
        (self.records / f"{stem}.md").write_text(text)

    def test_lexically_newer_superseded_record_is_not_selected(self) -> None:
        self.write_offset("2026-01-01-sampler-dff-mc-offset-01", "valid", 1.70)
        self.write_offset("2026-01-02-sampler-dff-mc-offset-01", "superseded", 1.80)
        offset, _sd, vdd, n, stem = wce._sampler_offset(self.CORNER)
        self.assertEqual(stem, "2026-01-01-sampler-dff-mc-offset-01")
        self.assertAlmostEqual(offset, 1.70 - 0.5 * vdd)
        self.assertEqual(n, 30)

    def test_historical_read_selects_the_superseded_record(self) -> None:
        self.write_offset("2026-01-01-sampler-dff-mc-offset-01", "valid", 1.70)
        self.write_offset("2026-01-02-sampler-dff-mc-offset-01", "superseded", 1.80)
        stem = wce._sampler_offset(self.CORNER, include_superseded=True)[4]
        self.assertEqual(stem, "2026-01-02-sampler-dff-mc-offset-01")

    def test_superseded_only_corner_is_missing_evidence(self) -> None:
        self.write_offset("2026-01-01-sampler-dff-mc-offset-01", "superseded", 1.70)
        with self.assertRaisesRegex(RuntimeError, "no valid .* at corner"):
            wce._sampler_offset(self.CORNER)

    def test_body_status_line_does_not_override_frontmatter(self) -> None:
        # The pre-#427 regex matched `status: superseded` anywhere in the file.
        self.write_offset("2026-01-01-sampler-dff-mc-offset-01", "valid", 1.70,
                          body="An earlier draft said:\n\nstatus: superseded\n\n")
        self.assertEqual(wce._sampler_offset(self.CORNER)[4],
                         "2026-01-01-sampler-dff-mc-offset-01")

    def test_missing_unknown_and_duplicate_status_name_the_record(self) -> None:
        for status in (None, "draft", "valid\nstatus: superseded"):
            with self.subTest(status=status):
                for old in self.records.glob("*.md"):
                    old.unlink()
                stem = "2026-01-01-sampler-dff-mc-offset-01"
                self.write_offset(stem, status, 1.70)
                with self.assertRaisesRegex(RuntimeError, stem):
                    wce._sampler_offset(self.CORNER)


if __name__ == "__main__":
    unittest.main()
