#!/usr/bin/env python3
"""Compare the DUT variants of issue #86's sampled-bit experiment.

    python3 sim/tools/sampler_bit_bias_variants.py           # the tables
    python3 sim/tools/sampler_bit_bias_variants.py --check   # gate the finding

Like ``sim/tools/liveness_tap_phase_variants.py``,
``sim/tools/array_coupling_variants.py`` and ``sim/tools/jitter_energy_law.py``
this is a *derivation*, not a simulation: it reads only evidence already
committed under ``sim/records/`` and does arithmetic on it. It needs neither
ngspice nor the PDK, and it writes nothing.

The question (issue #86)
------------------------
``sim/characterization-liveness-tap-phase-cost.md`` (#76, DR-0016 amendment A2)
measured that the DR-0016 per-ring liveness digitizer frequency-modulates the
ring it observes **in lockstep with clk**: 25.6 % apart on the raw ring node,
and, on the shipped DR-0018-buffered tap, a 19.9x ``clk``-locked residual that
is deterministic (0.12 % seed spread, ``L^0.96`` accumulation).

That is a measurement about PHASE, and #76 explicitly declined to turn it into
a claim about the sampled bit. Issue #86 is where that claim has to be earned,
because ``DR-0007`` §1's independence argument -- "N **free-running** ring
oscillators, no phase-locking of any kind between them" -- is stated about
rings whose frequency is nobody's function, and what #76 measured is a ring
whose instantaneous frequency is an exact function of the sampling clock's own
waveform. ``clk`` is an external pin (``DR-0012``) whose rate an integrator, or
an attacker, chooses.

The mechanism the experiment has to be able to see
--------------------------------------------------
The modulation repeats exactly once per clk period, so to first order the
deterministic phase advance between successive sampling instants is a
*constant* -- as it would be for a free-running ring, just a different
constant. What is not constant is the ring phase at which each clk EDGE lands,
and the size of the phase kick that edge delivers depends on where it lands.
That makes the sample-to-sample map a circle map rather than a pure rotation,
and a circle map LOCKS when the kick is large enough and the phase advance per
sample is near an integer number of ring periods. Locking is the failure this
experiment is built to catch: a locked ring's sampled phase stops advancing and
the sampled bit stops being a fresh draw.

Two consequences set the sweep:

* the dangerous clk rates are those where the per-clk-cycle phase advance is
  NEAR AN INTEGER number of ring periods (``-integer``); the informative
  background is a rate whose fractional part is far from any low-order
  rational (``-generic``);
* there are exactly two clk edges per clk period whatever the rate, so the
  deterministic kick per sample is rate-independent while the jitter that
  would smear it grows with the sample period. A FAST clk is therefore the
  conservative direction, and DR-0003's ratified floor (``-clk-floor``) is the
  shipped operating point rather than the worst one.

The variants
------------
One corner (``tt``/27 C/3.30 V), one circuit (``design/sampler_core.spice``'s
own wiring with 5-stage rings), one change per pair -- whether the two DR-0016
liveness digitizers' clock pin is driven by the same running ``clk`` that
drives the DR-0001 raw tap, or parked on the high rail. Both decks in a pair
instantiate both digitizers and carry their static load; both sample the raw
bit at the same instants with the same ``clk``; both draw the same noise
realization from a given seed, because they carry the same noise sources in
the same order. Only the modulation differs.

    rate            clocked deck                        static (control) deck
    near-integer    sampler-bit-bias-clocked-integer    sampler-bit-bias-static-integer
    generic         sampler-bit-bias-clocked-generic    sampler-bit-bias-static-generic
    DR-0003 floor   sampler-bit-bias-clocked-clk-floor  sampler-bit-bias-static-clk-floor

What is compared, and what deliberately is NOT
-----------------------------------------------
Running the liveness digitizers' clock instead of parking it changes two things
about the ring at once, and only one of them is the question:

1. the **mean** load on the buffer output moves, because a 50 % duty-cycle
   clock spends half its time at each of the two endpoint loads while a parked
   clock spends all of it at one. That shifts the ring's mean FREQUENCY by a
   fraction of a percent -- a static-load effect that any extra capacitance
   would produce, and one #51's ladder already established is innocent;
2. the load is **modulated in lockstep with clk**, which is #76's finding and
   #86's question.

Effect 1 makes the two decks' raw bit SEQUENCES incomparable, and it is
important to say why rather than to quietly report a big number. A ~0.2 %
difference in mean ring period, accumulated over the ~1000 ring periods a
256-sample window spans, is more than a full ring cycle of relative phase: the
two decks sample the same source at slightly different effective ratios, so
their bit streams decorrelate completely no matter what the modulation does.
The Hamming distance between them is therefore reported below as a
**diagnostic**, next to the ~N/2 a pair of decorrelated streams would give, and
it is deliberately kept out of the gate.

What IS compared, and gated:

* the bit stream's **bias** and its **short-lag serial correlations**, which
  are properties of the statistics rather than of the particular phase the
  window happened to start on;
* the ring's **phase advance per sample**, measured on the ring itself and not
  through the XOR -- the mechanism-level test. A ring pulled into lock by a
  clk-locked disturbance runs at exactly ``T_clk / N``; a ring merely loaded
  differently does not, and the two are told apart by whether the shift depends
  on how close ``T_clk / T_0`` sits to an integer. Doing this on the ring
  matters, because the XOR can hide a locked ring behind its still-free twin.

Why this reads the raw output as well as the records
----------------------------------------------------
The record carries each measured quantity as a mean and a seed-to-seed spread,
which is the right summary for a scalar and the wrong one for a bit *sequence*.
The sequence diagnostic above, and the noise's own baseline it is read against,
therefore come from each record's own committed raw ngspice output
(``sim/records/raw/<stem>/*.log``, whose checksums
``sim/tools/verify_record_checksums.py`` verifies on every pull request and
which ``sim/README.md`` requires be committed with the record). The ``bk``
measurements in run order ARE the sampled bit stream for that seed.

Every gated figure still comes from the record's own ``## Result`` block.

Why the biases here are NOT a randomness claim
----------------------------------------------
At this corner the injected ``sigma_1`` is ~0.7 ps against a ~2.8 ns ring
period, so randomizing the ring's phase over a full period would take ~2e7 ring
periods (~60 ms) of accumulation -- orders of magnitude past anything simulable.
The bits here are very nearly deterministic, which is exactly what makes them a
sensitive probe for a deterministic ``clk``-locked mechanism and exactly why no
bias figure here says anything about the shipped block's entropy. ``DR-0004``'s
tiering is unchanged, and ``DR-0007`` §2's sizing law is untouched by anything
in this file.
"""

