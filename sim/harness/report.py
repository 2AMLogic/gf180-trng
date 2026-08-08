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
import re
import statistics
import subprocess
from pathlib import Path
from typing import Callable

from . import runner
from .corners import PvtPoint
from .pdk import Pdk
from .runner import RunResult
from .testbench import Testbench

RECORDS_DIRNAME = "records"
RAW_DIRNAME = "raw"


class RecordExists(RuntimeError):
    """Refused to overwrite an existing append-only record."""


class RawFilesMismatch(RuntimeError):
    """A record's ``raw.files`` checksums disagree with the files on disk.

    The record is then not evidence of anything: its numbers no longer
    provably come from the raw output it points at. Raised (or reported)
    rather than swallowed -- see ``verify_raw_files``.
    """


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

    This scan is advisory only: it reports what is *already* taken, which
    two invocations that scan at the same instant will answer identically.
    ``reserve_record_stems`` is the allocator that actually claims stems.
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


def reserve_record_stems(records_dir: Path, date: str, slug: str, count: int) -> list[str]:
    """Claim ``count`` stems, using ``mkdir`` of ``raw/<stem>/`` as the lock.

    Scanning for the next free number and then using it (what
    ``allocate_record_stems`` does on its own) is not safe against a
    *second* ``run_corners.py`` process: both scans can return the same
    number, both runs then write their decks and logs into the same
    ``raw/<stem>/``, and the loser's raw output is silently overwritten
    after the winner has already hashed it into a record.

    ``Path.mkdir(exist_ok=False)`` is atomic (``mkdir(2)`` fails with
    ``EEXIST`` rather than racing), so creating the raw directory *is* the
    reservation: exactly one process can create any given one, and the
    other moves on to the next sequence number. The scan above is still
    used to pick a sensible starting point so this does not walk from 01
    on every run.
    """
    prefix = f"{date}-{slug}-"
    raw_root = records_dir / RAW_DIRNAME
    raw_root.mkdir(parents=True, exist_ok=True)
    start = allocate_record_stems(records_dir, date, slug, 1)[0]
    n = int(start[len(prefix):])
    stems: list[str] = []
    while len(stems) < count:
        stem = f"{prefix}{n:02d}"
        n += 1
        if (records_dir / f"{stem}.md").exists():
            # Raw directory removed but the record kept: the number is spent.
            continue
        try:
            (raw_root / stem).mkdir()
        except FileExistsError:
            continue  # another invocation owns this one
        stems.append(stem)
    return stems


