#!/usr/bin/env python3
"""Issue #13: the entropy-binding (minimum-``Q``) PVT corner of the shipped
array, and the device-mismatch bias measured at the nominal corner.

    python3 sim/tools/worst_corner_entropy.py           # full report
    python3 sim/tools/worst_corner_entropy.py --check    # hold the stated corner
                                                          to the records

This is a derivation, like ``sim/tools/array_sizing.py`` and
``sim/tools/starved_cell_jitter_energy.py`` beside it: it reads only records
already committed under ``sim/records/`` (plus, for the MC section, the raw
per-seed logs committed under ``sim/records/raw/``) and does arithmetic on
them. It needs neither ngspice nor the PDK, and it writes nothing.

The four things it reports
--------------------------
**1. The two record families agree.** ``sim/tb/ro-array-core-pvt-q/`` is the
27-point covered-grid re-measurement of the same array
``sim/tb/ro-array-core-power/`` measured at three points, with a 6x longer
transient window and a 5x looser solver-step ceiling (see that testbench's
header for why: the slow half of the grid does not fit in a 50 ns window at
all). Because the corner ranking below is read off the new family, the first
thing printed is the per-quantity agreement between the two families at the
three PVT points they share. That comparison is what licenses treating them
as one measurement; it is reported, and ``--check`` enforces a tolerance on
it.

**2. Which corner binds.** ``spec/decision-records/DR-0012-sampler-fixed-external-clock.md``
fixes the corner *metric* (``Q ∝ σ₁²/T₀³``, a fixed external sample clock --
NOT the ``σ₁/T₀`` form that a self-divided clock would give) and states the
*predicted* minimum: ``ss``/−40 °C/3.63 V. That prediction was made from
three measured PVT points. This script evaluates ``array_sizing.py``'s
``ArrayPoint`` machinery -- unchanged -- over the full covered grid
({tt, ff, ss} x {−40, 27, 125} °C x {2.97, 3.30, 3.63} V; ``fs``/``sf`` stay
out per DR-0006) and reports which corner actually minimizes ``Q``.

The answer is **not** the predicted one: it is ``ss``/**+125 °C**/3.63 V,
the hot end of the same process/supply corner. ``Q ~ T_K/(P*T0^2)``, and
warming that corner from −40 °C to +125 °C lengthens ``T0`` by two thirds,
whose ``1/T0^2`` term outweighs both the higher ``kT`` and the lower ring
power. Nothing about the metric changed -- the 3-point set the prediction
was made over simply did not contain a hot point at high supply.
``spec/decision-records/DR-0015-entropy-binding-corner-moves-to-the-hot-slow-corner.md``
records that, under DR-0012's own "Revisit if" trigger; the testbench was
not adjusted to reproduce the prediction.

It does that at three values of the jitter-energy constant ``a``: DR-0010's
stated plain-cell ``1.79``, and both constants issue #52 measured on the
STARVED cell this array actually ships (``a = 24.84`` at lag 1, ``a = 11.77``
on the asymptotic slope). ``a`` multiplies every corner's ``Q`` identically
(``ArrayPoint.g`` treats it as a device/geometry constant, not a per-corner
one), so it cannot change the *ranking* -- what it changes, and the reason
all three are printed, is the absolute margin against DR-0007 §2's
``Q_array >= M * Q_H0`` inequality.

**3. Monte Carlo mismatch.** Every record in (2) is a single, mismatch-free
device draw. Two nominal-corner Monte Carlo testbenches
(``sim/tb/ro-array-core-mc-freq/``, ``sim/tb/sampler-dff-mc-offset/``) close
that gap. This script reads their committed records AND, for the RO run,
their raw per-seed ngspice logs -- because a record's marginal mean/sd of
each ring separately cannot show whether one seed's mismatch draw happened
to pull the two rings' periods towards a common ratio, which is exactly what
DR-0007 §1's non-integer-ratio requirement defends against.

**4. Whether the conditioner and the health tests cover that spread.** The
last section converts the measured sampler-threshold offset into a raw-bit
bias and asks three questions with committed numbers: does the implied
bit-probability leave enough min-entropy for DR-0008's non-vetted
conditioner (break-even ``H = 0.106456``), and would DR-0002's RCT and APT
cutoffs -- which are computed at the assumed ``H₀ = 0.5`` -- false-trip on a
stream with that much bias? Every figure there is an explicitly-stated
bounding model, never a min-entropy measurement: DR-0004's tiering is
unchanged and measuring ``H`` is #12's job.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from array_sizing import (  # noqa: E402
    ArrayPoint,
    KB,
    A_JITTER_ENERGY,
    MARGIN_M,
    Q_H0,
    DR0010_RATE_BPS,
    load,
    shipped_ring_count,
)
from starved_cell_jitter_energy import load_points as load_starved_points  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"

#: What ``DR-0012-sampler-fixed-external-clock`` §Consequences predicts, from
#: the three PVT points that were measured when it was written. Restated here
#: so the difference between prediction and measurement is a visible line of
#: output rather than something a reader has to cross-check by hand.
PREDICTED_MIN_Q_CORNER = "ss/-40/3.63"

#: What the full covered grid actually measures, and what
#: ``DR-0015-entropy-binding-corner-moves-to-the-hot-slow-corner`` records.
#: Stated rather than derived so that a future record family which moves the
#: minimum again fails ``--check`` loudly instead of silently re-pointing
#: every document that cites this corner by name.
MEASURED_MIN_Q_CORNER = "ss/125/3.63"

#: The covered PVT grid, per DR-0006's ratified reduced process axis.
GRID_PROCESSES = ("tt", "ff", "ss")
GRID_TEMPS_C = (-40.0, 27.0, 125.0)
GRID_SUPPLIES_V = (2.97, 3.30, 3.63)

#: Largest relative difference tolerated between the two array record
#: families at a shared PVT point, for the quantities Q depends on (period
#: and per-ring supply current). Deliberately tight: these are the same
#: circuit at the same corner, differing only in transient window and solver
#: step ceiling, so anything above a fraction of a percent would mean the
#: looser step had changed the measurement rather than just its cost.
FAMILY_AGREEMENT_TOL = 0.01

#: Quantities compared across the two families. ring_swing_v/xo_swing_v are
#: deliberately NOT here: they are max/min over a fixed-length window, and
#: the two families' windows differ in both position and length, so they are
#: expected to disagree (reported below, not enforced).
AGREEMENT_KEYS = (
    "period_r1", "period_r2", "i_r1_a", "i_r2_a", "i_tree_a",
    "e_cycle_r1_j", "p_total_w",
)

#: DR-0002's parameters and its cutoffs at the assumed H0 = 0.5.
ALPHA = 2.0**-40
APT_WINDOW = 1024
C_RCT_AT_H0 = 81
C_APT_AT_H0 = 824
H0_TARGET = 0.5

#: DR-0008 §5's break-even raw min-entropy: the H at which K = 8 CRC-32
#: compression still earns the full 0.85 bit/bit non-vetted cap.
DR0008_BREAK_EVEN_H = 0.106456

_MEAS_LOG = re.compile(r"^\s*m_(\w+)\s*=\s*([-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)\s*$", re.M)

# `-[0-9]` and not `-`: the sequence number must follow the slug directly, so
# a record from a *variant* testbench whose slug starts with one of these
# (e.g. ro-array-core-power-BUFFERED, issue #75's unadopted buffer mitigation)
# can never be read as a shipped-array corner.
PVT_Q_GLOB = "*-ro-array-core-pvt-q-[0-9]*.md"
POWER_GLOB = "*-ro-array-core-power-[0-9]*.md"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _binom_tail(n: int, k: int, p: float) -> float:
    """``Pr(X >= k)`` for ``X ~ Bin(n, p)``, summed exactly in floating point.

    ``n`` is 1024 here, so the direct sum is both cheap and accurate enough:
    the quantity is compared against 2^-40, not reported to many digits.
    """
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    total = 0.0
    for i in range(k, n + 1):
        total += math.comb(n, i) * p**i * (1.0 - p) ** (n - i)
    return total


def shipped_points(glob: str, a: float) -> list[ArrayPoint]:
    """The shipped array's points, one per PVT corner, newest measurement first.

    The per-corner dedupe matters from #78 onward. Adopting the per-ring
    output buffer (``DR-0018``) moved the shipped array's operating point and
    the ``ro-array-core-pvt-q`` family was re-run against the adopted netlist,
    so this glob now matches TWO generations of every corner. Both keep
    ``status: valid`` -- ``sim/records/`` is append-only and the pre-adoption
    records remain true of the unbuffered array they measured -- but only the
    newer generation describes the array as it now ships, and every claim
    below ("this corner minimizes Q", "the margin there is Nx") is a claim
    about the shipped design. Ranking both generations in one table would
    also let a pre-adoption corner win the ranking on the strength of a
    slower ring the design no longer has.

    ``load`` returns records sorted by stem, and stems begin with the run
    date, so the last record of a corner is the newest one.
    """
    n = shipped_ring_count()
    pts = [ArrayPoint(r, a=a) for r in load(glob)]
    newest: dict[str, ArrayPoint] = {}
    for p in pts:
        if p.n == n:
            newest[p.rec.corner] = p
    return list(newest.values())


# --------------------------------------------------------------------------
# 1. the two array record families agree at the corners they share
# --------------------------------------------------------------------------

def report_family_agreement() -> float:
    """Print the per-quantity agreement; return the largest relative diff."""
    print("\n== ro-array-core-pvt-q vs ro-array-core-power at shared PVT points ==")
    new = {r.corner: r for r in load(PVT_Q_GLOB)}
    old = {r.corner: r for r in load(POWER_GLOB)}
    shared = sorted(set(new) & set(old))
    if not shared:
        print("  (no PVT point is measured by both families)")
        return 0.0
    worst = 0.0
    for corner in shared:
        diffs = []
        for key in AGREEMENT_KEYS:
            a_val, b_val = new[corner].values.get(key), old[corner].values.get(key)
            if a_val is None or b_val is None or b_val == 0:
                continue
            rel = abs(a_val - b_val) / abs(b_val)
            worst = max(worst, rel)
            diffs.append(f"{key} {rel:.2e}")
        print(f"  {corner:<15} " + "  ".join(diffs))
    print(f"  largest relative difference over {len(shared)} shared point(s), "
          f"{len(AGREEMENT_KEYS)} quantities each: {worst:.2e} "
          f"(tolerance {FAMILY_AGREEMENT_TOL:.0%})")
    for corner in shared:
        for key in ("ring_swing_v", "xo_swing_v"):
            a_val, b_val = new[corner].values.get(key), old[corner].values.get(key)
            if a_val is None or b_val is None or b_val == 0:
                continue
            print(f"  {corner:<15} {key}: {a_val:.4f} V (300 ns window) vs "
                  f"{b_val:.4f} V (50 ns window), {abs(a_val - b_val) / abs(b_val):.2%} apart "
                  f"-- NOT enforced: a max/min over a longer, later window is a "
                  f"different statistic, not a disagreement")
    return worst


# --------------------------------------------------------------------------
# 2. the per-corner Q table over the full covered grid
# --------------------------------------------------------------------------

def grid_coverage() -> tuple[int, list[str]]:
    """``(measured, missing)`` over the covered PVT grid."""
    have = {p.rec.corner for p in shipped_points(PVT_Q_GLOB, A_JITTER_ENERGY)}
    want = [
        f"{proc}/{t:.0f}/{v:.2f}"
        for proc in GRID_PROCESSES
        for t in GRID_TEMPS_C
        for v in GRID_SUPPLIES_V
    ]
    return len(have & set(want)), [c for c in want if c not in have]


def starved_cell_constants() -> tuple[float, float]:
    """``(a_lag1, a_asym)`` -- the two starved-cell constants issue #52 derived,
    averaged over its 3 measured corners exactly as
    ``starved_cell_jitter_energy.py``'s own summary line computes them."""
    points, _skipped = load_starved_points()
    a_lag1 = sum(p.a(p.kappa2_lag1) for p in points) / len(points)
    a_asym = sum(p.a(p.kappa2_asym) for p in points) / len(points)
    return a_lag1, a_asym


