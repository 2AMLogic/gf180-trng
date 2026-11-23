"""The one Icarus Verilog runner for the RTL/model equivalence tests (#1055).

Five unit-test modules -- ``test_conditioner``, ``test_health_test``,
``test_ring_liveness``, ``test_interface`` and ``test_trng_top`` -- each run
a ``tb_rtl_equivalence.v`` harness under Icarus Verilog and compare what it
wrote with the behavioural Python model. Every harness speaks the same
plusarg protocol: ``+stim=<path>`` is the ``$readmemb`` / ``$readmemh``
file, ``+out=<path>`` is where it writes one result line per cycle, and
``+nvec=<n>`` bounds the vector count. When it cannot run (a plusarg
missing, ``nvec`` past its capacity, ``$fopen`` failed) it prints
``FATAL: ...`` and calls ``$finish`` -- which exits ``vvp`` with status 0,
so the caller only notices by reading stdout.

That protocol, the ``iverilog -g2012`` / ``vvp`` pair around it and the
``FATAL`` check were copied into each module in turn as the digital blocks
gained their equivalence test. This module is the one copy. A test module
keeps only what is genuinely its own: encoding its model's stimulus rows
and parsing the result lines back into its model's shape.

Tool availability is not this module's business. Callers sit behind
``_tool_gate.requires_tools``; here a missing tool surfaces as the
``FileNotFoundError`` ``subprocess.run`` raises, never as a silent pass.
"""

from __future__ import annotations

import subprocess
import tempfile
from collections.abc import Callable, Iterable
from pathlib import Path

#: What every ``tb_rtl_equivalence.v`` prints before ``$finish`` when it
#: could not run; ``vvp`` still exits 0, so this string is the only signal.
FATAL_MARKER = "FATAL"


def compile_and_run_vvp(
    sources: Iterable[Path | str],
    *,
    include_dirs: Iterable[Path | str] = (),
    plusargs: Iterable[str] = (),
    run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> str:
    """Compile ``sources`` with ``iverilog -g2012`` and run the image.

    Each entry of ``include_dirs`` is passed as ``-I <dir>`` (for RTL that
    `` `include``s a generated header); ``plusargs`` go to ``vvp`` verbatim.
    Returns ``vvp``'s stdout.
    """
    with tempfile.TemporaryDirectory() as scratch:
        proc = _compile_and_run(sources, include_dirs, plusargs, Path(scratch), run)
    return proc.stdout


def run_rtl_equivalence(
    sources: Iterable[Path | str],
    *,
    stimulus: str,
    nvec: int,
    include_dirs: Iterable[Path | str] = (),
    run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> list[str]:
    """Run a ``tb_rtl_equivalence.v`` harness over ``stimulus``.

    Writes ``stimulus`` to a scratch file and runs the harness with
    ``+stim`` / ``+out`` / ``+nvec``. Returns the stripped, non-blank lines
    it wrote to ``+out`` -- ``[]`` when it wrote none.

    ``run`` exists for this module's own tests; real callers pass only the
    sources, the stimulus and the vector count.
    """
    with tempfile.TemporaryDirectory() as scratch:
        scratch = Path(scratch)
        stim = scratch / "stim.mem"
        out = scratch / "out.txt"
        stim.write_text(stimulus)
        _compile_and_run(
            sources, include_dirs, [f"+stim={stim}", f"+out={out}", f"+nvec={nvec}"],
            scratch, run,
        )
        if not out.exists():
            return []
        return [line.strip() for line in out.read_text().splitlines() if line.strip()]


def _compile_and_run(
    sources: Iterable[Path | str],
    include_dirs: Iterable[Path | str],
    plusargs: Iterable[str],
    scratch: Path,
    run: Callable[..., subprocess.CompletedProcess],
) -> subprocess.CompletedProcess:
    """Compile into ``scratch``, run, and refuse a ``FATAL`` run."""
    image = scratch / "sim.vvp"
    compile_argv = ["iverilog", "-g2012"]
    for directory in include_dirs:
        compile_argv += ["-I", str(directory)]
    run(
        [*compile_argv, "-o", str(image), *map(str, sources)],
        check=True, capture_output=True, text=True,
    )
    proc = run(["vvp", str(image), *plusargs], check=True, capture_output=True, text=True)
    if FATAL_MARKER in proc.stdout:
        raise AssertionError(proc.stdout)
    return proc
