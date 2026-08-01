#!/usr/bin/env python3
"""Unit tests for the interface / register block (DR-0013).

Four groups:

1. The register map's own consistency, and the staleness guard on the
   generated artifacts (`design/interface/regmap.py --check`). This is the
   check that keeps the RTL's `` `include``d header, the documented pinout
   #16/#27 read, and the behavioural model from drifting apart.
2. The behavioural model's contract, clause by clause against the two
   ratified records it implements -- DR-0001 (`OUT_MODE`, flush on switch,
   raw always available) and DR-0002 (latch, gate, flush, explicit clear plus
   a fresh start-up test).
3. Cross-block contract: the `en`/`flush` the conditioner (#8) documents as
   #26's obligation are actually driven that way.
4. RTL/model equivalence -- runs ``design/interface/trng_interface.v`` under
   Icarus Verilog against the same per-cycle stimulus and requires identical
   outputs every cycle. Skipped (not failed) when ``iverilog`` is not
   installed, the same way ``test_conditioner.py`` does it.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
IFACE_DIR = REPO_ROOT / "design" / "interface"
TB_DIR = SIM_DIR / "tb" / "interface-regfile"

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(IFACE_DIR))

import regmap  # noqa: E402
import trng_interface as iface  # noqa: E402

RTL = IFACE_DIR / "trng_interface.v"
RTL_TB = TB_DIR / "tb_rtl_equivalence.v"

CTRL, STATUS, DATA, RAW_DATA = regmap.CTRL, regmap.STATUS, regmap.DATA, regmap.RAW_DATA


def field(register: regmap.Register, name: str) -> regmap.Field:
    return next(f for f in register.fields if f.name == name)


def bit(word: int, register: regmap.Register, name: str) -> int:
    f = field(register, name)
    return (word >> f.lsb) & ((1 << f.width) - 1)


def raw_cycles(bits, **kwargs):
    """One stimulus cycle per raw sample."""
    return [iface.default_stimulus_word(raw_bit=b, raw_valid=True, **kwargs) for b in bits]


def pattern_bits(n: int, seed: int = 1):
    """A deterministic, stdlib-only bit pattern. Not a source model: these
    tests are about the block's plumbing, not about entropy."""
    x = seed & 0xFFFFFFFF
    out = []
    for _ in range(n):
        x = (1103515245 * x + 12345) & 0xFFFFFFFF
        out.append((x >> 16) & 1)
    return out


def run_model(vectors, dut=None):
    """Drive the model over ``vectors``; return (outputs, dut)."""
    dut = dut or iface.Interface()
    return [dut.step(**v) for v in vectors], dut


class RegisterMapTests(unittest.TestCase):
    def test_generated_artifacts_are_not_stale(self):
        """`regmap.py --check` is the structural guard: the RTL includes the
        generated header, so the RTL cannot drift from the normative map
        without this failing."""
        rc = regmap.main(["--check"])
        self.assertEqual(
            rc, regmap.EXIT_OK,
            "design/interface/ artifacts are stale -- run "
            "`python3 design/interface/regmap.py`",
        )

    def test_addresses_are_dense_and_unique(self):
        indices = [r.index for r in regmap.REGISTERS]
        self.assertEqual(indices, list(range(len(regmap.REGISTERS))))
        self.assertEqual(len(set(r.name for r in regmap.REGISTERS)), len(regmap.REGISTERS))

    def test_fields_do_not_overlap_and_fit_the_word(self):
        for register in regmap.REGISTERS:
            used = 0
            for f in register.fields:
                mask = ((1 << f.width) - 1) << f.lsb
                self.assertEqual(used & mask, 0, f"{register.name}.{f.name} overlaps")
                self.assertLess(f.msb, regmap.REG_BITS, f"{register.name}.{f.name} overflows")
                used |= mask

    def test_the_four_registers_dr0013_requires_all_exist(self):
        names = [r.name for r in regmap.REGISTERS]
        self.assertEqual(names, ["CTRL", "STATUS", "DATA", "RAW_DATA"])

    def test_out_mode_reset_default_is_conditioned(self):
        """DR-0001 §2: `conditioned` is the reset default."""
        self.assertEqual(bit(CTRL.reset, CTRL, "OUT_MODE"), 0)

    def test_enable_resets_high_so_startup_runs_without_software(self):
        self.assertEqual(bit(CTRL.reset, CTRL, "EN"), 1)
        self.assertEqual(bit(STATUS.reset, STATUS, "STARTUP"), 1)
        self.assertEqual(bit(STATUS.reset, STATUS, "COND_READY"), 0)
        self.assertEqual(bit(STATUS.reset, STATUS, "HT_ALARM"), 0)

    def test_health_flags_are_write_one_to_clear(self):
        for name in ("HT_FAIL_RCT", "HT_FAIL_APT", "OVF_DATA", "OVF_RAW"):
            self.assertEqual(field(STATUS, name).access, "W1C")

    def test_data_and_raw_data_are_distinct_read_only_registers(self):
        self.assertEqual(DATA.access, "RO")
        self.assertEqual(RAW_DATA.access, "RO")
        self.assertNotEqual(DATA.index, RAW_DATA.index)

    def test_level_fields_can_express_a_full_fifo(self):
        for name in ("DATA_LEVEL", "RAW_LEVEL"):
            self.assertGreaterEqual((1 << field(STATUS, name).width) - 1, regmap.FIFO_DEPTH)

    def test_the_generated_header_defines_every_field(self):
        header = regmap.verilog_header()
        for register in regmap.REGISTERS:
            self.assertIn(f"TRNG_ADDR_{register.name}", header)
            for f in register.fields:
                token = f"TRNG_{register.name}_{f.name}_"
                self.assertIn(token, header, f"{token} missing from the generated header")

    def test_rtl_uses_only_generated_names_for_addresses_and_bits(self):
        """A literal address or bit index in the RTL would be exactly the drift
        the generated header exists to prevent."""
        rtl = RTL.read_text()
        self.assertIn('`include "trng_regmap.vh"', rtl)
        for register in regmap.REGISTERS:
            self.assertIn(f"TRNG_ADDR_{register.name}", rtl)

    def test_external_ports_are_the_ones_16_needs(self):
        external = {p.name for p in regmap.PORTS if p.external}
        self.assertEqual(
            external,
            {
                "clk", "rst_n", "ht_alarm",
                "reg_sel", "reg_write", "reg_addr", "reg_wdata", "reg_rdata",
                "str_data", "str_valid", "str_ready",
            },
        )


