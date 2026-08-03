#!/usr/bin/env python3
"""Compare the SHIPPED-array variants of issue #87's liveness-tap phase experiment.

    python3 sim/tools/array_liveness_tap_phase_variants.py           # the tables
    python3 sim/tools/array_liveness_tap_phase_variants.py --check   # gate the finding

Like ``sim/tools/liveness_tap_phase_variants.py`` (issue #76), which this is the
direct successor to, it is a *derivation*, not a simulation: it reads only
records already committed under ``sim/records/`` and does arithmetic on them. It
needs neither ngspice nor the PDK, and it writes nothing.

The question (issue #87)
-----------------------
``sim/characterization-liveness-tap-phase-cost.md`` (issue #76, PR #85) measured
the DR-0016 liveness digitizer's ``clk``-locked phase disturbance on an ISOLATED
ring: 541x on a raw ring node, 19.9x behind a DR-0018 ``ro_buf``. It recorded
that 19.9x as an **upper bound** rather than as the shipped number, and said why:
its buffered deck's ``ro_buf`` output drives ONE consumer, where
``design/ro_array_core.spice`` has each buffer output driving the XOR combiner's
input as well --

    xb1 rn1 ro1 vdd vss ro_buf
    xa1 ro1 ro2 xo  vdd vss xor2        <- the second consumer
    xsr1 ro1 clk rst_n ring_bit1 ...    <- the digitizer

-- so the ``clk``-modulated share of that node's capacitance is smaller in the
shipped array than in #76's deck, and the residual should be smaller with it.
That argument is structural and was never measured. This script reads the
records that measure it.

#76 also left a second path wholly unmeasured: ``sampler_core``'s raw-tap
digitizer ``xsb`` puts the same ``clk``-driven pass gate on the combiner output
``xo``. ``xo`` is two active stages away from either ring node (``xa1``, then
that ring's own ``ro_buf``), so the same feed-back argument predicts a much
smaller effect -- again, predicts.

The variants this script tabulates
----------------------------------
One corner (``tt``/27 C/3.30 V), one window geometry, two pairs, and inside each
pair exactly one difference -- whether ``clk`` toggles:

1. ``array-liveness-tap-phase-clocked``      the SHIPPED sampler_core: both
                                             rings, both buffers, the combiner,
                                             all four sampler_dff; clk running
2. ``array-liveness-tap-phase-static``       variant 1, clk parked HIGH
3. ``array-liveness-tap-phase-xsb-clocked``  variant 1 with the two per-ring
                                             liveness digitizers REMOVED, so the
                                             only clk-driven pass gate downstream
                                             of a ring is xsb's on xo; clk running
4. ``array-liveness-tap-phase-xsb-static``   variant 3, clk parked HIGH

    shipped   sigma_1(1) / sigma_1(2)      <- the number #76's 19.9x bounded
    xsb-only  sigma_1(3) / sigma_1(4)      <- the path #76 never measured

Both ratios are taken inside one topology, so the neighbouring ring, the
combiner, the buffers and the digitizers' static load are all present
identically in numerator and denominator and cancel. That is #51's
variant-3-against-variant-2 discipline, which #76 applied twice and this applies
twice more.

Why the two families' sigma values are not interchangeable
----------------------------------------------------------
``sigma_N`` is a period-count statistic, and this family's rings are 11-stage
where #76's was 5-stage. Matching #76's 256/512 ring-period geometry would have
meant ~5.5 us of transient noise on a circuit that costs ~21 CPU-minutes per
simulated microsecond, so this family matches #76 in TIME instead: it opens its
window 128 ring periods after start-up and spans 256, which on a ~6.7 ns ring is
0.86 us of settling and a 1.71 us window against #76's 0.73 us and 1.46 us. Both
are longer in absolute time and cover more ``clk`` periods than #76's did, which
is what a ``clk``-locked disturbance depends on.

Consequently **only the within-family clocked/static RATIOS are compared across
the two experiments**, never the raw sigmas. Each ratio's numerator and
denominator share a window, so the geometry cancels out of it exactly.

Why the sigmas here are RAW
---------------------------
Every record here is at the same corner with the same fixed injected noise
density, so the corner scaling ``starved_cell_jitter_energy.py`` applies is a
common factor and is deliberately not applied. These numbers are therefore NOT
physical jitter and no entropy claim may be built on them (DR-0004 tiering).
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

#: The one corner this experiment is run at -- #76's and #51's, so the ratios
#: are directly comparable. This is a mechanism question, not a PVT one.
CORNER = "tt/27/3.30"

#: ``(label, record glob, testbench manifest, what makes it different)``.
VARIANTS = [
    (
        "1 shipped",
        "????-??-??-array-liveness-tap-phase-clocked-*.md",
        TB / "array-liveness-tap-phase-clocked" / "tb.json",
        "shipped sampler_core, clk running",
    ),
    (
        "2 shipped-static",
        "????-??-??-array-liveness-tap-phase-static-*.md",
        TB / "array-liveness-tap-phase-static" / "tb.json",
        "the same, clk parked HIGH",
    ),
    (
        "3 xsb",
        "????-??-??-array-liveness-tap-phase-xsb-clocked-*.md",
        TB / "array-liveness-tap-phase-xsb-clocked" / "tb.json",
        "no xsr1/xsr2, clk running",
    ),
    (
        "4 xsb-static",
        "????-??-??-array-liveness-tap-phase-xsb-static-*.md",
        TB / "array-liveness-tap-phase-xsb-static" / "tb.json",
        "the same, clk parked HIGH",
    ),
]

#: Issue #76's buffered pair, read here only so the "against the 19.9x upper
#: bound" comparison is computed from the same committed evidence rather than
#: transcribed as a constant that can go stale.
BOUND_VARIANTS = [
    (
        "76 buffered",
        "????-??-??-ring-liveness-tap-phase-buffered-0*.md",
        TB / "ring-liveness-tap-phase-buffered" / "tb.json",
        "#76: one 5-stage ring, buffer -> one digitizer, clk running",
    ),
    (
        "76 buf-static",
        "????-??-??-ring-liveness-tap-phase-buffered-static-*.md",
        TB / "ring-liveness-tap-phase-buffered-static" / "tb.json",
        "#76: the same, clk parked HIGH",
    ),
]

#: Classification thresholds on a variant's lag-1 sigma as a multiple of its own
#: static reference's. Deliberately the same numbers ``array_coupling_variants.py``
#: and ``liveness_tap_phase_variants.py`` already use, so nothing here is tuned to
#: this experiment's answer: at or below NULL_TOLERANCE a variant counts as
#: reproducing its reference, at or above EXCESS_FACTOR as carrying the artefact.
NULL_TOLERANCE = 3.0
EXCESS_FACTOR = 10.0

#: A variant's seed-to-seed spread of ``sigma_1``, as a fraction of the spread a
#: genuine estimate over the same window shows, at or below which that sigma is
#: judged DETERMINISTIC rather than random. Same constant, same rationale, as
#: ``liveness_tap_phase_variants.py``.
DETERMINISTIC_SPREAD_FRACTION = 1.0 / 3.0

#: Ring-period modulation depth, as a fraction of the reference period, at or
#: above which a per-block period swing counts as MATERIAL. Same constant and
#: same derivation-from-scatter as ``liveness_tap_phase_variants.py``.
MODULATION_MATERIAL = 0.003

#: How much smaller than #76's bound the shipped ratio has to come in before
#: this script will call the bound CONFIRMED rather than merely not-violated.
#: 10 % is well outside the seed-to-seed scatter of a sigma_1 ratio (each side
#: of which scatters a few per cent at worst) and well inside the separation
#: any of the mechanisms discussed would produce, so the classification cannot
#: flip on estimator noise.
BOUND_MARGIN = 0.10

#: The verdicts the committed records actually support, recorded in
#: ``sim/characterization-liveness-tap-phase-cost.md``.
#:
#: ``--check`` gates on the *measured* verdict still equalling these. That is
#: deliberately not the same as gating on a hypothesis being true: these are
#: written down AFTER the measurement, and if a future record moves the
#: classification the check fails and whoever moved it has to update the recorded
#: conclusion rather than quietly leaving a stale one in the characterization
#: document. Set either to ``None`` to run the classification without gating.
RECORDED_SHIPPED_VERDICT: str | None = "bound-confirmed-residual-remains"
RECORDED_XSB_VERDICT: str | None = "unreachable"


class Variant:
    """One DUT variant's record at :data:`CORNER`, with its window geometry."""

    def __init__(self, label: str, record: Record, manifest: Path, difference: str) -> None:
        self.label = label
        self.key = label.split(maxsplit=1)[1]
        self.rec = record
        self.difference = difference
        self.discarded, self.n_periods = window_geometry(manifest)
        self.period = record.values["period"]

        self.lags = _lags(record)
        self.sigma = {L: record.values[f"sigma_{L}"] for L in self.lags}
        self.exponent = _loglog_slope(
            [float(L) for L in self.lags], [self.sigma[L] for L in self.lags]
        )

        r2_lags = _lags(record, "sigma_r2_")
        self.r2_lags = r2_lags
        self.sigma_r2 = {L: record.values[f"sigma_r2_{L}"] for L in r2_lags}
        self.period_r2 = record.values.get("period_r2", float("nan"))

        self.blocks = [
            record.values[k]
            for k in sorted(k for k in record.values if re.fullmatch(r"period_b\d+", k))
        ]

    @property
    def spread_1(self) -> float | None:
        return self.rec.spread("sigma_1")

    @property
    def block_swing(self) -> float:
        """``(max - min)`` of the per-block mean periods, as a fraction of this
        variant's own mean period.

        This is the diagnostic that does not use the sigma estimator at all: a
        clk that toggles on a microsecond scale shows up here as blocks
        alternating between two levels, where a random walk shows only
        estimator scatter.
        """
        if not self.blocks:
            return float("nan")
        return (max(self.blocks) - min(self.blocks)) / self.period


