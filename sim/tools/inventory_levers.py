#!/usr/bin/env python3
"""Quantify digital cell-inventory levers against the Power and Area rows (#709).

    python3 sim/tools/inventory_levers.py            # print the table
    python3 sim/tools/inventory_levers.py --write    # regenerate sim/inventory-levers/levers.md
    python3 sim/tools/inventory_levers.py --check    # fail if that file is stale, or if the
                                                     # candidate RTL patch no longer applies

Each lever is an edit to the shipped inventories in
`design/digital_power_estimate.py` (the one copy `layout/floorplan/floorplan.py`
also prices its digital region from), re-priced through that script's own
Liberty parser and the PDK LEF. Nothing here is hand arithmetic on figures:
every column is recomputed from the inventories on each run.

What the columns are, and are not
---------------------------------
- cell area, flops, active and idle: the [DR-0004] Tier 2 inventory estimate,
  at the same corners and activity assumptions `design/digital_power_estimate.py`
  prints by default. Not a measurement.
- projected idle / floorplan: the figure of record (the gate-level digital term
  of `sim/tools/power_rollup.py`, [DR-0023]; `floorplan_area_um2` of
  `layout/floorplan/reports/area.json`) minus the estimate delta, the latter
  divided by the floorplan's `geometry_utilisation` for area. A PROJECTION: the
  committed digital footprint is the routed GDS bounding box, so the floorplan
  figure only moves when synthesis and place-and-route are re-run on the
  changed RTL, and that re-run is not part of this tool.

Levers are cumulative down the "+" rows and are each
also priced alone against the shipped inventory in the "alternatives" rows.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "design"))
sys.path.insert(0, str(REPO / "sim"))

import digital_power_estimate as dpe  # noqa: E402
from harness import pdk as pdk_mod  # noqa: E402  (sim/harness, as digital_power_estimate does)

OUT = REPO / "sim" / "inventory-levers" / "levers.md"
PATCH = REPO / "sim" / "inventory-levers" / "interface-raw-shift-no-reset.patch"
AREA_JSON = REPO / "layout" / "floorplan" / "reports" / "area.json"


def _swap(rows, name_part, old, new, count=None):
    """Replace cell `old` by `new` (optionally changing its count to `count`)."""
    out = []
    for row in rows:
        row = list(row)
        if name_part in row[0] and old in row[1]:
            counts = dict(row[1])
            n = counts.pop(old)
            counts[new] = counts.get(new, 0) + (n if count is None else count)
            row[1] = counts
        out.append(tuple(row))
    return out


def _storage_dffq(rows):
    return _swap(rows, "FIFO storage", "dffrnq_1", "dffq_1")


def _raw_shift_dffq(rows):
    return _swap(rows, "raw packing shift register", "dffrnq_1", "dffq_1")


def _raw_count_5b(rows):
    return [(r[0], {**r[1], "dffrnq_1": 5}, *r[2:]) if r[0] == "raw bit counter" else r
            for r in rows]


def _storage_latch(rows):
    return _swap(rows, "FIFO storage", "dffq_1", "latq_1")


def _read_mux4(rows):
    """reg_rdata's 96 mux2 as 32 mux4 -- inventory arithmetic only."""
    out = []
    for r in rows:
        if r[0] == "reg_rdata read mux":
            r = (r[0], {"mux4_1": 32}, *r[2:])
        out.append(r)
    return out


