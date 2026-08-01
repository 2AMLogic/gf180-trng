#!/usr/bin/env python3
"""Unit tests for the digital conditioner (DR-0008) and its verification
split (DR-0009).

Three groups:

1. The behavioural model's contract -- compression ratio, per-block state
   clear, flush-on-gate, flush-on-mode-switch, determinism.
2. The SP 800-90B conditioning arithmetic the DR's entropy accounting quotes.
3. RTL/model equivalence -- runs ``design/conditioner/crc32_conditioner.v``
   under Icarus Verilog against the same stimulus and requires identical
   output words. Skipped (not failed) when ``iverilog`` is not installed, the
   same way the PDK-dependent sim stages skip.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
TB_DIR = SIM_DIR / "tb" / "conditioner-crc32"

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(TB_DIR))
sys.path.insert(0, str(REPO_ROOT / "design" / "conditioner"))

import crc32_conditioner as cond  # noqa: E402
import source_model  # noqa: E402
import sp800_90b  # noqa: E402

RTL = REPO_ROOT / "design" / "conditioner" / "crc32_conditioner.v"
RTL_TB = TB_DIR / "tb_rtl_equivalence.v"


def _bits(label: str, n: int, seed: int = 7):
    stream = source_model.uniform_words(label, seed)
    return [next(stream) & 1 for _ in range(n)]


class ModelContractTests(unittest.TestCase):
    def test_k_and_block_bits_match_dr0008(self):
        self.assertEqual(cond.K, 8)
        self.assertEqual(cond.WORD_BITS, 32)
        self.assertEqual(cond.BLOCK_BITS, 256)

    def test_compression_ratio_is_exactly_k(self):
        bits = _bits("ratio", 256 * 40)
        words = cond.condition_bits(bits)
        self.assertEqual(len(words), 40)
        self.assertEqual(len(bits) / (len(words) * cond.WORD_BITS), cond.K)

    def test_partial_block_produces_no_word(self):
        self.assertEqual(cond.condition_bits(_bits("partial", 255)), [])
        self.assertEqual(len(cond.condition_bits(_bits("partial", 256))), 1)

    def test_state_is_cleared_between_blocks(self):
        """Each word must depend on exactly BLOCK_BITS raw bits and no earlier one."""
        block_a = _bits("a", 256, seed=11)
        block_b = _bits("b", 256, seed=12)
        joint = cond.condition_bits(block_a + block_b)
        self.assertEqual(joint[0], cond.condition_bits(block_a)[0])
        self.assertEqual(joint[1], cond.condition_bits(block_b)[0])

    def test_output_is_deterministic(self):
        bits = _bits("determinism", 256 * 8)
        self.assertEqual(cond.condition_bits(bits), cond.condition_bits(bits))

    def test_stuck_at_zero_source_gives_all_zero_words(self):
        """A dead source must not be laundered into a plausible-looking stream."""
        words = cond.condition_bits([0] * (256 * 4))
        self.assertEqual(words, [0, 0, 0, 0])

    def test_stuck_at_one_source_is_not_all_zero(self):
        """Stated as a limit, not a feature: only stuck-at-0 is visible at the
        output. Detecting a stuck-at-1 source is the health tests' job on the
        raw stream (DR-0002), never the conditioner's."""
        words = cond.condition_bits([1] * (256 * 4))
        self.assertTrue(all(w != 0 for w in words))

    def test_single_bit_flip_changes_the_word(self):
        bits = _bits("avalanche", 256)
        flipped = list(bits)
        flipped[123] ^= 1
        self.assertNotEqual(cond.condition_bits(bits), cond.condition_bits(flipped))

    def test_flush_discards_the_partial_block(self):
        dut = cond.Conditioner()
        for bit in _bits("flush-partial", 100):
            dut.step(raw_bit=bit, raw_valid=True)
        self.assertEqual(dut.count, 100)
        dut.step(flush=True)
        self.assertEqual(dut.count, 0)
        self.assertEqual(dut.state, cond.INIT_STATE)
        self.assertEqual(dut.bits_discarded, 100)

    def test_no_pre_flush_bit_influences_a_later_word(self):
        """The DR-0002 requirement, checked by construction."""
        pre = _bits("pre", 200, seed=21)
        post = _bits("post", 256 * 3, seed=22)

        dut = cond.Conditioner()
        for bit in pre:
            dut.step(raw_bit=bit, raw_valid=True)
        dut.step(flush=True)
        words = []
        for bit in post:
            word, valid = dut.step(raw_bit=bit, raw_valid=True)
            if valid:
                words.append(word)

        self.assertEqual(words, cond.condition_bits(post))

    def test_gate_deassert_holds_the_conditioner_cleared(self):
        """`en` low models the health-test gate / start-up test window."""
        dut = cond.Conditioner()
        for bit in _bits("gated", 500):
            _, valid = dut.step(raw_bit=bit, raw_valid=True, en=False)
            self.assertFalse(valid)
        self.assertEqual(dut.count, 0)
        self.assertEqual(dut.raw_absorbed, 0)

    def test_flush_wins_over_a_bit_presented_in_the_same_cycle(self):
        dut = cond.Conditioner()
        dut.step(raw_bit=1, raw_valid=True, flush=True)
        self.assertEqual(dut.raw_absorbed, 0)
        self.assertEqual(dut.state, cond.INIT_STATE)

    def test_out_mode_switch_flush_is_the_same_mechanism(self):
        """DR-0001 requires a flush on an OUT_MODE switch in either direction;
        it is the same `flush` port as the DR-0002 gate, so one mechanism
        covers both. This test pins that so the two cannot drift apart."""
        bits = _bits("mode-switch", 256 * 4)
        switch_at = 300
        dut = cond.Conditioner()
        words = []
        for i, bit in enumerate(bits):
            if i == switch_at:  # OUT_MODE raw -> conditioned, say
                dut.step(flush=True)
            word, valid = dut.step(raw_bit=bit, raw_valid=True)
            if valid:
                words.append(word)
        after = cond.condition_bits(bits[switch_at:])
        self.assertEqual(len(after), 2)
        self.assertEqual(words[-len(after):], after)

    def test_raw_valid_low_does_not_advance_the_lfsr(self):
        dut = cond.Conditioner()
        for _ in range(50):
            dut.step(raw_bit=1, raw_valid=False)
        self.assertEqual(dut.count, 0)
        self.assertEqual(dut.state, cond.INIT_STATE)

    def test_reset_clears_everything(self):
        dut = cond.Conditioner()
        for bit in _bits("reset", 300):
            dut.step(raw_bit=bit, raw_valid=True)
        dut.reset()
        self.assertEqual((dut.state, dut.count, dut.cond_valid), (cond.INIT_STATE, 0, False))

    def test_word_serialisation_is_lsb_first(self):
        self.assertEqual(cond.word_to_bits(0x00000001)[0], 1)
        self.assertEqual(cond.word_to_bits(0x80000000)[-1], 1)


