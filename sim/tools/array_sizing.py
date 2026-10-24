#!/usr/bin/env python3
"""Check the entropy source against DR-0007 §2's sizing inequality.

    python3 sim/tools/array_sizing.py                  # report Q_array per corner
    python3 sim/tools/array_sizing.py --check          # assert the ratified 2 kbps holds
    python3 sim/tools/array_sizing.py --rate 500       # ask about a different rate
    python3 sim/tools/array_sizing.py --a 1.79         # price a different constant

DR-0007 §6 makes this an acceptance criterion rather than a nicety: "#7 may not
close on an N without showing the §2 inequality holds at that corner." This
script is that showing, done from committed evidence records so a reviewer can
re-run it instead of re-deriving it.

Method
------
DR-0007 §2's array figure of merit is

    Q_array(T_s) = sum_i kappa_i^2 * T_s / T0_i^2        (independent rings)

with ``kappa^2`` the random-walk rate constant of ring *i*
(``sigma_acc^2(t) = kappa^2 t``). ``sim/tools/jitter_energy_law.py`` derives,
from this repository's 27-point candidate-A grid of a plain inverter ring, that
``kappa^2`` is fixed by the ring's power (DR-0010's ``(*)``):

    kappa^2 = a * kB * T / P_ring

``sim/tools/starved_cell_jitter_energy.py`` measures the same law on the
shipped, series-starved cell, and
``DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy`` §2 selects the
constant the array is sized against from it: the asymptotic-slope ``a`` at that
record's entropy-binding corner (``ss``/-40 C/3.63 V), **a = 7.32** -- not the
three-corner asymptotic mean (11.77), not a lag-1 figure (24.84 mean), and no
longer the plain cell's 1.79. A *deterministic* measurement of each ring's
period and supply current --
which is what ``sim/tb/ro-array-core-power/`` records at each PVT point -- is
enough to evaluate ``Q_array``. That is deliberate: a transient-noise run of the
shipped eleven-stage array over the tens of thousands of periods a direct
``sigma_acc`` measurement would need is not affordable, whereas its supply
current is cheap and bit-reproducible.

What ``--check`` actually enforces
---------------------------------
Three things, all hard failures:

  * ``Q_array >= M * Q_H0`` at every measured corner of the shipped array
    (the full covered grid, DR-0015), at the rate given by ``--rate``
    (default: the ratified 2 kbps raw-rate row);
  * that ``A_JITTER_ENERGY`` below still agrees, to within ``A_TOLERANCE``,
    with the value ``starved_cell_jitter_energy.sizing_constant()`` derives
    from the committed starved-cell records -- the asymptotic ``a`` at
    ``SIZING_CONSTANT_CORNER``, selected by corner identity -- so the two
    cannot drift apart unnoticed, and a wrong estimator cannot pass; and
  * that the selected corner's constant is still the smallest asymptotic
    ``a`` measured at any corner. DR-0015 moved the entropy-binding corner to
    ``ss``/+125 C/3.63 V, where no starved-cell jitter record exists; using
    the smallest measured constant there is the conservative reading, and
    this check fails if a later record stops making it so.

A derivation that cannot run at all (missing family, missing corner, a value
that is not a positive finite number) is also a hard failure.

Every run *also* prints ``kappa^2`` as measured by the transient-noise array
records (``sim/tb/ro-array-sanity-jitter/``, which measure ``sigma_1`` and the
ring's supply current in the same run) beside what the law predicts. That
comparison is **reported, not enforced**: the one such record in the tree
disagrees by over three orders of magnitude, and DR-0010 §Consequences diagnoses that
run's ``sigma`` as start-up settling drift rather than jitter (seed-independent
to 0.3 %, accumulating as lag^0.81 rather than lag^0.5); #51 later traced it
to deterministic ring-to-ring coupling through the XOR input stage. The law
itself was confirmed on the shipped starved cell by #46's long-window records,
which is where the stated constant now comes from.

What this does NOT do
---------------------
It does not measure ``H``. ``Q_H0`` is DR-0007 §2's stated target and DR-0004's
tiering still applies: everything here is a simulation-derived design estimate,
not an entropy assessment. #12 owns measuring ``H`` for the array.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _record_parsing import current_records, format_corner, parse_corner, parse_result_values, parse_status  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"

KB = 1.380649e-23

#: The array-sizing jitter-energy constant:
#: DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy §2's ``a`` --
#: the shipped starved cell's asymptotic-slope constant at that record's
#: entropy-binding corner (``ss``/-40 C/3.63 V), as derived by
#: ``starved_cell_jitter_energy.sizing_constant()``. Deliberately a *stated*
#: constant rather than a live one: the README's Raw rate row and
#: design/README.md are quoted against this exact value, and they must not
#: shift under a reader every time a record is appended. It is kept honest by
#: ``--check``, which re-runs the derivation and fails if the two have drifted
#: by more than A_TOLERANCE.
A_JITTER_ENERGY = 7.32

#: Allowed relative drift between A_JITTER_ENERGY and the live derivation.
#: Set from the selected quantity's own bounds, not from the spread between
#: corners or estimators. The derivation reads committed records only, so it is
#: deterministic; the stated 7.32 is it (7.322) rounded to three significant
#: figures, a rounding error of at most 0.005 / 7.32 = 0.07 %. One percent is
#: ~15x that, and still ~50x tighter than the nearest wrong estimator (the
#: asymptotic ``a`` at the next corner, 10.87, +49 %; the three-corner
#: asymptotic mean 11.77 is +61 %; the lag-1 figures are +190 % and more; the
#: plain cell's 1.79 is -76 %). A re-measured constant at the same corner --
#: a different seed set moves it by several percent -- fails too, on purpose:
#: moving the stated constant is a decision record's job.
A_TOLERANCE = 0.01

#: DR-0010's plain-cell ``a`` (sim/tools/jitter_energy_law.py, 27-point
#: candidate-A grid). No longer the sizing input; kept so historical tables
#: quoted at it (DR-0010 §3, DR-0015, the characterization summaries) stay
#: reproducible with ``--a 1.79`` and by the tools that print it beside the
#: starved-cell constants.
A_PLAIN_CELL = 1.79

#: DR-0007 §2
Q_H0 = 4.0e-3
MARGIN_M = 1.5

#: The ratified Raw rate row, in bits per second:
#: DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy §1, "> 2 kbps
#: sustained at the raw tap". The default rate every inequality is tested at.
RAW_RATE_BPS = 2000.0

#: DR-0010 §1's raw-rate value (> 500 bps), superseded in value by DR-0011-
#: raw-rate-at-the-measured-starved-cell-jitter-energy. Historical: kept for
#: the tools whose committed tables are quoted at it.
DR0010_RATE_BPS = 500.0

#: The fixed injected per-stage noise density of the jitter testbenches, V/sqrt(Hz).
INJECTED_DENSITY = 1.0e-8


class Record:
    def __init__(self, path: Path) -> None:
        text = path.read_text()
        self.stem = path.stem
        self.values = parse_result_values(text, label=self.stem, error_cls=RuntimeError)
        self.process, self.temp_c, self.vdd = parse_corner(text, label=self.stem)
        self.status = parse_status(text, label=self.stem)
        self.temp_k = self.temp_c + 273.15

    @property
    def corner(self) -> str:
        return format_corner(self.process, self.temp_c, self.vdd)


def load(glob: str, *, include_superseded: bool = False) -> list[Record]:
    """Records matching ``glob``; ``status: superseded`` ones are excluded
    unless ``include_superseded`` requests an explicit historical read."""
    return current_records(
        RECORDS, glob, make=Record, include_superseded=include_superseded)


#: Every record family that measures the shipped array's per-ring period and
#: supply current, i.e. everything this script's inequality can be evaluated
#: at. ``ro-array-core-power`` is the original three-point family;
#: ``ro-array-core-pvt-q`` (issue #13) is the full 27-point covered-grid
#: family, measured by the same expressions on the same DUT with a longer
#: transient window (see that testbench's header, and
#: ``sim/tools/worst_corner_entropy.py``, which reports the two families'
#: measured agreement at the three PVT points they share). Both are read
#: here, because "the inequality holds at every measured corner" is a much
#: weaker statement if the script only looks at three of them.
#: `-[0-9]` and not `-`: the sequence number must follow the slug directly, so
#: a record from a *variant* testbench whose slug starts with one of these
#: (e.g. ro-array-core-power-BUFFERED, issue #75's unadopted buffer
#: mitigation) can never be read as a shipped-array corner.
ARRAY_RECORD_GLOBS = ("*-ro-array-core-power-[0-9]*.md", "*-ro-array-core-pvt-q-[0-9]*.md")


def load_array_records() -> list[Record]:
    """Every shipped-array PVT record from every family in ``ARRAY_RECORD_GLOBS``."""
    return [rec for glob in ARRAY_RECORD_GLOBS for rec in load(glob)]


def dedupe_by_corner(points: list["ArrayPoint"]) -> list["ArrayPoint"]:
    """One point per PVT corner, preferring the full-grid family.

    Where both families measure the same corner they agree to a few parts in
    100 000 (``sim/tools/worst_corner_entropy.py`` reports that comparison),
    so which one wins is immaterial to any number here -- but printing the
    same corner twice would make the table look like a disagreement.
    """
    best: dict[str, ArrayPoint] = {}
    for point in points:
        current = best.get(point.rec.corner)
        if current is None or "pvt-q" in point.rec.stem:
            best[point.rec.corner] = point
    return list(best.values())


class ArrayPoint:
    """One PVT point of the shipped array."""

    def __init__(self, rec: Record, a: float = A_JITTER_ENERGY) -> None:
        self.rec = rec
        #: the jitter-energy constant this point is sized against. Defaults to
        #: the stated A_JITTER_ENERGY; ``--a`` overrides it so a superseding
        #: decision record can price a *different* measured constant without
        #: editing the stated constant the published arithmetic is quoted
        #: against. Changing the stated constant is a decision, not a run.
        self.a = a
        v = rec.values
        # N is read off the record, not assumed: a record of a two-ring array
        # carries period_r1/period_r2 and nothing else.
        self.n = len([k for k in v if re.fullmatch(r"period_r\d+", k)])
        idx = range(1, self.n + 1)
        self.periods = [v[f"period_r{i}"] for i in idx]
        self.currents = [abs(v[f"i_r{i}_a"]) for i in idx]
        self.powers = [i * rec.vdd for i in self.currents]
        self.p_rings = sum(self.powers)
        self.p_tree = abs(v["i_tree_a"]) * rec.vdd
        self.p_total = self.p_rings + self.p_tree
        self.e_cycle = abs(v["e_cycle_r1_j"])
        self.c_eff = abs(v["c_eff_node_r1_f"])
        self.ring_swing = v["ring_swing_v"]
        self.xo_swing = v["xo_swing_v"]
        self.xo_rate = v["xo_trans_per_s"]

    @property
    def g(self) -> float:
        """Q_array per second of sample period: Q_array(T_s) = g * T_s."""
        kt = KB * self.rec.temp_k
        return sum(self.a * kt / p / (t * t) for p, t in zip(self.powers, self.periods))

    def q_array(self, rate_bps: float) -> float:
        return self.g / rate_bps

    def max_rate_bps(self) -> float:
        return self.g / (MARGIN_M * Q_H0)


def sanity_invariant() -> list[tuple[str, float, float, float]]:
    """(record stem, kappa^2 measured, kappa^2 from the law, ratio) per sanity record."""
    noise = {r.corner: r for r in load("*-rostage-noise-*.md")}
    out = []
    for rec in load("*-ro-array-sanity-jitter-*.md"):
        n = noise.get(rec.corner)
        if n is None:
            continue
        scale = n.values["inoise_dens_1g"] / INJECTED_DENSITY
        sigma1 = rec.values["sigma_r1_1"] * scale
        t0 = rec.values["period_r1"]
        power = abs(rec.values["i_r1_a"]) * rec.vdd
        measured = sigma1**2 / t0
        predicted = A_JITTER_ENERGY * KB * rec.temp_k / power
        out.append((rec.stem, measured, predicted, measured / predicted))
    return out


def derived_sizing_constant():
    """Re-derive the sizing constant with ``sim/tools/starved_cell_jitter_energy.py``.

    Returns ``(constant, description)``. ``constant`` is the
    ``starved_cell_jitter_energy.SizingConstant`` -- the asymptotic ``a`` at
    the corner DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy §2
    names, with its record stem and every measured corner's value -- or None
    when the derivation could not run at all, with the reason in
    ``description``. None is a ``--check`` failure, not something to shrug at,
    because the constant this file sizes against would then be unverifiable.

    The plain-cell derivation (``jitter_energy_law.derive_a``) is deliberately
    not consulted: it remains correct about the plain cell, it simply is not
    the sizing input any more.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from starved_cell_jitter_energy import sizing_constant  # noqa: PLC0415

        sel = sizing_constant()
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        return None, f"could not be re-derived: {exc}"
    others = ", ".join(
        f"{c} {v:.3f}" for c, v in sorted(sel.by_corner.items()) if c != sel.corner)
    return sel, (
        f"starved_cell_jitter_energy.py derives asymptotic a = {sel.value:.3f} at "
        f"{sel.corner} ({sel.stem}); other measured corners: {others or 'none'}"
    )


