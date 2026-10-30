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
import json
import platform
import re
import statistics
import subprocess
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Callable

from . import pdk_models, runner, startup
from .corners import PvtPoint
from .pdk import Pdk
from .pdk_models import ModelManifest
from .runner import RunResult
from .testbench import MANIFEST_SNAPSHOT_NAME as _MANIFEST_SNAPSHOT_NAME
from .testbench import Testbench, write_input_snapshots

RECORDS_DIRNAME = "records"
RAW_DIRNAME = "raw"

#: Analysis types whose records carry the transient-noise reproduction scope
#: (#574, DR-0031). Only ``tran-noise``: the replay limit was measured for
#: ``trnoise`` sources, and is not assigned to deterministic or Monte Carlo
#: records.
TRNOISE_REPLAY_ANALYSIS_TYPES = ("tran-noise",)
#: The experiment that measured it and the decision record that adopts it.
TRNOISE_REPLAY_EVIDENCE = "sim/tool-experiments/2026-10-11-ngspice-trnoise-seed-replay/"
TRNOISE_REPLAY_DECISION = "DR-0031-transient-noise-reproducibility"


def reproduction_scope(analysis_type: str) -> dict | None:
    """What re-running a record of ``analysis_type`` reproduces, or ``None``
    when no limit has been measured for that type.

    For ``tran-noise`` the recorded seeds replay the deck and configuration
    (and every seeded non-``trnoise`` draw) but not the ``trnoise``
    waveforms: on the measured ngspice-46 build no seed or start-up control
    reproduced them across processes.
    """
    if analysis_type not in TRNOISE_REPLAY_ANALYSIS_TYPES:
        return None
    return {
        "scope": "deck-and-configuration",
        "trnoise_waveform_replay": False,
        "basis": TRNOISE_REPLAY_EVIDENCE,
        "decision": TRNOISE_REPLAY_DECISION,
    }


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


def git_blob_sha1(data: bytes) -> str:
    """Git blob SHA of ``data`` (what ``git hash-object`` yields), no subprocess."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def sha256_file(path: Path) -> str:
    """Bare-hex SHA-256 of ``path``, streamed in 1 MiB chunks (bounded memory)."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


#: Name of the per-record copy of the loaded ``tb.json`` kept in the raw dir.
MANIFEST_SNAPSHOT_NAME = _MANIFEST_SNAPSHOT_NAME


def _write_idempotent(path: Path, data: bytes) -> None:
    """Write ``data`` to ``path``; identical existing bytes are a no-op.

    Different existing bytes raise ``RuntimeError`` and are left untouched.
    """
    if path.exists():
        if path.read_bytes() != data:
            raise RuntimeError(
                f"{path}: refusing to overwrite an existing file with different content"
            )
        return
    path.write_bytes(data)


def snapshot_manifest(tb: Testbench, raw_dir: Path) -> tuple[str, str] | None:
    """Write the manifest bytes ``tb`` was loaded from into ``raw_dir``.

    Returns ``(file name, sha256)`` or ``None`` if ``tb`` carries no loaded
    bytes. Uses the bytes captured at load time, never the file's current
    content, so a manifest edited after loading cannot leak into the record.
    """
    if tb.manifest_bytes is None:
        return None
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / MANIFEST_SNAPSHOT_NAME
    _write_idempotent(path, tb.manifest_bytes)
    return MANIFEST_SNAPSHOT_NAME, sha256_file(path)


def allocate_record_stems(
    records_dir: Path, date: str, slug: str, count: int, lock_root: Path | None = None
) -> list[str]:
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
    if lock_root is not None and lock_root.is_dir():
        candidates += [p for p in lock_root.glob(f"{prefix}*") if p.is_dir()]
    for path in candidates:
        suffix = path.stem[len(prefix):]
        if suffix.isdigit():
            max_n = max(max_n, int(suffix))
    return [f"{prefix}{max_n + i:02d}" for i in range(1, count + 1)]


def allocate_record_stem(records_dir: Path, date: str, slug: str) -> str:
    """Mint the next unused ``<date>-<slug>-<nn>`` stem."""
    return allocate_record_stems(records_dir, date, slug, 1)[0]