class StartupTests(unittest.TestCase):
    """DR-0002: the start-up health test gates the conditioned path at
    power-on, and the reader can tell 'starting up' from 'failed'."""

    def test_resets_into_startup_with_the_conditioned_path_gated(self):
        dut = iface.Interface()
        self.assertEqual(dut.state, iface.STARTUP)
        self.assertFalse(dut.cond_ready)
        status = dut.status_value()
        self.assertEqual(bit(status, STATUS, "STARTUP"), 1)
        self.assertEqual(bit(status, STATUS, "COND_READY"), 0)
        self.assertEqual(bit(status, STATUS, "HT_ALARM"), 0)

    def test_startup_is_distinguishable_from_failed(self):
        """The curator's explicit requirement: a reader must be able to tell
        'still starting up' from 'failed and gated'. Both gate the conditioned
        path, so COND_READY alone cannot distinguish them."""
        starting = iface.Interface()
        failing = iface.Interface()
        failing.step(ht_fail_rct=True)
        s_start, s_fail = starting.status_value(), failing.status_value()
        self.assertEqual(bit(s_start, STATUS, "COND_READY"), 0)
        self.assertEqual(bit(s_fail, STATUS, "COND_READY"), 0)
        self.assertNotEqual(
            (bit(s_start, STATUS, "STARTUP"), bit(s_start, STATUS, "HT_ALARM")),
            (bit(s_fail, STATUS, "STARTUP"), bit(s_fail, STATUS, "HT_ALARM")),
        )

    def test_conditioner_is_held_disabled_for_the_whole_startup_window(self):
        """design/conditioner/README.md: #26 'holds en low for the whole
        start-up-test window'."""
        dut = iface.Interface()
        for _ in range(1024):
            out = dut.step(raw_bit=1, raw_valid=True)
            self.assertFalse(out.cond_en)
        out = dut.step(ht_startup_pass=True)
        self.assertFalse(out.cond_en)  # combinational on the pre-edge state
        self.assertTrue(dut.step().cond_en)

    def test_conditioned_words_are_dropped_while_gated(self):
        dut = iface.Interface()
        for _ in range(10):
            dut.step(cond_word=0xDEADBEEF, cond_valid=True)
        self.assertEqual(len(dut.cond_fifo), 0)
        self.assertEqual(dut.step(**iface.reg_read(DATA)).reg_rdata, 0)

    def test_raw_path_fills_during_startup(self):
        """DR-0001 §5 / DR-0002 §3: the raw path is not gated, so a
        characterization reader gets raw bits from the first sample -- not
        only after the start-up test passes."""
        dut = iface.Interface()
        _, dut = run_model(raw_cycles(pattern_bits(64)), dut)
        self.assertEqual(dut.state, iface.STARTUP)
        self.assertEqual(len(dut.raw_fifo), 2)
        self.assertEqual(bit(dut.status_value(), STATUS, "RAW_AVAIL"), 1)


