#!/usr/bin/env python3
"""Corner-swept static timing and power analysis of the placed-and-routed
digital section, for issue #145 (T1 checklist items 5 and 8, digital column).

    python3 sim/tb/digital-sta-power/run_sta.py --no-write   # run, print, mint nothing
    python3 sim/tb/digital-sta-power/run_sta.py              # run and mint records
    python3 sim/tb/digital-sta-power/run_sta.py --list       # the corner grid

What this is
------------
`layout/digital/build.py` (#111) placed and routed
`design/trng_top/trng_top.synth.v` (#143) and committed the routed DEF, the
as-built gate-level netlist and one implementation-corner report. That run
answered "does this design route at all". It did **not** answer "does it
close timing, and what does it cost, across the corner set" -- its own
README says so, and hands the question here.

This script is that answer. It re-opens the **committed** routed DEF
(`layout/digital/trng_top.def`), extracts real parasitics from the real
routing with OpenRCX, back-annotates them as SPEF, and runs OpenSTA over
the result once per corner:

- **timing** -- worst setup and hold slack against the P&R run's own 50 ns
  (20 MHz) constraint, with a propagated (not ideal) clock through the
  CTS-built tree, plus an Fmax found by bisecting the clock period rather
  than extrapolated from one slack number;
- **power** -- `report_power` at that same 20 MHz constraint *and* at the
  ratified 1 MHz raw-sample rate ([DR-0003]), the operating point
  `design/digital_power_estimate.py`'s library-based estimate prices, so
  the measured and estimated figures can be compared without a frequency
  correction in between;
- **area** -- the placed standard-cell area OpenROAD reports from the DEF
  itself (corner-independent; recorded in every record so no record has to
  be read together with another one to be complete).

Why OpenROAD directly, and not `klt`
------------------------------------
Every other physical-flow driver in this repository goes through `klt`
(`layout/_klt.py`), and this one deliberately does not, because there is no
`klt` verb that re-times an already-routed DEF. `klt place-and-route` does
run OpenSTA, but only *inside* a place-and-route run, at the one liberty
corner the request names, over an ideal clock, with placement-estimated
parasitics and no parasitic-corner control at all (its tech LEF is pinned
to the PDK's `nom` deck). Re-running the whole flow once per corner would
also give each corner a *different placement*, which is exactly what a
corner sweep must not do: the design under test has to be one fixed piece
of geometry. Filed generically upstream as klayout-tools#1099 (a signoff
STA verb over an existing DEF/netlist) and klayout-tools#1100 (parasitic-
corner selection); when those land, this script is the caller that should
switch to them. `openroad` is invoked here the same way `klt` invokes it --
`openroad -no_init -exit <script>` -- and the script it runs is written
into the record's own raw output, so the whole thing is auditable without
this file.

The corner set
--------------
`sim/harness/corners.py` sweeps the analog side over {tt, ss, ff} x
{-40, 27, 125} degC x {2.97, 3.30, 3.63} V = 27 points. A liberty corner is
not a free P/V/T choice: the library ships *characterised* bundles, and
`gf180mcu_fd_sc_mcu9t5v0` ships exactly five in the block's ratified 3.3 V
family (`design/README.md`) --

    ss_125C_3v00  ss_n40C_3v00  tt_025C_3v30  ff_125C_3v60  ff_n40C_3v60

-- which are the five corners of the analog grid's own P/V/T box that the
library actually characterises (the 1.8 V and 5.0 V families it also ships
describe a supply this block does not run at, and are excluded here for the
same reason `layout/digital/build.py` excludes them). Every one of the five
is swept against all three of the PDK's OpenRCX interconnect corners
(`min`/`nom`/`max`), because a timing corner for a routed block is a
(device, interconnect) pair and this repository has no basis for assuming
which pairing binds. 5 x 3 = 15 points, one record each, per DR-0005.

What this is not
----------------
Not silicon, and not a signoff sign-off. The parasitics are OpenRCX's own
extraction from the routed DEF against the PDK's shipped rule decks, which
is a real extraction and not an estimate -- but it is not a foundry-signed
extraction, the flow it re-opens has no power delivery at all
(klayout-tools#1091, #171), and the DEF it reads carries no `SPECIALNETS`,
so nothing here sees IR drop. Only reg-to-reg paths are timed: the design
has no `set_input_delay`/`set_output_delay` constraints, so port paths are
unconstrained, and every record states how many endpoints that leaves
untimed. Power carries a declared, uniform switching activity (see
`ACTIVITY`); it is a corner sweep of a *model*, not a measured supply
current, and `sim/characterization-digital-sta-area-power.md` says at
length what follows from that and what does not.

[DR-0003]: ../../../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

TB_DIR = Path(__file__).resolve().parent
SIM_DIR = TB_DIR.parents[1]
REPO_ROOT = SIM_DIR.parent

sys.path.insert(0, str(SIM_DIR))

from harness import report  # noqa: E402
from harness import pdk as pdk_mod  # noqa: E402

SLUG = "digital-sta-power"

#: The committed geometry under test. Never re-placed, never re-routed by
#: this script -- one design, fifteen corners.
DEF_PATH = REPO_ROOT / "layout" / "digital" / "trng_top.def"
PNR_NETLIST_PATH = REPO_ROOT / "layout" / "digital" / "trng_top.pnr.v"
PNR_REPORT_PATH = REPO_ROOT / "layout" / "digital" / "reports" / "place_and_route.json"

CELL_LIBRARY = "gf180mcu_fd_sc_mcu9t5v0"
HDL_TOPLEVEL = "trng_top"
CLOCK_PORT = "clk"

#: Scratch root. Under `layout/.work/` like every other physical-flow
#: driver's (gitignored) working directory -- the SPEF this script writes is
#: 3.3 MB per corner and is deliberately not committed; its sha256 and its
#: summed capacitance are (see `_spef_summary`).
WORK_DIR = REPO_ROOT / "layout" / ".work" / "digital-sta"

#: The P&R run's own timing constraint (`layout/digital/build.py`'s
#: `CONSTRAINTS`), restated here so this sweep times the design against the
#: constraint it was built to and not a new one. NOT a spec row: no issue in
#: this repository sets a digital-section Fmax requirement.
CONSTRAINT_PERIOD_NS = 50.0

#: [DR-0003]'s ratified raw rate, one raw bit per `clk` edge => 1 MHz. The
#: second operating point every corner's power is reported at, because it is
#: the one `design/digital_power_estimate.py` prices and a power comparison
#: across two different clock rates would be measuring the clock rate.
RATIFIED_RATE_PERIOD_NS = 1000.0

#: Uniform switching activity handed to OpenSTA, in **transitions per net
#: per clock cycle**, with a 50 % duty. `design/digital_power_estimate.py`'s
#: own `DEFAULT_ACTIVITY = 0.125` counts *rising* transitions per net per
#: cycle; a net that rises 0.125 times per cycle also falls 0.125 times per
#: cycle, so the same assumption is 0.25 transitions per cycle here. Stated
#: as a number rather than left at OpenSTA's own default precisely so the
#: measured-vs-estimated comparison is not a comparison of two different
#: activity models.
ACTIVITY = 0.25
ACTIVITY_DUTY = 0.5

#: Liberty corners: the five the library characterises in this block's
#: ratified 3.3 V family. Ordered slow -> fast, which is also the order the
#: setup and hold sides bind in.
LIBERTY_CORNERS = (
    "ss_125C_3v00",
    "ss_n40C_3v00",
    "tt_025C_3v30",
    "ff_125C_3v60",
    "ff_n40C_3v60",
)

#: OpenRCX interconnect (parasitic) corners the PDK ships, under
#: `libs.tech/openlane/rules.openrcx.<variant>.<corner>`. Orthogonal to the
#: liberty axis: the liberty deck models the devices, these model the wires.
RC_CORNERS = ("min", "nom", "max")

#: Which tech LEF the DEF is read against. Held at `nom` for every point on
#: purpose: the tech LEF supplies the *geometry* the committed DEF was routed
#: on (klt's own place-and-route pins it to `nom` too), so varying it would
#: change the design rather than the corner. The interconnect corner is
#: expressed through the OpenRCX rule deck above, which is what those decks
#: are for.
TECH_LEF_CORNER = "nom"

#: Bisection bounds and resolution for the Fmax search, in ns. The lower
#: bound is not a claim that a 0.1 ns period is meaningful -- it is a bracket
#: endpoint, and the search reports the period it converged to.
FMAX_MIN_PERIOD_NS = 0.1
FMAX_TOLERANCE_NS = 1e-3

OPENROAD_TIMEOUT_S = 1800

_METRIC = re.compile(r"^STA_METRIC\s+(\S+)\s+(\S+)\s*$", re.M)
_POWER_ROW = re.compile(
    r"^(Sequential|Combinational|Clock|Macro|Pad|Total)\s+"
    r"([\d.e+-]+)\s+([\d.e+-]+)\s+([\d.e+-]+)\s+([\d.e+-]+)",
    re.M,
)
_MISSING_INPUT = re.compile(r"There are (\d+) input ports missing set_input_delay")
_MISSING_OUTPUT = re.compile(r"There are (\d+) output ports missing set_output_delay")
_UNCONSTRAINED = re.compile(r"There are (\d+) unconstrained endpoints")
_LIB_ATTR = re.compile(r"^\s*(nom_process|nom_temperature|nom_voltage)\s*:\s*([-\d.]+)\s*;", re.M)


class StaError(RuntimeError):
    """The sweep could not be attempted, or a run did not produce metrics."""


@dataclass
class Corner:
    """One (liberty deck, interconnect deck) point of the grid."""

    liberty: str
    rc: str

    @property
    def process(self) -> str:
        return self.liberty.split("_")[0]

    @property
    def temp_c(self) -> float:
        raw = self.liberty.split("_")[1]
        value = float(raw.lstrip("n").rstrip("C"))
        return -value if raw.startswith("n") else value

    @property
    def vdd(self) -> float:
        raw = self.liberty.split("_")[2]
        return float(raw.replace("v", "."))

    @property
    def label(self) -> str:
        return f"{self.liberty}/rc-{self.rc}"


@dataclass
class Point:
    """Everything one record needs about one corner."""

    corner: Corner
    metrics: dict = field(default_factory=dict)
    power: dict = field(default_factory=dict)
    spef: dict = field(default_factory=dict)
    logs: dict = field(default_factory=dict)
    wall_s: float = 0.0


# --------------------------------------------------------------------------- #
# Environment
# --------------------------------------------------------------------------- #


def openroad_version() -> str | None:
    if shutil.which("openroad") is None:
        return None
    done = subprocess.run(
        ["openroad", "-version"], capture_output=True, text=True, check=False
    )
    return done.stdout.strip().splitlines()[0].strip() if done.stdout.strip() else None


def resolve_pdk():
    try:
        return pdk_mod.find_pdk()
    except Exception:
        return None


def deck_paths(pdk) -> dict[str, Path]:
    libs_ref = Path(pdk.path) / "libs.ref" / CELL_LIBRARY
    return {
        "lib_dir": libs_ref / "lib",
        "tech_lef": libs_ref / "techlef" / f"{CELL_LIBRARY}__{TECH_LEF_CORNER}.tlef",
        "cell_lef": libs_ref / "lef" / f"{CELL_LIBRARY}.lef",
        "rcx_dir": Path(pdk.path) / "libs.tech" / "openlane",
    }


def liberty_path(pdk, corner: str) -> Path:
    return deck_paths(pdk)["lib_dir"] / f"{CELL_LIBRARY}__{corner}.lib"


def rcx_rules_path(pdk, rc: str) -> Path:
    return deck_paths(pdk)["rcx_dir"] / f"rules.openrcx.{pdk.variant}.{rc}"


def check_environment(pdk) -> list[str]:
    missing: list[str] = []
    if openroad_version() is None:
        missing.append(
            "openroad is not on PATH (see layout/digital/README.md's 'OpenROAD' "
            "section for the pinned ORFS image, or install a native build)"
        )
    if pdk is None:
        missing.append("no gf180mcu PDK install found (see sim/harness/pdk.py)")
    else:
        paths = deck_paths(pdk)
        for name in ("tech_lef", "cell_lef"):
            if not paths[name].is_file():
                missing.append(f"{name} not found at {paths[name]}")
        for corner in LIBERTY_CORNERS:
            path = liberty_path(pdk, corner)
            if not path.is_file():
                missing.append(f"liberty deck not found at {path}")
        for rc in RC_CORNERS:
            path = rcx_rules_path(pdk, rc)
            if not path.is_file():
                missing.append(f"OpenRCX rule deck not found at {path}")
    for path in (DEF_PATH, PNR_NETLIST_PATH):
        if not path.is_file():
            missing.append(
                f"{path.relative_to(REPO_ROOT)} is missing -- run "
                "`python3 layout/digital/build.py` first (#111)"
            )
    return missing


def liberty_operating_conditions(path: Path) -> dict:
    """`nom_process`/`nom_temperature`/`nom_voltage` from a liberty header.

    Read from the deck itself rather than parsed out of its filename, so a
    record's stated corner is the corner the timing came from and not a
    naming convention this script believes in.
    """
    head = []
    with path.open(errors="replace") as handle:
        for i, line in enumerate(handle):
            head.append(line)
            if i > 200:
                break
    found = {m.group(1): float(m.group(2)) for m in _LIB_ATTR.finditer("".join(head))}
    return found


# --------------------------------------------------------------------------- #
# The OpenROAD session
# --------------------------------------------------------------------------- #


def _tcl(
    *,
    pdk,
    corner: Corner,
    period_ns: float,
    spef_path: Path,
    bisect: bool,
) -> str:
    """One OpenROAD session's script: read the committed DEF, extract, time.

    One session per (corner, clock period) on purpose. OpenSTA caches a
    design's clock-derived activity densities on the first power query, so a
    `create_clock` that *replaces* an existing clock mid-session updates
    every slack correctly but leaves `report_power`'s switching term at the
    old rate. Verified live during this script's own bring-up: re-creating
    the 50 ns clock at 1000 ns in one session left combinational switching
    power bit-identical (1.031943e-03 W) instead of falling 20x, while a
    fresh session at 1000 ns reported exactly 1/20th of the 50 ns session's
    total. The clock bisection below is therefore run *after* every power
    query in its session, and the 1 MHz power point gets a session of its
    own.
    """
    paths = deck_paths(pdk)
    lines = [
        f"read_liberty {liberty_path(pdk, corner.liberty)}",
        f"read_lef {paths['tech_lef']}",
        f"read_lef {paths['cell_lef']}",
        f"read_def {DEF_PATH}",
        f"create_clock -name {CLOCK_PORT} -period {period_ns} [get_ports {CLOCK_PORT}]",
        "define_process_corner -ext_model_index 0 X",
        f"extract_parasitics -ext_model_file {rcx_rules_path(pdk, corner.rc)}",
        f"write_spef {spef_path}",
        f"read_spef {spef_path}",
        # The ideal-clock slack is read FIRST, at the same corner and with the
        # same extracted parasitics, purely so this sweep can be reconciled
        # against `layout/digital/reports/place_and_route.json` -- which
        # reports an ideal (SDC-only) clock. Everything else in this session
        # is the propagated-clock number: a CTS-built tree exists in this DEF,
        # and timing it as ideal credits the design with zero insertion delay
        # and zero skew.
        'puts "STA_METRIC worst_setup_slack_ideal_s [sta::worst_slack_cmd max]"',
        'puts "STA_METRIC worst_hold_slack_ideal_s [sta::worst_slack_cmd min]"',
        "set_propagated_clock [all_clocks]",
        f"set_power_activity -global -activity {ACTIVITY} -duty {ACTIVITY_DUTY}",
        # Machine-readable metrics. The human-readable reports below land in
        # the same log and are the record's raw evidence.
        f'puts "STA_METRIC period_ns {period_ns}"',
        'puts "STA_METRIC worst_setup_slack_s [sta::worst_slack_cmd max]"',
        'puts "STA_METRIC worst_hold_slack_s [sta::worst_slack_cmd min]"',
        'puts "STA_METRIC tns_setup_s [sta::total_negative_slack_cmd max]"',
        'puts "STA_METRIC tns_hold_s [sta::total_negative_slack_cmd min]"',
        'puts "STA_METRIC clock_skew_setup_s [sta::worst_clk_skew_cmd max 0]"',
        'puts "STA_METRIC clock_skew_hold_s [sta::worst_clk_skew_cmd min 0]"',
        'puts "STA_METRIC cell_area_m2 [rsz::design_area]"',
        'puts "STA_METRIC utilization [rsz::utilization]"',
        "report_worst_slack -max -digits 4",
        "report_worst_slack -min -digits 4",
        "report_tns -digits 4",
        "report_checks -path_delay max -group_count 5 -digits 4 -format summary",
        "report_checks -path_delay min -group_count 5 -digits 4 -format summary",
        "report_clock_skew -setup -digits 4",
        "report_power -digits 6",
        "report_design_area",
        "check_setup",
    ]
    if bisect:
        lines += [
            "",
            "# Fmax by bisection on the clock period: the smallest period at",
            "# which worst setup slack is still >= 0. Reported alongside the",
            "# linear 1/(T - WNS) extrapolation the P&R flow's own",
            "# report_fmax_metric uses, so the two can be compared rather",
            "# than one of them assumed.",
            "proc setup_slack_at {p} {",
            f"  create_clock -name {CLOCK_PORT} -period $p [get_ports {CLOCK_PORT}]",
            "  set_propagated_clock [all_clocks]",
            "  return [sta::worst_slack_cmd max]",
            "}",
            f"set lo {FMAX_MIN_PERIOD_NS}",
            f"set hi {period_ns}",
            'puts "STA_METRIC bisect_slack_at_lo_s [setup_slack_at $lo]"',
            "if {[setup_slack_at $lo] >= 0} {",
            '  puts "STA_METRIC min_period_ns $lo"',
            "} else {",
            f"  while {{[expr {{$hi - $lo}}] > {FMAX_TOLERANCE_NS}}} {{",
            "    set mid [expr {($lo + $hi) / 2.0}]",
            "    if {[setup_slack_at $mid] >= 0} { set hi $mid } else { set lo $mid }",
            "  }",
            '  puts "STA_METRIC min_period_ns $hi"',
            '  puts "STA_METRIC min_period_slack_s [setup_slack_at $hi]"',
            '  puts "STA_METRIC min_period_hold_slack_s [sta::worst_slack_cmd min]"',
            "}",
        ]
    return "\n".join(lines) + "\n"


def _run_openroad(script_path: Path, log_path: Path) -> str:
    done = subprocess.run(
        ["openroad", "-no_init", "-exit", str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=OPENROAD_TIMEOUT_S,
        check=False,
    )
    text = done.stdout + ("\n" + done.stderr if done.stderr.strip() else "")
    log_path.write_text(text)
    if done.returncode != 0:
        raise StaError(
            f"openroad exited {done.returncode} for {script_path.name}; "
            f"see {log_path}"
        )
    return text


def _parse_metrics(text: str) -> dict:
    return {m.group(1): float(m.group(2)) for m in _METRIC.finditer(text)}


def _parse_power(text: str) -> dict:
    """The `report_power` table, per group and total, in watts."""
    out: dict[str, dict[str, float]] = {}
    for m in _POWER_ROW.finditer(text):
        out[m.group(1).lower()] = {
            "internal_w": float(m.group(2)),
            "switching_w": float(m.group(3)),
            "leakage_w": float(m.group(4)),
            "total_w": float(m.group(5)),
        }
    if "total" not in out:
        raise StaError("no report_power table in the OpenROAD log")
    return out


def _parse_setup_checks(text: str) -> dict:
    def _one(pattern) -> int | None:
        m = pattern.search(text)
        return int(m.group(1)) if m else 0

    return {
        "inputs_missing_delay": _one(_MISSING_INPUT),
        "outputs_missing_delay": _one(_MISSING_OUTPUT),
        "unconstrained_endpoints": _one(_UNCONSTRAINED),
    }


def _spef_summary(spef_path: Path) -> dict:
    """Total grounded (wire-to-ground) and coupling capacitance in the SPEF.

    OpenROAD writes this SPEF with `PIN_CAP NONE`, so every grounded entry is
    interconnect capacitance and none of it is a standard cell's own input
    pin -- which makes the per-net figure directly comparable against
    `design/digital_power_estimate.py`'s flat `DEFAULT_WIRE_CAP_F` allowance,
    the one term in that estimate that had no layout behind it at all.

    `*CAP` entries with two fields are node-to-ground; three fields are
    node-to-node coupling. Units come from the header (`*C_UNIT`), never
    assumed.
    """
    unit_f = 1e-12
    total_ground = 0.0
    total_coupling = 0.0
    nets = 0
    in_cap = False
    with spef_path.open(errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("*C_UNIT"):
                parts = line.split()
                scale = {"F": 1.0, "MF": 1e-3, "UF": 1e-6, "NF": 1e-9,
                         "PF": 1e-12, "FF": 1e-15}[parts[2].upper()]
                unit_f = float(parts[1]) * scale
            elif line.startswith("*D_NET"):
                nets += 1
                in_cap = False
            elif line.startswith("*CAP"):
                in_cap = True
            elif line.startswith("*RES") or line.startswith("*END"):
                in_cap = False
            elif in_cap and line and line[0].isdigit():
                fields = line.split()
                if len(fields) == 3:
                    total_ground += float(fields[2])
                elif len(fields) == 4:
                    total_coupling += float(fields[3])
    return {
        "nets": nets,
        "ground_cap_f": total_ground * unit_f,
        "coupling_cap_f": total_coupling * unit_f,
        "sha256": report.sha256_file(spef_path),
        "bytes": spef_path.stat().st_size,
    }


def run_point(pdk, corner: Corner, work_dir: Path) -> Point:
    """One corner: two OpenROAD sessions (20 MHz + 1 MHz), one Point."""
    started = time.time()
    point = Point(corner=corner)
    spef_path = work_dir / f"{HDL_TOPLEVEL}.{corner.liberty}.{corner.rc}.spef"

    for tag, period, bisect in (
        ("constraint", CONSTRAINT_PERIOD_NS, True),
        ("ratified-rate", RATIFIED_RATE_PERIOD_NS, False),
    ):
        script_path = work_dir / f"sta-{tag}.{corner.liberty}.{corner.rc}.tcl"
        log_path = work_dir / f"sta-{tag}.{corner.liberty}.{corner.rc}.log"
        script = _tcl(
            pdk=pdk, corner=corner, period_ns=period, spef_path=spef_path,
            bisect=bisect,
        )
        script_path.write_text(script)
        text = _run_openroad(script_path, log_path)
        metrics = _parse_metrics(text)
        power = _parse_power(text)
        point.logs[tag] = {"script": script_path, "log": log_path}
        point.power[tag] = power
        if tag == "constraint":
            point.metrics = metrics
            point.metrics.update(_parse_setup_checks(text))
            point.spef = _spef_summary(spef_path)
        else:
            point.metrics["ratified_rate_period_ns"] = metrics["period_ns"]

    point.wall_s = time.time() - started
    return point


# --------------------------------------------------------------------------- #
# Derived quantities
# --------------------------------------------------------------------------- #


def derive(point: Point) -> dict:
    """Everything a record's Result section quotes, in SI units.

    Only arithmetic on what the two sessions reported -- no modelling, and
    nothing that is not either a direct OpenROAD output or a ratio of two of
    them.
    """
    m = point.metrics
    c = point.corner
    constraint_ns = m["period_ns"]
    setup_ns = m["worst_setup_slack_s"] * 1e9
    hold_ns = m["worst_hold_slack_s"] * 1e9
    min_period_ns = m.get("min_period_ns")
    cell_area_um2 = m["cell_area_m2"] * 1e12
    p20 = point.power["constraint"]
    p1 = point.power["ratified-rate"]
    leakage_w = p20["total"]["leakage_w"]
    out = {
        "constraint_period_ns": constraint_ns,
        "constraint_freq_mhz": 1e3 / constraint_ns,
        "worst_setup_slack_ns": setup_ns,
        "worst_hold_slack_ns": hold_ns,
        "worst_setup_slack_ideal_clock_ns": m["worst_setup_slack_ideal_s"] * 1e9,
        "worst_hold_slack_ideal_clock_ns": m["worst_hold_slack_ideal_s"] * 1e9,
        "clock_tree_cost_ns": (m["worst_setup_slack_ideal_s"]
                               - m["worst_setup_slack_s"]) * 1e9,
        "tns_setup_ns": m["tns_setup_s"] * 1e9,
        "tns_hold_ns": m["tns_hold_s"] * 1e9,
        "clock_skew_setup_ns": m["clock_skew_setup_s"] * 1e9,
        "fmax_linear_mhz": 1e3 / (constraint_ns - setup_ns),
        "cell_area_um2": cell_area_um2,
        "utilization_pct": m["utilization"] * 100.0,
        "wire_cap_total_f": point.spef["ground_cap_f"],
        "wire_cap_per_net_f": point.spef["ground_cap_f"] / max(point.spef["nets"], 1),
        "coupling_cap_total_f": point.spef["coupling_cap_f"],
        "spef_nets": float(point.spef["nets"]),
        "p_total_20mhz_w": p20["total"]["total_w"],
        "p_internal_20mhz_w": p20["total"]["internal_w"],
        "p_switching_20mhz_w": p20["total"]["switching_w"],
        "p_clock_20mhz_w": p20["clock"]["total_w"],
        "p_sequential_20mhz_w": p20["sequential"]["total_w"],
        "p_combinational_20mhz_w": p20["combinational"]["total_w"],
        "p_total_1mhz_w": p1["total"]["total_w"],
        "p_internal_1mhz_w": p1["total"]["internal_w"],
        "p_switching_1mhz_w": p1["total"]["switching_w"],
        "p_clock_1mhz_w": p1["clock"]["total_w"],
        "p_clock_internal_1mhz_w": p1["clock"]["internal_w"],
        "p_clock_switching_1mhz_w": p1["clock"]["switching_w"],
        "p_sequential_1mhz_w": p1["sequential"]["total_w"],
        "p_sequential_internal_1mhz_w": p1["sequential"]["internal_w"],
        "p_sequential_switching_1mhz_w": p1["sequential"]["switching_w"],
        "p_combinational_1mhz_w": p1["combinational"]["total_w"],
        "p_combinational_internal_1mhz_w": p1["combinational"]["internal_w"],
        "p_combinational_switching_1mhz_w": p1["combinational"]["switching_w"],
        "p_leakage_w": leakage_w,
        "i_leakage_a": leakage_w / c.vdd,
        "i_total_1mhz_a": p1["total"]["total_w"] / c.vdd,
        "unconstrained_endpoints": float(m["unconstrained_endpoints"]),
        "inputs_missing_delay": float(m["inputs_missing_delay"]),
        "outputs_missing_delay": float(m["outputs_missing_delay"]),
    }
    if min_period_ns is not None:
        out["min_period_ns"] = min_period_ns
        out["fmax_bisect_mhz"] = 1e3 / min_period_ns
    return out


# --------------------------------------------------------------------------- #
# Records
# --------------------------------------------------------------------------- #


def _voltage_label(vdd: float) -> str:
    offset = (vdd - 3.3) / 3.3 * 100.0
    if abs(offset) < 0.05:
        return f"{vdd:.2f} V (nominal 3.3 V)"
    sign = "+" if offset > 0 else ""
    return f"{vdd:.2f} V (nominal 3.3 V, {sign}{offset:.1f}%)"


def _frontmatter(stem: str, point: Point, values: dict, pdk, git: dict,
                 raw_files, openroad: str, lib_conditions: dict) -> str:
    c = point.corner
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lib = liberty_path(pdk, c.liberty)
    paths = deck_paths(pdk)
    rcx = rcx_rules_path(pdk, c.rc)
    lines = [
        "---",
        f"record: {stem}",
        f"date: {now}",
        "status: valid",
        "",
        "level: gate (see spec/decision-records/"
        "DR-0021-gate-level-timing-and-power-records.md)",
        "",
        "testbench:",
        f"  path: sim/tb/{SLUG}/run_sta.py",
        f"  sha: {report.blob_sha(REPO_ROOT, TB_DIR / 'run_sta.py')}",
        "netlist:",
        "  path: layout/digital/trng_top.def",
        f"  sha: {report.blob_sha(REPO_ROOT, DEF_PATH)}",
        "  note: >-",
        "    The committed routed DEF from layout/digital/build.py (#111) -- one",
        "    fixed placement and routing, re-timed at this corner. The matching",
        "    as-built gate-level netlist is layout/digital/trng_top.pnr.v",
        f"    (sha {report.blob_sha(REPO_ROOT, PNR_NETLIST_PATH)}); OpenROAD reads the",
        "    instance set from the DEF, so the DEF is the DUT this record names.",
        f"repo_commit: {report.repo_commit_field(git)}",
        "",
        f"pdk: {pdk.variant} @ {pdk.version}",
        "pdk.models:",
        f"  - {lib} (liberty corner {c.liberty}, sha256:{report.sha256_file(lib)})",
        f"  - {paths['tech_lef']} (tech LEF, {TECH_LEF_CORNER} deck, "
        f"sha256:{report.sha256_file(paths['tech_lef'])})",
        f"  - {paths['cell_lef']} (cell LEF, sha256:{report.sha256_file(paths['cell_lef'])})",
        f"  - {rcx} (OpenRCX interconnect corner {c.rc}, sha256:{report.sha256_file(rcx)})",
        "",
        "tool:",
        '  ngspice: "n/a (gate-level record -- timing and power come from '
        'OpenSTA/OpenRCX inside OpenROAD, not from a device-level simulation)"',
        f'  openroad: "{openroad}"',
        f'  python: "{platform.python_version()} ({platform.python_implementation()})"',
        f"  platform: {platform.platform()}",
        "",
        "corner:",
        f"  process: {c.process}",
        f"  voltage: {_voltage_label(c.vdd)}",
        f"  temperature: {c.temp_c:g}",
        f"  liberty: {CELL_LIBRARY}__{c.liberty}",
        f"  interconnect: {c.rc} (OpenRCX rule deck; the parasitic corner, "
        "orthogonal to the liberty deck's device corner)",
    ]
    if lib_conditions:
        stated = ", ".join(
            f"{k} {v:g}" for k, v in sorted(lib_conditions.items())
        )
        lines.append(f"  liberty_operating_conditions: {stated} (read from the deck)")
    lines += [
        "",
        "analysis:",
        "  type: sta+power (OpenSTA over the committed routed DEF, OpenRCX-extracted "
        "parasitics back-annotated as SPEF)",
        "  tstop: n/a (static analysis -- no time-domain window)",
        "  tstep: n/a (static analysis)",
        "  tmax: n/a (static analysis)",
        "  noise_params: n/a (no device noise in a liberty-table analysis)",
        "  runs: 2 (one OpenROAD session per clock rate -- see the testbench "
        "docstring on why the two rates cannot share a session)",
        f"  clock: {CLOCK_PORT}, {CONSTRAINT_PERIOD_NS:g} ns "
        f"({1e3 / CONSTRAINT_PERIOD_NS:g} MHz) -- the P&R run's own constraint; "
        f"power also reported at {RATIFIED_RATE_PERIOD_NS:g} ns "
        f"({1e3 / RATIFIED_RATE_PERIOD_NS:g} MHz), DR-0003's ratified raw rate",
        "  clock_model: propagated (the CTS-built tree in the DEF), not ideal",
        f"  power_activity: {ACTIVITY} transitions/net/cycle, duty {ACTIVITY_DUTY} "
        "(set_power_activity -global; = design/digital_power_estimate.py's 0.125 "
        "RISING transitions/net/cycle)",
        "seeds: n/a (deterministic analysis)",
        "",
        "parasitics:",
        f"  spef_sha256: {point.spef['sha256']}",
        f"  spef_bytes: {point.spef['bytes']}",
        "  note: >-",
        "    The SPEF is regenerated by the reproduce command below and is NOT",
        "    committed (3.3 MB per corner, 15 corners). Its sha256 and its summed",
        "    capacitance are, so a re-run is checkable against this record.",
        "",
        "raw:",
        f"  path: sim/records/raw/{stem}/",
        "  files:",
    ]
    for name, digest in raw_files:
        lines.append(f"    - {name}  sha256:{digest}")
    lines.append(f"wall_time: {point.wall_s:.1f}s")
    lines.append("---")
    return "\n".join(lines)


def _result_lines(values: dict) -> str:
    order = [
        "constraint_period_ns", "constraint_freq_mhz",
        "worst_setup_slack_ns", "worst_hold_slack_ns",
        "worst_setup_slack_ideal_clock_ns", "worst_hold_slack_ideal_clock_ns",
        "clock_tree_cost_ns", "tns_setup_ns", "tns_hold_ns", "clock_skew_setup_ns",
        "min_period_ns", "fmax_bisect_mhz", "fmax_linear_mhz",
        "cell_area_um2", "utilization_pct",
        "spef_nets", "wire_cap_total_f", "wire_cap_per_net_f", "coupling_cap_total_f",
        "p_total_20mhz_w", "p_internal_20mhz_w", "p_switching_20mhz_w",
        "p_clock_20mhz_w", "p_sequential_20mhz_w", "p_combinational_20mhz_w",
        "p_total_1mhz_w", "p_internal_1mhz_w", "p_switching_1mhz_w",
        "p_clock_1mhz_w", "p_clock_internal_1mhz_w", "p_clock_switching_1mhz_w",
        "p_sequential_1mhz_w", "p_sequential_internal_1mhz_w",
        "p_sequential_switching_1mhz_w",
        "p_combinational_1mhz_w", "p_combinational_internal_1mhz_w",
        "p_combinational_switching_1mhz_w",
        "p_leakage_w", "i_leakage_a", "i_total_1mhz_a",
        "unconstrained_endpoints", "inputs_missing_delay", "outputs_missing_delay",
    ]
    out = []
    for key in order:
        if key in values:
            out.append(f"- `{key}`: {values[key]:.6e}")
    return "\n".join(out)


def _body(point: Point, values: dict) -> str:
    c = point.corner
    return f"""