def finalize_record(
    records_dir: Path,
    date: str,
    slug: str,
    render: Callable[[str, Path], str],
) -> Path:
    """Allocate a record stem, hand its raw directory to ``render``, and
    write the markdown text it returns to ``records/<stem>.md``.

    This is the "allocate -> mkdir -> write artifacts -> guard -> write
    markdown" skeleton shared by every ``sim/tb/*/run_demo.py`` script:
    ``render(stem, raw_dir)`` does the testbench-specific work (writing raw
    artifact files under ``raw_dir``, hashing them into a ``raw_files``
    list, and rendering the frontmatter/body), and this function owns the
    bookkeeping around it. Kept separate from ``write_record`` above, which
    serves the ``build_record``/``render_record`` pipeline used by
    ``sim/run_corners.py`` and takes an already-built record dict rather
    than a render callback.

    Raises ``RecordExists`` if ``records/<stem>.md`` already exists --
    normally prevented by ``allocate_record_stem`` minting an unused stem,
    but checked explicitly (as every caller did before this helper existed)
    since ``render`` runs between allocation and the check.
    """
    stem = allocate_record_stem(records_dir, date, slug)
    raw_dir = records_dir / RAW_DIRNAME / stem
    raw_dir.mkdir(parents=True, exist_ok=True)
    text = render(stem, raw_dir)
    path = records_dir / f"{stem}.md"
    if path.exists():  # pragma: no cover - allocate_record_stem prevents this
        raise RecordExists(f"{path} already exists")
    path.write_text(text)
    return path


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
    timeout_s: int | None = None,
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
        # Not rendered in the frontmatter; only used by the "How to reproduce"
        # section, which must stay copy-pasteable (sim/README.md). A run that
        # needed a non-default --timeout is NOT reproducible by a command that
        # omits it: the re-run dies on the default timeout and records "no
        # data (all runs failed to converge)" instead of the numbers above.
        "timeout_s": timeout_s,
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
        # Not rendered: kept so the record can be re-verified against the
        # directory it was actually hashed from (see verify_record).
        "raw_dir": raw_dir,
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
    # A long transient-noise run needs the --timeout it actually ran with, or
    # the reproduce command dies on the 300 s default and records nothing.
    timeout_s = record.get("timeout_s")
    timeout_args = (
        f"--timeout {timeout_s} "
        if timeout_s is not None and timeout_s != runner.DEFAULT_TIMEOUT_S
        else ""
    )
    if isinstance(record["seeds"], list) and record["seeds"]:
        for seed in record["seeds"]:
            lines.append(
                f"python3 sim/run_corners.py {tb.slug} --corners {record['corner_process']} "
                f"--temps {_fmt(record['corner_temperature'])} {supply_args}"
                f"--seeds {seed} {timeout_args}--no-write"
            )
    else:
        lines.append(
            f"python3 sim/run_corners.py {tb.slug} --corners {record['corner_process']} "
            f"--temps {_fmt(record['corner_temperature'])} {supply_args}{timeout_args}--no-write"
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
    """Write ``records/<stem>.md``; never overwrite an existing record.

    Raises ``RawFilesMismatch`` if the raw output has changed underneath the
    record between hashing (``build_record``) and writing -- a record whose
    checksums are already wrong at birth must not reach the disk.
    """
    records_dir.mkdir(parents=True, exist_ok=True)
    path = records_dir / f"{record['record']}.md"
    if path.exists():
        raise RecordExists(
            f"{path} already exists; records are append-only -- mint a new record stem"
        )
    problems = verify_record(record)
    if problems:
        raise RawFilesMismatch(
            f"refusing to write {path}: raw output changed after it was hashed "
            "(another run_corners.py invocation writing into the same raw "
            "directory?)\n  " + "\n  ".join(problems)
        )
    path.write_text(render_record(record, tb, caveats))
    return path


RAW_FILE_LINE = re.compile(r"^\s*-\s+(?P<name>\S+)\s+sha256:(?P<digest>[0-9a-f]{64})\s*$")


def parse_raw_section(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Read ``raw.path`` and ``raw.files`` back out of a rendered record.

    Deliberately a small line scanner over the shape ``render_frontmatter``
    emits, not a YAML parse: the harness is stdlib-only (see README.md), and
    this is the inverse of exactly one renderer.
    """
    raw_path = ""
    files: list[tuple[str, str]] = []
    in_raw = False
    in_files = False
    for line in text.splitlines():
        if line == "---" and files:
            break
        if line.startswith("raw:"):
            in_raw = True
            continue
        if in_raw and line.startswith("  path:"):
            raw_path = line.split(":", 1)[1].strip()
            continue
        if in_raw and line.strip() == "files:":
            in_files = True
            continue
        if in_files:
            match = RAW_FILE_LINE.match(line)
            if match:
                files.append((match.group("name"), match.group("digest")))
            else:
                in_raw = in_files = False
    return raw_path, files


def verify_raw_files(
    raw_dir: Path, raw_files: list[tuple[str, str]], *, check_unlisted: bool = True
) -> list[str]:
    """Re-hash ``raw_files`` against ``raw_dir``; return one line per problem.

    Empty list means the record's checksums still describe the bytes on
    disk. Three ways that can fail, all seen in the collision this guards
    (#60): a listed file is gone, a listed file's digest has changed
    (overwritten by another run), or the directory holds raw output the
    record never listed (another run's decks/logs landed in it).
    """
    problems: list[str] = []
    if not raw_dir.is_dir():
        return [f"{raw_dir}: raw directory is missing"]
    for fname, digest in raw_files:
        path = raw_dir / fname
        if not path.is_file():
            problems.append(f"{fname}: listed in raw.files but not present in {raw_dir}")
            continue
        actual = sha256_file(path)
        if actual != digest:
            problems.append(
                f"{fname}: sha256 on disk {actual} != {digest} recorded in raw.files"
            )
    if check_unlisted:
        listed = {name for name, _ in raw_files}
        for path in sorted(raw_dir.iterdir()):
            if path.is_file() and path.name not in listed:
                problems.append(
                    f"{path.name}: present in {raw_dir} but absent from raw.files"
                )
    return problems


def verify_record(record: dict, *, check_unlisted: bool = True) -> list[str]:
    """``verify_raw_files`` for an in-memory record from ``build_record``."""
    return verify_raw_files(
        Path(record["raw_dir"]), list(record["raw_files"]), check_unlisted=check_unlisted
    )


def verify_record_file(path: Path, repo_root: Path, *, check_unlisted: bool = True) -> list[str]:
    """``verify_raw_files`` for a record already written to disk."""
    raw_path, raw_files = parse_raw_section(path.read_text())
    if not raw_path:
        return [f"{path.name}: no raw.path in frontmatter"]
    if not raw_files:
        return [f"{path.name}: raw.files lists no files"]
    return verify_raw_files(repo_root / raw_path, raw_files, check_unlisted=check_unlisted)
