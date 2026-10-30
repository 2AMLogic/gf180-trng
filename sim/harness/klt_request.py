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

import os
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
    status. ``cleanup``, when given, runs in a ``finally`` on every path
    (success, refusal, failure to start) so a temporary request file beside a
    deck cannot outlive the call.

    The whole output namespace -- the response file, the stderr file and any
    ``<stem>`` / ``<stem>.*`` entry of the klt output prefix -- is reserved
    exclusively (``O_EXCL``) before any response file is opened or klt is
    launched. An occupied destination returns 3 with a message asking for a
    fresh output directory; nothing is submitted or overwritten. A klt that
    cannot start returns 127, with the reason in the reserved stderr file.
    """
    try:
        return _run_reserved(outdir, stem, request, backend, klt_cmd,
                             single_point=single_point, probe_hint=probe_hint)
    finally:
        if cleanup is not None:
            cleanup()


def run_probe_or_grid(outdir: str | Path, backend: str, klt_cmd: str, only: str | None, *,
                      request: Path, tb_dir: Path, render_probe: Callable[[str], str],
                      probe_hint: str) -> int:
    """Run a tool's declared grid, or one ``only`` probe point, through ``klt sim``.

    ``only`` is a single-point debug probe: it needs ``--backend local`` (else
    2 is returned) and runs a restricted request, ``render_probe(only)``,
    written next to the deck in ``tb_dir`` because klt resolves ``netlist``
    relative to the request file. That temporary request is removed on every
    path. Without ``only`` the committed ``request`` is run as the whole grid
    (stem ``grid``), which ``run_klt_request`` refuses on the local backend.
    """
    if only is not None and backend != "local":
        print("--only is a single-point debug probe and runs with --backend local", file=sys.stderr)
        return 2
    stem = "grid" if only is None else "probe-" + only.replace("/", "_")
    tmp = None
    if only is not None:
        tmp = tb_dir / f".{stem}.request.json"
        tmp.write_text(render_probe(only))
        request = tmp
    return run_klt_request(
        outdir, stem, request, backend, klt_cmd,
        single_point=only is not None, probe_hint=probe_hint,
        cleanup=None if tmp is None else (lambda: tmp.unlink(missing_ok=True)))


def _prefix_products(out: Path, stem: str, own: set[str]) -> list[str]:
    """Names in ``out`` that already belong to the klt output prefix ``stem``."""
    return sorted(e.name for e in out.iterdir()
                  if e.name not in own and (e.name == stem or e.name.startswith(stem + ".")))


def _reserve(out: Path, stem: str, report: Path, err: Path) -> str | None:
    """Exclusively claim the request's output namespace; None on success.

    The response and stderr files are created with ``O_CREAT | O_EXCL`` so two
    simultaneous launches cannot both pass. Only files this call created are
    ever removed on a failed reservation; an occupied destination is never
    touched. Any other entry named ``stem`` or ``stem.*`` (a backend product of
    the klt output prefix) also marks the destination occupied.
    """
    made: list[Path] = []
    found: list[str] = []
    try:
        for path in (report, err):
            try:
                os.close(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666))
            except FileExistsError:
                for done in made:
                    done.unlink(missing_ok=True)
                return path.name
            made.append(path)
        found = _prefix_products(out, stem, {report.name, err.name})
    except BaseException:
        for path in made:
            path.unlink(missing_ok=True)
        raise
    if found:
        for path in made:
            path.unlink(missing_ok=True)
        return found[0]
    return None


def _run_reserved(outdir, stem, request, backend, klt_cmd, *, single_point, probe_hint) -> int:
    if not single_point and backend == "local":
        print("refusing to run the whole grid locally: use --backend batch (shared-host rule)"
              + (f", or {probe_hint} for one probe point" if probe_hint else ""), file=sys.stderr)
        return 2
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    report = out / f"{stem}.report.json"
    err_path = out / f"{stem}.stderr.txt"
    busy = _reserve(out, stem, report, err_path)
    if busy is not None:
        print(f"refusing to reuse an occupied output destination: {out / busy} already exists "
              f"(request '{stem}'); nothing was submitted and nothing was overwritten. "
              "Choose a fresh output directory (or request name).", file=sys.stderr)
        return 3
    cmd = [*shlex.split(klt_cmd), "sim", str(request), "--backend", backend,
           "-o", str(out / stem), "--format", "json"]
    print("running:", " ".join(cmd))
    try:
        with open(report, "w") as fh, open(err_path, "w") as err:
            rc = subprocess.call(cmd, stdout=fh, stderr=err)
    except OSError as exc:
        # klt could not start (e.g. missing executable): keep the reason in the
        # reserved stderr file so the failed attempt leaves its own diagnostics.
        err_path.write_text(f"could not start {cmd[0]}: {exc}\n")
        print(f"could not start klt: {exc}; diagnostics: {err_path}", file=sys.stderr)
        return 127
    print(f"klt exit {rc}; report: {report}; stderr: {err_path}")
    return rc
