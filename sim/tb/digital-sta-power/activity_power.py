#!/usr/bin/env python3
"""Observed-activity power over the 15-point liberty x interconnect matrix
(#453; DR-0023's per-net switching-activity follow-up).

Reached through ``run_sta.py --activity [MANIFEST]`` (opt-in; the default
uniform-activity flow and its 15 ``digital-sta-power`` records are untouched):

    python3 sim/tb/digital-sta-power/activity.py capture      # traces + manifest
    python3 sim/tb/digital-sta-power/run_sta.py --activity --no-write
    python3 sim/tb/digital-sta-power/run_sta.py --activity               # 15 records
    python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty tt_025C_3v30 --rc nom --no-write

Per corner, two OpenROAD sessions over the committed routed DEF:

1. **uniform baseline** -- exactly the default flow's 1 MHz session
   (`run_sta._tcl`, ``set_power_activity -global`` at ``ACTIVITY``), which also
   extracts and writes the SPEF;
2. **observed** -- reads that same SPEF (identical parasitics, no
   re-extraction), then for every (workload, window) of the manifest runs
   ``read_vcd -scope tb/dut -begin_time B -end_time E <trace>``,
   ``report_activity_annotation`` and ``report_power``.

Both use the 1 MHz clock (DR-0003's ratified raw rate): the traces were
simulated at a 1 us period, so OpenSTA's activity (transitions per second of
trace time) is already at that rate and the like-for-like comparison needs no
frequency scaling.

A trace is rejected -- the corner fails, no record is minted -- when OpenSTA
binds too little of it to the design (``activity.validate_annotation``).
Unannotated pins are counted in every record; they run on OpenSTA's fallback
activity, never treated as measured.

One record per corner (DR-0005's granularity), slug ``digital-sta-activity``,
so ``digital_corner_characterization.py``'s ``*-digital-sta-power-*`` family
and the ratified rollup baseline do not see these records.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TB_DIR))

import activity  # noqa: E402
import run_sta  # noqa: E402
from harness import report  # noqa: E402

SLUG = "digital-sta-activity"
REPO_ROOT = run_sta.REPO_ROOT
SIM_DIR = run_sta.SIM_DIR

_SEGMENT = re.compile(
    r"^ACT_BEGIN (\S+) (\S+)\s*$(.*?)^ACT_END\s*$", re.M | re.S
)


def activity_block(manifest: dict) -> list[str]:
    lines: list[str] = []
    for name, tr in manifest["traces"].items():
        vcd = REPO_ROOT / tr["vcd_path"]
        for win, (lo, hi) in tr["windows_ps"].items():
            lines += [
                f'puts "ACT_BEGIN {name} {win}"',
                f"read_vcd -scope {activity.STA_SCOPE} -begin_time {lo} -end_time {hi} {vcd}",
                "report_activity_annotation",
                "report_power -digits 6",
                'puts "ACT_END"',
            ]
    return lines


def parse_segments(text: str) -> dict[tuple[str, str], dict]:
    out = {}
    for m in _SEGMENT.finditer(text):
        body = m.group(3)
        ann = activity.validate_annotation(
            activity.parse_annotation_report(body), label=f"{m.group(1)}/{m.group(2)}: "
        )
        out[(m.group(1), m.group(2))] = {
            "annotation": ann,
            "power": run_sta._parse_power(body),
        }
    return out


def run_corner(pdk, corner, manifest: dict, work_dir: Path) -> dict:
    """Both sessions for one corner. Raises ``activity.ActivityError`` /
    ``run_sta.StaError``; never returns a partial result."""
    started = time.time()
    spef_path = work_dir / f"{run_sta.HDL_TOPLEVEL}.{corner.liberty}.{corner.rc}.spef"
    tag = f"{corner.liberty}.{corner.rc}"

    uni_tcl = work_dir / f"act-uniform.{tag}.tcl"
    uni_log = work_dir / f"act-uniform.{tag}.log"
    uni_tcl.write_text(run_sta._tcl(
        pdk=pdk, corner=corner, period_ns=run_sta.RATIFIED_RATE_PERIOD_NS,
        spef_path=spef_path, bisect=False))
    uni_text = run_sta._run_openroad(uni_tcl, uni_log)

    obs_tcl = work_dir / f"act-observed.{tag}.tcl"
    obs_log = work_dir / f"act-observed.{tag}.log"
    obs_tcl.write_text(run_sta._tcl(
        pdk=pdk, corner=corner, period_ns=run_sta.RATIFIED_RATE_PERIOD_NS,
        spef_path=spef_path, bisect=False, activity_block=activity_block(manifest)))
    obs_text = run_sta._run_openroad(obs_tcl, obs_log)

    segments = parse_segments(obs_text)
    expected = {(n, w) for n, t in manifest["traces"].items() for w in t["windows_ps"]}
    if set(segments) != expected:
        raise activity.ActivityError(
            f"observed session produced {sorted(set(segments))}, expected {sorted(expected)}"
        )
    return {
        "corner": corner,
        "uniform": run_sta._parse_power(uni_text),
        "observed": segments,
        "spef": run_sta._spef_summary(spef_path),
        "logs": {"uniform": (uni_tcl, uni_log), "observed": (obs_tcl, obs_log)},
        "wall_s": time.time() - started,
    }


# --------------------------------------------------------------------------- #
# Records
# --------------------------------------------------------------------------- #


def result_values(res: dict) -> dict[str, float]:
    """Flat ``key -> value`` for the record's machine-readable bullets.

    Keys: ``uniform_<term>_w`` and
    ``obs_<workload>_<window>_<term>_w`` with ``term`` in total / internal /
    switching / leakage (and ``clock``/``sequential``/``combinational`` group
    totals), workload and window names with ``-`` -> ``_``.
    """
    vdd = res["corner"].vdd
    out: dict[str, float] = {}

    def put(prefix: str, power: dict) -> None:
        tot = power["total"]
        out[f"{prefix}_total_w"] = tot["total_w"]
        out[f"{prefix}_internal_w"] = tot["internal_w"]
        out[f"{prefix}_switching_w"] = tot["switching_w"]
        out[f"{prefix}_leakage_w"] = tot["leakage_w"]
        for grp in ("clock", "sequential", "combinational"):
            out[f"{prefix}_{grp}_w"] = power[grp]["total_w"]
        out[f"{prefix}_total_a"] = tot["total_w"] / vdd

    put("uniform", res["uniform"])
    for (name, win), seg in sorted(res["observed"].items()):
        key = f"obs_{name.replace('-', '_')}_{win}"
        put(key, seg["power"])
        ann = seg["annotation"]
        out[f"{key}_annotated_pins"] = float(ann["vcd"])
        out[f"{key}_unannotated_pins"] = float(ann["unannotated"])
    return out


def _fmt_w(v: float) -> str:
    return f"{v * 1e6:9.2f}"


def _table(res: dict, manifest: dict) -> str:
    uni = res["uniform"]["total"]
    rows = [
        "| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | "
        "vs uniform | annotated / unannotated pins |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
        f"| uniform ({run_sta.ACTIVITY} tr/net/cycle) | -- | -- | {_fmt_w(uni['internal_w'])} | "
        f"{_fmt_w(uni['switching_w'])} | {_fmt_w(uni['leakage_w'])} | {_fmt_w(uni['total_w'])} | "
        "1.000 | n/a (global) |",
    ]
    for (name, win), seg in sorted(res["observed"].items()):
        t = seg["power"]["total"]
        cycles = (manifest["traces"][name]["windows_cycles"][win][1]
                  - manifest["traces"][name]["windows_cycles"][win][0])
        a = seg["annotation"]
        rows.append(
            f"| {name} | {win} | {cycles} | {_fmt_w(t['internal_w'])} | {_fmt_w(t['switching_w'])} | "
            f"{_fmt_w(t['leakage_w'])} | {_fmt_w(t['total_w'])} | {t['total_w'] / uni['total_w']:.3f} | "
            f"{a['vcd']} / {a['unannotated']} |"
        )
    return "\n".join(rows)


def _frontmatter(stem: str, res: dict, manifest: dict, pdk, git: dict,
                 raw_files, openroad: str, lib_conditions: dict) -> str:
    c = res["corner"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lib = run_sta.liberty_path(pdk, c.liberty)
    paths = run_sta.deck_paths(pdk)
    rcx = run_sta.rcx_rules_path(pdk, c.rc)
    ident = manifest["identities"]
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
        f"  path: sim/tb/{run_sta.SLUG}/activity_power.py",
        f"  sha: {report.blob_sha(REPO_ROOT, TB_DIR / 'activity_power.py')}",
        "netlist:",
        "  path: layout/digital/trng_top.def",
        f"  sha: {report.blob_sha(REPO_ROOT, run_sta.DEF_PATH)}",
        "  note: >-",
        "    The committed routed DEF re-timed at this corner; the observed",
        "    activity comes from simulating the matching as-built gate-level",
        f"    netlist layout/digital/trng_top.pnr.v (sha {ident['netlist']['git_blob_sha']}).",
        f"repo_commit: {report.repo_commit_field(git)}",
        "",
        f"pdk: {pdk.variant} @ {pdk.version}",
        "pdk.models:",
        f"  - {lib.name} (liberty corner {c.liberty}, sha256:{report.sha256_file(lib)})",
        f"  - {paths['tech_lef'].name} (tech LEF, {run_sta.TECH_LEF_CORNER} deck, "
        f"sha256:{report.sha256_file(paths['tech_lef'])})",
        f"  - {paths['cell_lef'].name} (cell LEF, sha256:{report.sha256_file(paths['cell_lef'])})",
        f"  - {rcx.name} (OpenRCX interconnect corner {c.rc}, sha256:{report.sha256_file(rcx)})",
    ]
    for m in ident["cell_models"]:
        lines.append(f"  - {m['path']} (gate-simulation cell model, sha256:{m['sha256']})")
    lines += [
        "",
        "tool:",
        '  ngspice: "n/a (gate-level record)"',
        f'  openroad: "{openroad}"',
        f'  simulator: "{ident["simulator"]} {ident["simulator_flags"]}"',
        "",
        "corner:",
        f"  process: {c.process}",
        f"  voltage: {run_sta._voltage_label(c.vdd)}",
        f"  temperature: {c.temp_c:g}",
        f"  liberty: {run_sta.CELL_LIBRARY}__{c.liberty}",
        f"  interconnect: {c.rc} (OpenRCX rule deck)",
    ]
    if lib_conditions:
        stated = ", ".join(f"{k} {v:g}" for k, v in sorted(lib_conditions.items()))
        lines.append(f"  liberty_operating_conditions: {stated} (read from the deck)")
    lines += [
        "",
        "analysis:",
        "  type: sta+power with per-pin switching activity annotated from a post-route "
        "gate-level simulation (OpenSTA read_vcd), against a like-for-like uniform baseline",
        "  tstop: n/a (static power analysis over recorded activity)",
        "  tstep: n/a",
        "  tmax: n/a",
        "  noise_params: n/a",
        f"  runs: 2 (uniform-baseline session + observed-activity session over {len(manifest['traces'])} "
        "workloads x 3 capture windows)",
        f"  clock: {run_sta.CLOCK_PORT}, {run_sta.RATIFIED_RATE_PERIOD_NS:g} ns "
        f"({1e3 / run_sta.RATIFIED_RATE_PERIOD_NS:g} MHz) -- DR-0003's ratified raw rate; "
        "traces simulated at the same period so no rate scaling is applied",
        "  clock_model: propagated (CTS tree in the DEF); clock running in every window",
        f"  uniform_baseline: {run_sta.ACTIVITY} transitions/net/cycle, duty {run_sta.ACTIVITY_DUTY} "
        "(set_power_activity -global), same session shape as the default flow's 1 MHz point",
        "  activity_scope: tb/dut (read_vcd -scope)",
        f"seeds: base {manifest['traces'][next(iter(manifest['traces']))]['base_seed']}; per-workload "
        + ", ".join(f"{n} {t['seed']}" for n, t in manifest["traces"].items()),
        "",
        "parasitics:",
        f"  spef_sha256: {res['spef']['sha256']}",
        f"  spef_bytes: {res['spef']['bytes']}",
        "  note: >-",
        "    Both sessions read this one SPEF; it is regenerated, not committed.",
        "",
        "activity:",
        "  note: >-",
        "    Zero-delay gate simulation of the as-built post-route netlist",
        "    (iverilog -gno-specify); synthetic stimulus with declared seeds -- the",
        "    raw bits make no entropy claim. Not a silicon current measurement and",
        "    not a worst case.",
        f"  simulator_x_z: {ident['x_z_handling']}",
        f"  clock_activity: {ident['clock_activity']}",
        f"  testbench_sha: {ident['testbench']['git_blob_sha']}",
        f"  workloads_module_sha: {ident['workloads_module_git_blob_sha']}",
        "  traces:",
    ]
    for name, t in manifest["traces"].items():
        v = t["validation"]
        lines += [
            f"    - workload: {name}",
            f"      vcd_sha256: {t['vcd_sha256']}",
            f"      vcd_bytes: {t['vcd_bytes']}",
            f"      stimulus_sha256: {t['stimulus_sha256']}",
            f"      cycles: {t['cycles']}",
            f"      windows_cycles: {json.dumps(t['windows_cycles'])}",
            f"      instances_matched: {v['instances_matched']}/{v['netlist_instances']}",
            f"      xz_events: {v['xz_events']}",
            f"      same_timestamp_extra_changes: {v['same_timestamp_extra_changes']}",
        ]
    lines += ["", "raw:", f"  path: sim/records/raw/{stem}/", "  files:"]
    for name, digest in raw_files:
        lines.append(f"    - {name}  sha256:{digest}")
    lines.append(f"wall_time: {res['wall_s']:.1f}s")
    lines.append("---")
    return "\n".join(lines)


def _body(res: dict, manifest: dict) -> str:
    c = res["corner"]
    values = result_values(res)
    bullets = "\n".join(f"- `{k}`: {v:.6e}" for k, v in values.items())
    return f"""
## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

{_table(res, manifest)}

{bullets}

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty {c.liberty} --rc {c.rc} --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** ({c.liberty}, interconnect `{c.rc}`).
- **Observed activity is from a zero-delay simulation of five declared
  synthetic workloads.** Not a supply-current measurement, not silicon, and
  no workload here is claimed to be the worst case. Glitching beyond
  same-timestamp delta activity is not modelled.
- **Leakage is state-dependent in the library** (`when` conditions), so the
  leakage column moves a little between workloads. A *stopped* clock is not
  simulated: its idle power is leakage only, and this record's leakage
  column is the nearest evidence, not a measurement of that state. The
  `disabled-clock-running` workload is a disabled block with a **running**
  clock, which still pays the clock tree.
- **Clock-network activity** follows the propagated clock at the stated
  period (the VCD `clk` toggle count is validated against the window length).
- **Unannotated pins** (last column) run on OpenSTA's fallback activity and
  are never presented as measured; the trace is rejected outright below
  {activity.MIN_ANNOTATED_FRACTION:.0%} annotation.
- Uniform baseline: {run_sta.ACTIVITY} transitions/net/cycle at duty
  {run_sta.ACTIVITY_DUTY}, the default flow's model assumption.
- No IR drop, no I/O timing, no foundry-signed extraction: see
  `sim/tb/digital-sta-power/README.md`.