class RawPathTests(unittest.TestCase):
    def test_raw_word_packs_32_consecutive_samples_lsb_first(self):
        bits = pattern_bits(32, seed=5)
        _, dut = run_model(raw_cycles(bits))
        self.assertEqual(len(dut.raw_fifo), 1)
        self.assertEqual(iface.word_to_raw_bits(dut.raw_fifo[0]), bits)

    def test_raw_reads_are_undecimated_and_in_order(self):
        bits = pattern_bits(32 * 5, seed=6)
        vectors = raw_cycles(bits) + [iface.reg_read(RAW_DATA)] * 5
        outs, _ = run_model(vectors)
        words = [o.reg_rdata for o in outs[-5:]]
        recovered = [b for w in words for b in iface.word_to_raw_bits(w)]
        self.assertEqual(recovered, bits)

    def test_raw_data_is_not_gated_by_a_health_test_failure(self):
        """DR-0001 §5 and DR-0002 §3, the single most important property of
        this block: an alarm must not take the raw path away."""
        dut = iface.Interface()
        run_model(raw_cycles(pattern_bits(32 * 3, seed=7)), dut)
        dut.step(ht_fail_rct=True)  # latch an alarm
        self.assertEqual(dut.state, iface.FAILED)
        self.assertEqual(bit(dut.status_value(), STATUS, "HT_ALARM"), 1)

        # Raw words buffered before the failure are still readable ...
        out = dut.step(**iface.reg_read(RAW_DATA))
        self.assertNotEqual(out.reg_rdata, 0)
        # ... and acquisition keeps running while the alarm is latched.
        before = len(dut.raw_fifo)
        run_model(raw_cycles(pattern_bits(32, seed=8)), dut)
        self.assertEqual(len(dut.raw_fifo), before + 1)

    def test_raw_streaming_keeps_flowing_through_an_alarm(self):
        dut = iface.Interface()
        dut.step(**iface.ctrl_write(out_mode_raw=True))
        run_model(raw_cycles(pattern_bits(32, seed=9)), dut)
        self.assertTrue(dut.step(str_ready=False).str_valid)
        dut.step(ht_fail_rct=True)
        self.assertTrue(dut.step(str_ready=False).str_valid)

    def test_raw_overflow_drops_the_incoming_word_and_flags_it(self):
        """DR-0001 rejected register-only raw access partly because a reader
        that falls behind silently invalidates a 90B dataset. OVF_RAW is what
        makes that audible."""
        dut = iface.Interface()
        bits = pattern_bits(32 * (regmap.FIFO_DEPTH + 3), seed=10)
        run_model(raw_cycles(bits), dut)
        self.assertEqual(len(dut.raw_fifo), regmap.FIFO_DEPTH)
        self.assertEqual(bit(dut.status_value(), STATUS, "OVF_RAW"), 1)
        # What survived is the *oldest* contiguous run, not a scrambled mix.
        first = [b for w in list(dut.raw_fifo) for b in iface.word_to_raw_bits(w)]
        self.assertEqual(first, bits[: 32 * regmap.FIFO_DEPTH])

    def test_overflow_flag_is_write_one_to_clear(self):
        dut = iface.Interface()
        run_model(raw_cycles(pattern_bits(32 * (regmap.FIFO_DEPTH + 1), seed=11)), dut)
        self.assertEqual(bit(dut.status_value(), STATUS, "OVF_RAW"), 1)
        dut.step(**iface.status_w1c("OVF_RAW"))
        self.assertEqual(bit(dut.status_value(), STATUS, "OVF_RAW"), 0)


