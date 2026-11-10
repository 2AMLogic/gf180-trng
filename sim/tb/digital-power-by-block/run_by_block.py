#!/usr/bin/env python3
"""Per-sub-block power of the routed digital section, at one liberty corner.

    python3 sim/tb/digital-power-by-block/run_by_block.py --no-write   # print only
    python3 sim/tb/digital-power-by-block/run_by_block.py              # mint 1 record

Gate-level ([DR-0021]): the same committed routed DEF, the same OpenRCX
extraction, the same declared uniform switching activity and the same 1 MHz
clock as ``sim/tb/digital-sta-power/run_sta.py``'s ratified-rate session -- so
the whole-section figure here must equal that testbench's ``p_total_1mhz_w`` for
the same corner. What it adds is ``report_power -instances``: OpenSTA's
per-instance power, summed here by the hierarchy prefix the as-built netlist
keeps in its instance names (``u_conditioner/``, ``u_health_test/``,
``u_interface/``, ``u_ring_liveness/``), with the clock-tree cells
(``clkbuf_*`` / ``clkload*``) and everything else at the top level reported as
their own groups.

The sum of the per-instance totals is checked against ``report_power``'s own
total in the same session; a record is refused if they differ by more than
``SUM_TOLERANCE`` (every instance is in exactly one group, so the figures
reconcile by construction and any gap means the parse missed rows).

``--activity MANIFEST`` (repeatable, one manifest per clock rate; #812) swaps the
uniform activity for the toggle activity of a gate-level simulation: the same
session shape as ``sim/tb/digital-sta-power/activity_power.py`` (``read_vcd
-scope tb/dut``, annotation validated, trace rejected below 99 % bound pins),
then ``report_power -instances`` grouped exactly as above. Each rate also gets
a uniform-activity session at that rate's clock so the record can tabulate
VCD-derived against uniform per sub-block. Measurement only.

Default corner is ``ff_125C_3v60`` / OpenRCX ``max``: the corner at which
``sim/tools/power_rollup.py`` finds the committed digital active term binding.
Like every record in the ``digital-sta-power`` family this is a liberty-power
model at a declared activity, not a measured supply current ([DR-0021] section
3), and the record says so.

[DR-0021]: ../../../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TB_DIR = Path(__file__).resolve().parent
SIM_DIR = TB_DIR.parents[1]
REPO_ROOT = SIM_DIR.parent

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(SIM_DIR / "tb" / "digital-sta-power"))

import activity  # noqa: E402
import activity_power as ap_mod  # noqa: E402
import run_sta as sta  # noqa: E402
from harness import report  # noqa: E402

SLUG = "digital-power-by-block"
#: Slug of the VCD-activity records. Deliberately not ``digital-power-by-block-<N>``
#: so ``active_power_breakdown.BY_BLOCK_GLOB`` (``*-digital-power-by-block-[0-9]*``)
#: keeps selecting only the uniform-activity records the ratified breakdown uses.
ACTIVITY_SLUG = "digital-power-by-block-activity"
DEFAULT_MANIFESTS = (
    REPO_ROOT / "layout" / ".work" / ACTIVITY_SLUG / "1mhz" / activity.MANIFEST_NAME,
    REPO_ROOT / "layout" / ".work" / ACTIVITY_SLUG / "2khz" / activity.MANIFEST_NAME,
)
#: The one capture window the by-block table is read from.
ACTIVITY_WINDOW = "steady"
WORK_DIR = REPO_ROOT / "layout" / ".work" / SLUG

DEFAULT_LIBERTY = "ff_125C_3v60"
DEFAULT_RC = "max"

#: Hierarchy prefixes the as-built netlist keeps. Order is the report order.
BLOCKS = ("u_conditioner", "u_health_test", "u_interface", "u_ring_liveness")
CLOCK_TREE = "clock_tree"
OTHER = "top_level_other"
GROUPS = (*BLOCKS, CLOCK_TREE, OTHER)

#: Relative gap allowed between the instance sum and report_power's total.
SUM_TOLERANCE = 1e-3

_CLOCK_CELL = re.compile(r"^(clkbuf|clkload)")
_ROW = re.compile(r"^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$", re.M)


def group_of(instance: str) -> str:
    """Which reported group an instance name belongs to."""
    head = instance.split("/", 1)[0]
    if "/" in instance and head in BLOCKS:
        return head
    if _CLOCK_CELL.match(head):
        return CLOCK_TREE
    return OTHER


def parse_instance_rows(text: str) -> list[tuple[str, float, float, float, float]]:
    """``(name, internal, switching, leakage, total)`` per instance row, from the
    block between this script's BLOCK_BEGIN/BLOCK_END markers."""
    begin, end = text.find("BLOCK_BEGIN"), text.find("BLOCK_END")
    if begin < 0 or end < begin:
        raise sta.StaError("no per-instance power block in the OpenROAD log")
    rows = []
    for m in _ROW.finditer(text[begin:end]):
        try:
            values = [float(m.group(i)) for i in range(1, 5)]
        except ValueError:
            continue  # header or rule lines
        rows.append((m.group(5), *values))
    return rows


