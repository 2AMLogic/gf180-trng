#!/usr/bin/env python3
"""Unit tests for the on-die health tests (DR-0002) and their verification
split (DR-0009).

Four groups, matching ``sim/tests/test_conditioner.py``'s structure:

1. The cutoff formulas -- reproduce every row of DR-0002's cutoff table and
   the independent-verification tail probabilities, and check the APT
   degeneracy floor is refused rather than silently accepted.
2. The behavioural model's contract -- RCT run detection, APT window
   recurrence, the start-up counter, and the ``startup_req`` restart
   priority.
3. Fault injection -- detection-latency targets from DR-0002 ("Detection-
   latency targets (acceptance for #11's fault injection)"), reusing the
   declared-synthetic generators in ``sim/tb/health-test-fault-injection/``.
4. RTL/model equivalence -- runs ``design/health_test/rct_apt.v`` under
   Icarus Verilog against the same stimulus and requires identical pulse
   streams. Skipped (not failed) when ``iverilog`` is not installed, the
   same way ``test_conditioner.py``'s equivalence group does.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
TB_DIR = SIM_DIR / "tb" / "health-test-fault-injection"

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(TB_DIR))
sys.path.insert(0, str(REPO_ROOT / "design" / "health_test"))

import rct_apt as ht  # noqa: E402
import fault_injection as source_model  # noqa: E402

RTL = REPO_ROOT / "design" / "health_test" / "rct_apt.v"
RTL_TB = TB_DIR / "tb_rtl_equivalence.v"

# DR-0002's cutoff table (alpha = 2**-40, W = 1024), reproduced exactly.
DR0002_TABLE = {
    "0.1": (401, 1005),
    "0.2": (201, 961),
    "0.3": (135, 915),
    "0.4": (101, 869),
    "0.5": (81, 824),  # H0, draft
    "0.6": (68, 780),
    "0.7": (59, 739),
    "0.8": (51, 699),
    "0.9": (46, 661),
    "1.0": (41, 625),
}

# DR-0002's "APT degeneracy floor" table.
DR0002_DEGENERACY_TABLE = {
    "0.10": 1005,
    "0.08": 1012,
    "0.06": 1019,
    "0.05": 1022,
    "0.04": 1024,  # degenerate: cutoff has reached W
}


class CutoffTableTests(unittest.TestCase):
    """Direct, cheap correctness checks independent of any simulated bitstream."""

    def test_c_rct_matches_dr0002_table(self):
        for h, (c_rct, _) in DR0002_TABLE.items():
            with self.subTest(h=h):
                self.assertEqual(ht.c_rct(h), c_rct)

    def test_c_apt_matches_dr0002_table(self):
        for h, (_, c_apt) in DR0002_TABLE.items():
            with self.subTest(h=h):
                self.assertEqual(ht.c_apt(h), c_apt)

    def test_h0_defaults_match_ratified_draft_values(self):
        self.assertEqual(ht.c_rct(ht.H0), 81)
        self.assertEqual(ht.c_apt(ht.H0), 824)

    def test_degeneracy_table_reproduces_exactly(self):
        for h, c_apt in DR0002_DEGENERACY_TABLE.items():
            with self.subTest(h=h):
                self.assertEqual(ht.c_apt(h), c_apt)

    def test_h_at_or_below_003_is_unsatisfiable(self):
        """DR-0002: 'H <= 0.03: no C <= W satisfies the criterion'."""
        self.assertGreater(ht.c_apt("0.03"), ht.W)
        self.assertEqual(ht.c_apt("0.03"), ht.APT_DEGENERATE)

    def test_independent_verification_tail_probabilities_at_h0(self):
        """DR-0002 amendment A6: Pr(X>=824)=6.44e-13 <= alpha < Pr(X>=823)=1.10e-12."""
        p_824 = ht.apt_tail_probability(824, ht.H0)
        p_823 = ht.apt_tail_probability(823, ht.H0)
        self.assertAlmostEqual(float(p_824), 6.44e-13, delta=1e-14)
        self.assertAlmostEqual(float(p_823), 1.10e-12, delta=1e-13)
        self.assertLessEqual(p_824, ht.ALPHA)
        self.assertGreater(p_823, ht.ALPHA)

    def test_c_rct_requires_positive_h(self):
        with self.assertRaises(ValueError):
            ht.c_rct(0)
        with self.assertRaises(ValueError):
            ht.c_rct(-0.1)

    def test_c_apt_requires_positive_h(self):
        with self.assertRaises(ValueError):
            ht.c_apt(0)


class DegeneracyGuardTests(unittest.TestCase):
    """The construction-time guard against a pathologically low H (DR-0002)."""

    def test_constructing_from_a_degenerate_h_raises(self):
        with self.assertRaises(ValueError):
            ht.HealthTest.from_h("0.03")

    def test_constructing_with_an_explicit_out_of_range_c_apt_raises(self):
        with self.assertRaises(ValueError):
            ht.HealthTest(c_rct=81, c_apt=ht.W + 1, w=ht.W)
        with self.assertRaises(ValueError):
            ht.HealthTest(c_rct=81, c_apt=0, w=ht.W)

    def test_h0_construction_succeeds_and_matches_the_ratified_values(self):
        dut = ht.HealthTest.from_h(ht.H0)
        self.assertEqual((dut.c_rct, dut.c_apt, dut.w, dut.startup_samples), (81, 824, 1024, 1024))

    def test_c_rct_must_be_at_least_one(self):
        with self.assertRaises(ValueError):
            ht.HealthTest(c_rct=0, c_apt=1, w=1)


class RtlDefaultParameterTests(unittest.TestCase):
    """rct_apt.v's default parameters must match rct_apt.py's H0 formulas.

    Verilog parameters cannot be generated from a Python source of truth the
    way design/interface/regmap.py generates trng_regmap.vh/REGMAP.md, so
    this test is the mechanical check that stands in for a `--check` flag:
    if DR-0002's H0 = 0.5 cutoffs ever change on the Python side, this test
    fails until rct_apt.v's defaults are updated to match.
    """

    def _default_parameter(self, name: str) -> int:
        text = RTL.read_text()
        match = re.search(rf"parameter\s+integer\s+{name}\s*=\s*(\w+)", text)
        self.assertIsNotNone(match, f"could not find `parameter integer {name}` in {RTL}")
        value = match.group(1)
        if value == "W":  # STARTUP_SAMPLES defaults to W
            return self._default_parameter("W")
        return int(value)

    def test_rtl_defaults_match_h0_cutoffs(self):
        self.assertEqual(self._default_parameter("C_RCT"), ht.c_rct(ht.H0))
        self.assertEqual(self._default_parameter("C_APT"), ht.c_apt(ht.H0))
        self.assertEqual(self._default_parameter("W"), ht.W)
        self.assertEqual(self._default_parameter("STARTUP_SAMPLES"), ht.W)


def _bits(label: str, n: int, seed: int = 7, h="0.5"):
    stream, _, _ = source_model.biased_bits(label, seed, n, h)
    return stream


class ModelContractTests(unittest.TestCase):
    def test_rct_fires_exactly_once_for_a_source_stuck_far_beyond_the_cutoff(self):
        dut = ht.HealthTest(c_rct=5, c_apt=5, w=8)
        events = []
        for i in range(20):
            fail_rct, _, _ = dut.step(raw_bit=0, raw_valid=True)
            if fail_rct:
                events.append(i)
        # The run of identical bits completes at index 4 (the 5th sample);
        # the run counter then saturates at C_RCT rather than wrapping, so a
        # source stuck for far longer than C_RCT samples produces exactly one
        # pulse, never a repeating one (see rct_apt.v's module docstring).
        self.assertEqual(events, [4])

    def test_rct_does_not_fire_below_cutoff(self):
        dut = ht.HealthTest(c_rct=5, c_apt=5, w=8)
        fired = any(dut.step(raw_bit=1, raw_valid=True)[0] for _ in range(4))
        self.assertFalse(fired)

    def test_rct_resets_the_run_on_a_value_change(self):
        dut = ht.HealthTest(c_rct=3, c_apt=3, w=8)
        seq = [1, 1, 0, 1, 1]  # longest run is 2, never reaches 3
        fired = any(dut.step(raw_bit=b, raw_valid=True)[0] for b in seq)
        self.assertFalse(fired)

    def test_rct_cutoff_of_one_fires_on_the_first_sample(self):
        dut = ht.HealthTest(c_rct=1, c_apt=1, w=1)
        fail_rct, fail_apt, _ = dut.step(raw_bit=0, raw_valid=True)
        self.assertTrue(fail_rct)
        self.assertTrue(fail_apt)

    def test_apt_fires_when_window_recurrence_meets_cutoff(self):
        # W=4, C_APT=3: reference + 3 more matches within the 4-sample window.
        dut = ht.HealthTest(c_rct=100, c_apt=3, w=4)
        bits = [1, 1, 1, 1]  # reference=1, 4 occurrences >= 3
        events = [dut.step(raw_bit=b, raw_valid=True)[1] for b in bits]
        self.assertEqual(events, [False, False, False, True])

    def test_apt_does_not_fire_below_cutoff(self):
        dut = ht.HealthTest(c_rct=100, c_apt=3, w=4)
        bits = [1, 0, 0, 1]  # reference=1, only 2 occurrences (positions 0, 3)
        events = [dut.step(raw_bit=b, raw_valid=True)[1] for b in bits]
        self.assertEqual(events, [False, False, False, False])

    def test_apt_windows_are_non_overlapping_and_reset_after_each_one(self):
        dut = ht.HealthTest(c_rct=100, c_apt=3, w=4)
        bits = [1, 1, 1, 1, 0, 0, 0, 0]  # two back-to-back failing windows
        events = [dut.step(raw_bit=b, raw_valid=True)[1] for b in bits]
        self.assertEqual(events, [False, False, False, True, False, False, False, True])

    def test_startup_pass_fires_after_startup_samples_clean_samples(self):
        dut = ht.HealthTest(c_rct=100, c_apt=8, w=8, startup_samples=8)
        events = [dut.step(raw_bit=i % 2, raw_valid=True)[2] for i in range(16)]
        # Fires once at sample 8 (index 7); the counter saturates and does not
        # re-fire at sample 16 without an intervening failure or restart.
        self.assertEqual(events, [False] * 7 + [True] + [False] * 8)

    def test_a_failure_resets_the_startup_counter(self):
        dut = ht.HealthTest(c_rct=3, c_apt=8, w=8, startup_samples=8)
        for _ in range(2):
            dut.step(raw_bit=1, raw_valid=True)
        self.assertEqual(dut.startup_count, 2)
        dut.step(raw_bit=1, raw_valid=True)  # 3rd identical bit -> RCT fires
        self.assertEqual(dut.startup_count, 0)

    def test_startup_req_discards_the_in_flight_window_and_restarts(self):
        dut = ht.HealthTest(c_rct=100, c_apt=3, w=4, startup_samples=4)
        dut.step(raw_bit=1, raw_valid=True)
        dut.step(raw_bit=1, raw_valid=True)
        self.assertEqual((dut.apt_pos, dut.startup_count), (2, 2))
        dut.step(startup_req=True)
        self.assertEqual((dut.apt_pos, dut.apt_match, dut.startup_count), (0, 0, 0))
        self.assertEqual(dut.restarts, 1)

    def test_startup_req_wins_over_absorbing_the_same_cycle_sample(self):
        """Mirrors crc32_conditioner.py's flush-wins-over-absorb priority."""
        dut = ht.HealthTest(c_rct=1, c_apt=1, w=1)
        fail_rct, fail_apt, startup_pass = dut.step(
            raw_bit=1, raw_valid=True, startup_req=True
        )
        self.assertFalse(fail_rct)
        self.assertFalse(fail_apt)
        self.assertFalse(startup_pass)
        self.assertEqual(dut.samples_seen, 0)

    def test_raw_valid_low_does_not_advance_any_counter(self):
        dut = ht.HealthTest(c_rct=5, c_apt=5, w=8)
        for _ in range(50):
            dut.step(raw_bit=1, raw_valid=False)
        self.assertEqual((dut.rct_run, dut.apt_pos, dut.startup_count, dut.samples_seen), (0, 0, 0, 0))

    def test_model_is_deterministic(self):
        bits = _bits("determinism", 4096)

        def run():
            dut = ht.HealthTest.from_h(ht.H0)
            return ht.run_stream(dut, bits)

        self.assertEqual(run(), run())