class ConditionedPathTests(unittest.TestCase):
    def _running(self) -> iface.Interface:
        dut = iface.Interface()
        dut.step(ht_startup_pass=True)
        assert dut.state == iface.RUN
        return dut

    def test_conditioned_words_are_readable_once_running(self):
        dut = self._running()
        dut.step(cond_word=0x01234567, cond_valid=True)
        self.assertEqual(bit(dut.status_value(), STATUS, "DATA_AVAIL"), 1)
        self.assertEqual(dut.step(**iface.reg_read(DATA)).reg_rdata, 0x01234567)
        self.assertEqual(len(dut.cond_fifo), 0)

    def test_data_read_pops_exactly_one_word(self):
        dut = self._running()
        for word in (1, 2, 3):
            dut.step(cond_word=word, cond_valid=True)
        seen = [dut.step(**iface.reg_read(DATA)).reg_rdata for _ in range(3)]
        self.assertEqual(seen, [1, 2, 3])
        self.assertEqual(dut.step(**iface.reg_read(DATA)).reg_rdata, 0)

    def test_streaming_and_register_read_never_pop_the_same_word_twice(self):
        dut = self._running()
        for word in (0xA, 0xB):
            dut.step(cond_word=word, cond_valid=True)
        read_and_stream = dict(iface.reg_read(DATA), str_ready=True)
        out = dut.step(**read_and_stream)
        self.assertEqual(out.reg_rdata, 0xA)
        self.assertFalse(out.str_valid)  # the register read takes this cycle
        self.assertEqual(len(dut.cond_fifo), 1)

    def test_streaming_handshake_pops_on_valid_and_ready(self):
        dut = self._running()
        dut.step(cond_word=0xC0FFEE, cond_valid=True)
        out = dut.step(str_ready=False)
        self.assertTrue(out.str_valid)
        self.assertEqual(out.str_data, 0xC0FFEE)
        self.assertEqual(len(dut.cond_fifo), 1)  # not ready: nothing popped
        dut.step(str_ready=True)
        self.assertEqual(len(dut.cond_fifo), 0)

    def test_conditioned_overflow_sets_its_own_flag(self):
        dut = self._running()
        for i in range(regmap.FIFO_DEPTH + 2):
            dut.step(cond_word=i + 1, cond_valid=True)
        self.assertEqual(bit(dut.status_value(), STATUS, "OVF_DATA"), 1)
        self.assertEqual(bit(dut.status_value(), STATUS, "OVF_RAW"), 0)
        self.assertEqual(len(dut.cond_fifo), regmap.FIFO_DEPTH)


class HealthTestGateTests(unittest.TestCase):
    """DR-0002 §Failure behavior, clause by clause."""

    def _running_with_data(self):
        dut = iface.Interface()
        dut.step(ht_startup_pass=True)
        for word in (0x11111111, 0x22222222):
            dut.step(cond_word=word, cond_valid=True)
        return dut

    def test_failure_latches_the_flag_and_asserts_the_alarm(self):
        dut = self._running_with_data()
        dut.step(ht_fail_apt=True)
        status = dut.status_value()
        self.assertEqual(bit(status, STATUS, "HT_FAIL_APT"), 1)
        self.assertEqual(bit(status, STATUS, "HT_FAIL_RCT"), 0)
        self.assertEqual(bit(status, STATUS, "HT_ALARM"), 1)
        self.assertTrue(dut.step().ht_alarm)

    def test_the_latch_does_not_self_clear(self):
        dut = self._running_with_data()
        dut.step(ht_fail_rct=True)
        for _ in range(200):
            dut.step(raw_bit=1, raw_valid=True, ht_startup_pass=True)
        self.assertEqual(bit(dut.status_value(), STATUS, "HT_ALARM"), 1)
        self.assertEqual(dut.state, iface.FAILED)

    def test_failure_flushes_the_conditioned_fifo_and_deasserts_valid(self):
        dut = self._running_with_data()
        self.assertEqual(len(dut.cond_fifo), 2)
        out = dut.step(ht_fail_rct=True)
        self.assertFalse(out.str_valid)   # deasserts in the gate cycle itself
        self.assertTrue(out.cond_flush)   # and the conditioner is flushed
        self.assertFalse(out.cond_en)
        self.assertEqual(len(dut.cond_fifo), 0)

    def test_no_bit_from_the_failing_window_survives_the_gate(self):
        dut = self._running_with_data()
        dut.step(ht_fail_rct=True)
        for _ in range(10):
            self.assertEqual(dut.step(**iface.reg_read(DATA)).reg_rdata, 0)

    def test_a_failure_does_not_flush_the_raw_fifo(self):
        dut = iface.Interface()
        dut.step(ht_startup_pass=True)
        run_model(raw_cycles(pattern_bits(64, seed=12)), dut)
        self.assertEqual(len(dut.raw_fifo), 2)
        dut.step(ht_fail_apt=True)
        self.assertEqual(len(dut.raw_fifo), 2)

    def test_recovery_needs_an_explicit_clear_and_a_fresh_startup_pass(self):
        dut = self._running_with_data()
        dut.step(ht_fail_rct=True)
        self.assertEqual(dut.state, iface.FAILED)

        out = dut.step(**iface.status_w1c("HT_FAIL_RCT"))
        self.assertTrue(out.startup_req)          # restart the source + test
        self.assertEqual(dut.state, iface.STARTUP)
        self.assertEqual(bit(dut.status_value(), STATUS, "HT_ALARM"), 0)

        # Still gated until the fresh start-up test passes.
        for _ in range(50):
            self.assertFalse(dut.step(cond_word=0xFF, cond_valid=True).cond_en)
        self.assertEqual(len(dut.cond_fifo), 0)
        dut.step(ht_startup_pass=True)
        self.assertEqual(dut.state, iface.RUN)

    def test_clearing_only_one_of_two_flags_does_not_resume(self):
        dut = self._running_with_data()
        dut.step(ht_fail_rct=True, ht_fail_apt=True)
        out = dut.step(**iface.status_w1c("HT_FAIL_RCT"))
        self.assertFalse(out.startup_req)
        self.assertEqual(dut.state, iface.FAILED)
        self.assertEqual(bit(dut.status_value(), STATUS, "HT_ALARM"), 1)

    def test_a_failure_in_the_same_cycle_as_a_clear_wins(self):
        dut = self._running_with_data()
        dut.step(ht_fail_rct=True)
        clear = dict(iface.status_w1c("HT_FAIL_RCT"))
        clear["ht_fail_rct"] = True
        dut.step(**clear)
        self.assertEqual(bit(dut.status_value(), STATUS, "HT_FAIL_RCT"), 1)
        self.assertEqual(dut.state, iface.FAILED)

    def test_soft_reset_cannot_escape_a_latched_alarm(self):
        """DR-0002 makes write-1-to-clear the only way out of a latched
        alarm. A second clear path would be a way to resume without one."""
        dut = self._running_with_data()
        dut.step(ht_fail_rct=True)
        dut.step(**iface.ctrl_write(soft_reset=True))
        self.assertEqual(bit(dut.status_value(), STATUS, "HT_FAIL_RCT"), 1)
        self.assertEqual(dut.state, iface.FAILED)

    def test_a_failure_while_disabled_is_ignored(self):
        dut = iface.Interface()
        dut.step(**iface.ctrl_write(en=False))
        dut.step(ht_fail_rct=True)
        self.assertEqual(bit(dut.status_value(), STATUS, "HT_ALARM"), 0)