from __future__ import annotations

import argparse
import math
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from starved_cell_jitter_energy import Record, RecordError  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"
TB = REPO_ROOT / "sim" / "tb"

#: The one corner this experiment is run at -- the corner #51's coupling
#: ladder and #76's phase family were run at, so all three are comparable.
CORNER = "tt/27/3.30"

#: ``(rate key, human label, what the rate was chosen for)``
RATES = [
    (
        "integer",
        "near-integer",
        "phase advance ~4.00 ring-1 periods per sample: where a circle map locks",
    ),
    (
        "generic",
        "generic",
        "~4.38 periods per sample: fractional part far from a low-order rational",
    ),
    (
        "clk-floor",
        "DR-0003 floor",
        "clk ~1 MHz: the shipped operating point (DR-0003 rate, DR-0012 pin)",
    ),
]

#: Lags at which the +/-1 product mean ``r_L`` is recorded by the testbenches.
#: Short lags: the question is whether successive samples stop being independent
#: draws, which is a short-lag property.
LAGS = (1, 2, 3, 4, 6, 8, 12, 16)

#: How many combined standard errors the two decks' bias must differ by before
#: the difference counts as measured rather than as sampling scatter. Set here
#: before any result was looked at. The null this experiment can return is
#: "no measurable bias", never "no bias".
BIAS_SIGMA_THRESHOLD = 3.0

#: How many combined standard errors the clocked deck's short-lag serial
#: correlation may exceed the static deck's by. Same convention and same number
#: as the bias bound: bias alone would miss a rearrangement that preserves the
#: mean, and correlation alone would miss a tilt that preserves the structure.
RHO_SIGMA_THRESHOLD = 3.0

