"""Deck composition and ngspice execution for one PVT point (one or more
seeded runs, for stochastic testbenches)."""

from __future__ import annotations

import functools
import os
import re
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from .corners import PvtPoint
from .pdk import Pdk
from .testbench import Testbench

NGSPICE = "ngspice"
DEFAULT_TIMEOUT_S = 300

# Grace period the OS-level watchdog (see `timeout_bin`) gives ngspice to
# exit after its initial SIGTERM before escalating to an unblockable
# SIGKILL. ngspice does not normally ignore SIGTERM, but a deadlocked run
# (the incident this module guards against) might never reach a point where
# it notices the signal at all -- SIGKILL is what actually guarantees exit.
KILL_GRACE_S = 30

# How far past the OS-level watchdog's own bound (timeout_s + KILL_GRACE_S)
# the in-process guard (`Popen.communicate(timeout=...)`) waits before it
# steps in itself. Purely a fallback margin -- in the common case (this
# harness alive for the whole run, watchdog present) the watchdog always
# fires first and this guard never triggers.
_GUARD_PAD_S = 30

# Exit codes coreutils `timeout(1)` uses when IT terminated the command
# (rather than the command exiting on its own): 124 on a plain SIGTERM
# timeout, 137 (128+SIGKILL) if `--kill-after` had to escalate, and 143
# (128+SIGTERM) if ngspice happened to die from the TERM itself. This is a
# secondary signal only -- see the elapsed-time check next to its use below,
# which is what actually carries the classification: when `--kill-after`
# has to escalate to SIGKILL, `timeout` (by default, non-`--foreground`)
# puts itself in the *same* process group as the command it is watching, so
# the group-wide SIGKILL it sends can also catch `timeout` itself, and this
# process then observes `timeout`'s own exit as "killed by signal 9"
# (returncode -9) rather than one of the codes below.
_WATCHDOG_EXIT_CODES = frozenset({124, 137, 143})

# `print` output for a length-1 vector: "m_vout = 6.9043645202e-01"
_MEAS_RE = re.compile(r"^\s*m_(\w+)\s*=\s*([-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)\s*$")
_ERROR_RE = re.compile(r"^\s*(?:Error|ERROR|Fatal|fatal error|doAnalyses:)", re.MULTILINE)


class NgspiceMissing(RuntimeError):
    pass


@functools.lru_cache(maxsize=1)
def timeout_bin() -> str | None:
    """Locate the coreutils ``timeout(1)`` watchdog, or ``None`` if absent.

    ``timeout(1)`` is what makes the per-run bound survive this harness
    process itself being killed: it runs as ngspice's direct parent -- a
    *sibling* of this Python process in the process tree, not a descendant
    of it -- so if this harness is SIGKILLed mid-run (the actual failure
    mode behind the incident this module guards against: the harness's own
    Python process died, orphaning ``ngspice`` to init with nothing left to
    enforce any bound), ``timeout(1)`` is simply reparented to init/systemd
    right alongside it and keeps running its own alarm regardless -- it
    still fires and kills ``ngspice`` on schedule. ``subprocess.run(...,
    timeout=...)``'s enforcement, by contrast, lives entirely inside this
    interpreter and dies with it.

    macOS ships no ``timeout`` by default; Homebrew's ``coreutils`` package
    installs the same tool as ``gtimeout`` (to avoid clobbering a BSD tool
    of the same name), so both spellings are tried.
    """
    for name in ("timeout", "gtimeout"):
        exe = shutil.which(name)
        if exe:
            return exe
    return None


def _kill_process_group(pid: int) -> None:
    """Best-effort SIGKILL of ``pid``'s whole process group.

    Only meaningful when the process was started with
    ``start_new_session=True`` (so its pgid is its own pid, not this
    interpreter's) -- otherwise this would signal every process this
    harness itself belongs to. Swallows the case where the group is
    already gone (it may have exited on its own between the timeout firing
    and this call).
    """
    try:
        pgid = os.getpgid(pid)
    except ProcessLookupError:
        return
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def ngspice_version() -> str:
    exe = shutil.which(NGSPICE)
    if not exe:
        raise NgspiceMissing(
            "ngspice not found on PATH.\n"
            "  macOS:  brew install ngspice\n"
            "  Debian: apt-get install ngspice"
        )
    out = subprocess.run(
        [exe, "--version"], capture_output=True, text=True, check=False
    ).stdout
    for line in out.splitlines():
        if "ngspice-" in line:
            return line.strip().lstrip("* ").strip()
    return out.strip().splitlines()[0] if out.strip() else "unknown"


