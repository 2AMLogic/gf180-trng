#!/usr/bin/env python3
"""Whole-block active power broken down by sub-block, at the Power row's binding corner.

    python3 sim/tools/active_power_breakdown.py              # table at 1 MHz and at 2 kHz
    python3 sim/tools/active_power_breakdown.py --reconcile      # reconcile with power_rollup.py
    python3 sim/tools/active_power_breakdown.py --rate 1e6   # one rate only

This splits the figure ``sim/tools/power_rollup.py`` reports (749.4 uW at the
historical 1 MHz sample clock; the same tool's default, the ratified 2 kHz, is
the second column) into sub-blocks, every one read from a committed record:

========================  =====================================================
sub-block                 source
========================  =====================================================
ring 1, ring 2            ``ro-array-core-pvt-q`` record: ``p_rings_w`` split by
                          each ring's measured supply current (``i_r1_a``,
                          ``i_r2_a``) -- the rings sit on their own supply pins
ring buffers, XOR         the same record: ``p_total_w - p_rings_w`` (the
combiner                  ``vdd``-rail remainder), apportioned by the
                          ``ro-array-core-power-split`` record's measured
                          ``p_bufs_w : p_xor_w`` (#811); the two rows sum to the
                          remainder exactly. Without a split record the
                          remainder is one ``ring buffers + XOR`` row, because
                          ``pvt-q`` meters buffers and XOR on one pin
sampler (xsb, xsv)        ``sampler-dff-active-current`` charges x the same
                          corner's ``xo_trans_per_s`` (``power_rollup``'s model)
liveness samplers         GAP at the binding corner (no record); listed with the
                          nearest measured corner as context, NEVER summed
digital: conditioner,     ``digital-power-by-block`` record: OpenSTA per-instance
health tests, interface,  power summed by the as-built netlist's hierarchy
ring-liveness logic       prefix, plus the CTS clock tree and the remainder
========================  =====================================================

Corner convention is ``power_rollup.py``'s: the array and sampler terms are at
the corner where they bind (``ff`` / -40 C / 3.63 V), the digital section at its
own worst corner (``ff_125C_3v60`` / OpenRCX ``max``). The digital figure is a
liberty-power model at a declared uniform activity ([DR-0021] section 3), not a
measured supply current, and the label says so.

Digital power scales with the clock as ``P = leak + (P_1MHz - leak) * rate /
1 MHz`` per sub-block -- the same exact re-derivation ``power_rollup.py`` uses.

``--reconcile`` fails if the sub-block rows do not add up to the rollup's own
terms (same corner, same rate), if the by-block record's whole-section total
drifts from the rollup's digital term, or if a record is missing. It never
fails because the Power row is missed: that is a spec question, not a tool
failure.

[DR-0021]: ../../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import power_rollup as pr  # noqa: E402

BY_BLOCK_GLOB = "*-digital-power-by-block-[0-9]*.md"
#: Split-rail record of the ``vdd`` remainder into buffers and XOR (#811).
SPLIT_GLOB = "*-ro-array-core-power-split-[0-9]*.md"
MERGED_ROW = "ring buffers + XOR"
SPLIT_ROWS = ("ring buffers", "XOR combiner")
#: The split record's own ``p_bufs_w + p_xor_w`` must match the ``pvt-q``
#: remainder it apportions to within this fraction (two runs, minted separately).
SPLIT_RECONCILE_TOL = 0.02
ARRAY_CORNER = "ff/-40/3.63"

#: Rates reported side by side: the historical rate the Power row's 749.4 uW is
#: quoted at, and the currently ratified raw rate.
DEFAULT_RATES = (1e6, pr.RATIFIED_RAW_RATE_BPS)

DIGITAL_ROWS = (
    ("digital: interface", "interface"),
    ("digital: conditioner", "conditioner"),
    ("digital: health tests", "health_test"),
    ("digital: ring-liveness logic", "ring_liveness"),
    ("digital: clock tree", "clock_tree"),
    ("digital: other (buffers, tap/fill)", "top_level_other"),
)

#: Relative tolerance between the by-block record's whole-section total and the
#: rollup's digital term (two different runs of the same analysis, minted
#: separately; they differ only by the later OpenROAD session's float noise).
DIGITAL_RECONCILE_TOL = 1e-3
#: The analog terms are re-derived with the same arithmetic as the rollup.
ANALOG_RECONCILE_TOL = 1e-9


def digital_at_rate(rec: pr.Record, rate_hz: float) -> dict[str, float]:
    """Per-group digital power at ``rate_hz`` (W), exact in rate: leakage is
    constant, everything else is linear in the clock."""
    out = {}
    for _, key in DIGITAL_ROWS:
        total = rec.values[f"p_{key}_total_w"]
        leak = rec.values[f"p_{key}_leakage_w"]
        out[key] = leak + (total - leak) * (rate_hz / pr.DIGITAL_MEASUREMENT_RATE_HZ)
    return out


def load_split(array: pr.Record):
    """The newest valid split record at the array's corner, or ``None``."""
    recs = [r for r in pr.load(SPLIT_GLOB)
            if (r.process, r.temp_c, r.vdd) == (array.process, array.temp_c, array.vdd)]
    return recs[-1] if recs else None


