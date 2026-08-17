#!/usr/bin/env python3
"""Shared `klt` CLI plumbing for every `layout/` driver script.

`layout/verify.py`, `layout/floorplan/floorplan.py`, and each cell/block/ring
`build.py` all drive the `klt` command line the same way: run it with
`--format json`, read stdout-or-stderr, parse the JSON payload, and raise on
an empty run, unparseable output, or an `{"error": ...}` payload. This module
is the one copy of that boilerplate (issue #137 -- it used to be five
independent, near-byte-identical copies, one per caller).

The same five callers also each defined their own `klt_version()` (report
what `klt` is installed) and `normalise_gds()` (zero the BGNLIB/BGNSTR
timestamp fields `klt gen`/`klt gen-compose` stamp into GDSII, so committed
golden artefacts are byte-comparable across runs -- see
`layout/README.md` and klayout-tools#320); those moved in here too
(issue #156), for the same reason `_run_klt`/`FlowError`/`resolve_pdk` did.

`klt_origin()` (what commit a `klt` install was built from -- `klt --version`
alone cannot tell two builds apart, see its own docstring) is added here
rather than only living in `layout/verify.py`'s own copy (issue #143):
`design/synth.py` needs the identical provenance record
`layout/reports/environment.json` already carries, and this module is where
that kind of shared plumbing belongs. `layout/verify.py` keeps its own
existing copy for now -- consolidating that one is unrelated cleanup, not
this issue's scope.

Not a package member of anything else under `layout/` -- it computes its own
`REPO_ROOT` from its own location (`layout/_klt.py` sits directly under
`layout/`, so one `.parent` up is the repo root) rather than importing a
caller's `REPO_ROOT`, so callers keep resolving their own GDS/report paths
exactly as before.
"""

from __future__ import annotations

import json
import shutil
import struct
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

#: GDSII record type codes for BGNLIB/BGNSTR, the two records `klt
#: gen`/`klt gen-compose` stamp wall-clock time into.
_BGNLIB = 0x0102
_BGNSTR = 0x0502

#: Asks the `klt` venv's own interpreter what it installed. `importlib.metadata`
#: only sees distributions on the interpreter running it, and `klt` lives in its
#: own pipx/uv venv, so the question has to be asked over there.
_KLT_ORIGIN_PROBE = (
    "import importlib.metadata as m;"
    "print(m.distribution('klayout-tools').read_text('direct_url.json') or '')"
)


class FlowError(Exception):
    """A tool invocation could not produce a verdict at all."""


def resolve_pdk():
    """Resolve the gf180mcu install through the repo's one PDK resolver.

    `sim/harness/pdk.py` is that resolver (its own docstring: "No PDK path is
    ever hardcoded ... Everything resolves through this module"), so the
    layout flow uses it rather than re-implementing discovery and risking a
    DRC/LVS run against a different PDK install than the simulations cite.
    Returns None when no install is found.
    """
    try:
        from sim.harness import pdk as pdk_mod
    except ImportError:  # pragma: no cover - repo layout guarantees this
        return None
    try:
        return pdk_mod.find_pdk()
    except Exception:
        return None


def _run_klt(args: list[str], timeout_s: int = 600) -> dict:
    """Run `klt <args> --format json` from the repo root and parse stdout.

    Every path handed to `klt` is repo-root-relative and the working
    directory is the repo root, so the paths echoed back into the reports
    are stable across machines. `timeout_s` defaults to 600 (the value every
    caller but `layout/floorplan/floorplan.py` used); that caller passes 900
    explicitly, since its own `gen-compose` invocations run over more
    geometry than a single cell/block/ring build.
    """
    argv = ["klt", *args, "--format", "json"]
    done = subprocess.run(
        argv, capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=timeout_s
    )
    # klt writes its success payload to stdout and its `{"error": ...}`
    # payload to stderr, so both streams have to be considered before
    # concluding a run produced nothing at all.
    raw = done.stdout.strip() or done.stderr.strip()
    if not raw:
        raise FlowError(
            f"`{' '.join(argv)}` produced no output (exit {done.returncode})"
        )
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FlowError(f"`{' '.join(argv)}` emitted unparseable JSON: {exc}") from exc
    if "error" in payload:
        raise FlowError(f"`{' '.join(argv)}` failed: {payload['error'].get('message')}")
    return payload


def klt_version() -> str | None:
    """Return the installed `klt --version` string, or None if absent."""
    if shutil.which("klt") is None:
        return None
    try:
        done = subprocess.run(
            ["klt", "--version"], capture_output=True, text=True, timeout=60
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return (done.stdout or done.stderr).strip() or None


def klt_origin() -> dict | None:
    """Return what a `klt` install was built from, or None if unknowable.

    `klt --version` reports `0.1.0` for every build of klayout-tools to date,
    including installs straight off the tip of its main branch -- which is
    what `pipx install klayout-tools` / `uv tool install klayout-tools` from
    the repository URL gives you. So the version string does not identify a
    build, and on 2026-08-02 two `0.1.0` installs produced different LVS
    reports for the same fixture (#73). The commit does identify it.

    Best effort by construction: an install from a wheel has no upstream
    commit to report, and a layout this does not recognise reports nothing
    rather than guessing. A None here means "not recorded", never "the same
    as last time".
    """
    executable = shutil.which("klt")
    if executable is None:
        return None
    try:
        # The console script's shebang names the interpreter of the venv the
        # distribution is installed into -- the one that can answer.
        script = Path(executable).resolve().read_text(errors="replace")
    except OSError:
        return None
    shebang = script.split("\n", 1)[0]
    if not shebang.startswith("#!"):
        return None
    try:
        done = subprocess.run(
            [shebang[2:].strip(), "-c", _KLT_ORIGIN_PROBE],
            capture_output=True,
            text=True,
            timeout=60,
        )
        record = json.loads(done.stdout.strip())
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return None
    if not isinstance(record, dict):
        return None
    return {
        "url": record.get("url"),
        "commit": (record.get("vcs_info") or {}).get("commit_id"),
    }


def normalise_gds(raw: bytes) -> bytes:
    """Return `raw` with every BGNLIB/BGNSTR timestamp field zeroed."""
    out = bytearray(raw)
    offset = 0
    while offset + 4 <= len(out):
        length, record = struct.unpack_from(">HH", out, offset)
        if length < 4:
            break
        if record in (_BGNLIB, _BGNSTR):
            for index in range(offset + 4, offset + length):
                out[index] = 0
        offset += length
    return bytes(out)