class SourceModelTests(unittest.TestCase):
    def test_p_one_round_trips_through_min_entropy(self):
        for h in ("0.5", "0.106456", "0.03"):
            p1 = source_model.p_one_for_min_entropy(h)
            back = source_model.min_entropy_for_p_one(p1)
            self.assertLess(abs(back - Decimal(h)), Decimal("1e-9"))

    def test_stream_is_bit_identical_across_calls(self):
        a, _, _ = source_model.biased_bits("x", 1, 4096, "0.5")
        b, _, _ = source_model.biased_bits("x", 1, 4096, "0.5")
        self.assertEqual(a, b)

    def test_stream_depends_on_seed_and_label(self):
        a, _, _ = source_model.biased_bits("x", 1, 4096, "0.5")
        b, _, _ = source_model.biased_bits("x", 2, 4096, "0.5")
        c, _, _ = source_model.biased_bits("y", 1, 4096, "0.5")
        self.assertNotEqual(a, b)
        self.assertNotEqual(a, c)

    def test_measured_bias_tracks_the_declared_min_entropy(self):
        bits, p1_target, _ = source_model.biased_bits("bias", 5, 200000, "0.5")
        measured = sum(bits) / len(bits)
        self.assertLess(abs(measured - float(p1_target)), 0.005)

    def test_pack_lsb_first(self):
        self.assertEqual(source_model.pack_lsb_first([1, 0, 0, 0, 0, 0, 0, 0]), b"\x01")
        self.assertEqual(source_model.pack_lsb_first([0, 0, 0, 0, 0, 0, 0, 1]), b"\x80")


class Sp800_90bArithmeticTests(unittest.TestCase):
    N_IN = cond.BLOCK_BITS

    def test_non_vetted_cap_is_the_binding_term_at_the_design_target(self):
        h_out = sp800_90b.non_vetted_output_entropy(self.N_IN, 32, 32, Decimal("0.5") * self.N_IN)
        self.assertEqual(h_out, sp800_90b.NON_VETTED_CAP * 32)

    def test_break_even_matches_the_value_quoted_in_dr0008(self):
        be = sp800_90b.break_even_h_per_bit(self.N_IN, 32, 32)
        self.assertAlmostEqual(float(be), 0.106456, places=6)

    def test_below_break_even_the_conditioner_is_the_binding_term(self):
        h_out = sp800_90b.non_vetted_output_entropy(self.N_IN, 32, 32, Decimal("0.03") * self.N_IN)
        self.assertLess(h_out, sp800_90b.NON_VETTED_CAP * 32)
        self.assertAlmostEqual(float(h_out), 0.03 * self.N_IN, places=6)

    def test_zero_input_entropy_gives_zero_output_entropy(self):
        self.assertEqual(sp800_90b.output_entropy(self.N_IN, 32, 32, 0), 0)

    def test_output_entropy_is_monotone_in_input_entropy(self):
        values = [
            sp800_90b.output_entropy(self.N_IN, 32, 32, Decimal(h))
            for h in ("1", "8", "16", "27", "64", "128")
        ]
        self.assertEqual(values, sorted(values))

    def test_break_even_halves_when_the_block_doubles(self):
        be_k8 = sp800_90b.break_even_h_per_bit(256, 32, 32)
        be_k16 = sp800_90b.break_even_h_per_bit(512, 32, 32)
        self.assertAlmostEqual(float(be_k8 / be_k16), 2.0, places=6)