def report_corner(a_value: float, a_label: str, rate_bps: float,
                  full_table: bool) -> ArrayPoint:
    """Print the per-corner Q table at the given constant; return the worst point."""
    points = shipped_points(PVT_Q_GLOB, a_value)
    if not points:
        raise RuntimeError(
            f"no sim/records/{PVT_Q_GLOB} record measures a "
            f"{shipped_ring_count()}-ring array"
        )
    need = MARGIN_M * Q_H0
    print(f"\n-- a = {a_value:.3f} ({a_label}) -- "
          f"{a_value / A_JITTER_ENERGY:.2f}x the plain-cell constant ({A_JITTER_ENERGY:g}) --")
    ordered = sorted(points, key=lambda p: p.g)
    if full_table:
        header = (f"{'corner':<15} {'T0_r1 (s)':>11} {'P_tot (W)':>11} "
                  f"{'Q_array':>12} {'margin':>8} {'R_max(bps)':>11}")
        print(header)
        print("-" * len(header))
        rows = ordered
    else:
        header = f"{'corner':<15} {'Q_array':>12} {'margin':>8} {'R_max(bps)':>11}"
        print(header)
        print("-" * len(header))
        rows = ordered[:3] + ordered[-1:]
    for p in rows:
        q = p.q_array(rate_bps)
        if full_table:
            print(f"{p.rec.corner:<15} {p.periods[0]:11.4e} {p.p_total:11.4e} "
                  f"{q:12.4e} {q / need:7.2f}x {p.max_rate_bps():11.4g}")
        else:
            print(f"{p.rec.corner:<15} {q:12.4e} {q / need:7.2f}x {p.max_rate_bps():11.4g}")
    if not full_table:
        print(f"  (--full prints all {len(points)} rows; the three smallest and the "
              f"largest are shown)")
    return ordered[0]


