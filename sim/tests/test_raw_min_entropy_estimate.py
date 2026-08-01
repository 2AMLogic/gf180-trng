#!/usr/bin/env python3
"""Unit tests for sim/tools/raw_min_entropy_estimate.py (issue #12).

Covers the pure math (the MCV estimator and its confidence-degradation
formula) plus an integration check that the tool runs end-to-end against
whatever ``sampler-array-digitize`` records are actually committed --
skipped, not failed, if that family is ever renamed/removed, matching this
repository's convention for PDK-dependent skips (this check has no PDK
dependency, but the same "skip on a missing precondition rather than fail
the whole suite" shape applies).
"""

from __future__ import annotations

import math
import subprocess
import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR / "tools"))

import raw_min_entropy_estimate as est  # noqa: E402


class HHatTests(unittest.TestCase):
    def test_unbiased_is_one_bit(self):
        self.assertAlmostEqual(est.h_hat(0.5), 1.0, places=9)

    def test_fully_biased_is_zero_bits(self):
        self.assertAlmostEqual(est.h_hat(1.0), 0.0, places=9)
        self.assertAlmostEqual(est.h_hat(0.0), 0.0, places=9)

    def test_symmetric_in_p_and_one_minus_p(self):
        self.assertAlmostEqual(est.h_hat(0.3), est.h_hat(0.7), places=12)

    def test_matches_closed_form_two_thirds(self):
        # H = -log2(2/3) for p = 2/3, cross-checked against the same
        # estimator sim/tools/jitter_estimator_calibration_check.py validates.
        self.assertAlmostEqual(est.h_hat(2.0 / 3.0), -math.log2(2.0 / 3.0), places=12)


class ConfidenceDegradationTests(unittest.TestCase):
    def test_se_grows_as_n_shrinks(self):
        _, se_h_small_n = est.confidence_degradation(0.6, 10)
        _, se_h_large_n = est.confidence_degradation(0.6, 400000)
        self.assertGreater(se_h_small_n, se_h_large_n)

    def test_se_p_matches_binomial_formula(self):
        p, n = 0.6, 40
        se_p, _ = est.confidence_degradation(p, n)
        self.assertAlmostEqual(se_p, math.sqrt(p * (1 - p) / n), places=12)

    def test_zero_n_is_nan_not_a_crash(self):
        se_p, se_h = est.confidence_degradation(0.5, 0)
        self.assertTrue(math.isnan(se_p))
        self.assertTrue(math.isnan(se_h))


class SamplePeriodTests(unittest.TestCase):
    def test_reads_tclk_from_the_testbench_manifest(self):
        # Cross-checked against the manifest directly, so this fails loudly
        # if the testbench is ever retuned without updating this tool's
        # assumption about what T_s it is analysing.
        import json

        manifest = json.loads(est.TB_MANIFEST.read_text())
        expected = float(manifest["params"]["tclk"])
        self.assertEqual(est.sample_period_s(), expected)


@unittest.skipUnless(
    list((REPO_ROOT / "sim" / "records").glob("*-sampler-array-digitize-*.md")),
    "no sim/records/*-sampler-array-digitize-*.md evidence committed yet",
)
class EndToEndTests(unittest.TestCase):
    def test_loads_committed_records_and_computes_bits(self):
        records = est.load_records()
        self.assertGreaterEqual(len(records), 1)
        for rec in records:
            self.assertGreater(len(rec.bits), 0)
            self.assertTrue(all(b in (0, 1) for b in rec.bits))

    def test_cli_runs_clean(self):
        result = subprocess.run(
            [sys.executable, str(SIM_DIR / "tools" / "raw_min_entropy_estimate.py")],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("simulation-derived design estimate", result.stdout)


if __name__ == "__main__":
    unittest.main()