---

Written by `sim/tb/{run_sta.SLUG}/activity_power.py`. Append-only: never edit
or delete this file -- a re-run or correction mints a new record and points
back here via `supersedes` (see `sim/README.md`).
"""


def write_record(res: dict, manifest: dict, pdk, git: dict, openroad: str,
                 records_dir: Path) -> Path:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def render(stem: str, raw_dir: Path) -> str:
        names = []
        for tag, (tcl, log) in res["logs"].items():
            shutil.copyfile(tcl, raw_dir / f"{tag}.tcl")
            shutil.copyfile(log, raw_dir / f"{tag}.log")
            names += [f"{tag}.tcl", f"{tag}.log"]
        (raw_dir / "activity-manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        names.append("activity-manifest.json")
        raw_files = [(n, report.sha256_file(raw_dir / n)) for n in names]
        lib_conditions = run_sta.liberty_operating_conditions(
            run_sta.liberty_path(pdk, res["corner"].liberty))
        return (_frontmatter(stem, res, manifest, pdk, git, raw_files, openroad, lib_conditions)
                + "\n" + _body(res, manifest))

    return report.finalize_record(records_dir, date, SLUG, render)


def main(corners, manifest_path: Path, *, no_write: bool) -> int:
    pdk = run_sta.resolve_pdk()
    missing = run_sta.check_environment(pdk)
    if missing:
        for reason in missing:
            print(f"ERROR  {reason}", file=sys.stderr)
        return 3
    try:
        manifest = activity.load_manifest(manifest_path)
    except (activity.ActivityError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"REJECTED activity manifest {manifest_path}: {exc}", file=sys.stderr)
        return 1
    openroad = run_sta.openroad_version() or "unknown"
    run_sta.WORK_DIR.mkdir(parents=True, exist_ok=True)
    git = report.git_provenance(REPO_ROOT)
    records_dir = SIM_DIR / "records"
    for c in corners:
        try:
            res = run_corner(pdk, c, manifest, run_sta.WORK_DIR)
        except (activity.ActivityError, run_sta.StaError) as exc:
            print(f"REJECTED {c.label}: {exc}", file=sys.stderr)
            return 1
        uni = res["uniform"]["total"]["total_w"]
        steady = {n: s["power"]["total"]["total_w"] for (n, w), s in res["observed"].items()
                  if w == "steady"}
        print(f"{c.label:32s} uniform {uni * 1e6:8.2f} uW  steady: "
              + "  ".join(f"{n.split('-')[0]} {v * 1e6:7.2f}" for n, v in steady.items())
              + f"  [{res['wall_s']:.1f}s]")
        if not no_write:
            path = write_record(res, manifest, pdk, git, openroad, records_dir)
            print(f"  wrote {path.relative_to(REPO_ROOT)}")
    return 0


# --------------------------------------------------------------------------- #
# Negative controls
# --------------------------------------------------------------------------- #


def negative_controls(manifest_path: Path) -> int:
    """Prove the validation can fail, on real data.

    Each control mutates a real, validated trace (or the scope handed to
    OpenSTA) and must be REJECTED; a control that is accepted means the
    check it controls for is not in the loop. Exit 0 only if every control
    is rejected. Uses one corner (tt / nom), nothing is minted.
    """
    manifest = activity.load_manifest(manifest_path)
    name = next(iter(manifest["traces"]))
    tr = manifest["traces"][name]
    src = REPO_ROOT / tr["vcd_path"]
    work = run_sta.WORK_DIR / "negative-controls"
    work.mkdir(parents=True, exist_ok=True)
    insts = activity.netlist_instances()
    windows = {k: tuple(v) for k, v in tr["windows_cycles"].items()}
    wticks = activity.windows_to_ticks(windows, tr["clock_period_ns"])
    text = src.read_text()

    def python_side(label: str, mutated: str) -> bool:
        p = work / f"{label}.vcd"
        p.write_text(mutated)
        try:
            s = activity.summarize_vcd(p, wticks)
            activity.validate_trace(s, netlist_insts=insts, windows=windows,
                                    period_ns=tr["clock_period_ns"], total_cycles=tr["cycles"])
        except activity.ActivityError as exc:
            print(f"  rejected  {label}: {exc}")
            return True
        print(f"  ACCEPTED  {label}  <-- the check is not in the loop")
        return False

    header_end = text.index("$enddefinitions")
    ok = True
    ok &= python_side("empty-waveform", text[: header_end] + "$enddefinitions $end\n")
    ok &= python_side("wrong-dut-scope", text.replace("$scope module dut $end", "$scope module wrong $end", 1))
    first_inst = sorted(insts)[0]
    ok &= python_side("mismatched-netlist",
                      text.replace(f"$scope module {first_inst} $end",
                                   "$scope module not_in_this_netlist $end", 1))

    # OpenSTA side: a wrong scope binds nothing.
    pdk = run_sta.resolve_pdk()
    corner = run_sta.Corner(liberty="tt_025C_3v30", rc="nom")
    work_dir = run_sta.WORK_DIR
    work_dir.mkdir(parents=True, exist_ok=True)
    spef = work_dir / f"{run_sta.HDL_TOPLEVEL}.{corner.liberty}.{corner.rc}.spef"
    if not spef.is_file():
        uni = work_dir / "negctl-uniform.tcl"
        uni.write_text(run_sta._tcl(pdk=pdk, corner=corner,
                                    period_ns=run_sta.RATIFIED_RATE_PERIOD_NS,
                                    spef_path=spef, bisect=False))
        run_sta._run_openroad(uni, work_dir / "negctl-uniform.log")
    block = [
        'puts "ACT_BEGIN wrong-scope steady"',
        f"read_vcd -scope tb/not_the_dut {src}",
        "report_activity_annotation",
        "report_power -digits 6",
        'puts "ACT_END"',
    ]
    tcl = work_dir / "negctl-wrong-scope.tcl"
    tcl.write_text(run_sta._tcl(pdk=pdk, corner=corner,
                                period_ns=run_sta.RATIFIED_RATE_PERIOD_NS,
                                spef_path=spef, bisect=False, activity_block=block))
    out = run_sta._run_openroad(tcl, work_dir / "negctl-wrong-scope.log")
    try:
        parse_segments(out)
        print("  ACCEPTED  wrong-scope-in-opensta  <-- the check is not in the loop")
        ok = False
    except activity.ActivityError as exc:
        print(f"  rejected  wrong-scope-in-opensta: {exc}")
    return 0 if ok else 1


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="observed-activity power helpers")
    ap.add_argument("command", choices=("negative-controls",))
    ap.add_argument("--manifest", type=Path,
                    default=run_sta.WORK_DIR.parent / "digital-sta-activity" / "manifest.json")
    ns = ap.parse_args()
    raise SystemExit(negative_controls(ns.manifest))