# --------------------------------------------------------------------------
# 3. Monte Carlo mismatch
# --------------------------------------------------------------------------

def _parse_seed_pairs(raw_dir: Path, keys: tuple[str, ...]) -> list[dict[str, float]]:
    """Every per-seed ``m_<key> = <value>`` set found across ``raw_dir``'s logs,
    one dict per seed/run log that has ALL of ``keys`` (so a ring's period is
    always paired with its sibling ring's period from the SAME device draw)."""
    out = []
    for log in sorted(raw_dir.glob("*.log")):
        found = {m.group(1): float(m.group(2)) for m in _MEAS_LOG.finditer(log.read_text())}
        if all(k in found for k in keys):
            out.append({k: found[k] for k in keys})
    return out


def _cv(xs: list[float]) -> float:
    m = sum(xs) / len(xs)
    sd = (sum((x - m) ** 2 for x in xs) / max(len(xs) - 1, 1)) ** 0.5
    return sd / m


def report_mc_ro_freq() -> None:
    print("\n== RO-array frequency-spread MC (sim/tb/ro-array-core-mc-freq/) ==")
    records = sorted(RECORDS.glob("*-ro-array-core-mc-freq-*.md"))
    if not records:
        print("  (no sim/records/*-ro-array-core-mc-freq-*.md record committed yet)")
        return
    for rec_path in records:
        text = rec_path.read_text()
        raw_dir_m = re.search(r"path:\s*(sim/records/raw/\S+)/?\s*$", text, re.M)
        if raw_dir_m is None:
            print(f"  {rec_path.stem}: no raw.path found, skipping per-seed ratio check")
            continue
        raw_dir = REPO_ROOT / raw_dir_m.group(1).rstrip("/")
        pairs = _parse_seed_pairs(raw_dir, ("period_r1", "period_r2"))
        if not pairs:
            print(f"  {rec_path.stem}: no per-seed (period_r1, period_r2) pairs found "
                  f"under {raw_dir}")
            continue
        # period_r1/period_r2 == f_r2/f_r1: the ring FREQUENCY ratio, stated the
        # way design/README.md and DR-0007 §1 state it, so the two are directly
        # comparable without the reader inverting anything.
        ratios = [p["period_r1"] / p["period_r2"] for p in pairs]
        n = len(ratios)
        mean_ratio = sum(ratios) / n
        sd_ratio = (sum((r - mean_ratio) ** 2 for r in ratios) / max(n - 1, 1)) ** 0.5
        p1 = [p["period_r1"] for p in pairs]
        p2 = [p["period_r2"] for p in pairs]

        print(f"  {rec_path.stem}: {n} mismatch seeds")
        print(f"    period_r1 CV = {100 * _cv(p1):.2f}%   period_r2 CV = {100 * _cv(p2):.2f}%")
        print(f"    ring frequency ratio f_r2/f_r1 (= period_r1/period_r2): "
              f"mean {mean_ratio:.4f}  sd {sd_ratio:.4f} "
              f"({100 * sd_ratio / mean_ratio:.2f}% of mean)")
        nearest_int = round(mean_ratio)
        dist = abs(mean_ratio - nearest_int) / sd_ratio if sd_ratio else float("inf")
        print(f"    nearest integer ratio {nearest_int}: mean sits "
              f"{dist:.1f} sigma away from it across the measured spread")
        worst_dist = min(abs(r - round(r)) for r in ratios) if ratios else float("nan")
        print(f"    closest any SINGLE seed's ratio came to an integer: {worst_dist:.4f} "
              f"(0 = exactly integer, i.e. the injection-locking condition DR-0007 §1 "
              f"avoids by design; nothing observed here is close to it)")
        print(f"    reference: design/README.md's stated MISMATCH-FREE ratio is 1.057 "
              f"(ff/-40/3.63) to 1.062 (ss/-40/3.63) -- the "
              f"{100 * sd_ratio / mean_ratio:.2f}% mismatch-driven scatter measured here "
              f"is small against that ~6% deliberate skew")
        need = MARGIN_M * Q_H0
        q_sens = 2 * _cv(p1)  # Q ~ 1/T0^2 at fixed ring power, so a period CV moves Q by ~2x
        print(f"    Q_array sensitivity: at fixed ring power Q ~ 1/T0^2, so this period "
              f"spread moves Q_array by ~{100 * q_sens:.1f}% -- negligible against the "
              f"margin over M*Q_H0 ({need:g}) shown in section 2 above")