#: How much larger the FRACTIONAL frequency shift between the two arrangements
#: may be at a near-integer rate than off resonance before it counts as
#: injection PULLING rather than as a static-load offset.
#:
#: This is the discriminator that needs no threshold on the shift's own size,
#: only on its rate-dependence, and it is the right one: a load offset is the
#: same fraction of the ring's frequency at any clk rate, while pulling by
#: definition grows as the ratio approaches a rational. A ratio at or below 1.0
#: means the shift is, if anything, SMALLER where pulling would be strongest.
PULL_RESONANCE_FACTOR = 2.0

#: How close ``ring1_periods_per_sample`` has to sit to a whole number for a
#: rate to count as ON RESONANCE for the pulling test above. Loose on purpose:
#: it only has to separate the sweep's resonant points from its off-resonance
#: one, and a locking tongue that reached 0.05 of a period per sample would be
#: two orders of magnitude wider than anything these records show.
RESONANCE_WINDOW = 0.05

#: How close a ring's measured phase advance per sample has to sit to a whole
#: number of its own periods before it counts as PHASE-LOCKED to ``clk``.
#:
#: This is the mechanism-level test, and it does not go through the XOR at all.
#: A ring pulled into lock by a ``clk``-locked disturbance runs at exactly
#: ``T_clk / N``, so its measured ``ring1_periods_per_sample`` would be exactly
#: ``N`` -- to within the measurement's own scatter, which the committed records
#: put at ~5e-5 seed to seed on that quantity. 5e-4 is ~10x that: far enough
#: above the scatter that a locked ring cannot fail the test by accident, and
#: far enough below any free-running ratio that a free ring cannot pass it.
LOCK_TOLERANCE = 5e-4

#: The verdict the committed records actually support, recorded in
#: ``sim/characterization-sampler-bit-bias.md``.
#:
#: ``--check`` gates on the *measured* verdict still equalling this one. That is
#: deliberately not the same thing as gating on a hypothesis being true: this
#: constant is written down AFTER the measurement, and if a future record moves
#: the classification the check fails and whoever moved it has to update the
#: recorded conclusion rather than leave a stale one in the characterization
#: document. Set it to ``None`` to run the classification without gating.
RECORDED_VERDICT: str | None = "no-measurable-bit-effect"

_BK = re.compile(r"^bk\s+=\s+(-?[\d.]+e[-+]?\d+)\s*$", re.M)
_RAW_PATH = re.compile(r"^raw:\s*\n\s*path:\s*(\S+)", re.M)


def read_bit_streams(record: Record, n_samples: int, vdd: float) -> list[list[int]]:
    """The per-seed sampled bit sequences behind ``record``, from its own
    committed raw ngspice output.

    One list per seed, in run order, each ``n_samples`` bits long. Raises
    ``RecordError`` rather than guessing if the raw output is missing or does
    not contain exactly the expected number of samples -- a truncated sequence
    silently compared against a full one would produce a meaningless Hamming
    distance.
    """
    text = record.path.read_text()
    m = _RAW_PATH.search(text)
    if m is None:
        raise RecordError(f"{record.stem}: no raw.path in the frontmatter")
    raw_dir = REPO_ROOT / m.group(1)
    logs = sorted(raw_dir.glob("*-run*.log"))
    if not logs:
        raise RecordError(f"{record.stem}: no raw ngspice logs under {raw_dir}")
    streams = []
    for log in logs:
        values = [float(v) for v in _BK.findall(log.read_text())]
        if len(values) != n_samples:
            raise RecordError(
                f"{record.stem}: {log.name} carries {len(values)} sampled bits, "
                f"but the record says n_samples = {n_samples}"
            )
        streams.append([1 if v > 0.5 * vdd else 0 for v in values])
    return streams


def _hamming(a: list[int], b: list[int]) -> int:
    return sum(1 for x, y in zip(a, b) if x != y)


