#!/usr/bin/env python3
"""Derive the jitter-energy invariant from committed evidence records.

    python3 sim/tools/jitter_energy_law.py            # print the 27-point table
    python3 sim/tools/jitter_energy_law.py --check    # assert the invariant holds

This is a *derivation*, not a simulation: it reads only records already
committed under ``sim/records/`` and does arithmetic on them. It needs
neither ngspice nor the PDK, and it writes nothing.

What it derives
---------------
For a ring oscillator whose phase performs a random walk, the accumulated
jitter over an interval ``t`` is ``sigma_acc^2(t) = kappa^2 * t``, with

    kappa^2 = sigma_1^2 / T0                         (per-ring, units of s)

Classical ring-oscillator noise theory (Hajimiri/Lee; McNeill) says that
``kappa^2`` and the ring's *power* are not independent -- to first order
their product is set by temperature alone:

    a  =  kappa^2 * P / (kB * T)      ~ a dimensionless constant

This script evaluates ``a`` at every point of the candidate-A 5-stage grid
this repository has already measured, by combining three record families
that cover the *same* 27 PVT points:

  * ``2026-07-31-ro-inv-05stage-jitter-NN``   -> ``sigma_1`` (raw, at the
    fixed injected noise level) and the period,
  * ``2026-07-31-inv-stage-noise-NN``         -> ``inoise_dens_1g``, the
    per-corner device-noise density used to scale the fixed injection to a
    physical one (the same 1 GHz-proxy scaling
    ``sim/characterization-ro-delay-cell-jitter.md`` defines),
  * ``2026-08-01-ro-inv-05stage-power-NN``    -> ``p_active_w`` and
    ``c_eff_node_f``.

If ``a`` is in fact constant across that grid, then ``kappa^2`` -- and
therefore the entropy a ring delivers -- is fixed by the ring's power
budget and is *not* a free design variable. That is the premise DR-0010
rests on, so it is checkable here rather than asserted there.

Accuracy inherited from the inputs
----------------------------------
``sigma_1`` is a fixed-injection figure scaled by a single-frequency proxy
for the device noise density; ``sim/characterization-ro-delay-cell-jitter.md``
states that scaling is good to a factor of ~1.5-2x on sigma. Everything
here inherits that. The *constancy* of ``a`` across the grid is a much
stronger result than its absolute value, because the scaling error is
largely common-mode across corners.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _record_parsing import format_corner, parse_corner, parse_values  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"

KB = 1.380649e-23  # J/K, CODATA

#: The fixed per-stage injected noise density the jitter testbenches use,
#: in V/sqrt(Hz). See sim/tb/ro-inv-05stage-jitter/tb.json ``noise_params``.
INJECTED_DENSITY = 1.0e-8

JITTER = "2026-07-31-ro-inv-05stage-jitter-{nn:02d}"
STAGE_NOISE = "2026-07-31-inv-stage-noise-{nn:02d}"
POWER = "2026-08-01-ro-inv-05stage-power-{nn:02d}"
GRID_POINTS = range(1, 28)

#: The invariant's acceptable spread, max/min over the grid. Chosen with
#: headroom over the 1.29x actually observed, so this fails on a real
#: regression (a record family replaced with an inconsistent one) rather
#: than on arithmetic noise.
MAX_SPREAD = 1.60


class RecordError(RuntimeError):
    pass


def read_record(stem: str) -> tuple[dict[str, float], dict[str, object]]:
    path = RECORDS / f"{stem}.md"
    if not path.is_file():
        raise RecordError(f"no such record: sim/records/{stem}.md")
    text = path.read_text()
    values = parse_values(text)
    process, temp_c, vdd = parse_corner(text, label=stem, error_cls=RecordError)
    corner = {"process": process, "temp_c": temp_c, "vdd": vdd}
    return values, corner


class Point:
    def __init__(self, nn: int) -> None:
        jitter, corner = read_record(JITTER.format(nn=nn))
        noise, _ = read_record(STAGE_NOISE.format(nn=nn))
        power, power_corner = read_record(POWER.format(nn=nn))
        if (power_corner["process"], power_corner["temp_c"]) != (
            corner["process"],
            corner["temp_c"],
        ):
            raise RecordError(
                f"grid point {nn:02d} is not the same corner in the jitter and "
                f"power record families: {corner} vs {power_corner}"
            )
        self.nn = nn
        self.corner = format_corner(corner["process"], corner["temp_c"], corner["vdd"])
        self.temp_k = corner["temp_c"] + 273.15
        #: per-corner scaling of the fixed injection to the device's own
        #: high-frequency noise density (the 1 GHz proxy).
        self.scale = noise["inoise_dens_1g"] / INJECTED_DENSITY
        self.sigma_1 = jitter["sigma_1"] * self.scale
        self.period = power["period"]
        self.power_w = power["p_active_w"]
        self.c_eff_f = power["c_eff_node_f"]
        #: random-walk rate constant: sigma_acc^2(t) = kappa2 * t
        self.kappa2 = self.sigma_1**2 / self.period
        self.a = self.kappa2 * self.power_w / (KB * self.temp_k)

    def q(self, t_s: float) -> float:
        """DR-0007 §2's per-ring Q at sample period ``t_s``."""
        return self.kappa2 * t_s / self.period**2


