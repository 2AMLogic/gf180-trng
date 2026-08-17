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
4. **The #176 finding, pinned without a simulator.** The gate-level run showed
   that the post-route netlist and the RTL agree exactly and that both differ
   from the behavioural model on 259 cycles, all explained by two cross-block
   handoffs the RTL registers and the model does not. Because the probe model
   (`model_probe.registered_handoff_model`) is what agrees with the hardware,
   the *count* is computable in pure Python -- so these tests hold the
   published number to the model, and will fail the day #176 is fixed, which
   is exactly when the record's prose needs revisiting.
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

#: The published per-scenario divergence between the behavioural model and the
#: implementation (RTL and post-route netlist alike), from the #147 record.
#: Every other scenario must be zero. Update these two numbers only alongside
#: the record and #176 -- they are a published result, not a fixture.
PUBLISHED_MODEL_DIVERGENCE = {
    "startup-and-regfile": 1,
    "conditioner-blocks": 269,
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

    def test_the_five_member_suite_is_still_five_members(self):
        """`sim/tb/*/tb_rtl_equivalence.v` plus `smoke-trng-top` is the digital
        functional suite this re-runs. A sixth would need its own scenario, so
        it fails here rather than being silently uncovered."""
        equivalence = sorted(
            p.parent.name for p in (SIM_DIR / "tb").glob("*/tb_rtl_equivalence.v")
        )
        self.assertEqual(
            equivalence,
            [
                "conditioner-crc32",
                "health-test-fault-injection",
                "interface-regfile",
                "ring-liveness-fault-injection",
            ],
        )
        self.assertEqual(len(scenarios.SUITE_SCENARIOS), len(equivalence) + 1)


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


class RegisteredHandoffFindingTests(unittest.TestCase):
    """#176, pinned in pure Python.

    The gate-level run established that the probe model agrees with both the
    RTL and the post-route netlist exactly. So the number of cycles on which
    the as-committed model differs from the probe *is* the number of cycles on
    which it differs from the hardware -- computable here, with no simulator.
    """

    def test_published_divergence_counts_still_hold(self):
        for name in scenarios.SUITE_SCENARIOS:
            rows = scenarios.SCENARIOS[name].build()
            expected = PUBLISHED_MODEL_DIVERGENCE.get(name, 0)
            with self.subTest(scenario=name):
                self.assertEqual(
                    len(model_probe.diverging_cycles(rows)), expected,
                    "the model-vs-implementation divergence #147's record "
                    "publishes has changed. If #176 was fixed, expect 0 here "
                    "and update the record's prose; if not, something else "
                    "moved and the record is now wrong",
                )

    def test_the_probe_only_delays_two_signals(self):
        """The probe must be a *minimal* hypothesis: wrappers around two block
        outputs, nothing else re-implemented."""
        model = model_probe.registered_handoff_model()
        self.assertIsInstance(model.health, model_probe.RegisteredHealthStartup)
        self.assertIsInstance(model.cond, model_probe.RegisteredConditionerOutput)
        self.assertIsInstance(model, top.TopLevel)
        # The wrappers must be transparent for everything except step().
        self.assertEqual(model.cond.k, model_probe.as_committed_model().cond.k)
        self.assertEqual(
            model.health.c_rct, model_probe.as_committed_model().health.c_rct
        )

    def test_the_divergence_is_not_an_artefact_of_the_probe_alone(self):
        """A scenario with no conditioned word and no start-up pass must be
        unaffected by either delay -- otherwise the probe is changing more than
        the two handoffs it claims to."""
        for name in ("smoke", "ring1-stuck", "rct-stuck-output"):
            with self.subTest(scenario=name):
                rows = scenarios.SCENARIOS[name].build()
                self.assertEqual(model_probe.diverging_cycles(rows), [])


if __name__ == "__main__":
    unittest.main()