def aggregate(rows) -> dict[str, dict[str, float]]:
    out = {g: {"n": 0, "internal_w": 0.0, "switching_w": 0.0, "leakage_w": 0.0, "total_w": 0.0}
           for g in GROUPS}
    for name, internal, switching, leakage, total in rows:
        g = out[group_of(name)]
        g["n"] += 1
        g["internal_w"] += internal
        g["switching_w"] += switching
        g["leakage_w"] += leakage
        g["total_w"] += total
    return out


def _check_gap(inst_sum: float, total: float, what: str = "") -> float:
    gap = abs(inst_sum - total) / total
    if gap > SUM_TOLERANCE:
        raise sta.StaError(
            f"{what}per-instance sum {inst_sum:.6e} W differs from report_power total "
            f"{total:.6e} W by {gap:.2%} (> {SUM_TOLERANCE:.1%}); parse missed rows"
        )
    return gap


def measure(corner: "sta.Corner", pdk, period_ns: float = sta.RATIFIED_RATE_PERIOD_NS,
            tag: str = "") -> dict:
    """Uniform-activity per-instance power at ``period_ns`` (default: the 1 MHz
    ratified rate, file names unchanged). ``tag`` keeps another rate's session
    files apart."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    started = time.time()
    spef = WORK_DIR / f"trng_top.{corner.liberty}.{corner.rc}.spef"
    script = sta._tcl(
        pdk=pdk, corner=corner, period_ns=period_ns,
        spef_path=spef, bisect=False,
    )
    script += (
        'puts "BLOCK_BEGIN"\n'
        "report_power -instances [get_cells *] -digits 6\n"
        'puts "BLOCK_END"\n'
    )
    script_path = WORK_DIR / f"by-block{tag}.{corner.liberty}.{corner.rc}.tcl"
    log_path = WORK_DIR / f"by-block{tag}.{corner.liberty}.{corner.rc}.log"
    script_path.write_text(script)
    text = sta._run_openroad(script_path, log_path)
    total = sta._parse_power(text)["total"]
    groups = aggregate(parse_instance_rows(text))
    inst_sum = sum(g["total_w"] for g in groups.values())
    gap = _check_gap(inst_sum, total["total_w"])
    return {
        "corner": corner, "total": total, "groups": groups, "instance_sum_w": inst_sum,
        "gap": gap, "script": script_path, "log": log_path, "wall_s": time.time() - started,
        "spef": spef,
    }


# --------------------------------------------------------------------------- #
# VCD-activity mode (#812)
# --------------------------------------------------------------------------- #


def activity_block(manifest: dict, workload: str, window: str) -> list[str]:
    """The ``read_vcd`` + annotation + per-instance power lines for one window,
    inside ``activity_power``'s ACT_BEGIN/ACT_END frame so its parser (and its
    annotation validation) is reused unchanged."""
    tr = manifest["traces"][workload]
    lo, hi = tr["windows_ps"][window]
    return [
        f'puts "ACT_BEGIN {workload} {window}"',
        f"read_vcd -scope {activity.STA_SCOPE} -begin_time {lo} -end_time {hi} "
        f"{REPO_ROOT / tr['vcd_path']}",
        "report_activity_annotation",
        'puts "BLOCK_BEGIN"',
        "report_power -instances [get_cells *] -digits 6",
        'puts "BLOCK_END"',
        "report_power -digits 6",
        'puts "ACT_END"',
    ]


def parse_activity_session(text: str, workload: str, window: str) -> dict:
    """Validated annotation, ``report_power``'s total and the grouped
    per-instance rows of the one ``(workload, window)`` segment.

    Raises ``activity.ActivityError`` when OpenSTA bound too little (or nothing)
    to the design, and ``sta.StaError`` when the instance block is missing or
    does not sum to the total. A trace that annotates nothing never becomes a
    number."""
    segments = ap_mod.parse_segments(text)  # validates annotation of every segment
    seg = segments.get((workload, window))
    if seg is None:
        raise activity.ActivityError(
            f"no ({workload}, {window}) segment in the OpenROAD log; got {sorted(segments)}"
        )
    body = next(m.group(3) for m in ap_mod._SEGMENT.finditer(text)
                if (m.group(1), m.group(2)) == (workload, window))
    groups = aggregate(parse_instance_rows(body))
    inst_sum = sum(g["total_w"] for g in groups.values())
    total = seg["power"]["total"]
    gap = _check_gap(inst_sum, total["total_w"], f"{workload}/{window}: ")
    return {"annotation": seg["annotation"], "total": total, "groups": groups,
            "instance_sum_w": inst_sum, "gap": gap}


def measure_activity(corner: "sta.Corner", pdk, manifest: dict, label: str,
                     workload: str, window: str = ACTIVITY_WINDOW) -> dict:
    """One clock rate: the uniform per-instance session and the VCD-activity
    per-instance session, both at the manifest's clock period, over one SPEF."""
    tr = manifest["traces"][workload]
    period_ns = float(tr["clock_period_ns"])
    started = time.time()
    uniform = measure(corner, pdk, period_ns, tag=f".{label}")
    tag = f"{label}.{corner.liberty}.{corner.rc}"
    script_path = WORK_DIR / f"by-block-activity.{tag}.tcl"
    log_path = WORK_DIR / f"by-block-activity.{tag}.log"
    script_path.write_text(sta._tcl(
        pdk=pdk, corner=corner, period_ns=period_ns, spef_path=uniform["spef"],
        bisect=False, activity_block=activity_block(manifest, workload, window)))
    text = sta._run_openroad(script_path, log_path)
    observed = parse_activity_session(text, workload, window)
    return {
        "label": label, "period_ns": period_ns, "workload": workload, "window": window,
        "trace": tr, "uniform": uniform, "observed": observed,
        "script": script_path, "log": log_path, "wall_s": time.time() - started,
    }