def _stimulus(vectors) -> str:
    """One 4-bit binary vector per line: raw_bit, raw_valid, en, flush."""
    return "".join(
        f"{raw_bit:d}{raw_valid:d}{en:d}{flush:d}\n" for raw_bit, raw_valid, en, flush in vectors
    )


def _model_words(vectors):
    dut = cond.Conditioner()
    words = []
    for raw_bit, raw_valid, en, flush in vectors:
        word, valid = dut.step(
            raw_bit=raw_bit, raw_valid=bool(raw_valid), en=bool(en), flush=bool(flush)
        )
        if valid:
            words.append(word)
    return words


@unittest.skipUnless(
    shutil.which("iverilog") and shutil.which("vvp"),
    "Icarus Verilog not installed -- RTL/model equivalence not checked here "
    "(install iverilog to run it; see sim/tb/conditioner-crc32/README.md)",
)
class RtlEquivalenceTests(unittest.TestCase):
    """The RTL must reproduce the behavioural model word for word.

    This is what makes DR-0009's "the behavioural model is normative" a
    checkable statement rather than a preference.
    """

    def _run_rtl(self, vectors):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            stim = tmp / "stim.mem"
            out = tmp / "out.hex"
            vvp = tmp / "sim.vvp"
            stim.write_text(_stimulus(vectors))
            subprocess.run(
                ["iverilog", "-g2012", "-o", str(vvp), str(RTL), str(RTL_TB)],
                check=True,
                capture_output=True,
                text=True,
            )
            proc = subprocess.run(
                [
                    "vvp",
                    str(vvp),
                    f"+stim={stim}",
                    f"+out={out}",
                    f"+nvec={len(vectors)}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertNotIn("FATAL", proc.stdout, proc.stdout)
            if not out.exists():
                return []
            return [int(line, 16) for line in out.read_text().split()]

    def test_rtl_matches_model_on_a_plain_stream(self):
        bits = _bits("rtl-plain", 256 * 6, seed=31)
        vectors = [(b, 1, 1, 0) for b in bits]
        self.assertEqual(self._run_rtl(vectors), _model_words(vectors))

    def test_rtl_matches_model_with_stalls_gates_and_flushes(self):
        bits = _bits("rtl-mixed", 256 * 6, seed=32)
        vectors = []
        for i, bit in enumerate(bits):
            if i % 97 == 0:  # sampler stall: no new raw bit this cycle
                vectors.append((0, 0, 1, 0))
            if i == 700:  # health-test failure: gate + flush
                vectors.append((1, 1, 1, 1))
                vectors.extend((0, 0, 0, 0) for _ in range(5))  # held gated
            if i == 1300:  # OUT_MODE switch
                vectors.append((0, 0, 1, 1))
            vectors.append((bit, 1, 1, 0))
        self.assertEqual(self._run_rtl(vectors), _model_words(vectors))

    def test_rtl_matches_model_on_a_stuck_at_zero_source(self):
        vectors = [(0, 1, 1, 0) for _ in range(256 * 3)]
        rtl = self._run_rtl(vectors)
        self.assertEqual(rtl, _model_words(vectors))
        self.assertEqual(rtl, [0, 0, 0])


class DemoRunnerTests(unittest.TestCase):
    """The demonstration runner's scenarios must stay reproducible."""

    def setUp(self):
        sys.path.insert(0, str(TB_DIR))
        import run_demo  # noqa: PLC0415

        self.run_demo = run_demo

    def test_gate_flush_scenario_keeps_post_flush_words_independent(self):
        result = self.run_demo.run_scenario("gate-flush")
        self.assertTrue(result["flush_tail_independent_of_pre_flush_bits"])
        self.assertGreater(result["flush_events"], 0)
        self.assertGreater(result["bits_discarded_by_flush"], 0)

    def test_measured_compression_ratio_is_k_in_every_scenario(self):
        for name in self.run_demo.SCENARIOS:
            with self.subTest(scenario=name):
                result = self.run_demo.run_scenario(name)
                self.assertAlmostEqual(result["k_measured"], cond.K, places=9)

    def test_scenarios_are_bit_reproducible(self):
        first = self.run_demo.run_scenario("h050")["cond_stream_sha256"]
        second = self.run_demo.run_scenario("h050")["cond_stream_sha256"]
        self.assertEqual(first, second)
        self.assertEqual(len(first), len(hashlib.sha256(b"").hexdigest()))


if __name__ == "__main__":
    unittest.main()
