#!/usr/bin/env python3
"""Unit tests for the per-ring liveness monitor (DR-0016).

Three groups, matching ``sim/tests/test_health_test.py``'s structure:

1. The model's contract -- per-ring run detection, saturation, reset, and
   the reused-C_RCT default.
2. Fault injection -- detection-latency targets from DR-0016 (identical in
   form to DR-0002's "detected within C_RCT samples of onset"), reusing the
   declared-synthetic generators in ``sim/tb/ring-liveness-fault-injection/``.
3. RTL/model equivalence -- runs ``design/health_test/ring_liveness.v`` under
   Icarus Verilog against the same stimulus and requires identical pulse
   streams. Skipped (not failed) when ``iverilog`` is not installed, the
   same way ``test_health_test.py``'s equivalence group does.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
TB_DIR = SIM_DIR / "tb" / "ring-liveness-fault-injection"
HT_DIR = REPO_ROOT / "design" / "health_test"

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(TB_DIR))
sys.path.insert(0, str(HT_DIR))

import rct_apt as ht  # noqa: E402
import ring_liveness as rl  # noqa: E402
import ring_source_model as source_model  # noqa: E402

RTL = HT_DIR / "ring_liveness.v"
RTL_TB = TB_DIR / "tb_rtl_equivalence.v"


class DefaultCutoffTests(unittest.TestCase):
    """The monitor reuses DR-0002's C_RCT rather than inventing a new number."""

    def test_default_c_live_equals_c_rct_at_h0(self):
        dut = rl.RingLivenessMonitor()
        self.assertEqual(dut.c_live, ht.c_rct(ht.H0))
        self.assertEqual(dut.c_live, 81)

    def test_from_h_reuses_c_rct_formula(self):
        dut = rl.RingLivenessMonitor.from_h("0.8")
        self.assertEqual(dut.c_live, ht.c_rct("0.8"))
        self.assertEqual(dut.c_live, 51)

    def test_n_rings_must_be_positive(self):
        with self.assertRaises(ValueError):
            rl.RingLivenessMonitor(n_rings=0)

    def test_c_live_must_be_positive(self):
        with self.assertRaises(ValueError):
            rl.RingLivenessMonitor(c_live=-1)


class ModelContractTests(unittest.TestCase):
    def test_fires_exactly_once_for_a_ring_stuck_far_beyond_the_cutoff(self):
        dut = rl.RingLivenessMonitor(n_rings=1, c_live=5)
        events = []
        for i in range(20):
            (stuck,), _ = dut.step([0])
            if stuck:
                events.append(i)
        # The run of identical bits completes at index 4 (the 5th sample);
        # the run counter then saturates rather than wrapping, so a ring
        # stuck far longer than c_live samples produces exactly one pulse.
        self.assertEqual(events, [4])

    def test_does_not_fire_below_cutoff(self):
        dut = rl.RingLivenessMonitor(n_rings=1, c_live=5)
        fired = any(dut.step([1])[0][0] for _ in range(4))
        self.assertFalse(fired)

    def test_resets_the_run_on_a_value_change(self):
        dut = rl.RingLivenessMonitor(n_rings=1, c_live=3)
        seq = [1, 1, 0, 1, 1]  # longest run is 2, never reaches 3
        fired = any(dut.step([b])[0][0] for b in seq)
        self.assertFalse(fired)

    def test_cutoff_of_one_fires_on_the_first_sample(self):
        dut = rl.RingLivenessMonitor(n_rings=1, c_live=1)
        (stuck,), stuck_any = dut.step([0])
        self.assertTrue(stuck)
        self.assertTrue(stuck_any)

    def test_rings_are_independent(self):
        dut = rl.RingLivenessMonitor(n_rings=2, c_live=3)
        # Ring 0 stuck at 1; ring 1 toggles every sample.
        seq = [(1, 0), (1, 1), (1, 0), (1, 1), (1, 0)]
        results = [dut.step(list(row)) for row in seq]
        ring0_events = [i for i, (stuck, _) in enumerate(results) if stuck[0]]
        ring1_events = [i for i, (stuck, _) in enumerate(results) if stuck[1]]
        any_events = [i for i, (_, any_) in enumerate(results) if any_]
        self.assertEqual(ring0_events, [2])  # 3rd consecutive '1' on ring 0
        self.assertEqual(ring1_events, [])
        self.assertEqual(any_events, [2])

    def test_step_requires_n_rings_bits(self):
        dut = rl.RingLivenessMonitor(n_rings=2)
        with self.assertRaises(ValueError):
            dut.step([1])

    def test_reset_clears_state(self):
        dut = rl.RingLivenessMonitor(n_rings=1, c_live=3)
        dut.step([1])
        dut.step([1])
        dut.reset()
        fired = any(dut.step([1])[0][0] for _ in range(2))
        self.assertFalse(fired)  # run restarted from reset, not from 2

    def test_model_is_deterministic(self):
        bits = source_model.healthy_ring_bits("determinism", 4096, 500)

        def run():
            dut = rl.RingLivenessMonitor(n_rings=1)
            return rl.run_stream(dut, [[b] for b in bits])

        self.assertEqual(run(), run())