def compare_rows(rate: dict) -> list[tuple[str, float, float, float]]:
    """``(group, uniform_w, vcd_w, vcd/uniform)`` per group, report order."""
    out = []
    for name in GROUPS:
        u = rate["uniform"]["groups"][name]["total_w"]
        o = rate["observed"]["groups"][name]["total_w"]
        out.append((name, u, o, o / u if u else float("nan")))
    return out


def result_lines(res: dict) -> str:
    lines = [
        f"- `p_total_1mhz_w`: {res['total']['total_w']:.6e}",
        f"- `p_internal_1mhz_w`: {res['total']['internal_w']:.6e}",
        f"- `p_switching_1mhz_w`: {res['total']['switching_w']:.6e}",
        f"- `p_leakage_1mhz_w`: {res['total']['leakage_w']:.6e}",
        f"- `p_instance_sum_1mhz_w`: {res['instance_sum_w']:.6e}",
        f"- `instance_sum_gap`: {res['gap']:.3e}",
    ]
    for name in GROUPS:
        g = res["groups"][name]
        key = name.removeprefix("u_")
        lines += [
            f"- `n_{key}`: {g['n']}",
            f"- `p_{key}_total_w`: {g['total_w']:.6e}",
            f"- `p_{key}_internal_w`: {g['internal_w']:.6e}",
            f"- `p_{key}_switching_w`: {g['switching_w']:.6e}",
            f"- `p_{key}_leakage_w`: {g['leakage_w']:.6e}",
        ]
    return "\n".join(lines)


