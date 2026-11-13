"""Adapter helpers shared by the power tools (``power_switch``, ``power_switch_decay``,
``power_retention``, ``liveness_sampler_power``; ``fs_sf_capture``, ``supply_ripple`` and
``starved_hot_corner`` use only ``render``/``vals``): the "emit request / run / record /
analyze" layer that was identical in each, plus the record front-matter skeleton
(``render_header`` and friends) that was re-typed in each tool's ``render_measured`` /
``render_unmeasured``. Per-script pieces (``build_request``, ``derive``, ``checks``, and the
Result / Caveats / reproduce prose) stay in the tools; they differ for real. Everything here
either is pure or takes the per-script pieces as arguments, so each tool's emitted requests and
minted records are unchanged.
"""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path
from typing import Callable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness import klt_request as _kreq  # noqa: E402
from harness import record_mint as _mint  # noqa: E402
from harness import report as _report  # noqa: E402
import _record_parsing as _rp  # noqa: E402


def fmt(x: float) -> str:
    return f"{x:.6e}"


def label(rec: dict) -> str:
    proc, temp, vdd = rec["corner"]
    return f"{proc}/{temp:g}C/{vdd:.2f}V"


def vals(corner: dict) -> dict[str, float]:
    return {x["name"]: x["value"] for x in corner.get("measurements", []) if x.get("value") is not None}


def render(req: dict) -> str:
    return json.dumps(req, indent=1) + "\n"


SEEDS_NA = "seeds: n/a (deterministic; no noise sources)"

MODELS_LIB = "libs.tech/ngspice/sm141064.ngspice"


def render_header(*, stem: str, now, repo_root: Path, testbench: Path, netlist: Path, git: dict,
                  raw_files: Sequence[tuple[str, str]], status: str = "valid",
                  netlist_also: Path | None = None, pdk: str | None = None,
                  pdk_models: Sequence[str] = (), tool: Sequence[str] = (),
                  corner: Sequence[str] = (), analysis: Sequence[str] = (),
                  seeds: str = SEEDS_NA, wall_time: str | None = None) -> list[str]:
    """The record front matter every power tool emits, as a list of lines.

    sim/README.md fixes the field order and the blank lines between blocks; this is the one
    place that spells them out, so a new provenance field is added once rather than in each
    tool. The ``pdk``/``tool``/``corner``/``analysis`` blocks take their *indented body* lines
    from the caller (they are real per-tool differences -- a batch-fleet record names the
    worker's ngspice, a local probe the host's) and are omitted entirely when empty, which is
    how the attempt records drop them. The closing ``---`` and the blank line after it are
    included, so a caller continues straight into ``## Result``.
    """
    lines = ["---", f"record: {stem}", f"date: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}",
             f"status: {status}", "",
             "testbench:", f"  path: {testbench.relative_to(repo_root)}",
             f"  sha: {_report.blob_sha(repo_root, testbench)}",
             "netlist:", f"  path: {netlist.relative_to(repo_root)}",
             f"  sha: {_report.blob_sha(repo_root, netlist)}"]
    if netlist_also is not None:
        lines.append(f"  also: {netlist_also.relative_to(repo_root)} "
                     f"sha {_report.blob_sha(repo_root, netlist_also)}")
    lines += [f"repo_commit: {_report.repo_commit_field(git)}", ""]
    if pdk is not None:
        lines.append(f"pdk: {pdk}")
        if pdk_models:
            lines += ["pdk.models:", *pdk_models, ""]
    if tool:
        lines += ["tool:", *tool, ""]
    if corner:
        lines += ["corner:", *corner, ""]
    if analysis:
        lines += ["analysis:", *analysis, seeds, ""]
    lines += ["raw:", f"  path: sim/records/raw/{stem}/", "  files:",
              *[f"    - {n}  sha256:{h}" for n, h in raw_files]]
    if wall_time is not None:
        lines.append(f"wall_time: {wall_time}")
    return lines + ["---", ""]


def record_footer(tool_name: str, *, terse: bool = False) -> list[str]:
    """The closing rule and the append-only notice every record ends with.

    ``terse`` is the attempt-record wording. Like the front matter, this is record format
    rather than per-tool prose, so it lives here and not in eight places.
    """
    notice = "Append-only." if terse else "Append-only: never edit or delete this file."
    return ["---", "", f"Written by `sim/tools/{tool_name}.py record`. {notice}", ""]


def corner_lines(row: dict, nominal_v: float = 3.3) -> list[str]:
    """The ``corner:`` body for one measured unit."""
    return [f"  process: {row['process']}",
            f"  voltage: {_report._voltage_label(row['vdd'], nominal_v)}",
            f"  temperature: {row['temperature_c']}"]


def fleet_where(rep: dict) -> str:
    """Who ran it, for the Result sentence: the batch jobs, or a local debug probe."""
    jobs = ", ".join(_report.fleet_provenance(rep)["jobs"])
    return (f"batch fleet through klt sim (jobs {jobs})" if jobs
            else "local ngspice (single-point debug probe)")


