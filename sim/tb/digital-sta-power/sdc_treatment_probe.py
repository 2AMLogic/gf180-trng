#!/usr/bin/env python3
"""Why `run_sta.py` states the #233 interface load as `set_input_transition`
and not as `set_load` -- as a runnable comparison rather than an assertion.

Issue #233 asked for the six `digital`-facing inter-region trunks' Metal4
capacitance to be fed into the post-route STA, and expected `set_load` on the
four `combiner_sampler`-driven ports. `run_sta.py` uses
`set_input_transition` on all six instead. That is a modeling decision, and
this repository does not record modeling decisions as assertions -- this
probe is the testbench behind it. Two questions, one OpenROAD session each:

**1. Does `set_load` do anything at all on these ports?** (`--compare`, the
default.) One corner, one DEF, five otherwise identical sessions: no
interface constraint; `set_load` at the trunks' as-built capacitance;
`set_load` at an absurd 10 pF; the derived `set_input_transition`; and that
transition overstated 10x. All six ports are `DIRECTION INPUT` on `trng_top`
with no driver inside this netlist, so the expectation is that both
`set_load` sessions are *bit-identical* to the unconstrained one -- there is
no driver arc at the port for a load to attach to -- while
`set_input_transition` moves the port's own slew and the slew at the pins it
drives.

**2. Which slew domain are `set_input_transition` and `max_transition` in?**
(`--domain`.) The decks declare 30/70 % thresholds *and*
`slew_derate_from_library 0.5`, which is a factor of two between "the edge a
scope would measure" and "the number in the tables". `run_sta.py`'s
`SlewConvention` states the trunk RC in the table domain; this walks a
single port's `set_input_transition` across the library's `max_transition`
and reports where OpenSTA's own max-slew check flips, which pins it names,
and by how much -- settling the domain against the tool instead of against a
reading of the Liberty spec.

`--check` runs both and exits non-zero if either stops supporting the
decision `run_sta.py` documents. It needs `openroad` on `PATH` and the
gf180mcu PDK, like the sweep itself; with neither it exits 3 and says so, so
a PDK-less CI run can skip it deliberately rather than silently.
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
WORK_DIR = REPO_ROOT / "layout" / ".work" / "digital-sta-sdc-probe"

#: The port the domain walk uses. Any of the six would do; this one has the
#: longest trunk, so it is also the one whose stated transition is largest.
DOMAIN_WALK_PORT = "raw_bit"

#: `report_slews -digits`. The trunks' own stated transitions are a few
#: picoseconds, so OpenSTA's 2-digit default prints most of them as `0.00`
#: and a comparison against the unconstrained session would read as "no
#: change" purely from rounding.
SLEW_DIGITS = 9

#: How much the wire between a port and its load pins may degrade a stated
#: edge further, in ns, before the domain walk stops recognising the
#: comparison as 1:1. The SPEF-annotated trunk inside `digital` adds a real
#: but small amount (0.03 ns at `ss_125C_3v00`); a `slew_derate_from_library`
#: of 0.5 being applied to the stated value instead would show up as a factor
#: of two, far outside this.
DOMAIN_WALK_TOLERANCE_NS = 0.5

_FLOAT = r"[-\d.eE+]+"
#: `report_slews`' own one-line-per-object format: `<name> ^ min:max v min:max`.
_SLEW_ROW = re.compile(
    rf"^(\S+)\s+\^\s+({_FLOAT}):({_FLOAT})\s+v\s+({_FLOAT}):({_FLOAT})\s*$", re.M
)
_SLEW_BLOCK = re.compile(r"PROBE_SLEWS_BEGIN\n(.*?)\nPROBE_SLEWS_END", re.S)
_PROBE = re.compile(r"^PROBE\s+(\S+)\s+(\S+)\s*$", re.M)
_POWER_TOTAL = re.compile(
    rf"^Total\s+({_FLOAT})\s+({_FLOAT})\s+({_FLOAT})\s+({_FLOAT})", re.M
)


def _deck(pdk, corner: run_sta.Corner, body: list[str], *, slews_for: list[str]) -> str:
    """One session: read the committed DEF at `corner`, apply `body`, report."""
    paths = run_sta.deck_paths(pdk)
    lines = [
        f"read_liberty {run_sta.liberty_path(pdk, corner.liberty)}",
        f"read_lef {paths['tech_lef']}",
        f"read_lef {paths['cell_lef']}",
        f"read_def {run_sta.DEF_PATH}",
        f"create_clock -name {run_sta.CLOCK_PORT} "
        f"-period {run_sta.CONSTRAINT_PERIOD_NS} [get_ports {run_sta.CLOCK_PORT}]",
        *body,
        "define_process_corner -ext_model_index 0 X",
        "extract_parasitics -ext_model_file "
        f"{run_sta.rcx_rules_path(pdk, corner.rc)}",
        f"write_spef {WORK_DIR / 'probe.spef'}",
        f"read_spef {WORK_DIR / 'probe.spef'}",
        "set_propagated_clock [all_clocks]",
        f"set_power_activity -global -activity {run_sta.ACTIVITY} "
        f"-duty {run_sta.ACTIVITY_DUTY}",
        'puts "PROBE setup_slack_s [sta::worst_slack_cmd max]"',
        'puts "PROBE hold_slack_s [sta::worst_slack_cmd min]"',
        'puts "PROBE max_slew_limit [sta::max_slew_check_limit]"',
        'puts "PROBE max_slew_slack [sta::max_slew_check_slack]"',
        'puts "PROBE max_slew_violations [sta::max_slew_violation_count]"',
    ]
    lines.append('puts "PROBE_SLEWS_BEGIN"')
    for port in slews_for:
        # The port's own slew, then every pin on its net: a slew stated at an
        # input port reaches the load pins undegraded, and it is the load
        # pins OpenSTA checks against `max_transition`. `report_slews` prints
        # one line per object, keyed by the object's own name.
        lines += [
            f"foreach _o [concat [get_ports {{{port}}}] "
            f"[get_pins -of_objects [get_nets {{{port}}}]]] {{",
            f"  report_slews -digits {SLEW_DIGITS} $_o",
            "}",
        ]
    lines += [
        'puts "PROBE_SLEWS_END"',
        'puts "PROBE_VIOLATORS_BEGIN x"',
        "report_check_types -max_slew -violators -verbose",
        'puts "PROBE_VIOLATORS_END x"',
        "report_power -digits 8",
    ]
    return "\n".join(lines) + "\n"


def _run(pdk, corner: run_sta.Corner, name: str, body: list[str],
         slews_for: list[str]) -> dict:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    script = WORK_DIR / f"{name}.tcl"
    log = WORK_DIR / f"{name}.log"
    script.write_text(_deck(pdk, corner, body, slews_for=slews_for))
    done = subprocess.run(
        ["openroad", "-no_init", "-exit", str(script)],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
        timeout=run_sta.OPENROAD_TIMEOUT_S, check=False,
    )
    text = done.stdout + ("\n" + done.stderr if done.stderr.strip() else "")
    log.write_text(text)
    if done.returncode != 0:
        raise run_sta.StaError(f"openroad exited {done.returncode}; see {log}")
    scalars = {m.group(1): float(m.group(2)) for m in _PROBE.finditer(text)}
    power = _POWER_TOTAL.search(text)
    if power is None:
        raise run_sta.StaError(f"no report_power total in {log}")
    block = _SLEW_BLOCK.search(text)
    if block is None:
        raise run_sta.StaError(f"no report_slews block in {log}")
    slews = {
        m.group(1): (float(m.group(2)), float(m.group(3)),
                     float(m.group(4)), float(m.group(5)))
        for m in _SLEW_ROW.finditer(block.group(1))
    }
    if not slews:
        raise run_sta.StaError(f"report_slews block in {log} parsed to nothing")
    violators = sorted(run_sta._parse_max_slew_violators(
        text.replace("PROBE_VIOLATORS_BEGIN x", "STA_MAX_SLEW_VIOLATORS_BEGIN")
            .replace("PROBE_VIOLATORS_END x", "STA_MAX_SLEW_VIOLATORS_END")
    ))
    return {
        "name": name,
        **scalars,
        "p_internal_w": float(power.group(1)),
        "p_switching_w": float(power.group(2)),
        "p_leakage_w": float(power.group(3)),
        "p_total_w": float(power.group(4)),
        "slews": slews,
        "violators": violators,
        "log": str(log.relative_to(REPO_ROOT)),
    }


def _comparable(run: dict) -> tuple:
    """The figures a no-op treatment must leave untouched, exactly."""
    return (
        run["setup_slack_s"], run["hold_slack_s"], run["max_slew_slack"],
        run["max_slew_violations"], run["p_internal_w"], run["p_switching_w"],
        run["p_leakage_w"], run["p_total_w"], tuple(sorted(run["slews"].items())),
    )


def compare(pdk, corner: run_sta.Corner) -> dict:
    """`set_load` vs `set_input_transition` vs nothing, same corner, same DEF."""
    trunks = run_sta.digital_facing_trunks()
    slew = run_sta.liberty_slew_convention(run_sta.liberty_path(pdk, corner.liberty))
    ports = [t.def_pin for t in trunks]
    variants = {
        "baseline": [],
        "set_load_asbuilt": [
            f"set_load {t.cap_fF / 1000.0:.6f} [get_ports {{{t.def_pin}}}]"
            for t in trunks
        ],
        "set_load_10pf": [
            f"set_load 10.0 [get_ports {{{t.def_pin}}}]" for t in trunks
        ],
        "set_input_transition": [
            f"set_input_transition {t.transition_ns(slew):.6f} "
            f"[get_ports {{{t.def_pin}}}]"
            for t in trunks
        ],
        "set_input_transition_10x": [
            f"set_input_transition {t.transition_ns(slew) * 10:.6f} "
            f"[get_ports {{{t.def_pin}}}]"
            for t in trunks
        ],
    }
    runs = {
        name: _run(pdk, corner, f"compare-{name}", body, ports)
        for name, body in variants.items()
    }
    base = _comparable(runs["baseline"])
    return {
        "corner": corner.label,
        "slew_convention": {
            "lower_pct": slew.lower_pct, "upper_pct": slew.upper_pct,
            "derate": slew.derate, "rc_factor": slew.rc_factor,
        },
        "ports": {
            t.def_pin: {
                "net": t.net, "trunk_length_um": t.trunk_length_um,
                "res_ohm": t.res_ohm, "cap_fF": t.cap_fF,
                "transition_ns": t.transition_ns(slew),
            }
            for t in trunks
        },
        "runs": runs,
        "set_load_is_a_noop": all(
            _comparable(runs[name]) == base
            for name in ("set_load_asbuilt", "set_load_10pf")
        ),
        "transition_moves_port_slew": all(
            max(runs["set_input_transition"]["slews"][p])
            > max(runs["baseline"]["slews"][p])
            for p in ports
        ),
        "transition_is_monotonic": all(
            all(
                later >= earlier
                for later, earlier in zip(
                    runs["set_input_transition_10x"]["slews"][k],
                    runs["set_input_transition"]["slews"][k],
                )
            )
            for k in runs["set_input_transition"]["slews"]
        ),
    }


def domain_walk(pdk, corner: run_sta.Corner) -> dict:
    """Walk one port's stated transition across the library's own
    `max_transition` and report where OpenSTA's max-slew check flips."""
    probe = _run(pdk, corner, "domain-limit", [], [DOMAIN_WALK_PORT])
    limit = probe["max_slew_limit"]
    steps = {
        "just_under_limit": limit - 0.1,
        "just_over_limit": limit + 0.1,
        "twice_the_limit": 2 * limit + 0.1,
    }
    runs = {}
    for name, value in steps.items():
        runs[name] = _run(
            pdk, corner, f"domain-{name}",
            [f"set_input_transition {value:.6f} [get_ports {{{DOMAIN_WALK_PORT}}}]"],
            [DOMAIN_WALK_PORT],
        )
        runs[name]["stated_transition_ns"] = value
    under, over = runs["just_under_limit"], runs["just_over_limit"]
    return {
        "corner": corner.label,
        "port": DOMAIN_WALK_PORT,
        "max_transition_limit_ns": limit,
        "baseline_violations": probe["max_slew_violations"],
        "runs": runs,
        # The claim under test: the number `set_input_transition` states is
        # compared against `max_transition` 1:1, with no slew_derate applied.
        # A stated value 0.1 ns under the limit stays clean and one 0.1 ns
        # over it violates -- so the threshold is the limit itself -- and the
        # reported shortfall tracks `stated - limit` rather than half of it,
        # which is what a derate-applied reading would produce.
        "compared_one_to_one": (
            under["max_slew_violations"] == probe["max_slew_violations"]
            and under["max_slew_slack"] >= 0
            and over["max_slew_violations"] > probe["max_slew_violations"]
            and all(
                -DOMAIN_WALK_TOLERANCE_NS
                <= run["max_slew_slack"] + (run["stated_transition_ns"] - limit)
                <= 0
                for run in (over, runs["twice_the_limit"])
            )
        ),
        # The port that stated the slew is never itself a violator -- the
        # check lands on the load pins. This is why run_sta.py attributes a
        # violation by net rather than by port name.
        "violation_lands_on_load_pins_not_the_port": (
            DOMAIN_WALK_PORT not in over["violators"] and bool(over["violators"])
        ),
    }


