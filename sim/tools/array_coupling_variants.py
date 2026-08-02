#!/usr/bin/env python3
"""Compare the four DUT variants of issue #51's ring-to-ring coupling experiment.

    python3 sim/tools/array_coupling_variants.py           # the tables
    python3 sim/tools/array_coupling_variants.py --check   # gate the finding

Like ``sim/tools/jitter_energy_law.py`` and
``sim/tools/starved_cell_jitter_energy.py`` this is a *derivation*, not a
simulation: it reads only records already committed under ``sim/records/`` and
does arithmetic on them. It needs neither ngspice nor the PDK, and it writes
nothing.

The question (issue #51)
------------------------
``sim/records/2026-08-01-ro-array-sanity-jitter-01.md`` -- four rings plus an
XOR tree -- measures ``sigma_r1_1 = 23.2 ps`` on ring 1. The same delay cell,
at the same fixed injected noise density, at the same corner, over the same
16-period window shape, measures ``0.587 ps`` standing alone
(``sim/records/2026-08-01-ro-ring5-starved-jitter-long-02.md``). ~40x, and
seed-independent to 0.3 % where a genuine 16-period estimate scatters ~15 %.

Issue #46 refuted the explanation that was on record (that the array run's
16-period start-up window was the cause): the standalone deck reports that
same window geometry inside its own runs and it comes back healthy. So the
window is not the explanation, and two candidates were left:

* **coupling** -- ring 2's phase perturbs ring 1's threshold crossings through
  the shared gate structure of the combiner's input stage (in the array deck,
  ``xa1 ro1 ro2 t1 vdd 0 xor2`` puts ring 1's output on four transistor gates
  whose internal nodes ring 2 drives);
* **numerical** -- ngspice solves the whole deck on one shared adaptive
  timestep, so a second ring at an incommensurate frequency moves where ring
  1's own timepoints land.

Both predict a deterministic (seed-independent), faster-than-``sqrt(t)``
perturbation absent from a standalone ring, so neither is distinguishable from
the array record alone.

The four variants this script tabulates
---------------------------------------
Each differs from the control in exactly one thing, at one corner
(``tt``/27 C/3.30 V), through the control's own window geometry (opened 256
periods after start-up, spanning 512 periods):

1. ``ro-ring5-starved-jitter-long``      one ring, nothing attached (CONTROL)
2. ``ro-array-coupling-xor-static``      + the array's xa1, second input tied
                                         to a rail            (static load)
3. ``ro-array-coupling-xor-driven``      + xa1 driven by a second ring
                                                              (coupling path)
4. ``ro-array-coupling-rings-only``      two rings, unconnected  (numerical
                                                                  path)

Variant 4 is the decisive one: it contains everything the numerical
explanation needs and nothing the coupling explanation needs.

Why the sigmas here are RAW
---------------------------
``starved_cell_jitter_energy.py`` scales each record's ``sigma`` by that
corner's device-noise density, because it compares figures across corners.
Every record here is at the same corner with the same fixed injected density,
so the scaling is a common factor and is deliberately *not* applied: these
numbers are directly comparable to each other, and to the raw ``sigma_r1_1``
of the array-sanity record, without it. They are therefore NOT physical
jitter and no entropy claim may be built on them (DR-0004 tiering).
"""

from __future__ import annotations

import argparse
import math
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

#: The one corner this experiment is run at. It is a mechanism question, not a
#: PVT one (issue #51), so a single corner is the whole design.
CORNER = "tt/27/3.30"

#: ``(label, record glob, testbench manifest, what makes it different)``.
#: Order is the issue's variant order, which is also the order in which the
#: comparisons below are meant to be read.
#:
#: Every glob ends ``-[0-9]*`` and not ``-*``: the record's sequence number
#: must follow the testbench slug DIRECTLY. Without that, a glob also matches
#: any *derived* testbench whose slug merely starts with this one's -- issue
#: #75 added ``ro-array-coupling-xor-driven-buffered`` and
#: ``ro-array-coupling-xor-static-buffered``, either of which would otherwise
#: have been read in here as one of this experiment's own variants and moved
#: sim/characterization-array-ring-coupling.md's conclusion silently.
VARIANTS = [
    (
        "1 control",
        "*-ro-ring5-starved-jitter-long-[0-9]*.md",
        TB / "ro-ring5-starved-jitter-long" / "tb.json",
        "one ring, nothing attached",
    ),
    (
        "2 xor-static",
        "*-ro-array-coupling-xor-static-[0-9]*.md",
        TB / "ro-array-coupling-xor-static" / "tb.json",
        "+ xa1, 2nd input on a rail",
    ),
    (
        "3 xor-driven",
        "*-ro-array-coupling-xor-driven-[0-9]*.md",
        TB / "ro-array-coupling-xor-driven" / "tb.json",
        "+ xa1 driven by ring 2",
    ),
    (
        "4 rings-only",
        "*-ro-array-coupling-rings-only-[0-9]*.md",
        TB / "ro-array-coupling-rings-only" / "tb.json",
        "2 rings, unconnected",
    ),
]