def fleet_header(*, stem: str, row: dict, unit: dict, rep: dict,
                 raw_files: Sequence[tuple[str, str]], now, git: dict, repo_root: Path,
                 testbench: Path, netlist: Path, sections: Sequence[str],
                 analysis: Sequence[str], netlist_also: Path | None = None) -> list[str]:
    """Front matter for a measured record from a batch-fleet grid.

    The PDK and ngspice are the fleet worker's (``fleet_provenance``); the klt version and
    platform are the submitting host's, labelled as such.
    """
    prov = rep.get("provenance", {})
    fp = _report.fleet_provenance(rep)
    return render_header(
        stem=stem, now=now, repo_root=repo_root, testbench=testbench, netlist=netlist,
        netlist_also=netlist_also, git=git, raw_files=raw_files,
        pdk=f"gf180mcuD @ {fp['pdk_ver']}",
        pdk_models=[f"  - {MODELS_LIB} (sections: {' '.join(sections)})"],
        tool=[f"  klt: {prov.get('klt_version', 'unknown')} (client; batch backend)",
              f'  ngspice: "{fp["ngspice"]} (batch fleet)"',
              f'  platform: "{platform.platform()} (submitting host)"'],
        corner=corner_lines(row), analysis=analysis,
        wall_time=f"{unit.get('runtime_s', 'n/a')}s")


def render_attempt(*, stem: str, corners: Sequence[dict], rep: dict,
                   raw_files: Sequence[tuple[str, str]], now, git: dict, note: str,
                   repo_root: Path, testbench: Path, netlist: Path, tool_name: str) -> str:
    """The whole attempt record for a grid that produced no usable readings.

    Short by design: an attempt record claims no number, so it carries the provenance needed to
    tell which inputs were tried and nothing else. ``liveness_sampler_power`` writes its own,
    richer variant (it reports the fleet job's diagnostics).
    """
    prov = rep.get("provenance", {})
    lines = render_header(
        stem=stem, now=now, repo_root=repo_root, testbench=testbench, netlist=netlist, git=git,
        raw_files=raw_files, tool=[f"  klt: {prov.get('klt_version', 'unknown')}"])
    lines += ["## Result", "",
              f"UNMEASURED: {len(corners)} unit(s) produced no usable readings; "
              "no number is claimed.", ""]
    if note:
        lines += [note, ""]
    return "\n".join(lines + record_footer(tool_name, terse=True))


def analyse_report(report: dict, derive: Callable, checks: Callable, derivation_error: type[Exception]) -> list[dict]:
    rows = []
    for c in report.get("corners", []):
        v = vals(c)
        vdd = float(c.get("supply_v", {}).get("vsup", 3.3))
        key = f"{c.get('process')}/{c.get('temperature_c')}/{vdd:.2f}"
        row = {"corner": key, "process": c.get("process"), "temperature_c": c.get("temperature_c"),
               "vdd": vdd, "status": c.get("status")}
        try:
            row.update(derive(v, vdd))
            row["problems"] = checks(row)
            row["verdict"] = "OK" if not row["problems"] else "SUSPECT"
        except derivation_error as exc:
            row["problems"] = [str(exc)]
            row["verdict"] = "UNMEASURED"
        rows.append(row)
    return rows


def load_records(records_dir: Path, slug: str) -> list[dict]:
    """The current measurement records for ``slug``: corner plus Result bullets."""
    out = []
    for path in _rp.current_records(records_dir, f"*-{slug}-[0-9]*.md"):
        text = path.read_text()
        proc, temp, vdd = _rp.parse_corner(text, label=path.stem)
        out.append({"stem": path.stem, "corner": (proc, temp, vdd),
                    "values": _rp.parse_values(_rp.result_section(text, label=path.stem), label=path.stem)})
    return out


def cmd_emit(check: bool, *, path: Path, text: str, repo_root: Path, n_units: int) -> int:
    return _kreq.emit_requests(
        [(path, text)], check, repo_root=repo_root,
        ok=lambda: print(f"ok: {path.relative_to(repo_root)} matches the declared grid ({n_units} units)"))


def cmd_run(outdir: str, backend: str, klt_cmd: str, only: str | None, *, request: Path, tb_dir: Path,
            build_request: Callable) -> int:
    return _kreq.run_probe_or_grid(
        outdir, backend, klt_cmd, only, request=request, tb_dir=tb_dir,
        render_probe=lambda point: render(build_request(point)), probe_hint="--only PROCESS/TEMP/VDD")


def cmd_record(paths: list[str], note: str, records_dir: Path | None, *, repo_root: Path, slug: str,
               analyse_report: Callable, render_measured: Callable, render_unmeasured: Callable) -> int:
    return _mint.mint_records(
        paths, note, records_dir, repo_root=repo_root, slug=slug, slug_attempt=f"{slug}-attempt",
        analyse_report=analyse_report, render_measured=render_measured, render_unmeasured=render_unmeasured)


def cmd_analyze(paths: list[str], as_json: bool, *, analyse_report: Callable, table: Callable) -> int:
    rows: list[dict] = []
    for p in paths:
        rows += analyse_report(json.loads(Path(p).read_text()))
    if as_json:
        print(json.dumps(rows, indent=1))
    else:
        print(table(rows))
        bad = [r for r in rows if r["verdict"] != "OK"]
        print(f"\n{len(rows) - len(bad)}/{len(rows)} units usable"
              + ("" if not bad else "; not usable: " + ", ".join(f"{r['corner']} ({r['verdict']})" for r in bad)))
    return 0