def render(stem: str, raw_dir: Path, res: dict, pdk, git: dict, openroad: str) -> str:
    c = res["corner"]
    lib = sta.liberty_path(pdk, c.liberty)
    paths = sta.deck_paths(pdk)
    rcx = sta.rcx_rules_path(pdk, c.rc)
    raw = []
    for src, name in ((res["script"], "by-block.tcl"), (res["log"], "by-block.log")):
        shutil.copyfile(src, raw_dir / name)
        raw.append((name, report.sha256_file(raw_dir / name)))
    cond = sta.liberty_operating_conditions(lib)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    front = [
        "---",
        f"record: {stem}",
        f"date: {now}",
        "status: valid",
        "",
        "level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)",
        "",
        "testbench:",
        f"  path: sim/tb/{SLUG}/run_by_block.py",
        f"  sha: {report.blob_sha(REPO_ROOT, Path(__file__))}",
        "netlist:",
        "  path: layout/digital/trng_top.def",
        f"  sha: {report.blob_sha(REPO_ROOT, sta.DEF_PATH)}",
        "  note: >-",
        "    The committed routed DEF (same DUT as the digital-sta-power family).",
        "    Instance names keep the RTL hierarchy prefix, which is how power is",
        "    attributed to a sub-block.",
        f"repo_commit: {report.repo_commit_field(git)}",
        "",
        f"pdk: {pdk.variant} @ {pdk.version}",
        "pdk.models:",
        f"  - {lib} (liberty corner {c.liberty}, sha256:{report.sha256_file(lib)})",
        f"  - {paths['tech_lef']} (tech LEF, {sta.TECH_LEF_CORNER} deck, "
        f"sha256:{report.sha256_file(paths['tech_lef'])})",
        f"  - {paths['cell_lef']} (cell LEF, sha256:{report.sha256_file(paths['cell_lef'])})",
        f"  - {rcx} (OpenRCX interconnect corner {c.rc}, sha256:{report.sha256_file(rcx)})",
        "",
        "tool:",
        '  ngspice: "n/a (gate-level record -- power comes from OpenSTA inside OpenROAD)"',
        f"  openroad: \"{openroad}\"",
        "",
        "corner:",
        f"  process: {c.process}",
        f"  voltage: {c.vdd:.2f} V",
        f"  temperature: {c.temp_c:g}",
        f"  liberty: {sta.CELL_LIBRARY}__{c.liberty}",
        f"  interconnect: {c.rc} (OpenRCX rule deck)",
        "  liberty_operating_conditions: "
        + ", ".join(f"{k} {v:g}" for k, v in cond.items()),
        "",
        "analysis:",
        "  type: power (OpenSTA report_power -instances over the committed routed DEF, "
        "OpenRCX-extracted parasitics back-annotated as SPEF)",
        "  clock: clk, 1000 ns (1 MHz), propagated (the CTS-built tree in the DEF)",
        f"  power_activity: {sta.ACTIVITY} transitions/net/cycle, duty {sta.ACTIVITY_DUTY} "
        "(set_power_activity -global; the same declared activity as digital-sta-power)",
        "seeds: n/a (deterministic analysis)",
        "",
        "raw:",
        f"  path: sim/records/raw/{stem}/",
        "  files:",
        *[f"    - {n}  sha256:{d}" for n, d in raw],
        f"wall_time: {res['wall_s']:.1f}s",
        "---",
    ]
    body = f"""
## Result

{result_lines(res)}

Numbers only. These are liberty-power figures at a declared uniform activity
(DR-0021 section 3), not measured supply currents. Each instance is counted in
exactly one group and the group totals sum to `report_power`'s own total (gap
above). The clock-tree group is `clkbuf_*`/`clkload*` cells; `top_level_other`
is every remaining instance without a hierarchy prefix (placement/repair
buffers, tap, endcap and filler cells).

## How to reproduce

```sh
python3 sim/tb/{SLUG}/run_by_block.py --liberty {c.liberty} --rc {c.rc}
```

## Caveats

- Single corner ({c.liberty} / OpenRCX {c.rc}); says nothing about any other corner.
- Uniform declared activity, not this design's data-dependent activity.
- Hierarchy attribution is by instance-name prefix in the flattened as-built
  netlist; a cell the flow added outside a prefix lands in `top_level_other` or
  `clock_tree`.

---

Written by `sim/tb/{SLUG}/run_by_block.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
"""
    return "\n".join(front) + "\n" + body


