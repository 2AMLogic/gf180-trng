"""Append-only evidence records, conforming to the format ratified in
``sim/README.md``.

One record covers **one testbench at one PVT point**. A PVT sweep -- one
invocation of ``sim/run_corners.py`` across many corners/temperatures/
supplies -- produces one record per point, never one record with a table of
corners. That is the ratified convention this repository closed in issue
#5 before this harness landed; it differs from the aggregate-grid-record
convention used by the harness pattern this module was bootstrapped from
(2AMLogic/gf180-bandgap#23). See
``spec/decision-records/DR-0005-sim-harness-record-granularity.md`` for the
reconciliation.

Record naming: ``<YYYY-MM-DD>-<testbench-slug>-<nn>.md`` under
``sim/records/``, with raw output under
``sim/records/raw/<YYYY-MM-DD>-<testbench-slug>-<nn>/``.

CLAUDE.md and ``sim/README.md``: "sim/ results are append-only evidence."
This module never overwrites an existing record -- on a naming collision it
mints the next unused sequence number rather than clobbering.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import platform
import statistics
import subprocess
from pathlib import Path

from .corners import PvtPoint
from .pdk import Pdk
from .runner import RunResult
from .testbench import Testbench

RECORDS_DIRNAME = "records"
RAW_DIRNAME = "raw"


class RecordExists(RuntimeError):
    """Refused to overwrite an existing append-only record."""


def _git(*args: str, cwd: Path) -> str:
    try:
        out = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
        )
        return out.stdout.strip()
    except OSError:  # pragma: no cover - git always present in this repo
        return ""


def git_provenance(repo_root: Path) -> dict:
    """``repo_commit`` per sim/README.md: HEAD, ``-dirty`` if the tree is dirty."""
    commit = _git("rev-parse", "HEAD", cwd=repo_root) or "unknown"
    dirty = bool(_git("status", "--porcelain", cwd=repo_root))
    return {"commit": commit, "dirty": dirty}


def repo_commit_field(git: dict) -> str:
    return git["commit"] + ("-dirty" if git["dirty"] else "")


def blob_sha(repo_root: Path, path: Path) -> str:
    """Git blob SHA of ``path``'s current content.

    sim/README.md defines ``testbench.sha``/``netlist.sha`` as
    ``git rev-parse HEAD:<path>``. We use ``git hash-object`` instead so this
    resolves correctly even when the file has not been committed yet (e.g.
    while bringing up a new testbench) -- it returns the same blob SHA once
    committed, since both hash identical blob content.
    """
    out = _git("hash-object", str(path), cwd=repo_root)
    return out or "unknown"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def allocate_record_stems(records_dir: Path, date: str, slug: str, count: int) -> list[str]:
    """Mint ``count`` consecutive unused ``<date>-<slug>-<nn>`` stems.

    Append-only: never reuses a sequence number, even across superseded
    records. Allocating a whole PVT grid's stems in one call (rather than
    one at a time as each point finishes) is what lets ``run_corners.py``
    execute points concurrently without two workers racing for the same
    sequence number.

    An already-allocated stem is counted as used from the moment its
    ``raw/<stem>/`` directory exists, not from when its ``.md`` is written.
    A record's ``.md`` only appears when its point finishes, so scanning
    ``.md`` alone would hand the same number to a *second* ``run_corners.py``
    invocation started while the first is still simulating -- and long
    transient-noise runs (hours per PVT point) make running one corner per
    invocation, concurrently, the normal way to cover a grid. The loser of
    that race used to discover the collision only at ``write_record`` time,
    i.e. after paying for the whole run.
    """
    records_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"{date}-{slug}-"
    max_n = 0
    candidates = list(records_dir.glob(f"{prefix}*.md"))
    candidates += [p for p in (records_dir / RAW_DIRNAME).glob(f"{prefix}*") if p.is_dir()]
    for path in candidates:
        suffix = path.stem[len(prefix):]
        if suffix.isdigit():
            max_n = max(max_n, int(suffix))
    return [f"{prefix}{max_n + i:02d}" for i in range(1, count + 1)]


def allocate_record_stem(records_dir: Path, date: str, slug: str) -> str:
    """Mint the next unused ``<date>-<slug>-<nn>`` stem."""
    return allocate_record_stems(records_dir, date, slug, 1)[0]


def _voltage_label(vdd: float, nominal: float) -> str:
    if nominal == 0:
        return f"{vdd:.3f} V"
    offset_pct = (vdd - nominal) / nominal * 100.0
    if abs(offset_pct) < 1e-6:
        return f"{vdd:.3f} V (nominal {nominal:g} V)"
    sign = "+" if offset_pct > 0 else ""
    return f"{vdd:.3f} V (nominal {nominal:g} V, {sign}{offset_pct:.0f}%)"


def _fmt_wall(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds / 60
    return f"{minutes:.1f}m"


def _fmt(value) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        if value != 0 and (abs(value) < 1e-3 or abs(value) >= 1e5):
            return f"{value:.6e}"
        return f"{value:.6g}"
    return str(value)


def _yaml_str(value: str) -> str:
    """Quote a scalar only when needed for a valid, unambiguous YAML string.

    ``: `` (colon-space) and a handful of leading indicator characters are
    the only things that actually change parsing for a plain scalar; ``@``
    and similar are safe unquoted (and the worked example in sim/README.md
    leaves them bare, e.g. ``pdk: gf180mcuC @ <pdk-version-tag>``).
    """
    if value == "":
        return '""'
    starts_special = value[0] in "!&*?|>'\"%@`#-:{}[],"
    needs_quote = ": " in value or value.endswith(":") or starts_special or value.strip() != value
    if needs_quote:
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value


def build_record(
    tb: Testbench,
    pdk: Pdk,
    point: PvtPoint,
    results: list[RunResult],
    ngspice: str,
    repo_root: Path,
    stem: str,
    completed_utc: _dt.datetime,
    wall_seconds: float,
    raw_dir: Path,
    git: dict,
    supersedes: str = "",
) -> dict:
    """Assemble every field sim/README.md's frontmatter requires for one
    (testbench, PVT point) record."""
    # "status" here is the record's append-only lifecycle state (valid vs.
    # superseded, per sim/README.md), not a pass/fail verdict on the
    # measurement -- a failed simulation is still an honestly recorded fact,
    # surfaced in the "Result" prose section's run-failures list below.
    status = "valid"
    seeds = [r.seed for r in results if r.seed is not None]

    measure_names = list(tb.measure)
    samples: dict[str, list[float]] = {name: [] for name in measure_names}
    for r in results:
        for name in measure_names:
            if name in r.measurements:
                samples[name].append(r.measurements[name])

    raw_files: list[tuple[str, str]] = []
    for r in results:
        for fname in (r.deck_name, r.log_name):
            path = raw_dir / fname
            if path.is_file():
                raw_files.append((fname, sha256_file(path)))

    return {
        "record": stem,
        "date": completed_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "supersedes": supersedes,
        "testbench_path": _relpath(repo_root, tb.netlist),
        "testbench_sha": blob_sha(repo_root, tb.netlist),
        "netlist_path": _relpath(repo_root, tb.dut_netlist),
        "netlist_sha": blob_sha(repo_root, tb.dut_netlist),
        "repo_commit": repo_commit_field(git),
        "pdk": f"{pdk.variant} @ {pdk.version}",
        "pdk_models": [
            f"{pdk.model_lib} (sections: "
            f"{' '.join(tb.extra_lib_sections or point.corner.sections)})"
        ],
        "tool_ngspice": ngspice,
        "tool_platform": platform.platform(),
        "corner_process": point.corner.name,
        "corner_voltage": _voltage_label(point.vdd, tb.nominal_supply_v),
        "corner_voltage_v": point.vdd,
        "corner_temperature": point.temp_c,
        "analysis_type": tb.analysis_type,
        "analysis_tstop": tb.tstop or "n/a (op-point analysis)",
        "analysis_tstep": tb.tstep or "n/a",
        "analysis_tmax": tb.tmax or "n/a",
        "analysis_noise_params": tb.noise_params or "n/a",
        "analysis_runs": len(results),
        "seeds": seeds if seeds else "n/a (deterministic analysis)",
        "raw_path": _relpath(repo_root, raw_dir) + "/",
        "raw_files": raw_files,
        "wall_time": _fmt_wall(wall_seconds),
        "measure_names": measure_names,
        "samples": samples,
        "results": results,
        "tb_slug": tb.slug,
        "netlist_rel": _relpath(repo_root, tb.dut_netlist),
        "manifest_rel": _relpath(repo_root, tb.manifest_path),
    }


def _relpath(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:  # pragma: no cover - paths are always under the repo in practice
        return str(path)


def render_frontmatter(record: dict) -> str:
    lines = ["---", f"record: {record['record']}", f"date: {record['date']}",
             f"status: {record['status']}"]
    if record["supersedes"]:
        lines.append(f"supersedes: {record['supersedes']}")
    lines += [
        "",
        "testbench:",
        f"  path: {record['testbench_path']}",
        f"  sha: {record['testbench_sha']}",
        "netlist:",
        f"  path: {record['netlist_path']}",
        f"  sha: {record['netlist_sha']}",
        f"repo_commit: {record['repo_commit']}",
        "",
        f"pdk: {_yaml_str(record['pdk'])}",
        "pdk.models:",
    ]
    for entry in record["pdk_models"]:
        lines.append(f"  - {entry}")
    lines += [
        "",
        "tool:",
        f"  ngspice: {_yaml_str(record['tool_ngspice'])}",
        f"  platform: {_yaml_str(record['tool_platform'])}",
        "",
        "corner:",
        f"  process: {record['corner_process']}",
        f"  voltage: {record['corner_voltage']}",
        f"  temperature: {_fmt(record['corner_temperature'])}",
        "",
        "analysis:",
        f"  type: {record['analysis_type']}",
        f"  tstop: {record['analysis_tstop']}",
        f"  tstep: {record['analysis_tstep']}",
        f"  tmax: {record['analysis_tmax']}",
        f"  noise_params: {_yaml_str(record['analysis_noise_params'])}",
        f"  runs: {record['analysis_runs']}",
    ]
    seeds = record["seeds"]
    if isinstance(seeds, list):
        lines.append(f"seeds: [{', '.join(str(s) for s in seeds)}]")
    else:
        lines.append(f"seeds: {seeds}")
    lines += [
        "",
        "raw:",
        f"  path: {record['raw_path']}",
        "  files:",
    ]
    for fname, digest in record["raw_files"]:
        lines.append(f"    - {fname}  sha256:{digest}")
    lines += [
        f"wall_time: {record['wall_time']}",
        "---",
        "",
    ]
    return "\n".join(lines)


def render_result_section(record: dict) -> str:
    lines = ["## Result", ""]
    for name in record["measure_names"]:
        values = record["samples"][name]
        if not values:
            lines.append(f"- `{name}`: no data (all runs failed to converge)")
            continue
        if len(values) == 1:
            lines.append(f"- `{name}`: {_fmt(values[0])}")
        else:
            mean = sum(values) / len(values)
            # Sample standard deviation across seeds: the run-to-run spread
            # sim/README.md requires alongside every multi-run figure. For a
            # figure that is ITSELF a spread (a jitter sigma), this is the
            # uncertainty on that sigma, and downstream consumers need it to
            # know how many digits of it are real.
            sd = statistics.stdev(values) if len(values) > 1 else 0.0
            rel = f", {sd / abs(mean) * 100:.1f}% of mean" if mean else ""
            lines.append(
                f"- `{name}`: mean {_fmt(mean)} over {len(values)} seeds "
                f"(sd {_fmt(sd)}{rel}; min {_fmt(min(values))}, max {_fmt(max(values))})"
            )
    failed = [r for r in record["results"] if r.status != "ok"]
    if failed:
        lines.append("")
        lines.append("Run failures:")
        for r in failed:
            lines.append(f"- seed {r.seed}: {r.status} -- {r.message}")
    lines.append("")
    lines.append("Numbers only. No entropy-rate or spec-compliance claim is made by this record.")
    lines.append("")
    return "\n".join(lines)


def render_reproduce_section(record: dict, tb: Testbench) -> str:
    lines = ["## How to reproduce", "", "```sh"]
    # --supply/--supply-tol pin the EXACT recorded voltage (tolerance 0 ->
    # supply_points() returns a single point equal to --supply): omitting
    # these would default to tb.nominal_supply_v +/- tb.supply_tolerance,
    # silently re-sweeping all 3 supply points instead of reproducing the
    # one non-nominal corner (e.g. the +/-10% points) this record is for.
    supply_args = (
        f"--supply {_fmt(record['corner_voltage_v'])} --supply-tol 0 "
    )
    if isinstance(record["seeds"], list) and record["seeds"]:
        for seed in record["seeds"]:
            lines.append(
                f"python3 sim/run_corners.py {tb.slug} --corners {record['corner_process']} "
                f"--temps {_fmt(record['corner_temperature'])} {supply_args}"
                f"--seeds {seed} --no-write"
            )
    else:
        lines.append(
            f"python3 sim/run_corners.py {tb.slug} --corners {record['corner_process']} "
            f"--temps {_fmt(record['corner_temperature'])} {supply_args}--no-write"
        )
    lines += ["```", ""]
    return "\n".join(lines)


def render_caveats_section(caveats: list[str]) -> str:
    lines = ["## Caveats", ""]
    for line in caveats:
        lines.append(f"- {line}")
    lines.append("")
    return "\n".join(lines)


def render_record(record: dict, tb: Testbench, caveats: list[str]) -> str:
    body = [
        render_frontmatter(record),
        render_result_section(record),
        render_reproduce_section(record, tb),
        render_caveats_section(caveats),
        "---",
        "",
        "Written by `sim/run_corners.py`. Append-only: never edit or delete this",
        "file -- a re-run or correction mints a new record and points back here",
        "via `supersedes` (see `sim/README.md`).",
        "",
    ]
    return "\n".join(body)


def write_record(record: dict, tb: Testbench, records_dir: Path, caveats: list[str]) -> Path:
    """Write ``records/<stem>.md``; never overwrite an existing record."""
    records_dir.mkdir(parents=True, exist_ok=True)
    path = records_dir / f"{record['record']}.md"
    if path.exists():
        raise RecordExists(
            f"{path} already exists; records are append-only -- mint a new record stem"
        )
    path.write_text(render_record(record, tb, caveats))
    return path