def _print_compare(result: dict) -> None:
    conv = result["slew_convention"]
    print(f"corner {result['corner']}   slew convention "
          f"{conv['lower_pct']:g}-{conv['upper_pct']:g}% / derate "
          f"{conv['derate']:g} => {conv['rc_factor']:.4f} * R * C")
    print(f"{'port':14s} {'trunk um':>9s} {'R ohm':>8s} {'C fF':>8s} "
          f"{'stated ns':>10s}")
    for port, info in result["ports"].items():
        print(f"{port:14s} {info['trunk_length_um']:9.2f} {info['res_ohm']:8.2f} "
              f"{info['cap_fF']:8.3f} {info['transition_ns']:10.6f}")
    print()
    print(f"{'variant':26s} {'setup ns':>12s} {'hold ns':>10s} "
          f"{'P total W':>14s} {'slew viol':>10s} {'worst port slew ns':>19s}")
    for name, run in result["runs"].items():
        port_slews = [
            max(run["slews"][p]) for p in result["ports"] if p in run["slews"]
        ]
        print(f"{name:26s} {run['setup_slack_s'] * 1e9:12.6f} "
              f"{run['hold_slack_s'] * 1e9:10.6f} {run['p_total_w']:14.8e} "
              f"{run['max_slew_violations']:10.0f} {max(port_slews):19.6f}")
    print()
    print(f"set_load is a no-op (bit-identical to baseline): "
          f"{result['set_load_is_a_noop']}")
    print(f"set_input_transition moves every port's own slew: "
          f"{result['transition_moves_port_slew']}")
    print(f"10x overstatement never improves a slew: "
          f"{result['transition_is_monotonic']}")