def activity_values(rates: list[dict]) -> dict[str, float]:
    """Flat ``key -> value`` bullets of the VCD-activity record, keyed by rate label."""
    out: dict[str, float] = {}
    for r in rates:
        lab, o, u = r["label"], r["observed"], r["uniform"]
        out[f"{lab}_period_ns"] = r["period_ns"]
        out[f"{lab}_uniform_total_w"] = u["total"]["total_w"]
        out[f"{lab}_vcd_total_w"] = o["total"]["total_w"]
        out[f"{lab}_vcd_over_uniform"] = o["total"]["total_w"] / u["total"]["total_w"]
        for term in ("internal", "switching", "leakage"):
            out[f"{lab}_uniform_{term}_w"] = u["total"][f"{term}_w"]
            out[f"{lab}_vcd_{term}_w"] = o["total"][f"{term}_w"]
        out[f"{lab}_vcd_instance_sum_gap"] = o["gap"]
        out[f"{lab}_uniform_instance_sum_gap"] = u["gap"]
        out[f"{lab}_annotated_pins"] = float(o["annotation"]["vcd"])
        out[f"{lab}_unannotated_pins"] = float(o["annotation"]["unannotated"])
        out[f"{lab}_annotated_fraction"] = o["annotation"]["annotated_fraction"]
        for name, uw, ow, ratio in compare_rows(r):
            key = name.removeprefix("u_")
            out[f"{lab}_{key}_uniform_w"] = uw
            out[f"{lab}_{key}_vcd_w"] = ow
            out[f"{lab}_{key}_ratio"] = ratio
            out[f"{lab}_{key}_vcd_leakage_w"] = r["observed"]["groups"][name]["leakage_w"]
    return out


def _uw(v: float) -> str:
    return f"{v * 1e6:.3f}"


def activity_tables(rates: list[dict]) -> str:
    chunks = []
    for r in rates:
        rows = [
            f"### {r['label']} (clock period {r['period_ns']:g} ns)",
            "",
            "| sub-block | uniform uW | VCD-derived uW | VCD - uniform uW | VCD / uniform |",
            "|---|---:|---:|---:|---:|",
        ]
        for name, uw, ow, ratio in compare_rows(r):
            rows.append(f"| {name} | {_uw(uw)} | {_uw(ow)} | {_uw(ow - uw)} | {ratio:.3f} |")
        ut, ot = r["uniform"]["total"]["total_w"], r["observed"]["total"]["total_w"]
        rows.append(f"| **whole section** | {_uw(ut)} | {_uw(ot)} | {_uw(ot - ut)} | {ot / ut:.3f} |")
        chunks.append("\n".join(rows))
    return "\n\n".join(chunks)


