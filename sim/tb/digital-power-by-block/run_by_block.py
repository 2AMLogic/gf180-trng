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

Default corner is ``ff_125C_3v60`` / OpenRCX ``max``: the corner at which
``sim/tools/power_rollup.py`` finds the committed digital active term binding.
Like every record in the ``digital-sta-power`` family this is a liberty-power
model at a declared activity, not a measured supply current ([DR-0021] section
3), and the record says so.

[DR-0021]: ../../../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md
"""

from __future__ import annotations

import argparse
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

import run_sta as sta  # noqa: E402
from harness import report  # noqa: E402

SLUG = "digital-power-by-block"
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


def measure(corner: "sta.Corner", pdk) -> dict:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    started = time.time()
    spef = WORK_DIR / f"trng_top.{corner.liberty}.{corner.rc}.spef"
    script = sta._tcl(
        pdk=pdk, corner=corner, period_ns=sta.RATIFIED_RATE_PERIOD_NS,
        spef_path=spef, bisect=False,
    )
    script += (
        'puts "BLOCK_BEGIN"\n'
        "report_power -instances [get_cells *] -digits 6\n"
        'puts "BLOCK_END"\n'
    )
    script_path = WORK_DIR / f"by-block.{corner.liberty}.{corner.rc}.tcl"
    log_path = WORK_DIR / f"by-block.{corner.liberty}.{corner.rc}.log"
    script_path.write_text(script)
    text = sta._run_openroad(script_path, log_path)
    total = sta._parse_power(text)["total"]
    groups = aggregate(parse_instance_rows(text))
    inst_sum = sum(g["total_w"] for g in groups.values())
    gap = abs(inst_sum - total["total_w"]) / total["total_w"]
    if gap > SUM_TOLERANCE:
        raise sta.StaError(
            f"per-instance sum {inst_sum:.6e} W differs from report_power total "
            f"{total['total_w']:.6e} W by {gap:.2%} (> {SUM_TOLERANCE:.1%}); parse missed rows"
        )
    return {
        "corner": corner, "total": total, "groups": groups, "instance_sum_w": inst_sum,
        "gap": gap, "script": script_path, "log": log_path, "wall_s": time.time() - started,
    }


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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--liberty", default=DEFAULT_LIBERTY, choices=sta.LIBERTY_CORNERS)
    ap.add_argument("--rc", default=DEFAULT_RC, choices=sta.RC_CORNERS)
    ap.add_argument("--no-write", action="store_true", help="print without minting a record")
    args = ap.parse_args(argv)

    pdk = sta.resolve_pdk()
    openroad = sta.openroad_version()
    if pdk is None or openroad is None:
        print("error: needs openroad on PATH and a gf180mcu PDK install", file=sys.stderr)
        return 2
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