def split_gap(array: pr.Record, split: pr.Record) -> float:
    """Signed fraction by which the split record's buffers + XOR exceed the
    array record's ``p_total_w - p_rings_w`` remainder."""
    remainder = abs(array.values["p_total_w"]) - abs(array.values["p_rings_w"])
    tree = abs(split.values["p_bufs_w"]) + abs(split.values["p_xor_w"])
    return (tree - remainder) / remainder


def analog_terms(array: pr.Record, sampler: pr.Record, rate_hz: float,
                 split: pr.Record | None = None) -> dict[str, float]:
    p_total = abs(array.values["p_total_w"])
    p_rings = abs(array.values["p_rings_w"])
    i1, i2 = abs(array.values["i_r1_a"]), abs(array.values["i_r2_a"])
    s = pr.sampler_active(sampler, array.values["xo_trans_per_s"], rate_hz)
    remainder = p_total - p_rings
    out = {
        "ring 1": p_rings * i1 / (i1 + i2),
        "ring 2": p_rings * i2 / (i1 + i2),
        "sampler (xsb, xsv)": s["p_total_w"],
        "_array_total": p_total,
    }
    if split is None:
        out[MERGED_ROW] = remainder
    else:
        bufs, xor = abs(split.values["p_bufs_w"]), abs(split.values["p_xor_w"])
        out[SPLIT_ROWS[0]] = remainder * bufs / (bufs + xor)
        out[SPLIT_ROWS[1]] = remainder * xor / (bufs + xor)
    return out


def breakdown(rate_hz: float, *, arrays=None, samplers=None, by_block=None, split=None) -> dict:
    """Rows ``[(label, watts, provenance)]`` plus the reconciliation figures."""
    arrays = arrays or pr.by_corner(pr.load(pr.ARRAY_GLOBS), prefer="pvt-q")
    samplers = samplers or pr.by_corner(pr.load(pr.SAMPLER_ACTIVE_GLOB))
    if by_block is None:
        recs = pr.load(BY_BLOCK_GLOB)
        if not recs:
            raise RuntimeError(f"no records match sim/records/{BY_BLOCK_GLOB}")
        by_block = recs[-1]
    array, sampler = arrays[ARRAY_CORNER], samplers[ARRAY_CORNER]
    # ``split=False`` forces the single merged row (a comparison baseline).
    split = load_split(array) if split is None else (split or None)
    a = analog_terms(array, sampler, rate_hz, split)
    d = digital_at_rate(by_block, rate_hz)
    tree_rows = ([(MERGED_ROW, a[MERGED_ROW], "MEASURED")] if split is None else
                 [(label, a[label], "MEASURED (split-rail)") for label in SPLIT_ROWS])
    rows = [
        ("ring 1", a["ring 1"], "MEASURED"),
        ("ring 2", a["ring 2"], "MEASURED"),
        *tree_rows,
        ("sampler (xsb, xsv)", a["sampler (xsb, xsv)"], "MEASURED"),
    ] + [(label, d[key], "MEASURED-at-gate-level") for label, key in DIGITAL_ROWS]
    total = sum(w for _, w, _ in rows)
    return {"rows": rows, "total": total, "array_total": a["_array_total"],
            "sampler": a["sampler (xsb, xsv)"], "digital": sum(d.values()),
            "array_record": array.stem, "sampler_record": sampler.stem,
            "by_block_record": by_block.stem,
            "split_record": split.stem if split else None,
            "split_gap": split_gap(array, split) if split else None}