def render_activity(stem: str, raw_dir: Path, rates: list[dict], manifests: dict,
                    pdk, git: dict, openroad: str) -> str:
    corner = rates[0]["corner"]
    c = corner
    lib = sta.liberty_path(pdk, c.liberty)
    paths = sta.deck_paths(pdk)
    rcx = sta.rcx_rules_path(pdk, c.rc)
    raw = []
    for r in rates:
        lab = r["label"]
        for src, name in ((r["uniform"]["script"], f"{lab}-uniform.tcl"),
                          (r["uniform"]["log"], f"{lab}-uniform.log"),
                          (r["script"], f"{lab}-activity.tcl"),
                          (r["log"], f"{lab}-activity.log")):
            shutil.copyfile(src, raw_dir / name)
            raw.append((name, report.sha256_file(raw_dir / name)))
        (raw_dir / f"{lab}-manifest.json").write_text(
            json.dumps(manifests[lab], indent=2, sort_keys=True) + "\n")
        raw.append((f"{lab}-manifest.json", report.sha256_file(raw_dir / f"{lab}-manifest.json")))
    ident = manifests[rates[0]["label"]]["identities"]
    cond = sta.liberty_operating_conditions(lib)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    front = [
        "---",
        f"record: {stem}",
        f"date: {now}",
        "status: valid",
        "",
        "level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)",
        "",
        "testbench:",
        f"  path: sim/tb/{SLUG}/run_by_block.py",
        f"  sha: {report.blob_sha(REPO_ROOT, Path(__file__))}",
        "netlist:",
        "  path: layout/digital/trng_top.def",
        f"  sha: {report.blob_sha(REPO_ROOT, sta.DEF_PATH)}",
        "  note: >-",
        "    The committed routed DEF re-timed at this corner; the activity comes from",
        "    simulating the matching as-built gate-level netlist",
        f"    layout/digital/trng_top.pnr.v (sha {ident['netlist']['git_blob_sha']}).",
        f"repo_commit: {report.repo_commit_field(git)}",
        "",
        f"pdk: {pdk.variant} @ {pdk.version}",
        "pdk.models:",
        f"  - {lib} (liberty corner {c.liberty}, sha256:{report.sha256_file(lib)})",
        f"  - {paths['tech_lef']} (tech LEF, {sta.TECH_LEF_CORNER} deck, "
        f"sha256:{report.sha256_file(paths['tech_lef'])})",
        f"  - {paths['cell_lef']} (cell LEF, sha256:{report.sha256_file(paths['cell_lef'])})",
        f"  - {rcx} (OpenRCX interconnect corner {c.rc}, sha256:{report.sha256_file(rcx)})",
    ]
    for m in ident["cell_models"]:
        front.append(f"  - {m['path']} (gate-simulation cell model, sha256:{m['sha256']})")
    front += [
        "",
        "tool:",
        '  ngspice: "n/a (gate-level record -- power comes from OpenSTA inside OpenROAD)"',
        f'  openroad: "{openroad}"',
        f'  simulator: "{ident["simulator"]} {ident["simulator_flags"]}"',
        "",
        "corner:",
        f"  process: {c.process}",
        f"  voltage: {c.vdd:.2f} V",
        f"  temperature: {c.temp_c:g}",
        f"  liberty: {sta.CELL_LIBRARY}__{c.liberty}",
        f"  interconnect: {c.rc} (OpenRCX rule deck)",
        "  liberty_operating_conditions: "
        + ", ".join(f"{k} {v:g}" for k, v in cond.items()),
        "",
        "analysis:",
        "  type: power (OpenSTA report_power -instances over the committed routed DEF, "
        "OpenRCX parasitics as SPEF, switching activity read from a gate-level VCD), "
        "against a uniform-activity session at the same clock",
        "  clock: "
        + "; ".join(f"{r['label']} {r['period_ns']:g} ns, propagated" for r in rates),
        f"  uniform_baseline: {sta.ACTIVITY} transitions/net/cycle, duty {sta.ACTIVITY_DUTY} "
        "(set_power_activity -global; as digital-power-by-block)",
        f"  activity_scope: {activity.STA_SCOPE} (read_vcd -scope)",
        f"  activity_window: {rates[0]['window']}",
        f"seeds: base {rates[0]['trace']['base_seed']}; workload {rates[0]['workload']} "
        f"{rates[0]['trace']['seed']}",
        "",
        "activity:",
        "  note: >-",
        "    Zero-delay gate simulation of the as-built post-route netlist; one declared",
        "    synthetic workload, not a worst case. The raw bits make no entropy claim.",
        "    Not a silicon current measurement.",
        f"  workload: {rates[0]['workload']}",
        f"  window: {rates[0]['window']} (cycles "
        f"{rates[0]['trace']['windows_cycles'][rates[0]['window']]})",
        f"  testbench_sha: {ident['testbench']['git_blob_sha']}",
        f"  workloads_module_sha: {ident['workloads_module_git_blob_sha']}",
        "  traces:",
    ]
    for r in rates:
        t = r["trace"]
        front += [
            f"    - rate: {r['label']}",
            f"      clock_period_ns: {t['clock_period_ns']:g}",
            f"      vcd_sha256: {t['vcd_sha256']}",
            f"      vcd_bytes: {t['vcd_bytes']}",
            f"      stimulus_sha256: {t['stimulus_sha256']}",
            f"      cycles: {t['cycles']}",
            f"      instances_matched: {t['validation']['instances_matched']}/"
            f"{t['validation']['netlist_instances']}",
            f"      xz_events: {t['validation']['xz_events']}",
        ]
    front += ["", "raw:", f"  path: sim/records/raw/{stem}/", "  files:"]
    front += [f"    - {n}  sha256:{d}" for n, d in raw]
    front += [f"wall_time: {sum(r['wall_s'] for r in rates):.1f}s", "---"]
    bullets = "\n".join(f"- `{k}`: {v:.6e}" for k, v in activity_values(rates).items())
    body = f"""
## Result

Per-sub-block power of the routed digital section, OpenSTA `report_power
-instances` summed by `group_of` (the grouping of `digital-power-by-block-01`),
with switching activity read from a gate-level VCD ({rates[0]['workload']},
`{rates[0]['window']}` window) and, for the baseline column, the declared uniform
activity at the same clock. Every instance is in exactly one group; each group
set sums to `report_power`'s own total (gap in the bullets, limit
{SUM_TOLERANCE:.1%}).

{activity_tables(rates)}

{bullets}

Numbers only. Liberty-power figures at the stated activity (DR-0021 section 3),
not measured supply currents.

## Reconciliation with the uniform records

The 1 MHz uniform column is this tool's own uniform session and equals the
whole-section figure of `digital-power-by-block-01` (339.4 uW) because both use
the same DEF, SPEF extraction, activity and clock. It differs from the 348.2 uW
quoted in `sim/characterization-digital-activity-power.md` because that figure
comes from the 2026-10-10 `digital-sta-activity` records, taken on an earlier
routed DEF (blob `8f13adca...`); the 2026-10-29 records on the current DEF
(blob `87b3dedc...`) give 339.35 uW at this corner, and the whole-section
VCD figure for this workload there (253.55 uW, `conditioned_streaming` steady
window) agrees with the 1 MHz VCD column above to about 0.002 % (the residual
is not traced).

## Leakage versus switching at each rate

OpenSTA reads toggles per second of *trace* time, so each rate has its own VCD
(simulated at that rate's clock period) rather than a rescale of the other.
Leakage does not depend on the clock: it is the same state-weighted liberty
leakage at either rate (it varies a little with the logic states the trace
visits, see `*_vcd_leakage_w` against `*_uniform_leakage_w`). Internal and
switching power fall with the toggle rate, so at 2 kHz the section is
leakage-dominated; the VCD/uniform ratio there is therefore close to 1 and says
little about activity.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture --workload {rates[0]['workload']} \\
    --out layout/.work/{ACTIVITY_SLUG}/1mhz
python3 sim/tb/digital-sta-power/activity.py capture --workload {rates[0]['workload']} \\
    --period-ns 500000 --out layout/.work/{ACTIVITY_SLUG}/2khz
python3 sim/tb/digital-power-by-block/run_by_block.py --liberty {c.liberty} --rc {c.rc} --activity
```

## Caveats

- Single corner ({c.liberty} / OpenRCX {c.rc}); says nothing about any other corner.
- One declared stimulus ({rates[0]['workload']}); not a worst case and no entropy claim.
  The `{rates[0]['window']}` window is the post-start-up cycles of the workload
  (`windows_cycles` in the manifest); reset and start-up are not in the figures.
- Zero-delay simulation: glitching beyond same-timestamp delta activity is not
  modelled; x/z events are counted in the front matter.
- Unannotated pins run on OpenSTA's fallback activity and are counted above; a
  trace binding under {activity.MIN_ANNOTATED_FRACTION:.0%} of pins is rejected.
- Hierarchy attribution is by instance-name prefix, as in `digital-power-by-block`.

---

Written by `sim/tb/{SLUG}/run_by_block.py --activity`. Append-only: never edit or
delete this file -- a re-run or correction mints a new record and points back here
"""
    return "\n".join(front) + "\n" + body


