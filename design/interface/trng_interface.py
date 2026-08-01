#!/usr/bin/env python3
"""Bit-exact behavioural model of the TRNG interface / register block.

This module is the **normative** description of the block's cycle-by-cycle
behaviour at the level fixed by
``spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md``
(§2 lists "the output FIFO, ``OUT_MODE`` mux, and register file (#26)" as
verified behaviourally). The synthesisable RTL in ``trng_interface.v``
implements the same function and is checked against this model cycle-for-cycle
by ``sim/tests/test_interface.py``.

The contract itself is fixed by
``spec/decision-records/DR-0013-interface-register-map-and-streaming-semantics.md``,
which derives it from two ratified records:

* **DR-0001** -- ``OUT_MODE`` selects what the streaming port carries
  (``conditioned`` at reset, ``raw``); a mode change flushes the conditioner
  and the output FIFO; ``DATA``/``RAW_DATA`` are distinct registers; raw
  access is unconditional and is never gated by health-test state.
* **DR-0002** -- an RCT/APT failure **latches** a sticky flag, asserts
  ``ht_alarm``, and gates the *conditioned* path (valid deasserts, ``DATA``
  returns no new bits, the FIFO is flushed). Recovery is explicit:
  write-1-to-clear the flag, then a fresh 1024-sample start-up test must pass
  before the conditioned path ungates.

Addresses, bit positions and reset values are **not** written here: they come
from :mod:`regmap`, which also generates the Verilog header the RTL includes.

Nothing in this module estimates entropy, and nothing in it has a P/V/T
corner (DR-0009 rule 3).
"""

from __future__ import annotations

import sys
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import regmap  # noqa: E402

MASK32 = (1 << regmap.REG_BITS) - 1

# Block states. COND_READY is exactly `state is RUN`.
IDLE = "idle"        # CTRL.EN = 0: acquisition stopped, both paths flushed
STARTUP = "startup"  # DR-0002 start-up health test in progress, nothing failed
RUN = "run"          # conditioned path ungated
FAILED = "failed"    # a latched HT_FAIL_* gates the conditioned path


def _bit(word: int, index: int) -> int:
    return (word >> index) & 1


@dataclass
class Outputs:
    """Everything the block drives in one cycle.

    ``reg_rdata``, ``str_data``, ``str_valid`` and ``ht_alarm`` are
    combinational functions of the state **before** this cycle's clock edge --
    a reader sees the state the block was in when the access was presented.
    ``cond_en``, ``cond_flush`` and ``startup_req`` are combinational on this
    cycle's events, so a flush reaches the conditioner in the same cycle as the
    register write that caused it (see DR-0013 §Decision, "Flush timing").
    """

    reg_rdata: int = 0
    str_data: int = 0
    str_valid: bool = False
    ht_alarm: bool = False
    cond_en: bool = False
    cond_flush: bool = False
    startup_req: bool = False

    def as_tuple(self) -> tuple[int, int, int, int, int, int, int]:
        return (
            self.reg_rdata,
            self.str_data,
            int(self.str_valid),
            int(self.ht_alarm),
            int(self.cond_en),
            int(self.cond_flush),
            int(self.startup_req),
        )


@dataclass(frozen=True)
class _Events:
    """The gate/flush/restart events decoded from one cycle's inputs."""

    en_next: bool
    mode_next: bool
    fail_rct_next: bool
    fail_apt_next: bool
    alarm_next: bool
    restart: bool
    flush_raw: bool
    flush_cond: bool