def _analysis_context(tb: Testbench, point: PvtPoint) -> dict[str, float]:
    """Python-side substitution values for ``tb.json``'s ``analyses`` lines.

    ``compose_deck`` inserts each ``analyses`` entry as an *interactive*
    control-block command (``dc``/``meas``/...), not a native ``.dc``/
    ``.meas`` card -- and ngspice's interactive commands do not evaluate
    ``.param``-defined symbols in a numeric-argument position: ``dc vd 0
    vdd_val 0.01`` and ``dc vd 0 {vdd_val} 0.01`` (curly-brace and bare-token
    substitution both tried) fail identically with ``Error: Bad syntax!``
    against ngspice-47. A testbench whose sweep bounds or comparison
    thresholds must track the PVT point's own supply -- anything voltage-swept
    beyond a single hardcoded nominal point -- has no ngspice-side way to
    reference ``vdd_val`` in these lines. This substitutes the numbers in
    Python instead, before the deck is written, via ``str.format(**context)``
    on each ``analyses`` entry: an entry containing e.g. ``{vdd_val}`` gets the
    literal numeric value substituted textually, so ngspice only ever sees a
    plain number. ``vdd_val``/``vdd_nom``/``temp_c`` mirror the ``.param``
    values set above; ``vdd_half`` covers the common mid-supply comparison
    point (e.g. a CMOS inverter/gate switching threshold measurement).
    """
    return {
        "vdd_val": point.vdd,
        "vdd_nom": tb.nominal_supply_v,
        "vdd_half": point.vdd / 2.0,
        "temp_c": point.temp_c,
    }


def compose_deck(tb: Testbench, pdk: Pdk, point: PvtPoint, seed: int | None = None) -> str:
    """Build the complete, self-contained ngspice deck for one PVT point.

    ``seed`` -- when given -- is emitted as ``.option seed=<seed>`` ahead of
    the model include, so it governs every random draw in the run (device
    mismatch, ``trnoise()`` sources, Monte Carlo skew). Required by the
    harness for any testbench whose ``analysis_type`` is stochastic.
    """
    lines: list[str] = [
        f"* {tb.slug} @ {point.corner_id} -- GENERATED by sim/harness, do not edit",
        f"* corner={point.corner.name} ({point.corner.description})",
        f"* temp={point.temp_c} C  vdd={point.vdd} V  pdk={pdk.variant}@{pdk.version}",
        "",
        "* ---- PVT parameters -------------------------------------------------",
        f".param vdd_nom={tb.nominal_supply_v!r}",
        f".param vdd_val={point.vdd!r}",
        f".param temp_c={point.temp_c!r}",
    ]
    for key, value in tb.params.items():
        lines.append(f".param {key}={value}")

    lines += [
        "",
        "* ---- gf180mcu models ------------------------------------------------",
        f'.include "{pdk.design_include}"',
    ]
    if seed is not None:
        lines.append(f".option seed={seed}")
    # Design-switch overrides (e.g. sw_stat_mismatch=1) must come AFTER the
    # design.ngspice include above, or its own defaults win instead.
    for key, value in tb.design_params.items():
        lines.append(f".param {key}={value}")
    if tb.extra_lib_sections:
        # A section like "statistical" is a self-contained, mismatch-enabled
        # replacement for the plain per-family corner sections (it redefines
        # the same subckts with extra mismatch params) -- ngspice silently
        # *ignores* a second definition of the same subckt, so loading both
        # would leave the mismatch-enabled model shadowed by the plain one.
        # tb.json's "corners" still selects the PVT grid's process-corner
        # axis for bookkeeping (the record's corner.process field); only the
        # library sections actually `.lib`-included are overridden here.
        for section in tb.extra_lib_sections:
            lines.append(f'.lib "{pdk.model_lib}" {section}')
    else:
        for section in point.corner.sections:
            lines.append(f'.lib "{pdk.model_lib}" {section}')

    lines += [
        "",
        f".temp {point.temp_c!r}",
    ]
    for option in tb.options:
        lines.append(f".options {option}")

    if tb.design_netlist is not None:
        lines += [
            "",
            "* ---- device under test (schematic-derived, design/netlist.py) -------",
            f'.include "{tb.design_netlist}"',
        ]

    lines += [
        "",
        "* ---- testbench ------------------------------------------------------",
        f'.include "{tb.netlist}"',
        "",
        "* ---- measurement ----------------------------------------------------",
        ".control",
        "set numdgt=10",
        "set noaskquit",
    ]
    analysis_context = _analysis_context(tb, point)
    lines += [f"  {analysis.format(**analysis_context)}" for analysis in tb.analyses]
    for name, expr in tb.measure.items():
        lines.append(f"  let m_{name} = {expr}")
    for name in tb.measure:
        lines.append(f"  print m_{name}")
    lines += [".endc", ".end", ""]
    return "\n".join(lines)