def _print_domain(result: dict) -> None:
    print(f"corner {result['corner']}   port {result['port']}   library "
          f"max_transition {result['max_transition_limit_ns']:g} ns   "
          f"baseline violations {result['baseline_violations']:.0f}")
    print(f"{'stated transition':>18s} {'violations':>11s} {'max slew slack':>15s} "
          f"{'port itself a violator':>24s}")
    for name, run in result["runs"].items():
        print(f"{run['stated_transition_ns']:18.3f} "
              f"{run['max_slew_violations']:11.0f} {run['max_slew_slack']:15.4f} "
              f"{str(result['port'] in run['violators']):>24s}")
    print()
    print(f"stated slew compared against max_transition 1:1 (no derate): "
          f"{result['compared_one_to_one']}")
    print(f"violation lands on load pins, not the stating port: "
          f"{result['violation_lands_on_load_pins_not_the_port']}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--liberty", default=run_sta.LIBERTY_CORNERS[0],
                    help="liberty corner (default: %(default)s)")
    ap.add_argument("--rc", default=run_sta.RC_CORNERS[0],
                    help="OpenRCX interconnect corner (default: %(default)s)")
    ap.add_argument("--compare", action="store_true",
                    help="set_load vs set_input_transition (default)")
    ap.add_argument("--domain", action="store_true",
                    help="walk set_input_transition across max_transition")
    ap.add_argument("--check", action="store_true",
                    help="run both and fail if either stops supporting run_sta.py's "
                         "documented treatment")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    pdk = run_sta.resolve_pdk()
    missing = run_sta.check_environment(pdk)
    if missing:
        for reason in missing:
            print(f"ERROR  {reason}", file=sys.stderr)
        return 3

    corner = run_sta.Corner(liberty=args.liberty, rc=args.rc)
    do_compare = args.compare or args.check or not (args.compare or args.domain)
    do_domain = args.domain or args.check

    out: dict = {}
    if do_compare:
        out["compare"] = compare(pdk, corner)
    if do_domain:
        out["domain"] = domain_walk(pdk, corner)

    if args.json:
        print(json.dumps(out, indent=2, default=str))
    else:
        if "compare" in out:
            _print_compare(out["compare"])
        if "domain" in out:
            print()
            _print_domain(out["domain"])

    if not args.check:
        return 0

    failures = []
    c, d = out["compare"], out["domain"]
    if not c["set_load_is_a_noop"]:
        failures.append(
            "set_load on these input ports is no longer a no-op -- run_sta.py's "
            "stated reason for not using it needs revisiting"
        )
    if not c["transition_moves_port_slew"]:
        failures.append(
            "set_input_transition no longer moves the six ports' own slew -- the "
            "interface load would be stating nothing"
        )
    if not c["transition_is_monotonic"]:
        failures.append("a 10x larger stated transition improved a slew somewhere")
    if not d["compared_one_to_one"]:
        failures.append(
            "set_input_transition is no longer compared against max_transition "
            "1:1 -- SlewConvention's derate handling needs revisiting"
        )
    if not d["violation_lands_on_load_pins_not_the_port"]:
        failures.append(
            "a max-slew violation now names the stating port itself -- "
            "interface_load_max_slew_violations' by-net attribution needs "
            "revisiting"
        )
    for line in failures:
        print(f"FAIL  {line}", file=sys.stderr)
    if failures:
        return 1
    print("\nOK: every finding run_sta.py's #233 treatment rests on still holds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
