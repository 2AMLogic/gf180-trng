#!/usr/bin/env python3
"""Derive the jitter-energy invariant ``a`` for the SHIPPED starved delay cell.

    python3 sim/tools/starved_cell_jitter_energy.py          # the table
    python3 sim/tools/starved_cell_jitter_energy.py --check   # gate the method

Like ``sim/tools/jitter_energy_law.py`` this is a *derivation*, not a
simulation: it reads only records already committed under ``sim/records/`` and
does arithmetic on them. It needs neither ngspice nor the PDK, and it writes
nothing.

Why it exists (issue #46)
-------------------------
DR-0010's rate row rests on

    a  =  kappa^2 * P_ring / (k_B * T)   =   1.79 +/- 0.14              (*)

fitted by ``jitter_energy_law.py`` to a **plain, unstarved** 5-stage inverter
ring over the 27-point candidate-A grid. The cell this project ships is a
minimum-width, series-**starved** inverter, and DR-0010 names the gap between
the two as its own largest open risk. This script closes the arithmetic half of
that gap: it evaluates the same ``a`` for the starved cell, from the long-window
transient-noise records ``sim/tb/ro-ring5-starved-jitter-long/`` produces, and
states the ratio to ``(*)``.

The two things it checks about the *method*, not the circuit
------------------------------------------------------------
The measurement this replaces
(``sim/records/2026-08-01-ro-array-sanity-jitter-01.md``) produced a plausible
looking ``sigma`` that was start-up settling drift rather than jitter. Two
diagnostics caught it, and both are computed here for every record so the same
mistake cannot pass silently a second time:

* **Seed spread.** A ``sigma`` estimate from a finite window is itself a random
  variable, and its seed-to-seed scatter scales as ``sqrt(L / NP)`` for lag
  ``L`` over ``NP`` periods. The *absolute* scale of that scatter is NOT taken
  from a formula here. ``sqrt(L / (2 NP))`` -- the textbook standard error of a
  standard deviation from ``NP/L`` independent increments -- is only an upper
  bound, because these estimators use all ``NP-L`` **overlapping** increments
  rather than ``NP/L`` disjoint ones. So the reference is taken from the
  plain-cell records this repository has already committed
  (``2026-07-31-ro-inv-05stage-jitter-*``: 128-period window, 4 seeds each,
  lag-1 spread 5.4 % against the 6.3 % the formula predicts) and rescaled by
  ``sqrt(NP_ref / NP)``. Both the empirical reference and the analytic bound are
  printed; ``--check`` gates on the empirical one.

  The run this family replaces varied **0.3 %** at lag 1 over a 16-period
  window, where the empirical reference predicts ~15 %. That is not a tight
  measurement, it is every seed tracing the same deterministic settling curve.
* **Accumulation exponent.** A phase random walk gives
  ``sigma_acc(L) ~ L^0.5``. Deterministic drift gives ``L^1``. The sanity run
  came back at ``L^0.81``.

Both are reported per record; ``--check`` gates on the first only. The exponent
is deliberately **not** gated: a starved ring whose accumulation genuinely
departs from ``L^0.5`` is a finding this repository wants recorded, not a build
failure (issue #46 acceptance criterion 4).

kappa^2, two ways, and why the difference matters
-------------------------------------------------
``jitter_energy_law.py`` takes ``kappa^2 = sigma_1^2 / T0`` -- the lag-1 figure
-- because on the plain cell the accumulation is clean ``sqrt(t)`` and every lag
gives the same answer. That is not guaranteed for a starved cell, whose series
starve devices give the ring a memory longer than one period. So this script
reports **both**:

* ``kappa2_lag1``  -- ``sigma_1^2 / T0``, like-for-like with ``(*)``;
* ``kappa2_asym``  -- a zero-intercept least-squares slope of
  ``sigma_acc^2`` against elapsed time over the **largest** lags measured.

DR-0007 §2 extrapolates ``sigma_acc`` to a sample period thousands of periods
long, so ``kappa2_asym`` is the one that governs the entropy claim; ``kappa2_lag1``
is the one that is comparable with the plain-cell grid. Where they disagree,
that disagreement is the result, and it is printed rather than averaged away.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from jitter_energy_law import KB, INJECTED_DENSITY, derive_a  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"

#: The long-window starved-cell family this script reads.
JITTER_GLOB = "*-ro-ring5-starved-jitter-long-*.md"
#: The per-corner device-noise record that scales the fixed injection to a
#: physical one, exactly as jitter_energy_law.py does for the plain cell.
NOISE_GLOB = "*-rostage-noise-*.md"
#: The plain-cell family the seed-spread reference is calibrated against. It is
#: the same family jitter_energy_law.py fits ``a`` to, measured with the same
#: estimator over a 128-period window.
PLAIN_GLOB = "2026-07-31-ro-inv-05stage-jitter-*.md"

#: Periods in the measurement window and periods discarded before it opens.
#: Read off the testbench rather than assumed -- see ``window_geometry``.
TB_MANIFEST = REPO_ROOT / "sim" / "tb" / "ro-ring5-starved-jitter-long" / "tb.json"
PLAIN_TB_MANIFEST = REPO_ROOT / "sim" / "tb" / "ro-inv-05stage-jitter" / "tb.json"

#: ``--check`` tolerance on the seed-spread diagnostic: the measured lag-1
#: spread must be within this factor of the plain-cell family's own lag-1
#: spread rescaled to this window length, in EITHER direction. Three is
#: deliberately generous -- with 8 seeds the sample standard deviation itself
#: carries ~27 % uncertainty, and the reference is itself an 4-seed estimate --
#: and still rejects the ~30x-too-tight signature of the run this family
#: replaces.
SPREAD_TOLERANCE = 3.0

_MEAN = re.compile(
    r"^- `([a-z0-9_]+)`:\s*mean\s+(-?[\d.]+(?:e[-+]?\d+)?)\s+over\s+(\d+)\s+seeds"
    r"\s*\(sd\s+(-?[\d.]+(?:e[-+]?\d+)?)",
    re.M,
)
_SINGLE = re.compile(r"^- `([a-z0-9_]+)`:\s*(-?[\d.]+(?:e[-+]?\d+)?)\s*$", re.M)


class RecordError(RuntimeError):
    pass


class Record:
    """One committed evidence record, with its per-seed spread preserved."""

    def __init__(self, path: Path) -> None:
        text = path.read_text()
        self.path = path
        self.stem = path.stem
        self.values: dict[str, float] = {}
        self.sd: dict[str, float] = {}
        self.seeds = 1
        for m in _SINGLE.finditer(text):
            self.values[m.group(1)] = float(m.group(2))
        for m in _MEAN.finditer(text):
            self.values[m.group(1)] = float(m.group(2))
            self.seeds = int(m.group(3))
            self.sd[m.group(1)] = float(m.group(4))
        self.process = self._field(text, r"process:\s*(\w+)")
        self.temp_c = float(self._field(text, r"temperature:\s*(-?[\d.]+)"))
        self.vdd = float(self._field(text, r"voltage:\s*([\d.]+)"))
        self.temp_k = self.temp_c + 273.15

    def _field(self, text: str, pattern: str) -> str:
        m = re.search(pattern, text)
        if m is None:
            raise RecordError(f"{self.stem}: cannot find {pattern!r} in the frontmatter")
        return m.group(1)

    @property
    def corner(self) -> str:
        return f"{self.process}/{self.temp_c:.0f}/{self.vdd:.2f}"

    def spread(self, key: str) -> float | None:
        """Relative seed-to-seed standard deviation of ``key``, or None."""
        if key not in self.sd or not self.values.get(key):
            return None
        return self.sd[key] / abs(self.values[key])


def window_geometry(manifest_path: Path = TB_MANIFEST) -> tuple[int, int]:
    """``(periods discarded before the window, periods in the window)``.

    Parsed out of the testbench manifest so the diagnostics below cannot go
    stale against a testbench that was re-tuned.
    """
    import json

    manifest = json.loads(manifest_path.read_text())
    m = re.search(r"tbar = \(tc\[(\d+)\] - tc\[(\d+)\]\)/(\d+)", "\n".join(manifest["analyses"]))
    if m is None:
        raise RecordError(f"{manifest_path}: cannot find the window definition")
    return int(m.group(2)), int(m.group(3))


def analytic_spread(lag: int, n_periods: int) -> float:
    """Textbook standard error of a ``sigma`` estimate at ``lag`` over a window
    of ``n_periods`` periods, treating the increments as ``n_periods/lag``
    independent draws: the standard error of a standard deviation from ``m``
    samples is ``1/sqrt(2m)``.

    This is an **upper bound**, not the expectation. The estimators here use
    all ``n_periods - lag`` overlapping increments, which is strictly more
    information than the ``n_periods/lag`` disjoint ones this assumes -- on the
    committed plain-cell family it overestimates the observed scatter ~2x. Use
    :func:`reference_spread` for the number to compare a measurement against;
    this one is printed to show how much of the gap is method and how much is
    the circuit.
    """
    return math.sqrt(lag / (2.0 * n_periods))


def reference_spread(lag: int, n_periods: int) -> tuple[float, int, int]:
    """Seed-to-seed spread a *genuine* ``sigma_<lag>`` estimate shows over
    ``n_periods`` periods, calibrated on committed evidence.

    Returns ``(spread, number of reference records, reference window length)``.

    Method: take the mean relative seed spread of ``sigma_<lag>`` over the
    plain-cell 5-stage family (``PLAIN_GLOB``), whose window length is read
    from its own manifest, and rescale by ``sqrt(NP_ref / n_periods)``. The
    scaling exponent is the only assumption -- the estimator's scatter is
    ``propto sqrt(lag / NP)`` whatever the overlap factor is, and the overlap
    factor is exactly what the empirical reference absorbs.

    Calibrating against the plain cell rather than the starved one is
    deliberate: the reference must not be derived from the very records the
    check is judging.
    """
    _, ref_periods = window_geometry(PLAIN_TB_MANIFEST)
    spreads = []
    for path in sorted(RECORDS.glob(PLAIN_GLOB)):
        rec = Record(path)
        got = rec.spread(f"sigma_{lag}")
        if got is not None:
            spreads.append(got)
    if not spreads:
        raise RecordError(
            f"no sim/records/{PLAIN_GLOB} record carries a sigma_{lag} seed spread, so "
            "the seed-spread diagnostic has nothing to calibrate against"
        )
    ref = sum(spreads) / len(spreads)
    return ref * math.sqrt(ref_periods / n_periods), len(spreads), ref_periods


def _lags(rec: Record, prefix: str = "sigma_") -> list[int]:
    out = []
    for key in rec.values:
        m = re.fullmatch(prefix + r"(\d+)", key)
        if m:
            out.append(int(m.group(1)))
    return sorted(out)


def _loglog_slope(xs: list[float], ys: list[float]) -> float:
    lx = [math.log(x) for x in xs]
    ly = [math.log(y) for y in ys]
    n = len(lx)
    mx, my = sum(lx) / n, sum(ly) / n
    num = sum((a - mx) * (b - my) for a, b in zip(lx, ly))
    den = sum((a - mx) ** 2 for a in lx)
    return num / den


class Point:
    """One PVT point of the starved cell: jitter, power and noise density."""

    def __init__(self, jitter: Record, noise: Record, discarded: int, n_periods: int) -> None:
        self.rec = jitter
        self.noise = noise
        self.discarded = discarded
        self.n_periods = n_periods
        #: per-corner scaling of the fixed injection to the device's own
        #: high-frequency noise density (the same 1 GHz proxy
        #: jitter_energy_law.py uses for the plain cell).
        self.scale = noise.values["inoise_dens_1g"] / INJECTED_DENSITY
        self.period = jitter.values["period"]
        self.power_w = jitter.values["p_active_w"]
        self.lags = _lags(jitter)
        #: sigma_acc at each measured lag, scaled to a physical noise density
        self.sigma = {L: jitter.values[f"sigma_{L}"] * self.scale for L in self.lags}

        self.exponent = _loglog_slope(
            [float(L) for L in self.lags], [self.sigma[L] for L in self.lags]
        )
        big = [L for L in self.lags if L >= max(self.lags) // 8]
        self.exponent_tail = _loglog_slope(
            [float(L) for L in big], [self.sigma[L] for L in big]
        )

        self.kappa2_lag1 = self.sigma[1] ** 2 / self.period
        #: zero-intercept least-squares slope of sigma_acc^2 against elapsed
        #: time, over the top decade of lag actually measured.
        num = sum(L * self.period * self.sigma[L] ** 2 for L in big)
        den = sum((L * self.period) ** 2 for L in big)
        self.kappa2_asym = num / den
        self.tail_lags = big

        # the 16-period, opened-at-start-up window the sanity run used,
        # reproduced inside the SAME run for a like-for-like comparison.
        s_lags = _lags(jitter, "sigma_startup16_")
        self.startup_lags = s_lags
        self.startup_sigma = {
            L: jitter.values[f"sigma_startup16_{L}"] * self.scale for L in s_lags
        }
        self.startup_exponent = (
            _loglog_slope([float(L) for L in s_lags], [self.startup_sigma[L] for L in s_lags])
            if len(s_lags) > 1
            else float("nan")
        )
        self.startup_kappa2 = (
            self.startup_sigma[1] ** 2 / jitter.values["period_startup16"] if s_lags else float("nan")
        )

    def a(self, kappa2: float) -> float:
        return kappa2 * self.power_w / (KB * self.rec.temp_k)

    @property
    def period_drift_ppm(self) -> float:
        """Peak-to-peak spread of the per-block mean period, in ppm of the
        window mean -- the record's own evidence that the period has stopped
        drifting before (and during) the measurement window."""
        blocks = [v for k, v in self.rec.values.items() if re.fullmatch(r"period_b\d+", k)]
        if not blocks:
            return float("nan")
        return 1e6 * (max(blocks) - min(blocks)) / self.period

    @property
    def measured_spread_1(self) -> float | None:
        return self.rec.spread("sigma_1")


def load_points() -> list[Point]:
    jitter = [Record(p) for p in sorted(RECORDS.glob(JITTER_GLOB))]
    if not jitter:
        raise RecordError(f"no sim/records/{JITTER_GLOB} records found")
    noise = {r.corner: r for r in (Record(p) for p in sorted(RECORDS.glob(NOISE_GLOB)))}
    discarded, n_periods = window_geometry()
    points = []
    for rec in jitter:
        n = noise.get(rec.corner)
        if n is None:
            raise RecordError(
                f"{rec.stem}: no {NOISE_GLOB} record at {rec.corner}, so the fixed "
                "injection cannot be scaled to this corner's device-noise density"
            )
        points.append(Point(rec, n, discarded, n_periods))
    return points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="starved_cell_jitter_energy.py",
        description="Derive a = kappa^2 P / (kB T) for the shipped starved delay cell.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if any record's seed spread is inconsistent with its "
        "window length (the settling-drift signature this family exists to avoid)",
    )
    args = parser.parse_args(argv)

    try:
        points = load_points()
        a_plain, a_lo, a_hi = derive_a()
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    discarded, n_periods = window_geometry()
    print(
        f"shipped starved cell, 5-stage ring, window = {n_periods} periods opened "
        f"{discarded} periods after start-up\n"
        f"plain-cell reference (sim/tools/jitter_energy_law.py): "
        f"a = {a_plain:.3f} (min {a_lo:.3f}, max {a_hi:.3f})\n"
    )

    header = (
        f"{'corner':<15} {'T0 (s)':>11} {'P (W)':>11} {'sig_1 (s)':>11} "
        f"{'expon':>6} {'tail':>6} {'kap2_lag1':>11} {'kap2_asym':>11} "
        f"{'a_lag1':>8} {'a_asym':>8}"
    )
    print(header)
    print("-" * len(header))
    for p in points:
        print(
            f"{p.rec.corner:<15} {p.period:11.4e} {p.power_w:11.4e} {p.sigma[1]:11.4e} "
            f"{p.exponent:6.3f} {p.exponent_tail:6.3f} {p.kappa2_lag1:11.4e} "
            f"{p.kappa2_asym:11.4e} {p.a(p.kappa2_lag1):8.3f} {p.a(p.kappa2_asym):8.3f}"
        )

    print("\naccumulation (sigma_acc, s; scaled to the corner's device-noise density)")
    lags = points[0].lags
    print("  " + f"{'corner':<15}" + "".join(f"{'L=' + str(L):>11}" for L in lags))
    for p in points:
        print("  " + f"{p.rec.corner:<15}" + "".join(f"{p.sigma[L]:11.4e}" for L in lags))
    print("  " + f"{'sqrt(L) x sig_1':<15}" + "".join(
        f"{points[0].sigma[1] * math.sqrt(L):11.4e}" for L in lags
    ))

    print("\nmethod diagnostics (issue #46)")
    ref_1, ref_n, ref_periods = reference_spread(1, n_periods)
    ana_1 = analytic_spread(1, n_periods)
    print(
        f"  seed-spread reference at lag 1: {100 * ref_1:.2f}%  (mean over {ref_n} "
        f"plain-cell {PLAIN_GLOB} records at a {ref_periods}-period window, rescaled "
        f"by sqrt({ref_periods}/{n_periods}))\n"
        f"  analytic upper bound sqrt(1/(2*{n_periods})): {100 * ana_1:.2f}%"
    )
    print(
        f"  {'corner':<15} {'blk drift':>10} {'spread_1':>9} {'ref':>9} "
        f"{'ratio':>7} {'16-per a':>9} {'16-per expon':>13}"
    )
    ok = True
    for p in points:
        got = p.measured_spread_1
        ratio = (got / ref_1) if got else float("nan")
        if got is None or not (1 / SPREAD_TOLERANCE <= ratio <= SPREAD_TOLERANCE):
            ok = False
        print(
            f"  {p.rec.corner:<15} {p.period_drift_ppm:9.1f}p {100 * (got or 0):8.2f}% "
            f"{100 * ref_1:8.2f}% {ratio:7.2f} {p.a(p.startup_kappa2):9.3f} "
            f"{p.startup_exponent:13.3f}"
        )
    print(
        "  'blk drift' is the peak-to-peak spread of the per-block mean period, in ppm.\n"
        "  '16-per' columns are the SAME run measured the way the superseded sanity\n"
        "  run measured it: 16 periods, window opened at the second edge."
    )

    mean_lag1 = sum(p.a(p.kappa2_lag1) for p in points) / len(points)
    mean_asym = sum(p.a(p.kappa2_asym) for p in points) / len(points)
    print(
        f"\na (lag-1, like-for-like with (*)): mean {mean_lag1:.3f} over "
        f"{len(points)} corners  ->  {mean_lag1 / a_plain:.2f}x the plain cell's {a_plain:.2f}"
    )
    print(
        f"a (asymptotic slope over lags {points[0].tail_lags}): mean {mean_asym:.3f}  ->  "
        f"{mean_asym / a_plain:.2f}x the plain cell's {a_plain:.2f}"
    )

    if args.check:
        if not ok:
            print(
                f"\nFAIL: at least one record's lag-1 seed spread is more than "
                f"{SPREAD_TOLERANCE:g}x away from the {100 * ref_1:.2f}% a genuine "
                f"{n_periods}-period estimate shows. A spread far BELOW the reference "
                "is the settling-drift signature of "
                "sim/records/2026-08-01-ro-array-sanity-jitter-01.md; far above it "
                "means something other than stationary jitter is in the window.",
                file=sys.stderr,
            )
            return 1
        print(
            f"\nOK: every record's lag-1 seed spread is within {SPREAD_TOLERANCE:g}x of "
            f"the {100 * ref_1:.2f}% a genuine {n_periods}-period estimate shows."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