@dataclass
class Interface:
    """One instance of the interface / register block.

    One :meth:`step` call is one rising edge of the sampler clock. The
    register bus is synchronous to that clock; a clock-domain crossing for an
    integrator whose bus runs elsewhere is #27's, not this block's (DR-0013
    §Consequences).
    """

    fifo_depth: int = regmap.FIFO_DEPTH

    # --- control/status state -------------------------------------------
    en: bool = field(default=True, init=False)
    out_mode_raw: bool = field(default=False, init=False)
    state: str = field(default=STARTUP, init=False)
    ht_fail_rct: bool = field(default=False, init=False)
    ht_fail_apt: bool = field(default=False, init=False)
    ovf_data: bool = field(default=False, init=False)
    ovf_raw: bool = field(default=False, init=False)

    # --- datapath state --------------------------------------------------
    cond_fifo: deque = field(default_factory=deque, init=False)
    raw_fifo: deque = field(default_factory=deque, init=False)
    raw_shift: int = field(default=0, init=False)
    raw_count: int = field(default=0, init=False)

    # --- lifetime counters (model bookkeeping, not hardware) -------------
    cycles: int = field(default=0, init=False)
    raw_words_in: int = field(default=0, init=False)
    cond_words_in: int = field(default=0, init=False)
    raw_words_out: int = field(default=0, init=False)
    cond_words_out: int = field(default=0, init=False)
    flushes: int = field(default=0, init=False)
    startups: int = field(default=0, init=False)
    words_dropped_by_flush: int = field(default=0, init=False)
    raw_bits_dropped_by_flush: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.fifo_depth < 1:
            raise ValueError("FIFO_DEPTH must be >= 1")
        self.reset()

    # -- reset ------------------------------------------------------------

    def reset(self) -> None:
        """Asynchronous power-on reset (``rst_n`` low).

        CTRL.EN resets to 1 and the machine resets into STARTUP, so the
        block runs the DR-0002 start-up health test at power-on with no
        software write. The health-test block resets into the same state, so
        no ``startup_req`` pulse is needed (or emitted) at power-on.
        """
        self.en = bool(_bit(regmap.CTRL.reset, self._ctrl("EN").lsb))
        self.out_mode_raw = bool(_bit(regmap.CTRL.reset, self._ctrl("OUT_MODE").lsb))
        self.state = STARTUP if self.en else IDLE
        self.ht_fail_rct = False
        self.ht_fail_apt = False
        self.ovf_data = False
        self.ovf_raw = False
        self.cond_fifo.clear()
        self.raw_fifo.clear()
        self.raw_shift = 0
        self.raw_count = 0

    # -- derived state ----------------------------------------------------

    @staticmethod
    def _ctrl(name: str) -> regmap.Field:
        return next(f for f in regmap.CTRL.fields if f.name == name)

    @staticmethod
    def _status(name: str) -> regmap.Field:
        return next(f for f in regmap.STATUS.fields if f.name == name)

    @property
    def alarm(self) -> bool:
        return self.ht_fail_rct or self.ht_fail_apt

    @property
    def cond_ready(self) -> bool:
        return self.state == RUN

    def ctrl_value(self) -> int:
        value = 0
        value |= int(self.en) << self._ctrl("EN").lsb
        value |= int(self.out_mode_raw) << self._ctrl("OUT_MODE").lsb
        # SOFT_RESET is write-1-self-clearing; it always reads 0.
        return value

    def status_value(self) -> int:
        value = 0
        value |= int(self.ht_fail_rct) << self._status("HT_FAIL_RCT").lsb
        value |= int(self.ht_fail_apt) << self._status("HT_FAIL_APT").lsb
        value |= int(self.alarm) << self._status("HT_ALARM").lsb
        value |= int(self.state == STARTUP) << self._status("STARTUP").lsb
        value |= int(self.cond_ready) << self._status("COND_READY").lsb
        value |= int(bool(self.cond_fifo)) << self._status("DATA_AVAIL").lsb
        value |= int(bool(self.raw_fifo)) << self._status("RAW_AVAIL").lsb
        value |= int(self.ovf_data) << self._status("OVF_DATA").lsb
        value |= int(self.ovf_raw) << self._status("OVF_RAW").lsb
        value |= len(self.cond_fifo) << self._status("DATA_LEVEL").lsb
        value |= len(self.raw_fifo) << self._status("RAW_LEVEL").lsb
        return value & MASK32

    # -- this cycle's control events --------------------------------------

    def _events(
        self,
        ht_fail_rct: bool,
        ht_fail_apt: bool,
        reg_sel: bool,
        reg_write: bool,
        reg_addr: int,
        reg_wdata: int,
    ) -> _Events:
        """Decode the events that gate, flush and restart the block.

        Split out of :meth:`step` so :meth:`peek_control` can report
        ``cond_en``/``cond_flush``/``startup_req`` for a cycle without
        advancing state -- there is one implementation, not two.
        """
        write_ctrl = bool(reg_sel) and bool(reg_write) and reg_addr == regmap.CTRL.index
        write_status = bool(reg_sel) and bool(reg_write) and reg_addr == regmap.STATUS.index

        en_next = self.en
        mode_next = self.out_mode_raw
        soft_reset = False
        if write_ctrl:
            en_next = bool(_bit(reg_wdata, self._ctrl("EN").lsb))
            mode_next = bool(_bit(reg_wdata, self._ctrl("OUT_MODE").lsb))
            soft_reset = bool(_bit(reg_wdata, self._ctrl("SOFT_RESET").lsb))
        mode_switch = mode_next != self.out_mode_raw
        enable_rise = en_next and not self.en
        disable = (not en_next) and self.en

        # A failure pulse beats a write-1-to-clear presented in the same
        # cycle: set wins over clear, so a clear can never lose a failure.
        fail_rct_next = self.ht_fail_rct
        fail_apt_next = self.ht_fail_apt
        if write_status:
            if _bit(reg_wdata, self._status("HT_FAIL_RCT").lsb):
                fail_rct_next = False
            if _bit(reg_wdata, self._status("HT_FAIL_APT").lsb):
                fail_apt_next = False
        fail_event = bool(ht_fail_rct or ht_fail_apt) and self.en
        if ht_fail_rct and self.en:
            fail_rct_next = True
        if ht_fail_apt and self.en:
            fail_apt_next = True
        alarm_next = fail_rct_next or fail_apt_next
        alarm_cleared = self.alarm and not alarm_next

        # DR-0002 §Failure behavior 4: clearing the latched flag restarts the
        # noise source and the start-up health test. So does a soft reset and
        # a 0->1 transition of CTRL.EN. None of them can ungate a still-latched
        # alarm, because `alarm_next` is evaluated ahead of `restart` in the
        # state update.
        restart = (alarm_cleared or soft_reset or enable_rise) and en_next and not alarm_next

        # Two flush scopes, and the difference between them is DR-0001 §5.
        #
        #   flush_raw   the raw FIFO and the partial raw word. Asserted only on
        #               events that are software-initiated (a mode change, a
        #               soft reset, a disable) or that restart the noise source
        #               (an alarm clear) -- never on a health-test failure,
        #               because discarding the raw path on failure would remove
        #               exactly the observability needed to diagnose it.
        #   flush_cond  the conditioner and the conditioned FIFO. Everything in
        #               flush_raw, plus the DR-0002 failure gate.
        flush_raw = bool(mode_switch or restart or disable)
        flush_cond = bool(flush_raw or fail_event)

        return _Events(
            en_next=en_next,
            mode_next=mode_next,
            fail_rct_next=fail_rct_next,
            fail_apt_next=fail_apt_next,
            alarm_next=alarm_next,
            restart=restart,
            flush_raw=flush_raw,
            flush_cond=flush_cond,
        )

    def peek_control(
        self,
        ht_fail_rct: bool = False,
        ht_fail_apt: bool = False,
        reg_sel: bool = False,
        reg_write: bool = False,
        reg_addr: int = 0,
        reg_wdata: int = 0,
        **_ignored,
    ) -> tuple[bool, bool, bool]:
        """``(cond_en, cond_flush, startup_req)`` for a cycle, without stepping.

        These three outputs are combinational on the same inputs the
        conditioner (#8) consumes in the same cycle, so a caller that models
        both blocks together can close the loop without inventing a cycle of
        skew that the hardware does not have.
        """
        ev = self._events(ht_fail_rct, ht_fail_apt, reg_sel, reg_write, reg_addr, reg_wdata)
        return (self.cond_ready and not ev.flush_cond, ev.flush_cond, ev.restart)

    # -- one clock edge ---------------------------------------------------

    def step(
        self,
        raw_bit: int = 0,
        raw_valid: bool = False,
        cond_word: int = 0,
        cond_valid: bool = False,
        ht_fail_rct: bool = False,
        ht_fail_apt: bool = False,
        ht_startup_pass: bool = False,
        reg_sel: bool = False,
        reg_write: bool = False,
        reg_addr: int = 0,
        reg_wdata: int = 0,
        str_ready: bool = False,
    ) -> Outputs:
        """Advance one sampler-clock edge and return this cycle's outputs."""
        self.cycles += 1
        reg_addr &= (1 << regmap.ADDR_W) - 1
        reg_wdata &= MASK32
        cond_word &= MASK32

        reg_read = bool(reg_sel) and not reg_write
        write_status = bool(reg_sel) and bool(reg_write) and reg_addr == regmap.STATUS.index

        ev = self._events(ht_fail_rct, ht_fail_apt, reg_sel, reg_write, reg_addr, reg_wdata)
        en_next = ev.en_next
        mode_next = ev.mode_next
        fail_rct_next = ev.fail_rct_next
        fail_apt_next = ev.fail_apt_next
        alarm_next = ev.alarm_next
        restart = ev.restart
        flush_raw = ev.flush_raw
        flush_cond = ev.flush_cond

        # --- combinational outputs, from the pre-edge state ---------------
        out = Outputs()
        out.ht_alarm = self.alarm
        out.cond_flush = flush_cond
        out.cond_en = self.cond_ready and not flush_cond
        out.startup_req = restart

        cond_avail = bool(self.cond_fifo) and self.cond_ready
        raw_avail = bool(self.raw_fifo)
        read_data = reg_read and reg_addr == regmap.DATA.index
        read_raw = reg_read and reg_addr == regmap.RAW_DATA.index

        if reg_read:
            if reg_addr == regmap.CTRL.index:
                out.reg_rdata = self.ctrl_value()
            elif reg_addr == regmap.STATUS.index:
                out.reg_rdata = self.status_value()
            elif reg_addr == regmap.DATA.index:
                out.reg_rdata = self.cond_fifo[0] if cond_avail else 0
            else:
                out.reg_rdata = self.raw_fifo[0] if raw_avail else 0

        # The streaming port and the register read share one FIFO per path.
        # A register read takes the cycle; the streaming port simply shows no
        # valid word in it, so a word can never be popped twice.
        if self.out_mode_raw:
            out.str_data = self.raw_fifo[0] if raw_avail else 0
            out.str_valid = raw_avail and not read_raw and not flush_raw
        else:
            out.str_data = self.cond_fifo[0] if cond_avail else 0
            out.str_valid = cond_avail and not read_data and not flush_cond

        # --- state update -------------------------------------------------
        # Sticky overflow flags are cleared here, before the FIFO update that
        # may set them again: a set in the same cycle wins, the same rule the
        # HT_FAIL_* latches use, so a clear can never lose an event.
        if write_status:
            if _bit(reg_wdata, self._status("OVF_DATA").lsb):
                self.ovf_data = False
            if _bit(reg_wdata, self._status("OVF_RAW").lsb):
                self.ovf_raw = False

        pop_stream = out.str_valid and bool(str_ready)
        pop_data = (read_data and cond_avail and not flush_cond) or (
            pop_stream and not self.out_mode_raw
        )
        pop_raw = (read_raw and raw_avail and not flush_raw) or (
            pop_stream and self.out_mode_raw
        )

        if flush_cond or flush_raw:
            self.flushes += 1

        if flush_cond:
            self.words_dropped_by_flush += len(self.cond_fifo)
            self.cond_fifo.clear()
        elif pop_data:
            self.cond_fifo.popleft()
            self.cond_words_out += 1

        if flush_raw:
            self.words_dropped_by_flush += len(self.raw_fifo)
            self.raw_bits_dropped_by_flush += self.raw_count
            self.raw_fifo.clear()
            self.raw_shift = 0
            self.raw_count = 0
        elif pop_raw:
            self.raw_fifo.popleft()
            self.raw_words_out += 1

        # Raw acquisition is never gated by health-test state (DR-0001 §5):
        # it runs in STARTUP, in RUN and in FAILED alike. Only CTRL.EN = 0
        # stops it, and only a flush_raw event discards what it has buffered.
        if self.en and raw_valid and not flush_raw:
            self.raw_shift = (self.raw_shift >> 1) | (
                (raw_bit & 1) << (regmap.RAW_PACK_BITS - 1)
            )
            self.raw_count += 1
            if self.raw_count == regmap.RAW_PACK_BITS:
                self.raw_words_in += 1
                if len(self.raw_fifo) < self.fifo_depth:
                    self.raw_fifo.append(self.raw_shift & MASK32)
                else:
                    self.ovf_raw = True
                self.raw_shift = 0
                self.raw_count = 0

        if cond_valid and self.cond_ready and not flush_cond:
            self.cond_words_in += 1
            if len(self.cond_fifo) < self.fifo_depth:
                self.cond_fifo.append(cond_word)
            else:
                self.ovf_data = True

        self.ht_fail_rct = fail_rct_next
        self.ht_fail_apt = fail_apt_next
        self.en = en_next
        self.out_mode_raw = mode_next

        if not en_next:
            self.state = IDLE
        elif alarm_next:
            self.state = FAILED
        elif restart:
            self.state = STARTUP
            self.startups += 1
        elif self.state == STARTUP and ht_startup_pass:
            self.state = RUN

        return out