class OutModeTests(unittest.TestCase):
    """DR-0001 §2: the mode switch and its flush."""

    def _running(self):
        dut = iface.Interface()
        dut.step(ht_startup_pass=True)
        return dut

    def test_streaming_source_follows_out_mode(self):
        dut = self._running()
        dut.step(cond_word=0xCCCCCCCC, cond_valid=True)
        run_model(raw_cycles([1] * 32), dut)
        self.assertEqual(dut.step().str_data, 0xCCCCCCCC)
        dut.step(**iface.ctrl_write(out_mode_raw=True))  # flushes both FIFOs
        run_model(raw_cycles([1] * 32), dut)
        self.assertEqual(dut.step().str_data, 0xFFFFFFFF)

    def test_mode_switch_flushes_both_fifos_and_the_conditioner(self):
        dut = self._running()
        dut.step(cond_word=0xABCD, cond_valid=True)
        run_model(raw_cycles(pattern_bits(64, seed=13)), dut)
        self.assertEqual((len(dut.cond_fifo), len(dut.raw_fifo)), (1, 2))
        out = dut.step(**iface.ctrl_write(out_mode_raw=True))
        self.assertTrue(out.cond_flush)
        self.assertEqual((len(dut.cond_fifo), len(dut.raw_fifo)), (0, 0))

    def test_mode_switch_discards_the_partial_raw_word(self):
        dut = self._running()
        run_model(raw_cycles(pattern_bits(20, seed=14)), dut)
        self.assertEqual(dut.raw_count, 20)
        dut.step(**iface.ctrl_write(out_mode_raw=True))
        self.assertEqual((dut.raw_count, dut.raw_shift), (0, 0))

    def test_no_pre_switch_word_is_readable_after_the_switch(self):
        """The property DR-0001 §2 actually asks for."""
        dut = self._running()
        for word in (0xDEAD0001, 0xDEAD0002):
            dut.step(cond_word=word, cond_valid=True)
        run_model(raw_cycles([1] * 64), dut)  # 0xFFFFFFFF words in the raw FIFO

        dut.step(**iface.ctrl_write(out_mode_raw=True))
        dut.step(**iface.ctrl_write(out_mode_raw=False))
        for _ in range(4):
            self.assertEqual(dut.step(**iface.reg_read(DATA)).reg_rdata, 0)
            self.assertEqual(dut.step(**iface.reg_read(RAW_DATA)).reg_rdata, 0)

    def test_streaming_valid_deasserts_across_the_switch(self):
        dut = self._running()
        dut.step(cond_word=0x5A5A5A5A, cond_valid=True)
        self.assertTrue(dut.step().str_valid)
        out = dut.step(**iface.ctrl_write(out_mode_raw=True))
        self.assertFalse(out.str_valid)
        self.assertFalse(dut.step().str_valid)

    def test_rewriting_the_same_mode_is_not_a_switch(self):
        dut = self._running()
        dut.step(cond_word=0x1234, cond_valid=True)
        out = dut.step(**iface.ctrl_write(out_mode_raw=False))
        self.assertFalse(out.cond_flush)
        self.assertEqual(len(dut.cond_fifo), 1)

    def test_a_mode_switch_does_not_restart_the_startup_test(self):
        """DR-0001 requires a flush, not a re-qualification: the source has
        not been restarted, so demanding another 1024-sample window would add
        1 ms of dead time for nothing."""
        dut = self._running()
        out = dut.step(**iface.ctrl_write(out_mode_raw=True))
        self.assertFalse(out.startup_req)
        self.assertEqual(dut.state, iface.RUN)