# (label, transform, applies-to-shipped-RTL?, note)
CANDIDATES = [
    ("storage priced as `dffq_1`", _storage_dffq,
     "model correction, no RTL change: `cond_mem`/`raw_mem` have no reset in "
     "`trng_interface.v`, and synthesis already maps all 128 to `dffq_1`"),
    ("`raw_shift` without reset", _raw_shift_dffq,
     "RTL candidate (`interface-raw-shift-no-reset.patch`): the register is fully "
     "overwritten before it is ever read"),
    ("`raw_bit_count` 5 bits", _raw_count_5b,
     "RTL candidate (same patch): 0..31 needs 5 bits; synthesis had already "
     "pruned the unused top bit, so the synthesized saving is zero"),
]
ALTERNATIVES = [
    ("FIFO storage as `latq_1`", _storage_latch,
     "NOT adopted: needs latch timing under STA/CTS and a restructured write "
     "strobe; changes the sequential style of ratified storage"),
    ("`reg_rdata` mux as `mux4_1`", _read_mux4,
     "NOT adopted: inventory arithmetic only. The inventory prices reg_rdata as "
     "96 full mux2 although most data bits have constant-zero CTRL/STATUS "
     "inputs; synthesis was not run on this variant, so the figure is not credible "
     "as a saving"),
]


def lef_areas(root: Path) -> dict[str, float]:
    lef = root / "libs.ref" / dpe.STDCELL_LIB / "lef" / f"{dpe.STDCELL_LIB}.lef"
    text = lef.read_text()
    out = {}
    for m in re.finditer(r"MACRO (\S+)\n(?:.*\n){0,14}?\s+SIZE ([\d.]+) BY ([\d.]+)", text):
        out[m.group(1).split("__")[-1]] = float(m.group(2)) * float(m.group(3))
    return out


def _iface_rows():
    return list(dpe.INTERFACE_INVENTORY)


def evaluate(root: Path, interface_rows, areas):
    blocks = [(n, interface_rows if n.startswith("interface") else inv, ship)
              for n, inv, ship in dpe.BLOCKS]
    saved = dpe.BLOCKS
    dpe.BLOCKS = blocks
    try:
        idle = dpe.run(root, dpe.CORNER_IDLE, dpe.RAW_RATE_HZ, dpe.DEFAULT_ACTIVITY,
                       dpe.DEFAULT_FANOUT, dpe.DEFAULT_WIRE_CAP_F)
        act = dpe.run(root, dpe.CORNER_ACTIVE, dpe.RAW_RATE_HZ, dpe.DEFAULT_ACTIVITY,
                      dpe.DEFAULT_FANOUT, dpe.DEFAULT_WIRE_CAP_F)
    finally:
        dpe.BLOCKS = saved
    area = 0.0
    for _n, inv, ship in blocks:
        if ship:
            for row in inv:
                for suffix, n in row[1].items():
                    area += n * areas[suffix]
    st = idle["shipped_total"]
    return {
        "cells": st["cells"], "flops": st["flops"], "area": area,
        "idle_a": st["leakage_a"], "active_w": act["shipped_total"]["active_w"],
    }


def figures_of_record():
    """Gate-level idle (A) and the floorplan figure/utilisation, from the tree."""
    out = subprocess.run([sys.executable, str(REPO / "sim/tools/power_rollup.py")],
                         capture_output=True, text=True, check=True).stdout
    m = re.search(r"Worst idle corner: .*?-> ([\d.]+) uA", out)
    d = re.search(r"digital leakage \(MEASURED-at-gate-level\):\s+([\d.]+) uA", out)
    fp = json.loads(AREA_JSON.read_text())
    return {
        "idle_total_a": float(m.group(1)) * 1e-6,
        "idle_digital_a": float(d.group(1)) * 1e-6,
        "floorplan_um2": fp["rollup"]["floorplan_area_um2"],
        "util": fp["geometry_utilisation"],
    }


def build_rows(root: Path):
    areas = lef_areas(root)
    base_rows = _iface_rows()
    base = evaluate(root, base_rows, areas)
    rows = [("baseline (shipped inventory)", base, "", None)]
    cur = base_rows
    for label, fn, note in CANDIDATES:
        cur = fn(cur)
        rows.append((f"+ {label}", evaluate(root, cur, areas), note, None))
    for label, fn, note in ALTERNATIVES:
        # alternatives are priced on top of the cumulative candidate set
        rows.append((f"alt: {label}", evaluate(root, fn(cur), areas), note, None))
    return base, rows


