#!/usr/bin/env python3
"""Check the entropy source against DR-0007 §2's sizing inequality.

    python3 sim/tools/array_sizing.py                  # report Q_array per corner
    python3 sim/tools/array_sizing.py --check          # assert DR-0008's rate holds
    python3 sim/tools/array_sizing.py --rate 2000      # ask about a different rate

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
from this repository's 27-point candidate-A grid, that ``kappa^2`` is fixed by
the ring's power:

    kappa^2 = a * kB * T / P_ring ,    a = 1.79 +/- 0.14

so a *deterministic* measurement of each ring's period and supply current --
which is what ``sim/tb/ro-array-core-power/`` records at each PVT point -- is
enough to evaluate ``Q_array``. That is deliberate: a transient-noise run of the
shipped eleven-stage array over the tens of thousands of periods a direct
``sigma_acc`` measurement would need is not affordable, whereas its supply
current is cheap and bit-reproducible.

What ``--check`` actually enforces
---------------------------------
Exactly two things, both hard failures:

  * ``Q_array >= M * Q_H0`` at every measured corner of the shipped array, at
    the rate given by ``--rate``; and
  * that ``A_JITTER_ENERGY`` below still agrees, to within ``A_TOLERANCE``,
    with what ``sim/tools/jitter_energy_law.py`` derives from the record
    families it reads -- so the two cannot drift apart unnoticed.

Every run *also* prints ``kappa^2`` as measured by the transient-noise array
records (``sim/tb/ro-array-sanity-jitter/``, which measure ``sigma_1`` and the
ring's supply current in the same run) beside what the law predicts. That
comparison is **reported, not enforced**: the one such record in the tree
disagrees by four orders of magnitude, and DR-0008 §Consequences diagnoses that
run's ``sigma`` as start-up settling drift rather than jitter (seed-independent
to 0.3 %, accumulating as lag^0.81 rather than lag^0.5). Confirming the law on
the shipped starved cell needs a longer, later window; that measurement is #46's
and this script does not pretend to stand in for it.

What this does NOT do
---------------------
It does not measure ``H``. ``Q_H0`` is DR-0007 §2's stated target and DR-0004's
tiering still applies: everything here is a simulation-derived design estimate,
not an entropy assessment. #12 owns measuring ``H`` for the array.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"

KB = 1.380649e-23

#: DR-0008's ``a``, from sim/tools/jitter_energy_law.py over the candidate-A
#: 27-point grid. Deliberately a *stated* constant rather than a live one: the
#: figures in DR-0008 §3, the README's Raw rate row and design/README.md are all
#: quoted against this exact value, and they must not shift under a reader every
#: time a record is appended. It is kept honest by ``--check``, which re-runs the
#: derivation and fails if the two have drifted by more than A_TOLERANCE.
A_JITTER_ENERGY = 1.79

#: Allowed relative drift between A_JITTER_ENERGY and the live derivation.
#: Comfortably tighter than the 1.29x spread of ``a`` across the grid itself,
#: so a record family swapped for an inconsistent one fails loudly, and loose
#: enough that ordinary rounding does not.
A_TOLERANCE = 0.05

#: DR-0007 §2
Q_H0 = 4.0e-3
MARGIN_M = 1.5

#: DR-0008 §1's proposed raw-rate row, in bits per second.
DR0008_RATE_BPS = 500.0

#: The fixed injected per-stage noise density of the jitter testbenches, V/sqrt(Hz).
INJECTED_DENSITY = 1.0e-8

_VALUE = re.compile(r"^- `([a-z0-9_]+)`:\s*(?:mean\s+)?(-?[\d.]+(?:e[-+]?\d+)?)", re.M)


class Record:
    def __init__(self, path: Path) -> None:
        text = path.read_text()
        self.stem = path.stem
        self.values = {m.group(1): float(m.group(2)) for m in _VALUE.finditer(text)}
        self.process = self._field(text, r"process:\s*(\w+)")
        self.temp_c = float(self._field(text, r"temperature:\s*(-?[\d.]+)"))
        self.vdd = float(self._field(text, r"voltage:\s*([\d.]+)"))
        self.temp_k = self.temp_c + 273.15

    @staticmethod
    def _field(text: str, pattern: str) -> str:
        m = re.search(pattern, text)
        if m is None:
            raise RuntimeError(f"cannot find {pattern!r}")
        return m.group(1)

    @property
    def corner(self) -> str:
        return f"{self.process}/{self.temp_c:.0f}/{self.vdd:.2f}"


def load(glob: str) -> list[Record]:
    return [Record(p) for p in sorted(RECORDS.glob(glob))]


class ArrayPoint:
    """One PVT point of the shipped array."""

    def __init__(self, rec: Record) -> None:
        self.rec = rec
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
        return sum(
            A_JITTER_ENERGY * kt / p / (t * t) for p, t in zip(self.powers, self.periods)
        )

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


def derived_law_constant() -> tuple[float | None, str]:
    """Re-derive ``a`` with ``sim/tools/jitter_energy_law.py``.

    Returns ``(value, description)``. ``value`` is None when the derivation
    could not run at all, with the reason in ``description`` -- that is a
    ``--check`` failure, not something to shrug at, because the constant this
    file sizes against would then be unverifiable.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from jitter_energy_law import derive_a  # noqa: PLC0415

        mean_a, lo, hi = derive_a()
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        return None, f"could not be re-derived: {exc}"
    return mean_a, f"mean {mean_a:.3f} (min {lo:.3f}, max {hi:.3f})"


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
        "--rate", type=float, default=DR0008_RATE_BPS, metavar="BPS",
        help=f"raw rate to test the inequality at (default {DR0008_RATE_BPS:g} bps, DR-0008 §1)",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="exit non-zero unless the inequality holds at every measured corner",
    )
    args = parser.parse_args(argv)

    records = load("*-ro-array-core-power-*.md")
    if not records:
        print("ERROR: no sim/records/*-ro-array-core-power-*.md records found", file=sys.stderr)
        return 2
    shipped_n = shipped_ring_count()
    points, other = [], []
    for rec in records:
        (points if ArrayPoint(rec).n == shipped_n else other).append(ArrayPoint(rec))
    if not points:
        print(
            f"ERROR: no record measures the shipped {shipped_n}-ring array "
            f"(design/ro_array_core.spice)",
            file=sys.stderr,
        )
        return 2

    a_derived, a_note = derived_law_constant()
    need = MARGIN_M * Q_H0
    print(f"DR-0007 §2 requires Q_array >= M * Q_H0 = {MARGIN_M} * {Q_H0:g} = {need:g}")
    print(f"evaluated at a raw rate of {args.rate:g} bps (T_s = {1/args.rate:.4g} s)")
    print(
        f"sizing constant a = {A_JITTER_ENERGY:g}; jitter_energy_law.py {a_note}\n"
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
        if a_derived is None:
            print(
                f"\nFAIL: the sizing constant a = {A_JITTER_ENERGY:g} {a_note}",
                file=sys.stderr,
            )
            return 2
        drift = abs(a_derived - A_JITTER_ENERGY) / A_JITTER_ENERGY
        if drift > A_TOLERANCE:
            print(
                f"\nFAIL: A_JITTER_ENERGY = {A_JITTER_ENERGY:g} has drifted {drift:.1%} "
                f"from the {a_derived:.3f} sim/tools/jitter_energy_law.py now derives "
                f"(tolerance {A_TOLERANCE:.0%}). The constant is not the thing to edit "
                f"on its own: DR-0008 §3's arithmetic and every rate figure quoted from "
                f"it move with it.",
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
            f"\nOK: a = {A_JITTER_ENERGY:g} is within {A_TOLERANCE:.0%} of the derivation "
            f"({drift:.1%} off), and DR-0007 §2 holds at every measured corner at "
            f"{args.rate:g} bps."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