class EnableTests(unittest.TestCase):
    def test_disable_idles_and_flushes_both_paths(self):
        dut = iface.Interface()
        dut.step(ht_startup_pass=True)
        dut.step(cond_word=0x99, cond_valid=True)
        run_model(raw_cycles([1] * 32), dut)
        dut.step(**iface.ctrl_write(en=False))
        self.assertEqual(dut.state, iface.IDLE)
        self.assertEqual((len(dut.cond_fifo), len(dut.raw_fifo)), (0, 0))

    def test_disabled_block_acquires_nothing(self):
        dut = iface.Interface()
        dut.step(**iface.ctrl_write(en=False))
        run_model(raw_cycles([1] * 64), dut)
        self.assertEqual(len(dut.raw_fifo), 0)
        self.assertEqual(dut.raw_count, 0)

    def test_re_enable_reruns_the_startup_test(self):
        dut = iface.Interface()
        dut.step(ht_startup_pass=True)
        dut.step(**iface.ctrl_write(en=False))
        out = dut.step(**iface.ctrl_write(en=True))
        self.assertTrue(out.startup_req)
        self.assertEqual(dut.state, iface.STARTUP)
        dut.step(ht_startup_pass=True)
        self.assertEqual(dut.state, iface.RUN)

    def test_enable_is_a_control_not_a_lock(self):
        """DR-0001 §4 forbids a fuse/lock on raw access. EN is ordinary R/W
        state that resets to 1, so no configuration leaves raw access
        unavailable-by-default or unrecoverable."""
        self.assertEqual(field(CTRL, "EN").access, "RW")
        self.assertEqual(field(CTRL, "EN").reset, 1)
        dut = iface.Interface()
        dut.step(**iface.ctrl_write(en=False))
        dut.step(**iface.ctrl_write(en=True))
        run_model(raw_cycles(pattern_bits(32, seed=15)), dut)
        self.assertEqual(len(dut.raw_fifo), 1)

    def test_soft_reset_restarts_the_startup_test_and_flushes(self):
        dut = iface.Interface()
        dut.step(ht_startup_pass=True)
        dut.step(cond_word=0x77, cond_valid=True)
        out = dut.step(**iface.ctrl_write(soft_reset=True))
        self.assertTrue(out.startup_req)
        self.assertTrue(out.cond_flush)
        self.assertEqual(dut.state, iface.STARTUP)
        self.assertEqual(len(dut.cond_fifo), 0)

    def test_soft_reset_reads_back_as_zero(self):
        dut = iface.Interface()
        dut.step(**iface.ctrl_write(soft_reset=True))
        ctrl = dut.step(**iface.reg_read(CTRL)).reg_rdata
        self.assertEqual(bit(ctrl, CTRL, "SOFT_RESET"), 0)
        self.assertEqual(bit(ctrl, CTRL, "EN"), 1)