class Variant:
    """One deck's record at :data:`CORNER`, with its bit statistics."""

    def __init__(self, slug: str, record: Record) -> None:
        self.slug = slug
        self.rec = record
        v = record.values
        self.n = int(round(v["n_samples"]))
        self.ones = v["ones_frac"]
        self.bit_mean = v["bit_mean"]
        self.periods_per_sample = (
            v["ring1_periods_per_sample"],
            v["ring2_periods_per_sample"],
        )
        self.period_r1 = v["period_r1"]
        self.period_r2 = v["period_r2"]
        self.tclk = v["tclk_s"]
        self.worst_rail_dev = v["worst_rail_dev_v"]
        self.xo_swing = v["xo_swing_v"]
        self.r = {L: v[f"r_{L}"] for L in LAGS if f"r_{L}" in v}
        self.streams = read_bit_streams(record, self.n, record.vdd)

    @property
    def bias(self) -> float:
        """The +/-1 mean of the sampled bit stream. 0 is balanced."""
        return self.bit_mean

    @property
    def seed_divergence(self) -> float:
        """Mean Hamming distance between two different SEEDS of this deck.

        The noise's own effect on the sampled bit sequence, in the same units
        as the clocked-vs-static comparison: the yardstick that comparison has
        to be read against.
        """
        pairs = [
            _hamming(self.streams[i], self.streams[j])
            for i in range(len(self.streams))
            for j in range(i + 1, len(self.streams))
        ]
        return statistics.fmean(pairs) if pairs else 0.0

    def rho(self, lag: int) -> float | None:
        """Mean-removed, normalized serial correlation at ``lag``.

        The testbench records the raw +/-1 product mean ``r_L``; for a stream
        with mean ``m``, ``r_L = m^2 + (1 - m^2) * rho_L``. A constant stream
        has ``m^2 = 1`` and no defined correlation, returned as ``None`` rather
        than as a fabricated number.
        """
        if lag not in self.r:
            return None
        m = self.bit_mean
        denom = 1.0 - m * m
        if denom <= 1e-9:
            return None
        return (self.r[lag] - m * m) / denom

    @property
    def n_eff(self) -> float:
        """Effective independent sample count, from the measured short-lag
        correlations: ``N / (1 + 2 * sum_L rho_L)``.

        A nearly-deterministic bit stream is not an independent one, and
        treating it as if it were would make every bias figure here look better
        resolved than it is. Where the stream is constant (no defined
        correlation) the effective count is 1: one constant is one observation.
        """
        rhos = [self.rho(L) for L in (1, 2, 3, 4)]
        if any(r is None for r in rhos):
            return 1.0
        factor = 1.0 + 2.0 * sum(r for r in rhos if r is not None)
        if factor <= 0:
            return float(self.n)
        return max(1.0, min(float(self.n), self.n / factor))

    @property
    def bias_se(self) -> float:
        """Standard error on :attr:`bias`, from the effective sample count."""
        p = self.ones
        return 2.0 * math.sqrt(max(p * (1.0 - p), 1e-6) / self.n_eff)