def _load(spec) -> Variant:
    label, glob, manifest, difference = spec
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
    return Variant(label, matches[-1], manifest, difference)


def load_variants() -> tuple[list[Variant], list[Variant]]:
    return [_load(s) for s in VARIANTS], [_load(s) for s in BOUND_VARIANTS]


def classify_shipped(by_key: dict[str, Variant], bound: float, ref_spread_1: float):
    """``(verdict, rationale)`` for issue #87's first question: how large is the
    ``clk``-locked residual on the SHIPPED array, and is it below the 19.9x upper
    bound #76 recorded for it?

    Numerator and denominator differ in exactly one thing -- whether ``clk``
    toggles -- so the fan-out, the neighbouring ring and every static load are
    identical on both sides and cancel.
    """
    shipped = by_key["shipped"]
    static = by_key["shipped-static"]
    ratio = shipped.sigma[1] / static.sigma[1]
    spread = shipped.spread_1
    deterministic = spread is not None and spread <= DETERMINISTIC_SPREAD_FRACTION * ref_spread_1
    swing = shipped.block_swing

    if ratio >= bound:
        return "bound-violated", (
            f"  BOUND VIOLATED. The shipped array's lag-1 sigma is {ratio:.2f}x its own static\n"
            f"  reference, at or above the {bound:.1f}x issue #76 recorded as an UPPER BOUND on\n"
            "  it. #76's structural argument -- that a buffer output driving xa1 as well as\n"
            "  its digitizer must carry a smaller clk-modulated share of its load -- does not\n"
            "  hold on this evidence, and the bound in\n"
            "  sim/characterization-liveness-tap-phase-cost.md must be withdrawn rather than\n"
            "  reworded."
        )
    if ratio > bound * (1.0 - BOUND_MARGIN):
        return "bound-not-separated", (
            f"  BOUND NOT SEPARATED. The shipped array's lag-1 sigma is {ratio:.2f}x its own\n"
            f"  static reference against #76's {bound:.1f}x bound -- below it, but by less than\n"
            f"  the {100 * BOUND_MARGIN:.0f} % margin this script requires before calling the direction\n"
            "  measured rather than coincidental. The bound is not violated and is not\n"
            "  confirmed."
        )
    if ratio <= NULL_TOLERANCE:
        return "bound-confirmed-quiet", (
            f"  BOUND CONFIRMED, AND THE RESIDUAL IS IN THE QUIET BAND. The shipped array's\n"
            f"  lag-1 sigma is {ratio:.2f}x its own static reference, against the {bound:.1f}x #76\n"
            "  recorded as an upper bound on it -- so #76's structural argument holds, and\n"
            f"  the residual is at or below the {NULL_TOLERANCE:.0f}x this repository's variant ladders treat\n"
            "  as reproducing a reference. On this evidence the shipped fan-out reduces the\n"
            "  clk-locked disturbance to something the estimator cannot separate from a\n"
            "  quiet ring."
        )
    return "bound-confirmed-residual-remains", (
        f"  BOUND CONFIRMED, RESIDUAL REMAINS. The shipped array's lag-1 sigma is {ratio:.2f}x\n"
        f"  its own static reference, against the {bound:.1f}x #76 recorded as an upper bound on\n"
        f"  it -- {100 * (1 - ratio / bound):.0f} % below the bound, so #76's structural argument (the shipped\n"
        "  buffer output drives xa1 as well as its digitizer, so the clk-modulated share of\n"
        "  its load is smaller) is measured rather than merely argued. It is NOT removed:\n"
        f"  {ratio:.2f}x is still outside the {NULL_TOLERANCE:.0f}x band a variant reproducing its reference\n"
        f"  occupies, the per-block period swing is {100 * swing:.3f} % against a {100 * MODULATION_MATERIAL:.1f} % materiality\n"
        "  threshold, and the seed spread is "
        + (f"{100 * spread:.2f} %" if spread is not None else "n/a")
        + f" against a {100 * ref_spread_1:.2f} % reference\n"
        f"  ({'deterministic' if deterministic else 'not collapsed'})."
    )