class ConditionerContractTests(unittest.TestCase):
    """The contract design/conditioner/README.md states this block owes #8:
    'asserts flush for at least one sampler clock on a health-test-failure
    gate and on an OUT_MODE write in either direction, and holds en low for
    the whole start-up-test window.'"""

    def test_flush_on_a_health_test_failure_gate(self):
        dut = iface.Interface()
        dut.step(ht_startup_pass=True)
        self.assertTrue(dut.step(ht_fail_rct=True).cond_flush)

    def test_flush_on_an_out_mode_write_in_either_direction(self):
        dut = iface.Interface()
        dut.step(ht_startup_pass=True)
        self.assertTrue(dut.step(**iface.ctrl_write(out_mode_raw=True)).cond_flush)
        self.assertTrue(dut.step(**iface.ctrl_write(out_mode_raw=False)).cond_flush)

    def test_en_is_low_for_the_whole_startup_window_and_high_only_in_run(self):
        dut = iface.Interface()
        self.assertFalse(dut.step().cond_en)
        dut.step(ht_startup_pass=True)
        self.assertTrue(dut.step().cond_en)
        dut.step(ht_fail_apt=True)
        self.assertFalse(dut.step().cond_en)

    def test_en_is_low_in_the_flush_cycle_itself(self):
        """Flush and enable must not both be asserted in the gate cycle: the
        conditioner would otherwise absorb one more bit from the failing
        window before seeing the flush."""
        dut = iface.Interface()
        dut.step(ht_startup_pass=True)
        out = dut.step(ht_fail_rct=True)
        self.assertTrue(out.cond_flush)
        self.assertFalse(out.cond_en)

    def test_a_conditioned_word_arriving_in_a_flush_cycle_is_discarded(self):
        dut = iface.Interface()
        dut.step(ht_startup_pass=True)
        dut.step(cond_word=0xBAD, cond_valid=True, ht_fail_rct=True)
        self.assertEqual(len(dut.cond_fifo), 0)


class DeterminismTests(unittest.TestCase):
    def test_the_model_is_deterministic(self):
        vectors = _mixed_vectors()
        first, _ = run_model(vectors)
        second, _ = run_model(vectors)
        self.assertEqual([o.as_tuple() for o in first], [o.as_tuple() for o in second])


# ---------------------------------------------------------------------------
# RTL / model equivalence
# ---------------------------------------------------------------------------

_STIM_BITS = (
    ("str_ready", 0),
    ("reg_write", 1),
    ("reg_sel", 2),
    ("ht_startup_pass", 3),
    ("ht_fail_apt", 4),
    ("ht_fail_rct", 5),
    ("cond_valid", 6),
    ("raw_valid", 7),
    ("raw_bit", 8),
)


def encode_vector(cycle: dict) -> int:
    """Pack one stimulus cycle into the 75-bit word tb_rtl_equivalence.v reads."""
    word = 0
    for name, position in _STIM_BITS:
        word |= (int(bool(cycle[name])) & 1) << position
    word |= (cycle["reg_addr"] & 0b11) << 9
    word |= (cycle["reg_wdata"] & 0xFFFFFFFF) << 11
    word |= (cycle["cond_word"] & 0xFFFFFFFF) << 43
    return word


def _mixed_vectors():
    """One stimulus stream that exercises every clause of DR-0013 in order."""
    bits = pattern_bits(32 * 12, seed=99)
    vectors: list[dict] = []

    # Power-on: raw fills while the conditioned path is gated.
    vectors += raw_cycles(bits[:96])
    vectors.append(iface.reg_read(STATUS))
    vectors.append(iface.reg_read(RAW_DATA))

    # Start-up test passes; conditioned words start flowing.
    vectors.append(iface.default_stimulus_word(ht_startup_pass=True))
    for i in range(3):
        vectors.append(
            iface.default_stimulus_word(
                raw_bit=bits[i], raw_valid=True, cond_word=0x1000 + i, cond_valid=True
            )
        )
    vectors.append(iface.reg_read(DATA))
    vectors.append(iface.default_stimulus_word(str_ready=True))
    vectors.append(iface.default_stimulus_word(str_ready=True))

    # Overflow both FIFOs.
    for i in range(regmap.FIFO_DEPTH + 3):
        vectors.append(iface.default_stimulus_word(cond_word=0x2000 + i, cond_valid=True))
    vectors += raw_cycles(bits[96:])
    vectors.append(iface.reg_read(STATUS))
    vectors.append(iface.status_w1c("OVF_DATA", "OVF_RAW"))

    # Health-test failure, gate, and a partial then complete recovery.
    vectors.append(iface.default_stimulus_word(ht_fail_rct=True, ht_fail_apt=True))
    vectors.append(iface.reg_read(DATA))
    vectors.append(iface.reg_read(RAW_DATA))
    vectors.append(iface.status_w1c("HT_FAIL_RCT"))
    vectors.append(iface.reg_read(STATUS))
    vectors.append(iface.status_w1c("HT_FAIL_APT"))
    vectors += raw_cycles(bits[:64])
    vectors.append(iface.default_stimulus_word(ht_startup_pass=True))

    # OUT_MODE switch in both directions, mid-stream.
    vectors += raw_cycles(bits[:48])
    vectors.append(iface.ctrl_write(out_mode_raw=True))
    vectors += raw_cycles(bits[:64], str_ready=True)
    vectors.append(iface.reg_read(RAW_DATA))
    vectors.append(iface.ctrl_write(out_mode_raw=False))
    vectors.append(iface.reg_read(CTRL))

    # Disable, re-enable, soft reset.
    vectors.append(iface.ctrl_write(en=False))
    vectors += raw_cycles(bits[:40])
    vectors.append(iface.ctrl_write(en=True))
    vectors += raw_cycles(bits[:40])
    vectors.append(iface.default_stimulus_word(ht_startup_pass=True))
    vectors.append(iface.ctrl_write(soft_reset=True))
    vectors.append(iface.reg_read(STATUS))
    vectors += raw_cycles(bits[:40])
    return vectors


