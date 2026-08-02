#!/usr/bin/env python3
"""The five-block top-level assembly: entropy source + sampler (transistor
level, the DR-0001 raw tap and the DR-0016 per-ring liveness taps) feeding
conditioner + health tests + per-ring liveness monitor + interface
(behavioural, per DR-0009).

This module is the **normative** description of the top-level assembly's
cycle-by-cycle wiring, at the level
``spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md``
assigns to it ("top-level bitstream-level integration (#14)" is listed under
"What is verified behaviourally"). ``trng_top.v`` implements the same wiring
in RTL, gluing together the four real synthesisable modules
(``crc32_conditioner.v``, ``rct_apt.v``, ``ring_liveness.v``,
``trng_interface.v``) with plain wires and no extra logic; ``sim/tests/test_trng_top.py`` checks that this
module and that RTL agree, and that both sides of ``design/xschem/trng_top.sch``'s
raw tap (``clk``/``rst_n``/``raw_bit``/``raw_valid``) name their pins the
same way -- the pinout-mismatch class of bug a schematic picture alone
cannot catch.

Everything upstream of the raw tap -- the entropy source (#7) and the
sampler (#9) -- is transistor-level (``design/xschem/trng_top.sch``,
instantiating ``sampler_core.sym`` unmodified) and is **not** reproduced
here: :class:`TopLevel` takes ``raw_bit``/``raw_valid`` and the per-ring
``ring_bit`` samples per cycle from whatever the caller supplies, exactly as
``crc32_conditioner.Conditioner``, ``rct_apt.HealthTest`` and
``ring_liveness.RingLivenessMonitor`` already do individually.

``ring_bit[i]`` is ring *i*'s own digitized sample -- ``sampler_core.sch``'s
``ring_bit1``/``ring_bit2``, produced by two more instances of the raw tap's
own ``sampler_dff`` on ``ro_array_core``'s ``ro1``/``ro2`` observation pins.
``ring_bit[0]`` is ring 1. The monitor's ``ring_stuck_any`` becomes the
interface's ``ht_fail_ring``: a third source of DR-0002's single latch, not a
second mechanism (DR-0016 "Failure behavior").

Registered vs. combinational: the load-bearing detail
-----------------------------------------------------
``rct_apt.v``'s three outputs (``ht_fail_rct``, ``ht_fail_apt``,
``ht_startup_pass``) are ``output reg`` -- registered, so they are stable
for the whole cycle *after* the edge that computed them, and
``ring_liveness.v``'s ``ring_stuck``/``ring_stuck_any`` are registered the
same way, so ``ht_fail_ring`` follows the identical one-cycle rule below. ``trng_interface.v``'s
``cond_en``/``cond_flush``/``startup_req`` are ``output wire`` -- purely
combinational on this cycle's inputs, exactly as
``design/interface/README.md`` documents for the conditioner's ``en``/
``flush``. Wired directly (as ``trng_top.v`` does, and as real synchronous
RTL always does), the natural signal flow is: the health test's *previous*
edge's registered failure flags are what the interface combinationally acts
on *this* cycle, and the ``startup_req``/``cond_en``/``cond_flush`` that
produces is what the conditioner and the health test consume as **this**
cycle's control inputs.

:meth:`TopLevel.step` reproduces that ordering explicitly, because a
sequence of plain Python method calls has no equivalent of "stable for the
cycle" unless the caller imposes it:

1. ``iface.peek_control(ht_fail_rct=<last>, ht_fail_apt=<last>,
   ht_fail_ring=<last>, **bus)`` -- the interface's purely-combinational
   response to the *previous* edge's latched health-test and liveness flags
   plus this cycle's register-bus stimulus.
2. ``cond.step(..., en=cond_en, flush=cond_flush)`` -- the conditioner sees
   this cycle's ``en``/``flush``, per its own documented contract.
3. ``health.step(..., startup_req=startup_req)`` -- the health test sees
   this cycle's ``startup_req`` and evaluates ``raw_bit`` against its
   internal state, producing the flags that will be registered *for* this
   edge (i.e. visible to the interface starting *next* cycle).
   ``liveness.step(ring_bit)`` is evaluated in the same position and for the
   same reason: its pulse is registered on this edge, so the interface sees
   it from the next cycle on. It takes no ``startup_req`` -- DR-0016 gives
   the monitor no window to restart, only a per-ring run counter.
4. ``iface.step(..., ht_fail_rct=<last>, ht_fail_apt=<last>, ht_startup_pass=...)``
   -- the same *previous*-cycle failure flags step 1 used (so the interface's
   internal state update is self-consistent with what it just told the
   conditioner and health test), plus this cycle's fresh
   ``ht_startup_pass`` pulse (which, unlike the two failure flags, has
   nowhere upstream of the interface that needs it a cycle earlier).
5. The health test's *this*-cycle flags become "last" for the next call.

Getting this backwards -- feeding the interface *this* cycle's still-being-
computed failure flags, or feeding the health test *this* cycle's not-yet-
computed ``startup_req`` -- is exactly the kind of same-cycle wiring mistake
the RTL cannot express (a wire cannot depend on its own value) but a
hand-sequenced behavioural model can get wrong silently. That is why this
ordering is stated here rather than left to be reconstructed from the call
sequence.

DR-0009 rules that apply to every record produced from this module: no
corner (rule 2), no P/V/T-dependent claim (rule 3), and every record must
name its raw-bit input source (rule 4) -- see ``sim/tb/smoke-trng-top/``.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conditioner"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "health_test"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "interface"))

import crc32_conditioner as cond  # noqa: E402
import rct_apt as ht  # noqa: E402
import regmap  # noqa: E402
import ring_liveness as rl  # noqa: E402
import trng_interface as iface  # noqa: E402

#: Entropy-source rings monitored for liveness. DR-0010 ships N = 2, and
#: design/xschem/sampler_core.sch instantiates exactly that many per-ring
#: digitizers; trng_top.v carries the same number as its N_RINGS parameter.
N_RINGS = 2

#: DR-0002's draft H0 = 0.5, giving the health test's default cutoffs
#: (C_RCT=81, C_APT=824 at W=1024) -- the same default rct_apt.v ships and
#: sim/tb/health-test-fault-injection/ uses. #13's ratified worst-corner H
#: is a one-argument change (HealthTest.from_h), not a redesign, exactly as
#: design/health_test/README.md documents.
H0 = ht.H0


@dataclass
class TopLevel:
    """The four digital blocks, wired as ``design/xschem/trng_top.sch``'s
    analog half (entropy source + sampler) expects to be fed, and as
    ``trng_top.v`` wires the real RTL.

    One :meth:`step` call is one sampler-clock edge (DR-0012: the sampler
    clock, fixed external, is what all four blocks, the raw tap and the two
    per-ring liveness taps share).
    """

    h: object = H0
    n_rings: int = N_RINGS

    cond: cond.Conditioner = field(init=False)
    health: "ht.HealthTest" = field(init=False)
    liveness: "rl.RingLivenessMonitor" = field(init=False)
    iface: iface.Interface = field(init=False)

    #: The health test's and the liveness monitor's registered failure flags,
    #: as the interface would see them at the start of this cycle -- see the
    #: module docstring.
    _last_ht_fail_rct: bool = field(default=False, init=False)
    _last_ht_fail_apt: bool = field(default=False, init=False)
    _last_ring_stuck_any: bool = field(default=False, init=False)

    #: Lifetime counters -- model bookkeeping, not hardware.
    cycles: int = field(default=0, init=False)
    raw_samples: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.cond = cond.Conditioner()
        self.health = ht.HealthTest.from_h(self.h)
        # DR-0016: C_LIVE is rct_apt.c_rct(H) -- the SAME cutoff, from the
        # same assumed H the health test above uses, not a second number.
        self.liveness = rl.RingLivenessMonitor.from_h(self.h, n_rings=self.n_rings)
        self.iface = iface.Interface()

    def step(
        self,
        raw_bit: int = 0,
        raw_valid: bool = False,
        ring_bit=None,
        **bus,
    ) -> iface.Outputs:
        """Advance one sampler-clock edge. ``ring_bit`` is this cycle's
        per-ring digitized samples (``n_rings`` of them, ring 1 first);
        omitting it holds every ring at 0, which is what an unwired caller
        should see -- and, after ``C_LIVE`` such cycles, exactly what a dead
        ring looks like. ``bus`` carries the register-bus stimulus
        (``reg_sel``/``reg_write``/``reg_addr``/``reg_wdata``/``str_ready``)
        that ``trng_interface.Interface.step`` accepts. Returns the
        interface's :class:`~trng_interface.Outputs` for this cycle -- the
        full top-level output (register reads, the streaming port,
        ``ht_alarm``)."""
        self.cycles += 1
        if raw_valid:
            self.raw_samples += 1
        if ring_bit is None:
            ring_bit = (0,) * self.n_rings

        cond_en, cond_flush, startup_req = self.iface.peek_control(
            ht_fail_rct=self._last_ht_fail_rct,
            ht_fail_apt=self._last_ht_fail_apt,
            ht_fail_ring=self._last_ring_stuck_any,
            **bus,
        )
        cond_word, cond_valid = self.cond.step(
            raw_bit=raw_bit, raw_valid=raw_valid, en=cond_en, flush=cond_flush
        )
        ht_fail_rct, ht_fail_apt, ht_startup_pass = self.health.step(
            raw_bit=raw_bit, raw_valid=raw_valid, startup_req=startup_req
        )
        _ring_stuck, ring_stuck_any = self.liveness.step(ring_bit)
        out = self.iface.step(
            raw_bit=raw_bit,
            raw_valid=raw_valid,
            cond_word=cond_word,
            cond_valid=cond_valid,
            ht_fail_rct=self._last_ht_fail_rct,
            ht_fail_apt=self._last_ht_fail_apt,
            ht_fail_ring=self._last_ring_stuck_any,
            ht_startup_pass=ht_startup_pass,
            **bus,
        )
        self._last_ht_fail_rct, self._last_ht_fail_apt = ht_fail_rct, ht_fail_apt
        self._last_ring_stuck_any = ring_stuck_any
        return out


#: Convenience re-exports so a caller of this module does not also need to
#: import design/interface/regmap.py directly for the register indices.
CTRL, STATUS, DATA, RAW_DATA = regmap.CTRL, regmap.STATUS, regmap.DATA, regmap.RAW_DATA