## Result

{_result_lines(values)}

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-sta-area-power.md` for what the fifteen
records of this family, read together, do and do not establish.

## How to reproduce

```sh
python3 sim/tb/{SLUG}/run_sta.py --liberty {c.liberty} --rc {c.rc} --no-write
```

Drop `--liberty`/`--rc` for the full 15-point grid, and `--no-write` to mint
records. Records are append-only: a re-run mints a new stem, it never
overwrites this one. Needs `openroad` on `PATH` and the gf180mcu PDK
(`python3 sim/run_corners.py --check-env` reports the PDK; the OpenROAD
provisioning is `layout/digital/README.md`'s "OpenROAD" section).

## Caveats

- **One corner** ({c.liberty}, interconnect `{c.rc}`). Says nothing about any
  other corner. A liberty deck bundles process, voltage and temperature
  together, so this record's P/V/T is the deck's, not a free choice.
- **Gate level, not device level.** Cell delays, internal energies and
  leakages are the library's characterised tables, not a device-model
  simulation of this netlist. That is what makes a corner sweep affordable
  here and it is also its ceiling: nothing in this record re-derives the
  library.
- **Reg-to-reg paths only.** The design carries no `set_input_delay`/
  `set_output_delay`, so port paths are unconstrained and untimed --
  `unconstrained_endpoints` above says how many endpoints that leaves out.
  This matches the constraint set the P&R run itself used.
- **Extraction, not signoff extraction.** Parasitics are OpenRCX's own
  extraction of the committed routed DEF against the PDK's shipped
  `rules.openrcx` deck. Real geometry, real coupling -- but not a
  foundry-signed extraction, and no IR drop: the DEF has no `SPECIALNETS`
  section and the flow that produced it builds no power delivery at all
  (#171, klayout-tools#1091).
- **Power carries a declared uniform switching activity**
  ({ACTIVITY} transitions/net/cycle, duty {ACTIVITY_DUTY}), applied globally.
  It is not a measured supply current and not a simulation of this design's
  real data. Leakage is the one power column with no activity assumption in
  it.
- **The clock constraint is this run's input, not a spec row.** No issue in
  this repository sets a digital-section Fmax requirement; the ratified rate
  row is DR-0003's > 1 Mbps at the raw tap.
- **Area is corner-independent** and is repeated in every record of this
  family so no record has to be read alongside another to be complete; it is
  the DEF's own placed standard-cell area, not a die area.

---

Written by `sim/tb/{SLUG}/run_sta.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here via
`supersedes` (see `sim/README.md`).
"""


def write_record(point: Point, values: dict, pdk, git: dict, openroad: str,
                 records_dir: Path) -> Path:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stem = report.allocate_record_stem(records_dir, date, SLUG)
    raw_dir = records_dir / "raw" / stem
    raw_dir.mkdir(parents=True, exist_ok=True)

    names = []
    for tag in ("constraint", "ratified-rate"):
        for kind in ("script", "log"):
            src = point.logs[tag][kind]
            name = f"{tag}.{'tcl' if kind == 'script' else 'log'}"
            shutil.copyfile(src, raw_dir / name)
            names.append(name)
    raw_files = [(n, report.sha256_file(raw_dir / n)) for n in names]

    lib_conditions = liberty_operating_conditions(liberty_path(pdk, point.corner.liberty))
    path = records_dir / f"{stem}.md"
    if path.exists():  # pragma: no cover - allocate_record_stem prevents this
        raise report.RecordExists(f"{path} already exists")
    path.write_text(
        _frontmatter(stem, point, values, pdk, git, raw_files, openroad, lib_conditions)
        + "\n"
        + _body(point, values)
    )
    return path


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def grid(liberty: list[str] | None, rc: list[str] | None) -> list[Corner]:
    libs = liberty or list(LIBERTY_CORNERS)
    rcs = rc or list(RC_CORNERS)
    for name in libs:
        if name not in LIBERTY_CORNERS:
            raise StaError(
                f"unknown liberty corner {name!r}; known: {', '.join(LIBERTY_CORNERS)}"
            )
    for name in rcs:
        if name not in RC_CORNERS:
            raise StaError(f"unknown interconnect corner {name!r}; known: {', '.join(RC_CORNERS)}")
    return [Corner(liberty=lib, rc=r) for lib in libs for r in rcs]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--liberty", action="append", help="liberty corner(s) to run")
    ap.add_argument("--rc", action="append", help="OpenRCX interconnect corner(s) to run")
    ap.add_argument("--no-write", action="store_true",
                    help="run and print without minting evidence records")
    ap.add_argument("--list", action="store_true", help="print the corner grid and exit")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    try:
        corners = grid(args.liberty, args.rc)
    except StaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.list:
        for c in corners:
            print(f"{c.label:32s} process={c.process} temp={c.temp_c:g}C vdd={c.vdd:.2f}V")
        return 0

    pdk = resolve_pdk()
    missing = check_environment(pdk)
    if missing:
        for reason in missing:
            print(f"ERROR  {reason}", file=sys.stderr)
        return 3

    openroad = openroad_version() or "unknown"
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    git = report.git_provenance(REPO_ROOT)
    records_dir = SIM_DIR / "records"

    results = []
    for c in corners:
        point = run_point(pdk, c, WORK_DIR)
        values = derive(point)
        results.append((point, values))
        print(
            f"{c.label:32s} setup {values['worst_setup_slack_ns']:8.3f} ns  "
            f"hold {values['worst_hold_slack_ns']:7.3f} ns  "
            f"fmax {values.get('fmax_bisect_mhz', float('nan')):7.2f} MHz  "
            f"P(1MHz) {values['p_total_1mhz_w'] * 1e3:7.3f} mW  "
            f"leak {values['p_leakage_w'] * 1e6:7.2f} uW  "
            f"[{point.wall_s:.1f}s]"
        )
        if not args.no_write:
            path = write_record(point, values, pdk, git, openroad, records_dir)
            print(f"  wrote {path.relative_to(REPO_ROOT)}")

    if args.json:
        print(json.dumps(
            [{"corner": p.corner.label, **v} for p, v in results], indent=2
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