def default_stimulus_word(**kwargs) -> dict:
    """A no-op cycle, for tests and demos that override one field at a time."""
    cycle = dict(
        raw_bit=0, raw_valid=False, cond_word=0, cond_valid=False,
        ht_fail_rct=False, ht_fail_apt=False, ht_startup_pass=False,
        reg_sel=False, reg_write=False, reg_addr=0, reg_wdata=0, str_ready=False,
    )
    cycle.update(kwargs)
    return cycle


def ctrl_write(out_mode_raw: bool = False, en: bool = True, soft_reset: bool = False) -> dict:
    """A CTRL write cycle with the given field values."""
    word = 0
    if en:
        word |= 1 << Interface._ctrl("EN").lsb
    if out_mode_raw:
        word |= 1 << Interface._ctrl("OUT_MODE").lsb
    if soft_reset:
        word |= 1 << Interface._ctrl("SOFT_RESET").lsb
    return default_stimulus_word(
        reg_sel=True, reg_write=True, reg_addr=regmap.CTRL.index, reg_wdata=word
    )


def status_w1c(*fields: str) -> dict:
    """A STATUS write-1-to-clear cycle for the named fields."""
    word = 0
    for name in fields:
        word |= 1 << Interface._status(name).lsb
    return default_stimulus_word(
        reg_sel=True, reg_write=True, reg_addr=regmap.STATUS.index, reg_wdata=word
    )


def reg_read(register: regmap.Register) -> dict:
    """A read cycle of ``register``."""
    return default_stimulus_word(reg_sel=True, reg_write=False, reg_addr=register.index)


def word_to_raw_bits(word: int, width: int = regmap.RAW_PACK_BITS) -> list[int]:
    """Unpack a ``RAW_DATA`` word back into the raw samples that made it.

    The inverse of the block's packing: sample *i* of the group is bit *i* of
    the word (LSB first), so a captured raw word stream is a raw *sample*
    stream with no reordering -- which is what DR-0004's sequential dataset
    needs.
    """
    return [(word >> i) & 1 for i in range(width)]
