#!/usr/bin/env python3
"""Bit-exact behavioural model of the per-ring liveness monitor.

This module is the **normative** description of the liveness monitor's
cycle-by-cycle behaviour at the level fixed by
``spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md``.
The synthesisable RTL in ``ring_liveness.v`` implements the same function and
is checked against this model cycle-for-cycle (``sim/tests/test_ring_liveness.py``),
matching the ``rct_apt.{py,v}`` / ``crc32_conditioner.{py,v}`` pattern.

Fixed by
``spec/decision-records/DR-0016-per-ring-liveness-monitor.md``:

* **Mechanism: reuse DR-0002's RCT test, per ring, on a per-ring observation
  point.** DR-0002's Repetition Count Test already exists to catch exactly
  this failure signature -- a sampled bit repeating far more often than an
  effectively-random source would -- but it observes the *combined* raw tap
  (``xo`` after the sampler), where one dead ring out of N=2 still leaves a
  live ring driving the XOR node, so the combined stream keeps looking
  plausible (design/README.md "Per-ring liveness"). This module runs the
  **identical** run-length test, with the **identical** cutoff formula
  (:func:`rct_apt.c_rct`), independently on each ring's own already-digitized,
  already-``clk``-synchronized sample (``ring_bit`` -- produced upstream by a
  per-ring digitizer structurally identical to the raw tap's own
  ``sampler_dff``, per DR-0016). No new statistical assumption is introduced:
  the default cutoff is ``rct_apt.c_rct(rct_apt.H0)`` = 81, the same number
  and the same H0 = 0.5 draft assumption DR-0002 already carries, so a future
  ratified worst-corner H (#13) updates both cutoffs from the same edit.
* **Detection latency is the same class of bound DR-0002 already states for
  RCT**: the monitor fires the cycle a ring's sampled bit first repeats
  ``C_LIVE`` times in a row (default 81), and (matching ``rct_apt.py``'s RCT
  run counter) then **saturates** rather than re-firing every cycle
  thereafter, so a ring stuck far longer than ``C_LIVE`` samples produces
  exactly one pulse per stall onset.
* **Flag, not hard stop** (DR-0016 "Failure behavior"): ``ring_stuck``/
  ``ring_stuck_any`` are designed to be OR'd into the *same* latch-and-gate
  mechanism DR-0002 already defines for ``ht_fail_rct``/``ht_fail_apt`` --
  latched, gates the conditioned path only, leaves the raw path diagnostic,
  recovers only via an explicit software clear followed by the start-up
  retest. This module does not itself latch or gate anything (mirroring
  ``rct_apt.v``'s own "we only ever report" boundary); that is
  ``design/interface/``'s job (tracked as a follow-up, see DR-0016).
* **Why RCT and not also a per-ring APT**: RCT alone already gives a
  deterministic, bounded detection of "ring frozen at a single value", which
  is this issue's stated failure mode (a *stuck or dead* ring). A per-ring
  APT would mostly re-detect the same failure at worse latency without
  covering a materially different, demonstrated fault mode; DR-0016 leaves it
  as a revisit trigger rather than building it against no evidence.

Nothing in this module estimates entropy or makes any claim about a ring's
frequency or duty cycle; it observes a declared per-ring bit sequence and
reports repetition. Evidence lives under ``sim/records/``.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rct_apt as ht  # noqa: E402


@dataclass
class RingLivenessMonitor:
    """N_RINGS independent instances of DR-0002's RCT run-length test, one
    per entropy-source ring.

    Ports, matching ``ring_liveness.v`` one-for-one:

    ==================  =======================================================
    ``step(...)``       one rising edge of the sampler clock (DR-0012)
    ``ring_bits``       a sequence of N_RINGS already-digitized, already-
                        ``clk``-synchronized per-ring samples (see module
                        docstring)
    returns             ``(ring_stuck: tuple[bool, ...], ring_stuck_any: bool)``
                        -- each element of ``ring_stuck`` is a one-cycle pulse
    ==================  =======================================================
    """

    n_rings: int = 2
    #: Consecutive repeated samples of a ring's own digitized bit before that
    #: ring is declared stuck. Defaults to DR-0002's own C_RCT at the current
    #: H0 (81 at H0 = 0.5) -- the same cutoff, the same assumption, no new
    #: number introduced. A parameter, not a constant, exactly as DR-0002
    #: requires of C_RCT itself.
    c_live: int = 0

    _ring_run: list[int] = field(default=None, init=False)  # type: ignore[assignment]
    _ring_last_bit: list[int] = field(default=None, init=False)  # type: ignore[assignment]

    #: Lifetime counters -- model bookkeeping, not hardware.
    samples_seen: int = field(default=0, init=False)
    stuck_events: list[list[int]] = field(default=None, init=False)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.n_rings < 1:
            raise ValueError(f"n_rings must be >= 1, got {self.n_rings}")
        if not self.c_live:
            self.c_live = ht.c_rct(ht.H0)
        if self.c_live < 1:
            raise ValueError(f"c_live must be >= 1, got {self.c_live}")
        self._ring_run = [0] * self.n_rings
        self._ring_last_bit = [0] * self.n_rings
        self.stuck_events = [[] for _ in range(self.n_rings)]

    @classmethod
    def from_h(cls, h, alpha=ht.ALPHA, n_rings: int = 2) -> "RingLivenessMonitor":
        """Construct from an assumed per-ring min-entropy ``H`` rather than a
        raw cutoff -- the same "parameter, not a constant" path
        ``rct_apt.HealthTest.from_h`` offers for the combined raw tap."""
        return cls(n_rings=n_rings, c_live=ht.c_rct(h, alpha))

    def reset(self) -> None:
        """Async reset: matches ``ring_liveness.v``'s ``rst_n`` behaviour."""
        self._ring_run = [0] * self.n_rings
        self._ring_last_bit = [0] * self.n_rings

    def step(self, ring_bits) -> tuple[tuple[bool, ...], bool]:
        """Advance one sampler-clock edge.

        ``ring_bits`` must have exactly ``n_rings`` elements. Returns
        ``(ring_stuck, ring_stuck_any)``.
        """
        ring_bits = list(ring_bits)
        if len(ring_bits) != self.n_rings:
            raise ValueError(
                f"expected {self.n_rings} ring bits, got {len(ring_bits)}"
            )
        self.samples_seen += 1
        stuck = [False] * self.n_rings
        for i, bit in enumerate(ring_bits):
            bit &= 1
            match = self._ring_run[i] != 0 and bit == self._ring_last_bit[i]
            if match:
                run_next = (
                    self._ring_run[i] + 1
                    if self._ring_run[i] < self.c_live
                    else self._ring_run[i]
                )
            else:
                run_next = 1
            fires = run_next == self.c_live and self._ring_run[i] != self.c_live
            stuck[i] = fires
            if fires:
                self.stuck_events[i].append(self.samples_seen - 1)
            self._ring_run[i] = run_next
            self._ring_last_bit[i] = bit
        return tuple(stuck), any(stuck)


def run_stream(dut: RingLivenessMonitor, ring_bit_rows) -> dict:
    """Drive ``dut`` over ``ring_bit_rows`` (one N_RINGS-wide row per sampler
    clock). Returns per-ring event index lists and the OR'd event list."""
    per_ring_events: list[list[int]] = [[] for _ in range(dut.n_rings)]
    any_events: list[int] = []
    for i, row in enumerate(ring_bit_rows):
        stuck, stuck_any = dut.step(row)
        for r, fired in enumerate(stuck):
            if fired:
                per_ring_events[r].append(i)
        if stuck_any:
            any_events.append(i)
    return {"per_ring_events": per_ring_events, "any_events": any_events}