def reserve_record_stems(
    records_dir: Path, date: str, slug: str, count: int, lock_root: Path | None = None
) -> list[str]:
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

    ``lock_root`` moves the lock out of ``records/raw/`` for stored evidence
    (``evidence_store``): ``<lock_root>/<stem>/`` is then the claim *and* the
    staging directory, and no ``records/raw/<stem>/`` is ever created.
    """
    prefix = f"{date}-{slug}-"
    raw_root = lock_root if lock_root is not None else records_dir / RAW_DIRNAME
    raw_root.mkdir(parents=True, exist_ok=True)
    start = allocate_record_stems(records_dir, date, slug, 1, lock_root)[0]
    n = int(start[len(prefix):])
    stems: list[str] = []
    while len(stems) < count:
        stem = f"{prefix}{n:02d}"
        n += 1
        if (records_dir / f"{stem}.md").exists() or (records_dir / RAW_DIRNAME / stem).exists():
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
    """Reserve a record stem, hand its raw directory to ``render``, and
    publish the markdown text it returns as ``records/<stem>.md``.

    This is the "reserve -> write artifacts -> publish markdown" skeleton
    shared by the callback-based behavioral writers (``sim/tb/*/run_*.py``):
    ``render(stem, raw_dir)`` does the testbench-specific work (writing raw
    artifact files under ``raw_dir``, hashing them into a ``raw_files``
    list, and rendering the frontmatter/body), and this function owns the
    bookkeeping around it. Kept separate from ``write_record`` above, which
    serves the ``build_record``/``render_record`` pipeline used by
    ``sim/run_corners.py`` and takes an already-built record dict rather
    than a render callback.

    Guarantees for callback writers (#514):

    * The stem is claimed with ``reserve_record_stems`` -- an atomic
      ``mkdir`` of ``raw/<stem>/`` -- *before* ``render`` runs, so two
      concurrent invocations for the same date and slug always receive
      distinct stems and disjoint raw directories. ``render`` is handed a
      directory that already exists, is empty, and belongs to this call
      alone; it must write only inside it.
    * If ``render`` raises, the exception propagates and the reserved raw
      directory (with whatever ``render`` had written so far) is left in
      place. The stem stays occupied, so a later invocation mints the next
      number instead of reusing a directory holding a failed attempt's
      partial output -- the same policy as ``sim/run_corners.py``.
    * The markdown is published with exclusive creation (``open(..., "x")``),
      so an existing ``records/<stem>.md`` is never overwritten, even one
      that appeared between reservation and publication. That collision
      raises ``RecordExists``; the raw directory is kept.
    """
    stem = reserve_record_stems(records_dir, date, slug, 1)[0]
    raw_dir = records_dir / RAW_DIRNAME / stem
    text = render(stem, raw_dir)
    return publish_record_text(records_dir / f"{stem}.md", text)


BEHAVIORAL_PDK = (
    "n/a (behavioral-level record -- no device models are instantiated, per DR-0009)"
)
BEHAVIORAL_NGSPICE = "n/a (behavioral-level record -- ngspice is not invoked)"
BEHAVIORAL_PROCESS = (
    "n/a (behavioral-level record -- no device models, so no process corner "
    "exists; DR-0009 forbids citing this record for any P/V/T-dependent claim)"
)


def behavioral_frontmatter(
    *,
    stem: str,
    git: dict,
    raw_files,
    repo_root: Path,
    testbench: str,
    netlist: str,
    netlist_note: list[str],
    analysis_type: str,
    tstop: str,
    noise_params: str,
    seeds: str,
    wall_time: str,
    sections: list[list[str]] = (),
    level_suffix: str = "",
    pre_commit_sections: list[list[str]] = (),
    tool_extra: list[str] = (),
    pdk: str = BEHAVIORAL_PDK,
    ngspice: str = BEHAVIORAL_NGSPICE,
    process: str = BEHAVIORAL_PROCESS,
) -> str:
    """Render the frontmatter of a behavioral-level (DR-0009) record.

    The record skeleton shared by the ``sim/tb/*`` behavioral runners: the
    ``record``/``date``/``status`` header, the DR-0009 ``level`` line, the
    ``testbench``/``netlist`` blob SHAs, ``repo_commit``, the ``n/a``
    device-model fields (``pdk``, ``tool.ngspice``, ``corner.*``,
    ``analysis.tstep``/``tmax``), the python/platform lines, and the
    trailing ``raw`` checksum list. Each runner passes only what differs.

    ``testbench`` and ``netlist`` are repo-relative paths whose blob SHAs are
    hashed here. ``netlist_note`` is the folded ``note: >-`` body, one entry
    per line (already unindented). ``tstop``, ``noise_params`` and ``seeds``
    are the text following their keys. ``sections`` are the runner-specific
    blocks (``source_model:``, ``interface:`` ...), each a list of lines,
    emitted after ``analysis`` and separated by blank lines;
    ``pre_commit_sections`` are blocks emitted between ``netlist`` and
    ``repo_commit``. ``tool_extra`` lines go between ``python`` and
    ``platform``. ``pdk``, ``ngspice`` and ``process`` override the default
    ``n/a`` wording for a runner whose text legitimately differs.
    ``wall_time`` is the pre-formatted ``wall_time`` value.
    """
    now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "---",
        f"record: {stem}",
        f"date: {now}",
        "status: valid",
        "",
        "level: behavioral (see spec/decision-records/"
        "DR-0009-behavioral-vs-transistor-verification-split.md)" + level_suffix,
        "",
        "testbench:",
        f"  path: {testbench}",
        f"  sha: {blob_sha(repo_root, repo_root / testbench)}",
        "netlist:",
        f"  path: {netlist}",
        f"  sha: {blob_sha(repo_root, repo_root / netlist)}",
        "  note: >-",
        *[f"    {n}" for n in netlist_note],
    ]
    for block in pre_commit_sections:
        lines += ["", *block]
    if pre_commit_sections:
        lines.append("")
    lines += [
        f"repo_commit: {repo_commit_field(git)}",
        "",
        f"pdk: {pdk}",
        "pdk.models:",
        "  - n/a (behavioral-level record)",
        "",
        "tool:",
        f'  ngspice: "{ngspice}"',
        f'  python: "{platform.python_version()} ({platform.python_implementation()})"',
        *tool_extra,
        f"  platform: {platform.platform()}",
        "",
        "corner:",
        f"  process: {process}",
        "  voltage: n/a (behavioral-level record)",
        "  temperature: n/a (behavioral-level record)",
        "",
        "analysis:",
        f"  type: {analysis_type}",
        f"  tstop: {tstop}",
        "  tstep: n/a",
        "  tmax: n/a",
        f"  noise_params: {noise_params}",
        "  runs: 1",
        f"seeds: {seeds}",
    ]
    for block in sections:
        lines += ["", *block]
    lines += ["", "raw:", f"  path: sim/records/raw/{stem}/", "  files:"]
    for name, digest in raw_files:
        lines.append(f"    - {name}  sha256:{digest}")
    lines.append(f"wall_time: {wall_time}")
    lines.append("---")
    return "\n".join(lines)


def publish_record_text(path: Path, text: str) -> Path:
    """Create ``path`` holding ``text``; never replace an existing file.

    Exclusive creation (``O_CREAT | O_EXCL``) makes the existence check and
    the write one atomic step, so there is no window in which another
    writer's record could be clobbered. Raises ``RecordExists`` if ``path``
    is already present. If the write itself fails after creation, the
    partial file -- which this call alone created -- is removed so it
    cannot be mistaken for a record.
    """
    try:
        handle = open(path, "x")
    except FileExistsError:
        raise RecordExists(
            f"{path} already exists; records are append-only -- mint a new record stem"
        ) from None
    try:
        with handle:
            handle.write(text)
    except BaseException:
        path.unlink(missing_ok=True)
        raise
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


def _startup_lines(record: dict) -> list[str]:
    """Additive ``tool`` lines for the ngspice start-up policy; absent for
    records built without it (older callers, hand-built dicts)."""
    meta = record.get("tool_ngspice_startup")
    if not meta:
        return []
    return [
        f"  ngspice_startup: {_yaml_str(meta['policy'])}",
        f"  ngspice_startup_flags: {_yaml_str(meta['flags'])}",
        f"  ngspice_startup_spinit: {_yaml_str(meta['spinit'])}",
        f"  ngspice_startup_spinit_sha256: {meta['spinit_sha256']}",
        *(
            [f"  ngspice_startup_spinit_snapshot: {_yaml_str(meta['spinit_snapshot'])}"]
            if meta.get("spinit_snapshot")
            else []
        ),
    ]


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
    model_manifest: ModelManifest | None = None,
    startup_snapshot: startup.Snapshot | None = None,
    stored_manifest: str = "",
) -> dict:
    """Assemble every field sim/README.md's frontmatter requires for one
    (testbench, PVT point) record.

    ``model_manifest`` is the PDK model-content manifest (#562) captured
    before the run; ``sim/run_corners.py`` passes the pre-run capture after
    re-checking it. When omitted it is computed here from the live PDK.

    ``startup_snapshot`` is the ngspice start-up script captured before the
    invocation's first launch (#582). The record's digest comes from those
    bytes, never from re-reading the checkout, and the copy the runs
    consumed is listed in ``raw.files``. When omitted the legacy metadata
    (live-file digest, no snapshot claim) is emitted.

    ``stored_manifest`` (repo-relative path) marks a stored-evidence record:
    ``raw_dir`` is then the git-ignored staging directory, the frontmatter
    carries a ``stored_evidence`` table instead of a ``raw:`` block, and the
    caller sets ``record["stored_files"]`` from the published manifest before
    the record is written.
    """
    # "status" here is the record's append-only lifecycle state (valid vs.
    # superseded, per sim/README.md), not a pass/fail verdict on the
    # measurement -- a failed simulation is still an honestly recorded fact,
    # surfaced in the "Result" prose section's run-failures list below.
    status = "valid"
    seeds = [r.seed for r in results if r.seed is not None]

    measure_names = list(tb.measure)
    samples: dict[str, list[float]] = {name: [] for name in measure_names}
    # Only status-ok runs feed the primary summaries. A failed run keeps its
    # parsed measurements (runner.run_one retains them for diagnosis), but
    # they are surfaced separately as failed-run diagnostics, never averaged
    # in with successful values.
    for r in results:
        if r.status != "ok":
            continue
        for name in measure_names:
            if name in r.measurements:
                samples[name].append(r.measurements[name])

    raw_files: list[tuple[str, str]] = []
    for r in results:
        for fname in (r.deck_name, r.log_name):
            path = raw_dir / fname
            if path.is_file():
                raw_files.append((fname, sha256_file(path)))

    manifest_snapshot = snapshot_manifest(tb, raw_dir)
    if manifest_snapshot is not None:
        raw_files.append(manifest_snapshot)

    # The SPICE inputs ngspice consumed: the run already materialized them
    # (runner.run_one); this re-checks they still equal the bytes captured at
    # load (raising if a snapshot was mutated mid-run) and lists them.
    input_snapshots = write_input_snapshots(tb, raw_dir)
    raw_files.extend(input_snapshots)
    if startup_snapshot is not None:
        # Re-checked like the SPICE inputs: raises if the copy ngspice read
        # no longer equals the captured bytes.
        raw_files.append(startup.write_snapshot(startup_snapshot, raw_dir))
    if tb.netlist_bytes is not None:
        testbench_sha = git_blob_sha1(tb.netlist_bytes)
        netlist_sha = git_blob_sha1(tb.dut_netlist_bytes)
    else:
        testbench_sha = blob_sha(repo_root, tb.netlist)
        netlist_sha = blob_sha(repo_root, tb.dut_netlist)
    snapshot_digest = dict(input_snapshots)

    # PDK model-content identity (#562): which model files, by PDK-relative
    # path and SHA-256, the deck's .include/.lib entry points reach.
    lib_sections = list(tb.extra_lib_sections or point.corner.sections)
    if model_manifest is None:
        model_manifest = pdk_models.manifest_for_deck(pdk, lib_sections)
    models_path = write_model_manifest(model_manifest, raw_dir)
    models_sha256 = sha256_file(models_path)
    raw_files.append((models_path.name, models_sha256))
    fragment_snapshot = tb.fragment_snapshot_name if input_snapshots else None
    dut_snapshot = tb.dut_snapshot_name if input_snapshots else None

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
        "testbench_sha": testbench_sha,
        "netlist_path": _relpath(repo_root, tb.dut_netlist),
        "netlist_sha": netlist_sha,
        "repo_commit": repo_commit_field(git),
        "pdk": f"{pdk.variant} @ {pdk.version}",
        "pdk_models": [
            f"{pdk.model_lib} (sections: "
            f"{' '.join(tb.extra_lib_sections or point.corner.sections)})"
        ],
        "pdk_content_manifest": models_path.name,
        "pdk_content_sha256": models_sha256,
        "pdk_content_identity": model_manifest.identity,
        "pdk_content_files": len(model_manifest.files),
        "pdk_content_complete": model_manifest.complete,
        "pdk_content_problems": list(model_manifest.problems),
        "tool_ngspice": ngspice,
        "tool_ngspice_startup": startup.metadata(startup_snapshot),
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
        # Additive (#574): absent (None) for analysis types with no measured
        # replay limit, so their records render exactly as before.
        "reproduction": reproduction_scope(tb.analysis_type),
        "raw_path": "" if stored_manifest else _relpath(repo_root, raw_dir) + "/",
        "stored_manifest": stored_manifest,
        "stored_files": [],
        "raw_files": raw_files,
        # Not rendered: kept so the record can be re-verified against the
        # directory it was actually hashed from (see verify_record).
        "raw_dir": raw_dir,
        "wall_time": _fmt_wall(wall_seconds),
        "measure_names": measure_names,
        "samples": samples,
        "runs_attempted": len(results),
        "runs_ok": sum(1 for r in results if r.status == "ok"),
        "results": results,
        "tb_slug": tb.slug,
        "netlist_rel": _relpath(repo_root, tb.dut_netlist),
        "manifest_rel": _relpath(repo_root, tb.manifest_path),
        "manifest_snapshot": manifest_snapshot[0] if manifest_snapshot else "",
        "manifest_sha256": manifest_snapshot[1] if manifest_snapshot else "",
        "manifest_sha": git_blob_sha1(tb.manifest_bytes) if manifest_snapshot else "",
        "testbench_snapshot": fragment_snapshot or "",
        "testbench_sha256": snapshot_digest.get(fragment_snapshot, ""),
        "netlist_snapshot": dut_snapshot or "",
        "netlist_sha256": snapshot_digest.get(dut_snapshot, ""),
        "netlist_dependencies": [name for name, _ in tb.design_dependencies],
    }


def write_model_manifest(manifest: ModelManifest, raw_dir: Path, name: str = "") -> Path:
    """Write ``manifest`` as ``raw_dir/pdk-models.json`` (or ``name``)."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / (name or pdk_models.MANIFEST_NAME)
    _write_idempotent(path, manifest.to_json_bytes())
    return path


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
    ]
    # Additive: records predating the manifest snapshot (#510) have no
    # ``manifest:`` block and stay valid as they are.
    if record.get("manifest_sha256"):
        lines += [
            "manifest:",
            f"  path: {record['manifest_rel']}",
            f"  sha: {record['manifest_sha']}",
            f"  snapshot: {record['manifest_snapshot']}",
            f"  sha256: {record['manifest_sha256']}",
        ]
    # Additive: records predating the SPICE-input snapshots (#515) have no
    # ``inputs:`` block and stay valid as they are.
    if record.get("testbench_sha256"):
        lines += [
            "inputs:",
            f"  testbench_snapshot: {record['testbench_snapshot']}",
            f"  testbench_sha256: {record['testbench_sha256']}",
            f"  netlist_snapshot: {record['netlist_snapshot']}",
            f"  netlist_sha256: {record['netlist_sha256']}",
        ]
        if record.get("netlist_dependencies"):
            lines.append(
                f"  netlist_dependencies: {', '.join(record['netlist_dependencies'])}"
            )
    lines += [
        "",
        f"pdk: {_yaml_str(record['pdk'])}",
        "pdk.models:",
    ]
    for entry in record["pdk_models"]:
        lines.append(f"  - {entry}")
    # Additive: records predating the model-content manifest (#562) have no
    # ``pdk_content:`` block and stay valid as they are.
    if record.get("pdk_content_sha256"):
        lines += [
            "pdk_content:",
            f"  manifest_file: {record['pdk_content_manifest']}",
            f"  sha256: {record['pdk_content_sha256']}",
            f"  identity: {record['pdk_content_identity']}",
            f"  file_count: {record['pdk_content_files']}",
            f"  complete: {'true' if record['pdk_content_complete'] else 'false'}",
            f"  problems: {len(record.get('pdk_content_problems') or [])}",
        ]
    lines += [
        "",
        "tool:",
        f"  ngspice: {_yaml_str(record['tool_ngspice'])}",
        *_startup_lines(record),
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
    # Additive (#574, DR-0031): only tran-noise records carry it; records
    # without the block (older ones, other analysis types) stay valid.
    reproduction = record.get("reproduction")
    if reproduction:
        lines += [
            "reproduction:",
            f"  scope: {reproduction['scope']}",
            "  trnoise_waveform_replay: "
            f"{'true' if reproduction['trnoise_waveform_replay'] else 'false'}",
            f"  basis: {reproduction['basis']}",
            f"  decision: {reproduction['decision']}",
        ]
    if record.get("stored_manifest"):
        lines += ["", "stored_evidence:", f"  manifest: {record['stored_manifest']}", "  files:"]
        for fname, size, digest in record["stored_files"]:
            lines.append(f"    - {fname}  size:{size}  sha256:{digest}")
    else:
        lines += ["", "raw:", f"  path: {record['raw_path']}", "  files:"]
        for fname, digest in record["raw_files"]:
            lines.append(f"    - {fname}  sha256:{digest}")
    lines += [
        f"wall_time: {record['wall_time']}",
        "---",
        "",
    ]
    return "\n".join(lines)


def render_result_section(record: dict) -> str:
    """Render the "Result" prose.

    Primary measurement lines summarize status-ok runs only. Measurements a
    failed run happened to retain are listed afterward under an explicit
    "Failed-run diagnostics" heading with the failure reason, and are never
    folded into the means above.
    """
    results = record["results"]
    attempted = record.get("runs_attempted", len(results))
    ok = record.get("runs_ok", sum(1 for r in results if r.status == "ok"))
    lines = ["## Result", ""]
    for name in record["measure_names"]:
        values = record["samples"][name]
        if not values:
            lines.append(
                f"- `{name}`: no successful-run data "
                f"({ok} of {attempted} runs succeeded)"
            )
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
    lines.append("")
    lines.append(
        f"Runs: {ok} of {attempted} successful. Summaries above use "
        "successful runs only."
    )
    failed = [r for r in results if r.status != "ok"]
    if failed:
        lines.append("")
        lines.append(
            "Run failures (nonzero exit, simulator error or analysis error, "
            "missing or non-finite measurements, or timeout):"
        )
        for r in failed:
            lines.append(f"- seed {r.seed}: {r.status} -- {r.message}")
        retained = [r for r in failed if r.measurements]
        if retained:
            lines.append("")
            lines.append(
                "Failed-run diagnostics (values parsed from runs that did not "
                "succeed; NOT included in the summaries above, not evidence "
                "about the device):"
            )
            for r in retained:
                lines.append(f"- seed {r.seed} ({r.status}: {r.message}):")
                for name, value in r.measurements.items():
                    lines.append(f"  - `{name}`: {_fmt(value)}")
    lines.append("")
    lines.append("Numbers only. No entropy-rate or spec-compliance claim is made by this record.")
    lines.append("")
    return "\n".join(lines)


def _where(record: dict, name: str) -> str:
    """Markdown naming where a raw artifact of ``record`` lives."""
    if record.get("stored_manifest"):
        return f"`{name}` in the stored evidence (`{record['stored_manifest']}`)"
    return f"`{record['raw_path']}{name}`"


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
    reproduction = record.get("reproduction")
    if reproduction and not reproduction["trnoise_waveform_replay"]:
        lines += [
            "These commands replay the deck and configuration with the recorded "
            "seed(s). The seeds fix the netlist-parameter and control-language "
            "random draws, but they do not reproduce the `trnoise` transient-noise "
            "waveforms: on the ngspice-46 build measured in "
            f"`{reproduction['basis']}` no seed or start-up control made them "
            "repeat across simulator processes, so a re-run draws a fresh noise "
            "realization and its measured values will differ from the ones "
            "above. Exact waveform replay is not claimed. Agreement between a "
            "re-run and this record is a statistical claim that needs its own "
            "tolerance and evidence; this record does not demonstrate it. See "
            f"`spec/decision-records/{reproduction['decision']}.md`.",
            "",
        ]
    if record.get("manifest_sha256"):
        lines += [
            f"The manifest used is snapshotted as {_where(record, record['manifest_snapshot'])}"
            f" (sha256 `{record['manifest_sha256']}`). "
            f"The commands above read the CURRENT `{record['manifest_rel']}`; check "
            "out `repo_commit` and, if the snapshot differs from the tree "
            "(`diff`), restore the snapshot over it before re-running. See "
            "`sim/README.md`.",
            "",
        ]
    if record.get("testbench_sha256"):
        lines += [
            f"The SPICE inputs ngspice consumed are snapshotted next to the decks as "
            f"{_where(record, record['testbench_snapshot'])} and "
            f"{_where(record, record['netlist_snapshot'])} (the decks include "
            "these copies, not the working-tree files). `testbench.sha`/`netlist.sha` "
            "hash those same bytes; if they differ from the tree at `repo_commit`, "
            "the run used dirty-tree input -- restore the snapshots over the "
            "originals (in a scratch worktree) before re-running. See `sim/README.md`.",
            "",
        ]
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

    The early existence check gives a fast ``RecordExists`` that takes
    precedence over a raw-file mismatch, but it is not the authority: the
    rendered Markdown is published through ``publish_record_text``, whose
    exclusive creation refuses a destination that appeared after the check
    and removes its own partial file if the write fails.
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
    text = render_record(record, tb, caveats)
    return publish_record_text(path, text)


RAW_FILE_LINE = re.compile(r"^\s*-\s+(?P<name>\S+)\s+sha256:(?P<digest>[0-9a-f]{64})\s*$")


class RawSectionError(ValueError):
    """A record's frontmatter ``raw`` provenance is malformed or ambiguous."""


def parse_raw_section(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Read ``raw.path`` and ``raw.files`` back out of a rendered record.

    Deliberately a small line scanner over the shape ``render_frontmatter``
    emits, not a YAML parse: the harness is stdlib-only (see README.md), and
    this is the inverse of exactly one renderer.

    Strict about that shape: only the initial ``---`` ... ``---`` frontmatter
    block is read (a ``raw:`` example in the Markdown body is ignored), and
    anything malformed raises ``RawSectionError`` rather than yielding a
    parsed prefix: an unterminated frontmatter block, a duplicate ``raw:`` /
    ``path:`` / ``files:`` declaration, an unknown line inside ``raw:``, or a
    file entry that is not ``- <name>  sha256:<64 hex>``. A record with no
    ``raw:`` section at all returns ``("", [])``.
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return "", []
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise RawSectionError(
            "frontmatter is not terminated by a closing '---' line"
        ) from None
    front = lines[1:end]

    raw_path = ""
    files: list[tuple[str, str]] = []
    seen_raw = seen_path = seen_files = False
    i = 0
    while i < len(front):
        line = front[i]
        i += 1
        if line.rstrip() != "raw:":
            if line.startswith("raw:"):
                raise RawSectionError(f"unsupported raw declaration: {line!r}")
            continue
        if seen_raw:
            raise RawSectionError("duplicate 'raw:' declaration in frontmatter")
        seen_raw = True
        while i < len(front) and front[i][:1] in (" ", "\t"):
            line = front[i]
            i += 1
            if not line.strip():
                continue
            if line.startswith("  path:") and not line.startswith("   "):
                if seen_path:
                    raise RawSectionError("duplicate 'raw.path' declaration")
                seen_path = True
                raw_path = line.split(":", 1)[1].strip()
            elif line.rstrip() == "  files:":
                if seen_files:
                    raise RawSectionError("duplicate 'raw.files' declaration")
                seen_files = True
                while i < len(front) and front[i][:1] in (" ", "\t"):
                    entry = front[i]
                    i += 1
                    match = RAW_FILE_LINE.match(entry)
                    if not match:
                        raise RawSectionError(
                            f"malformed raw.files entry (want '- <name>  "
                            f"sha256:<64 hex>'): {entry.strip()!r}"
                        )
                    files.append((match.group("name"), match.group("digest")))
            else:
                raise RawSectionError(f"unexpected line inside raw: {line.strip()!r}")
    return raw_path, files


STORED_FILE_LINE = re.compile(
    r"^\s*-\s+(?P<name>\S+)\s+size:(?P<size>\d+)\s+sha256:(?P<digest>[0-9a-f]{64})\s*$"
)


def parse_stored_section(text: str) -> tuple[str, list[tuple[str, int, str]]] | None:
    """Read ``stored_evidence`` (manifest path and table) out of a record.

    ``None`` means the record has no such block (a legacy ``raw:`` record).
    Same strictness as ``parse_raw_section``: only the initial frontmatter is
    read and anything malformed raises ``RawSectionError``.
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise RawSectionError("frontmatter is not terminated by a closing '---' line") from None
    front = lines[1:end]
    manifest = ""
    files: list[tuple[str, int, str]] = []
    found = False
    i = 0
    while i < len(front):
        line = front[i]
        i += 1
        if line.rstrip() != "stored_evidence:":
            if line.startswith("stored_evidence:"):
                raise RawSectionError(f"unsupported stored_evidence declaration: {line!r}")
            continue
        if found:
            raise RawSectionError("duplicate 'stored_evidence:' declaration in frontmatter")
        found = True
        seen_manifest = seen_files = False
        while i < len(front) and front[i][:1] in (" ", "\t"):
            line = front[i]
            i += 1
            if not line.strip():
                continue
            if line.startswith("  manifest:") and not line.startswith("   "):
                if seen_manifest:
                    raise RawSectionError("duplicate 'stored_evidence.manifest' declaration")
                seen_manifest = True
                manifest = line.split(":", 1)[1].strip()
            elif line.rstrip() == "  files:":
                if seen_files:
                    raise RawSectionError("duplicate 'stored_evidence.files' declaration")
                seen_files = True
                while i < len(front) and front[i][:1] in (" ", "\t"):
                    entry = front[i]
                    i += 1
                    match = STORED_FILE_LINE.match(entry)
                    if not match:
                        raise RawSectionError(
                            "malformed stored_evidence.files entry (want '- <name>  "
                            f"size:<bytes>  sha256:<64 hex>'): {entry.strip()!r}"
                        )
                    files.append(
                        (match.group("name"), int(match.group("size")), match.group("digest"))
                    )
            else:
                raise RawSectionError(
                    f"unexpected line inside stored_evidence: {line.strip()!r}"
                )
    return (manifest, files) if found else None


def verify_stored_record(path: Path, repo_root: Path, stored: tuple[str, list[tuple[str, int, str]]],
                         text: str) -> list[str]:
    """Check a stored-evidence record against its committed manifest.

    The table must equal the manifest's entries (name, size, sha256); the
    manifest must be ``manifests/artifacts/<stem>.manifest.json`` and well
    formed; the record must carry no ``raw:`` block and have no
    ``sim/records/raw/<stem>/`` directory beside it. The stored bytes are not
    re-hashed here; ``klt artifact verify <manifest>`` does that on a fleet
    worker, against the store.
    """
    from . import evidence_store  # local: keeps report importable on its own

    manifest_rel, table = stored
    stem = path.stem
    expected_rel = f"{evidence_store.MANIFEST_SUBDIR}/{stem}{evidence_store.MANIFEST_SUFFIX}"
    problems: list[str] = []
    if manifest_rel != expected_rel:
        problems.append(f"stored_evidence.manifest {manifest_rel!r} != {expected_rel!r}")
    if not table:
        problems.append("stored_evidence.files lists no files")
    names = [n for n, _s, _d in table]
    if len(set(names)) != len(names):
        problems.append("stored_evidence.files names a file twice")
    try:
        raw_path, _raw_files = parse_raw_section(text)
    except RawSectionError:
        raw_path = "x"
    if raw_path:
        problems.append("stored record also has a raw: block")
    raw_dir = path.resolve().parent / RAW_DIRNAME / stem
    if raw_dir.exists():
        problems.append(f"stored record has a raw directory beside it: {raw_dir}")
    data, schema = evidence_store.load_manifest(repo_root / expected_rel)
    problems += [f"manifest: {p}" for p in schema]
    if data is not None:
        manifest_table = evidence_store.manifest_table(data)
        if manifest_table != sorted(table):
            mine, theirs = set(table), set(manifest_table)
            for row in sorted(mine - theirs):
                problems.append(f"table row {row!r} is not in the manifest")
            for row in sorted(theirs - mine):
                problems.append(f"manifest entry {row!r} is not in the table")
    listed = [(n, d) for n, _s, d in table]
    problems += verify_manifest_reference(text, listed)
    problems += verify_inputs_reference(text, listed)
    problems += verify_pdk_content_reference(text, listed, None)
    problems += verify_startup_reference(text, listed)
    return problems


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


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def validate_raw_artifacts(
    repo_root: Path, raw_root: Path, raw_path: str, raw_files: list[tuple[str, str]]
) -> tuple[Path | None, list[tuple[str, Path]], list[str]]:
    """Check a record's declared artifacts live inside its raw directory.

    ``raw_path`` must be repository-relative (no absolute form, no ``..``)
    and resolve strictly inside ``raw_root`` (the evidence raw root, itself
    inside ``repo_root``). Each ``raw_files`` name must be a simple file name
    and, after resolving symlinks, stay inside the raw directory. Returns
    ``(raw_dir, [(name, path)], problems)``; when ``problems`` is non-empty
    nothing may be read or hashed. Pure path logic: never opens a file.
    """
    pure = PurePosixPath(raw_path)
    if not raw_path or "\\" in raw_path or pure.is_absolute() or PureWindowsPath(raw_path).drive:
        return None, [], [f"raw.path {raw_path!r} must be a repository-relative path"]
    if ".." in pure.parts:
        return None, [], [f"raw.path {raw_path!r} must not contain '..'"]
    root = repo_root.resolve()
    base = raw_root.resolve()
    raw_dir = repo_root / raw_path
    resolved = raw_dir.resolve()
    if not _is_within(resolved, root):
        return None, [], [f"raw.path {raw_path!r} resolves outside the repository"]
    if resolved == base or not _is_within(resolved, base):
        return None, [], [
            f"raw.path {raw_path!r} resolves outside the evidence raw root "
            f"{base.relative_to(root) if _is_within(base, root) else base}"
        ]
    problems: list[str] = []
    artifacts: list[tuple[str, Path]] = []
    for name, _digest in raw_files:
        if name in (".", "..") or "/" in name or "\\" in name or PureWindowsPath(name).drive:
            problems.append(f"raw.files name {name!r} must be a simple file name")
            continue
        candidate = raw_dir / name
        if not _is_within(candidate.resolve(), resolved):
            problems.append(f"raw.files name {name!r} resolves outside the raw directory")
            continue
        artifacts.append((name, candidate))
    return raw_dir, artifacts, problems


def verify_record_file(path: Path, repo_root: Path, *, check_unlisted: bool = True) -> list[str]:
    """``verify_raw_files`` for a record already written to disk."""
    try:
        text = path.read_text()
        stored = parse_stored_section(text)
        raw_path, raw_files = parse_raw_section(text)
    except RawSectionError as exc:
        return [f"{path.name}: malformed raw provenance: {exc}"]
    if stored is not None:
        return [f"{path.name}: {p}" for p in verify_stored_record(path, repo_root, stored, text)]
    if not raw_path:
        return [f"{path.name}: no raw.path in frontmatter"]
    if not raw_files:
        return [f"{path.name}: raw.files lists no files"]
    raw_dir, _artifacts, bad = validate_raw_artifacts(
        repo_root, path.resolve().parent / RAW_DIRNAME, raw_path, raw_files
    )
    if bad or raw_dir is None:
        return [f"{path.name}: invalid raw provenance: {p}" for p in bad]
    problems = verify_raw_files(raw_dir, raw_files, check_unlisted=check_unlisted)
    problems += verify_manifest_reference(text, raw_files)
    problems += verify_inputs_reference(text, raw_files)
    problems += verify_pdk_content_reference(text, raw_files, raw_dir)
    problems += verify_startup_reference(text, raw_files)
    return problems


def parse_manifest_section(text: str) -> dict[str, str]:
    """Read the optional top-level ``manifest:`` block (empty if absent)."""
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return {}
    front = lines[1:lines.index("---", 1)]
    out: dict[str, str] = {}
    in_block = False
    for line in front:
        if line.rstrip() == "manifest:":
            in_block = True
            continue
        if in_block:
            if line[:1] not in (" ", "\t"):
                break
            key, _, value = line.strip().partition(":")
            out[key] = value.strip()
    return out


def verify_manifest_reference(text: str, raw_files: list[tuple[str, str]]) -> list[str]:
    """The ``manifest.sha256`` a record declares must match its raw.files entry.

    (The snapshot's bytes themselves are covered by the raw.files re-hash.)
    Legacy records without a ``manifest:`` block yield no problems.
    """
    ref = parse_manifest_section(text)
    if not ref:
        return []
    listed = dict(raw_files)
    name, digest = ref.get("snapshot", ""), ref.get("sha256", "")
    if not name or name not in listed:
        return [f"manifest.snapshot {name!r} is not listed in raw.files"]
    if listed[name] != digest.removeprefix("sha256:"):
        return [f"manifest.sha256 {digest} != {listed[name]} recorded for {name} in raw.files"]
    return []


def parse_inputs_section(text: str) -> dict[str, str]:
    """Read the optional top-level ``inputs:`` block (empty if absent)."""
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return {}
    front = lines[1:lines.index("---", 1)]
    out: dict[str, str] = {}
    in_block = False
    for line in front:
        if line.rstrip() == "inputs:":
            in_block = True
            continue
        if in_block:
            if line[:1] not in (" ", "\t"):
                break
            key, _, value = line.strip().partition(":")
            out[key] = value.strip()
    return out


def verify_inputs_reference(text: str, raw_files: list[tuple[str, str]]) -> list[str]:
    """Each SPICE-input digest a record declares must match its raw.files entry.

    Legacy records without an ``inputs:`` block yield no problems.
    """
    ref = parse_inputs_section(text)
    if not ref:
        return []
    listed = dict(raw_files)
    problems: list[str] = []
    for role in ("testbench", "netlist"):
        name = ref.get(f"{role}_snapshot", "")
        digest = ref.get(f"{role}_sha256", "")
        if not name or name not in listed:
            problems.append(f"inputs.{role}_snapshot {name!r} is not listed in raw.files")
        elif listed[name] != digest.removeprefix("sha256:"):
            problems.append(
                f"inputs.{role}_sha256 {digest} != {listed[name]} recorded for {name} in raw.files"
            )
    for dep in [d.strip() for d in ref.get("netlist_dependencies", "").split(",") if d.strip()]:
        if dep not in listed:
            problems.append(f"inputs.netlist_dependencies {dep!r} is not listed in raw.files")
    return problems


def parse_pdk_content_section(text: str) -> dict[str, str]:
    """Read the optional top-level ``pdk_content:`` block (empty if absent)."""
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return {}
    front = lines[1:lines.index("---", 1)]
    out: dict[str, str] = {}
    in_block = False
    for line in front:
        if line.rstrip() == "pdk_content:":
            in_block = True
            continue
        if in_block:
            if line[:1] not in (" ", "\t"):
                break
            key, _, value = line.strip().partition(":")
            out[key] = value.strip()
    return out


def verify_pdk_content_reference(
    text: str, raw_files: list[tuple[str, str]], raw_dir: Path | None = None
) -> list[str]:
    """The ``pdk_content`` block must agree with its manifest in raw.files.

    The manifest's bytes are covered by the raw.files re-hash; this checks
    the block names a listed file with the listed digest and -- when the raw
    directory is available -- that the identity, file count and completeness
    it declares are the ones recomputed from that manifest. Legacy records
    without a ``pdk_content:`` block yield no problems.
    """
    ref = parse_pdk_content_section(text)
    if not ref:
        return []
    listed = dict(raw_files)
    name, digest = ref.get("manifest_file", ""), ref.get("sha256", "")
    if not name or name not in listed:
        return [f"pdk_content.manifest_file {name!r} is not listed in raw.files"]
    if listed[name] != digest.removeprefix("sha256:"):
        return [f"pdk_content.sha256 {digest} != {listed[name]} recorded for {name} in raw.files"]
    if raw_dir is None:
        return []
    path = raw_dir / name
    if not path.is_file() or sha256_file(path) != listed[name]:
        return []  # already reported by the raw.files re-hash
    try:
        doc = json.loads(path.read_text())
    except (ValueError, UnicodeDecodeError) as exc:
        return [f"pdk_content.manifest_file {name} is not valid JSON: {exc}"]
    if not isinstance(doc, dict):
        return [f"pdk_content.manifest_file {name} is not a JSON object"]
    problems: list[str] = []
    identity = pdk_models.identity_from_document(doc)
    if ref.get("identity") != identity or doc.get("identity") != identity:
        problems.append(
            f"pdk_content.identity {ref.get('identity')} does not match {identity} "
            f"recomputed from {name}"
        )
    files = doc.get("files") if isinstance(doc.get("files"), list) else []
    if ref.get("file_count") != str(len(files)):
        problems.append(
            f"pdk_content.file_count {ref.get('file_count')} != {len(files)} listed in {name}"
        )
    doc_problems = doc.get("problems") if isinstance(doc.get("problems"), list) else []
    complete = "true" if not doc_problems else "false"
    if ref.get("complete") != complete or doc.get("complete") is not (complete == "true"):
        problems.append(f"pdk_content.complete {ref.get('complete')} disagrees with {name}")
    return problems


_STARTUP_KEY_PREFIX = "ngspice_startup_"


def parse_startup_section(text: str) -> dict[str, str]:
    """Read the ``ngspice_startup_*`` lines of the frontmatter ``tool:`` block.

    Keys are returned without the prefix (``spinit_sha256``,
    ``spinit_snapshot``, ...). Empty for records without the lines.
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return {}
    front = lines[1:lines.index("---", 1)]
    out: dict[str, str] = {}
    in_block = False
    for line in front:
        if line.rstrip() == "tool:":
            in_block = True
            continue
        if in_block:
            if line[:1] not in (" ", "\t"):
                break
            key, _, value = line.strip().partition(":")
            if key.startswith(_STARTUP_KEY_PREFIX):
                out[key[len(_STARTUP_KEY_PREFIX):]] = value.strip().strip('"')
    return out


def verify_startup_reference(text: str, raw_files: list[tuple[str, str]]) -> list[str]:
    """A declared start-up snapshot must be listed with the declared digest.

    (The snapshot's bytes are covered by the raw.files re-hash.) Records
    without ``ngspice_startup_spinit_snapshot`` -- legacy records and the
    #575 format that hashed the live checkout file -- yield no problems.
    """
    ref = parse_startup_section(text)
    name = ref.get("spinit_snapshot", "")
    if not name:
        return []
    listed = dict(raw_files)
    digest = ref.get("spinit_sha256", "")
    if name not in listed:
        return [f"tool.ngspice_startup_spinit_snapshot {name!r} is not listed in raw.files"]
    if listed[name] != digest.removeprefix("sha256:"):
        return [
            f"tool.ngspice_startup_spinit_sha256 {digest} != {listed[name]} "
            f"recorded for {name} in raw.files"
        ]
    return []
