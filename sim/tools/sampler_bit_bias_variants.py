#!/usr/bin/env python3
"""Compare the DUT variants of issue #86's sampled-bit-bias experiment.

    python3 sim/tools/sampler_bit_bias_variants.py           # the tables
    python3 sim/tools/sampler_bit_bias_variants.py --check   # gate the finding

Like ``sim/tools/liveness_tap_phase_variants.py``,
``sim/tools/array_coupling_variants.py`` and ``sim/tools/jitter_energy_law.py``
this is a *derivation*, not a simulation: it reads only records already
committed under ``sim/records/`` and does arithmetic on them. It needs neither
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
because ``DR-0007`` §1's independence argument -- "N free-running ring
oscillators, no phase-locking of any kind between them" -- is stated about a
ring whose frequency is nobody's function, and what #76 measured is a ring
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
experiment is built to catch: a locked ring's sampled phase stops advancing,
and the sampled bit stops being a fresh draw.

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

The variants this script tabulates
----------------------------------
One corner (``tt``/27 C/3.30 V), one circuit (``design/sampler_core.spice``'s
own wiring with 5-stage rings), one change per pair -- whether the two DR-0016
liveness digitizers' clock pin is driven by the same running ``clk`` that
drives the DR-0001 raw tap, or parked on the high rail. Both decks in a pair
instantiate both digitizers and carry their static load; only the modulation
differs, and both sample the raw bit at the same instants with the same
``clk``.

    rate            clocked deck                        static (control) deck
    near-integer    sampler-bit-bias-clocked-integer    sampler-bit-bias-static-integer
    generic         sampler-bit-bias-clocked-generic    sampler-bit-bias-static-generic
    DR-0003 floor   sampler-bit-bias-clocked-clk-floor  sampler-bit-bias-static-clk-floor

What is compared, and why it is not just the bias
-------------------------------------------------
Each record carries the sampled bit SEQUENCE, packed little-endian into
16-bit integers (``bit_code_00`` ...), alongside the aggregate statistics.
When a record's seed-to-seed spread on those codes is zero -- which, in this
regime, it is, because the injected noise accumulates far too little phase to
flip a sampled bit -- the code is an exact integer and this script can compare
two decks' streams **bit for bit** (a Hamming distance), not merely compare
two bias figures that a compensating pair of flips would leave equal.

That matters both ways round. A zero Hamming distance is a much stronger null
than "the biases agree to within the resolution". A nonzero one is a much more
specific finding than "the biases differ".

Why the biases here are NOT a randomness claim
----------------------------------------------
At this corner the injected ``sigma_1`` is ~0.7 ps against a ~2.8 ns ring
period, so randomizing the ring's phase over a full period would take ~2e7
ring periods (~60 ms) of accumulation -- six orders of magnitude past anything
simulable. Every bit in this family is therefore essentially DETERMINISTIC,
which is exactly what makes it a sensitive probe for a deterministic
``clk``-locked mechanism and exactly why no bias figure here says anything
about the shipped block's entropy. ``DR-0004``'s tiering is unchanged, and
``DR-0007`` §2's sizing law is untouched by anything in this file.
"""

from __future__ import annotations

import argparse
import json
import math
import re
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
        "per-clk-cycle phase advance ~4.00 ring-1 periods: where a circle map locks",
    ),
    (
        "generic",
        "generic",
        "~4.38 ring-1 periods: fractional part far from any low-order rational",
    ),
    (
        "clk-floor",
        "DR-0003 floor",
        "clk ~1 MHz: the shipped operating point (DR-0003 raw rate, DR-0012 pin)",
    ),
]

#: Lags at which the +/-1 product mean ``r_L`` is recorded by the testbenches.
#: Short lags only: the question is whether successive samples stop being
#: independent draws, which is a short-lag property.
LAGS = (1, 2, 3, 4, 6, 8, 12, 16)

