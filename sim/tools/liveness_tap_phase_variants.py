#!/usr/bin/env python3
"""Compare the DUT variants of issue #76's liveness-tap phase-cost experiment.

    python3 sim/tools/liveness_tap_phase_variants.py           # the tables
    python3 sim/tools/liveness_tap_phase_variants.py --check   # gate the finding

Like ``sim/tools/array_coupling_variants.py``, ``sim/tools/jitter_energy_law.py``
and ``sim/tools/starved_cell_jitter_energy.py`` this is a *derivation*, not a
simulation: it reads only records already committed under ``sim/records/`` and
does arithmetic on them. It needs neither ngspice nor the PDK, and it writes
nothing.

The question (issue #76)
------------------------
``sim/characterization-array-ring-coupling.md`` (#51) indicted one arrangement:
a ring node sharing an input stage with something else that is switching. At
``tt``/27 C/3.30 V that measured ``sigma_1`` at 28.6x the standalone ring's,
against 1.06x for the same gate load with the neighbour held on a rail.

``design/sampler_core.spice`` contains that shape a second time. ``xsr1`` /
``xsr2`` -- the DR-0016 per-ring liveness digitizers shipped by #71 -- put each
ring node on a ``sampler_dff`` ``d`` input, which in that cell is the channel
terminal of a transmission gate whose GATES are driven by ``clk``:

    XMtdp d clk  m vdd pfet_03v3 W=0.44u
    XMtdn d clkb m vss nfet_03v3 W=0.22u

``sim/tb/ring-liveness-tap-power/`` measured what that costs the rings in
POWER. Nothing measured what it costs them in PHASE, and ``clk`` is an
external, attacker-rate pin (DR-0012), so a disturbance locked to it is
coherent with the sampling instant by construction.

What PR #82 changed underneath the question
-------------------------------------------
While this experiment was being built, PR #82 (issue #75) adopted a per-ring
output buffer: ``design/sampler_core.spice`` now reads ``xr1 ... rn1``,
``xb1 rn1 ro1 vdd vss ro_buf``, ``xsr1 ro1 clk ...``, so the digitizer taps
the BUFFER's output and not the ring's own node. That adoption was decided on
the *combiner*-path evidence in
``sim/characterization-ring-buffer-mitigation.md``; nothing measured what it
did to the *digitizer* path. So issue #76's question did not go away, it split
in two, and both halves are measured here:

* what the pre-#82 direct tap cost the ring in phase, and
* whether the buffer #82 adopted removes that cost on this path too.

The variants this script tabulates
----------------------------------
One corner (``tt``/27 C/3.30 V), one window geometry (the control's: opened
256 periods after start-up, spanning 512 periods), one change per pair:

1. ``ro-ring5-starved-jitter-long``        one ring, nothing attached (CONTROL)
2. ``ring-liveness-tap-phase-clk-high``    + the digitizer ON THE RING NODE,
                                           clk on the HIGH rail (master
                                           transmission gate OFF)
3. ``ring-liveness-tap-phase-clk-low``     + the same, clk on the LOW rail
                                           (master transmission gate ON)
4. ``ring-liveness-tap-phase-clocked``     + the same, clk RUNNING  <- pre-#82
                                           shipped topology
5. ``ring-liveness-tap-phase-buffered``    variant 4 with the shipped ``ro_buf``
                                           between ring node and tap  <- post-#82
                                           shipped topology
6. ``ring-liveness-tap-phase-buffered-static``  variant 5 with clk on the HIGH
                                           rail: the buffered pair's static
                                           reference

Variants 2 and 3 are the two static endpoints a running ``clk`` alternates
between; the gap between them is the rate-independent part of the result,
because a 50 % duty-cycle clock puts the ring in each state half the time
whatever its frequency.

The clk-locked question is then asked **inside each topology**, against that
topology's own static reference, so exactly one thing differs between
numerator and denominator (clk toggles / clk does not):

    unbuffered   sigma_1(4 clocked)  / sigma_1(2 clk-high)
    buffered     sigma_1(5 buffered) / sigma_1(6 buf-static)

That is #51's variant-3-against-variant-2 discipline applied twice, and it is
the pairing ``sim/characterization-ring-buffer-mitigation.md`` argues for:
inserting a buffer changes two things about a ring at once (it isolates the
node AND it lightens the load), so a ratio taken across the buffer insertion
spans two changes and attributes neither.

Why the sigmas here are RAW
---------------------------
``starved_cell_jitter_energy.py`` scales each record's ``sigma`` by that
corner's device-noise density, because it compares figures across corners.
Every record here is at the same corner with the same fixed injected density,
so the scaling is a common factor and is deliberately *not* applied. These
numbers are therefore NOT physical jitter and no entropy claim may be built on
them (DR-0004 tiering).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from starved_cell_jitter_energy import (  # noqa: E402
    Record,
    RecordError,
    _lags,
    _loglog_slope,
    reference_spread,
    window_geometry,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"
TB = REPO_ROOT / "sim" / "tb"

#: The one corner this experiment is run at. Like #51's, it is a mechanism
#: question, not a PVT one, and it is the corner #51's variants were run at so
#: the two ladders are directly comparable.
CORNER = "tt/27/3.30"

#: ``(label, record glob, testbench manifest, what makes it different)``.
VARIANTS = [
    (
        "1 control",
        "*-ro-ring5-starved-jitter-long-*.md",
        TB / "ro-ring5-starved-jitter-long" / "tb.json",
        "one ring, nothing attached",
    ),
    (
        "2 clk-high",
        "*-ring-liveness-tap-phase-clk-high-*.md",
        TB / "ring-liveness-tap-phase-clk-high" / "tb.json",
        "+ tap, clk on the high rail",
    ),
    (
        "3 clk-low",
        "*-ring-liveness-tap-phase-clk-low-*.md",
        TB / "ring-liveness-tap-phase-clk-low" / "tb.json",
        "+ tap, clk on the low rail",
    ),
    (
        "4 clocked",
        "*-ring-liveness-tap-phase-clocked-*.md",
        TB / "ring-liveness-tap-phase-clocked" / "tb.json",
        "+ tap, clk running",
    ),
    (
        "5 buffered",
        "*-ring-liveness-tap-phase-buffered-0*.md",
        TB / "ring-liveness-tap-phase-buffered" / "tb.json",
        "clocked + the shipped ro_buf",
    ),
    (
        "6 buf-static",
        "*-ring-liveness-tap-phase-buffered-static-*.md",
        TB / "ring-liveness-tap-phase-buffered-static" / "tb.json",
        "buffered, clk on the high rail",
    ),
]

#: Classification thresholds on each variant's lag-1 sigma as a multiple of the
#: control's. Deliberately the same numbers ``array_coupling_variants.py`` uses,
#: so the two experiments are graded on one scale: at or below NULL_TOLERANCE a
#: variant counts as reproducing the control, at or above EXCESS_FACTOR as
#: carrying the artefact.
NULL_TOLERANCE = 3.0
EXCESS_FACTOR = 10.0

#: A variant's seed-to-seed spread of ``sigma_1``, as a fraction of the spread a
#: genuine estimate over the same window shows, at or below which the variant's
#: sigma is judged DETERMINISTIC rather than random. #51's coupled case came in
#: at 1.0 % against a ~15 % reference (0.07 of it); the control, its static
#: variant and its unconnected-rings variant came in at 3.9 / 2.3 / 6.0 %
#: against 2.7 % (1.4-2.2 of it). A third is far outside anything a genuine
#: estimate has shown in this repository and far above what the coupled case
#: showed, so the classification cannot flip on either.
DETERMINISTIC_SPREAD_FRACTION = 1.0 / 3.0

#: Ring-period modulation depth, as a fraction of the reference period, at or
#: above which a period difference counts as MATERIAL -- i.e. large enough that
#: a clock alternating between two such states is a frequency modulation rather
#: than a nudge, and small enough that the threshold is set by measurement
#: scatter rather than by the answer.
#:
#: It is derived from scatter, not from any result here. The committed
#: 5-stage-ring records reproduce their mean period seed to seed to ~0.03 %
#: (#51's variant-4 null agrees with its control's period to 4 parts in 10^6,
#: and the per-block means within one run scatter by ~0.03 %), so 0.3 % is
#: ~10x the noise on the quantity being compared, and ~2x the 0.16 % separation
#: #51 measured between two of its own differently-loaded variants -- a
#: difference that experiment treated as real but small.
MODULATION_MATERIAL = 0.003

#: The verdict the committed records actually support, recorded in
#: ``sim/characterization-liveness-tap-phase-cost.md``.
#:
#: ``--check`` gates on the *measured* verdict still equalling this one. That is
#: deliberately not the same thing as gating on a hypothesis being true: this
#: constant is written down AFTER the measurement, and if a future record moves
#: the classification the check fails and whoever moved it has to update the
#: recorded conclusion rather than quietly leaving a stale one in the
#: characterization document. Set it to ``None`` to run the classification
#: without gating on its outcome.
RECORDED_VERDICT: str | None = "clk-locked"

#: Same contract for the buffer question, which is a separate finding with its
#: own evidence: ``"removed"``, ``"reduced"``, ``"not-removed"``, or ``None`` to
#: skip the gate.
RECORDED_BUFFER_VERDICT: str | None = "removed"


class Variant:
    """One DUT variant's record at :data:`CORNER`, with both windows."""

    def __init__(self, label: str, record: Record, manifest: Path, difference: str) -> None:
        self.label = label
        self.key = label.split()[1]
        self.rec = record
        self.difference = difference
        self.discarded, self.n_periods = window_geometry(manifest)
        self.period = record.values["period"]

        self.lags = _lags(record)
        self.sigma = {L: record.values[f"sigma_{L}"] for L in self.lags}
        self.exponent = _loglog_slope(
            [float(L) for L in self.lags], [self.sigma[L] for L in self.lags]
        )
        tail = [L for L in self.lags if L >= max(self.lags) // 8]
        self.tail_lags = tail
        self.exponent_tail = _loglog_slope(
            [float(L) for L in tail], [self.sigma[L] for L in tail]
        )

        s_lags = _lags(record, "sigma_startup16_")
        self.startup_lags = s_lags
        self.startup_sigma = {L: record.values[f"sigma_startup16_{L}"] for L in s_lags}
        self.startup_period = record.values.get("period_startup16", float("nan"))

        self.blocks = [
            record.values[k]
            for k in sorted(k for k in record.values if re.fullmatch(r"period_b\d+", k))
        ]

    @property
    def spread_1(self) -> float | None:
        return self.rec.spread("sigma_1")

    @property
    def block_swing(self) -> float:
        """``(max - min)`` of the 16 per-block mean periods, as a fraction of
        this variant's own mean period.

        Each block is 48 consecutive periods (~150 ns), so a clk that toggles
        on a microsecond scale shows up here directly as blocks alternating
        between two levels, where a random walk shows only estimator scatter.
        This is the diagnostic that does not depend on the sigma estimator at
        all.
        """
        if not self.blocks:
            return float("nan")
        return (max(self.blocks) - min(self.blocks)) / self.period


def load_variants() -> list[Variant]:
    out: list[Variant] = []
    for label, glob, manifest, difference in VARIANTS:
        matches = []
        for path in sorted(RECORDS.glob(glob)):
            rec = Record(path)
            if rec.corner != CORNER or "sigma_1" not in rec.values:
                continue
            matches.append(rec)
        if not matches:
            raise RecordError(
                f"variant {label!r}: no sim/records/{glob} record at {CORNER} carries a "
                "sigma_1, so this variant cannot be compared"
            )
        # Latest record wins; earlier ones stay on file as append-only evidence.
        out.append(Variant(label, matches[-1], manifest, difference))
    return out


def classify(by_key: dict[str, Variant], ref_spread_1: float) -> tuple[str, str]:
    """``(verdict, rationale)`` for the clk-locked question, on the PRE-#82
    topology -- the digitizer's ``d`` input directly on the ring node.

    The comparison is inside one topology: variant 4 (clk running) against
    variant 2 (the same deck, clk parked on a rail). One thing differs between
    numerator and denominator, and it is the thing under test.

    Three signatures have to agree, and each is independently falsifiable:

    * **the static endpoints are materially apart** -- which rail ``clk`` sits
      on decides how fast the ring runs. If they were not, alternating between
      them could not be a modulation and any sigma excess would have to come
      from somewhere else.
    * **the clocked deck's lag-1 sigma is in the excess band** over its own
      static reference. A load effect cannot produce this, because the load is
      the same in both decks.
    * **that sigma is seed-independent**, i.e. its seed-to-seed spread has
      collapsed relative to what a genuine estimate over the same window
      shows. Noise scatters seed to seed; a deterministic component does not.

    Both thresholds are the ones ``array_coupling_variants.py`` already uses,
    so nothing here is tuned to this experiment's answer.
    """
    high = by_key["clk-high"]
    low = by_key["clk-low"]
    clocked = by_key["clocked"]

    endpoint_gap = abs(low.period - high.period) / high.period
    ratio = clocked.sigma[1] / high.sigma[1]
    spread = clocked.spread_1
    deterministic = spread is not None and spread <= DETERMINISTIC_SPREAD_FRACTION * ref_spread_1

    if endpoint_gap < MODULATION_MATERIAL and ratio <= NULL_TOLERANCE:
        return "quiet", (
            "  QUIET. The tap's two static endpoints (clk on either rail) sit within\n"
            f"  {100 * MODULATION_MATERIAL:.1f} % of each other on ring period, and running clk does not move\n"
            "  lag-1 sigma away from the static reference. On this evidence the pre-#82\n"
            "  digitizer tap costs its ring nothing measurable in phase at this corner."
        )
    if ratio >= EXCESS_FACTOR and deterministic:
        return "clk-locked", (
            "  CLK-LOCKED. Three things agree. (a) The tap's two static endpoints are\n"
            f"  {100 * endpoint_gap:.2f} % apart on ring period, so which rail clk sits on decides how\n"
            "  fast the ring runs. (b) With clk RUNNING and nothing else changed,\n"
            f"  lag-1 sigma is {ratio:.0f}x the static reference's -- the ring is being walked\n"
            "  between those two endpoints. (c) That sigma is seed-independent to\n"
            f"  {100 * spread:.2f} % where a genuine estimate over the same window scatters\n"
            f"  {100 * ref_spread_1:.2f} %, so what it measures is deterministic, not noise.\n"
            "  A deterministic component locked to clk is coherent with the sampling\n"
            "  instant by construction and does not average away over samples."
        )
    if ratio >= EXCESS_FACTOR:
        return "excess-not-attributed", (
            "  EXCESS, NOT ATTRIBUTED. The running-clk deck carries a large lag-1 sigma\n"
            "  excess over its own static reference, but its seed spread has not\n"
            "  collapsed the way a deterministic component requires. Something is\n"
            "  inflating sigma and this experiment does not say it is clk. That is a\n"
            "  stated open result: it narrows the search without closing it."
        )
    return "quiet", (
        "  QUIET. The running-clk deck's lag-1 sigma does not reach the excess band\n"
        "  over its own static reference. Whatever the tap's static endpoints do,\n"
        "  walking between them at this clk rate does not show up as a sigma excess."
    )


def classify_buffer(by_key: dict[str, Variant], ref_spread_1: float) -> tuple[str, str]:
    """``(verdict, rationale)`` for issue #76's last acceptance item, which
    PR #82 turned from a proposal into the shipped topology.

    Same pairing, one topology down: variant 5 (buffered, clk running) against
    variant 6 (buffered, clk parked). Comparing the buffered clocked deck
    against the UNbuffered static one would span two changes -- the buffer both
    isolates the ring node and lightens it -- which is the pairing argument
    ``sim/characterization-ring-buffer-mitigation.md`` makes for its own decks.
    """
    high = by_key["clk-high"]
    clocked = by_key["clocked"]
    buffered = by_key["buffered"]
    static = by_key["buf-static"]

    before = clocked.sigma[1] / high.sigma[1]
    after = buffered.sigma[1] / static.sigma[1]
    swing_before = clocked.block_swing
    swing_after = buffered.block_swing

    if after <= NULL_TOLERANCE and swing_after < MODULATION_MATERIAL:
        return "removed", (
            "  REMOVED. With the shipped ro_buf between the ring node and the\n"
            f"  digitizer, lag-1 sigma falls from {before:.0f}x its static reference to {after:.2f}x,\n"
            f"  and the per-block period swing from {100 * swing_before:.2f} % to {100 * swing_after:.3f} %. The buffer's\n"
            "  input capacitance does not change when clk moves, so the ring no longer\n"
            "  sees a clk-dependent load."
        )
    if after < before / 3.0 or swing_after < swing_before / 3.0:
        return "reduced", (
            f"  REDUCED, NOT REMOVED. The buffer takes lag-1 sigma from {before:.0f}x its static\n"
            f"  reference to {after:.1f}x and the per-block period swing from {100 * swing_before:.2f} % to\n"
            f"  {100 * swing_after:.2f} %, but the residual is still outside the band a quiet ring\n"
            "  occupies. A buffer helps on this path and is not by itself sufficient."
        )
    return "not-removed", (
        f"  NOT REMOVED. Lag-1 sigma is {after:.1f}x its own static reference with the\n"
        f"  buffer against {before:.0f}x without it, and the per-block period swing is\n"
        f"  {100 * swing_after:.2f} % against {100 * swing_before:.2f} %. The buffer PR #82 adopted does not remove\n"
        "  the clk-locked disturbance on the digitizer path on this evidence. What\n"
        "  survives it is charge fed back through the buffer's own input stage: the\n"
        "  clk-dependent load sits on the buffer's OUTPUT, and a change in that load\n"
        "  changes the buffer's output slew, which the gate-drain capacitance of the\n"
        "  buffer's own devices carries back to its input -- the ring node."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="liveness_tap_phase_variants.py",
        description="Compare issue #76's DUT variants and say whether the DR-0016 "
        "liveness digitizer puts a clk-locked component on its ring's phase.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the variant separation that supports the recorded "
        "conclusion no longer holds over the committed records",
    )
    args = parser.parse_args(argv)

    try:
        variants = load_variants()
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    control = variants[0]
    by_key = {v.key: v for v in variants}

    print(
        f"issue #76 -- DUT variants at {CORNER} (process/degC/V), same starved delay\n"
        f"cell, same fixed injected noise density, same window geometry. sigma is RAW\n"
        f"at the injected level: comparable across these rows and to #51's ladder in\n"
        f"sim/characterization-array-ring-coupling.md, but not physical jitter.\n"
    )

    lags = control.lags
    header = (
        f"{'variant':<12} {'differs by':<31} {'T0 (s)':>11} "
        + "".join(f"{'L=' + str(L):>11}" for L in lags)
        + f"{'expon':>7}{'tail':>7}{'spr_1':>8}"
    )
    print(f"{control.n_periods}-period window, opened {control.discarded} periods after start-up")
    print(header)
    print("-" * len(header))
    for v in variants:
        spread = v.spread_1
        print(
            f"{v.label:<12} {v.difference:<31} {v.period:11.4e} "
            + "".join(f"{v.sigma[L]:11.4e}" for L in lags)
            + f"{v.exponent:7.3f}{v.exponent_tail:7.3f}"
            + (f"{100 * spread:7.2f}%" if spread is not None else f"{'n/a':>8}")
        )
    ref_1, ref_n, ref_periods = reference_spread(1, control.n_periods)
    print(
        f"\n  seed-spread reference at lag 1 for a {control.n_periods}-period window: "
        f"{100 * ref_1:.2f}%\n"
        f"  (mean over {ref_n} plain-cell records at a {ref_periods}-period window, "
        f"rescaled by sqrt({ref_periods}/{control.n_periods}); see\n"
        f"  sim/tools/starved_cell_jitter_energy.py for the calibration.)"
    )

    print("\nring period, and how much it moves across the run")
    print(
        f"  {'variant':<12} {'T0 (s)':>11} {'vs control':>11} "
        f"{'min block':>11} {'max block':>11} {'swing':>9}"
    )
    for v in variants:
        lo = min(v.blocks) if v.blocks else float("nan")
        hi = max(v.blocks) if v.blocks else float("nan")
        print(
            f"  {v.label:<12} {v.period:11.4e} {v.period / control.period:10.3f}x "
            f"{lo:11.4e} {hi:11.4e} {100 * v.block_swing:8.2f}%"
        )
    print(
        "  (each block is 48 consecutive periods, ~150 ns; the swing is\n"
        "  (max-min)/T0 over the 16 blocks of the same run.)"
    )

    print("\nratio to the control at lag 1")
    for v in variants[1:]:
        long_ratio = v.sigma[1] / control.sigma[1]
        short_ratio = (
            v.startup_sigma[1] / control.startup_sigma[1]
            if control.startup_sigma and v.startup_sigma
            else float("nan")
        )
        print(
            f"  {v.label:<12} {long_ratio:10.2f}x  (512-period window)"
            f"   {short_ratio:8.2f}x  (16-period start-up window)"
        )

    print(
        "\n  the within-topology ratio, which is the one this experiment turns on:\n"
        "  numerator and denominator differ by exactly one thing, whether clk toggles."
    )
    for topo, num, den in (
        ("pre-#82  (tap on the ring node)", "clocked", "clk-high"),
        ("post-#82 (tap on the ro_buf output)", "buffered", "buf-static"),
    ):
        n, d = by_key[num], by_key[den]
        print(
            f"    {topo:<38} {n.sigma[1] / d.sigma[1]:8.2f}x"
            f"   ({num} / {den})"
        )

    high, low = by_key["clk-high"], by_key["clk-low"]
    print(
        f"\nthe tap's two static endpoints, which a running clk alternates between:\n"
        f"  clk on the HIGH rail (master transmission gate OFF): T0 = {high.period:.4e} s\n"
        f"  clk on the LOW  rail (master transmission gate ON ): T0 = {low.period:.4e} s\n"
        f"  gap = {100 * abs(low.period - high.period) / high.period:.2f}% of the clk-high period"
        f"   ({100 * MODULATION_MATERIAL:.1f}% counts as material)\n"
        f"  A 50% duty-cycle clock puts the ring in each state half the time whatever\n"
        f"  its frequency, so this gap is the RATE-INDEPENDENT part of the result.\n"
    )

    verdict, rationale = classify(by_key, ref_1)
    print(f"\nverdict: {verdict.upper()}")
    print(rationale)

    buffer_verdict, buffer_rationale = classify_buffer(by_key, ref_1)
    print(f"\nbuffer (issue #76's last acceptance item): {buffer_verdict.upper()}")
    print(buffer_rationale)

    if args.check:
        failed = False
        for got, recorded, what in (
            (verdict, RECORDED_VERDICT, "the clk-locked question"),
            (buffer_verdict, RECORDED_BUFFER_VERDICT, "the buffer question"),
        ):
            if recorded is None:
                print(
                    f"\nERROR: the recorded verdict for {what} is unset, so --check has "
                    "nothing to gate against.",
                    file=sys.stderr,
                )
                return 2
            if got != recorded:
                print(
                    f"\nFAIL: the committed records now classify {what} as {got!r}, but the "
                    f"conclusion recorded in "
                    f"sim/characterization-liveness-tap-phase-cost.md is {recorded!r}. "
                    "Either a record changed or a variant was re-run; update the recorded "
                    "conclusion to match the evidence (and this constant with it) rather "
                    "than leaving a stale one.",
                    file=sys.stderr,
                )
                failed = True
        if failed:
            return 1
        print(
            f"\nOK: the committed records still classify as {verdict!r} / "
            f"{buffer_verdict!r}, the conclusions "
            "sim/characterization-liveness-tap-phase-cost.md records."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
