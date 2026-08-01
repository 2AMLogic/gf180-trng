#!/usr/bin/env python3
"""Check the jitter-estimator-calibration record against its closed-form prediction.

    python3 sim/tools/jitter_estimator_calibration_check.py             # print the table
    python3 sim/tools/jitter_estimator_calibration_check.py --check     # assert tolerance holds

This is the calibration experiment DR-0012 (transient-noise simulation
methodology) requires: a source with analytically known statistics pushed
through the same bit-extraction + min-entropy-estimation step the real
estimation pipeline will use, checked against a closed-form prediction. It
reads only a record already committed under ``sim/records/`` (by default the
newest ``jitter-estimator-calibration`` record) and does arithmetic on it. It
needs neither ngspice nor the PDK, and it writes nothing -- the same shape as
``sim/tools/jitter_energy_law.py --check``.

What it derives
----------------
``sim/tb/jitter-estimator-calibration/`` drives an already-calibrated
``trnoise()`` source (the same NA/NT pair
``sim/tb/trnoise-calibration/tb_trnoise_cal.sp`` validates against
``S_w = 2*NA^2*NT``) into a comparator: ``bit = 1`` iff ``v(nw) + bias > 0``.
Each held noise sample is i.i.d. ``N(0, NA^2)`` by construction, so

    P(bit = 1) = Phi(bias / NA)                              [[exact]]

where ``Phi`` is the standard normal CDF. Three ``bias`` values are chosen
(see :data:`LEVELS`) so this probability equals ``2**-H`` for
``H in {1.0, 0.5, 0.1}`` bit/sample -- i.e. so the most-common-value
min-entropy point estimator

    H_hat = -log2(max(p1_hat, 1 - p1_hat))

that DR-0004 Tier 2 anticipates ("90B-style estimators ... applied only to
the extent the achievable simulated bit count supports") has a known target
to recover from the simulated stream.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path
from statistics import NormalDist

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"
SLUG = "jitter-estimator-calibration"

#: The trnoise() sample standard deviation this testbench injects -- see
#: sim/tb/jitter-estimator-calibration/tb.json ``params.vn_rms`` and
#: sim/tb/trnoise-calibration (same NA, independently PSD-validated there).
NA = 2.2361e-3

_NORMAL = NormalDist(0, 1)

#: (measurement name, target H in bit/sample). The bias value baked into
#: each measurement's ngspice `let` expression in tb.json is
#: NA * Phi^-1(2**-H) -- reproduced here from H, not copied by hand, so the
#: two can never silently drift apart.
LEVELS: tuple[tuple[str, float], ...] = (
    ("p1_h100", 1.0),
    ("p1_h050", 0.5),
    ("p1_h010", 0.1),
)

#: Tolerance on H_hat vs. the analytic target, in bits. Chosen with headroom
#: over the run-to-run spread actually observed at n ~= 4e5 samples/seed x 4
#: seeds (binomial SE(p1) ~ 8e-4 at p=0.5, i.e. SE(H) ~ 2e-3 via the delta
#: method dH/dp = 1/(p ln 2)) -- see the record's own Caveats for the figure
#: actually measured. Fails on a real regression (e.g. the bias values and
#: the estimator silently drifting apart), not on ordinary seed-to-seed noise.
TOLERANCE_BITS = 0.02


class RecordError(RuntimeError):
    pass


def bias_for_h(h: float) -> float:
    """The comparator offset that makes P(bit=1) = 2**-H exactly, given NA."""
    p = 2.0**-h
    return NA * _NORMAL.inv_cdf(p)


def p1_target(h: float) -> float:
    return 2.0**-h


def h_hat(p1: float) -> float:
    """Most-common-value min-entropy point estimate from a measured P(bit=1)."""
    return -math.log2(max(p1, 1.0 - p1))


_VALUE = re.compile(r"^- `([a-z0-9_]+)`:\s*(?:mean\s+)?(-?[\d.]+(?:e[-+]?\d+)?)", re.M)


def latest_record() -> Path:
    candidates = sorted(RECORDS.glob(f"*-{SLUG}-*.md"))
    if not candidates:
        raise RecordError(f"no committed record matches sim/records/*-{SLUG}-*.md")
    return candidates[-1]


def read_record(path: Path) -> dict[str, float]:
    if not path.is_file():
        raise RecordError(f"no such record: {path}")
    text = path.read_text()
    return {m.group(1): float(m.group(2)) for m in _VALUE.finditer(text)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="jitter_estimator_calibration_check.py",
        description="Check the jitter-estimator-calibration record's measured "
        "P(bit=1) against the closed-form Phi(bias/NA) prediction.",
    )
    parser.add_argument(
        "record", nargs="?", metavar="RECORD_STEM_OR_PATH",
        help=f"record to check (default: newest sim/records/*-{SLUG}-*.md)",
    )
    parser.add_argument(
        "--check", action="store_true",
        help=f"exit non-zero if any level's |H_hat - H_target| exceeds {TOLERANCE_BITS} bit",
    )
    parser.add_argument(
        "--tolerance", type=float, default=TOLERANCE_BITS, metavar="BITS",
        help=f"override the tolerance in bits (default {TOLERANCE_BITS})",
    )
    args = parser.parse_args(argv)

    if args.record:
        path = Path(args.record)
        if not path.suffix:
            path = RECORDS / f"{args.record}.md"
    else:
        try:
            path = latest_record()
        except RecordError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2

    try:
        values = read_record(path)
    except RecordError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"record: {path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path}")
    print(f"NA (injected trnoise sample sigma): {NA:.6g} V\n")

    header = f"{'name':>9}  {'H target':>8}  {'bias (V)':>12}  {'p1 target':>10}  {'p1 measured':>12}  {'H_hat':>8}  {'|dH| (bit)':>10}"
    print(header)
    print("-" * len(header))

    worst = 0.0
    missing: list[str] = []
    for name, h_target in LEVELS:
        if name not in values:
            missing.append(name)
            continue
        p1_meas = values[name]
        h_meas = h_hat(p1_meas)
        d = abs(h_meas - h_target)
        worst = max(worst, d)
        print(
            f"{name:>9}  {h_target:8.3f}  {bias_for_h(h_target):12.6e}  "
            f"{p1_target(h_target):10.6f}  {p1_meas:12.6f}  {h_meas:8.4f}  {d:10.4f}"
        )

    if missing:
        print(f"\nERROR: record is missing measurement(s): {', '.join(missing)}", file=sys.stderr)
        return 2

    print(f"\nworst |H_hat - H_target| over the three levels: {worst:.4f} bit")

    if args.check:
        if worst > args.tolerance:
            print(
                f"\nFAIL: worst deviation {worst:.4f} bit exceeds tolerance {args.tolerance} bit -- "
                "the bit-extraction/estimator pipeline does not reproduce the closed-form prediction.",
                file=sys.stderr,
            )
            return 1
        print(f"\nOK: worst deviation {worst:.4f} bit is within {args.tolerance} bit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
