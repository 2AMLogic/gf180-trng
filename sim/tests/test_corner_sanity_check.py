#!/usr/bin/env python3
"""Unit tests for the pass/fail logic of ``sim/tools/corner_sanity_check.py``.

The tool guards append-only evidence against a silently ignored process-corner
selection. Its ngspice runs are only exercised by ``sim/selftest.sh`` (which
skips without ngspice/PDK), so the decision is factored into the pure
``evaluate`` function and tested here with synthetic drive currents.

Needs no ngspice and no PDK.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SIM_DIR / "tools"))

import corner_sanity_check as csc  # noqa: E402


def ids(ss: float, tt: float, ff: float) -> dict[str, float]:
    return {"ss": ss, "tt": tt, "ff": ff}


def with_spread(pct: float) -> dict[str, float]:
    """tt = 1.0, ss/ff placed symmetrically so (ff - ss) / tt == pct / 100."""
    half = pct / 200.0
    return ids(1.0 - half, 1.0, 1.0 + half)


class EvaluateTest(unittest.TestCase):
    def test_expected_ordering_passes(self) -> None:
        ok, msg = csc.evaluate(ids(0.8e-3, 1.0e-3, 1.2e-3))
        self.assertTrue(ok)
        self.assertIn("PASS", msg)
        self.assertIn("40.00%", msg)

    def test_tt_equal_ss_fails(self) -> None:
        ok, msg = csc.evaluate(ids(1.0e-3, 1.0e-3, 1.2e-3))
        self.assertFalse(ok)
        self.assertIn("FAIL", msg)

    def test_inverted_ordering_fails(self) -> None:
        ok, msg = csc.evaluate(ids(1.2e-3, 1.0e-3, 0.8e-3))
        self.assertFalse(ok)
        self.assertIn("expected Id(ss) < Id(tt) < Id(ff)", msg)

    def test_ff_below_tt_fails(self) -> None:
        ok, msg = csc.evaluate(ids(0.8e-3, 1.0e-3, 0.9e-3))
        self.assertFalse(ok)
        self.assertIn("FAIL", msg)

    def test_spread_just_below_floor_fails(self) -> None:
        ok, msg = csc.evaluate(with_spread(csc.MIN_SPREAD_PCT - 0.01))
        self.assertFalse(ok)
        self.assertIn("spread is only", msg)

    def test_spread_just_above_floor_passes(self) -> None:
        ok, msg = csc.evaluate(with_spread(csc.MIN_SPREAD_PCT + 0.01))
        self.assertTrue(ok)
        self.assertIn("PASS", msg)

    def test_zero_tt_fails_without_raising(self) -> None:
        ok, msg = csc.evaluate(ids(-1.0e-3, 0.0, 1.0e-3))
        self.assertFalse(ok)
        self.assertIn("FAIL", msg)

    def test_negative_tt_fails_without_raising(self) -> None:
        ok, msg = csc.evaluate(ids(-2.0e-3, -1.0e-3, 1.0e-3))
        self.assertFalse(ok)
        self.assertIn("FAIL", msg)


if __name__ == "__main__":
    unittest.main()