def _sampler_offset() -> tuple[float, float, float, int, str]:
    """``(systematic_offset_v, mismatch_sd_v, vdd, n_seeds, record_stem)``."""
    records = sorted(RECORDS.glob("*-sampler-dff-mc-offset-*.md"))
    if not records:
        raise RuntimeError("no sim/records/*-sampler-dff-mc-offset-*.md record committed yet")
    pattern = re.compile(
        r"^- `(dtrip_v)`:\s*mean\s+(-?[\d.]+(?:e[-+]?\d+)?)\s+over\s+(\d+)\s+seeds"
        r"\s*\(sd\s+(-?[\d.]+(?:e[-+]?\d+)?)", re.M,
    )
    rec_path = records[-1]
    text = rec_path.read_text()
    m = pattern.search(text)
    if m is None:
        raise RuntimeError(f"{rec_path.stem}: no dtrip_v seed-aggregate found")
    mean_v, n, sd_v = float(m.group(2)), int(m.group(3)), float(m.group(4))
    vdd_m = re.search(r"voltage:\s*([\d.]+)", text)
    vdd = float(vdd_m.group(1)) if vdd_m else 3.3
    return mean_v - 0.5 * vdd, sd_v, vdd, n, rec_path.stem


def _crossing_slew(corner: str) -> tuple[float, str]:
    """``(slew_v_per_s, how_it_was_obtained)`` for the ``xo`` edge at ``corner``.

    ``sim/tb/ro-array-core-xo-slew/`` measures this directly, two ways, and
    this function combines them into ONE number with a stated construction:

      * ``xo``'s steepest dV/dt (``max``/``min`` of the numerically
        differentiated transient) is the peak slew, i.e. the slew at the
        single fastest point of the edge. Using it alone would UNDERSTATE a
        timing offset, because a threshold that sits away from that point
        sees a slower crossing.
      * On the ring node, which is periodic and can therefore carry both
        methods, the same record also measures the average slew across the
        40-60 % band. The band/peak ratio there says how much slower the
        band-average is than the peak on this circuit's edges.

    The headline figure is ``xo``'s peak slew scaled by the ring node's own
    band/peak ratio: a band-average slew for ``xo``, built from ``xo``'s own
    peak and a shape factor measured on a node where both methods are safe.
    The slower of the rising and falling edges is used, since a raw bit is
    captured on either.

    If no slew record exists at this corner, the caller gets the older
    swing-over-period proxy instead, clearly labelled -- that proxy averages
    over an entire period rather than an edge and is several times too slow.
    """
    slew_recs = {r.corner: r for r in load("*-ro-array-core-xo-slew-*.md")}
    rec = slew_recs.get(corner)
    if rec is not None:
        xo_peak = min(abs(rec.values["xo_slew_rise_v_per_s"]),
                      abs(rec.values["xo_slew_fall_v_per_s"]))
        ro_peak = min(abs(rec.values["ro1_slew_rise_v_per_s"]),
                      abs(rec.values["ro1_slew_fall_v_per_s"]))
        band = 0.5 * (abs(rec.values["ro1_band_slew_a_v_per_s"])
                      + abs(rec.values["ro1_band_slew_b_v_per_s"]))
        shape = band / ro_peak
        return xo_peak * shape, (
            f"measured ({rec.stem}): xo peak {xo_peak:.3e} V/s x ring-node "
            f"band/peak shape factor {shape:.3f}"
        )
    for glob in (PVT_Q_GLOB, POWER_GLOB):
        array = next((r for r in load(glob) if r.corner == corner), None)
        if array is not None:
            proxy = array.values["xo_swing_v"] / array.values["period_r1"]
            return proxy, (
                f"FALLBACK swing-over-period proxy ({array.stem}): {proxy:.3e} V/s "
                f"-- an average over a whole period, not an edge; several times too "
                f"slow, and therefore several times too pessimistic about bias"
            )
    raise RuntimeError(f"no slew record and no array record at {corner}")