def grid_points() -> list[Point]:
    """Every point of the candidate-A grid this repository has measured."""
    return [Point(nn) for nn in GRID_POINTS]


def derive_a(points: list[Point] | None = None) -> tuple[float, float, float]:
    """``(mean, min, max)`` of ``a = kappa^2 * P / (kB * T)`` over that grid.

    This function is the single source of truth for the constant DR-0010 calls
    ``a``. ``sim/tools/array_sizing.py`` sizes the array against a *stated*
    value of it (so that the numbers quoted in DR-0010 and the README do not
    shift under them every time a record is appended), and its ``--check``
    re-runs this derivation and fails if the two have drifted apart. Raises
    :class:`RecordError` if the record families it reads are incomplete.
    """
    values = [p.a for p in (points if points is not None else grid_points())]
    return statistics.mean(values), min(values), max(values)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="jitter_energy_law.py",
        description="Derive kappa^2 * P / (kB T) from committed evidence records.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=f"exit non-zero if the invariant's spread exceeds {MAX_SPREAD}x",
    )
    parser.add_argument(
        "--sample-period",
        type=float,
        default=1e-6,
        metavar="T_S",
        help="sample period for the reported per-ring Q (default 1e-6 s = 1 Mbps)",
    )
    args = parser.parse_args(argv)

    try:
        points = grid_points()
    except RecordError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    header = (
        f"{'NN':>3}  {'corner':<15} {'T0 (s)':>11} {'sigma_1 (s)':>12} "
        f"{'P (W)':>11} {'kappa^2 (s)':>12} {'a':>6} {'Q':>10}"
    )
    print(f"candidate-A 5-stage grid, Q at T_s = {args.sample_period:g} s\n")
    print(header)
    print("-" * len(header))
    for p in points:
        print(
            f"{p.nn:>3}  {p.corner:<15} {p.period:11.4e} {p.sigma_1:12.4e} "
            f"{p.power_w:11.4e} {p.kappa2:12.4e} {p.a:6.3f} {p.q(args.sample_period):10.3e}"
        )

    values = [p.a for p in points]
    mean_a, min_a, max_a = derive_a(points)
    spread = max_a / min_a
    worst = min(points, key=lambda p: p.q(args.sample_period))
    print()
    print(
        f"a = kappa^2 P / (kB T):  mean {mean_a:.3f}   "
        f"min {min_a:.3f}   max {max_a:.3f}   "
        f"sd {statistics.pstdev(values):.3f}   spread {spread:.2f}x"
    )
    print(
        f"  over a grid on which P itself spans "
        f"{max(p.power_w for p in points) / min(p.power_w for p in points):.2f}x and "
        f"kappa^2 spans "
        f"{max(p.kappa2 for p in points) / min(p.kappa2 for p in points):.2f}x"
    )
    print(
        f"minimum-Q (entropy-binding) corner: {worst.corner} "
        f"(Q = {worst.q(args.sample_period):.3e}, record {worst.nn:02d})"
    )

    if args.check:
        if spread > MAX_SPREAD:
            print(
                f"\nFAIL: invariant spread {spread:.2f}x exceeds {MAX_SPREAD}x -- "
                "the jitter, stage-noise and power record families no longer agree.",
                file=sys.stderr,
            )
            return 1
        print(f"\nOK: invariant spread {spread:.2f}x is within {MAX_SPREAD}x.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
