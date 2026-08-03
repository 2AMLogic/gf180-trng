#!/usr/bin/env python3
"""What does the DR-0016 per-ring liveness digitizer cost the ring in PHASE?
(issue #76)

    python3 sim/tools/ring_liveness_tap_phase.py           # the tables
    python3 sim/tools/ring_liveness_tap_phase.py --check   # gate the finding

Like ``sim/tools/array_coupling_variants.py`` and
``sim/tools/array_coupling_buffer_variant.py`` this is a *derivation*, not a
simulation: it reads only records already committed under ``sim/records/`` and
does arithmetic on them. It needs neither ngspice nor the PDK, and it writes
nothing.

The question (issue #76)
------------------------
``sim/characterization-array-ring-coupling.md`` (issue #51 / PR #67) indicts a
specific arrangement: a ring node driving the input of a cell whose internal
nodes something else is driving. It measured 28.6x on ``sigma_1`` against
1.06x for the same gate load with the neighbour on a rail, so the load was
innocent and the neighbour's *switching* was the mechanism.

DR-0016's per-ring liveness digitizers put a ring's observation node on a
``sampler_dff`` ``d`` input -- one terminal of a transmission gate whose gates
are driven by ``clk``. ``sim/tb/ring-liveness-tap-power/`` measured what that
costs the rings in POWER. This family measures what it costs them in PHASE,
and whether driving the digitizer from a DR-0018 ``ro_buf`` output instead of
from the ring node removes it.

Why the static pair is the load-bearing part
--------------------------------------------
A ``clk``-driven pass gate does not inject a rare impulse into the ring: it
*modulates the ring's load* between two values at the clock rate. That makes
the mechanism predictable from two runs in which nothing switches at all --
the ring's period with the pass gate shut, and with it open. If the clocked
run's ``sigma_1`` is what a two-level period modulation between those two
periods predicts, then the disturbance is that modulation, is deterministic,
and is phase-locked to ``clk`` by construction. The prediction is

    p             = (T_open - T_bar) / (T_open - T_shut)     duty, from T_bar
    sigma_1_pred  = |T_open - T_shut| * sqrt(p * (1 - p))

with every term on the right measured in a *different* deck from the
``sigma_1`` on the left. Nothing in it is fitted.

Sigma here is RAW at the fixed injected level, exactly as in
``array_coupling_variants.py`` -- comparable across these rows, not physical
jitter, and no entropy claim may be built on it (DR-0004 tiering).
"""

from __future__ import annotations

import argparse
import math
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

#: The one corner this experiment (and issue #51's) is run at.
CORNER = "tt/27/3.30"

#: ``(label, record glob)`` in the order the comparisons are meant to be read.
#: Row 0 is issue #51's own committed control -- the same delay cell at the
#: same injected density with NOTHING attached, i.e. issue #76's
#: "digitizers absent" row. It is cited, not re-run.
VARIANTS = [
    ("0 control", "*-ro-ring5-starved-jitter-long-[0-9]*.md"),
    ("1 tap-shut", "*-ring-liveness-tap-phase-shut-*.md"),
    ("2 tap-open", "*-ring-liveness-tap-phase-open-*.md"),
    ("3 tap-clocked", "*-ring-liveness-tap-phase-clocked-*.md"),
    ("4 buf-shut", "*-ring-liveness-tap-phase-buffered-shut-*.md"),
    ("5 buf-open", "*-ring-liveness-tap-phase-buffered-open-*.md"),
    ("6 buf-clocked", "*-ring-liveness-tap-phase-buffered-clocked-*.md"),
]

#: The manifest whose window geometry every deck in this family shares, and
#: which the seed-spread reference is rescaled to.
FAMILY_TB_MANIFEST = TB / "ring-liveness-tap-phase-clocked" / "tb.json"


class Variant:
    def __init__(self, label: str, record: Record) -> None:
        self.label = label
        self.rec = record
        self.period = record.values["period"]
        self.lags = _lags(record)
        self.sigma = {L: record.values[f"sigma_{L}"] for L in self.lags}
        self.exponent = _loglog_slope(
            [float(L) for L in self.lags], [self.sigma[L] for L in self.lags]
        )
        self.bins = [
            record.values[f"period_b{i:02d}"]
            for i in range(16)
            if f"period_b{i:02d}" in record.values
        ]

    @property
    def spread_1(self) -> float | None:
        return self.rec.spread("sigma_1")