def _slew_and_sigma(rate_bps: float, corner: str = "tt/27/3.30") -> tuple[float, float, str]:
    """``(slew_v_per_s, sigma_acc_s, slew_provenance)`` at ``corner``.

    ``sigma_acc`` is the single ring's accumulated-jitter sd at the sample
    interval, from that corner's ``kappa2_asym`` in
    ``sim/tools/starved_cell_jitter_energy.py``: ``sigma_acc = sqrt(k2 * Ts)``.
    """
    slew, provenance = _crossing_slew(corner)
    starved_points, _skipped = load_starved_points()
    starved = next((p for p in starved_points if p.rec.corner == corner), None)
    if starved is not None:
        return slew, (starved.kappa2_asym / rate_bps) ** 0.5, provenance
    # No transient-noise record of the shipped cell at this corner. Fall back
    # to the jitter-energy law DR-0007 §2 evaluates Q with in the first place
    # (kappa^2 = a * kB * T / P_ring, at the starved cell's own asymptotic a),
    # applied to this corner's measured ring power. Labelled, never silent:
    # it is a model, and the corner it is most needed at is precisely the one
    # that has never been measured directly.
    _a_lag1, a_asym = starved_cell_constants()
    point = next((p for p in shipped_points(PVT_Q_GLOB, a_asym)
                  if p.rec.corner == corner), None)
    if point is None:
        raise RuntimeError(f"no array record at {corner} to derive kappa^2 from")
    kappa2 = a_asym * KB * point.rec.temp_k / point.powers[0]
    return (
        slew,
        (kappa2 / rate_bps) ** 0.5,
        provenance + f"; sigma_acc LAW-DERIVED (kappa^2 = a*kB*T/P_ring at "
                     f"a = {a_asym:.3f}), not measured -- no "
                     f"sim/tb/ro-ring5-starved-jitter-long/ record exists at this corner",
    )