#: The record the whole experiment exists to explain. Its own window is 16
#: periods opened at the second rise, which is what ``sigma_startup16_*``
#: reproduces inside every variant run.
SANITY_RECORD = RECORDS / "2026-08-01-ro-array-sanity-jitter-01.md"

#: Classification thresholds, applied to each variant's lag-1 sigma as a
#: multiple of the control's.
#:
#: ``NULL_TOLERANCE`` -- at or below this, a variant counts as *reproducing the
#: control*: whatever it adds did not move sigma materially. Three is chosen to
#: sit clear of the factor the static XOR load alone can move sigma by (the
#: loaded ring is slower and its edges are slower, which converts more of the
#: same injected noise into timing) while being far below the ~29x the effect
#: under investigation is. Measured, that load factor is 1.06x, so the band is
#: not tight.
NULL_TOLERANCE = 3.0
#: ``EXCESS_FACTOR`` -- at or above this, a variant counts as *reproducing the
#: artefact*. Ten is well below the 28.6x actually measured on variant 3 and
#: well above any plausible load effect, so the classification cannot flip on
#: either.
EXCESS_FACTOR = 10.0

#: The verdict the committed records actually support, recorded in
#: ``sim/characterization-array-ring-coupling.md``.
#:
#: ``--check`` gates on the *measured* verdict still equalling this one. That
#: is deliberately not the same thing as gating on a particular hypothesis
#: being true: this constant is written down AFTER the measurement, and if a
#: future record moves the classification the check fails and whoever moved it
#: has to update the recorded conclusion rather than quietly leaving a stale
#: one in the characterization document. Set it to ``None`` to run the
#: classification without gating on its outcome.
RECORDED_VERDICT: str | None = "coupling"


class Variant:
    """One DUT variant's record at :data:`CORNER`, with both windows."""

    def __init__(self, label: str, record: Record, manifest: Path, difference: str) -> None:
        self.label = label
        self.rec = record
        self.difference = difference
        self.discarded, self.n_periods = window_geometry(manifest)
        self.period = record.values["period"]
        self.period_r2 = record.values.get("period_r2")

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
        self.startup_exponent = (
            _loglog_slope(
                [float(L) for L in s_lags], [self.startup_sigma[L] for L in s_lags]
            )
            if len(s_lags) > 1
            else float("nan")
        )

    @property
    def spread_1(self) -> float | None:
        return self.rec.spread("sigma_1")

    @property
    def startup_spread_1(self) -> float | None:
        return self.rec.spread("sigma_startup16_1")

    @property
    def beat_hz(self) -> float | None:
        """``|1/T0_r1 - 1/T0_r2|`` when a second ring is present.

        The coupling hypothesis says the perturbation is a beat between two
        incommensurate ring frequencies, so the beat rate is the number the
        hypothesis actually predicts something about and it is reported rather
        than left implicit.
        """
        if not self.period_r2:
            return None
        return abs(1.0 / self.period - 1.0 / self.period_r2)


class SanityRun:
    """The array-sanity record, in the same shape as a :class:`Variant`.

    Its measurement keys are ``sigma_r1_*`` over a 16-period window opened at
    the second rise, so it lines up with the variants' ``sigma_startup16_*``
    block and with nothing else. Keeping it in its own class rather than
    pretending it is a fifth variant is deliberate: it has no 512-period
    window to compare against, and quietly putting it in the long-window table
    would invite exactly the apples-to-oranges reading this experiment exists
    to remove.
    """

    label = "ro-array-sanity-jitter (4 rings + XOR tree)"

    def __init__(self, path: Path) -> None:
        self.rec = Record(path)
        self.stem = path.stem
        self.period = self.rec.values["period_r1"]
        self.lags = sorted(
            int(m.group(1))
            for m in (re.fullmatch(r"sigma_r1_(\d+)", k) for k in self.rec.values)
            if m
        )
        self.sigma = {L: self.rec.values[f"sigma_r1_{L}"] for L in self.lags}
        self.exponent = _loglog_slope(
            [float(L) for L in self.lags], [self.sigma[L] for L in self.lags]
        )

    @property
    def spread_1(self) -> float | None:
        return self.rec.spread("sigma_r1_1")


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