def load_variants() -> list[Variant]:
    out: list[Variant] = []
    for label, glob in VARIANTS:
        matches = [
            rec
            for rec in (Record(p) for p in sorted(RECORDS.glob(glob)))
            if rec.corner == CORNER and "sigma_1" in rec.values
        ]
        if not matches:
            raise RecordError(
                f"variant {label!r}: no sim/records/{glob} record at {CORNER} carries a "
                "sigma_1, so this variant cannot be compared"
            )
        # Latest record wins; earlier ones stay on file as append-only
        # evidence. A failed run's record carries no sigma_1 and so never
        # reaches this filter.
        out.append(Variant(label, matches[-1]))
    return out


def predict(shut: Variant, opened: Variant, clocked: Variant) -> dict[str, float]:
    """The two-level-modulation prediction for ``clocked`` from the static pair.

    Every input is measured in a deck other than the one being predicted.
    """
    delta = abs(opened.period - shut.period)
    span = opened.period - shut.period
    duty = (opened.period - clocked.period) / span if span else float("nan")
    return {
        "delta": delta,
        "duty_shut": duty,
        "sigma_1_pred": delta * math.sqrt(max(duty * (1.0 - duty), 0.0)),
        "sigma_1_meas": clocked.sigma[1],
    }


def _fmt_pred(name: str, p: dict[str, float]) -> None:
    ratio = p["sigma_1_meas"] / p["sigma_1_pred"] if p["sigma_1_pred"] else float("nan")
    print(f"  {name}")
    print(
        f"    period at the two static points differ by {p['delta'] * 1e12:8.2f} ps"
        f"   (duty at the shut point {p['duty_shut']:.3f}, from the clocked run's own T_bar)"
    )
    print(
        f"    sigma_1 PREDICTED from those two decks : {p['sigma_1_pred']:.4e} s\n"
        f"    sigma_1 MEASURED  in the clocked deck  : {p['sigma_1_meas']:.4e} s"
        f"   ({ratio:.3f}x predicted)"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ring_liveness_tap_phase.py",
        description="What does the DR-0016 per-ring liveness digitizer cost the "
        "ring in phase, and does a DR-0018 per-ring buffer remove it? (issue #76)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero unless (a) the clocked unbuffered variant's sigma_1 "
        "exceeds BOTH of its own static controls' and (b) the buffered "
        "arrangement's clk-switching ratio is below the unbuffered one -- a "
        "minimal gate that the disturbance is real and that the buffer moved "
        "it in the isolating direction, not a claim about how much",
    )
    args = parser.parse_args(argv)

    try:
        variants = load_variants()
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    by = {v.label.split()[-1]: v for v in variants}
    control = by["control"]
    shut, opened, clocked = by["tap-shut"], by["tap-open"], by["tap-clocked"]
    bshut, bopen, bclocked = by["buf-shut"], by["buf-open"], by["buf-clocked"]

    print(
        f"issue #76 -- what does the DR-0016 liveness digitizer cost the ring in\n"
        f"PHASE, at {CORNER} (process/degC/V)? sigma is RAW at the injected level:\n"
        f"comparable across these rows, not physical jitter.\n"
    )

    lags = clocked.lags
    header = (
        f"{'variant':<16} {'T0 (s)':>11} "
        + "".join(f"{'L=' + str(L):>11}" for L in lags)
        + f"{'expon':>7}{'spr_1':>8}"
    )
    print(header)
    print("-" * len(header))
    for v in variants:
        spread = v.spread_1
        print(
            f"{v.label:<16} {v.period:11.4e} "
            + "".join(f"{v.sigma[L]:11.4e}" for L in lags if L in v.sigma)
            + f"{v.exponent:7.3f}"
            + (f"{100 * spread:7.1f}%" if spread is not None else f"{'n/a':>8}")
        )

    # ---- the headline ratios ------------------------------------------
    print("\nsigma_1 against the DIGITIZERS-ABSENT control (issue #76's first bullet)")
    for v in (shut, opened, clocked, bshut, bopen, bclocked):
        print(f"  {v.label:<16} {v.sigma[1] / control.sigma[1]:10.2f}x")

    print("\nTHE ONE-CHANGE RATIO -- clk switching / clk quiet, same tap point")
    print("  (numerator and denominator differ in exactly one thing: does clk switch)")
    for tag, run, quiet_a, quiet_b in (
        ("digitizer on the RAW ring node", clocked, shut, opened),
        ("digitizer on the BUFFERED node", bclocked, bshut, bopen),
    ):
        ra = run.sigma[1] / quiet_a.sigma[1]
        rb = run.sigma[1] / quiet_b.sigma[1]
        print(
            f"  {tag:<32} {ra:9.2f}x (vs {quiet_a.label.split()[-1]})"
            f"   {rb:9.2f}x (vs {quiet_b.label.split()[-1]})"
        )

    worst_unbuf = max(clocked.sigma[1] / shut.sigma[1], clocked.sigma[1] / opened.sigma[1])
    worst_buf = max(bclocked.sigma[1] / bshut.sigma[1], bclocked.sigma[1] / bopen.sigma[1])
    if worst_unbuf > 1.0:
        removed = 1.0 - (worst_buf - 1.0) / (worst_unbuf - 1.0)
        print(
            f"\n  -> the buffer removes {removed * 100:.2f}% of the clk-switching excess,"
            f" leaving {worst_buf:.2f}x"
        )
        print(
            f"  -> squared (what DR-0007 §2 substitutes): {worst_unbuf ** 2:.0f}x"
            f" over-statement becomes {worst_buf ** 2:.1f}x"
        )

    # ---- is it phase-locked to clk? -----------------------------------
    print("\nIS IT PHASE-LOCKED TO clk? the two-level-modulation prediction")
    print("  every term on the right of the prediction is measured in a deck other")
    print("  than the one it predicts; nothing here is fitted.")
    _fmt_pred("digitizer on the RAW ring node", predict(shut, opened, clocked))
    _fmt_pred("digitizer on the BUFFERED node", predict(bshut, bopen, bclocked))

    _, n_periods = window_geometry(FAMILY_TB_MANIFEST)
    ref, n_ref, ref_np = reference_spread(1, n_periods)
    print(
        f"\n  seed-to-seed spread of sigma_1 -- a GENUINE {n_periods}-period estimate"
        f" scatters ~{100 * ref:.1f}%"
    )
    print(f"  (calibrated on {n_ref} plain-cell records over {ref_np} periods)")
    for v in variants:
        s = v.spread_1
        if s is None:
            continue
        verdict = "deterministic" if s < ref / 3 else "consistent with jitter"
        print(f"    {v.label:<16} {100 * s:6.2f}%   {verdict}")

    print("\n  accumulation exponent over lags "
          f"{lags[0]}..{lags[-1]} -- 0.5 is a phase random walk,")
    print("  1.0 is a deterministic drift")
    for v in variants:
        print(f"    {v.label:<16} {v.exponent:6.3f}")

    # ---- the modulation, read straight off the bin series --------------
    print("\n  period per 48-period bin (the clk-locked modulation as a shape, ps)")
    for v in (shut, opened, clocked, bshut, bopen, bclocked):
        if not v.bins:
            continue
        print(f"    {v.label:<16} " + " ".join(f"{b * 1e12:7.1f}" for b in v.bins[:8]))
        print(f"    {'':<16} " + " ".join(f"{b * 1e12:7.1f}" for b in v.bins[8:]))

    if args.check:
        problems = []
        if not (clocked.sigma[1] > shut.sigma[1] and clocked.sigma[1] > opened.sigma[1]):
            problems.append(
                "the clocked unbuffered variant's sigma_1 does not exceed both of its "
                "own static controls' -- the disturbance this family exists to measure "
                "is not present in the committed records"
            )
        if worst_buf >= worst_unbuf:
            problems.append(
                "the buffered arrangement's clk-switching ratio is not below the "
                "unbuffered one -- the mitigation did not move sigma_1 in the "
                "isolating direction"
            )
        if problems:
            for p in problems:
                print(f"\nCHECK FAILED: {p}", file=sys.stderr)
            return 1
        print("\nCHECK OK: the clk-locked disturbance is present unbuffered, and the")
        print("buffer reduces it. (This gate says the signs are right; the size of")
        print("the residual is the finding, and it is above, not here.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