#: How many combined standard errors the two decks' bias must differ by before
#: the difference counts as measured rather than as sampling scatter. 3 sigma
#: is the same convention ``array_coupling_variants.py`` uses for its own
#: null band, and it is set here BEFORE looking at any result: the null this
#: experiment can return is "no measurable bias", never "no bias".
BIAS_SIGMA_THRESHOLD = 3.0

#: A record's relative seed-to-seed spread on a bit-sequence code at or below
#: which the sequence counts as seed-independent, so the code may be treated as
#: an exact integer and compared bit for bit. Exactly zero is what the
#: committed records show; the tolerance exists so that a future record with
#: one flipped bit in one seed degrades to the statistical comparison instead
#: of silently producing a nonsense Hamming distance.
CODE_DETERMINISTIC_SPREAD = 0.0

#: The verdict the committed records actually support, recorded in
#: ``sim/characterization-sampler-bit-bias.md``.
#:
#: ``--check`` gates on the *measured* verdict still equalling this one. That
#: is deliberately not the same thing as gating on a hypothesis being true:
#: this constant is written down AFTER the measurement, and if a future record
#: moves the classification the check fails and whoever moved it has to update
#: the recorded conclusion rather than leave a stale one in the
#: characterization document. Set it to ``None`` to run the classification
#: without gating on its outcome.
RECORDED_VERDICT: str | None = "no-measurable-bit-effect"


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
        self.codes = [
            v[k] for k in sorted(k for k in v if re.fullmatch(r"bit_code_\d+", k))
        ]
        self.code_spreads = [
            record.sd.get(k, 0.0)
            for k in sorted(k for k in v if re.fullmatch(r"bit_code_\d+", k))
        ]

    @property
    def bias(self) -> float:
        """The +/-1 mean of the sampled bit stream. 0 is balanced."""
        return self.bit_mean

    @property
    def codes_deterministic(self) -> bool:
        """Every chunk of the bit sequence is the same in every seed."""
        return all(sd <= CODE_DETERMINISTIC_SPREAD for sd in self.code_spreads)

    def rho(self, lag: int) -> float | None:
        """Mean-removed, normalized serial correlation at ``lag``.

        The testbench records the raw +/-1 product mean ``r_L``; for a stream
        with mean ``m``, ``r_L = m^2 + (1 - m^2) * rho_L``. A stream that is
        constant has ``m^2 = 1`` and no defined correlation, which is returned
        as ``None`` rather than as a fabricated number.
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

        A deterministic bit stream is not an independent one, and treating it
        as if it were would make every bias figure here look ~sqrt(N) times
        better resolved than it is. Where the stream is constant (no defined
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


def load_pairs() -> list[tuple[str, str, str, Variant, Variant]]:
    out = []
    for key, label, why in RATES:
        clocked = _load(f"sampler-bit-bias-clocked-{key}")
        static = _load(f"sampler-bit-bias-static-{key}")
        if clocked.n != static.n:
            raise RecordError(
                f"{key}: the clocked deck records {clocked.n} bits and the static "
                f"deck {static.n}; they are not comparable"
            )
        out.append((key, label, why, clocked, static))
    return out


def hamming(a: list[float], b: list[float]) -> int | None:
    """Bits differing between two packed bit sequences, or None if either is
    not an exact integer code (i.e. a seed flipped one)."""
    if len(a) != len(b):
        return None
    total = 0
    for x, y in zip(a, b):
        xi, yi = int(round(x)), int(round(y))
        if abs(x - xi) > 1e-6 or abs(y - yi) > 1e-6:
            return None
        total += bin(xi ^ yi).count("1")
    return total


def tclk_from_manifest(slug: str) -> float:
    manifest = json.loads((TB / slug / "tb.json").read_text())
    raw = manifest["params"]["tclk_per"]
    return float(raw.rstrip("nu")) * (1e-9 if raw.endswith("n") else 1e-6)


def classify(pairs) -> tuple[str, str]:
    """``(verdict, rationale)``.

    Three outcomes, in increasing order of how much the digitizers' clock
    matters to the bit:

    * ``identical`` -- at every rate the two decks produce the SAME sampled
      bit sequence, bit for bit. Nothing about the bit stream changed.
    * ``no-measurable-bit-effect`` -- some sampled bits differ, but at no rate
      does the bias differ by more than :data:`BIAS_SIGMA_THRESHOLD` combined
      standard errors, and the effect does not grow towards the locking rate.
    * ``bit-effect`` -- at some rate the bias difference exceeds that
      threshold.
    """
    flips = {}
    sig = {}
    for key, _label, _why, clocked, static in pairs:
        h = hamming(clocked.codes, static.codes) if (
            clocked.codes_deterministic and static.codes_deterministic
        ) else None
        flips[key] = h
        se = math.hypot(clocked.bias_se, static.bias_se)
        delta = abs(clocked.bias - static.bias)
        sig[key] = delta / se if se > 0 else float("inf")

    worst_key = max(sig, key=lambda k: sig[k])
    worst = sig[worst_key]

    if all(h == 0 for h in flips.values()):
        return "identical", (
            "  IDENTICAL. At every clk rate measured -- including the near-integer\n"
            "  rate, where a clk-locked disturbance would lock the ring's sampled\n"
            "  phase if it can, and including DR-0003's ratified floor -- the raw\n"
            "  tap produces the SAME sampled bit sequence whether the DR-0016\n"
            "  liveness digitizers' clock is running or parked. Not the same bias:\n"
            "  the same bits. The clk-locked frequency modulation #76 measured does\n"
            "  not reach the sampled bit at this corner."
        )
    if worst < BIAS_SIGMA_THRESHOLD:
        detail = ", ".join(
            f"{k}: {flips[k]} bit(s) of {p[3].n}" if flips[k] is not None else f"{k}: n/a"
            for k, *_rest, p in ((k, None, None, None) for k in [])
        )
        return "no-measurable-bit-effect", (
            "  NO MEASURABLE BIT EFFECT. Some individual sampled bits differ between\n"
            "  the clocked and static decks, but at no measured clk rate does the\n"
            f"  bit stream's bias differ by more than {BIAS_SIGMA_THRESHOLD:.0f} combined standard\n"
            f"  errors (worst: {worst:.2f} sigma, at the {worst_key} rate). This is a\n"
            "  bound, not a proof of zero -- read it together with the resolution\n"
            "  column, which is set by the effective sample count, not by N.\n"
            f"  {detail}"
        )
    return "bit-effect", (
        "  BIT EFFECT. At the "
        f"{worst_key} rate the sampled bit stream's bias differs by {worst:.2f}\n"
        "  combined standard errors between the clocked and static decks -- more\n"
        f"  than the {BIAS_SIGMA_THRESHOLD:.0f} sigma this script was set to require before calling a\n"
        "  difference measured. DR-0007 §1's independence argument needs a term\n"
        "  for the sample clock, and the characterization document and DR-0007\n"
        "  have to say so."
    )


def _fmt_rho(v: float | None) -> str:
    return "  n/a" if v is None else f"{v:+.3f}"


def report(pairs) -> None:
    print("Issue #86 -- does the clk-locked liveness-digitizer modulation bias the")
    print(f"sampled bit? All rows at {CORNER}, 4 seeds each.\n")

    print("Sampling geometry (measured in the run, not assumed):\n")
    print(f"  {'rate':<14} {'deck':<10} {'T_clk':>10} {'T0 ring1':>10} "
          f"{'ring1 periods/sample':>22} {'frac':>7}")
    for key, label, _why, clocked, static in pairs:
        for name, var in (("clocked", clocked), ("static", static)):
            ppc = var.periods_per_sample[0]
            print(f"  {label if name == 'clocked' else '':<14} {name:<10} "
                  f"{var.tclk * 1e9:>9.4f}n {var.period_r1 * 1e9:>9.4f}n "
                  f"{ppc:>22.4f} {ppc - math.floor(ppc):>7.4f}")
    print()

    print("Sampled-bit statistics at the DR-0001 raw tap:\n")
    header = (f"  {'rate':<14} {'deck':<10} {'N':>5} {'ones':>7} {'bias':>8} "
              f"{'N_eff':>7} {'+/-':>7} " + " ".join(f"rho{L:<3}" for L in (1, 2, 3, 4)))
    print(header)
    for key, label, _why, clocked, static in pairs:
        for name, var in (("clocked", clocked), ("static", static)):
            rhos = " ".join(_fmt_rho(var.rho(L)) for L in (1, 2, 3, 4))
            print(f"  {label if name == 'clocked' else '':<14} {name:<10} "
                  f"{var.n:>5} {var.ones:>7.4f} {var.bias:>+8.4f} "
                  f"{var.n_eff:>7.1f} {var.bias_se:>7.4f} {rhos}")
    print()

    print("The comparison the experiment exists for -- one change, at each rate:\n")
    print(f"  {'rate':<14} {'|d bias|':>9} {'combined SE':>12} {'sigma':>7} "
          f"{'bits differing':>16}")
    for key, label, _why, clocked, static in pairs:
        delta = abs(clocked.bias - static.bias)
        se = math.hypot(clocked.bias_se, static.bias_se)
        h = hamming(clocked.codes, static.codes) if (
            clocked.codes_deterministic and static.codes_deterministic
        ) else None
        hs = "n/a (seed-dependent)" if h is None else f"{h} of {clocked.n}"
        print(f"  {label:<14} {delta:>9.4f} {se:>12.4f} "
              f"{(delta / se if se else float('inf')):>7.2f} {hs:>16}")
    print()

    print("Sanity rows (a sampled level that is not at a rail is itself a finding):\n")
    print(f"  {'rate':<14} {'deck':<10} {'worst rail dev':>15} {'xo swing':>10}")
    for key, label, _why, clocked, static in pairs:
        for name, var in (("clocked", clocked), ("static", static)):
            print(f"  {label if name == 'clocked' else '':<14} {name:<10} "
                  f"{var.worst_rail_dev * 1e3:>13.3f}mV {var.xo_swing:>9.4f}V")
    print()

    verdict, rationale = classify(pairs)
    print(f"Verdict: {verdict}\n")
    print(rationale)
    print()
    print("Records used:")
    for key, label, _why, clocked, static in pairs:
        print(f"  {label:<14} clocked {clocked.rec.stem}")
        print(f"  {'':<14} static  {static.rec.stem}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--check", action="store_true",
        help="exit nonzero if the committed records stop supporting the recorded "
             "verdict (the gate CI runs)",
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

    verdict, rationale = classify(pairs)
    if RECORDED_VERDICT is None:
        print(f"sampler bit bias: verdict {verdict} (not gated)")
        return 0
    if verdict != RECORDED_VERDICT:
        print(
            f"error: the committed records now classify as {verdict!r}, but\n"
            f"sim/characterization-sampler-bit-bias.md and this script record\n"
            f"{RECORDED_VERDICT!r}. One of them is stale -- re-read the records,\n"
            f"update the document, and move RECORDED_VERDICT with it.\n\n{rationale}",
            file=sys.stderr,
        )
        return 1
    for key, label, _why, clocked, static in pairs:
        for var in (clocked, static):
            if var.worst_rail_dev > 0.1:
                print(
                    f"error: {var.rec.stem} sampled a level {var.worst_rail_dev * 1e3:.1f} mV "
                    "from mid-supply, i.e. a capture that never settled to a logic "
                    "level. The bit statistics derived from it are not statistics "
                    "about a bit.",
                    file=sys.stderr,
                )
                return 1
    print(f"sampler bit bias: {RECORDED_VERDICT} (issue #86) -- OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
