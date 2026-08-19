#!/usr/bin/env python3
"""Apply the #10/DR-0012 methodology's min-entropy point estimator to the
REAL transistor-derived raw bitstream (issue #12), and explain the result
against the design's own jitter-energy sizing law.

    python3 sim/tools/raw_min_entropy_estimate.py

This is a *derivation*, not a simulation: it reads only records already
committed under ``sim/records/`` (the ``sampler-array-digitize`` family from
issue #9, plus the ``ro-array-core-power`` family DR-0010's sizing law
already reads) and does arithmetic on them, the same shape as
``sim/tools/jitter_energy_law.py`` / ``sim/tools/array_sizing.py``. It needs
neither ngspice nor the PDK, and it writes nothing.

What it computes
-----------------
1. **The most-common-value min-entropy point estimator**
   (``H_hat = -log2(max(p1_hat, 1 - p1_hat))``), the estimator DR-0012 §2
   names as what a bounded sim-stage estimate is allowed to be and that
   ``sim/tools/jitter_estimator_calibration_check.py`` already validated
   against a closed-form target -- applied here to the *real* sampler-chain
   bits (``sim/tb/sampler-array-digitize``, issue #9) instead of an idealized
   calibration source, at both corners that testbench has run.
2. **Confidence degradation at the achieved N**, per DR-0012 §2's own stated
   formula (binomial SE on p, propagated through the estimator's local
   sensitivity) -- and, separately and explicitly, why that formula's
   independence assumption is itself not credible at this N (see
   "Effective independence" below).
3. **A physical cross-check, with no new simulation**: DR-0010's jitter-
   energy law (`Q_array(T_s) = g * T_s`, evaluated by
   ``sim/tools/array_sizing.py``) tells us how much phase noise the shipped
   array accumulates in exactly the sample interval this testbench uses,
   using both DR-0010's stated (plain-cell) constant and issue #46's
   measured (shipped starved-cell) constant. That comparison explains the
   estimator's output rather than merely reporting it.

What this does NOT do
----------------------
It does not, and cannot, produce DR-0004 Tier 2's target headline figure (a
supportable non-trivial min-entropy estimate at a rate the design could
actually run at). Section 3 below is the quantitative reason why not, read
from evidence this repository already has. See
``sim/characterization-raw-min-entropy-and-battery.md`` for the full
narrative this script's numbers feed.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"
TOOLS_DIR = Path(__file__).resolve().parent
TB_MANIFEST = REPO_ROOT / "sim" / "tb" / "sampler-array-digitize" / "tb.json"

sys.path.insert(0, str(TOOLS_DIR))
import array_sizing as asiz  # noqa: E402
import starved_cell_jitter_energy as scje  # noqa: E402
from _record_parsing import field, format_corner, parse_corner  # noqa: E402

SLUG = "sampler-array-digitize"

_VALUE_MEAN = re.compile(
    r"^- `([a-z0-9_]+)`:\s*mean\s+(-?[\d.]+(?:e[-+]?\d+)?)\s+over\s+(\d+)\s+seeds"
    r"\s*\(sd\s+(-?[\d.]+(?:e[-+]?\d+)?)",
    re.M,
)
_BIT_KEY = re.compile(r"^b(\d+)_v$")


class RecordError(RuntimeError):
    pass


class BitstreamRecord:
    """One committed sampler-array-digitize record: its bits and its corner."""

    def __init__(self, path: Path) -> None:
        text = path.read_text()
        self.stem = path.stem
        self.values: dict[str, float] = {}
        self.sd: dict[str, float] = {}
        self.n_seeds = 1
        for m in _VALUE_MEAN.finditer(text):
            self.values[m.group(1)] = float(m.group(2))
            self.n_seeds = int(m.group(3))
            self.sd[m.group(1)] = float(m.group(4))
        self.process, self.temp_c, self.vdd = parse_corner(
            text, label=self.stem, error_cls=RecordError
        )
        self.seeds = field(text, r"^seeds:\s*(\[[^\]]*\])", label=self.stem, error_cls=RecordError)

        bit_indices = sorted(
            int(m.group(1)) for k in self.values if (m := _BIT_KEY.fullmatch(k))
        )
        if not bit_indices:
            raise RecordError(f"{self.stem}: no bN_v measurements found")
        half_rail = self.vdd / 2.0
        self.bits = [1 if self.values[f"b{i}_v"] > half_rail else 0 for i in bit_indices]
        self.bit_spread_v = [self.sd.get(f"b{i}_v", 0.0) for i in bit_indices]

    @property
    def corner(self) -> str:
        return format_corner(self.process, self.temp_c, self.vdd)


def load_records() -> list[BitstreamRecord]:
    paths = sorted(RECORDS.glob(f"*-{SLUG}-*.md"))
    if not paths:
        raise RecordError(f"no sim/records/*-{SLUG}-*.md records found")
    return [BitstreamRecord(p) for p in paths]


def h_hat(p1: float) -> float:
    """Most-common-value min-entropy point estimate (DR-0012 §2)."""
    p_max = max(p1, 1.0 - p1)
    if p_max <= 0:
        return float("nan")
    return -math.log2(p_max)


def confidence_degradation(p1: float, n: int) -> tuple[float, float]:
    """``(SE(p1_hat), SE(H_hat))`` from DR-0012 §2's stated formula:
    binomial SE on p, propagated through the estimator's local sensitivity
    ``|dH/dp| = 1 / (p_max * ln 2)`` at the achieved ``p_max``."""
    if n <= 0:
        return float("nan"), float("nan")
    se_p = math.sqrt(p1 * (1.0 - p1) / n)
    p_max = max(p1, 1.0 - p1)
    if p_max <= 0:
        return se_p, float("nan")
    dh_dp = 1.0 / (p_max * math.log(2.0))
    return se_p, se_p * dh_dp


def sample_period_s() -> float:
    """The testbench's sample interval (``tclk``), read from its manifest
    rather than assumed, so this cannot silently drift from what actually
    ran."""
    import json

    manifest = json.loads(TB_MANIFEST.read_text())
    tclk = manifest["params"]["tclk"]
    return float(tclk)


def starved_cell_a_asym() -> float:
    """Mean of the shipped starved cell's asymptotic-slope jitter-energy
    constant (issue #46) over the corners it has been measured at -- the
    same figure ``starved_cell_jitter_energy.py``'s own CLI prints as
    ``a (asymptotic slope ...)``, recomputed here rather than hardcoded so it
    cannot drift from that module's own derivation."""
    points, _ = scje.load_points()
    return sum(p.a(p.kappa2_asym) for p in points) / len(points)


def q_context(corner: str, t_s: float) -> dict | None:
    """DR-0007 §2's Q_array at sample interval ``t_s`` for ``corner``, using
    both DR-0010's stated (plain-cell) constant and issue #46's measured
    (shipped starved-cell) constant. Returns ``None`` if no
    ``ro-array-core-power`` record exists for that corner (nothing to
    compare against)."""
    records = asiz.load("*-ro-array-core-power-*.md")
    shipped_n = asiz.shipped_ring_count()
    a_starved = starved_cell_a_asym()
    for rec in records:
        if rec.corner != corner:
            continue
        point_plain = asiz.ArrayPoint(rec, a=asiz.A_JITTER_ENERGY)
        if point_plain.n != shipped_n:
            continue
        point_starved = asiz.ArrayPoint(rec, a=a_starved)
        need = asiz.MARGIN_M * asiz.Q_H0
        return {
            "corner": corner,
            "t_s": t_s,
            "q_plain": point_plain.q_array(1.0 / t_s),
            "q_starved": point_starved.q_array(1.0 / t_s),
            "a_plain": asiz.A_JITTER_ENERGY,
            "a_starved": a_starved,
            "need": need,
        }
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="raw_min_entropy_estimate.py",
        description="MCV min-entropy point estimate on the real sampler-array-digitize "
        "bitstream, cross-checked against DR-0010's jitter-energy sizing law.",
    )
    parser.parse_args(argv)

    try:
        records = load_records()
        t_s = sample_period_s()
    except RecordError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(
        "MCV raw min-entropy point estimate -- sim/tb/sampler-array-digitize "
        f"(issue #9), sample interval T_s = {t_s:.3e} s\n"
        "LABEL (DR-0004): simulation-derived design estimate; "
        "not an SP 800-90B entropy assessment.\n"
    )

    header = (
        f"{'corner':<15} {'N':>3} {'seeds':>7} {'ones':>5} {'p1_hat':>8} "
        f"{'H_hat (bit)':>12} {'SE(p1), naive N=bits':>22} {'SE(H), naive':>13}"
    )
    print(header)
    print("-" * len(header))
    for rec in records:
        n = len(rec.bits)
        ones = sum(rec.bits)
        p1 = ones / n
        h = h_hat(p1)
        se_p, se_h = confidence_degradation(p1, n)
        print(
            f"{rec.corner:<15} {n:>3} {rec.n_seeds:>7} {ones:>5} {p1:8.3f} "
            f"{h:12.4f} {se_p:22.4f} {se_h:13.4f}"
        )

    print(
        "\nEffective independence (why the 'naive N=bits' SE column above "
        "overstates confidence):"
    )
    for rec in records:
        max_spread = max(rec.bit_spread_v) if rec.bit_spread_v else 0.0
        print(
            f"  {rec.corner}: {rec.n_seeds} independent noise seeds "
            f"({rec.seeds}), worst per-bit seed-to-seed spread {max_spread:.3e} V "
            f"-- {'IDENTICAL bit pattern at every seed' if max_spread < 1e-3 else 'bits vary across seeds'}"
        )
    print(
        "  Each record's bits are ten SUCCESSIVE samples of one evolving ring-phase\n"
        "  process, not ten independent draws, and (per the spreads above) an\n"
        "  additional noise seed changes NONE of them. So the true count of\n"
        "  independent random realizations behind each row is much closer to 1\n"
        "  (one noise process, observed not to move the outcome) than to the 10\n"
        "  bits or 10*n_seeds samples the naive SE formula assumes -- the naive\n"
        "  column above is DR-0012 Section 2's formula applied honestly, and it is\n"
        "  still not a defensible confidence interval at this N. Report both."
    )

    print("\nPhysical cross-check: DR-0007 Section 2 Q_array at this testbench's T_s")
    print(
        f"  DR-0007 requires Q_array >= M*Q_H0 = {asiz.MARGIN_M}*{asiz.Q_H0:g} "
        f"= {asiz.MARGIN_M * asiz.Q_H0:g} for H >= 0.5 to be a supportable design point.\n"
    )
    qheader = (
        f"{'corner':<15} {'Q_array (a=1.79, plain)':>24} {'Q_array (a=#46 starved)':>24} "
        f"{'shortfall vs required (starved)':>32}"
    )
    print(qheader)
    print("-" * len(qheader))
    any_ctx = False
    for rec in records:
        ctx = q_context(rec.corner, t_s)
        if ctx is None:
            print(f"{rec.corner:<15}  (no matching ro-array-core-power record)")
            continue
        any_ctx = True
        shortfall = ctx["need"] / ctx["q_starved"]
        print(
            f"{ctx['corner']:<15} {ctx['q_plain']:24.3e} {ctx['q_starved']:24.3e} "
            f"{shortfall:31.1f}x"
        )
    if any_ctx:
        print(
            "\n  Even using issue #46's measured constant for the SHIPPED starved cell\n"
            "  (the more favorable of the two, ~6.6x the plain-cell value DR-0010\n"
            "  states), Q_array at this testbench's necessarily-fast sample interval\n"
            "  is several orders of magnitude below what DR-0007's sizing law\n"
            "  considers necessary for H = 0.5. That is the physical reason the\n"
            "  observed bits are identical across every seed run so far: at this T_s\n"
            "  the array has not yet accumulated enough phase noise, by a wide\n"
            "  margin, for noise to plausibly flip which side of the sampler's\n"
            "  threshold a sample lands on. The H_hat figures in the first table are\n"
            "  therefore NOT a supportable estimate of the design's real min-entropy\n"
            "  at any rate under consideration -- see\n"
            "  sim/characterization-raw-min-entropy-and-battery.md for the full\n"
            "  reasoning, including why the entropy-supporting rate (DR-0010's\n"
            "  proposed 500 bps) is itself unaffordable to simulate directly."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