@dataclass
class RunResult:
    """The outcome of one seeded ngspice invocation at one PVT point."""

    point: PvtPoint
    seed: int | None
    status: str                                   # "ok" | "failed" | "error" | "timeout"
    measurements: dict[str, float] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)
    seconds: float = 0.0
    deck_name: str = ""
    log_name: str = ""
    message: str = ""


def parse_measurements(text: str) -> dict[str, float]:
    found: dict[str, float] = {}
    for line in text.splitlines():
        match = _MEAS_RE.match(line)
        if match:
            try:
                found[match.group(1)] = float(match.group(2))
            except ValueError:  # pragma: no cover - regex already constrains this
                continue
    return found


def _timeout_result(
    point: PvtPoint,
    seed: int | None,
    deck_path: Path,
    log_path: Path,
    elapsed: float,
    timeout_s: int,
    output: str,
    *,
    watchdog_fired: bool,
) -> RunResult:
    """Build the ``RunResult`` + breadcrumb log for a run the timeout killed.

    Used from both the OS-level watchdog path (``timeout(1)``/``gtimeout``
    exited with a code that means *it* killed ngspice) and the in-process
    fallback guard (``Popen.communicate(timeout=...)`` itself expired,
    either because no watchdog binary is on ``PATH`` or because the
    watchdog was somehow stuck too). Either way, the corner must report as
    killed-by-timeout rather than as a generic ngspice failure -- see
    ``sim/README.md`` and issue #83.
    """
    via = "timeout(1)/gtimeout" if watchdog_fired else "harness in-process guard"
    message = (
        f"ngspice timed out: no result after {elapsed:.1f}s "
        f"(bound {timeout_s}s + {KILL_GRACE_S}s kill-grace), killed by {via} "
        f"via process-group SIGKILL; deck {deck_path.name}"
    )
    log_path.write_text(
        f"TIMEOUT after {elapsed:.1f}s (bound {timeout_s}s, killed by {via})\n"
        f"deck: {deck_path.name}\n\n{output}"
    )
    return RunResult(
        point=point,
        seed=seed,
        status="timeout",
        seconds=elapsed,
        deck_name=deck_path.name,
        log_name=log_path.name,
        message=message,
    )