def _positive_finite(text: str) -> float:
    """argparse type: a positive, finite float (a rate or a constant)."""
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a number: {text!r}") from None
    if not (math.isfinite(value) and value > 0):
        raise argparse.ArgumentTypeError(f"must be a positive finite number, got {text!r}")
    return value


def shipped_ring_count() -> int:
    """How many rings design/ro_array_core.spice actually instantiates.

    Records of a superseded array size stay in sim/records/ forever -- that is
    what append-only means -- so the inequality must be evaluated against the
    records that describe the array in design/, not against every record the
    testbench ever produced.
    """
    netlist = REPO_ROOT / "design" / "ro_array_core.spice"
    body = netlist.read_text().split(".ends", 1)[0]
    return len(re.findall(r"^x\S+\s+.*\bro_ring\d+\b", body, re.M))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="array_sizing.py",
        description="Evaluate DR-0007 §2's sizing inequality for the shipped array.",
    )
    parser.add_argument(
        "--rate", type=_positive_finite, default=RAW_RATE_BPS, metavar="BPS",
        help=f"raw rate to test the inequality at (default {RAW_RATE_BPS:g} bps, the "
             "ratified Raw rate row, DR-0011-raw-rate-at-the-measured-starved-cell-"
             f"jitter-energy §1; DR-0010's superseded value was {DR0010_RATE_BPS:g})",
    )
    parser.add_argument(
        "--a", type=_positive_finite, default=A_JITTER_ENERGY, dest="a", metavar="A",
        help=f"jitter-energy constant to size against (default {A_JITTER_ENERGY:g}, the "
             "stated DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy §2 "
             "value). Overriding it prices a different constant -- e.g. DR-0010's "
             f"plain-cell {A_PLAIN_CELL:g} -- WITHOUT moving the stated one; moving that "
             "is a decision record's job, not a flag's. Incompatible with --check, "
             "which exists to hold the stated constant to the derivation.",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="exit non-zero unless the inequality holds at every measured corner",
    )
    args = parser.parse_args(argv)
    if args.check and args.a != A_JITTER_ENERGY:
        print(
            "error: --check asserts the STATED constant still matches its derivation, "
            "so it cannot be combined with an overridden --a",
            file=sys.stderr,
        )
        return 2

    records = load_array_records()
    if not records:
        print(
            "ERROR: no shipped-array records found (globs: "
            + ", ".join(ARRAY_RECORD_GLOBS) + ")",
            file=sys.stderr,
        )
        return 2
    shipped_n = shipped_ring_count()
    points, other = [], []
    for rec in records:
        point = ArrayPoint(rec, a=args.a)
        (points if point.n == shipped_n else other).append(point)
    points = dedupe_by_corner(points)
    if not points:
        print(
            f"ERROR: no record measures the shipped {shipped_n}-ring array "
            f"(design/ro_array_core.spice)",
            file=sys.stderr,
        )
        return 2

    sel, a_note = derived_sizing_constant()
    need = MARGIN_M * Q_H0
    print(f"DR-0007 §2 requires Q_array >= M * Q_H0 = {MARGIN_M} * {Q_H0:g} = {need:g}")
    if args.rate == RAW_RATE_BPS:
        print(f"evaluated at a raw rate of {args.rate:g} bps (T_s = {1/args.rate:.4g} s), "
              f"the ratified Raw rate row")
    else:
        print(f"evaluated at a raw rate of {args.rate:g} bps (T_s = {1/args.rate:.4g} s)"
              f"  <-- OVERRIDDEN via --rate (the ratified row is {RAW_RATE_BPS:g} bps)")
    if args.a == A_JITTER_ENERGY:
        print(f"sizing constant a = {A_JITTER_ENERGY:g} (stated); {a_note}\n")
    else:
        print(
            f"sizing constant a = {args.a:g}  <-- OVERRIDDEN via --a "
            f"({args.a / A_JITTER_ENERGY:.2f}x the stated {A_JITTER_ENERGY:g}). "
            f"Nothing published is quoted at this value.\n"
            f"{a_note}\n"
        )

    header = (
        f"{'corner':<15} {'N':>2} {'T0_r1 (s)':>10} {'P_rings':>10} {'P_tree':>10} {'P_tot':>10} "
        f"{'E_cyc (J)':>10} {'swing':>7} {'xo':>7} {'Q_array':>10} {'R_max(bps)':>11}"
    )
    print(header)
    print("-" * len(header))
    for p in sorted(points, key=lambda p: p.q_array(args.rate)):
        print(
            f"{p.rec.corner:<15} {p.n:2d} {p.periods[0]:10.4e} {p.p_rings:10.4e} {p.p_tree:10.4e} "
            f"{p.p_total:10.4e} {p.e_cycle:10.4e} {p.ring_swing:7.3f} {p.xo_swing:7.3f} "
            f"{p.q_array(args.rate):10.3e} {p.max_rate_bps():11.4g}"
        )

    worst = min(points, key=lambda p: p.g)
    print()
    print(f"minimum-Q (entropy-binding) corner over the measured points: {worst.rec.corner}")
    print(f"  Q_array({args.rate:g} bps) = {worst.q_array(args.rate):.3e}   "
          f"required {need:g}   margin {worst.q_array(args.rate) / need:.2f}x")
    print(f"  highest rate satisfying DR-0007 §2 there: {worst.max_rate_bps():.4g} bps")

    hottest = max(points, key=lambda p: p.p_total)
    print(f"maximum-power corner over the measured points: {hottest.rec.corner}"
          f"  P_total(entropy source) = {hottest.p_total * 1e6:.1f} uW")

    if other:
        print(
            f"\n({len(other)} record(s) measure a different array size than the "
            f"{shipped_n}-ring cell in design/ and are excluded: "
            + ", ".join(sorted({f'{p.n}-ring' for p in other}))
            + ")"
        )

    inv = sanity_invariant()
    if inv:
        print("\njitter-energy law checked against the transient-noise array records:")
        for stem, meas, pred, ratio in inv:
            print(f"  {stem}: kappa^2 measured {meas:.4e} s, from the law {pred:.4e} s, "
                  f"ratio {ratio:.2f}x")
    else:
        print("\n(no ro-array-sanity-jitter records paired with a rostage-noise corner yet)")

    if args.check:
        if sel is None:
            print(
                f"\nFAIL: the sizing constant a = {A_JITTER_ENERGY:g} {a_note}",
                file=sys.stderr,
            )
            return 2
        drift = abs(sel.value - A_JITTER_ENERGY) / A_JITTER_ENERGY
        if drift > A_TOLERANCE:
            print(
                f"\nFAIL: A_JITTER_ENERGY = {A_JITTER_ENERGY:g} has drifted {drift:.1%} "
                f"from the asymptotic a = {sel.value:.3f} that "
                f"sim/tools/starved_cell_jitter_energy.py now derives at {sel.corner} "
                f"({sel.stem}; tolerance {A_TOLERANCE:.0%}). The constant is not the "
                f"thing to edit on its own: the Raw rate row and every rate figure "
                f"quoted from it move with it.",
                file=sys.stderr,
            )
            return 1
        if not sel.is_smallest:
            print(
                f"\nFAIL: the selected corner {sel.corner} (a = {sel.value:.3f}) is no "
                f"longer the smallest asymptotic a measured; {sel.smallest_corner} has "
                f"{sel.by_corner[sel.smallest_corner]:.3f}. Applying the selected value "
                f"at the DR-0015 entropy-binding corner is then no longer the "
                f"conservative reading, and the sizing constant needs a decision.",
                file=sys.stderr,
            )
            return 1
        failures = [p for p in points if p.q_array(args.rate) < need]
        if failures:
            for p in failures:
                print(
                    f"\nFAIL: {p.rec.corner}: Q_array = {p.q_array(args.rate):.3e} < {need:g}",
                    file=sys.stderr,
                )
            return 1
        print(
            f"\nOK: a = {A_JITTER_ENERGY:g} is within {A_TOLERANCE:.0%} of the asymptotic "
            f"a derived at {sel.corner} ({drift:.2%} off), the smallest measured; and "
            f"DR-0007 §2 holds at all {len(points)} measured corners at {args.rate:g} bps."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