def classify(ratios: dict[str, float]) -> tuple[str, str]:
    """``(verdict, rationale)`` from the three lag-1 sigma ratios to the control.

    The order of the tests is the order in which an explanation, once it
    applies, makes the later comparisons uninterpretable:

    * **load** is tested first. Variant 2 adds only a static gate load, and
      every other variant carries that same load. If the load alone reproduces
      the artefact then variants 3 and 4 inherit it and separate nothing.
    * **numerical** next. Variant 4 has two rings on one shared adaptive
      timestep and no electrical path between them, so if it reproduces the
      artefact then variant 3 -- which also has two rings -- cannot attribute
      anything to the attachment.
    * **coupling** last, and only when it is the *sole* variant that moves:
      variant 3 differs from variant 2 by the neighbour switching, and from
      variant 4 by the electrical attachment.
    * otherwise **neither**: a stated negative result, not a silence.
    """
    static = ratios["2 xor-static"]
    driven = ratios["3 xor-driven"]
    rings = ratios["4 rings-only"]

    if static >= EXCESS_FACTOR:
        return "load", (
            "  LOAD. The static combiner load alone (variant 2, second XOR input on\n"
            "  a rail, no switching neighbour anywhere in the deck) already\n"
            "  reproduces the artefact. Variants 3 and 4 carry that same load, so\n"
            "  they attribute nothing further, and the array deck's excess is a\n"
            "  property of the loaded ring rather than of its neighbours."
        )
    if rings >= EXCESS_FACTOR:
        return "numerical", (
            "  NUMERICAL. The excess appears with a second ring present in the same\n"
            "  deck and NO electrical connection to it (variant 4), so it is a\n"
            "  property of solving two asynchronous rings on one shared adaptive\n"
            "  timestep, not of the circuit. It bounds what any multi-ring\n"
            "  transient-noise run in this repository may quote as a per-ring sigma."
        )
    if driven >= EXCESS_FACTOR and static <= NULL_TOLERANCE and rings <= NULL_TOLERANCE:
        return "coupling", (
            "  COUPLING. The excess appears only when a second ring DRIVES the\n"
            "  combiner's other input (variant 3). It does not appear when that\n"
            "  input is tied to a rail (variant 2, the same load), and it does not\n"
            "  appear when the second ring is present in the same deck but\n"
            "  electrically unconnected (variant 4, the same shared adaptive\n"
            "  timestep). Electrical attachment is the difference; being solved\n"
            "  together is not."
        )
    return "neither", (
        "  NEITHER. No variant reproduces the artefact: see the ratios above. One\n"
        "  XOR gate and one neighbouring ring do not account for what the array\n"
        "  deck measured, so the cause lies in what these decks do NOT reproduce --\n"
        "  the other two rings, the rest of the XOR tree, the array deck's much\n"
        "  shorter run, or its different ngspice build and host. That is a stated\n"
        "  negative result and it narrows the search; it does not close it."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="array_coupling_variants.py",
        description="Compare issue #51's four DUT variants and say which "
        "hypothesis -- coupling or numerical -- the data supports.",
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
        sanity = SanityRun(SANITY_RECORD)
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    control = variants[0]
    by_label = {v.label.split()[0]: v for v in variants}

    print(
        f"issue #51 -- four DUT variants at {CORNER} (process/degC/V), same starved\n"
        f"delay cell, same fixed injected noise density, same window geometry.\n"
        f"sigma is RAW at the injected level: comparable across these rows and to\n"
        f"{sanity.stem}, but not physical jitter.\n"
    )

    lags = control.lags
    header = (
        f"{'variant':<14} {'differs by':<28} {'T0 (s)':>11} "
        + "".join(f"{'L=' + str(L):>11}" for L in lags)
        + f"{'expon':>7}{'tail':>7}{'spr_1':>8}"
    )
    print("512-period window, opened 256 periods after start-up")
    print(header)
    print("-" * len(header))
    for v in variants:
        spread = v.spread_1
        print(
            f"{v.label:<14} {v.difference:<28} {v.period:11.4e} "
            + "".join(f"{v.sigma[L]:11.4e}" for L in lags)
            + f"{v.exponent:7.3f}{v.exponent_tail:7.3f}"
            + (f"{100 * spread:7.1f}%" if spread is not None else f"{'n/a':>8}")
        )
    ref_1, ref_n, ref_periods = reference_spread(1, control.n_periods)
    print(
        f"\n  seed-spread reference at lag 1 for a {control.n_periods}-period window: "
        f"{100 * ref_1:.2f}%\n"
        f"  (mean over {ref_n} plain-cell records at a {ref_periods}-period window, "
        f"rescaled by sqrt({ref_periods}/{control.n_periods}); see\n"
        f"  sim/tools/starved_cell_jitter_energy.py for the calibration.)"
    )

    print("\n16-period window opened at the second rise -- the window")
    print(f"{sanity.stem} itself used, reproduced inside the SAME runs")
    s_lags = control.startup_lags
    header2 = (
        f"{'variant':<14} {'T0 (s)':>11} "
        + "".join(f"{'L=' + str(L):>11}" for L in s_lags)
        + f"{'expon':>7}{'spr_1':>8}"
    )
    print(header2)
    print("-" * len(header2))
    for v in variants:
        spread = v.startup_spread_1
        print(
            f"{v.label:<14} {v.startup_period:11.4e} "
            + "".join(f"{v.startup_sigma[L]:11.4e}" for L in s_lags)
            + f"{v.startup_exponent:7.3f}"
            + (f"{100 * spread:7.1f}%" if spread is not None else f"{'n/a':>8}")
        )
    s_spread = sanity.spread_1
    print(
        f"{'the record':<14} {sanity.period:11.4e} "
        + "".join(f"{sanity.sigma[L]:11.4e}" for L in sanity.lags)
        + f"{sanity.exponent:7.3f}"
        + (f"{100 * s_spread:7.1f}%" if s_spread is not None else f"{'n/a':>8}")
    )
    ref_s, _, _ = reference_spread(1, 16)
    print(
        f"\n  seed-spread reference at lag 1 for a 16-period window: {100 * ref_s:.2f}%.\n"
        f"  A spread far BELOW it means every seed is tracing the same deterministic\n"
        f"  curve; that is the signature {sanity.stem}\n"
        f"  shows at {100 * (s_spread or 0):.1f}%."
    )

    print("\nratio to the control at lag 1")
    print(f"  {'variant':<14} {'512-period window':>19} {'16-period window':>19}")
    for v in variants[1:]:
        long_ratio = v.sigma[1] / control.sigma[1]
        short_ratio = (
            v.startup_sigma[1] / control.startup_sigma[1]
            if control.startup_sigma
            else float("nan")
        )
        print(f"  {v.label:<14} {long_ratio:18.1f}x {short_ratio:18.1f}x")
    print(
        f"  {'the record':<14} {'n/a':>19} "
        f"{sanity.sigma[1] / control.startup_sigma[1]:18.1f}x"
    )

    for v in variants:
        if v.beat_hz is not None:
            print(
                f"\n  {v.label}: ring 1 at {1 / v.period:.4e} Hz, ring 2 at "
                f"{1 / v.period_r2:.4e} Hz, beat {v.beat_hz:.4e} Hz "
                f"({v.beat_hz * v.period:.4f} cycles of ring 1 per beat period"
                f" -> one beat every {1 / (v.beat_hz * v.period):.1f} periods)"
            )

    ratios = {
        label: by_label[label.split()[0]].sigma[1] / control.sigma[1]
        for label in ("2 xor-static", "3 xor-driven", "4 rings-only")
    }
    verdict, rationale = classify(ratios)

    print("\nratios used for the classification (lag-1 sigma / control's)")
    for label, ratio in ratios.items():
        band = (
            "reproduces the artefact"
            if ratio >= EXCESS_FACTOR
            else "reproduces the control"
            if ratio <= NULL_TOLERANCE
            else "neither band"
        )
        print(f"  {label:<14} {ratio:7.2f}x   {band}")
    print(
        f"  (>= {EXCESS_FACTOR:g}x counts as reproducing the artefact, "
        f"<= {NULL_TOLERANCE:g}x as reproducing the control.)"
    )

    print(f"\nverdict: {verdict.upper()}")
    print(rationale)

    if args.check:
        if RECORDED_VERDICT is None:
            print(
                "\nERROR: RECORDED_VERDICT is unset, so --check has nothing to gate "
                "against. Set it to the verdict the committed records support.",
                file=sys.stderr,
            )
            return 2
        if verdict != RECORDED_VERDICT:
            print(
                f"\nFAIL: the committed records now classify as {verdict!r}, but the "
                f"conclusion recorded in sim/characterization-array-ring-coupling.md "
                f"is {RECORDED_VERDICT!r}. Either a record changed or a variant was "
                "re-run; update the recorded conclusion to match the evidence "
                "(and this constant with it) rather than leaving a stale one.",
                file=sys.stderr,
            )
            return 1
        print(
            f"\nOK: the committed records still classify as {verdict!r}, the "
            "conclusion sim/characterization-array-ring-coupling.md records."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