class Pair:
    """One clk rate's clocked deck and its one-line-different control."""

    def __init__(self, key: str, label: str, why: str,
                 clocked: Variant, static: Variant) -> None:
        self.key = key
        self.label = label
        self.why = why
        self.clocked = clocked
        self.static = static
        if clocked.n != static.n:
            raise RecordError(
                f"{key}: the clocked deck records {clocked.n} bits and the static "
                f"deck {static.n}; they are not comparable"
            )
        if len(clocked.streams) != len(static.streams):
            raise RecordError(
                f"{key}: {len(clocked.streams)} clocked seeds against "
                f"{len(static.streams)} static seeds; the comparison is not paired"
            )

    @property
    def n(self) -> int:
        return self.clocked.n

    @property
    def paired_hamming(self) -> list[int]:
        """Per-seed Hamming distance between the two decks' bit streams."""
        return [
            _hamming(c, s)
            for c, s in zip(self.clocked.streams, self.static.streams)
        ]

    @property
    def variant_divergence(self) -> float:
        return statistics.fmean(self.paired_hamming)

    @property
    def noise_divergence(self) -> float:
        """The noise's own baseline, pooled over both decks."""
        return statistics.fmean(
            [self.clocked.seed_divergence, self.static.seed_divergence]
        )

    @property
    def bias_delta(self) -> float:
        return abs(self.clocked.bias - self.static.bias)

    @property
    def bias_se(self) -> float:
        return math.hypot(self.clocked.bias_se, self.static.bias_se)

    @property
    def bias_sigma(self) -> float:
        return self.bias_delta / self.bias_se if self.bias_se else float("inf")

    @property
    def lock_margin(self) -> float:
        """How far the clocked deck's ring-1 phase advance per sample sits from
        the nearest whole number of ring periods.

        Zero (to within measurement scatter) is a ring phase-locked to ``clk``.
        This is measured on the ring itself and does not pass through the XOR,
        so it cannot be masked by the other ring still running free.
        """
        ppc = self.clocked.periods_per_sample[0]
        return abs(ppc - round(ppc))

    @property
    def pull(self) -> float:
        """How far the digitizers' running clock moves ring 1's phase advance
        per sample, against the same deck with that clock parked.

        Injection pulling short of lock shows up here as a shift that GROWS as
        the ratio approaches an integer; a static-load difference shows up as
        the same fractional frequency shift at every rate. Which of the two it
        is, is read off the rate-dependence, not off the size.
        """
        return (self.clocked.periods_per_sample[0]
                - self.static.periods_per_sample[0])

    @property
    def frequency_shift(self) -> float:
        """The clocked deck's mean ring-1 period against the static deck's, as
        a fraction. Positive means the running clock makes the ring faster."""
        return (self.static.period_r1 - self.clocked.period_r1) / self.static.period_r1

    @property
    def rho_delta_sigma(self) -> tuple[int, float]:
        """``(lag, sigma)`` for the short lag at which the clocked deck's serial
        correlation most exceeds the static deck's, in combined standard errors.

        The standard error of a serial correlation estimated from N samples is
        ~1/sqrt(N) under the null, so the combined error on a difference of two
        is ~sqrt(2/N). Magnitudes are compared, not signed values: the question
        is whether the modulation adds structure, in either direction.
        """
        se = math.sqrt(2.0 / self.n)
        worst_lag, worst = 1, 0.0
        for lag in (1, 2, 3, 4):
            rc, rs = self.clocked.rho(lag), self.static.rho(lag)
            if rc is None or rs is None:
                continue
            d = (abs(rc) - abs(rs)) / se
            if d > worst:
                worst_lag, worst = lag, d
        return worst_lag, worst

    @property
    def decorrelated_reference(self) -> float:
        """Bits two INDEPENDENT streams of these two biases would differ in.

        The yardstick the raw Hamming distance has to be read against: for
        streams with +/-1 means ``m_c`` and ``m_s`` and no relation to each
        other, the expected disagreement fraction is ``(1 - m_c * m_s) / 2``.
        """
        m = self.clocked.bias * self.static.bias
        return self.n * (1.0 - m) / 2.0


def _load(slug: str) -> Variant:
    matches = []
    for path in sorted(RECORDS.glob(f"*-{slug}-*.md")):
        rec = Record(path)
        if rec.corner != CORNER or "ones_frac" not in rec.values:
            continue
        matches.append(rec)
    if not matches:
        raise RecordError(
            f"no sim/records/*-{slug}-*.md record at {CORNER} carries an "
            "ones_frac, so this variant cannot be compared"
        )
    # Latest record wins; earlier ones stay on file as append-only evidence.
    return Variant(slug, matches[-1])


def load_pairs() -> list[Pair]:
    return [
        Pair(key, label, why,
             _load(f"sampler-bit-bias-clocked-{key}"),
             _load(f"sampler-bit-bias-static-{key}"))
        for key, label, why in RATES
    ]