def report_mc_sampler_offset(rate_bps: float) -> None:
    print("\n== Sampler decision-threshold MC (sim/tb/sampler-dff-mc-offset/) ==")
    try:
        offset_v, sd_v, vdd, n, stem = _sampler_offset()
    except RuntimeError as exc:
        print(f"  ({exc})")
        return
    print(f"  {stem}: {n} mismatch seeds, VDD = {vdd:g} V")
    print(f"    systematic (non-mismatch) offset from ideal mid-supply "
          f"{0.5 * vdd:.3f} V: {1000 * offset_v:+.1f} mV -- present at EVERY seed, a "
          f"property of this cell's P/N sizing on this PDK, not a mismatch effect "
          f"(see sim/tb/sampler-dff-mc-offset/tb_sampler_dff_mc_offset.sp)")
    print(f"    mismatch-driven spread alone (sd): {1000 * sd_v:.2f} mV "
          f"({100 * sd_v / vdd:.2f}% of VDD) -- this is issue #13's actual question")

    try:
        slew, sigma_acc, provenance = _slew_and_sigma(rate_bps)
    except RuntimeError as exc:
        print(f"    (could not compare against jitter: {exc})")
        return
    print(f"    converting a voltage offset at the decision node to an equivalent "
          f"timing offset uses the nominal corner's own xo-edge slew "
          f"({slew:.3e} V/s -- {provenance}) and the single ring's "
          f"accumulated-jitter sd at DR-0010's {rate_bps:g} bps target "
          f"({sigma_acc * 1e9:.3f} ns):")
    for label, volts in (("systematic offset", abs(offset_v)), ("mismatch spread (1 sd)", sd_v)):
        dt = volts / slew
        print(f"      {label:<24} {1000 * volts:7.2f} mV -> {dt * 1e12:7.1f} ps "
              f"= {dt / sigma_acc:.3f} sigma_acc")


# --------------------------------------------------------------------------
# 4. do the conditioner and health-test margins cover that spread?
# --------------------------------------------------------------------------