def render(root: Path) -> str:
    base, rows = build_rows(root)
    rec = figures_of_record()
    lines = [
        "<!-- generated by sim/tools/inventory_levers.py --write; do not edit by hand -->",
        "# Digital cell-inventory levers against the Power and Area rows",
        "",
        "Tier 2 inventory estimate ([DR-0004]); see `sim/tools/inventory_levers.py` for",
        "what each column is. The `alt:` rows are priced on top of the cumulative",
        "candidate rows and are each independent of one another.",
        "",
        "| step | cells | flops | cell area um^2 | d area | digital idle nA (est.) | d idle nA "
        "| digital active uW (est.) | projected idle uA | projected floorplan um^2 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for label, r, _note, _ in rows:
        da = r["area"] - base["area"]
        di = (r["idle_a"] - base["idle_a"]) * 1e9
        proj_idle = rec["idle_total_a"] + (r["idle_a"] - base["idle_a"])
        proj_fp = rec["floorplan_um2"] + da / rec["util"]
        lines.append(
            f"| {label} | {r['cells']} | {r['flops']} | {r['area']:.1f} | {da:+.1f} "
            f"| {r['idle_a'] * 1e9:.1f} | {di:+.1f} | {r['active_w'] * 1e6:.3f} "
            f"| {proj_idle * 1e6:.4f} | {proj_fp:.1f} |"
        )
    lines += [
        "",
        f"Figures of record this table is projected from: idle {rec['idle_total_a'] * 1e6:.3f} uA "
        f"(worst corner, `sim/tools/power_rollup.py`), floorplan {rec['floorplan_um2']:.1f} um^2 "
        f"(`layout/floorplan/reports/area.json`, geometry utilisation {rec['util']}). "
        "Rows are projections, not measurements: the committed digital footprint is the "
        "routed GDS bounding box and only moves when synthesis and place-and-route are re-run.",
        "",
        "Rows and why:",
        "",
    ]
    for label, _r, note, _ in rows[1:]:
        lines.append(f"- {label}: {note}")
    lines.append("")
    last = rows[len(CANDIDATES)]
    idle_p = rec["idle_total_a"] + (last[1]["idle_a"] - base["idle_a"])
    fp_p = rec["floorplan_um2"] + (last[1]["area"] - base["area"]) / rec["util"]
    lines.append(
        f"Cumulative candidate set (`{last[0]}`): projected idle {idle_p * 1e6:.3f} uA "
        f"against `< 1 uA` ({'met' if idle_p < 1e-6 else 'still missed'}); projected "
        f"floorplan {fp_p:.0f} um^2 against `< 50000 um^2` "
        f"({'met' if fp_p < 50000 else 'still missed'})."
    )
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--pdk-root", type=Path)
    args = ap.parse_args(argv)
    try:
        root = args.pdk_root or pdk_mod.find_pdk().path
    except pdk_mod.PdkNotFound as exc:
        print(f"gf180mcu PDK not found: {exc}", file=sys.stderr)
        return 2
    text = render(root)
    if args.write:
        OUT.write_text(text)
        print(f"wrote {OUT.relative_to(REPO)}")
        return 0
    if args.check:
        rc = 0
        if not OUT.is_file() or OUT.read_text() != text:
            print(f"STALE  {OUT.relative_to(REPO)}: run with --write")
            rc = 1
        r = subprocess.run(["git", "apply", "--check", str(PATCH)], cwd=REPO,
                           capture_output=True, text=True)
        if r.returncode:
            print(f"STALE  {PATCH.relative_to(REPO)} no longer applies:\n{r.stderr}")
            rc = 1
        if rc == 0:
            print("ok     inventory levers table and candidate RTL patch are current")
        return rc
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