@unittest.skipUnless(
    shutil.which("iverilog") and shutil.which("vvp"),
    "Icarus Verilog not installed -- RTL/model equivalence not checked here "
    "(install iverilog to run it; see sim/tb/interface-regfile/README.md)",
)
class RtlEquivalenceTests(unittest.TestCase):
    """The RTL must reproduce the behavioural model output for output, cycle
    for cycle. This is what makes DR-0009 rule 5 ('the behavioural model is
    normative for the RTL') a checkable statement rather than a preference."""

    def _run_rtl(self, vectors):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            stim = tmp / "stim.hex"
            out = tmp / "out.txt"
            vvp = tmp / "sim.vvp"
            stim.write_text("".join(f"{encode_vector(v):019x}\n" for v in vectors))
            subprocess.run(
                # -I: trng_interface.v `include`s the generated regmap header.
                ["iverilog", "-g2012", "-I", str(IFACE_DIR),
                 "-o", str(vvp), str(RTL), str(RTL_TB)],
                check=True, capture_output=True, text=True,
            )
            proc = subprocess.run(
                ["vvp", str(vvp), f"+stim={stim}", f"+out={out}", f"+nvec={len(vectors)}"],
                check=True, capture_output=True, text=True,
            )
            self.assertNotIn("FATAL", proc.stdout, proc.stdout)
            rows = []
            for line in out.read_text().split("\n"):
                if not line.strip():
                    continue
                rdata, sdata, flags = line.split()
                rows.append(
                    (int(rdata, 16), int(sdata, 16)) + tuple(int(c) for c in flags)
                )
            return rows

    def _assert_matches(self, vectors, expect=("str_valid",)):
        rtl = self._run_rtl(vectors)
        model = [o.as_tuple() for o in run_model(vectors)[0]]
        self.assertEqual(len(rtl), len(model))
        for cycle, (a, b) in enumerate(zip(rtl, model)):
            self.assertEqual(a, b, f"RTL and model diverge at cycle {cycle}")
        # A comparison of two all-quiet streams would agree for the wrong
        # reason, so require the stimulus to have actually moved the outputs
        # it claims to exercise.
        index = {"str_valid": 2, "ht_alarm": 3, "cond_en": 4,
                 "cond_flush": 5, "startup_req": 6}
        for name in expect:
            self.assertTrue(
                any(row[index[name]] for row in model),
                f"stimulus never asserted {name} -- the comparison proves nothing",
            )
        self.assertGreater(len(set(model)), 2, "output stream is degenerate")

    def test_rtl_matches_model_on_the_full_scenario_stream(self):
        self._assert_matches(
            _mixed_vectors(),
            expect=("str_valid", "ht_alarm", "cond_en", "cond_flush", "startup_req"),
        )

    def test_rtl_matches_model_on_a_plain_raw_capture(self):
        self._assert_matches(
            raw_cycles(pattern_bits(32 * 6, seed=41))
            + [iface.ctrl_write(out_mode_raw=True)]
            + raw_cycles(pattern_bits(32 * 6, seed=42), str_ready=True)
        )

    def test_rtl_matches_model_across_a_gate_and_recovery(self):
        vectors = [iface.default_stimulus_word(ht_startup_pass=True)]
        vectors += [
            iface.default_stimulus_word(cond_word=0xFEED0000 + i, cond_valid=True)
            for i in range(4)
        ]
        vectors.append(iface.default_stimulus_word(ht_fail_apt=True))
        vectors += [iface.reg_read(DATA)] * 3
        vectors.append(iface.status_w1c("HT_FAIL_APT"))
        vectors += [iface.reg_read(STATUS)] * 2
        vectors.append(iface.default_stimulus_word(ht_startup_pass=True))
        vectors += [
            iface.default_stimulus_word(cond_word=0xBEEF0000 + i, cond_valid=True)
            for i in range(4)
        ]
        vectors += [iface.reg_read(DATA)] * 5
        self._assert_matches(
            vectors, expect=("str_valid", "ht_alarm", "cond_flush", "startup_req")
        )


if __name__ == "__main__":
    unittest.main()