def liveness_context(rate_hz: float) -> str:
    """The liveness samplers' nearest measured term, for context only."""
    samplers = pr.by_corner(pr.load(pr.SAMPLER_ACTIVE_GLOB))
    lives = pr.by_corner(pr.load(pr.LIVENESS_GLOB))
    if ARRAY_CORNER in lives:
        return f"measured at {ARRAY_CORNER}"
    for corner, rec in lives.items():
        try:
            f_clk = rate_hz
            q = samplers[corner].values.get("q_clkcyc_xsv_c")
            term = pr.liveness_active(rec, f_clk, abs(q))
        except (KeyError, TypeError):
            continue
        return (f"GAP at {ARRAY_CORNER}; nearest record {corner}: "
                f"{pr._w(term['p_total_w'])} (flops + array loading), NOT in the total")
    return f"GAP at {ARRAY_CORNER}, no liveness record anywhere"


def reconcile(rate_hz: float) -> list[str]:
    """Problems found re-deriving the rollup's terms; empty when everything agrees."""
    problems = []
    bd = breakdown(rate_hz)
    arrays = pr.by_corner(pr.load(pr.ARRAY_GLOBS), prefer="pvt-q")
    samplers = pr.by_corner(pr.load(pr.SAMPLER_ACTIVE_GLOB))
    array, sampler = arrays[ARRAY_CORNER], samplers[ARRAY_CORNER]
    rollup_array = abs(array.values["p_total_w"])
    rollup_sampler = pr.sampler_active(sampler, array.values["xo_trans_per_s"], rate_hz)["p_total_w"]
    rollup_digital = pr.digital_measured(rate_hz)["active_w"]
    ring_rows = sum(w for label, w, _ in bd["rows"]
                    if label in ("ring 1", "ring 2", MERGED_ROW, *SPLIT_ROWS))
    if abs(ring_rows - rollup_array) > ANALOG_RECONCILE_TOL * rollup_array:
        problems.append(f"array rows {ring_rows:.6e} W != rollup array term {rollup_array:.6e} W")
    if abs(bd["sampler"] - rollup_sampler) > ANALOG_RECONCILE_TOL * rollup_sampler:
        problems.append(f"sampler {bd['sampler']:.6e} W != rollup {rollup_sampler:.6e} W")
    if bd["split_record"] is not None and abs(bd["split_gap"]) > SPLIT_RECONCILE_TOL:
        problems.append(
            f"{bd['split_record']} buffers + XOR differs from {bd['array_record']}'s "
            f"p_total_w - p_rings_w by {bd['split_gap']:+.2%} (> {SPLIT_RECONCILE_TOL:.0%})")
    gap = abs(bd["digital"] - rollup_digital) / rollup_digital
    if gap > DIGITAL_RECONCILE_TOL:
        problems.append(
            f"by-block digital {bd['digital']:.6e} W differs from the rollup's digital term "
            f"{rollup_digital:.6e} W by {gap:.2%} (> {DIGITAL_RECONCILE_TOL:.1%})")
    return problems


def _uw(w: float) -> str:
    return f"{w * 1e6:9.2f}"


