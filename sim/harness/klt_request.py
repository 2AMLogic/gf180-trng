"""One scaffold for the evidence tools' ``klt sim`` emit/run cycle (issue #590).

``sim/tools/`` evidence producers each used to carry their own copy of "write
the declared request, check it for drift, run it through ``klt sim``", and the
copies diverged on the shared-host rule: only one tool refused to run a whole
grid on the local backend. This module is the single copy the tools share.

The shared-host rule enforced here: a whole declared grid is submitted to the
batch fleet through ``klt sim`` and never swept locally on a shared worker.
The one exception is a tool's single-point debug probe (``single_point=True``).
"""

from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path
from typing import Callable, Iterable


def emit_requests(items: Iterable[tuple[Path, str]], check: bool, *, repo_root: Path,
                  ok: Callable[[], None] | None = None) -> int:
    """Write or drift-check the committed request files of a declared grid.

    ``items`` is one ``(path, text)`` pair per committed request file. In check
    mode every file must exist and equal ``text`` byte-for-byte; each mismatch
    prints the ``DRIFT:`` line and counts. In write mode each file is rewritten
    (its parent directory is created if needed) and ``wrote ...`` is printed.
    ``ok``, when given, is called after a clean check so the tool can print its
    own success line. Returns 0 when clean, 1 when drifted.
    """
    bad = 0
    for path, text in items:
        if check:
            if not path.exists() or path.read_text() != text:
                print(f"DRIFT: {path.relative_to(repo_root)} does not match the declared grid")
                bad += 1
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            print(f"wrote {path.relative_to(repo_root)}")
    if check and not bad and ok is not None:
        ok()
    return 1 if bad else 0


def run_klt_request(outdir: str | Path, stem: str, request: Path, backend: str,
                    klt_cmd: str = "klt", *, single_point: bool = False,
                    probe_hint: str | None = None,
                    cleanup: Callable[[], None] | None = None) -> int:
    """Run one request through ``klt sim`` and capture its artifacts.

    The shared-host rule lives here, once, for every tool: a whole declared
    grid (``single_point=False``) never runs with ``--backend local``. A
    refused run prints the reason to stderr and returns 2 before creating
    anything. ``probe_hint`` names the tool's single-point selector (e.g.
    ``"--only PROCESS/TEMP/VDD"``) in that message; omit it when the tool has
    no probe mode.

    An accepted run creates ``outdir``, prints the command, runs
    ``[*shlex.split(klt_cmd), "sim", request, "--backend", backend, "-o",
    outdir/stem, "--format", "json"]`` with stdout/stderr captured to
    ``<stem>.report.json`` / ``<stem>.stderr.txt``, and returns klt's exit
    status. ``cleanup``, when given, runs in a ``finally`` around the
    subprocess so a temporary request file beside a deck cannot outlive it.
    """
    if not single_point and backend == "local":
        print("refusing to run the whole grid locally: use --backend batch (shared-host rule)"
              + (f", or {probe_hint} for one probe point" if probe_hint else ""), file=sys.stderr)
        return 2
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    report = out / f"{stem}.report.json"
    cmd = [*shlex.split(klt_cmd), "sim", str(request), "--backend", backend,
           "-o", str(out / stem), "--format", "json"]
    print("running:", " ".join(cmd))
    try:
        with open(report, "w") as fh, open(out / f"{stem}.stderr.txt", "w") as err:
            rc = subprocess.call(cmd, stdout=fh, stderr=err)
    finally:
        if cleanup is not None:
            cleanup()
    print(f"klt exit {rc}; report: {report}; stderr: {out / (stem + '.stderr.txt')}")
    return rc