class FaultInjectionTests(unittest.TestCase):
    """DR-0002 'Detection-latency targets (acceptance for #11's fault injection)'."""

    def test_stuck_output_detected_within_c_rct_samples_of_onset(self):
        dut = ht.HealthTest.from_h(ht.H0)
        healthy = _bits("stuck-lead-in", 2000, seed=101)
        onset = len(healthy)
        stuck = source_model.constant_bits(1, dut.c_rct + 50)
        result = ht.run_stream(dut, healthy + stuck)
        first = min(
            (i for i in result["rct_events"] + result["apt_events"] if i >= onset),
            default=None,
        )
        self.assertIsNotNone(first, "stuck output was never detected")
        self.assertLessEqual(first - onset, dut.c_rct - 1)

    def test_heavily_biased_stream_detected_within_2w_samples_of_onset(self):
        dut = ht.HealthTest.from_h(ht.H0)
        healthy = _bits("biased-lead-in", 2000, seed=102)
        onset = len(healthy)
        biased, _, _ = source_model.biased_bits("biased-fault", 202, 4 * dut.w, "0.05")
        result = ht.run_stream(dut, healthy + biased)
        first = min(
            (i for i in result["rct_events"] + result["apt_events"] if i >= onset),
            default=None,
        )
        self.assertIsNotNone(first, "heavily biased stream was never detected")
        self.assertLessEqual(first - onset, 2 * dut.w - 1)

    def test_injection_locked_source_detected_within_2w_samples_of_onset(self):
        dut = ht.HealthTest.from_h(ht.H0)
        healthy = _bits("lock-lead-in", 2000, seed=103)
        onset = len(healthy)
        locked = source_model.oscillator_lockup_bits(4 * dut.w)
        result = ht.run_stream(dut, healthy + locked)
        first = min(
            (i for i in result["rct_events"] + result["apt_events"] if i >= onset),
            default=None,
        )
        self.assertIsNotNone(first, "injection-locked source was never detected")
        self.assertLessEqual(first - onset, 2 * dut.w - 1)

    def test_healthy_stream_at_h0_produces_no_alarm(self):
        dut = ht.HealthTest.from_h(ht.H0)
        bits = _bits("healthy-no-alarm", 4 * dut.w, seed=104, h="0.5")
        result = ht.run_stream(dut, bits)
        self.assertEqual(result["rct_events"], [])
        self.assertEqual(result["apt_events"], [])

    def test_false_positive_rate_at_an_inflated_alpha_matches_the_binomial_prediction(self):
        """DR-0002: alpha=2**-40 cannot be observed directly, so verify the
        mechanism at a deliberately inflated alpha where the predicted alarm
        rate is observable in a feasible sample count."""
        h = Decimal("0.5")
        alpha = Decimal("0.05")  # deliberately loose: ~1 in 20 windows should fail
        c_apt_loose = ht.c_apt(h, alpha=alpha, w=64)
        dut = ht.HealthTest(c_rct=1000, c_apt=c_apt_loose, w=64)  # RCT effectively disabled
        n_windows = 4000
        bits = _bits("false-positive", n_windows * 64, seed=105, h=str(h))
        result = ht.run_stream(dut, bits)
        observed_rate = len(result["apt_events"]) / n_windows
        predicted_rate = float(1 - (1 - alpha))  # tail at cutoff is <= alpha by construction
        # Loose statistical check: observed rate should be within an order of
        # magnitude of the target alpha, not a tight bound (few thousand
        # windows is not enough to pin 5% to high precision, only to rule out
        # gross mechanism failure such as never firing or always firing).
        self.assertGreater(observed_rate, 0.0)
        self.assertLess(observed_rate, 10 * alpha)
        self.assertLessEqual(predicted_rate, 1.0)


