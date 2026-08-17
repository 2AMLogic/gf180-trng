#!/usr/bin/env python3
"""Fmax, area and power of the digital section across the corner set, from
the committed gate-level records.

    python3 sim/tools/digital_corner_characterization.py           # the tables
    python3 sim/tools/digital_corner_characterization.py --check   # gate the findings
    python3 sim/tools/digital_corner_characterization.py --estimate  # + the
                                                          # library-based estimate

Like ``sim/tools/power_rollup.py`` and ``sim/tools/worst_corner_entropy.py``
this is a *derivation*, not a run: it reads evidence already committed under
``sim/records/`` (the ``digital-sta-power`` family, ``level: gate`` per
[DR-0021]) plus two committed report artefacts, and does arithmetic on them.
It needs no PDK, no ``openroad`` and no ``klt``, writes nothing, and is what
``npm run check:spec`` runs to keep
``sim/characterization-digital-sta-area-power.md`` from going stale.

The three legs
--------------
**Timing.** Per-corner worst setup and hold slack against the 50 ns (20 MHz)
constraint the place-and-route run itself used, and the Fmax each corner
supports (bisected on the clock period, not extrapolated). The binding corner
is named on both the setup and the hold side, because they are different
corners and always will be: setup binds slow/hot/low-supply, hold binds
fast/cold/high-supply.

**Area.** The placed standard-cell area OpenROAD reports from the committed
routed DEF, against the bottom-up inventory estimate in
``layout/floorplan/reports/area.json`` that predates any synthesis. Both are
cell area, so they are directly comparable; the *die* area in
``layout/digital/reports/place_and_route.json`` is not comparable to either
(it follows arithmetically from that run's own 40 % utilization target) and
this tool refuses to present it as if it were.

**Power.** Per-corner total, per-group and leakage power at two operating
points -- the 20 MHz implementation constraint and [DR-0003]'s ratified 1 MHz
raw rate -- and, with ``--estimate`` (which needs the PDK), the same corners'
figures from ``design/digital_power_estimate.py``, the library-based estimate
this measurement supersedes. The comparison is deliberately made at 1 MHz on
both sides: comparing a 20 MHz measurement against a 1 MHz estimate would
mostly measure the clock rate.

What this tool does not do
--------------------------
It does not edit, propose or evaluate a README row. The digital section's
area and idle-current overages are already routed by [DR-0019] and [DR-0017];
the area row itself is #150's decision, and nothing here changes it. This
tool supplies the measurement, states it against the row, and stops there.

[DR-0003]: ../../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0017]: ../../spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
[DR-0019]: ../../spec/decision-records/DR-0019-area-row-versus-output-fifo-dominated-digital-section.md
[DR-0021]: ../../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"
RECORD_GLOB = "*-digital-sta-power-[0-9]*.md"

PNR_REPORT = REPO_ROOT / "layout" / "digital" / "reports" / "place_and_route.json"
FLOORPLAN_AREA = REPO_ROOT / "layout" / "floorplan" / "reports" / "area.json"
ESTIMATE_SCRIPT = REPO_ROOT / "design" / "digital_power_estimate.py"

#: The ratified README area row, in um^2. Quoted, never enforced: this tool
#: reports the measured area against the row and leaves the row to #150.
AREA_BUDGET_UM2 = 50_000.0

#: [DR-0003]'s ratified raw rate. The operating point the power comparison is
#: made at, because it is the one the library-based estimate prices.
RATIFIED_RATE_HZ = 1e6

#: The findings the committed records support, as recorded in
#: ``sim/characterization-digital-sta-area-power.md``. ``--check`` gates on
#: the records still supporting *these*, so that a re-run that moves a number
#: fails here rather than leaving a stale figure in the document. Written
#: after the measurement, exactly as ``sim/tools/sampler_bit_bias_variants.py``
#: writes its own ``RECORDED_VERDICT``.
RECORDED = {
    "corner_count": 15,
    "setup_binding_corner": "ss_125C_3v00/rc-max",
    "setup_binding_slack_ns": 23.000,
    "hold_binding_corner": "ff_n40C_3v60/rc-min",
    "hold_binding_slack_ns": 0.707,
    "fmax_floor_mhz": 37.037,
    "fmax_floor_corner": "ss_125C_3v00/rc-max",
    "cell_area_um2": 113_087.9,
    "area_ratio_vs_inventory": 1.5183,
    "power_1mhz_max_w": 6.9514e-4,
    "power_1mhz_max_corner": "ff_125C_3v60/rc-max",
    "leakage_max_w": 1.00258e-5,
    "leakage_max_corner": "ff_125C_3v60",
    "leakage_max_current_a": 2.78495e-6,
}

#: Fractional tolerance for the numeric gates above. The analysis is
#: deterministic (no seeds, no solver) but not bit-portable: a different
#: OpenROAD build or a different PDK revision moves the last digits. 1 % is
#: far tighter than any real regression and far looser than that noise.
TOLERANCE = 0.01

_VALUE = re.compile(r"^- `([a-z0-9_]+)`:\s*(-?[\d.]+(?:e[-+]?\d+)?)", re.M)
_FIELD = {
    "liberty": re.compile(r"^\s*liberty:\s*(\S+)\s*$", re.M),
    "interconnect": re.compile(r"^\s*interconnect:\s*(\w+)", re.M),
    "process": re.compile(r"^\s*process:\s*(\w+)\s*$", re.M),
    "temperature": re.compile(r"^\s*temperature:\s*(-?[\d.]+)", re.M),
    "voltage": re.compile(r"^\s*voltage:\s*([\d.]+)\s*V", re.M),
    "level": re.compile(r"^level:\s*(\w+)", re.M),
    "status": re.compile(r"^status:\s*(\w+)", re.M),
    "openroad": re.compile(r'^\s*openroad:\s*"([^"]+)"', re.M),
    "netlist_sha": re.compile(r"^netlist:\s*\n\s*path:.*\n\s*sha:\s*([0-9a-f]+)", re.M),
}


class RecordError(RuntimeError):
    """A record this tool must read is missing, malformed or not gate-level."""


class Record:
    """One committed ``digital-sta-power`` record."""

    def __init__(self, path: Path) -> None:
        text = path.read_text()
        self.path = path
        self.stem = path.stem
        self.values = {m.group(1): float(m.group(2)) for m in _VALUE.finditer(text)}
        self.fields = {}
        for name, pattern in _FIELD.items():
            m = pattern.search(text)
            if m is None and name not in ("netlist_sha", "openroad"):
                raise RecordError(f"{self.stem}: no {name} in the frontmatter")
            self.fields[name] = m.group(1) if m else None
        if self.fields["level"] != "gate":
            raise RecordError(
                f"{self.stem}: level is {self.fields['level']!r}, not 'gate' -- "
                "this tool aggregates gate-level records only (DR-0021)"
            )

    @property
    def liberty(self) -> str:
        # `corner.liberty` is the full deck name (<library>__<corner>).
        return self.fields["liberty"].split("__")[-1]

    @property
    def rc(self) -> str:
        return self.fields["interconnect"]

    @property
    def corner(self) -> str:
        return f"{self.liberty}/rc-{self.rc}"

    @property
    def valid(self) -> bool:
        return self.fields["status"] == "valid"

    def v(self, key: str) -> float:
        if key not in self.values:
            raise RecordError(f"{self.stem}: no `{key}` in the Result section")
        return self.values[key]


def resolve_pdk_root() -> Path:
    """The installed PDK root, through the repo's one resolver
    (``sim/harness/pdk.py``) -- never a hardcoded path. Raises
    ``RecordError`` when no install resolves, so the PDK-dependent legs can
    be skipped rather than guessed at."""
    sys.path.insert(0, str(REPO_ROOT / "sim"))
    try:
        from harness import pdk as pdk_mod  # noqa: PLC0415
        found = pdk_mod.find_pdk()
    except Exception as exc:  # pragma: no cover - depends on the machine
        raise RecordError(f"no gf180mcu PDK install found: {exc}") from exc
    if found is None:
        raise RecordError("no gf180mcu PDK install found (see sim/harness/pdk.py)")
    return Path(found.path)


def load(records_dir: Path = RECORDS) -> list[Record]:
    records = [Record(p) for p in sorted(records_dir.glob(RECORD_GLOB))]
    if not records:
        raise RecordError(
            f"no records matching {RECORD_GLOB} under {records_dir} -- run "
            "`python3 sim/tb/digital-sta-power/run_sta.py` first"
        )
    live = [r for r in records if r.valid]
    # Latest record per corner wins: a re-run mints a new stem (append-only),
    # and sorted() puts it later.
    by_corner: dict[str, Record] = {}
    for rec in live:
        by_corner[rec.corner] = rec
    return [by_corner[k] for k in sorted(by_corner)]


# --------------------------------------------------------------------------- #
# Derivations
# --------------------------------------------------------------------------- #


def timing(records: list[Record]) -> dict:
    setup = min(records, key=lambda r: r.v("worst_setup_slack_ns"))
    hold = min(records, key=lambda r: r.v("worst_hold_slack_ns"))
    fmax = min(records, key=lambda r: r.v("fmax_bisect_mhz"))
    return {
        "rows": [
            {
                "corner": r.corner,
                "setup_ns": r.v("worst_setup_slack_ns"),
                "hold_ns": r.v("worst_hold_slack_ns"),
                "tns_setup_ns": r.v("tns_setup_ns"),
                "skew_ns": r.v("clock_skew_setup_ns"),
                "fmax_mhz": r.v("fmax_bisect_mhz"),
                "fmax_linear_mhz": r.v("fmax_linear_mhz"),
                "min_period_ns": r.v("min_period_ns"),
            }
            for r in records
        ],
        "setup_binding": setup.corner,
        "setup_binding_slack_ns": setup.v("worst_setup_slack_ns"),
        "hold_binding": hold.corner,
        "hold_binding_slack_ns": hold.v("worst_hold_slack_ns"),
        "fmax_floor_corner": fmax.corner,
        "fmax_floor_mhz": fmax.v("fmax_bisect_mhz"),
        "constraint_ns": records[0].v("constraint_period_ns"),
        "constraint_mhz": records[0].v("constraint_freq_mhz"),
        "closes_everywhere": all(
            r.v("worst_setup_slack_ns") > 0 and r.v("worst_hold_slack_ns") > 0
            for r in records
        ),
        "bisect_vs_linear_max_rel": max(
            abs(r.v("fmax_bisect_mhz") - r.v("fmax_linear_mhz"))
            / r.v("fmax_bisect_mhz")
            for r in records
        ),
        "unconstrained_endpoints": records[0].v("unconstrained_endpoints"),
    }


def area(records: list[Record]) -> dict:
    """Measured placed cell area against the pre-synthesis inventory estimate.

    Both sides are *cell* area -- the sum of the standard cells' own
    footprints -- which is the only comparison the two artefacts support.
    Neither is a die area, and the die figure in the place-and-route report
    is this run's own 40 %-utilization input rather than a result, so it is
    reported here as context and never differenced against the row.
    """
    measured = {r.v("cell_area_um2") for r in records}
    if max(measured) - min(measured) > 1.0:
        raise RecordError(
            "the records disagree on placed cell area "
            f"({min(measured):.1f} .. {max(measured):.1f} um^2); cell area is "
            "corner-independent, so this means two different designs were "
            "measured and the family must not be aggregated"
        )
    cell_area = records[0].v("cell_area_um2")
    fp = json.loads(FLOORPLAN_AREA.read_text())
    digital = next(r for r in fp["regions"] if r["id"] == "digital")
    pnr = json.loads(PNR_REPORT.read_text())
    return {
        "measured_cell_area_um2": cell_area,
        "measured_utilization_pct": records[0].v("utilization_pct"),
        "measured_instances": pnr["checks"]["components"]["placed"],
        "measured_library": "gf180mcu_fd_sc_mcu9t5v0 (9-track)",
        "estimate_cell_area_um2": digital["cell_area_um2"],
        "estimate_cells": digital["cell_count"],
        "estimate_library": f"{fp['stdcell_library']} (7-track)",
        "estimate_placed_60pct_um2": digital["placed_area_um2"]["60pct"],
        "estimate_guarded_um2": digital["guarded_area_um2"],
        "ratio": cell_area / digital["cell_area_um2"],
        "delta_um2": cell_area - digital["cell_area_um2"],
        "die_area_um2": pnr["die_area_um2"],
        "die_utilization_target_pct": pnr["request"]["floorplan"]["utilization_pct"],
        "budget_um2": AREA_BUDGET_UM2,
        "share_of_budget_pct": cell_area / AREA_BUDGET_UM2 * 100.0,
        "implied_die_at_60pct_um2": cell_area / 0.60,
        "implied_die_at_80pct_um2": cell_area / 0.80,
    }


#: The as-built netlist, and the two standard-cell libraries the measured and
#: estimated area figures are priced in. Used only by ``area_crosscheck``,
#: which needs the PDK.
PNR_NETLIST = REPO_ROOT / "layout" / "digital" / "trng_top.pnr.v"
MEASURED_LIBRARY = "gf180mcu_fd_sc_mcu9t5v0"
ESTIMATE_LIBRARY = "gf180mcu_fd_sc_mcu7t5v0"
CROSSCHECK_CORNER = "tt_025C_3v30"

_INSTANCE = re.compile(rf"{MEASURED_LIBRARY}__(\w+)\s+\S+\s*\(")


def _library_cell_areas(library: str, pdk_root: Path) -> dict[str, float]:
    """``area :`` per cell, from a liberty deck. Cell *area* is a physical
    property and is identical at every corner of a library, so which deck is
    read does not matter -- ``CROSSCHECK_CORNER`` is named only so the read
    is reproducible."""
    path = (pdk_root / "libs.ref" / library / "lib"
            / f"{library}__{CROSSCHECK_CORNER}.lib")
    if not path.is_file():
        raise RecordError(f"liberty deck not found at {path}")
    text = path.read_text(errors="replace")
    pattern = re.compile(
        rf"cell\({library}__(\w+)\)\s*\{{\s*\n\s*area\s*:\s*([\d.]+)"
    )
    return {m.group(1): float(m.group(2)) for m in pattern.finditer(text)}


def area_crosscheck(measured_cell_area_um2: float, estimate_cell_area_um2: float,
                    estimate_cells: int, pdk_root: Path) -> dict:
    """Split the area miss into a cell-count term and a track-height term.

    The measured figure prices 2499 real 9-track instances; the inventory
    estimate prices 1655 assumed 7-track cells. Those differ on two axes at
    once, and quoting one ratio hides which axis carries it. Pricing the
    *same as-built netlist* against the 7-track library separates them:

        estimate (7t, inventory)  --cell count/mix-->  as-built (7t)
                                  --track height-->    as-built (9t) = measured

    Every cell in the as-built netlist has a same-named counterpart in the
    7-track library (both libraries ship the same 229 cells at different row
    heights), so the intermediate figure needs no substitution rules.
    """
    text = PNR_NETLIST.read_text(errors="replace")
    histogram: dict[str, int] = {}
    for name in _INSTANCE.findall(text):
        histogram[name] = histogram.get(name, 0) + 1
    instances = sum(histogram.values())
    measured_areas = _library_cell_areas(MEASURED_LIBRARY, pdk_root)
    estimate_areas = _library_cell_areas(ESTIMATE_LIBRARY, pdk_root)
    missing = sorted(c for c in histogram if c not in estimate_areas)
    if missing:
        raise RecordError(
            f"{len(missing)} cell(s) in the as-built netlist have no "
            f"{ESTIMATE_LIBRARY} counterpart ({', '.join(missing[:5])}) -- the "
            "two libraries are no longer cell-for-cell comparable and this "
            "cross-check must not be presented as if they were"
        )
    as_built_9t = sum(n * measured_areas[c] for c, n in histogram.items())
    as_built_7t = sum(n * estimate_areas[c] for c, n in histogram.items())
    return {
        "instances": instances,
        "as_built_9t_um2": as_built_9t,
        "as_built_7t_um2": as_built_7t,
        "liberty_vs_openroad_rel": (
            abs(as_built_9t - measured_cell_area_um2) / measured_cell_area_um2
        ),
        "cell_count_term": as_built_7t / estimate_cell_area_um2,
        "track_height_term": as_built_9t / as_built_7t,
        "mean_cell_um2_measured_9t": as_built_9t / instances,
        "mean_cell_um2_measured_7t": as_built_7t / instances,
        "mean_cell_um2_estimate_7t": estimate_cell_area_um2 / estimate_cells,
    }


def power(records: list[Record]) -> dict:
    at_1mhz = max(records, key=lambda r: r.v("p_total_1mhz_w"))
    at_20mhz = max(records, key=lambda r: r.v("p_total_20mhz_w"))
    leaky = max(records, key=lambda r: r.v("p_leakage_w"))
    return {
        "rows": [
            {
                "corner": r.corner,
                "p_1mhz_w": r.v("p_total_1mhz_w"),
                "p_20mhz_w": r.v("p_total_20mhz_w"),
                "clock_1mhz_w": r.v("p_clock_1mhz_w"),
                "seq_1mhz_w": r.v("p_sequential_1mhz_w"),
                "comb_1mhz_w": r.v("p_combinational_1mhz_w"),
                "leakage_w": r.v("p_leakage_w"),
                "leakage_a": r.v("i_leakage_a"),
                "wire_cap_per_net_f": r.v("wire_cap_per_net_f"),
            }
            for r in records
        ],
        "max_1mhz_corner": at_1mhz.corner,
        "max_1mhz_w": at_1mhz.v("p_total_1mhz_w"),
        "max_20mhz_corner": at_20mhz.corner,
        "max_20mhz_w": at_20mhz.v("p_total_20mhz_w"),
        "max_leakage_corner": leaky.corner,
        "max_leakage_w": leaky.v("p_leakage_w"),
        "max_leakage_a": leaky.v("i_leakage_a"),
        "activity_note": "0.25 transitions/net/cycle, duty 0.5 (declared, uniform)",
    }


def estimate(corner: str) -> dict:
    """``design/digital_power_estimate.py`` at one liberty corner, as JSON.

    Needs the PDK's 7-track liberty libraries. Raises ``RecordError`` (not a
    bare exception) when it cannot run, so callers can degrade to the
    record-only legs the way ``sim/tools/power_rollup.py`` does.
    """
    proc = subprocess.run(
        [
            sys.executable, str(ESTIMATE_SCRIPT), "--corner", corner,
            "--raw-rate", repr(RATIFIED_RATE_HZ), "--json",
        ],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        raise RecordError(
            f"design/digital_power_estimate.py failed at {corner} "
            f"({proc.returncode}) -- it needs the PDK's 7-track liberty "
            f"libraries:\n{proc.stderr.strip()}"
        )
    return json.loads(proc.stdout)


def estimate_comparison(records: list[Record]) -> list[dict]:
    """Measured vs estimated power at 1 MHz, per liberty corner.

    Two estimate columns, not one, because the synthesized netlist settles a
    question the estimate had to assume: it contains **no integrated clock
    gates at all** (the RTL's enables became feedback multiplexers), so the
    estimate's headline -- which credits the two output FIFOs with clock
    gating at 1/256 and 1/2048 duty -- is not a model of what was built. The
    estimate's own ungated variant (``interface_mux_feedback``) is the
    like-for-like row, and both are shown so the comparison cannot be read as
    turning on which one is picked.
    """
    out = []
    by_liberty: dict[str, Record] = {}
    for r in records:
        # `nom` interconnect: the middle parasitic corner, and the deck the
        # place-and-route run itself used.
        if r.rc == "nom":
            by_liberty[r.liberty] = r
    for liberty, rec in sorted(by_liberty.items()):
        est = estimate(liberty)
        shipped = est["shipped_total"]
        gated_w = shipped["active_w"]
        ungated = est["interface_mux_feedback"]
        interface = est["blocks"]["interface (#26)"]
        ungated_w = (
            shipped["active_w"]
            - interface["p_dynamic_w"] - interface["leak_default_w"]
            + ungated["p_dynamic_w"] + ungated["leak_default_w"]
        )
        measured = rec.v("p_total_1mhz_w")
        out.append({
            "corner": liberty,
            "measured_w": measured,
            "measured_leakage_w": rec.v("p_leakage_w"),
            "estimate_gated_w": gated_w,
            "estimate_ungated_w": ungated_w,
            "estimate_leakage_w": shipped["leakage_w"],
            "ratio_vs_gated": measured / gated_w,
            "ratio_vs_ungated": measured / ungated_w,
            "leakage_ratio": rec.v("p_leakage_w") / shipped["leakage_w"],
            "estimate_cells": shipped["cells"],
            "estimate_flops": shipped["flops"],
            "estimate_wire_cap_f": est["wire_cap_f"],
            "measured_wire_cap_per_net_f": rec.v("wire_cap_per_net_f"),
        })
    return out


# --------------------------------------------------------------------------- #
# Presentation
# --------------------------------------------------------------------------- #


def _w(x: float) -> str:
    for unit, scale in (("W", 1.0), ("mW", 1e-3), ("uW", 1e-6), ("nW", 1e-9)):
        if abs(x) >= scale:
            return f"{x / scale:.4g} {unit}"
    return f"{x:.3g} W"


def _a(x: float) -> str:
    for unit, scale in (("A", 1.0), ("mA", 1e-3), ("uA", 1e-6), ("nA", 1e-9)):
        if abs(x) >= scale:
            return f"{x / scale:.4g} {unit}"
    return f"{x:.3g} A"


def report(records: list[Record], with_estimate: bool) -> None:
    t = timing(records)
    a = area(records)
    p = power(records)

    print(f"digital section, {len(records)} gate-level corners "
          f"(DR-0021), OpenROAD {records[0].fields['openroad']}")
    print(f"DUT: layout/digital/trng_top.def @ {records[0].fields['netlist_sha'][:12]} "
          f"-- {a['measured_instances']} placed instances, {a['measured_library']}")
    print()

    print(f"== Timing (constraint {t['constraint_ns']:g} ns = "
          f"{t['constraint_mhz']:g} MHz, propagated clock, extracted parasitics) ==")
    print(f"{'corner':28s} {'setup':>9s} {'hold':>8s} {'skew':>7s} "
          f"{'Tmin':>8s} {'Fmax':>9s}")
    for row in t["rows"]:
        print(f"{row['corner']:28s} {row['setup_ns']:8.3f}n {row['hold_ns']:7.3f}n "
              f"{row['skew_ns']:6.3f}n {row['min_period_ns']:7.3f}n "
              f"{row['fmax_mhz']:8.2f}M")
    print(f"  setup binds at {t['setup_binding']}: {t['setup_binding_slack_ns']:.3f} ns")
    print(f"  hold  binds at {t['hold_binding']}: {t['hold_binding_slack_ns']:.3f} ns")
    print(f"  Fmax floor     {t['fmax_floor_corner']}: {t['fmax_floor_mhz']:.2f} MHz")
    print(f"  every corner closes at {t['constraint_mhz']:g} MHz: {t['closes_everywhere']}")
    print(f"  bisected vs 1/(T-WNS) Fmax agree to "
          f"{t['bisect_vs_linear_max_rel'] * 100:.4f} % worst case")
    print(f"  unconstrained endpoints (no set_input/output_delay): "
          f"{t['unconstrained_endpoints']:.0f}")
    print()

    print("== Area (standard-cell area; NOT die area) ==")
    print(f"  measured, placed  {a['measured_cell_area_um2']:10.1f} um^2  "
          f"({a['measured_instances']} instances, {a['measured_library']}, "
          f"{a['measured_utilization_pct']:.1f} % achieved utilization)")
    print(f"  inventory estimate{a['estimate_cell_area_um2']:10.1f} um^2  "
          f"({a['estimate_cells']} cells, {a['estimate_library']})")
    print(f"  delta             {a['delta_um2']:+10.1f} um^2  "
          f"= {a['ratio']:.3f}x the estimate")
    print(f"  vs the < 0.05 mm^2 README row: {a['share_of_budget_pct']:.1f} % on "
          f"cell area alone (row untouched -- #150/DR-0019)")
    print(f"  implied die at 60/80 % utilization: "
          f"{a['implied_die_at_60pct_um2']:.0f} / "
          f"{a['implied_die_at_80pct_um2']:.0f} um^2")
    print(f"  this run's own die {a['die_area_um2']:.0f} um^2 follows from its "
          f"{a['die_utilization_target_pct']:g} % utilization target -- an input, "
          "not a result")
    print()

    print(f"== Power ({p['activity_note']}) ==")
    print(f"{'corner':28s} {'@1MHz':>10s} {'@20MHz':>10s} {'clock':>9s} "
          f"{'leakage':>9s} {'I_leak':>9s}")
    for row in p["rows"]:
        print(f"{row['corner']:28s} {_w(row['p_1mhz_w']):>10s} "
              f"{_w(row['p_20mhz_w']):>10s} {_w(row['clock_1mhz_w']):>9s} "
              f"{_w(row['leakage_w']):>9s} {_a(row['leakage_a']):>9s}")
    print(f"  active power binds at {p['max_1mhz_corner']}: "
          f"{_w(p['max_1mhz_w'])} at 1 MHz, {_w(p['max_20mhz_w'])} at 20 MHz "
          f"({p['max_20mhz_corner']})")
    print(f"  leakage binds at {p['max_leakage_corner']}: "
          f"{_w(p['max_leakage_w'])} = {_a(p['max_leakage_a'])}")
    print()

    if not with_estimate:
        print("(--estimate adds the library-based estimate comparison; it needs "
              "the PDK's 7-track liberty libraries)")
        return

    x = area_crosscheck(
        a["measured_cell_area_um2"], a["estimate_cell_area_um2"],
        a["estimate_cells"], resolve_pdk_root(),
    )
    print("== Area: where the 1.52x came from ==")
    print(f"  inventory estimate, 7-track      {a['estimate_cell_area_um2']:10.1f} um^2 "
          f"({a['estimate_cells']} cells, {x['mean_cell_um2_estimate_7t']:.2f} um^2/cell)")
    print(f"  as-built netlist priced 7-track  {x['as_built_7t_um2']:10.1f} um^2 "
          f"({x['instances']} instances, {x['mean_cell_um2_measured_7t']:.2f} um^2/cell)"
          f"  -> cell count/mix x{x['cell_count_term']:.3f}")
    print(f"  as-built netlist, 9-track (built){x['as_built_9t_um2']:10.1f} um^2 "
          f"({x['mean_cell_um2_measured_9t']:.2f} um^2/cell)"
          f"  -> track height x{x['track_height_term']:.3f}")
    print(f"  liberty sum vs OpenROAD's own report_design_area: "
          f"{x['liberty_vs_openroad_rel'] * 100:.4f} % apart")
    print()

    print("== Measured vs design/digital_power_estimate.py, both at 1 MHz ==")
    print(f"{'corner':16s} {'measured':>10s} {'est(gated)':>11s} "
          f"{'est(ungated)':>13s} {'x gated':>8s} {'x ungated':>10s} "
          f"{'leak x':>7s}")
    for row in estimate_comparison(records):
        print(f"{row['corner']:16s} {_w(row['measured_w']):>10s} "
              f"{_w(row['estimate_gated_w']):>11s} "
              f"{_w(row['estimate_ungated_w']):>13s} "
              f"{row['ratio_vs_gated']:7.1f}x {row['ratio_vs_ungated']:9.1f}x "
              f"{row['leakage_ratio']:6.2f}x")
    print("  'gated' is the estimate's headline (it assumes clock gating on the")
    print("  two output FIFOs); 'ungated' is its own per-flop-feedback-mux")
    print("  variant, which is what synthesis actually built -- the netlist")
    print("  contains no integrated clock gates at all.")


# --------------------------------------------------------------------------- #
# The gate
# --------------------------------------------------------------------------- #


def check(records: list[Record]) -> list[str]:
    """Return the list of failures; empty means the document is still true."""
    fails: list[str] = []
    t = timing(records)
    a = area(records)
    p = power(records)

    def close(name: str, got: float, want: float) -> None:
        if want == 0:
            ok = got == 0
        else:
            ok = abs(got - want) / abs(want) <= TOLERANCE
        if not ok:
            fails.append(
                f"{name}: records give {got:.6g}, "
                f"sim/characterization-digital-sta-area-power.md and RECORDED "
                f"say {want:.6g} (> {TOLERANCE * 100:g} % apart)"
            )

    def equal(name: str, got, want) -> None:
        if got != want:
            fails.append(f"{name}: records give {got!r}, RECORDED says {want!r}")

    equal("corner count", len(records), RECORDED["corner_count"])
    if not t["closes_everywhere"]:
        offenders = [
            r["corner"] for r in t["rows"]
            if r["setup_ns"] <= 0 or r["hold_ns"] <= 0
        ]
        fails.append(
            "the recorded finding is that every corner closes timing at "
            f"{t['constraint_mhz']:g} MHz with positive setup AND hold slack; "
            f"these do not: {', '.join(offenders)}"
        )
    equal("setup binding corner", t["setup_binding"], RECORDED["setup_binding_corner"])
    close("setup binding slack", t["setup_binding_slack_ns"],
          RECORDED["setup_binding_slack_ns"])
    equal("hold binding corner", t["hold_binding"], RECORDED["hold_binding_corner"])
    close("hold binding slack", t["hold_binding_slack_ns"],
          RECORDED["hold_binding_slack_ns"])
    equal("Fmax floor corner", t["fmax_floor_corner"], RECORDED["fmax_floor_corner"])
    close("Fmax floor", t["fmax_floor_mhz"], RECORDED["fmax_floor_mhz"])
    if t["fmax_floor_mhz"] <= t["constraint_mhz"]:
        fails.append(
            f"Fmax floor {t['fmax_floor_mhz']:.2f} MHz is at or below the "
            f"{t['constraint_mhz']:g} MHz the design was built to -- the "
            "document's margin statement no longer holds"
        )
    if t["bisect_vs_linear_max_rel"] > 0.01:
        fails.append(
            "the bisected Fmax and the 1/(T - WNS) extrapolation now differ by "
            f"{t['bisect_vs_linear_max_rel'] * 100:.2f} %; the document states "
            "they agree, which is what licenses quoting either one"
        )

    close("placed cell area", a["measured_cell_area_um2"], RECORDED["cell_area_um2"])
    close("area vs inventory estimate", a["ratio"], RECORDED["area_ratio_vs_inventory"])

    close("max power at 1 MHz", p["max_1mhz_w"], RECORDED["power_1mhz_max_w"])
    equal("max-power corner at 1 MHz", p["max_1mhz_corner"],
          RECORDED["power_1mhz_max_corner"])
    close("max leakage", p["max_leakage_w"], RECORDED["leakage_max_w"])
    close("max leakage current", p["max_leakage_a"], RECORDED["leakage_max_current_a"])
    if not p["max_leakage_corner"].startswith(RECORDED["leakage_max_corner"]):
        fails.append(
            f"leakage now binds at {p['max_leakage_corner']}, "
            f"RECORDED says the {RECORDED['leakage_max_corner']} liberty corner"
        )
    return fails


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit nonzero if the committed records stop supporting "
                         "the recorded findings (the gate CI runs)")
    ap.add_argument("--estimate", action="store_true",
                    help="add the library-based estimate comparison (needs the PDK)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    try:
        records = load()
    except RecordError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        payload = {
            "timing": timing(records),
            "area": area(records),
            "power": power(records),
        }
        if args.estimate:
            payload["estimate_comparison"] = estimate_comparison(records)
            payload["area_crosscheck"] = area_crosscheck(
                payload["area"]["measured_cell_area_um2"],
                payload["area"]["estimate_cell_area_um2"],
                payload["area"]["estimate_cells"],
                resolve_pdk_root(),
            )
        print(json.dumps(payload, indent=2))
        return 0

    if not args.check:
        report(records, with_estimate=args.estimate)
        return 0

    fails = check(records)
    if fails:
        print("error: the committed gate-level records no longer support "
              "sim/characterization-digital-sta-area-power.md:", file=sys.stderr)
        for line in fails:
            print(f"  - {line}", file=sys.stderr)
        print(
            "\nOne of them is stale. Re-read the records, update the document, "
            "and move this script's RECORDED table with it -- never the other "
            "way round.",
            file=sys.stderr,
        )
        return 1
    t = timing(records)
    print(
        f"digital corner characterization: {len(records)} corners, setup binds "
        f"at {t['setup_binding']} (+{t['setup_binding_slack_ns']:.2f} ns), hold "
        f"at {t['hold_binding']} (+{t['hold_binding_slack_ns']:.2f} ns), Fmax "
        f"floor {t['fmax_floor_mhz']:.1f} MHz (issue #145) -- OK"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
