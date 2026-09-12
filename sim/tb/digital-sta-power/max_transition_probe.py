#!/usr/bin/env python3
"""Where the routed digital section violates the library's own
`max_transition`, what drives it, and what that costs -- as a runnable
measurement rather than an assertion.

    python3 sim/tb/digital-sta-power/max_transition_probe.py           # the grid
    python3 sim/tb/digital-sta-power/max_transition_probe.py --check   # gate it
    python3 sim/tb/digital-sta-power/max_transition_probe.py --liberty tt_025C_3v30 --rc max

Why this exists
---------------
`run_sta.py` asks OpenSTA for the library's own max-transition check
(`report_check_types -max_slew`, added for [#233]) and every record carries
the three metrics that fall out: `max_slew_limit_ns`, `max_slew_slack_ns`,
`max_slew_violations`. Nine of the fifteen corners report violations. That
is enough to *state* the finding and not nearly enough to *decide* what to
do about it ([#237]), because a violation count says nothing about which
nets are involved, whether they are one structure or fifteen accidents,
whether the design's reported timing and power actually ride on the
extrapolated tables, or what a constraint would have to say to remove them.

This probe answers those four questions off the committed DEF, at every
corner, without re-placing or re-routing anything:

1. **Which nets.** Every pin OpenSTA's own `-max_slew -violators` check
   names is resolved to its net, that net's driver pin, the driver's
   instance and library cell, and the net's total pin count. A violation
   that is one over-fanned net repeated across corners is a
   drive-strength/fanout outcome of the build flow; a violation that moves
   from net to net with the corner would be something else entirely, and
   the two call for different fixes.
2. **Whether the reported numbers ride on it.** `report_checks -through`
   over the whole violator set gives the worst setup slack of any path that
   passes through a max-transition-violating pin, against the design-wide
   worst setup slack at the same corner. If they are the same number, the
   critical path this repository quotes *is* an extrapolated path.
3. **What it costs in power.** `report_power -instances` over every
   instance owning a violating pin (plus the offending nets' drivers),
   against the design total, so "the internal-energy tables are being
   extrapolated" carries a fraction rather than a shrug.
4. **What a constraint would have to say.** A liberty corner's
   `max_transition` is not a fixed fraction of the slew the design actually
   produces there: between `ss_125C_3v00` and `ff_125C_3v60` this library's
   limit falls by 2.54x while this design's worst slew falls by ~2.16x. So
   the `set_max_transition` that would have to be stated at
   `layout/digital/build.py`'s single P&R corner for *every* corner to come
   out clean is not that corner's own library limit -- it is a smaller,
   derived number. `--json`'s `pnr_corner_target` reports it, computed from
   the measured per-corner slews rather than assumed.

What it deliberately does not do
--------------------------------
It does not re-run place-and-route, and it does not mint records. The
fifteen `digital-sta-power` records already describe this DEF at these
corners; this is the *decomposition* behind three of their numbers, in the
same relationship `sdc_treatment_probe.py` has to the `interface_loads:`
block. `sim/characterization-digital-sta-area-power.md` section 2a states
the verdict this measurement supports, and
`sim/tools/digital_corner_characterization.py --check` gates the record-side
half of it with no PDK needed.

`--check` needs `openroad` on `PATH` and the gf180mcu PDK, like the sweep
itself; with neither it exits 3 and says so, so a PDK-less CI run can skip
it deliberately rather than silently.

[#233]: https://github.com/2AMLogic/gf180-trng/issues/233
[#237]: https://github.com/2AMLogic/gf180-trng/issues/237
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TB_DIR))

import run_sta  # noqa: E402

REPO_ROOT = run_sta.REPO_ROOT

#: Scratch root, gitignored like the sweep's own (`layout/.work/`).
WORK_DIR = REPO_ROOT / "layout" / ".work" / "digital-sta-max-transition"

#: The liberty corner `layout/digital/build.py` implements at -- the single
#: deck OpenROAD's own `repair_design` sees during place-and-route, and
#: therefore the deck any `set_max_transition` this flow could state would
#: have to be expressed in. Read from that module rather than restated, so
#: the two cannot drift.
PNR_CORNER = "ss_125C_3v00"

#: The findings `sim/characterization-digital-sta-area-power.md` section 2a's
#: verdict rests on, written after the measurement in the same shape
#: `sim/tools/digital_corner_characterization.py`'s own `RECORDED` table and
#: `sim/tools/sampler_bit_bias_variants.py`'s `RECORDED_VERDICT` use.
#: ``--check`` fails if the committed DEF stops supporting them.
RECORDED = {
    # Every pin the max-transition check names, at every corner, is on one of
    # these four nets. Named rather than counted: the verdict is that this is
    # *one structure* (four high-fanout nets built by synthesis + P&R), not a
    # corner-dependent scatter, and a net appearing here that is not in this
    # set would break that reading.
    "violating_nets": (
        "u_conditioner/_095_",
        "u_interface/_0606_",
        "u_interface/_0999_",
        "u_interface/_1190_",
    ),
    # Corners with at least one violating pin, of the 15.
    "violating_corners": 9,
    # The worst setup slack, over all corners, of any path passing through a
    # max-transition-violating pin. Positive: those paths still close against
    # the 50 ns constraint, which is what bounds the residual risk. It is also
    # exactly this repository's headline setup margin (section 2, +21.935 ns at
    # ss_125C_3v00/rc-max), because at every violating corner the design's
    # critical path *is* a path through a violating pin.
    "worst_setup_slack_through_violators_ns": 21.935,
    # The violating instances' share of total power, worst over all corners
    # (ff_125C_3v60/rc-max).
    "power_share_max": 0.0184,
    # The library's sibling max_capacitance check, which nothing in this
    # repository had asked for either until this probe. Worst corner
    # (ff_125C_3v60/rc-max) -- non-zero, and part of the accepted residual.
    "max_capacitance_violations": 6,
    # The design's worst net fanout, in load pins (`rst_n`). Measured from
    # topology rather than checked against the library, which declares no
    # max_fanout of any kind -- see `_tcl` below. Quoted in section 2a because
    # it is clean at every corner while a 13-load net violates at seven, which
    # is what rules `set_max_fanout` out as the lever here.
    "max_net_fanout": 201,
}

#: Fractional tolerance for the numeric gates above -- the same 1 % and the
#: same reasoning as `sim/tools/digital_corner_characterization.py`'s
#: `TOLERANCE`: the analysis is deterministic but not bit-portable across
#: OpenROAD builds or PDK revisions.
TOLERANCE = 0.01

#: Load-pin count at or above which a net is counted in
#: `nets_over_fanout_threshold`. Not a limit and not a rule -- this library
#: declares no `max_fanout` of any kind (see `_tcl` below), so there is no
#: library number to compare against. 16 is stated here purely as a reporting
#: bucket, chosen because the nets this probe finds violating `max_transition`
#: all carry more than that and the great majority of the design's nets carry
#: far fewer, which is the shape the count is there to show.
_FANOUT_THRESHOLD = 16

_SCALAR = re.compile(r"^PROBE\s+(\S+)\s+(\S+)\s*$", re.M)
_MAX_FANOUT_NET = re.compile(r"^PROBE_MAXFANOUTNET\s+(\S+)\s*$", re.M)
_NET = re.compile(
    r"^PROBE_NET\s+(\S+)\s+pins\s+(\d+)\s+driver\s+(\S+)\s+master\s+(\S+)\s*$", re.M
)
_VIOLATOR_PIN = re.compile(r"^PROBE_PIN\s+(\S+)\s+net\s+(\S+)\s*$", re.M)
_THROUGH = re.compile(
    r"PROBE_THROUGH_BEGIN\n(.*?)PROBE_THROUGH_END", re.S
)
_SUMMARY_ROW = re.compile(r"^\S+.*?\)\s+(-?[\d.]+)\s*$", re.M)
_POWER_INSTANCE_ROW = re.compile(
    r"^\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+(\S+)\s*$", re.M
)
_POWER_BLOCK = re.compile(r"PROBE_POWER_BEGIN\n(.*?)PROBE_POWER_END", re.S)
_TOTAL_POWER_BLOCK = re.compile(
    r"PROBE_TOTALPOWER_BEGIN\n(.*?)PROBE_TOTALPOWER_END", re.S
)
_TOTAL_ROW = re.compile(
    r"^Total\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)", re.M
)


# --------------------------------------------------------------------------- #
# The session
# --------------------------------------------------------------------------- #


def _tcl(pdk, corner: run_sta.Corner, spef_path: Path) -> str:
    """One OpenROAD session: `run_sta.py`'s own constraint-period setup, then
    the max-transition decomposition.

    The first half is deliberately assembled from `run_sta.py`'s own helpers
    (same liberty/LEF/DEF, same 50 ns `create_clock`, same six [#233]
    `set_input_transition` lines, same OpenRCX deck, same
    `set_propagated_clock`, same `set_power_activity`) so every number this
    probe reports is decomposing the numbers the records already carry and
    not a differently-constrained session that happens to look similar.

    The violator set is captured *inside* the session
    (`sta::redirect_string_begin`), not parsed out of the log and fed back in
    a second run: `report_check_types` names the pins, and those same pin
    objects are then what the net/driver walk, the `report_checks -through`
    query and the `report_power -instances` query are issued over. One
    session, one extraction, one set of pins -- nothing to go out of step.
    """
    paths = run_sta.deck_paths(pdk)
    trunks = run_sta.digital_facing_trunks()
    slew = run_sta.liberty_slew_convention(run_sta.liberty_path(pdk, corner.liberty))
    lines = [
        f"read_liberty {run_sta.liberty_path(pdk, corner.liberty)}",
        f"read_lef {paths['tech_lef']}",
        f"read_lef {paths['cell_lef']}",
        f"read_def {run_sta.DEF_PATH}",
        f"create_clock -name {run_sta.CLOCK_PORT} "
        f"-period {run_sta.CONSTRAINT_PERIOD_NS} [get_ports {run_sta.CLOCK_PORT}]",
    ]
    lines += [
        f"set_input_transition {t.transition_ns(slew):.6f} "
        f"[get_ports {{{t.def_pin}}}]"
        for t in trunks
    ]
    lines += [
        "define_process_corner -ext_model_index 0 X",
        "extract_parasitics -ext_model_file "
        f"{run_sta.rcx_rules_path(pdk, corner.rc)}",
        f"write_spef {spef_path}",
        f"read_spef {spef_path}",
        "set_propagated_clock [all_clocks]",
        f"set_power_activity -global -activity {run_sta.ACTIVITY} "
        f"-duty {run_sta.ACTIVITY_DUTY}",
        "",
        "# The three metrics every record already carries, restated here so a",
        "# probe run is checkable against the record for the same corner.",
        'puts "PROBE max_slew_limit_ns [sta::max_slew_check_limit]"',
        'set _msslack [sta::max_slew_check_slack]',
        'if {$_msslack eq ""} { set _msslack nan }',
        'puts "PROBE max_slew_slack_ns $_msslack"',
        'puts "PROBE max_slew_violations [sta::max_slew_violation_count]"',
        'puts "PROBE worst_setup_slack_s [sta::worst_slack_cmd max]"',
        'puts "PROBE worst_hold_slack_s [sta::worst_slack_cmd min]"',
        "",
        "# The library's sibling design-rule check. Reported for the same",
        "# reason max_transition now is: nothing in this repository had asked",
        "# for it, so 'it is clean' was an assumption rather than a measurement.",
        "# The limit is in the deck's own capacitive_load_unit (1 pF for every",
        "# deck in this family), not farads -- read from the liberty header by",
        "# `liberty_capacitive_load_unit_f` rather than assumed here.",
        'puts "PROBE max_capacitance_violations [sta::max_capacitance_violation_count]"',
        'set _cl [sta::max_capacitance_check_limit]',
        'if {$_cl eq ""} { set _cl nan }',
        'puts "PROBE max_capacitance_limit $_cl"',
        'set _cs [sta::max_capacitance_check_slack]',
        'if {$_cs eq ""} { set _cs nan }',
        'puts "PROBE max_capacitance_slack $_cs"',
        "",
        "# `sta::max_fanout_violation_count` is NOT called here, and the",
        "# omission is deliberate rather than an oversight: on this design it",
        "# takes OpenROAD down with SIGSEGV inside sta::CheckFanouts::check",
        "# (reproduced on 26Q3-1510-g6cb3f2b704 at every corner). It is also",
        "# not the question worth asking -- `sta::max_fanout_check_limit`",
        "# returns 1e30 because this library declares no default_max_fanout and",
        "# no per-pin max_fanout at all, so there is nothing for OpenSTA to",
        "# check against and a fanout constraint here could only ever come from",
        "# SDC. What the fanout question actually needs is the design's own",
        "# topology, which is measured directly below instead.",
        f"set _fanout_threshold {_FANOUT_THRESHOLD}",
        "set _max_fanout 0",
        'set _max_fanout_net ""',
        "set _over 0",
        "foreach _net [get_nets *] {",
        "  set _loads 0",
        "  foreach _q [get_pins -of_objects $_net] {",
        '    if {[sta::pin_direction $_q] == "input"} { incr _loads }',
        "  }",
        "  if {$_loads > $_max_fanout} {",
        "    set _max_fanout $_loads",
        "    set _max_fanout_net [get_full_name $_net]",
        "  }",
        "  if {$_loads >= $_fanout_threshold} { incr _over }",
        "}",
        'puts "PROBE max_net_fanout $_max_fanout"',
        'puts "PROBE nets_over_fanout_threshold $_over"',
        'puts "PROBE_MAXFANOUTNET $_max_fanout_net"',
        "",
        "# Capture the violator list in-session rather than round-tripping it",
        "# through the log: these same pin objects are what every query below",
        "# is issued over.",
        "sta::redirect_string_begin",
        "report_check_types -max_slew -violators -verbose",
        "set _report [sta::redirect_string_end]",
        "set _pins {}",
        "foreach _line [split $_report \"\\n\"] {",
        "  if {[regexp {^Pin\\s+(\\S+)(\\s+[\\^v])?\\s*$} $_line -> _n]} {",
        "    lappend _pins $_n",
        "  }",
        "}",
        'puts "PROBE violator_pins_parsed [llength $_pins]"',
        "",
        "# Each violating pin -> its net -> that net's driver and total pin",
        "# count. `sta::pin_direction` is the authority on which pin is the",
        "# driver; this module does not re-derive it from the netlist.",
        "array set _nets {}",
        "foreach _p $_pins {",
        "  set _net [get_nets -of_objects [get_pins $_p]]",
        "  set _nn [get_full_name $_net]",
        '  puts "PROBE_PIN $_p net $_nn"',
        "  if {![info exists _nets($_nn)]} {",
        "    set _all [get_pins -of_objects $_net]",
        '    set _drv ""',
        "    foreach _q $_all {",
        '      if {[sta::pin_direction $_q] != "input"} { set _drv [get_full_name $_q] }',
        "    }",
        "    set _nets($_nn) [list [llength $_all] $_drv]",
        "  }",
        "}",
        "foreach _nn [lsort [array names _nets]] {",
        "  lassign $_nets($_nn) _cnt _drv",
        '  set _ref "none"',
        '  if {$_drv ne ""} {',
        "    set _inst [file dirname $_drv]",
        '    if {$_inst ne "."} { set _ref [get_property [get_cells $_inst] ref_name] }',
        "  }",
        '  if {$_drv eq ""} { set _drv "none" }',
        '  puts "PROBE_NET $_nn pins $_cnt driver $_drv master $_ref"',
        "}",
        "",
        "# Does the design's reported timing ride on an extrapolated path?",
        "# `-through` with the whole violator list means 'any path through any",
        "# of these pins'; compare the answer against worst_setup_slack_s above.",
        'puts "PROBE_THROUGH_BEGIN"',
        "if {[llength $_pins] > 0} {",
        "  report_checks -through $_pins -path_delay max -group_path_count 1 "
        "-digits 6 -format summary",
        "}",
        'puts "PROBE_THROUGH_END"',
        "",
        "# ... and how much of the design's power is booked to cells whose",
        "# input slew is outside the characterised range. Every instance that",
        "# owns a violating pin, plus each offending net's driver.",
        "set _insts {}",
        "foreach _p $_pins {",
        "  set _i [file dirname $_p]",
        '  if {$_i ne "."} { lappend _insts $_i }',
        "}",
        "foreach _nn [array names _nets] {",
        "  lassign $_nets($_nn) _c _d",
        '  if {$_d ne ""} {',
        "    set _i [file dirname $_d]",
        '    if {$_i ne "."} { lappend _insts $_i }',
        "  }",
        "}",
        "set _insts [lsort -unique $_insts]",
        'puts "PROBE violating_instances [llength $_insts]"',
        'puts "PROBE_POWER_BEGIN"',
        "if {[llength $_insts] > 0} { report_power -instances [get_cells $_insts] -digits 10 }",
        'puts "PROBE_POWER_END"',
        'puts "PROBE_TOTALPOWER_BEGIN"',
        "report_power -digits 10",
        'puts "PROBE_TOTALPOWER_END"',
    ]
    return "\n".join(lines) + "\n"


def _run(pdk, corner: run_sta.Corner) -> str:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{corner.liberty}.{corner.rc}"
    script = WORK_DIR / f"max-transition-{stem}.tcl"
    log = WORK_DIR / f"max-transition-{stem}.log"
    script.write_text(_tcl(pdk, corner, WORK_DIR / f"{stem}.spef"))
    done = subprocess.run(
        ["openroad", "-no_init", "-exit", str(script)],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
        timeout=run_sta.OPENROAD_TIMEOUT_S, check=False,
    )
    text = done.stdout + ("\n" + done.stderr if done.stderr.strip() else "")
    log.write_text(text)
    if done.returncode != 0:
        raise run_sta.StaError(f"openroad exited {done.returncode}; see {log}")
    return text


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #


def _parse_power_share(text: str) -> tuple[float, float]:
    """`(power booked to violating instances, design total)`, in watts.

    `report_power -instances` prints one row per instance with the name
    *last*; `report_power`'s own summary prints a `Total` row with the name
    absent. Parsed separately, from their own delimited blocks, so neither
    can be mistaken for the other.
    """
    block = _POWER_BLOCK.search(text)
    violating = 0.0
    if block is not None:
        for m in _POWER_INSTANCE_ROW.finditer(block.group(1)):
            violating += float(m.group(4))
    total_block = _TOTAL_POWER_BLOCK.search(text)
    if total_block is None:
        raise run_sta.StaError("no report_power summary block in the OpenROAD log")
    total = _TOTAL_ROW.search(total_block.group(1))
    if total is None:
        raise run_sta.StaError("no report_power Total row in the OpenROAD log")
    return violating, float(total.group(4))


def _parse_through_slack(text: str) -> float | None:
    """Worst setup slack of any path through a violating pin, in ns, or
    `None` when the corner has no violators to pass through."""
    block = _THROUGH.search(text)
    if block is None:
        raise run_sta.StaError("no PROBE_THROUGH block in the OpenROAD log")
    rows = _SUMMARY_ROW.findall(block.group(1))
    return float(rows[0]) if rows else None


def parse(text: str) -> dict:
    scalars = {}
    for m in _SCALAR.finditer(text):
        try:
            scalars[m.group(1)] = float(m.group(2))
        except ValueError:
            scalars[m.group(1)] = float("nan")
    if "max_slew_limit_ns" not in scalars:
        raise run_sta.StaError("no PROBE metrics in the OpenROAD log")

    nets = {}
    for m in _NET.finditer(text):
        nets[m.group(1)] = {
            "net": m.group(1),
            "pins_on_net": int(m.group(2)),
            "driver_pin": m.group(3),
            "driver_master": m.group(4),
            "violating_pins": 0,
        }
    for m in _VIOLATOR_PIN.finditer(text):
        if m.group(2) in nets:
            nets[m.group(2)]["violating_pins"] += 1

    violating_w, total_w = _parse_power_share(text)
    limit = scalars["max_slew_limit_ns"]
    slack = scalars["max_slew_slack_ns"]
    max_fanout_net = _MAX_FANOUT_NET.search(text)
    return {
        "max_slew_limit_ns": limit,
        "max_slew_slack_ns": slack,
        # OpenSTA's slack is `limit - slew`, so the worst slew the design
        # actually produces at this corner follows directly. Reported because
        # it, not the slack, is what scales across corners -- see
        # `pnr_corner_target` below.
        "worst_slew_ns": limit - slack,
        "max_slew_violations": int(scalars["max_slew_violations"]),
        "violator_pins_parsed": int(scalars.get("violator_pins_parsed", 0)),
        "worst_setup_slack_ns": scalars["worst_setup_slack_s"] * 1e9,
        "worst_hold_slack_ns": scalars["worst_hold_slack_s"] * 1e9,
        "worst_setup_slack_through_violators_ns": _parse_through_slack(text),
        "max_capacitance_violations": int(scalars["max_capacitance_violations"]),
        "max_capacitance_limit": scalars["max_capacitance_limit"],
        "max_capacitance_slack": scalars["max_capacitance_slack"],
        "max_net_fanout": int(scalars["max_net_fanout"]),
        "max_fanout_net": max_fanout_net.group(1) if max_fanout_net else None,
        "fanout_threshold": _FANOUT_THRESHOLD,
        "nets_over_fanout_threshold": int(scalars["nets_over_fanout_threshold"]),
        "violating_instances": int(scalars.get("violating_instances", 0)),
        "violating_instance_power_w": violating_w,
        "total_power_w": total_w,
        "violating_power_share": (violating_w / total_w) if total_w else float("nan"),
        "nets": sorted(nets.values(), key=lambda n: -n["pins_on_net"]),
    }


# --------------------------------------------------------------------------- #
# Derivation
# --------------------------------------------------------------------------- #


def pnr_corner_target(rows: list[dict]) -> dict:
    """What a `set_max_transition` at the P&R corner would have to say for
    every corner to come out clean -- derived from the measured slews.

    `layout/digital/build.py` reads exactly one liberty deck (`PNR_CORNER`),
    so OpenROAD's `repair_design` only ever sees that deck's own
    `max_transition`, and any constraint this flow could state would be a
    single scalar in that deck's domain. That scalar is **not** the P&R
    corner's own library limit, because the limit and the slew do not scale
    together across the corner set: this function measures the ratio instead
    of assuming it.

    For each corner `c` sharing an interconnect deck with the P&R corner,
    the slew at the P&R corner that would leave `c` exactly at its limit is
    `limit_c * slew_pnr / slew_c`. The binding corner is the one where that
    is smallest, and that number is the target. A ratio > 1 against the P&R
    corner's own limit would mean the library limit is already the binding
    constraint and no extra tightening would be needed; a ratio < 1 is by
    how much the flow would have to over-constrain itself relative to the
    deck it implements at.

    Returns `{}` when no corner violates -- there is nothing to target.
    """
    by_label = {(r["corner"]["liberty"], r["corner"]["rc"]): r for r in rows}
    requirements = []
    for (liberty, rc), row in sorted(by_label.items()):
        pnr = by_label.get((PNR_CORNER, rc))
        if pnr is None or row["worst_slew_ns"] <= 0:
            continue
        requirements.append({
            "corner": f"{liberty}/rc-{rc}",
            "limit_ns": row["max_slew_limit_ns"],
            "worst_slew_ns": row["worst_slew_ns"],
            "slew_vs_pnr_corner": row["worst_slew_ns"] / pnr["worst_slew_ns"],
            "required_pnr_slew_ns": (
                row["max_slew_limit_ns"] * pnr["worst_slew_ns"] / row["worst_slew_ns"]
            ),
        })
    if not requirements:
        return {}
    binding = min(requirements, key=lambda r: r["required_pnr_slew_ns"])
    # The P&R corner's own limit, from whichever of its interconnect decks
    # this run covered -- `max_transition` is a liberty attribute, so all
    # three carry the same number, and keying on one of them by name would
    # make a partial-grid run fail instead of reporting a partial answer.
    pnr_limit = next(
        row["max_slew_limit_ns"]
        for (liberty, _rc), row in sorted(by_label.items())
        if liberty == PNR_CORNER
    )
    return {
        "pnr_corner": PNR_CORNER,
        "pnr_corner_library_limit_ns": pnr_limit,
        "binding_corner": binding["corner"],
        "required_set_max_transition_ns": binding["required_pnr_slew_ns"],
        "fraction_of_library_limit": binding["required_pnr_slew_ns"] / pnr_limit,
        "requirements": requirements,
    }


def survey(pdk, corners: list[run_sta.Corner]) -> dict:
    rows = []
    for corner in corners:
        parsed = parse(_run(pdk, corner))
        parsed["corner"] = {
            "liberty": corner.liberty, "rc": corner.rc, "label": corner.label
        }
        rows.append(parsed)
    trunk_pins = {t.def_pin for t in run_sta.digital_facing_trunks()}
    all_nets = sorted({n["net"] for r in rows for n in r["nets"]})
    return {
        "def": str(run_sta.DEF_PATH.relative_to(REPO_ROOT)),
        "def_sha256": run_sta.report.sha256_file(run_sta.DEF_PATH),
        "constraint_period_ns": run_sta.CONSTRAINT_PERIOD_NS,
        "corners": rows,
        "violating_nets": all_nets,
        "violating_corner_count": sum(1 for r in rows if r["max_slew_violations"]),
        "trunk_ports": sorted(trunk_pins),
        "pnr_corner_target": pnr_corner_target(rows),
    }


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #


def _print(result: dict) -> None:
    print(f"DEF {result['def']}  sha256:{result['def_sha256'][:16]}…  "
          f"constraint {result['constraint_period_ns']:g} ns")
    print()
    print(f"{'corner':22s} {'limit':>7s} {'worst slew':>11s} {'slack':>9s} "
          f"{'viol':>5s} {'setup (design)':>15s} {'setup (through)':>16s} "
          f"{'P share':>8s}")
    for row in result["corners"]:
        through = row["worst_setup_slack_through_violators_ns"]
        print(
            f"{row['corner']['label']:22s} {row['max_slew_limit_ns']:7.2f} "
            f"{row['worst_slew_ns']:11.4f} {row['max_slew_slack_ns']:9.4f} "
            f"{row['max_slew_violations']:5d} {row['worst_setup_slack_ns']:15.4f} "
            f"{('n/a' if through is None else f'{through:.4f}'):>16s} "
            f"{row['violating_power_share'] * 100:7.3f}%"
        )
    print()
    print("== The nets the violating pins are on ==")
    seen: dict[str, dict] = {}
    for row in result["corners"]:
        for net in row["nets"]:
            entry = seen.setdefault(net["net"], dict(net, corners=[], worst=0))
            entry["corners"].append(row["corner"]["label"])
            entry["worst"] = max(entry["worst"], net["violating_pins"])
    print(f"{'net':24s} {'pins':>5s} {'driver':>22s} {'master':>34s} "
          f"{'corners':>8s} {'worst viol':>11s}")
    for net in sorted(seen.values(), key=lambda n: -n["pins_on_net"]):
        print(f"{net['net']:24s} {net['pins_on_net']:5d} {net['driver_pin']:>22s} "
              f"{net['driver_master']:>34s} {len(net['corners']):8d} "
              f"{net['worst']:11d}")
    print()
    dr = result["corners"][0]
    print("== The library's sibling design-rule checks ==")
    print(f"{'corner':22s} {'max_cap limit':>14s} {'max_cap slack':>14s} "
          f"{'violations':>11s}")
    for row in result["corners"]:
        print(f"{row['corner']['label']:22s} {row['max_capacitance_limit']:14.4f} "
              f"{row['max_capacitance_slack']:14.4f} "
              f"{row['max_capacitance_violations']:11d}")
    print("  (limit and slack in the decks' own capacitive_load_unit, 1 pF)")
    print(f"  max_fanout: this library declares none at all -- no "
          f"default_max_fanout, no per-pin max_fanout, so OpenSTA has nothing")
    print(f"  to check against. Measured topology instead: worst net fanout "
          f"{dr['max_net_fanout']} loads ({dr['max_fanout_net']}), "
          f"{dr['nets_over_fanout_threshold']} nets at or above "
          f"{dr['fanout_threshold']} loads.")
    print()
    target = result["pnr_corner_target"]
    if target:
        print(f"== What a set_max_transition at the P&R corner "
              f"({target['pnr_corner']}) would have to say ==")
        print(f"{'corner':22s} {'limit':>7s} {'worst slew':>11s} "
              f"{'slew / P&R corner':>18s} {'required P&R slew':>18s}")
        for req in target["requirements"]:
            print(f"{req['corner']:22s} {req['limit_ns']:7.2f} "
                  f"{req['worst_slew_ns']:11.4f} {req['slew_vs_pnr_corner']:18.4f} "
                  f"{req['required_pnr_slew_ns']:18.4f}")
        print()
        print(f"  binding corner: {target['binding_corner']}")
        print(f"  required set_max_transition at {target['pnr_corner']}: "
              f"{target['required_set_max_transition_ns']:.4f} ns "
              f"({target['fraction_of_library_limit'] * 100:.1f} % of that deck's "
              f"own {target['pnr_corner_library_limit_ns']:g} ns limit)")


# --------------------------------------------------------------------------- #
# The gate
# --------------------------------------------------------------------------- #


def check(result: dict) -> list[str]:
    """Return the list of failures; empty means section 2a's verdict holds."""
    fails: list[str] = []

    unexpected = set(result["violating_nets"]) - set(RECORDED["violating_nets"])
    if unexpected:
        fails.append(
            "the max-transition violation has spread to nets outside the "
            "recorded structure: " + ", ".join(sorted(unexpected))
            + " -- section 2a's verdict is that this is one set of over-fanned "
            "nets, not a corner-dependent scatter"
        )
    missing = set(RECORDED["violating_nets"]) - set(result["violating_nets"])
    if missing:
        fails.append(
            "these recorded violating nets no longer violate anywhere: "
            + ", ".join(sorted(missing))
            + " -- good news, but section 2a and RECORDED now overstate the "
            "problem and must be re-read against the current DEF"
        )
    if result["violating_corner_count"] != RECORDED["violating_corners"]:
        fails.append(
            f"{result['violating_corner_count']} of {len(result['corners'])} "
            "corners report a max-transition violation; RECORDED says "
            f"{RECORDED['violating_corners']}"
        )

    trunk_ports = set(result["trunk_ports"])
    for row in result["corners"]:
        on_trunk = trunk_ports & {net["net"] for net in row["nets"]}
        if on_trunk:
            fails.append(
                f"{row['corner']['label']}: a violating pin is now on a #233 "
                f"trunk net ({', '.join(sorted(on_trunk))}) -- section 2a's "
                "'pre-existing and not #233's' reading no longer holds"
            )

    through = [
        row["worst_setup_slack_through_violators_ns"] for row in result["corners"]
        if row["worst_setup_slack_through_violators_ns"] is not None
    ]
    if not through:
        fails.append(
            "no corner reports a timing path through a violating pin -- the "
            "residual-risk bound section 2a states cannot be re-derived"
        )
    else:
        worst = min(through)
        if worst <= 0:
            fails.append(
                f"a path through a max-transition-violating pin now fails setup "
                f"({worst:.4f} ns) -- the accepted residual risk was that those "
                "paths still close with margin"
            )
        want = RECORDED["worst_setup_slack_through_violators_ns"]
        if abs(worst - want) / abs(want) > TOLERANCE:
            fails.append(
                f"worst setup slack through a violating pin is {worst:.4f} ns, "
                f"RECORDED says {want:.4f} ns (> {TOLERANCE * 100:g} % apart)"
            )

    share = max(row["violating_power_share"] for row in result["corners"])
    if share > RECORDED["power_share_max"] * (1 + TOLERANCE):
        fails.append(
            f"the cells whose input slew is outside the characterised range now "
            f"carry {share * 100:.3f} % of total power; RECORDED says at most "
            f"{RECORDED['power_share_max'] * 100:.3f} %"
        )

    worst_cap = max(row["max_capacitance_violations"] for row in result["corners"])
    if worst_cap != RECORDED["max_capacitance_violations"]:
        fails.append(
            f"max_capacitance: worst corner reports {worst_cap} violating pins, "
            f"RECORDED says {RECORDED['max_capacitance_violations']} -- the "
            "library's sibling design-rule check has moved and section 2a's "
            "accepted residual risk is stated against the recorded figure"
        )
    # Fanout is topology, so every corner must report the same number; a
    # spread would mean the corners did not read the same design, which is a
    # louder failure than the value being wrong.
    fanouts = {row["max_net_fanout"] for row in result["corners"]}
    if len(fanouts) > 1:
        fails.append(
            f"the corners disagree on the design's worst net fanout "
            f"({sorted(fanouts)}) -- fanout is corner-independent, so this "
            "means they did not all read the same DEF"
        )
    elif fanouts != {RECORDED["max_net_fanout"]}:
        fails.append(
            f"the design's worst net fanout is now {fanouts.pop()} loads, "
            f"RECORDED says {RECORDED['max_net_fanout']} -- section 2a quotes "
            "it as the reason fanout does not predict this violation"
        )
    return fails


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--liberty", action="append", help="liberty corner(s) to run")
    ap.add_argument("--rc", action="append", help="interconnect corner(s) to run")
    ap.add_argument("--check", action="store_true",
                    help="exit nonzero if the committed DEF stops supporting "
                         "sim/characterization-digital-sta-area-power.md's "
                         "section 2a verdict")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    try:
        corners = run_sta.grid(args.liberty, args.rc)
    except run_sta.StaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    pdk = run_sta.resolve_pdk()
    missing = run_sta.check_environment(pdk)
    if missing:
        for reason in missing:
            print(f"ERROR  {reason}", file=sys.stderr)
        return 3

    result = survey(pdk, corners)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print(result)

    if not args.check:
        return 0
    if len(corners) != len(run_sta.LIBERTY_CORNERS) * len(run_sta.RC_CORNERS):
        print("error: --check needs the full corner grid (drop --liberty/--rc)",
              file=sys.stderr)
        return 2

    fails = check(result)
    if fails:
        print("\nerror: the committed DEF no longer supports "
              "sim/characterization-digital-sta-area-power.md section 2a:",
              file=sys.stderr)
        for line in fails:
            print(f"  - {line}", file=sys.stderr)
        print(
            "\nOne of them is stale. Re-read the measurement, update section 2a "
            "and RECORDED with it -- never the other way round.",
            file=sys.stderr,
        )
        return 1
    print("\nOK: section 2a's max-transition verdict still holds -- the "
          f"violation is confined to {len(RECORDED['violating_nets'])} nets, "
          "no trunk net is involved, and every path through a violating pin "
          "still closes setup.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