class FaultInjectionTests(unittest.TestCase):
    """DR-0016's detection-latency target: a stuck ring is detected within
    C_LIVE samples of onset, exactly as DR-0002 states for C_RCT."""

    def test_stuck_ring_detected_within_c_live_samples_of_onset(self):
        dut = rl.RingLivenessMonitor(n_rings=2)
        healthy = [
            list(row)
            for row in zip(
                source_model.healthy_ring_bits("r0", 501, 2000),
                source_model.healthy_ring_bits("r1", 502, 2000),
            )
        ]
        onset = len(healthy)
        other = source_model.healthy_ring_bits("r1-cont", 503, dut.c_live + 50)
        stuck = source_model.stuck_ring_bits(1, dut.c_live + 50)
        fault = [list(row) for row in zip(stuck, other)]
        result = rl.run_stream(dut, healthy + fault)
        ring0_events = result["per_ring_events"][0]
        first = next((i for i in ring0_events if i >= onset), None)
        self.assertIsNotNone(first, "stuck ring was never detected")
        self.assertLessEqual(first - onset, dut.c_live - 1)
        # The healthy ring must never be flagged.
        self.assertEqual(result["per_ring_events"][1], [])

    def test_healthy_pair_produces_no_alarm(self):
        dut = rl.RingLivenessMonitor(n_rings=2)
        rows = [
            list(row)
            for row in zip(
                source_model.healthy_ring_bits("h0", 601, 4 * dut.c_live),
                source_model.healthy_ring_bits("h1", 602, 4 * dut.c_live),
            )
        ]
        result = rl.run_stream(dut, rows)
        self.assertEqual(result["any_events"], [])


@unittest.skipUnless(
    shutil.which("iverilog") and shutil.which("vvp"),
    "Icarus Verilog not installed -- RTL/model equivalence not checked here "
    "(install iverilog to run it; see sim/tb/ring-liveness-fault-injection/README.md)",
)
class RtlEquivalenceTests(unittest.TestCase):
    """The RTL must reproduce the behavioural model pulse for pulse.

    DUT is instantiated at its default parameters (N_RINGS=2, C_LIVE=81) --
    see tb_rtl_equivalence.v's docstring for why parameters are not swept at
    run time here.
    """

    N_RINGS = 2
    C_LIVE = 81

    def test_rtl_defaults_match_c_rct_at_h0(self):
        text = RTL.read_text()
        match = re.search(r"parameter\s+integer\s+C_LIVE\s*=\s*(\w+)", text)
        self.assertIsNotNone(match, f"could not find `parameter integer C_LIVE` in {RTL}")
        self.assertEqual(int(match.group(1)), ht.c_rct(ht.H0))

    def _run_rtl(self, vectors):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            stim = tmp / "stim.mem"
            out = tmp / "out.mem"
            vvp = tmp / "sim.vvp"
            stim.write_text(
                "".join(f"{r1:d}{r0:d}\n" for r0, r1 in vectors)
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
            # line is "SS A": bit0=ring_stuck[1], bit1=ring_stuck[0], bit2=ring_stuck_any
            # (tb_rtl_equivalence.v's %b%b on {ring_stuck, ring_stuck_any}).
            # Re-order to (ring0_stuck, ring1_stuck) to match the model's
            # step()'s (stuck[0], stuck[1]) convention.
            return [
                ((line[1] == "1", line[0] == "1"), line[2] == "1") for line in lines
            ]

    def _model_pulses(self, vectors):
        dut = rl.RingLivenessMonitor(n_rings=self.N_RINGS, c_live=self.C_LIVE)
        pulses = []
        for row in vectors:
            pulses.append(dut.step(list(row)))
        return pulses

    def test_rtl_matches_model_on_a_stuck_ring(self):
        vectors = [(1, 0) for _ in range(300)]  # ring 0 stuck at 1, ring 1 stuck at 0
        self.assertEqual(self._run_rtl(vectors), self._model_pulses(vectors))

    def test_rtl_matches_model_with_one_ring_toggling_and_one_stuck(self):
        toggling = source_model.healthy_ring_bits("rtl-mixed", 701, 300)
        vectors = [(toggling[i], 1) for i in range(300)]  # ring 1 stuck at 1
        self.assertEqual(self._run_rtl(vectors), self._model_pulses(vectors))

    def test_rtl_matches_model_on_two_independent_healthy_rings(self):
        r0 = source_model.healthy_ring_bits("rtl-r0", 801, 500)
        r1 = source_model.healthy_ring_bits("rtl-r1", 802, 500)
        vectors = list(zip(r0, r1))
        self.assertEqual(self._run_rtl(vectors), self._model_pulses(vectors))


if __name__ == "__main__":
    unittest.main()