def classify(pairs: list[Pair]) -> tuple[str, str]:
    """``(verdict, rationale)``.

    ``no-measurable-bit-effect`` requires all four of these, each of which
    would fail on its own:

    * **bias** -- at no rate does the sampled stream's bias differ between the
      clocked and static decks by more than :data:`BIAS_SIGMA_THRESHOLD`
      combined standard errors;
    * **serial correlation** -- at no rate does the clocked deck's short-lag
      correlation exceed the static deck's by more than
      :data:`RHO_SIGMA_THRESHOLD` combined standard errors. Bias alone would
      miss a rearrangement that preserves the mean;
    * **no lock** -- at no rate does ring 1's phase advance per sample sit
      within :data:`LOCK_TOLERANCE` of a whole number of its own periods. This
      is checked on the ring, because the XOR can hide a locked ring behind its
      still-free twin, and both bit-level bounds above would then pass;
    * **no pulling** -- the frequency shift between the two arrangements is not
      larger near the integer ratio than away from it by more than
      :data:`PULL_RESONANCE_FACTOR`. This is what separates injection pulling
      short of lock from an ordinary static-load offset, and it needs no
      threshold on the shift's own size.

    Anything else is ``bit-effect``, with the failing bound named.
    """
    locked = [p for p in pairs if p.lock_margin < LOCK_TOLERANCE]
    if locked:
        p = locked[0]
        return "bit-effect", (
            f"  RING PHASE-LOCKED TO CLK. At the {p.label} rate the clocked deck's\n"
            f"  ring 1 advances {p.clocked.periods_per_sample[0]:.5f} of its own periods per sample --\n"
            f"  within {LOCK_TOLERANCE:g} of a whole number, i.e. running at exactly T_clk/N.\n"
            "  A locked ring's sampled phase does not advance, whatever the XOR's\n"
            "  other input is doing, so this is a finding about the entropy source\n"
            "  even where the bit-level bounds pass. DR-0007 §1's 'free-running, no\n"
            "  phase-locking of any kind' is the sentence at issue."
        )

    worst_bias = max(pairs, key=lambda p: p.bias_sigma)
    worst_rho = max(pairs, key=lambda p: p.rho_delta_sigma[1])
    rho_lag, rho_sigma = worst_rho.rho_delta_sigma

    # The pulling test, on the SCALE-FREE shift: a static-load offset is the
    # same fraction of the ring's frequency at any clk rate, pulling is not.
    # "On resonance" is every rate whose phase advance per sample sits within
    # RESONANCE_WINDOW of a whole number -- which in this sweep is more rates
    # than were deliberately placed there.
    on_res = [p for p in pairs if p.lock_margin < RESONANCE_WINDOW]
    off_res = [p for p in pairs if p.lock_margin >= RESONANCE_WINDOW]
    pull_ratio = None
    if on_res and off_res:
        base = statistics.fmean([abs(p.frequency_shift) for p in off_res])
        peak = max(abs(p.frequency_shift) for p in on_res)
        pull_ratio = float("inf") if base == 0 and peak > 0 else (peak / base if base else 0.0)

    failures = []
    if worst_bias.bias_sigma >= BIAS_SIGMA_THRESHOLD:
        failures.append(
            f"  BIAS. At the {worst_bias.label} rate the sampled stream's bias differs by\n"
            f"  {worst_bias.bias_sigma:.2f} combined standard errors between the clocked and static decks,\n"
            f"  past the {BIAS_SIGMA_THRESHOLD:.0f} sigma this script requires before calling a difference\n"
            "  measured."
        )
    if rho_sigma >= RHO_SIGMA_THRESHOLD:
        failures.append(
            f"  SERIAL CORRELATION. At the {worst_rho.label} rate the clocked deck's lag-{rho_lag}\n"
            f"  correlation exceeds the static deck's by {rho_sigma:.2f} combined standard errors,\n"
            f"  past the {RHO_SIGMA_THRESHOLD:.0f} sigma threshold. The modulation is adding structure to\n"
            "  the bit stream that the same circuit without it does not have."
        )
    if pull_ratio is not None and pull_ratio > PULL_RESONANCE_FACTOR:
        failures.append(
            f"  INJECTION PULLING. The fractional frequency shift the digitizers'\n"
            f"  running clock causes is {pull_ratio:.2f}x larger on resonance than off it, past the\n"
            f"  {PULL_RESONANCE_FACTOR:.1f}x threshold. A static load offset does not depend on how close\n"
            "  T_clk/T_0 sits to an integer; pulling does."
        )

    if failures:
        return "bit-effect", (
            "  BIT EFFECT -- the following bound(s) failed.\n\n"
            + "\n\n".join(failures)
            + "\n\n  DR-0007 §1's independence argument needs a term for the sample clock,\n"
              "  and the characterization document and DR-0007 have to say so."
        )

    pull_line = (
        "      df/f "
        + ", ".join(f"{p.frequency_shift * 100:+.3f}% ({p.label})" for p in pairs)
        + f";\n      ratio on/off resonance {pull_ratio:.2f}x.\n"
        if pull_ratio is not None
        else "      (the sweep has no on- and off-resonance rate to compare; not evaluated)\n"
    )
    return "no-measurable-bit-effect", (
        "  NO MEASURABLE BIT EFFECT, on four bounds each of which would have failed\n"
        "  separately.\n"
        f"  (a) Bias: worst {worst_bias.bias_sigma:.2f} sigma, at the {worst_bias.label} rate,\n"
        f"      against a {BIAS_SIGMA_THRESHOLD:.0f} sigma threshold.\n"
        f"  (b) Serial correlation: the clocked deck's short-lag correlation exceeds\n"
        f"      the static deck's by at most {rho_sigma:.2f} sigma (lag {rho_lag}, {worst_rho.label} rate),\n"
        f"      against a {RHO_SIGMA_THRESHOLD:.0f} sigma threshold.\n"
        "  (c) No lock: ring 1's phase advance per sample stays "
        f"{min(p.lock_margin for p in pairs):.5f} periods\n"
        f"      clear of a whole number at its closest, against a {LOCK_TOLERANCE:g} tolerance.\n"
        "  (d) No pulling: the frequency shift between the two arrangements does not\n"
        "      grow towards the integer ratio --\n"
        + pull_line +
        "  This is a bound, not a proof of zero. Read it with the resolution column,\n"
        "  which is set by the EFFECTIVE sample count, not by N.\n"
    )