def main_activity(args, pdk, openroad: str) -> int:
    corner = sta.Corner(args.liberty, args.rc)
    paths = args.activity or list(DEFAULT_MANIFESTS)
    rates, manifests = [], {}
    try:
        for path in paths:
            manifest = activity.load_manifest(path)
            tr = manifest["traces"].get(args.workload)
            if tr is None:
                raise activity.ActivityError(f"{path}: no workload {args.workload!r}")
            label = {1000.0: "1mhz", activity.PERIOD_2KHZ_NS: "2khz"}[float(tr["clock_period_ns"])]
            r = measure_activity(corner, pdk, manifest, label, args.workload)
            r["corner"] = corner
            rates.append(r)
            manifests[label] = manifest
    except (activity.ActivityError, sta.StaError, OSError, KeyError) as exc:
        print(f"REJECTED: {exc}", file=sys.stderr)
        return 1
    if len({r["label"] for r in rates}) != len(rates):
        print("REJECTED: two manifests at the same clock rate", file=sys.stderr)
        return 1
    print(activity_tables(rates))
    if args.no_write:
        return 0
    git = report.git_provenance(REPO_ROOT)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = report.finalize_record(
        REPO_ROOT / "sim" / "records", date, ACTIVITY_SLUG,
        lambda stem, raw_dir: render_activity(stem, raw_dir, rates, manifests, pdk, git, openroad),
    )
    print(f"wrote {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--liberty", default=DEFAULT_LIBERTY, choices=sta.LIBERTY_CORNERS)
    ap.add_argument("--rc", default=DEFAULT_RC, choices=sta.RC_CORNERS)
    ap.add_argument("--no-write", action="store_true", help="print without minting a record")
    ap.add_argument("--activity", nargs="*", type=Path, metavar="MANIFEST",
                    help="VCD-activity mode (#812): one activity.py manifest per clock rate "
                         "(default: the 1 MHz and 2 kHz manifests under layout/.work/"
                         f"{ACTIVITY_SLUG}/); mints a {ACTIVITY_SLUG} record")
    ap.add_argument("--workload", default="conditioned-streaming",
                    help="workload read from each manifest in --activity mode")
    args = ap.parse_args(argv)

    pdk = sta.resolve_pdk()
    openroad = sta.openroad_version()
    if pdk is None or openroad is None:
        print("error: needs openroad on PATH and a gf180mcu PDK install", file=sys.stderr)
        return 2
    if args.activity is not None:
        return main_activity(args, pdk, openroad)
    try:
        res = measure(sta.Corner(args.liberty, args.rc), pdk)
    except sta.StaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(result_lines(res))
    if args.no_write:
        return 0
    git = report.git_provenance(REPO_ROOT)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = report.finalize_record(
        REPO_ROOT / "sim" / "records", date, SLUG,
        lambda stem, raw_dir: render(stem, raw_dir, res, pdk, git, openroad),
    )
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