def run_one(
    tb: Testbench,
    pdk: Pdk,
    point: PvtPoint,
    workdir: Path,
    seed: int | None = None,
    run_index: int = 0,
    timeout_s: int = DEFAULT_TIMEOUT_S,
) -> RunResult:
    """Simulate one (PVT point, seed) pair. Never raises for sim failure.

    ``workdir`` holds both the generated deck and the raw ngspice log --
    it is the eventual ``sim/records/raw/<record-stem>/`` directory (or a
    scratch directory for a ``--no-write`` run).

    The ngspice invocation is bounded by ``timeout_s`` two ways at once
    (see issue #83, filed after a hung ngspice ran ~4.5h undetected because
    the harness process that launched it had itself been killed):

    - An OS-level watchdog (``timeout(1)``/``gtimeout``, see
      :func:`timeout_bin`) wraps the ngspice invocation directly. It runs
      as ngspice's parent, independent of this Python process staying
      alive, so it still fires even if this harness is itself killed
      mid-run.
    - ``Popen.communicate(timeout=...)`` is a secondary, in-process guard
      for the common case (harness alive for the whole run), padded past
      the watchdog's own bound so the watchdog gets first chance to act.

    Both the ngspice invocation and (when present) the watchdog wrapping it
    run in a fresh process session (``start_new_session=True``), so a kill
    -- whether the watchdog's own default group-kill or this function's
    :func:`_kill_process_group` fallback -- reaches every descendant, not
    just the direct child.
    """
    workdir.mkdir(parents=True, exist_ok=True)
    stem = f"{point.corner_id}-run{run_index}" if seed is not None else point.corner_id
    deck_path = workdir / f"{stem}.spice"
    log_path = workdir / f"{stem}.log"
    deck_path.write_text(compose_deck(tb, pdk, point, seed=seed))

    watchdog = timeout_bin()
    if watchdog is not None:
        cmd = [
            watchdog,
            f"--kill-after={KILL_GRACE_S}s",
            f"{timeout_s}s",
            NGSPICE, "-b", str(deck_path),
        ]
        # This harness process may die before the watchdog's own bound
        # elapses; pad the in-process guard well past it so the watchdog is
        # given the chance to act first, and this guard is only a fallback
        # for the (harness-alive) case where the watchdog is somehow stuck.
        guard_s = timeout_s + KILL_GRACE_S + _GUARD_PAD_S
    else:
        # No coreutils timeout(1)/gtimeout on PATH: fall back to the
        # in-process guard alone. It cannot survive this harness process
        # itself dying (see issue #83) -- `--check-env` warns about this.
        cmd = [NGSPICE, "-b", str(deck_path)]
        guard_s = timeout_s

    started = time.monotonic()
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=workdir,
            start_new_session=True,
        )
    except FileNotFoundError as exc:
        raise NgspiceMissing(str(exc)) from exc

    try:
        stdout, stderr = proc.communicate(timeout=guard_s)
        returncode = proc.returncode
    except subprocess.TimeoutExpired:
        # The in-process guard itself expired -- kill the whole process
        # group (the watchdog too, if present) rather than trust anything
        # further to exit on its own.
        elapsed = time.monotonic() - started
        _kill_process_group(proc.pid)
        try:
            stdout, stderr = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:  # pragma: no cover - defensive only
            stdout, stderr = "", ""
        return _timeout_result(
            point, seed, deck_path, log_path, elapsed, timeout_s,
            (stdout or "") + "\n" + (stderr or ""), watchdog_fired=False,
        )

    output = stdout + "\n" + stderr
    elapsed = time.monotonic() - started

    # The watchdog enforced the bound itself -- communicate() returned
    # normally (no TimeoutExpired) because the wrapped process already
    # exited, not because ngspice finished on its own. Detected primarily
    # by elapsed time (robust regardless of exactly which process the
    # watchdog's own exit status reflects -- see `_WATCHDOG_EXIT_CODES`
    # above), with the known exit codes as a fast-path/secondary signal.
    if watchdog is not None and (
        returncode in _WATCHDOG_EXIT_CODES or elapsed >= timeout_s
    ):
        return _timeout_result(
            point, seed, deck_path, log_path, elapsed, timeout_s, output,
            watchdog_fired=True,
        )

    log_path.write_text(output)

    measurements = parse_measurements(output)
    missing = [name for name in tb.measure if name not in measurements]

    if missing:
        errors = "; ".join(_ERROR_RE.findall(output)[:3])
        first_error = next(
            (line.strip() for line in output.splitlines() if _ERROR_RE.match(line)), ""
        )
        return RunResult(
            point=point,
            seed=seed,
            status="failed",
            measurements=measurements,
            missing=missing,
            seconds=elapsed,
            deck_name=deck_path.name,
            log_name=log_path.name,
            message=first_error or errors or f"ngspice exit {returncode}, no measurements parsed",
        )

    return RunResult(
        point=point,
        seed=seed,
        status="ok",
        measurements=measurements,
        seconds=elapsed,
        deck_name=deck_path.name,
        log_name=log_path.name,
    )


def plan_runs(tb: Testbench, seeds: list[int] | None) -> list[tuple[int | None, int]]:
    """The ``(seed, run_index)`` pairs one PVT point needs.

    This is where the "no seed, no evidence" rule from ``sim/README.md`` is
    enforced, so that both the serial (:func:`run_point`) and the parallel
    (``run_corners.py -j``) execution paths inherit it from one place.
    """
    if not tb.stochastic:
        return [(None, 0)]
    if not seeds:
        raise ValueError(
            f"{tb.slug}: stochastic testbench (analysis_type={tb.analysis_type!r}) "
            "requires at least one seed -- sim/README.md: 'no seed, no evidence'"
        )
    return [(seed, i) for i, seed in enumerate(seeds)]


def run_point(
    tb: Testbench,
    pdk: Pdk,
    point: PvtPoint,
    workdir: Path,
    seeds: list[int] | None,
    timeout_s: int = DEFAULT_TIMEOUT_S,
) -> list[RunResult]:
    """Run every seed (or the single deterministic run) for one PVT point."""
    return [
        run_one(tb, pdk, point, workdir, seed=seed, run_index=index, timeout_s=timeout_s)
        for seed, index in plan_runs(tb, seeds)
    ]
