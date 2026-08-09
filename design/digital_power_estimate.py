#!/usr/bin/env python3
"""Standard-cell power estimate for the three digital blocks, from the PDK's
own Liberty timing/power libraries.

    python3 design/digital_power_estimate.py
    python3 design/digital_power_estimate.py --corner ss_125C_3v00
    python3 design/digital_power_estimate.py --json

What this is
------------
`design/conditioner/`, `design/health_test/` and `design/interface/` are
RTL/behavioural only: they have no schematic, no netlist and no synthesis
flow in this repository (``design/README.md``), so their power CANNOT be
SPICE-measured the way `ro_array_core` and `sampler_core` are. This script
is the honest substitute, and it is a **[DR-0004] Tier 2 estimate, never a
measurement**:

1. a **gate-level inventory** of each block's RTL, at the same granularity
   and by the same method as ``design/conditioner/area_estimate.py`` (whose
   conditioner inventory this script imports rather than duplicating);
2. each cell's **leakage** read straight out of the ``gf180mcu_fd_sc_mcu7t5v0``
   Liberty library that ships with the installed PDK -- real characterised
   library data, per input state, at a real characterisation corner;
3. a **dynamic** term computed as ``alpha * C * V^2 * f`` from the library's
   own input-pin capacitances plus the library's own ``internal_power``
   tables, under switching-activity and fanout assumptions that are stated
   as arguments and printed with every result.

Item 2 is library data with essentially no modelling freedom. Item 3 is an
estimate on top of an estimate, and at the sample rates this block runs at
it is also the smaller term -- which is the single most important thing this
script has to say, and the reason it is worth writing at all.

Why the 7-track 5 V library, and which corners
----------------------------------------------
Same choice ``area_estimate.py`` argues: gf180mcu ships ``mcu7t5v0``
(denser) and ``mcu9t5v0``, and the 7-track library is characterised at
``ff_n40C_3v60``, ``ff_125C_3v60``, ``ss_125C_3v00`` and ``tt_025C_3v30``.
Those bracket the two corners the README's Power row binds at:

- **active** binds at ``ff`` / +10 % (fastest) -> ``ff_n40C_3v60``;
- **idle** binds at ``ff`` / +10 % / +125 C (leakiest) -> ``ff_125C_3v60``.

The library is characterised at 3.60 V and the envelope's upper rail is
3.63 V (3.3 V + 10 %). That 0.8 % voltage gap is not corrected for; it is
noted in the output, and it is far below the estimate's own uncertainty.

Why CI does not run this
------------------------
It needs ``libs.ref/gf180mcu_fd_sc_mcu7t5v0``, and the PDK nightly provisions
only ``gf180mcu_fd_pr`` (the device models ngspice needs). That is the same
constraint ``design/conditioner/area_estimate.py`` already lives with, and
the same answer: the script is run locally, its output is quoted in
``sim/characterization-startup-and-power-budget.md`` and
[DR-0017] with the command that regenerates it, and what CI *does* enforce is
in ``sim/tests/test_power_rollups.py`` -- the Liberty parser against a
synthetic library, and staleness guards that fail if any RTL parameter the
gate inventories depend on moves without the inventory being revisited.

[DR-0004]: ../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0017]: ../spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "sim"))
sys.path.insert(0, str(REPO_ROOT / "design" / "conditioner"))

from harness import pdk as pdk_mod  # noqa: E402

import area_estimate  # noqa: E402  (design/conditioner/area_estimate.py)

STDCELL_LIB = "gf180mcu_fd_sc_mcu7t5v0"

#: Liberty corner used for each README Power-row half. Both are real
#: characterisation corners shipped with the PDK.
CORNER_ACTIVE = "ff_n40C_3v60"
CORNER_IDLE = "ff_125C_3v60"
CORNER_NOMINAL = "tt_025C_3v30"
CORNER_SLOW = "ss_125C_3v00"

#: Ratified README rows this estimate is compared against.
ACTIVE_BUDGET_W = 500e-6
IDLE_BUDGET_A = 1e-6

#: Ratified sample-clock rate (DR-0003). DR-0010 proposes 500 bps; it is
#: Proposed, not ratified, so the default here is the ratified row and the
#: proposed rate is available via --raw-rate.
RAW_RATE_HZ = 1e6

# ---------------------------------------------------------------------------
# Gate-level inventories
# ---------------------------------------------------------------------------
#
# Format matches area_estimate.INVENTORY: (section, {cell suffix: count}, note),
# with an OPTIONAL fourth element -- a dict of per-section switching overrides:
#
#   clock_duty  fraction of sample-clock cycles on which this section's flops
#               actually see a clock edge. 1.0 unless the section sits behind
#               an integrated clock gate, in which case it is the rate at which
#               that gate opens. Getting this wrong is the single largest error
#               available in the dynamic term: charging all 512 clock-gated FIFO
#               flops at the full sample rate overstates the interface's
#               dynamic power by more than an order of magnitude.
#   activity    expected 0->1 transitions per net per sample-clock cycle for
#               this section, overriding the global default. Used where a
#               section is plainly not driven at the sample rate -- a FIFO word
#               written once per 32 or 256 raw bits, a read mux that moves only
#               when the host reads.
#
# Flip-flop counts are enumerated directly from each module's `reg`
# declarations at its shipped default parameters, and are the part of these
# inventories with no modelling freedom in them. Combinational counts are a
# structural estimate of what a synthesiser must produce at minimum for the
# written RTL; a real run will differ in buffering, drive strength and the
# exact comparator/increment implementations.

#: Raw samples per conditioned output word: K = 8 blocks of 32 (DR-0008).
COND_WORD_PERIOD = 256
#: Raw samples per packed raw output word (TRNG_RAW_PACK_BITS).
RAW_WORD_PERIOD = 32
#: Words in each FIFO (trng_interface FIFO_DEPTH).
FIFO_DEPTH = 8

#: design/health_test/rct_apt.v at the DR-0002 defaults
#: (C_RCT = 81 -> 7-bit counter, C_APT = 824 and W = 1024 -> 11-bit counters,
#: STARTUP_SAMPLES = 1024 -> 11-bit counter). 45 flops.
HEALTH_TEST_INVENTORY = [
    ("RCT run counter", {"dffrnq_1": 7}, "rct_run, 0..81, saturating"),
    ("RCT last-bit register", {"dffrnq_1": 1}, "rct_last_bit"),
    (
        "RCT increment",
        {"xor2_1": 6, "and2_1": 6},
        "ripple-carry increment across bits 1..6 of the 7-bit counter",
    ),
    (
        "RCT cutoff compare",
        {"xor2_1": 7, "nor2_1": 3, "nand2_1": 2, "inv_1": 1},
        "rct_run == C_RCT: 7 bitwise XORs into a NOR/NAND reduction tree",
    ),
    (
        "RCT bit compare + reload",
        {"xor2_1": 1, "mux2_1": 7},
        "raw_bit == rct_last_bit; the run counter reloads 1 on a mismatch",
    ),
    ("APT window position", {"dffrnq_1": 11}, "apt_pos, 0..1024"),
    ("APT match counter", {"dffrnq_1": 11}, "apt_match, 0..1024"),
    ("APT reference bit", {"dffrnq_1": 1}, "apt_ref_bit"),
    (
        "APT increments",
        {"xor2_1": 20, "and2_1": 20},
        "two 11-bit ripple increments (apt_pos, apt_match)",
    ),
    (
        "APT window-end compare",
        {"xor2_1": 11, "nor2_1": 5, "nand2_1": 3, "inv_1": 2},
        "apt_pos == W, an 11-bit equality",
    ),
    (
        "APT cutoff compare",
        {"nand2_1": 22, "inv_1": 11, "nor2_1": 5},
        "apt_match >= C_APT, an 11-bit magnitude comparator (~3 GE/bit)",
    ),
    (
        "APT bit compare + window reload",
        {"xor2_1": 1, "mux2_1": 22},
        "raw_bit == apt_ref_bit; both APT counters reload at a window boundary",
    ),
    ("start-up counter", {"dffrnq_1": 11}, "startup_count, saturating at 1024"),
    (
        "start-up increment + compare + reload",
        {"xor2_1": 10, "and2_1": 10, "nor2_1": 5, "nand2_1": 3, "inv_1": 2, "mux2_1": 11},
        "11-bit increment, == STARTUP_SAMPLES, and the startup_req restart path",
    ),
    (
        "output strobes",
        {"dffrnq_1": 3},
        "ht_fail_rct / ht_fail_apt / ht_startup_pass one-cycle pulses",
    ),
    (
        "valid / restart gating",
        {"and2_1": 4, "nor2_1": 2, "inv_1": 2},
        "raw_valid enable and startup_req restart priority",
    ),
]

#: design/health_test/ring_liveness.v at N_RINGS = 2, C_LIVE = 81 (7-bit
#: counters). 18 flops. DR-0016's monitor -- built, but NOT yet wired into the
#: alarm path and with no shipped schematic for its per-ring digitizer (#65),
#: so it is reported separately and excluded from the shipped totals, exactly
#: as design/README.md treats the metastability tap.
LIVENESS_INVENTORY = [
    ("per-ring last bit", {"dffrnq_1": 2}, "ring_last_bit, one per ring (N_RINGS = 2)"),
    ("per-ring run counters", {"dffrnq_1": 14}, "ring_run[0..1], 7 bits each, saturating at C_LIVE"),
    ("per-ring stuck strobes", {"dffrnq_1": 2}, "ring_stuck one-cycle pulses"),
    (
        "per-ring increments",
        {"xor2_1": 12, "and2_1": 12},
        "two 7-bit ripple increments",
    ),
    (
        "per-ring cutoff compares",
        {"xor2_1": 14, "nor2_1": 6, "nand2_1": 4, "inv_1": 2},
        "ring_run == C_LIVE, twice",
    ),
    (
        "per-ring bit compares + reload",
        {"xor2_1": 2, "mux2_1": 14},
        "ring_bit == ring_last_bit; counter reloads 1 on a mismatch",
    ),
    ("ring_stuck_any", {"or2_1": 1}, "OR across the per-ring strobes"),
]

#: design/interface/trng_interface.v at FIFO_DEPTH = 8, TRNG_LEVEL_BITS = 4.
#: 572 flops, of which 512 are the two 8 x 32-bit output FIFOs. Enable is
#: modelled as one integrated clock gate per FIFO word plus one for the raw
#: shift register, which is what a synthesiser does for a register-file-style
#: FIFO; INTERFACE_MUX_FEEDBACK_DELTA below is the pessimistic bound if clock
#: gating is disallowed.
INTERFACE_INVENTORY = [
    (
        "conditioned FIFO storage",
        {"dffrnq_1": 256},
        "cond_mem[0:7], 32 bits each; one word written per 256 raw samples "
        "(K = 8), so any given word's clock gate opens once per 2048",
        {
            "clock_duty": 1.0 / (COND_WORD_PERIOD * FIFO_DEPTH),
            "activity": 0.25 / (COND_WORD_PERIOD * FIFO_DEPTH),
        },
    ),
    (
        "raw FIFO storage",
        {"dffrnq_1": 256},
        "raw_mem[0:7], 32 bits each; one word written per 32 raw samples, so "
        "any given word's clock gate opens once per 256",
        {
            "clock_duty": 1.0 / (RAW_WORD_PERIOD * FIFO_DEPTH),
            "activity": 0.25 / (RAW_WORD_PERIOD * FIFO_DEPTH),
        },
    ),
    ("FIFO word clock gates", {"icgtp_1": 16}, "one per FIFO word, both FIFOs"),
    ("FIFO head pointers", {"dffrnq_1": 6}, "cond_head, raw_head, 3 bits each (PTR_W)"),
    (
        "FIFO occupancy counters",
        {"dffrnq_1": 8},
        "cond_count, raw_count_w, 4 bits each (CNT_W = TRNG_LEVEL_BITS)",
    ),
    (
        "pointer / counter arithmetic",
        {"xor2_1": 18, "and2_1": 18, "mux2_1": 14},
        "two 3-bit head increments and two 4-bit up/down counters with hold",
    ),
    (
        "FIFO read multiplexers",
        {"mux2_1": 448},
        "two 32-bit 8:1 read muxes (cond_mem[cond_head], raw_mem[raw_head]) "
        "-- 7 mux2 per bit per FIFO. Combinational: their output moves when a "
        "head pointer advances, i.e. once a word is consumed, not once a "
        "sample arrives",
        {"activity": 0.25 / RAW_WORD_PERIOD},
    ),
    (
        "empty / full / avail decode",
        {"nor2_1": 8, "nand2_1": 8, "inv_1": 6, "and2_1": 6},
        "cond_avail / raw_avail / overflow conditions from the two counters",
    ),
    ("raw packing shift register", {"dffrnq_1": 32}, "raw_shift, 32 bits"),
    ("raw packing clock gate", {"icgtp_1": 1}, "shift enabled on raw_valid"),
    ("raw bit counter", {"dffrnq_1": 6}, "raw_bit_count, TRNG_LEVEL_BITS+2 bits"),
    (
        "raw bit counter arithmetic",
        {"xor2_1": 5, "and2_1": 5, "nor2_1": 3, "nand2_1": 2, "inv_1": 1, "mux2_1": 6},
        "increment, wrap at RAW_PACK_BITS = 32, and hold",
    ),
    (
        "control / status registers",
        {"dffrnq_1": 8},
        "state[1:0], ctrl_en, ctrl_out_mode_raw, fail_rct, fail_apt, ovf_data, ovf_raw",
    ),
    (
        "state machine + register decode",
        {"nand2_1": 14, "nor2_1": 10, "inv_1": 8, "and2_1": 10, "or2_1": 6, "mux2_1": 10},
        "4-state FSM next-state logic, 2-bit address decode, write-strobe "
        "qualification, ht_alarm / startup_req / cond_en / cond_flush",
    ),
    (
        "reg_rdata read mux",
        {"mux2_1": 96},
        "combinational 4:1 32-bit read mux over CTRL / STATUS / DATA / RAW_DATA "
        "(always @* in the RTL, so no flops); moves on a host register access",
        {"activity": 0.25 / RAW_WORD_PERIOD},
    ),
    (
        "streaming output mux",
        {"mux2_1": 32},
        "str_data selects the conditioned or raw FIFO head per OUT_MODE; moves "
        "when the selected FIFO head advances",
        {"activity": 0.25 / RAW_WORD_PERIOD},
    ),
]

#: The two FIFOs and the raw shift register with per-flop feedback muxes
#: instead of clock gates -- the pessimistic bound if clock gating is
#: disallowed, mirroring area_estimate.MUX_FEEDBACK_DELTA.
INTERFACE_MUX_FEEDBACK_DELTA = {"icgtp_1": -17, "mux2_1": 544}

BLOCKS = [
    ("conditioner (#8)", area_estimate.INVENTORY, True),
    ("health tests (#11)", HEALTH_TEST_INVENTORY, True),
    ("interface (#26)", INTERFACE_INVENTORY, True),
    ("ring-liveness monitor [DR-0016]", LIVENESS_INVENTORY, False),
]

# ---------------------------------------------------------------------------
# Switching-activity assumptions -- every one of these is an ASSUMPTION and is
# printed with the result. They are the whole modelling freedom in the dynamic
# term.
# ---------------------------------------------------------------------------

#: Expected 0->1 transitions per net per sample-clock cycle, for ordinary
#: logic and register outputs. A TRNG's data path carries random bits, so a
#: register bit toggles about half the cycles it is enabled; most of these
#: registers are enabled on a minority of cycles (FIFO words are written once
#: per 32 raw bits, the APT counters advance every cycle). 0.125 -- a net
#: changing state a quarter of the cycles -- is a mid estimate, not a bound.
DEFAULT_ACTIVITY = 0.125

#: Average fanout of a net, in units of "one 1x input pin". 1.6 is an ordinary
#: random-logic figure.
DEFAULT_FANOUT = 1.6

#: Per-net wiring capacitance allowance, farads. Pre-layout, unverified: no
#: floorplan or router has been run on any of these blocks. Quoted so the
#: sensitivity is visible rather than hidden inside a single total.
DEFAULT_WIRE_CAP_F = 2e-15

# ---------------------------------------------------------------------------
# Liberty parsing
# ---------------------------------------------------------------------------

#: Liberty header units for these libraries, checked at load time:
#: leakage_power_unit 1uW; internal-power energy unit = voltage_unit *
#: current_unit * time_unit = 1 V * 1 mA * 1 ns = 1 pJ; capacitive_load_unit
#: (1, pf).
LEAKAGE_UNIT_W = 1e-6
ENERGY_UNIT_J = 1e-12
CAP_UNIT_F = 1e-12


class LibertyCell:
    __slots__ = ("name", "area", "leak_default", "leak_min", "leak_max", "pin_caps", "internal")

    def __init__(self, name: str):
        self.name = name
        self.area = 0.0
        self.leak_default: float | None = None
        self.leak_min: float | None = None
        self.leak_max: float | None = None
        self.pin_caps: dict[str, float] = {}
        self.internal: list[float] = []


_CELL_RE = re.compile(r"^\s*cell\s*\(([^)]+)\)\s*\{")
_PIN_RE = re.compile(r"^\s*pin\s*\(([^)]+)\)\s*\{")
_ATTR_RE = re.compile(r"^\s*(\w+)\s*:\s*\"?([^\";]+?)\"?\s*;")
_VALUES_RE = re.compile(r"values\s*\(")


def parse_liberty(path: Path) -> dict[str, LibertyCell]:
    """Extract per-cell leakage, area, pin capacitance and internal energy.

    A hand-rolled brace-depth scan rather than a Liberty parser dependency:
    this repository is stdlib-only by convention (``sim/README.md``,
    ``sim/run_corners.py``), and the four attributes needed here are all
    simple ``name : value ;`` lines at known nesting depths.
    """
    cells: dict[str, LibertyCell] = {}
    cell: LibertyCell | None = None
    cell_depth = 0
    depth = 0
    in_leakage = False
    leak_depth = 0
    leak_value: float | None = None
    leak_when = False
    in_pin = False
    pin_depth = 0
    pin_name = ""
    pin_dir = ""
    pin_cap: float | None = None
    in_power_table = False
    table_depth = 0
    table_buf: list[str] = []

    for raw in path.read_text().splitlines():
        line = raw.strip()

        if cell is None:
            m = _CELL_RE.match(raw)
            if m:
                cell = LibertyCell(m.group(1).strip())
                cell_depth = depth
        elif not in_leakage and not in_pin:
            if re.match(r"^\s*leakage_power\s*\(\s*\)\s*\{", raw):
                in_leakage, leak_depth, leak_value, leak_when = True, depth, None, False
            else:
                m = _PIN_RE.match(raw)
                if m:
                    in_pin, pin_depth = True, depth
                    pin_name, pin_dir, pin_cap = m.group(1).strip(), "", None

        if in_leakage:
            a = _ATTR_RE.match(raw)
            if a and a.group(1) == "value":
                leak_value = float(a.group(2))
            elif a and a.group(1) == "when":
                leak_when = True
        elif in_pin:
            a = _ATTR_RE.match(raw)
            if a and a.group(1) == "capacitance" and pin_cap is None:
                pin_cap = float(a.group(2))
            elif a and a.group(1) == "direction":
                pin_dir = a.group(2)
            if in_power_table:
                table_buf.append(line)
            elif _VALUES_RE.search(line) and table_depth:
                in_power_table, table_buf = True, [line]
            elif re.match(r"^\s*(rise|fall)_power\s*\(", raw):
                table_depth = depth

        depth += raw.count("{") - raw.count("}")

        if in_power_table and ")" in line and line.rstrip().endswith((");", ")")):
            joined = " ".join(table_buf)
            nums = re.findall(r"-?\d+\.?\d*(?:[eE][-+]?\d+)?", joined.split("(", 1)[-1])
            vals = [abs(float(n)) for n in nums]
            if vals and cell is not None:
                # Mid-slew entry: representative of a net driven by a 1x cell.
                cell.internal.append(vals[len(vals) // 3])
            in_power_table, table_buf, table_depth = False, [], 0

        if in_leakage and depth <= leak_depth:
            in_leakage = False
            if cell is not None and leak_value is not None:
                if leak_when:
                    cell.leak_min = leak_value if cell.leak_min is None else min(cell.leak_min, leak_value)
                    cell.leak_max = leak_value if cell.leak_max is None else max(cell.leak_max, leak_value)
                else:
                    cell.leak_default = leak_value

        if in_pin and depth <= pin_depth:
            in_pin = False
            if cell is not None and pin_cap is not None and pin_dir == "input":
                cell.pin_caps[pin_name] = pin_cap

        if cell is not None and depth <= cell_depth:
            a = _ATTR_RE.match(raw)
            cells[cell.name] = cell
            cell = None
        elif cell is not None:
            a = _ATTR_RE.match(raw)
            if a and a.group(1) == "area":
                cell.area = float(a.group(2))

    return cells


# ---------------------------------------------------------------------------
# Estimation
# ---------------------------------------------------------------------------


def _cell(cells: dict[str, LibertyCell], suffix: str) -> LibertyCell:
    key = f"{STDCELL_LIB}__{suffix}"
    if key not in cells:
        raise KeyError(f"{key} not found in the Liberty library")
    return cells[key]


def _sections(inventory):
    """Normalise 3-tuple and 4-tuple inventory rows to (counts, overrides)."""
    for row in inventory:
        counts = row[1]
        overrides = row[3] if len(row) > 3 else {}
        yield counts, overrides


def _clock_pin_cap(cell: LibertyCell) -> float:
    for name, cap in cell.pin_caps.items():
        if name.upper() in ("CLK", "CK", "C"):
            return cap
    return 0.0


def estimate_block(cells, inventory, vdd: float, freq: float,
                   activity: float, fanout: float, wire_cap_f: float) -> dict:
    """Leakage and dynamic power for one inventory, section by section.

    Leakage is state-dependent, so three totals are carried: the library's
    state-independent default, and the sums of the per-state minima and
    maxima. Dynamic is split into the clock net, the data nets and the
    library's own internal (short-circuit + internal-node) energy, because
    those three respond very differently to the assumptions and a single
    total would hide which one is carrying the answer.
    """
    leak_def = leak_min = leak_max = 0.0
    leak_flop = leak_comb = 0.0
    flops = cell_count = 0
    clock_cap_f = clock_cap_eff_f = data_cap_f = 0.0
    p_clock = p_data = p_internal = 0.0

    for counts, ov in _sections(inventory):
        sec_activity = ov.get("activity", activity)
        sec_duty = ov.get("clock_duty", 1.0)
        for suffix, n in counts.items():
            c = _cell(cells, suffix)
            cell_count += n
            d = c.leak_default if c.leak_default is not None else (c.leak_max or 0.0)
            leak_def += n * d * LEAKAGE_UNIT_W
            leak_min += n * (c.leak_min if c.leak_min is not None else d) * LEAKAGE_UNIT_W
            leak_max += n * (c.leak_max if c.leak_max is not None else d) * LEAKAGE_UNIT_W
            if suffix.startswith("dff"):
                leak_flop += n * d * LEAKAGE_UNIT_W
            else:
                leak_comb += n * d * LEAKAGE_UNIT_W

            if suffix.startswith("dff") or suffix.startswith("icgtp"):
                if suffix.startswith("dff"):
                    flops += n
                # A clock gate's OWN clock pin is on the always-on trunk.
                duty = 1.0 if suffix.startswith("icgtp") else sec_duty
                cap = n * _clock_pin_cap(c) * CAP_UNIT_F
                clock_cap_f += cap
                clock_cap_eff_f += cap * duty
                p_clock += cap * duty * vdd * vdd * freq

            # Each instance drives one net; its load is `fanout` average 1x
            # input pins plus a wiring allowance.
            avg_in_cap = (sum(c.pin_caps.values()) / len(c.pin_caps)) if c.pin_caps else 0.0
            cap_d = n * (fanout * avg_in_cap * CAP_UNIT_F + wire_cap_f)
            data_cap_f += cap_d
            p_data += sec_activity * cap_d * vdd * vdd * freq

            if c.internal:
                mean_int = sum(c.internal) / len(c.internal) * ENERGY_UNIT_J
                p_internal += n * sec_activity * mean_int * freq

    return {
        "cells": cell_count,
        "flops": flops,
        "leak_default_w": leak_def,
        "leak_min_w": leak_min,
        "leak_max_w": leak_max,
        "leak_flop_w": leak_flop,
        "leak_comb_w": leak_comb,
        "clock_cap_total_f": clock_cap_f,
        "clock_cap_effective_f": clock_cap_eff_f,
        "data_cap_f": data_cap_f,
        "p_clock_w": p_clock,
        "p_data_w": p_data,
        "p_internal_w": p_internal,
        "p_dynamic_w": p_clock + p_data + p_internal,
    }


def lib_path(pdk_root: Path, corner: str) -> Path:
    return pdk_root / "libs.ref" / STDCELL_LIB / "lib" / f"{STDCELL_LIB}__{corner}.lib"


def corner_vdd(corner: str) -> float:
    m = re.search(r"(\d+)v(\d+)$", corner)
    return float(f"{m.group(1)}.{m.group(2)}") if m else 3.3


def run(pdk_root: Path, corner: str, freq: float, activity: float,
        fanout: float, wire_cap_f: float) -> dict:
    path = lib_path(pdk_root, corner)
    if not path.is_file():
        raise FileNotFoundError(f"Liberty library not found: {path}")
    cells = parse_liberty(path)
    vdd = corner_vdd(corner)

    out = {
        "corner": corner,
        "library": STDCELL_LIB,
        "lib_path": str(path),
        "vdd_v": vdd,
        "raw_rate_hz": freq,
        "activity": activity,
        "fanout": fanout,
        "wire_cap_f": wire_cap_f,
        "blocks": {},
    }
    shipped_leak = shipped_leak_min = shipped_leak_max = shipped_dyn = 0.0
    shipped_leak_flop = shipped_leak_comb = 0.0
    shipped_flops = shipped_cells = 0
    for name, inventory, shipped in BLOCKS:
        est = estimate_block(cells, inventory, vdd, freq, activity, fanout, wire_cap_f)
        est["shipped"] = shipped
        out["blocks"][name] = est
        if shipped:
            shipped_leak += est["leak_default_w"]
            shipped_leak_flop += est["leak_flop_w"]
            shipped_leak_comb += est["leak_comb_w"]
            shipped_leak_min += est["leak_min_w"]
            shipped_leak_max += est["leak_max_w"]
            shipped_dyn += est["p_dynamic_w"]
            shipped_flops += est["flops"]
            shipped_cells += est["cells"]

    # Mux-feedback variant: same sections, with the FIFO/shift clock gates
    # replaced by per-flop feedback muxes (so every one of those flops is back
    # on the always-on clock trunk).
    variant = []
    for row in INTERFACE_INVENTORY:
        counts, note = dict(row[1]), row[2]
        ov = dict(row[3]) if len(row) > 3 else {}
        if "FIFO storage" in row[0]:
            counts["mux2_1"] = counts.get("mux2_1", 0) + sum(
                n for s, n in row[1].items() if s.startswith("dff")
            )
            ov["clock_duty"] = 1.0
        elif "clock gate" in row[0]:
            counts = {}
        elif "shift register" in row[0]:
            counts["mux2_1"] = counts.get("mux2_1", 0) + 32
        variant.append((row[0], counts, note, ov))
    out["interface_mux_feedback"] = estimate_block(
        cells, variant, vdd, freq, activity, fanout, wire_cap_f
    )

    out["shipped_total"] = {
        "cells": shipped_cells,
        "flops": shipped_flops,
        "leakage_w": shipped_leak,
        "leakage_flop_w": shipped_leak_flop,
        "leakage_comb_w": shipped_leak_comb,
        "leakage_flop_a": shipped_leak_flop / vdd,
        "leakage_comb_a": shipped_leak_comb / vdd,
        "leakage_min_w": shipped_leak_min,
        "leakage_max_w": shipped_leak_max,
        "leakage_a": shipped_leak / vdd,
        "leakage_min_a": shipped_leak_min / vdd,
        "leakage_max_a": shipped_leak_max / vdd,
        "dynamic_w": shipped_dyn,
        "active_w": shipped_leak + shipped_dyn,
        "active_frac_of_budget": (shipped_leak + shipped_dyn) / ACTIVE_BUDGET_W,
        "idle_frac_of_budget": (shipped_leak / vdd) / IDLE_BUDGET_A,
        "idle_min_frac_of_budget": (shipped_leak_min / vdd) / IDLE_BUDGET_A,
        "idle_max_frac_of_budget": (shipped_leak_max / vdd) / IDLE_BUDGET_A,
    }
    return out


def _w(x: float) -> str:
    for unit, scale in (("W", 1.0), ("mW", 1e-3), ("uW", 1e-6), ("nW", 1e-9), ("pW", 1e-12)):
        if abs(x) >= scale or scale == 1e-12:
            return f"{x / scale:.3g} {unit}"
    return f"{x:g} W"


def _a(x: float) -> str:
    for unit, scale in (("A", 1.0), ("mA", 1e-3), ("uA", 1e-6), ("nA", 1e-9), ("pA", 1e-12)):
        if abs(x) >= scale or scale == 1e-12:
            return f"{x / scale:.3g} {unit}"
    return f"{x:g} A"


def report(res: dict) -> None:
    print(f"library   : {res['library']} @ {res['corner']}  (VDD {res['vdd_v']} V)")
    print(f"            {res['lib_path']}")
    print(f"sample clk: {res['raw_rate_hz']:g} Hz")
    print(
        f"assumed   : activity {res['activity']} 0->1 transitions/net/cycle, "
        f"fanout {res['fanout']}, wire {res['wire_cap_f'] * 1e15:g} fF/net"
    )
    print()
    hdr = (f"| {'Block':<34} | {'cells':>5} | {'flops':>5} | {'leakage':>9} |"
           f" {'P_clk':>9} | {'P_data':>9} | {'P_int':>9} | {'dynamic':>9} |")
    rule = ("|" + "-" * 36 + "|" + "-" * 7 + "|" + "-" * 7 + "|" + "-" * 11
            + ("|" + "-" * 11) * 4 + "|")
    print(hdr)
    print(rule)
    for name, est in res["blocks"].items():
        tag = "" if est["shipped"] else " (not shipped)"
        print(
            f"| {name + tag:<34} | {est['cells']:>5} | {est['flops']:>5} | "
            f"{_w(est['leak_default_w']):>9} | {_w(est['p_clock_w']):>9} | "
            f"{_w(est['p_data_w']):>9} | {_w(est['p_internal_w']):>9} | "
            f"{_w(est['p_dynamic_w']):>9} |"
        )
    t = res["shipped_total"]
    print(rule)
    print(
        f"| {'SHIPPED TOTAL':<34} | {t['cells']:>5} | {t['flops']:>5} | "
        f"{_w(t['leakage_w']):>9} | {'':>9} | {'':>9} | {'':>9} | "
        f"{_w(t['dynamic_w']):>9} |"
    )
    print()
    print(f"digital active (leakage + dynamic) : {_w(t['active_w'])}"
          f"   = {t['active_frac_of_budget']:.1%} of the < 500 uW row")
    print(f"digital idle   (leakage only)      : {_a(t['leakage_a'])}"
          f"   = {t['idle_frac_of_budget']:.1%} of the < 1 uA row")
    print(f"  of which flip-flops (enumerated) : {_a(t['leakage_flop_a'])}"
          f"   = {t['leakage_flop_a'] / IDLE_BUDGET_A:.0%} of that row on their own")
    print(f"  of which combinational (estimated): {_a(t['leakage_comb_a'])}"
          f"   = {t['leakage_comb_a'] / IDLE_BUDGET_A:.0%} of that row")
    print(f"  leakage range over input states  : {_a(t['leakage_min_a'])}"
          f" .. {_a(t['leakage_max_a'])}"
          f"  ({t['idle_min_frac_of_budget']:.0%} .. {t['idle_max_frac_of_budget']:.0%}"
          " of that row)")
    print()
    mf = res["interface_mux_feedback"]
    iface = res["blocks"]["interface (#26)"]
    print(
        "interface without clock gating (per-flop feedback muxes): "
        f"leakage {_w(mf['leak_default_w'])} (vs {_w(iface['leak_default_w'])}), "
        f"dynamic {_w(mf['p_dynamic_w'])} (vs {_w(iface['p_dynamic_w'])})"
    )
    print()
    print("This is a [DR-0004] Tier 2 ESTIMATE, not a measurement. No synthesiser,")
    print("floorplan or router has been run on any of these blocks; the leakage")
    print("column is characterised library data against an enumerated gate")
    print("inventory, the dynamic column additionally rests on the activity,")
    print("fanout and wire-capacitance assumptions printed above.")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--corner", default=CORNER_IDLE,
                   help=f"Liberty corner (default {CORNER_IDLE}, the idle-binding one). "
                        f"Others shipped: {CORNER_ACTIVE}, {CORNER_NOMINAL}, {CORNER_SLOW}")
    p.add_argument("--all-corners", action="store_true",
                   help="report every characterised corner in the 3.3 V family")
    p.add_argument("--raw-rate", type=float, default=RAW_RATE_HZ,
                   help="sample-clock rate in Hz (default 1e6, the ratified row; "
                        "DR-0010 proposes 500)")
    p.add_argument("--activity", type=float, default=DEFAULT_ACTIVITY)
    p.add_argument("--fanout", type=float, default=DEFAULT_FANOUT)
    p.add_argument("--wire-cap-ff", type=float, default=DEFAULT_WIRE_CAP_F * 1e15)
    p.add_argument("--pdk-root", type=Path, help="override PDK discovery")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    args = p.parse_args(argv)

    if args.pdk_root:
        root = args.pdk_root
    else:
        try:
            root = pdk_mod.find_pdk().path
        except pdk_mod.PdkNotFound as exc:
            print(f"gf180mcu PDK not found: {exc}", file=sys.stderr)
            return 2

    corners = ([CORNER_ACTIVE, CORNER_IDLE, CORNER_NOMINAL, CORNER_SLOW]
               if args.all_corners else [args.corner])
    results = []
    for corner in corners:
        results.append(run(root, corner, args.raw_rate, args.activity,
                           args.fanout, args.wire_cap_ff * 1e-15))

    if args.json:
        print(json.dumps(results if args.all_corners else results[0], indent=2))
        return 0
    for i, res in enumerate(results):
        if i:
            print("\n" + "=" * 78 + "\n")
        report(res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