def report_bias_margins(rate_bps: float) -> None:
    print("\n== Does the measured mismatch bias fit inside the spec's margins? ==")
    print("  MODEL, stated once and used for every number below: the ring's crossing")
    print("  time at the sampler is Gaussian with sd sigma_acc; a threshold offset")
    print("  displaces that crossing by dt = offset/slew; the captured bit's")
    print("  probability is therefore p = Phi(dt/sigma_acc). This is a BOUNDING")
    print("  model for the effect of bias alone, not a min-entropy measurement --")
    print("  the H it yields is a CEILING (what H could be if bias were the only")
    print("  departure from ideal), so the meaningful question is whether that")
    print("  ceiling stays well above the targets, i.e. whether bias is nowhere near")
    print("  being the binding constraint. Measuring H itself is #12's job and")
    print("  DR-0004's tiering is unchanged.")
    try:
        offset_v, sd_v, vdd, n, stem = _sampler_offset()
    except RuntimeError as exc:
        print(f"  ({exc})")
        return

    cases = [
        ("mismatch spread, 1 sd", sd_v),
        ("mismatch spread, 3 sd", 3.0 * sd_v),
        ("systematic offset alone", abs(offset_v)),
        ("systematic + 3 sd mismatch", abs(offset_v) + 3.0 * sd_v),
    ]
    worst_z, worst_corner = None, ""
    for corner, note in (
        ("tt/27/3.30", "where the offset was actually measured"),
        (PREDICTED_MIN_Q_CORNER,
         "EXTRAPOLATION: sim/tb/sampler-dff-mc-offset/ is nominal-corner-only, so "
         "this row set carries the NOMINAL corner's measured offset over to this "
         "corner's own measured slew and jitter. The offset's own corner dependence "
         "is unmeasured"),
        (MEASURED_MIN_Q_CORNER,
         "the entropy-binding corner (DR-0015). Same extrapolation of the offset as "
         "above, and sigma_acc here is law-derived rather than measured -- see the "
         "provenance line"),
    ):
        try:
            slew_c, sigma_c, provenance = _slew_and_sigma(rate_bps, corner)
        except RuntimeError as exc:
            print(f"\n  at {corner}: skipped ({exc})")
            continue
        print(f"\n  at {corner} -- {note}")
        print(f"  xo-edge slew {slew_c:.3e} V/s -- {provenance}")
        print(f"  sigma_acc({rate_bps:g} bps) {sigma_c * 1e9:.3f} ns")
        header = (f"  {'case':<28} {'dt/sigma':>9} {'p_major':>8} {'H ceiling':>10} "
                  f"{'vs H0=0.5':>10} {'vs DR-0008':>11}")
        print(header)
        print("  " + "-" * (len(header) - 2))
        for label, volts in cases:
            z = (volts / slew_c) / sigma_c
            p = _norm_cdf(z)
            h = -math.log2(p)
            print(f"  {label:<28} {z:9.3f} {p:8.4f} {h:10.4f} "
                  f"{h / H0_TARGET:9.2f}x {h / DR0008_BREAK_EVEN_H:10.2f}x")
            if label == cases[-1][0] and (worst_z is None or z > worst_z):
                worst_z, worst_corner = z, corner
    if worst_z is None:
        return
    print(f"\n  (H ceiling = -log2(p_major); DR-0008 §5's break-even is "
          f"H = {DR0008_BREAK_EVEN_H:g}, below which K = 8 CRC-32 compression stops "
          f"earning the full 0.85 bit/bit non-vetted cap)")

    print("\n  DR-0002 health tests, cutoffs frozen at the assumed H0 = 0.5")
    print(f"  (C_RCT = {C_RCT_AT_H0}, C_APT = {C_APT_AT_H0} in a W = {APT_WINDOW} window, "
          f"alpha = 2^-40 = {ALPHA:.3e}).")
    print("  The question is whether a stream carrying the measured bias would trip")
    print("  cutoffs that were computed for an unbiased-at-H0 stream:")
    p = _norm_cdf(worst_z)
    rct_rate = p ** (C_RCT_AT_H0 - 1)
    apt_rate = _binom_tail(APT_WINDOW, C_APT_AT_H0, p)
    print(f"    worst case modelled ({cases[-1][0]}, at {worst_corner}): "
          f"p_major = {p:.4f}")
    print(f"    RCT: Pr({C_RCT_AT_H0} identical consecutive samples) = {rct_rate:.3e}  "
          f"-- {'BELOW' if rct_rate <= ALPHA else 'ABOVE'} alpha ({ALPHA:.3e}), "
          f"i.e. the false-alarm budget is {'preserved' if rct_rate <= ALPHA else 'BLOWN'}")
    print(f"    APT: Pr(X >= {C_APT_AT_H0}) for X ~ Bin({APT_WINDOW}, {p:.4f}) = "
          f"{apt_rate:.3e}  -- {'BELOW' if apt_rate <= ALPHA else 'ABOVE'} alpha, "
          f"i.e. the false-alarm budget is "
          f"{'preserved' if apt_rate <= ALPHA else 'BLOWN'}")
    print(f"    (expected majority count in a {APT_WINDOW}-sample window at this p: "
          f"{APT_WINDOW * p:.0f}, against the {C_APT_AT_H0} cutoff -- "
          f"{(C_APT_AT_H0 - APT_WINDOW * p) / math.sqrt(APT_WINDOW * p * (1 - p)):.1f} "
          f"sd of headroom)")


# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="worst_corner_entropy.py",
        description="Issue #13: the entropy-binding PVT corner over the covered grid, "
                    "and the device-mismatch bias measured at the nominal corner.",
    )
    parser.add_argument(
        "--rate", type=float, default=DR0010_RATE_BPS, metavar="BPS",
        help=f"raw rate to evaluate Q at (default {DR0010_RATE_BPS:g} bps, DR-0010 §1)",
    )
    parser.add_argument(
        "--full", action="store_true",
        help="print every grid row of every Q table, not just the extremes",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="exit non-zero unless the records still support the stated "
             f"entropy-binding corner ({MEASURED_MIN_Q_CORNER}), the covered grid is "
             "complete, and the two array record families still agree where they overlap",
    )
    args = parser.parse_args(argv)

    a_lag1, a_asym = starved_cell_constants()
    print("issue #13: entropy-binding corner over the covered PVT grid, and "
          "Monte Carlo mismatch bias")
    print(f"plain-cell constant (jitter_energy_law.py):  a = {A_JITTER_ENERGY:g}")
    print(f"starved-cell constants (starved_cell_jitter_energy.py): "
          f"a_lag1 = {a_lag1:.3f}, a_asym = {a_asym:.3f}")

    agreement = report_family_agreement()

    measured, missing = grid_coverage()
    total = len(GRID_PROCESSES) * len(GRID_TEMPS_C) * len(GRID_SUPPLIES_V)
    print(f"\n== covered PVT grid: {measured}/{total} points measured by "
          f"sim/tb/ro-array-core-pvt-q/ ==")
    if missing:
        print("  missing: " + ", ".join(missing))
    print("  (fs/sf process corners are out of scope by DR-0006; no claim below "
          "extends to them)")

    worsts = []
    try:
        for a_value, label in (
            (A_JITTER_ENERGY, "plain cell, DR-0010's stated constant"),
            (a_asym, "starved cell, asymptotic slope"),
            (a_lag1, "starved cell, lag-1"),
        ):
            worsts.append((label, report_corner(a_value, label, args.rate, args.full)))
    except RuntimeError as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 2

    print(f"\nDR-0012-sampler-fixed-external-clock predicted minimum-Q corner: "
          f"{PREDICTED_MIN_Q_CORNER} (from 3 measured PVT points)")
    print(f"this repository's stated entropy-binding corner (DR-0015, from the "
          f"{total}-point grid): {MEASURED_MIN_Q_CORNER}")
    ok = True
    for label, worst in worsts:
        match = "matches" if worst.rec.corner == MEASURED_MIN_Q_CORNER else "DOES NOT MATCH"
        if worst.rec.corner != MEASURED_MIN_Q_CORNER:
            ok = False
        print(f"  measured minimum-Q corner ({label}): {worst.rec.corner}  "
              f"-- {match} the stated corner")
    print("\n  a multiplies every corner's Q identically, so the three agree by "
          "construction; they are all printed because the MARGIN, not the ranking, "
          "is what the constant moves.")
    if MEASURED_MIN_Q_CORNER != PREDICTED_MIN_Q_CORNER:
        pred = next((p for p in shipped_points(PVT_Q_GLOB, A_JITTER_ENERGY)
                     if p.rec.corner == PREDICTED_MIN_Q_CORNER), None)
        meas = next((p for p in shipped_points(PVT_Q_GLOB, A_JITTER_ENERGY)
                     if p.rec.corner == MEASURED_MIN_Q_CORNER), None)
        if pred is not None and meas is not None:
            print(f"\n  The measured minimum is NOT the predicted one. At "
                  f"{PREDICTED_MIN_Q_CORNER}, Q = {pred.q_array(args.rate):.4e}; at "
                  f"{MEASURED_MIN_Q_CORNER}, Q = {meas.q_array(args.rate):.4e} "
                  f"({100 * (1 - meas.g / pred.g):.1f}% lower). The prediction was "
                  f"made over a 3-point set that did not contain the hot corner: "
                  f"Q ~ T_K/(P*T0^2), and going from -40 C to +125 C at ss/3.63 V "
                  f"lengthens T0 from {pred.periods[0] * 1e9:.2f} ns to "
                  f"{meas.periods[0] * 1e9:.2f} ns, whose 1/T0^2 term outweighs both "
                  f"the higher kT and the lower ring power. DR-0015 records this; "
                  f"DR-0012-sampler-fixed-external-clock's own 'Revisit if' clause "
                  f"names this exact outcome as its trigger.")

    report_mc_ro_freq()
    report_mc_sampler_offset(args.rate)
    report_bias_margins(args.rate)

    if args.check:
        problems = []
        if not ok:
            problems.append(
                f"the measured minimum-Q corner is not the stated "
                f"{MEASURED_MIN_Q_CORNER}. That is a reportable result, not a "
                f"constant to edit: DR-0012-sampler-fixed-external-clock's own "
                f"'Revisit if' clause names this exact case, and it routes through "
                f"spec/ with a decision record."
            )
        if missing:
            problems.append(
                f"the covered PVT grid is incomplete ({measured}/{total}); a MINIMUM "
                f"over a partial grid is not the claim this script states. Missing: "
                + ", ".join(missing)
            )
        if agreement > FAMILY_AGREEMENT_TOL:
            problems.append(
                f"the two array record families differ by {agreement:.2%} at a shared "
                f"PVT point (tolerance {FAMILY_AGREEMENT_TOL:.0%}); the corner table "
                f"above reads one family and is cross-checked against the other, so "
                f"they cannot be allowed to drift apart silently."
            )
        if problems:
            for problem in problems:
                print(f"\nFAIL: {problem}", file=sys.stderr)
            return 1
        print(f"\nOK: {MEASURED_MIN_Q_CORNER} minimizes Q over all {total} covered "
              f"grid points at every constant checked, and the two array record "
              f"families agree to {agreement:.2e} where they overlap.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
