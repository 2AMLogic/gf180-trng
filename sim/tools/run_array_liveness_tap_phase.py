#!/usr/bin/env python3
"""Resumable, detached launcher for issue #87's shipped-array tap-phase runs.

    python3 sim/tools/run_array_liveness_tap_phase.py               # launch, detached
    python3 sim/tools/run_array_liveness_tap_phase.py --status       # check progress
    python3 sim/tools/run_array_liveness_tap_phase.py --foreground   # run inline (debugging)

``sim/characterization-shipped-array-tap-phase.md``'s "What has stopped it so
far" section records three prior launches of the sixteen runs (four decks x
four seeds) this experiment needs, none of which produced a committable
record. Two failure modes are this repository's to fix, and this script is
the fix:

  1. **Attempt 1** died when the agent session that launched
     ``run_corners.py`` ended: ``SIGTERM`` reached every ``ngspice`` under it
     because the whole batch inherited that session's process group. Fixed
     here by launching the actual batch under ``start_new_session=True``
     (the ``subprocess`` equivalent of calling ``os.setsid()`` in the child)
     -- so nothing above that child's own session can reach it with one
     signal, and a Ctrl-C or turn-ending SIGTERM sent to this script's own
     process group stops at this script, not the ngspice runs it started.
  2. A single ``run_corners.py`` invocation only writes a PVT point's record
     once every seed of that point has finished (see
     ``sim/harness/cli.py``'s ``_emit``), so a kill at 95 % of a ~348
     CPU-minute point (four seeds at ~87 CPU-min each) loses the whole
     point, not just the unfinished seed. Fixed here by looping per deck:
     before each attempt, check whether a clean record (corner
     ``tt/27/3.30``, all four seeds present) already exists for that deck
     and skip it if so; if a previous attempt left an incomplete record or
     an orphaned ``raw/<stem>/`` directory (a stem reserved by
     ``run_corners.py`` but never written because the process died first),
     delete just that deck's leftovers and retry -- so a kill costs at most
     one deck's most recent attempt, never the whole batch, and never a
     deck that already finished cleanly.

Attempts 2 and 3 died to a host-level event outside this repository's
control (every ``ngspice`` on the machine killed at once, coinciding with a
``loom-daemon`` restart) -- this script cannot fix that, but the per-deck
retry loop above means a recurrence only costs whatever deck was running
when it happens, and a re-launch resumes from there rather than from zero.

This script does not itself measure anything and writes no conclusion --
it is infrastructure for producing the sixteen runs
``sim/characterization-shipped-array-tap-phase.md``'s Results section is
waiting on. See that document for the method, the per-seed cost estimate,
and the full history of what has stopped this experiment so far.

Stdlib only; no ngspice or PDK access of its own (it shells out to
``sim/run_corners.py``, which needs both -- see its own ``--check-env``).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SIM_DIR = REPO_ROOT / "sim"
RECORDS_DIR = SIM_DIR / "records"
RAW_DIR = RECORDS_DIR / "raw"
RUN_CORNERS = SIM_DIR / "run_corners.py"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from starved_cell_jitter_energy import Record  # noqa: E402

#: Scratch location for this launcher's own log + PID file. Under sim/.work/,
#: which is already gitignored wholesale (sim/README.md: the shared scratch
#: workdir for --no-write runs) -- nothing here is ever meant to be committed.
WORK_DIR = SIM_DIR / ".work" / "array-liveness-tap-phase-launch"
DEFAULT_LOG = WORK_DIR / "run.log"
DEFAULT_PIDFILE = WORK_DIR / "run.pid"

#: The four decks sim/characterization-shipped-array-tap-phase.md's "What is
#: left to do" step 1 names, in the same order.
DECKS = [
    "array-liveness-tap-phase-clocked",
    "array-liveness-tap-phase-static",
    "array-liveness-tap-phase-xsb-clocked",
    "array-liveness-tap-phase-xsb-static",
]

#: One corner, per the doc's Method section: tt/27 C/3.30 V, directly
#: comparable to issue #51's coupling ladder and issue #76's phase-cost
#: family. Four independent noise seeds per deck, per sim/README.md.
SEEDS = (1, 2, 3, 4)
#: -j 4 matches sim/characterization-shipped-array-tap-phase.md's own "What is
#: left to do" reproduction command: one deck's four seeds are independent
#: ngspice processes, so running them concurrently only changes wall clock,
#: never what is measured.
CORNER_ARGS = [
    "--corners", "tt",
    "--temps", "27",
    "--supply", "3.3",
    "--supply-tol", "0",
    "--seeds", *[str(s) for s in SEEDS],
    "-j", "4",
]
#: Matches harness.report / starved_cell_jitter_energy.Record.corner's
#: "<process>/<temp:.0f>/<vdd:.2f>" format exactly, so the string compares
#: rather than needing its own parsing of the corner grid.
CORNER_LABEL = "tt/27/3.30"

#: run_corners.py's own default per-run timeout is 300 s; each of these runs
#: costs ~87 CPU-minutes, two orders of magnitude more (see the
#: characterization doc's "What the runs cost"). 24 h leaves headroom on a
#: busy host without masking a genuinely hung run over a whole day.
DEFAULT_TIMEOUT_S = 86400
#: Retries per deck before this launcher gives up on it and moves on to the
#: next (still reporting the failure at the end) rather than looping forever
#: against a deck that cannot converge.
DEFAULT_MAX_ATTEMPTS = 5


def _log(msg: str) -> None:
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def _load_record(path: Path) -> Record | None:
    try:
        return Record(path)
    except Exception as exc:  # noqa: BLE001 - unparseable record is not ours to touch
        _log(f"  (could not parse {path.name}, leaving it alone: {exc})")
        return None


def deck_status(slug: str) -> str:
    """``"complete"``, ``"incomplete"`` or ``"missing"`` for ``slug`` at
    :data:`CORNER_LABEL`.

    ``"complete"`` means the newest matching record at that corner carries a
    ``sigma_1`` contributed by all four seeds -- the same bar
    ``array_liveness_tap_phase_variants.py`` requires to read a variant at
    all. Records at a different corner are never inspected here; this
    experiment runs exactly one corner and has nothing to say about others.
    """
    best: Record | None = None
    for path in sorted(RECORDS_DIR.glob(f"????-??-??-{slug}-*.md")):
        rec = _load_record(path)
        if rec is None or rec.corner != CORNER_LABEL:
            continue
        best = rec  # sorted ascending by stem (date + 2-digit sequence); last wins
    if best is None:
        return "missing"
    if "sigma_1" in best.values and best.seeds >= len(SEEDS):
        return "complete"
    return "incomplete"


def clean_stale(slug: str) -> list[str]:
    """Delete every non-``"complete"`` record (and its raw dir) for ``slug``
    at :data:`CORNER_LABEL`, plus any orphaned ``raw/<stem>/`` reserved for
    this slug's corner with no record at all -- the minimum the
    characterization doc's "What has stopped it so far" names as what a
    resumable driver needs: a stem a killed run left behind must not block
    (or be mistaken for) the next attempt's evidence.

    Returns the paths removed, for the caller to log. Never touches a record
    at a different corner, and never touches a ``"complete"`` one -- deleting
    committed evidence is not this script's job even when it is stale by some
    other measure.
    """
    removed: list[str] = []
    for path in sorted(RECORDS_DIR.glob(f"????-??-??-{slug}-*.md")):
        rec = _load_record(path)
        if rec is None or rec.corner != CORNER_LABEL:
            continue
        complete = "sigma_1" in rec.values and rec.seeds >= len(SEEDS)
        if complete:
            continue
        raw = RAW_DIR / path.stem
        path.unlink()
        removed.append(str(path))
        if raw.is_dir():
            shutil.rmtree(raw)
            removed.append(str(raw))
    if RAW_DIR.is_dir():
        for raw in sorted(RAW_DIR.glob(f"????-??-??-{slug}-*")):
            if not raw.is_dir():
                continue
            if not (RECORDS_DIR / f"{raw.name}.md").exists():
                shutil.rmtree(raw)
                removed.append(str(raw))
    return removed


def run_deck(slug: str, timeout_s: int) -> int:
    """Run one deck's four-seed grid point via ``run_corners.py``.

    Inherits this process's own stdout/stderr, so in detached mode (where
    those are the log file) ``run_corners.py``'s own per-point progress line
    and ngspice's own diagnostics land in the same log this script writes
    to, in order.
    """
    cmd = [
        sys.executable, str(RUN_CORNERS), slug,
        *CORNER_ARGS, "--timeout", str(timeout_s),
    ]
    _log(f"$ {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=REPO_ROOT, check=False)
    return proc.returncode


def check_env() -> bool:
    proc = subprocess.run(
        [sys.executable, str(RUN_CORNERS), "--check-env"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        _log("environment check failed; not starting any run:")
        for line in (proc.stdout + proc.stderr).splitlines():
            _log(f"  {line}")
        return False
    return True


def main_loop(decks: list[str], timeout_s: int, max_attempts: int) -> int:
    _log(
        f"issue #87 shipped-array tap-phase launcher starting: decks={decks} "
        f"corner={CORNER_LABEL} seeds={list(SEEDS)} timeout={timeout_s}s "
        f"max_attempts={max_attempts}"
    )
    if not check_env():
        return 1

    t_start = time.time()
    failures: list[str] = []
    for slug in decks:
        if deck_status(slug) == "complete":
            _log(f"{slug}: already has a complete {CORNER_LABEL} 4-seed record, skipping")
            continue

        landed = False
        for attempt in range(1, max_attempts + 1):
            for removed in clean_stale(slug):
                _log(f"{slug}: removed stale {removed}")
            _log(f"{slug}: attempt {attempt}/{max_attempts} starting")
            t0 = time.time()
            rc = run_deck(slug, timeout_s)
            elapsed_h = (time.time() - t0) / 3600
            status = deck_status(slug)
            _log(
                f"{slug}: attempt {attempt} finished rc={rc} elapsed={elapsed_h:.2f}h "
                f"status={status}"
            )
            if status == "complete":
                landed = True
                break

        if landed:
            _log(f"{slug}: record landed cleanly")
        else:
            _log(f"{slug}: FAILED after {max_attempts} attempts; giving up on this deck for now")
            failures.append(slug)

    total_h = (time.time() - t_start) / 3600
    _log(f"batch finished in {total_h:.2f}h; failed decks: {failures or 'none'}")
    return 1 if failures else 0


def print_status(decks: list[str]) -> int:
    any_incomplete = False
    for slug in decks:
        status = deck_status(slug)
        print(f"{slug:<40} {status}")
        if status != "complete":
            any_incomplete = True
    return 1 if any_incomplete else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_array_liveness_tap_phase.py",
        description=(
            "Resumable, detached launcher for issue #87's shipped-array tap-phase "
            "runs: four decks x four seeds at tt/27C/3.30V, via sim/run_corners.py."
        ),
    )
    parser.add_argument(
        "--decks", nargs="+", default=DECKS, choices=DECKS,
        help="which decks to run/resume (default: all four)",
    )
    parser.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT_S,
        help="per-ngspice-run wall-clock bound in seconds, passed to run_corners.py "
        "--timeout (default %(default)s)",
    )
    parser.add_argument(
        "--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS,
        help="retries per deck before giving up on it and moving to the next "
        "(default %(default)s)",
    )
    parser.add_argument(
        "--log", type=Path, default=DEFAULT_LOG,
        help="log file; also the detached child's stdout/stderr (default %(default)s)",
    )
    parser.add_argument(
        "--pidfile", type=Path, default=DEFAULT_PIDFILE,
        help="where to record the detached child's PID (default %(default)s)",
    )
    parser.add_argument(
        "--foreground", action="store_true",
        help="run the batch inline instead of forking a detached child. Used "
        "internally by the detached child itself; useful standalone only for a "
        "short --decks subset test, since a foreground run dies with this "
        "process (see module docstring, attempt 1)",
    )
    parser.add_argument(
        "--status", action="store_true",
        help="print each deck's status (complete/incomplete/missing) and exit; "
        "does not launch or run anything",
    )
    args = parser.parse_args(argv)

    if args.status:
        return print_status(args.decks)

    args.log.parent.mkdir(parents=True, exist_ok=True)

    if args.foreground:
        return main_loop(args.decks, args.timeout, args.max_attempts)

    # Detached launch: re-invoke this same script with --foreground in its own
    # session (start_new_session=True is subprocess's os.setsid()-in-the-child
    # equivalent), stdio redirected to the log file, and return immediately
    # without waiting. A SIGTERM to this process's own process group -- e.g.
    # this agent turn or session ending -- reaches this launcher and nothing
    # past it, because the child is in a different session. See "What has
    # stopped it so far" / attempt 1 in
    # sim/characterization-shipped-array-tap-phase.md.
    cmd = [
        sys.executable, str(Path(__file__).resolve()), "--foreground",
        "--timeout", str(args.timeout),
        "--max-attempts", str(args.max_attempts),
        "--log", str(args.log),
        "--decks", *args.decks,
    ]
    with open(args.log, "ab", buffering=0) as logf:
        proc = subprocess.Popen(
            cmd,
            cwd=REPO_ROOT,
            stdin=subprocess.DEVNULL,
            stdout=logf,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    args.pidfile.parent.mkdir(parents=True, exist_ok=True)
    args.pidfile.write_text(f"{proc.pid}\n")
    print(f"launched pid={proc.pid}")
    print(f"log       {args.log}")
    print(f"pidfile   {args.pidfile}")
    print(f"status    python3 {Path(__file__).name} --status")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
