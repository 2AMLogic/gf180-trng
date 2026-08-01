#!/usr/bin/env python3
"""Unit tests for sim/tools/statistical_battery.py (issue #12).

Covers the regularized incomplete gamma function (against the closed-form
``Q(1/2, x) = erfc(sqrt(x))`` identity, independent of any hand-transcribed
reference table), each of the four battery tests against a known-degenerate
input (should FAIL loudly), and the sample-count floors that trigger
"omitted" rather than a truncated/misleading result.
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR / "tools"))

import statistical_battery as battery  # noqa: E402


class GammaInccTests(unittest.TestCase):
    def test_matches_erfc_identity(self):
        # Q(1/2, x) = erfc(sqrt(x)) for any x >= 0 -- a closed-form identity
        # that does not depend on any transcribed table.
        for x in (1e-6, 0.05, 0.5, 1.0, 3.0, 10.0, 40.0, 80.0):
            got = battery.gammaincc(0.5, x)
            want = math.erfc(math.sqrt(x))
            self.assertAlmostEqual(got, want, delta=1e-10, msg=f"x={x}")

    def test_zero_x_is_one(self):
        self.assertEqual(battery.gammaincc(2.5, 0.0), 1.0)

    def test_domain_errors(self):
        with self.assertRaises(battery.BatteryError):
            battery.gammaincc(0.0, 1.0)
        with self.assertRaises(battery.BatteryError):
            battery.gammaincc(1.0, -1.0)

    def test_monotonically_decreasing_in_x(self):
        a = 2.0
        xs = [0.1, 1.0, 5.0, 20.0]
        values = [battery.gammaincc(a, x) for x in xs]
        self.assertEqual(values, sorted(values, reverse=True))


class MonobitTests(unittest.TestCase):
    def test_all_ones_fails(self):
        bits = [1] * 200
        r = battery.monobit_test(bits)
        self.assertFalse(r["omitted"])
        self.assertLess(r["p_value"], 1e-6)

    def test_balanced_alternating_passes(self):
        bits = [i % 2 for i in range(200)]
        r = battery.monobit_test(bits)
        self.assertFalse(r["omitted"])
        self.assertGreater(r["p_value"], 0.5)  # perfectly balanced -> S_n = 0

    def test_below_minimum_is_omitted(self):
        r = battery.monobit_test([1, 0, 1])
        self.assertTrue(r["omitted"])
        self.assertIn("below", r["reason"])


class BlockFrequencyTests(unittest.TestCase):
    def test_all_zero_blocks_fail(self):
        bits = [0] * 2048
        r = battery.block_frequency_test(bits, m=128)
        self.assertFalse(r["omitted"])
        self.assertLess(r["p_value"], 1e-6)

    def test_too_short_is_omitted(self):
        r = battery.block_frequency_test([1] * 50, m=128)
        self.assertTrue(r["omitted"])


class RunsTests(unittest.TestCase):
    def test_perfectly_alternating_is_too_many_runs(self):
        # Alternating 0101... is balanced (passes the prerequisite) but has
        # the maximum possible number of runs -- a classic runs-test failure.
        bits = [i % 2 for i in range(1000)]
        r = battery.runs_test(bits)
        self.assertIsNotNone(r["p_value"])
        self.assertLess(r["p_value"], 1e-6)

    def test_unbalanced_stream_not_applicable(self):
        bits = [1] * 990 + [0] * 10
        r = battery.runs_test(bits)
        self.assertIsNone(r.get("p_value"))
        self.assertIn("not applicable", r["reason"])

    def test_too_short_is_omitted(self):
        r = battery.runs_test([1, 0] * 10)
        self.assertTrue(r["omitted"])


class LongestRunTests(unittest.TestCase):
    def test_all_ones_fails(self):
        bits = [1] * 4096
        r = battery.longest_run_test(bits)
        self.assertFalse(r["omitted"])
        self.assertLess(r["p_value"], 1e-6)

    def test_below_minimum_omitted(self):
        r = battery.longest_run_test([1, 0] * 30)  # n=60 < 128
        self.assertTrue(r["omitted"])

    def test_above_table_range_omitted(self):
        # SHA-256 counter-mode filler well above the M=8 table's validated
        # upper edge (6272) -- must be omitted, not silently applied.
        bits = battery.bits_from_file  # sanity: attribute exists
        self.assertTrue(callable(bits))
        big = [i % 2 for i in range(10000)]
        r = battery.longest_run_test(big)
        self.assertTrue(r["omitted"])
        self.assertIn("6272", r["reason"])


class RunBatteryTests(unittest.TestCase):
    def test_returns_four_tests_in_fixed_order(self):
        bits = [i % 2 for i in range(4096)]
        results = battery.run_battery(bits)
        self.assertEqual(len(results), 4)
        self.assertEqual(
            [r["name"].split(" (")[0] for r in results],
            ["monobit", "block frequency", "runs", "longest run of ones"],
        )

    def test_pass_field_only_set_when_not_omitted_or_na(self):
        bits = [1] * 990 + [0] * 10  # too unbalanced for the runs prerequisite
        results = battery.run_battery(bits)
        runs_result = next(r for r in results if r["name"] == "runs")
        self.assertNotIn("pass", runs_result)


class SelfCheckTests(unittest.TestCase):
    def test_module_self_check_passes(self):
        self.assertEqual(battery.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
