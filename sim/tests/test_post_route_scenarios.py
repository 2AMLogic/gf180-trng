#!/usr/bin/env python3
"""Unit tests for the post-route gate-level re-run's stimulus (#147).

The re-run itself (`sim/tb/trng-top-post-route/run_demo.py`) needs a gate
netlist, an SDF, Icarus Verilog and a cocotb-capable `klt`, none of which
exist on the PR-blocking CI path. These tests cover everything about it that
is **pure Python**, which is more than it sounds:

1. **The stimulus is well-formed and deterministic.** Every scenario builds,
   every row is a complete set of `trng_top` inputs, and building twice gives
   byte-identical stimulus -- the property that makes the two simulation legs
   comparable at all.
2. **Each scenario actually exercises the mechanism it is named for**, checked
   against the behavioural model rather than asserted in a docstring: the
   start-up scenario completes a DR-0002 window, the conditioner scenario
   produces two distinct conditioned words, the two fault scenarios raise
   `ht_alarm` inside their ratified latency bounds, and the scenarios that are
   *not* about alarms never raise one. A scenario that stopped covering its
   mechanism (an off-by-one in a length, a source model changing) would fail
   here in a second instead of after a multi-minute gate-level run.
3. **The DR-0016 trap that made scenario 2 necessary.** `trng_top` has
   per-ring liveness inputs the per-block behavioural testbenches have no
   equivalent of; leaving them idle raises `ht_alarm` at C_LIVE and gates the
   conditioned path. That is asserted directly, so the reason the stimulus
   drives healthy ring taps cannot be lost to a later "simplification".
4. **That the comparison can still see the defect it was built to find.** The
   first run of this testbench found the netlist and the RTL agreeing and both
   disagreeing with the behavioural model, because `TopLevel.step` passed two
   cross-block handoffs combinationally where the RTL registers them (#176,
   fixed in #178). The model now agrees, which raises the obvious question: is
   the agreement real, or has the stimulus stopped being sensitive to that
   kind of skew? `model_probe` answers it in pure Python -- delaying those two
   handoffs a *second* time must still change the outputs. A comparison that
   could not see the defect it was built to find is not evidence that the
   defect is absent.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
TB_DIR = SIM_DIR / "tb" / "trng-top-post-route"

for _path in (TB_DIR, REPO_ROOT / "design" / "trng_top"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import model_probe  # noqa: E402
import scenarios  # noqa: E402
import trng_top as top  # noqa: E402

#: Scenarios whose stimulus must be **sensitive** to a one-cycle skew on the
#: two cross-block handoffs #176/#178 were about: delaying them again (the
#: `model_probe` wrappers, on top of the committed model which already delays
#: them) has to change at least this many cycles of output. These are lower
#: bounds, deliberately loose -- the exact counts move with any change to the
#: stimulus, but "the stimulus can see the skew at all" must not.
#:
#: `smoke` (11 cycles, no start-up window, no conditioner block) is absent on
#: purpose: nothing in it reaches either handoff, so it cannot be sensitive to
#: them, and asserting otherwise would be asserting a coincidence.
SKEW_SENSITIVE_SCENARIOS = {
    "startup-and-regfile": 1,
    "conditioner-blocks": 1,
}

INPUT_KEYS = {
    "raw_bit", "raw_valid", "ring_bit", "reg_sel", "reg_write",
    "reg_addr", "reg_wdata", "str_ready",
}


def run_model(rows, model=None):
    """Step ``rows`` through a top-level model; return ``(outputs, model)``."""
    model = model or top.TopLevel()
    return [model.step(**row) for row in rows], model


def first_alarm(outs) -> int | None:
    for index, out in enumerate(outs):
        if out.ht_alarm:
            return index
    return None


class StimulusShapeTests(unittest.TestCase):
    def test_every_scenario_builds_and_is_registered(self):
        self.assertEqual(
            sorted(scenarios.SCENARIOS), sorted(scenarios.ALL_SCENARIOS)
        )
        for name in scenarios.ALL_SCENARIOS:
            with self.subTest(scenario=name):
                self.assertGreater(len(scenarios.SCENARIOS[name].build()), 0)

    def test_every_row_is_a_complete_set_of_top_level_inputs(self):
        for name in scenarios.ALL_SCENARIOS:
            rows = scenarios.SCENARIOS[name].build()
            with self.subTest(scenario=name):
                for row in rows:
                    self.assertEqual(set(row), INPUT_KEYS)
                    self.assertIn(row["raw_bit"], (0, 1))
                    self.assertEqual(len(row["ring_bit"]), 2)
                    self.assertLess(row["reg_addr"], len(scenarios.regmap.REGISTERS))
                    self.assertLessEqual(row["reg_wdata"], 0xFFFFFFFF)

    def test_stimulus_is_deterministic(self):
        """The two simulation legs are only comparable because the stimulus is
        a pure function of the committed generators and seeds."""
        for name in scenarios.ALL_SCENARIOS:
            with self.subTest(scenario=name):
                self.assertEqual(
                    scenarios.SCENARIOS[name].build(),
                    scenarios.SCENARIOS[name].build(),
                )

    def test_the_three_control_scenarios_share_one_stimulus(self):
        """The annotation control and the settle sweep must drive *exactly*
        what `reg-read-walk` drives -- the only variable between them is the
        sampling offset."""
        base = scenarios.SCENARIOS["reg-read-walk"].build()
        for name in ("reg-read-walk-early-sample", "reg-read-walk-settle-sweep"):
            with self.subTest(scenario=name):
                self.assertEqual(scenarios.SCENARIOS[name].build(), base)

    def test_every_suite_scenario_names_its_behavioural_counterpart(self):
        for name in scenarios.SUITE_SCENARIOS:
            counterpart = REPO_ROOT / scenarios.SCENARIOS[name].counterpart
            with self.subTest(scenario=name):
                self.assertTrue(
                    counterpart.is_dir(),
                    f"{name} names a counterpart that does not exist: {counterpart}",
                )

    def test_the_digital_suite_has_not_grown_a_member_without_a_scenario(self):
        """Every RTL-equivalence testbench under `sim/tb/` is either re-run by a
        scenario here or explicitly accounted for.

        A sixth digital testbench appearing with no scenario and no entry below
        would be silently uncovered by the post-route re-run, so it fails here
        instead. `trng-top-crosscheck` (#178) is the one deliberate exception:
        it is an assembled-RTL-vs-model check, which is exactly what this
        testbench's own `rtl` leg does over the same stimulus, so re-running it
        as a scenario would duplicate rather than add coverage.
        """
        per_block = {
            "conditioner-crc32",
            "health-test-fault-injection",
            "interface-regfile",
            "ring-liveness-fault-injection",
        }
        covered_elsewhere = {"trng-top-crosscheck"}
        found = {
            p.parent.name for p in (SIM_DIR / "tb").glob("*/tb_rtl_equivalence.v")
        }
        self.assertEqual(found, per_block | covered_elsewhere)
        # One scenario per per-block testbench, plus smoke-trng-top's.
        self.assertEqual(len(scenarios.SUITE_SCENARIOS), len(per_block) + 1)


class MechanismCoverageTests(unittest.TestCase):
    """Each scenario exercises what it is named for -- checked, not asserted."""

    def test_smoke_drives_the_recorded_transistor_derived_bits(self):
        rows = scenarios.SCENARIOS["smoke"].build()
        driven = [row["raw_bit"] for row in rows if row["raw_valid"]]
        self.assertEqual(driven, scenarios.raw_source.raw_bits())
        outs, _ = run_model(rows)
        self.assertIsNone(first_alarm(outs), "the smoke scenario must not alarm")

    def test_startup_scenario_completes_exactly_one_dr0002_window(self):
        rows = scenarios.SCENARIOS["startup-and-regfile"].build()
        outs, model = run_model(rows)
        self.assertEqual(model.health.startup_passes, 1)
        self.assertIsNone(first_alarm(outs), "a healthy start-up must not alarm")

    def test_conditioner_scenario_produces_two_distinct_conditioned_words(self):
        rows = scenarios.SCENARIOS["conditioner-blocks"].build()
        outs, model = run_model(rows)
        self.assertGreaterEqual(model.cond.words_out, 2)
        self.assertIsNone(first_alarm(outs))
        reads = [
            out.reg_rdata
            for row, out in zip(rows, outs)
            if row["reg_sel"] and not row["reg_write"]
            and row["reg_addr"] == scenarios.DATA
        ]
        # Three DATA reads by design (see `_conditioner_blocks`): the first two
        # must return the two conditioned words, and the third an empty FIFO.
        # The third read exists because the hardware's registered
        # `cond_valid` (#176) lands a word a cycle later than the model's, and
        # the scenario has to give the slower path room.
        self.assertEqual(len(reads), 3)
        self.assertNotIn(
            0, reads[:2], "a DATA read of 0 means the FIFO was still empty"
        )
        self.assertNotEqual(reads[0], reads[1])
        self.assertEqual(reads[2], 0, "the FIFO should be drained by the third read")

    def test_rct_scenario_alarms_within_the_dr0002_latency_bound(self):
        rows = scenarios.SCENARIOS["rct-stuck-output"].build()
        outs, _ = run_model(rows)
        alarm = first_alarm(outs)
        self.assertIsNotNone(alarm, "a stuck raw source must raise ht_alarm")
        latency = alarm - scenarios.RCT_ONSET_CYCLE
        self.assertGreater(latency, 0)
        # C_RCT samples to detect, plus one cycle for rct_apt.v's registered
        # flag to reach the interface. Anything looser would not be a bound.
        self.assertLessEqual(latency, scenarios.C_RCT + 1)

    def test_ring_scenario_alarms_within_the_dr0016_latency_bound(self):
        rows = scenarios.SCENARIOS["ring1-stuck"].build()
        outs, _ = run_model(rows)
        alarm = first_alarm(outs)
        self.assertIsNotNone(alarm, "a frozen ring must raise ht_alarm")
        latency = alarm - scenarios.RING_ONSET_CYCLE
        self.assertGreater(latency, 0)
        self.assertLessEqual(latency, scenarios.C_LIVE + 1)

    def test_ring_scenario_keeps_the_raw_tap_alive(self):
        """DR-0016's whole point: the dead ring is invisible at the combined
        raw tap, so the raw path must look healthy while the watchdog fires."""
        rows = scenarios.SCENARIOS["ring1-stuck"].build()
        raw = [row["raw_bit"] for row in rows if row["raw_valid"]]
        self.assertGreater(len(raw), scenarios.C_LIVE)
        self.assertIn(0, raw)
        self.assertIn(1, raw)

    def test_reg_read_walk_changes_reg_rdata_on_consecutive_cycles(self):
        """What makes the annotation control discriminating: on idle stimulus,
        sampling early would be indistinguishable from sampling late."""
        rows = scenarios.SCENARIOS["reg-read-walk"].build()
        outs, _ = run_model(rows)
        reads = [
            out.reg_rdata
            for row, out in zip(rows, outs)
            if row["reg_sel"] and not row["reg_write"]
        ]
        self.assertGreaterEqual(len(reads), 16)
        changes = sum(1 for a, b in zip(reads, reads[1:]) if a != b)
        self.assertGreater(
            changes, len(reads) // 2,
            "reg_rdata must change on most consecutive read cycles",
        )


class RingLivenessTrapTests(unittest.TestCase):
    """Why every long scenario drives healthy per-ring taps."""

    def test_idle_ring_inputs_alarm_at_c_live(self):
        idle = [scenarios.cycle(raw_bit=i % 2, raw_valid=True) for i in range(200)]
        outs, _ = run_model(idle)
        alarm = first_alarm(outs)
        self.assertIsNotNone(
            alarm,
            "two idle ring inputs are two dead rings -- if this stops alarming, "
            "DR-0016's watchdog has been weakened",
        )
        self.assertLessEqual(alarm, scenarios.C_LIVE + 1)

    def test_every_scenario_longer_than_c_live_drives_the_ring_taps(self):
        for name in scenarios.ALL_SCENARIOS:
            rows = scenarios.SCENARIOS[name].build()
            if len(rows) <= scenarios.C_LIVE:
                continue
            with self.subTest(scenario=name):
                for ring in range(2):
                    values = {row["ring_bit"][ring] for row in rows}
                    if name == "ring1-stuck" and ring == 0:
                        continue  # this ring is deliberately frozen
                    self.assertEqual(
                        values, {0, 1},
                        f"{name} leaves ring {ring} constant for "
                        f"{len(rows)} cycles (> C_LIVE = {scenarios.C_LIVE})",
                    )


class RegisteredHandoffSensitivityTests(unittest.TestCase):
    """The comparison can still see the defect it was built to find.

    #176 (fixed in #178) was a one-cycle skew on two cross-block handoffs that
    made the behavioural model disagree with both the RTL and the post-route
    netlist. The model now agrees -- so the question these tests answer is
    whether that agreement is *informative*: delaying those two handoffs again
    must still change the outputs. If it did not, the gate-level run's
    model-agreement would be compatible with the skew being back, and the
    record's "all three agree" would be worth nothing.

    Pure Python: no simulator, so it holds on the PR-blocking CI path.
    """

    def test_the_stimulus_is_sensitive_to_a_one_cycle_handoff_skew(self):
        for name, minimum in SKEW_SENSITIVE_SCENARIOS.items():
            rows = scenarios.SCENARIOS[name].build()
            with self.subTest(scenario=name):
                self.assertGreaterEqual(
                    len(model_probe.diverging_cycles(rows)), minimum,
                    f"{name} no longer notices a one-cycle skew on "
                    "ht_startup_pass / cond_word / cond_valid. The gate-level "
                    "run's model-agreement is therefore not evidence that the "
                    "#176 skew is absent -- fix the stimulus, do not relax "
                    "this bound",
                )

    def test_the_probe_only_delays_two_signals(self):
        """The probe must stay a *minimal* perturbation: wrappers around two
        block outputs, nothing else re-implemented."""
        model = model_probe.registered_handoff_model()
        self.assertIsInstance(model.health, model_probe.RegisteredHealthStartup)
        self.assertIsInstance(model.cond, model_probe.RegisteredConditionerOutput)
        self.assertIsInstance(model, top.TopLevel)
        # The wrappers must be transparent for everything except step().
        self.assertEqual(model.cond.k, model_probe.as_committed_model().cond.k)
        self.assertEqual(
            model.health.c_rct, model_probe.as_committed_model().health.c_rct
        )

    def test_scenarios_that_cannot_reach_either_handoff_are_unaffected(self):
        """A scenario with no start-up pass and no conditioned word must be
        untouched by either delay -- otherwise the probe is perturbing more
        than the two handoffs it claims to, and the test above would be
        measuring the wrong thing."""
        for name in ("smoke", "ring1-stuck", "rct-stuck-output"):
            with self.subTest(scenario=name):
                rows = scenarios.SCENARIOS[name].build()
                self.assertEqual(model_probe.diverging_cycles(rows), [])


if __name__ == "__main__":
    unittest.main()