def _fmt_rho(v: float | None) -> str:
    return "   n/a" if v is None else f"{v:+.3f}"


def report(pairs: list[Pair]) -> None:
    print("Issue #86 -- does the clk-locked liveness-digitizer modulation reach the")
    print(f"sampled bit? All rows at {CORNER}, 4 seeds each.\n")

    print("Sampling geometry, measured in the run rather than assumed:\n")
    print(f"  {'rate':<14} {'deck':<8} {'T_clk':>11} {'T0 ring1':>10} "
          f"{'ring1 per/sample':>17} {'frac':>7}")
    for p in pairs:
        for name, var in (("clocked", p.clocked), ("static", p.static)):
            ppc = var.periods_per_sample[0]
            print(f"  {p.label if name == 'clocked' else '':<14} {name:<8} "
                  f"{var.tclk * 1e9:>10.4f}n {var.period_r1 * 1e9:>9.4f}n "
                  f"{ppc:>17.4f} {ppc - math.floor(ppc):>7.4f}")
    print()

    print("Sampled-bit statistics at the DR-0001 raw tap:\n")
    print(f"  {'rate':<14} {'deck':<8} {'N':>4} {'ones':>7} {'bias':>8} "
          f"{'N_eff':>6} {'+/-':>7}  " + "".join(f"rho{L:<4}" for L in (1, 2, 3, 4)))
    for p in pairs:
        for name, var in (("clocked", p.clocked), ("static", p.static)):
            rhos = " ".join(_fmt_rho(var.rho(L)) for L in (1, 2, 3, 4))
            print(f"  {p.label if name == 'clocked' else '':<14} {name:<8} "
                  f"{var.n:>4} {var.ones:>7.4f} {var.bias:>+8.4f} "
                  f"{var.n_eff:>6.1f} {var.bias_se:>7.4f}  {rhos}")
    print()

    print("GATED -- the two bit-level bounds, one line different, per rate:\n")
    print(f"  {'rate':<14} {'|d bias|':>9} {'comb SE':>8} {'sigma':>6}   "
          f"{'worst |d rho|':>13} {'lag':>4} {'sigma':>6}")
    for p in pairs:
        lag, sig = p.rho_delta_sigma
        drho = sig * math.sqrt(2.0 / p.n)
        print(f"  {p.label:<14} {p.bias_delta:>9.4f} {p.bias_se:>8.4f} "
              f"{p.bias_sigma:>6.2f}   {drho:>13.4f} {lag:>4} {sig:>6.2f}")
    print()

    print("GATED -- the mechanism test, measured on ring 1 and not through the XOR:\n")
    print(f"  {'rate':<14} {'clocked per/sample':>19} {'nearest int':>12} "
          f"{'|margin|':>9} {'pull':>11} {'df/f':>9}")
    for p in pairs:
        ppc = p.clocked.periods_per_sample[0]
        print(f"  {p.label:<14} {ppc:>19.5f} {round(ppc):>12d} "
              f"{p.lock_margin:>9.5f} {p.pull:>+11.6f} {p.frequency_shift * 100:>+8.3f}%")
    print()
    print("  A ring locked to clk/N runs at exactly T_clk/N, i.e. |margin| = 0 to within")
    print(f"  the ~5e-5 seed-to-seed scatter these records show on that quantity; the gate")
    print(f"  calls a ring locked below |margin| < {LOCK_TOLERANCE:g}. 'pull' is how far running the")
    print("  digitizers' clock moves that advance against parking it, and 'df/f' the same")
    print("  thing as a fractional frequency shift: a static-load offset is the same df/f")
    print("  at every rate, while injection pulling grows towards the integer ratio.")
    print()

    print("NOT GATED -- raw sequence divergence, reported so it is not mistaken for a")
    print("bound. The df/f above is enough to slide the two decks' ring phases past each")
    print("other several times inside the window, so their bit streams decorrelate")
    print("whatever the modulation does:\n")
    print(f"  {'rate':<14} {'bits moved':>11} {'if decorrelated':>16} "
          f"{'noise baseline':>15} {'phase slip':>11}")
    for p in pairs:
        slip = abs(p.frequency_shift) * p.n * p.clocked.periods_per_sample[0]
        print(f"  {p.label:<14} {p.variant_divergence:>7.2f}/{p.n:<3} "
              f"{p.decorrelated_reference:>12.1f}/{p.n:<3} "
              f"{p.noise_divergence:>11.2f}/{p.n:<3} {slip:>9.2f} cyc")
    print()
    print("  'bits moved'      mean over seeds of the Hamming distance between the two")
    print("                    decks' sampled bit streams at the SAME seed.")
    print("  'if decorrelated' what two unrelated streams of these two biases would give.")
    print("  'noise baseline'  mean Hamming distance between two different SEEDS of the")
    print("                    same deck: what redrawing the noise alone does.")
    print("  'phase slip'      ring-1 cycles the two decks' phases slide apart across the")
    print("                    window, from df/f alone.")
    print()

    print("Sanity rows -- a sampled level that is not at a rail is itself a finding:\n")
    print(f"  {'rate':<14} {'deck':<8} {'worst rail dev':>15} {'xo swing':>10}")
    for p in pairs:
        for name, var in (("clocked", p.clocked), ("static", p.static)):
            print(f"  {p.label if name == 'clocked' else '':<14} {name:<8} "
                  f"{var.worst_rail_dev * 1e3:>13.3f}mV {var.xo_swing:>9.4f}V")
    print()

    verdict, rationale = classify(pairs)
    print(f"Verdict: {verdict}\n")
    print(rationale)
    print()
    print("Records used:")
    for p in pairs:
        print(f"  {p.label:<14} clocked {p.clocked.rec.stem}")
        print(f"  {'':<14} static  {p.static.rec.stem}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--check", action="store_true",
        help="exit nonzero if the committed evidence stops supporting the "
             "recorded verdict (the gate CI runs)",
    )
    args = ap.parse_args(argv)

    try:
        pairs = load_pairs()
    except RecordError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not args.check:
        report(pairs)
        return 0

    for p in pairs:
        for var in (p.clocked, p.static):
            if var.worst_rail_dev > 0.1:
                print(
                    f"error: {var.rec.stem} sampled a level "
                    f"{var.worst_rail_dev * 1e3:.1f} mV from the nearer supply rail, i.e. a "
                    "capture that never settled to a logic level. Bit statistics "
                    "taken off that are not statistics about a bit.",
                    file=sys.stderr,
                )
                return 1

    verdict, rationale = classify(pairs)
    if RECORDED_VERDICT is None:
        print(f"sampler bit bias: verdict {verdict} (not gated)")
        return 0
    if verdict != RECORDED_VERDICT:
        print(
            f"error: the committed evidence now classifies as {verdict!r}, but\n"
            "sim/characterization-sampler-bit-bias.md and this script record\n"
            f"{RECORDED_VERDICT!r}. One of them is stale -- re-read the records,\n"
            "update the document, and move RECORDED_VERDICT with it.\n\n"
            f"{rationale}",
            file=sys.stderr,
        )
        return 1
    print(f"sampler bit bias: {RECORDED_VERDICT} (issue #86) -- OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
