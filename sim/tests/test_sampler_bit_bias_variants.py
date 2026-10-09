#!/usr/bin/env python3
"""Unit tests for ``sim/tools/sampler_bit_bias_variants.py`` (issue #357).

The tool's ``--check`` gates the recorded verdict of issue #86's sampled-bit
experiment (``no-measurable-bit-effect``). ``npm run check:spec`` shows only
that today's corpus still classifies that way. These tests build a synthetic
corpus (six records plus their raw ngspice logs) in a temporary directory,
patch the module's ``RECORDS`` and ``REPO_ROOT``, and check:

1. the arithmetic (``_hamming``, ``Variant.rho`` / ``n_eff`` / ``bias_se``,
   ``Pair`` properties) against hand-computed values;
2. ``classify`` and ``main(["--check"])``: a baseline corpus with no effect
   exits zero, and each way the bit effect can show up -- phase lock, bias,
   serial correlation, injection pulling, an unsettled sampled level -- is
   caught with a non-zero exit.

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

import sampler_bit_bias_variants as sb  # noqa: E402

N = 100
SEEDS = 2

#: Neutral deck: unbiased, uncorrelated, a free-running (non-integer) ring.
NEUTRAL = dict(
    ones_frac=0.5, bit_mean=0.0, ppc1=4.38, ppc2=4.21, period_r1=2.8e-9,
    r={1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}, rail_dev=0.001,
)
#: ring-1 periods per sample for the near-integer, generic and clk-floor rates:
#: only the first sits within RESONANCE_WINDOW of a whole number, none within
#: LOCK_TOLERANCE.
PPC = {"integer": 4.01, "generic": 4.38, "clk-floor": 1000.3}


def record_text(raw_rel: str, deck: dict) -> str:
    bullets = {
        "n_samples": N, "ones_frac": deck["ones_frac"], "bit_mean": deck["bit_mean"],
        "ring1_periods_per_sample": deck["ppc1"], "ring2_periods_per_sample": deck["ppc2"],
        "period_r1": deck["period_r1"], "period_r2": 2.9e-9, "tclk_s": 1.0e-8,
        "worst_rail_dev_v": deck["rail_dev"], "xo_swing_v": 3.3,
    }
    bullets.update({f"r_{lag}": v for lag, v in deck["r"].items()})
    body = "\n".join(f"- `{k}`: {v!r}" for k, v in bullets.items())
    return (
        f"raw:\n  path: {raw_rel}\n\n"
        f"corner:\n  process: tt\n  voltage: 3.3\n  temperature: 27\n\n{body}\n"
    )


class CorpusTestCase(unittest.TestCase):
    """A temporary repo root holding ``sim/records`` and ``sim/raw``."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.records = self.root / "sim" / "records"
        self.records.mkdir(parents=True)
        for name, value in (("REPO_ROOT", self.root), ("RECORDS", self.records)):
            p = mock.patch.object(sb, name, value)
            p.start()
            self.addCleanup(p.stop)

    def write_deck(self, slug: str, deck: dict, streams: list[list[int]] | None = None) -> None:
        raw_rel = f"sim/raw/{slug}"
        raw = self.root / raw_rel
        raw.mkdir(parents=True, exist_ok=True)
        if streams is None:
            streams = [[i % 2 for i in range(N)] for _ in range(SEEDS)]
        for i, bits in enumerate(streams):
            # 3.3 V rails; a bit is "1" when the sampled level is above vdd/2.
            lines = "".join(f"bk = {3.3 * b:.6e}\n" for b in bits)
            (raw / f"tb-run{i}.log").write_text(lines)
        (self.records / f"2026-01-01-{slug}-01.md").write_text(record_text(raw_rel, deck))

    def write_corpus(self, clocked: dict | None = None, static: dict | None = None,
                     per_rate: dict | None = None) -> None:
        """Every rate gets the neutral deck, unless overridden.

        ``clocked``/``static`` override fields of every rate's deck;
        ``per_rate[key] = {"clocked": {...}, "static": {...}}`` override one rate.
        """
        for key, _label, _why in sb.RATES:
            for kind, common in (("clocked", clocked), ("static", static)):
                deck = dict(NEUTRAL, ppc1=PPC[key])
                deck.update(common or {})
                deck.update((per_rate or {}).get(key, {}).get(kind, {}))
                self.write_deck(f"sampler-bit-bias-{kind}-{key}", deck)

    def run_main(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = sb.main(list(args))
        return code, out.getvalue(), err.getvalue()


class HammingTests(unittest.TestCase):
    def test_counts_differing_positions(self) -> None:
        self.assertEqual(sb._hamming([0, 1, 1, 0], [0, 1, 1, 0]), 0)
        self.assertEqual(sb._hamming([0, 1, 1, 0], [1, 1, 0, 0]), 2)
        self.assertEqual(sb._hamming([0, 0, 0], [1, 1, 1]), 3)

    def test_empty_streams(self) -> None:
        self.assertEqual(sb._hamming([], []), 0)


class VariantArithmeticTests(CorpusTestCase):
    def variant(self, deck: dict, streams=None) -> sb.Variant:
        self.write_deck("sampler-bit-bias-clocked-generic", deck, streams)
        return sb._load("sampler-bit-bias-clocked-generic")

    def test_bit_streams_threshold_at_half_supply(self) -> None:
        v = self.variant(NEUTRAL, streams=[[1, 0, 1] + [0] * (N - 3),
                                           [0, 0, 1] + [0] * (N - 3)])
        self.assertEqual(v.streams[0][:3], [1, 0, 1])
        self.assertEqual(v.streams[1][:3], [0, 0, 1])

    def test_seed_divergence_is_mean_pairwise_hamming(self) -> None:
        # Three seeds differing in 1, 2 and 3 positions pairwise-by-construction:
        a = [0] * N
        b = [1] + [0] * (N - 1)          # d(a,b) = 1
        c = [1, 1] + [0] * (N - 2)       # d(a,c) = 2, d(b,c) = 1
        v = self.variant(NEUTRAL, streams=[a, b, c])
        self.assertAlmostEqual(v.seed_divergence, (1 + 2 + 1) / 3)

    def test_rho_removes_the_mean(self) -> None:
        # r_L = m^2 + (1 - m^2) rho with m = 0.5, rho = 0.2 -> r = 0.25 + 0.75 * 0.2
        v = self.variant(dict(NEUTRAL, bit_mean=0.5, ones_frac=0.75,
                              r={1: 0.4, 2: 0.25, 3: 0.25, 4: 0.25}))
        self.assertAlmostEqual(v.rho(1), 0.2)
        self.assertAlmostEqual(v.rho(2), 0.0)
        self.assertIsNone(v.rho(7))  # not recorded

    def test_rho_of_a_constant_stream_is_undefined(self) -> None:
        v = self.variant(dict(NEUTRAL, bit_mean=1.0, ones_frac=1.0,
                              r={1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}))
        self.assertIsNone(v.rho(1))
        self.assertEqual(v.n_eff, 1.0)  # one constant is one observation

    def test_n_eff_shrinks_with_serial_correlation(self) -> None:
        # m = 0, so rho = r. rho_1 = 0.5, others 0 -> N / (1 + 2 * 0.5) = N / 2.
        v = self.variant(dict(NEUTRAL, r={1: 0.5, 2: 0.0, 3: 0.0, 4: 0.0}))
        self.assertAlmostEqual(v.n_eff, N / 2)
        # Uncorrelated -> all N samples count.
        self.assertAlmostEqual(self.variant(NEUTRAL).n_eff, float(N))

    def test_bias_se_from_effective_count(self) -> None:
        # p = 0.5, n_eff = N: 2 * sqrt(0.25 / 100) = 0.1
        self.assertAlmostEqual(self.variant(NEUTRAL).bias_se, 0.1)


class PairArithmeticTests(CorpusTestCase):
    def pair(self, clocked: dict, static: dict, key: str = "generic") -> sb.Pair:
        self.write_deck(f"sampler-bit-bias-clocked-{key}", dict(NEUTRAL, **clocked))
        self.write_deck(f"sampler-bit-bias-static-{key}", dict(NEUTRAL, **static))
        label, why = next((l, w) for k, l, w in sb.RATES if k == key)
        return sb.Pair(key, label, why,
                       sb._load(f"sampler-bit-bias-clocked-{key}"),
                       sb._load(f"sampler-bit-bias-static-{key}"))

    def test_lock_margin_is_distance_to_nearest_integer(self) -> None:
        self.assertAlmostEqual(self.pair(dict(ppc1=4.38), {}).lock_margin, 0.38)
        self.assertAlmostEqual(self.pair(dict(ppc1=3.9), {}).lock_margin, 0.1)
        self.assertAlmostEqual(self.pair(dict(ppc1=4.0003), {}).lock_margin, 0.0003)

    def test_pull_and_frequency_shift(self) -> None:
        p = self.pair(dict(ppc1=4.40, period_r1=2.7e-9), dict(ppc1=4.38, period_r1=2.8e-9))
        self.assertAlmostEqual(p.pull, 0.02)
        # (static - clocked) / static = 0.1e-9 / 2.8e-9: positive = clocked is faster.
        self.assertAlmostEqual(p.frequency_shift, 0.1 / 2.8)

    def test_bias_sigma_in_combined_standard_errors(self) -> None:
        # clocked p = 0.75 (bias 0.5), static p = 0.5 (bias 0), no correlation.
        p = self.pair(dict(bit_mean=0.5, ones_frac=0.75, r={1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25}),
                      {})
        se_c = 2 * math.sqrt(0.75 * 0.25 / N)
        se_s = 2 * math.sqrt(0.25 / N)
        self.assertAlmostEqual(p.bias_delta, 0.5)
        self.assertAlmostEqual(p.bias_se, math.hypot(se_c, se_s))
        self.assertAlmostEqual(p.bias_sigma, 0.5 / math.hypot(se_c, se_s))

    def test_rho_delta_sigma_picks_the_worst_lag(self) -> None:
        p = self.pair(dict(r={1: 0.0, 2: 0.3, 3: 0.1, 4: 0.0}), {})
        lag, sigma = p.rho_delta_sigma
        self.assertEqual(lag, 2)
        self.assertAlmostEqual(sigma, 0.3 / math.sqrt(2.0 / N))

    def test_rho_delta_ignores_a_static_deck_with_more_structure(self) -> None:
        p = self.pair({}, dict(r={1: 0.5, 2: 0.0, 3: 0.0, 4: 0.0}))
        self.assertEqual(p.rho_delta_sigma[1], 0.0)

    def test_decorrelated_reference(self) -> None:
        # N * (1 - m_c * m_s) / 2 with m_c = 0.5, m_s = -0.5 -> 100 * 1.25 / 2
        p = self.pair(dict(bit_mean=0.5, ones_frac=0.75, r={1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25}),
                      dict(bit_mean=-0.5, ones_frac=0.25, r={1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25}))
        self.assertAlmostEqual(p.decorrelated_reference, 62.5)

    def test_mismatched_bit_counts_are_rejected(self) -> None:
        self.write_deck("sampler-bit-bias-clocked-generic", NEUTRAL)
        self.write_deck("sampler-bit-bias-static-generic", NEUTRAL)
        clocked = sb._load("sampler-bit-bias-clocked-generic")
        static = sb._load("sampler-bit-bias-static-generic")
        static.n += 1
        with self.assertRaises(sb.RecordError):
            sb.Pair("generic", "generic", "", clocked, static)


class ClassifyTests(CorpusTestCase):
    def verdict(self, **overrides) -> tuple[str, str]:
        self.write_corpus(**overrides)
        return sb.classify(sb.load_pairs())

    def test_neutral_corpus_has_no_measurable_effect(self) -> None:
        self.assertEqual(self.verdict()[0], "no-measurable-bit-effect")

    def test_phase_lock_is_a_bit_effect(self) -> None:
        verdict, why = self.verdict(per_rate={"integer": {"clocked": {"ppc1": 4.0001}}})
        self.assertEqual(verdict, "bit-effect")
        self.assertIn("PHASE-LOCKED", why)

    def test_lock_tolerance_boundary(self) -> None:
        inside = 4 + sb.LOCK_TOLERANCE * 0.5
        outside = 4 + sb.LOCK_TOLERANCE * 2
        self.assertEqual(
            self.verdict(per_rate={"integer": {"clocked": {"ppc1": inside}}})[0], "bit-effect")
        self.assertEqual(
            self.verdict(per_rate={"integer": {"clocked": {"ppc1": outside}}})[0],
            "no-measurable-bit-effect")

    def test_bias_difference_is_a_bit_effect(self) -> None:
        verdict, why = self.verdict(per_rate={"generic": {"clocked": dict(
            bit_mean=0.5, ones_frac=0.75, r={1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25})}})
        self.assertEqual(verdict, "bit-effect")
        self.assertIn("BIAS", why)

    def test_added_serial_correlation_is_a_bit_effect(self) -> None:
        verdict, why = self.verdict(per_rate={"generic": {"clocked": dict(
            r={1: 0.6, 2: 0.0, 3: 0.0, 4: 0.0})}})
        self.assertEqual(verdict, "bit-effect")
        self.assertIn("SERIAL CORRELATION", why)

    def test_resonant_frequency_shift_is_injection_pulling(self) -> None:
        # Shift is 5 % on resonance, 1 % off it: ratio 5x > PULL_RESONANCE_FACTOR.
        shifted = lambda frac: {"clocked": {"period_r1": 2.8e-9 * (1 - frac)}}
        verdict, why = self.verdict(per_rate={
            "integer": shifted(0.05), "generic": shifted(0.01), "clk-floor": shifted(0.01)})
        self.assertEqual(verdict, "bit-effect")
        self.assertIn("INJECTION PULLING", why)

    def test_uniform_frequency_shift_is_a_static_load_not_pulling(self) -> None:
        shifted = {"clocked": {"period_r1": 2.8e-9 * 0.95}}
        verdict, _ = self.verdict(per_rate={k: shifted for k in PPC})
        self.assertEqual(verdict, "no-measurable-bit-effect")


class CheckGateTests(CorpusTestCase):
    def test_check_passes_on_a_neutral_corpus(self) -> None:
        self.write_corpus()
        code, out, _ = self.run_main("--check")
        self.assertEqual(code, 0)
        self.assertIn("OK", out)

    def test_check_fails_when_the_verdict_leaves_the_recorded_one(self) -> None:
        self.write_corpus(per_rate={"integer": {"clocked": {"ppc1": 4.0001}}})
        code, _, err = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("bit-effect", err)

    def test_check_fails_on_an_unsettled_sampled_level(self) -> None:
        self.write_corpus(per_rate={"generic": {"static": {"rail_dev": 0.2}}})
        code, _, err = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("rail", err)

    def test_rail_deviation_boundary(self) -> None:
        self.write_corpus(clocked={"rail_dev": 0.09})
        self.assertEqual(self.run_main("--check")[0], 0)
        self.write_corpus(clocked={"rail_dev": 0.11})
        self.assertEqual(self.run_main("--check")[0], 1)

    def test_check_is_a_gate_on_the_recorded_verdict_only(self) -> None:
        # A neutral corpus against a recorded verdict that says "effect": stale.
        self.write_corpus()
        with mock.patch.object(sb, "RECORDED_VERDICT", "bit-effect"):
            self.assertEqual(self.run_main("--check")[0], 1)

    def test_ungated_mode_never_fails_on_the_verdict(self) -> None:
        self.write_corpus(per_rate={"integer": {"clocked": {"ppc1": 4.0001}}})
        with mock.patch.object(sb, "RECORDED_VERDICT", None):
            code, out, _ = self.run_main("--check")
        self.assertEqual(code, 0)
        self.assertIn("not gated", out)

    def test_missing_records_are_an_error(self) -> None:
        code, _, err = self.run_main("--check")
        self.assertEqual(code, 2)
        self.assertIn("error", err)

    def test_truncated_raw_output_is_an_error(self) -> None:
        self.write_corpus()
        log = next((self.root / "sim" / "raw").rglob("*-run0.log"))
        log.write_text("bk = 0.000000e+00\n")
        self.assertEqual(self.run_main("--check")[0], 2)

    def test_report_mode_runs_on_a_neutral_corpus(self) -> None:
        self.write_corpus()
        code, out, _ = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("Verdict: no-measurable-bit-effect", out)


if __name__ == "__main__":
    unittest.main()