@unittest.skipUnless(
    shutil.which("iverilog") and shutil.which("vvp"),
    "Icarus Verilog not installed -- RTL/model equivalence not checked here "
    "(install iverilog to run it; see sim/tb/health-test-fault-injection/README.md)",
)
class RtlEquivalenceTests(unittest.TestCase):
    """The RTL must reproduce the behavioural model pulse for pulse.

    DUT is instantiated at its default parameters (C_RCT=81, C_APT=824,
    W=1024, STARTUP_SAMPLES=1024) -- see tb_rtl_equivalence.v's docstring for
    why parameters are not swept at run time here.
    """

    DEFAULT_DUT = dict(c_rct=81, c_apt=824, w=1024, startup_samples=1024)

    def _run_rtl(self, vectors):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            stim = tmp / "stim.mem"
            out = tmp / "out.mem"
            vvp = tmp / "sim.vvp"
            stim.write_text(
                "".join(f"{raw_bit:d}{raw_valid:d}{startup_req:d}\n" for raw_bit, raw_valid, startup_req in vectors)
            )
            subprocess.run(
                ["iverilog", "-g2012", "-o", str(vvp), str(RTL), str(RTL_TB)],
                check=True,
                capture_output=True,
                text=True,
            )
            proc = subprocess.run(
                ["vvp", str(vvp), f"+stim={stim}", f"+out={out}", f"+nvec={len(vectors)}"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertNotIn("FATAL", proc.stdout, proc.stdout)
            lines = out.read_text().split()
            self.assertEqual(len(lines), len(vectors))
            return [(line[0] == "1", line[1] == "1", line[2] == "1") for line in lines]

    def _model_pulses(self, vectors):
        dut = ht.HealthTest(**self.DEFAULT_DUT)
        pulses = []
        for raw_bit, raw_valid, startup_req in vectors:
            pulses.append(
                dut.step(raw_bit=raw_bit, raw_valid=bool(raw_valid), startup_req=bool(startup_req))
            )
        return pulses

    def test_rtl_matches_model_on_a_stuck_source(self):
        vectors = [(1, 1, 0) for _ in range(300)]
        self.assertEqual(self._run_rtl(vectors), self._model_pulses(vectors))

    def test_rtl_matches_model_on_a_healthy_biased_stream_across_full_windows(self):
        bits = _bits("rtl-healthy", 1024 * 3, seed=201)
        vectors = [(b, 1, 0) for b in bits]
        self.assertEqual(self._run_rtl(vectors), self._model_pulses(vectors))

    def test_rtl_matches_model_with_stalls_and_a_startup_restart(self):
        bits = _bits("rtl-mixed", 1024 * 2, seed=202)
        vectors = []
        for i, bit in enumerate(bits):
            if i % 131 == 0:  # sampler stall: no new raw bit this cycle
                vectors.append((0, 0, 0))
            if i == 1500:  # a restart mid-stream (e.g. a cleared alarm)
                vectors.append((0, 0, 1))
            vectors.append((bit, 1, 0))
        self.assertEqual(self._run_rtl(vectors), self._model_pulses(vectors))

    def test_rtl_matches_model_on_a_biased_stream_that_trips_apt(self):
        bits, _, _ = source_model.biased_bits("rtl-biased-fail", 203, 1024 * 3, "0.1")
        vectors = [(b, 1, 0) for b in bits]
        self.assertEqual(self._run_rtl(vectors), self._model_pulses(vectors))


if __name__ == "__main__":
    unittest.main()