def render(rates) -> str:
    bds = {r: breakdown(r) for r in rates}
    lines = [
        f"corner: array + sampler at {ARRAY_CORNER} (binds); digital at ff_125C_3v60 / rc-max "
        "(its own worst corner), per power_rollup.py's convention",
        f"records: {bds[rates[0]]['array_record']}, {bds[rates[0]]['sampler_record']}, "
        f"{bds[rates[0]]['by_block_record']}",
    ]
    if bds[rates[0]]["split_record"]:
        lines.append(
            f"buffers / XOR split: {bds[rates[0]]['split_record']}, its buffers + XOR is "
            f"{bds[rates[0]]['split_gap']:+.2%} from the array record's remainder "
            "(rows are apportioned so they sum to that remainder exactly)")
    lines += [
        "",
        f"| {'sub-block':<36} | {'provenance':<22} |"
        + "".join(f" {f'{r:g} Hz uW':>14} | share |" for r in rates),
    ]
    lines.append("|" + "|".join(["-" * 38, "-" * 24] + ["-" * 15, "-" * 7] * len(rates)) + "|")
    for i, (label, _, prov) in enumerate(bds[rates[0]]["rows"]):
        cells = ""
        for r in rates:
            w = bds[r]["rows"][i][1]
            cells += f" {_uw(w):>14} | {w / bds[r]['total']:5.1%} |"
        lines.append(f"| {label:<36} | {prov:<22} |{cells}")
    totals = "".join(f" {_uw(bds[r]['total']):>14} | {1.0:5.1%} |" for r in rates)
    lines.append(f"| {'TOTAL (liveness samplers excluded)':<36} | {'':<22} |{totals}")
    vs = "".join(f" {bds[r]['total'] / pr.ACTIVE_BUDGET_W:>13.1%}  | {'':5} |" for r in rates)
    lines.append(f"| {'vs the < 500 uW row':<36} | {'':<22} |{vs}")
    lines += ["", f"liveness samplers (xsr1, xsr2): {liveness_context(rates[0])}"]
    lines += ["", "LEVERS (arithmetic on the rows above; each is a model figure, none is silicon)"]
    hi, lo = max(rates), min(rates)
    d_hi, d_lo = bds[hi]["digital"], bds[lo]["digital"]
    lines.append(
        f"  1. digital clock rate {hi:g} Hz -> {lo:g} Hz returns {_uw(d_hi - d_lo).strip()} uW "
        f"(digital {_uw(d_hi).strip()} -> {_uw(d_lo).strip()} uW); the whole block goes "
        f"{_uw(bds[hi]['total']).strip()} -> {_uw(bds[lo]['total']).strip()} uW"
    )
    rows_hi = {label: w for label, w, _ in bds[hi]["rows"]}
    biggest = sorted(((w, label) for label, w in rows_hi.items() if label.startswith("digital")),
                     reverse=True)[:2]
    for n, (w, label) in enumerate(biggest, start=2):
        lines.append(f"  {n}. {label} is {_uw(w).strip()} uW at {hi:g} Hz "
                     f"({w / bds[hi]['total']:.1%} of the block); an upper bound on what trimming "
                     "it could return, before any clock gating")
    if SPLIT_ROWS[0] in rows_hi:
        tree = rows_hi[SPLIT_ROWS[0]] + rows_hi[SPLIT_ROWS[1]]
        lines.append(
            f"  3b. ring buffers {_uw(rows_hi[SPLIT_ROWS[0]]).strip()} uW + XOR combiner "
            f"{_uw(rows_hi[SPLIT_ROWS[1]]).strip()} uW = {_uw(tree).strip()} uW at {hi:g} Hz "
            f"({tree / bds[hi]['total']:.1%} of the block); an upper bound on what any trim "
            "there could return -- the whole of their power, and they must still drive the sampler")
    lines.append(
        f"  4. rings are {_uw(rows_hi['ring 1'] + rows_hi['ring 2']).strip()} uW "
        f"({(rows_hi['ring 1'] + rows_hi['ring 2']) / bds[hi]['total']:.1%}) and are the entropy "
        "source itself; a lever there trades against entropy rate, not a free return"
    )
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rate", type=float, action="append",
                    help="sample-clock rate in Hz (repeatable; default 1e6 and 2e3)")
    ap.add_argument("--reconcile", action="store_true",
                    help="reconcile the rows with power_rollup.py; exit 1 on disagreement")
    args = ap.parse_args(argv)
    rates = tuple(args.rate) if args.rate else DEFAULT_RATES
    try:
        print(render(rates))
        if args.reconcile:
            problems = [p for r in rates for p in reconcile(r)]
            for p in problems:
                print(f"FAIL: {p}", file=sys.stderr)
            if problems:
                return 1
            print("\nOK: sub-block rows reconcile with power_rollup.py's terms at every rate shown")
    except (RuntimeError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
