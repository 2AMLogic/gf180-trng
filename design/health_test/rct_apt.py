#!/usr/bin/env python3
"""Bit-exact behavioural model of the on-die health tests: RCT + APT.

This module is the **normative** description of the health-test block's
cycle-by-cycle behaviour at the level fixed by
``spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md``.
The synthesisable RTL in ``rct_apt.v`` implements the same function and is
checked against this model cycle-for-cycle
(``sim/tests/test_health_test.py``), matching the
``design/conditioner/crc32_conditioner.{py,v}`` pattern.

The tests, their cutoffs, the window, and the failure/start-up semantics are
fixed by
``spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md``:

* **Repetition Count Test (RCT)** -- fails when the same raw sample value
  repeats ``C_RCT`` times in a row. ``C_RCT = 1 + ceil(-log2(alpha) / H)``.
* **Adaptive Proportion Test (APT)** -- fails when, within a window of ``W``
  consecutive raw samples, the value of the window's first sample (the
  "reference") recurs ``C_APT`` or more times. ``C_APT`` is the smallest `C`
  with ``Pr(X >= C) <= alpha`` for ``X ~ Binomial(W, 2**-H)``. Windows are
  non-overlapping: a completed window is immediately followed by a fresh one
  whose reference is the very next sample.
* **Start-up test** -- both tests run continuously on the raw tap; a
  independent counter tracks samples since the last reset/restart with *no*
  RCT/APT failure, and pulses ``ht_startup_pass`` for one cycle once that
  count reaches ``STARTUP_SAMPLES`` (DR-0002 fixes this at exactly ``W`` =
  1024 consecutive clean raw samples). ``startup_req`` (from the interface
  block, DR-0013) discards any in-flight RCT/APT window and restarts this
  counter, mirroring a real noise-source restart.

Per DR-0002, **the cutoffs are parameters of a min-entropy assumption H, not
hard-coded constants**: :func:`c_rct` and :func:`c_apt` compute them from
``H``, ``alpha`` and ``W``, and :class:`HealthTest` takes the resulting
integer cutoffs (or ``H`` via :meth:`HealthTest.from_h`) as constructor
arguments -- exactly as ``crc32_conditioner.py`` takes ``K`` as a parameter
rather than baking in 256. The ratified draft H0 = 0.5 (``C_RCT = 81``,
``C_APT = 824``) is the *default*, not the only supported value; #13's
worst-corner H is expected to supply a different H later.

DR-0002's **APT degeneracy floor** (no valid ``C_APT <= W`` exists once H
falls to about 0.03-0.05 at the ratified alpha/W) is enforced as a
constructor-time :class:`ValueError`, never a silently wrong cutoff.

Nothing in this module estimates entropy; it observes a declared bitstream
and reports pass/fail. Evidence lives under ``sim/records/``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from decimal import Decimal, getcontext

# 120 digits of precision: alpha = 2**-40 ~= 9.09e-13 and the binomial tail
# terms at W = 1024 span many orders of magnitude below that. Matches the
# precision budget `sim/tb/conditioner-crc32/sp800_90b.py` uses for the same
# reason.
getcontext().prec = 120

#: False-positive probability, both tests (DR-0002 Context: chosen against the
#: >= 1 Mbps raw sample rate -- ~12.7 days between spurious RCT alarms,
#: ~36 years between spurious APT alarms).
ALPHA = Decimal(2) ** -40

#: APT window size, binary source (DR-0002 "Test inputs and placement").
W = 1024

#: Draft assumption H0 = 0.5 bit/sample (DR-0002 "Initial numeric values") --
#: an assumption with no evidence record behind it, superseded once #13 lands
#: a worst-corner measurement. Provided so callers have a documented default
#: to construct against; not baked into any cutoff below without going
#: through :func:`c_rct` / :func:`c_apt`.
H0 = Decimal("0.5")

_LN2 = Decimal(2).ln()


def _log2(x: Decimal) -> Decimal:
    return x.ln() / _LN2


def _ceil_decimal(x: Decimal) -> int:
    """Ceiling of a Decimal, as a Python int."""
    return int(x.to_integral_value(rounding="ROUND_CEILING"))


def c_rct(h, alpha=ALPHA) -> int:
    """RCT cutoff: ``1 + ceil(-log2(alpha) / H)`` (DR-0002).

    ``h`` is the assumed per-sample min-entropy in bits; ``alpha`` is the
    target false-positive probability for this test.
    """
    h = Decimal(str(h))
    alpha = Decimal(str(alpha))
    if h <= 0:
        raise ValueError(f"H must be > 0 bit/sample, got {h}")
    if not (0 < alpha < 1):
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")
    neg_log2_alpha = -_log2(alpha)
    return 1 + _ceil_decimal(neg_log2_alpha / h)


def apt_tail_probability(c: int, h, w: int = W) -> Decimal:
    """``Pr(X >= c)`` for ``X ~ Binomial(w, 2**-h)``, computed exactly.

    Exposed separately from :func:`c_apt` so a caller (or a unit test) can
    check a specific cutoff's tail probability directly, the way
    DR-0002's "Independent verification" subsection quotes
    ``Pr(X >= 824) = 6.44e-13`` and ``Pr(X >= 823) = 1.10e-12`` at H0 = 0.5.
    """
    h = Decimal(str(h))
    if h <= 0:
        raise ValueError(f"H must be > 0 bit/sample, got {h}")
    if not (0 <= c <= w):
        raise ValueError(f"c must be in [0, w={w}], got {c}")
    p = Decimal(2) ** (-h)  # Pr(a given later sample matches the reference)
    q = Decimal(1) - p
    return sum(
        (Decimal(math.comb(w, k)) * (p**k) * (q ** (w - k)) for k in range(c, w + 1)),
        Decimal(0),
    )


#: Sentinel returned by :func:`c_apt` when no cutoff in ``[1, w]`` satisfies
#: the criterion -- DR-0002's APT degeneracy floor, hit around H <= 0.03-0.05
#: at the ratified alpha/W. Deliberately outside the valid range so a caller
#: that forgets to check gets a cutoff `HealthTest` will refuse to accept,
#: rather than a plausible-looking wrong number.
APT_DEGENERATE = W + 1


def c_apt(h, alpha=ALPHA, w: int = W) -> int:
    """APT cutoff: smallest ``C`` with ``Pr(X >= C) <= alpha``, ``X ~ Bin(w, 2**-h)``.

    Returns :data:`APT_DEGENERATE` (``w + 1``) if no such ``C`` in ``[0, w]``
    exists -- DR-0002's "APT degeneracy floor": at the ratified alpha and w
    this happens once H drops to roughly 0.03 bit/sample. Callers that need a
    cutoff to actually use (rather than to report) should go through
    :class:`HealthTest` / :meth:`HealthTest.from_h`, which raises instead of
    silently accepting a degenerate value.
    """
    h = Decimal(str(h))
    alpha = Decimal(str(alpha))
    if h <= 0:
        raise ValueError(f"H must be > 0 bit/sample, got {h}")
    if not (0 < alpha < 1):
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")
    if w < 1:
        raise ValueError("w must be >= 1")

    p = Decimal(2) ** (-h)
    q = Decimal(1) - p

    tail = Decimal(0)
    best = APT_DEGENERATE
    for k in range(w, -1, -1):
        pmf = Decimal(math.comb(w, k)) * (p**k) * (q ** (w - k))
        tail += pmf
        if tail <= alpha:
            best = k
        else:
            break
    return best


@dataclass
class HealthTest:
    """One instance of the RCT + APT health-test block.

    Ports, matching ``rct_apt.v`` one-for-one:

    ==================  =======================================================
    ``step(...)``       one rising edge of the sampler clock
    ``raw_bit``         the DR-0001 raw tap, one bit per sample
    ``raw_valid``       this cycle carries a new raw sample
    ``startup_req``     restart the noise source / start-up window (from the
                        interface block, DR-0013); discards any in-flight
                        RCT/APT window and takes priority over absorbing this
                        cycle's sample, the same way ``flush`` beats
                        absorption in ``crc32_conditioner.py``
    returns             ``(ht_fail_rct, ht_fail_apt, ht_startup_pass)`` --
                        each a one-cycle pulse
    ==================  =======================================================
    """

    c_rct: int
    c_apt: int
    w: int = W
    #: Consecutive clean raw samples required for the start-up test to pass.
    #: DR-0002 fixes this at exactly ``W`` (1024); kept as its own parameter
    #: (defaulting to ``w``) so the two are not accidentally conflated.
    startup_samples: int = 0

    rct_run: int = field(default=0, init=False)
    rct_last_bit: int = field(default=0, init=False)

    apt_pos: int = field(default=0, init=False)
    apt_match: int = field(default=0, init=False)
    apt_ref_bit: int = field(default=0, init=False)

    startup_count: int = field(default=0, init=False)

    #: Lifetime counters -- model bookkeeping, not hardware.
    samples_seen: int = field(default=0, init=False)
    rct_failures: int = field(default=0, init=False)
    apt_failures: int = field(default=0, init=False)
    startup_passes: int = field(default=0, init=False)
    restarts: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.c_rct < 1:
            raise ValueError(f"C_RCT must be >= 1, got {self.c_rct}")
        if self.w < 1:
            raise ValueError(f"W must be >= 1, got {self.w}")
        if not (1 <= self.c_apt <= self.w):
            raise ValueError(
                f"C_APT={self.c_apt} is outside [1, W={self.w}] -- this is DR-0002's "
                "APT degeneracy floor: no valid cutoff exists at this H/alpha/W "
                "(hit around H <= 0.03-0.05 bit/sample at the ratified "
                "alpha=2**-40, W=1024). Feeding a pathologically low H must not "
                "silently produce an unusable cutoff."
            )
        if not self.startup_samples:
            self.startup_samples = self.w
        if self.startup_samples < 1:
            raise ValueError("startup_samples must be >= 1")

    @classmethod
    def from_h(cls, h, alpha=ALPHA, w: int = W, startup_samples: int = 0) -> "HealthTest":
        """Construct from an assumed min-entropy ``H`` rather than raw cutoffs.

        This is the "parameter, not a constant" path DR-0002 requires:
        ``HealthTest.from_h(H0)`` reproduces the ratified draft cutoffs
        (``C_RCT=81``, ``C_APT=824``); a future ratified worst-corner H from
        #13 is a one-argument change, not a redesign.
        """
        return cls(
            c_rct=c_rct(h, alpha),
            c_apt=c_apt(h, alpha, w),
            w=w,
            startup_samples=startup_samples,
        )

    def restart_window(self) -> None:
        """Discard any in-flight RCT/APT window and restart the start-up counter.

        Called on ``startup_req`` (DR-0002 §Failure behavior 4: clearing a
        latched alarm restarts the noise source and the start-up test) and
        equivalently at power-on.
        """
        self.rct_run = 0
        self.rct_last_bit = 0
        self.apt_pos = 0
        self.apt_match = 0
        self.apt_ref_bit = 0
        self.startup_count = 0
        self.restarts += 1

    def step(
        self,
        raw_bit: int = 0,
        raw_valid: bool = False,
        startup_req: bool = False,
    ) -> tuple[bool, bool, bool]:
        """Advance one sampler-clock edge.

        Returns ``(ht_fail_rct, ht_fail_apt, ht_startup_pass)``.
        """
        if startup_req:
            # Restart wins over absorption: a sample presented in the same
            # cycle as a restart belongs to the window being discarded, the
            # same priority crc32_conditioner.py gives `flush` over a raw bit.
            self.restart_window()
            return False, False, False

        if not raw_valid:
            return False, False, False

        bit = raw_bit & 1
        self.samples_seen += 1

        # --- RCT: longest run of a repeated value ------------------------
        match_rct = self.rct_run != 0 and bit == self.rct_last_bit
        if match_rct:
            rct_run_next = self.rct_run + 1 if self.rct_run < self.c_rct else self.rct_run
        else:
            rct_run_next = 1
        ht_fail_rct = rct_run_next == self.c_rct and self.rct_run != self.c_rct
        self.rct_run = rct_run_next
        self.rct_last_bit = bit

        # --- APT: occurrences of the window's reference value ------------
        window_starting = self.apt_pos == 0
        apt_match_next = (
            1 if window_starting else self.apt_match + (1 if bit == self.apt_ref_bit else 0)
        )
        apt_pos_next = self.apt_pos + 1
        window_done = apt_pos_next == self.w
        ht_fail_apt = window_done and apt_match_next >= self.c_apt
        if window_starting:
            self.apt_ref_bit = bit
        if window_done:
            self.apt_pos = 0
            self.apt_match = 0
        else:
            self.apt_pos = apt_pos_next
            self.apt_match = apt_match_next

        # --- Start-up test: consecutive clean samples ---------------------
        ht_startup_pass = False
        if ht_fail_rct or ht_fail_apt:
            self.startup_count = 0
        elif self.startup_count < self.startup_samples:
            su_next = self.startup_count + 1
            if su_next == self.startup_samples:
                ht_startup_pass = True
            self.startup_count = su_next

        if ht_fail_rct:
            self.rct_failures += 1
        if ht_fail_apt:
            self.apt_failures += 1
        if ht_startup_pass:
            self.startup_passes += 1

        return ht_fail_rct, ht_fail_apt, ht_startup_pass


def run_stream(dut: HealthTest, bits, restart_at=()) -> dict:
    """Drive ``dut`` over ``bits``, optionally restarting (``startup_req``) at
    the given 0-based sample indices. Returns per-event index lists."""
    restart_set = set(restart_at)
    rct_events: list[int] = []
    apt_events: list[int] = []
    startup_events: list[int] = []
    for i, bit in enumerate(bits):
        if i in restart_set:
            dut.step(startup_req=True)
        fail_rct, fail_apt, startup_pass = dut.step(raw_bit=bit, raw_valid=True)
        if fail_rct:
            rct_events.append(i)
        if fail_apt:
            apt_events.append(i)
        if startup_pass:
            startup_events.append(i)
    return {
        "rct_events": rct_events,
        "apt_events": apt_events,
        "startup_events": startup_events,
    }