def classify_xsb(by_key: dict[str, Variant], ref_spread_1: float):
    """``(verdict, rationale)`` for issue #87's second question: does the
    raw-tap digitizer's own ``clk``-driven pass gate, on the combiner output
    ``xo``, reach either ring node at all?

    Same pairing: the xsb-only topology against itself with ``clk`` parked.
    """
    xsb = by_key["xsb"]
    static = by_key["xsb-static"]
    ratio = xsb.sigma[1] / static.sigma[1]
    ratio_r2 = (
        xsb.sigma_r2[1] / static.sigma_r2[1]
        if xsb.sigma_r2 and static.sigma_r2
        else float("nan")
    )
    swing = xsb.block_swing

    if ratio <= NULL_TOLERANCE and swing < MODULATION_MATERIAL:
        return "unreachable", (
            f"  UNREACHABLE AT THIS CORNER. With the two per-ring liveness digitizers removed,\n"
            "  the only clk-driven pass gate left downstream of a ring is xsb's, on the\n"
            f"  combiner output xo. Running clk moves ring 1's lag-1 sigma to {ratio:.2f}x its own\n"
            f"  static reference (ring 2: {ratio_r2:.2f}x) and leaves the per-block period swing at\n"
            f"  {100 * swing:.3f} %, below the {100 * MODULATION_MATERIAL:.1f} % materiality threshold. xo is two active stages\n"
            "  away from either ring node -- xa1, then that ring's own ro_buf -- and on this\n"
            "  evidence nothing measurable survives them."
        )
    if ratio >= EXCESS_FACTOR:
        return "reaches", (
            f"  REACHES THE RING. Running clk puts ring 1's lag-1 sigma at {ratio:.2f}x its own\n"
            f"  static reference (ring 2: {ratio_r2:.2f}x) with NO per-ring liveness digitizer\n"
            "  attached, so the xsb-on-xo path carries a clk-locked disturbance back through\n"
            "  xa1 and the per-ring buffer to the ring node on its own. That is a second\n"
            "  aggressor #76 never measured, and it is not attributable to DR-0016."
        )
    return "marginal", (
        f"  MARGINAL. Running clk moves ring 1's lag-1 sigma to {ratio:.2f}x its own static\n"
        f"  reference (ring 2: {ratio_r2:.2f}x) with no per-ring digitizer attached: above the\n"
        f"  {NULL_TOLERANCE:.0f}x band a variant reproducing its reference occupies, but below the\n"
        f"  {EXCESS_FACTOR:.0f}x this repository's ladders treat as carrying the artefact. Stated as an\n"
        "  open result rather than resolved in either direction."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="array_liveness_tap_phase_variants.py",
        description="Compare issue #87's shipped-array DUT variants: how large is the "
        "DR-0016 liveness digitizer's clk-locked phase disturbance where the buffer "
        "output also drives xa1, and does the xsb-on-xo path reach a ring at all?",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the variant separation that supports the recorded "
        "conclusion no longer holds over the committed records",
    )
    args = parser.parse_args(argv)

    try:
        variants, bound_variants = load_variants()
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    by_key = {v.key: v for v in variants}
    bound_by_key = {v.key: v for v in bound_variants}
    shipped = by_key["shipped"]

    print(
        f"issue #87 -- SHIPPED-ARRAY DUT variants at {CORNER} (process/degC/V). Every\n"
        f"deck carries the full design/sampler_core.spice topology; the four differ in\n"
        f"whether clk toggles and whether xsr1/xsr2 are present. sigma is RAW at the\n"
        f"fixed injected level and is NOT physical jitter.\n"
    )

    lags = shipped.lags
    header = (
        f"{'variant':<16} {'differs by':<34} {'T0 (s)':>11} "
        + "".join(f"{'L=' + str(L):>11}" for L in lags)
        + f"{'expon':>7}{'spr_1':>8}"
    )
    print(
        f"{shipped.n_periods}-period window, opened {shipped.discarded} periods after "
        f"start-up ({1e6 * shipped.n_periods * shipped.period:.2f} us long)"
    )
    print(header)
    print("-" * len(header))
    for v in variants:
        spread = v.spread_1
        print(
            f"{v.label:<16} {v.difference:<34} {v.period:11.4e} "
            + "".join(f"{v.sigma[L]:11.4e}" for L in lags)
            + f"{v.exponent:7.3f}"
            + (f"{100 * spread:7.2f}%" if spread is not None else f"{'n/a':>8}")
        )
    ref_1, ref_n, ref_periods = reference_spread(1, shipped.n_periods)
    print(
        f"\n  seed-spread reference at lag 1 for a {shipped.n_periods}-period window: "
        f"{100 * ref_1:.2f}%\n"
        f"  (mean over {ref_n} plain-cell records at a {ref_periods}-period window, "
        f"rescaled by sqrt({ref_periods}/{shipped.n_periods}); see\n"
        f"  sim/tools/starved_cell_jitter_energy.py for the calibration. The rescaling is\n"
        f"  a window-length law and carries no ring-length term, so it applies to this\n"
        f"  11-stage family as it does to the 5-stage one it was calibrated on.)"
    )

    print("\nring period, and how much it moves across the run")
    print(
        f"  {'variant':<16} {'T0 ring1':>11} {'T0 ring2':>11} "
        f"{'min block':>11} {'max block':>11} {'swing':>9}"
    )
    for v in variants:
        lo = min(v.blocks) if v.blocks else float("nan")
        hi = max(v.blocks) if v.blocks else float("nan")
        print(
            f"  {v.label:<16} {v.period:11.4e} {v.period_r2:11.4e} "
            f"{lo:11.4e} {hi:11.4e} {100 * v.block_swing:8.3f}%"
        )
    nblk = len(shipped.blocks) or 1
    print(
        f"  (each block is {(shipped.discarded + shipped.n_periods) // nblk} consecutive "
        f"periods; the swing is (max-min)/T0 over the\n"
        f"  {nblk} blocks of the same run. Ring 2 is the wstv = 0.240u ring, running in\n"
        "  every deck of this family.)"
    )

    print("\nthe within-topology ratios, which are what this experiment turns on:")
    print("  numerator and denominator differ by exactly one thing, whether clk toggles.")
    print(f"  {'pair':<44} {'ring 1':>10} {'ring 2':>10}")
    for title, num, den, table in (
        ("shipped array (xa1 + both digitizers)", "shipped", "shipped-static", by_key),
        ("xsb on xo only (no per-ring digitizer)", "xsb", "xsb-static", by_key),
        ("#76's bound (5-stage, one consumer)", "buffered", "buf-static", bound_by_key),
    ):
        n, d = table[num], table[den]
        r2 = (
            f"{n.sigma_r2[1] / d.sigma_r2[1]:9.2f}x"
            if n.sigma_r2 and d.sigma_r2
            else f"{'n/a':>10}"
        )
        print(f"  {title:<44} {n.sigma[1] / d.sigma[1]:9.2f}x {r2}")

    bound = bound_by_key["buffered"].sigma[1] / bound_by_key["buf-static"].sigma[1]
    ratio = shipped.sigma[1] / by_key["shipped-static"].sigma[1]
    print(
        f"\n  #76's upper bound on the shipped number: {bound:.2f}x\n"
        f"  the shipped number itself:               {ratio:.2f}x"
        f"   ({'below' if ratio < bound else 'NOT below'} the bound"
        + (f", by {100 * (1 - ratio / bound):.0f} %)" if ratio < bound else ")")
    )

    verdict, rationale = classify_shipped(by_key, bound, ref_1)
    print(f"\nshipped-array residual: {verdict.upper()}")
    print(rationale)

    xsb_verdict, xsb_rationale = classify_xsb(by_key, ref_1)
    print(f"\nxsb-on-xo path: {xsb_verdict.upper()}")
    print(xsb_rationale)

    if args.check:
        failed = False
        for got, recorded, what in (
            (verdict, RECORDED_SHIPPED_VERDICT, "the shipped-array residual"),
            (xsb_verdict, RECORDED_XSB_VERDICT, "the xsb-on-xo path"),
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
            f"\nOK: the committed records still classify as {verdict!r} / {xsb_verdict!r}, "
            "the conclusions sim/characterization-liveness-tap-phase-cost.md records."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
