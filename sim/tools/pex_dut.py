#!/usr/bin/env python3
"""Helpers shared by the two `klt pex` DUT generators.

`sim/tb/ro-ring11-pex/build_dut.py` and `sim/tb/combiner-sampler-pex/build_dut.py`
each render a schematic-side DUT whose header matches a `klt extract` port
order. The netlist parsing, the testbench `xdut` check and the `klt extract`
call are the same job in both, so they live here; the port-mapping rules,
rendering and CLI stay in the generators.

`extract` honours the `KLT` environment variable (a shell-quoted command, for
example `KLT="uvx --from klayout-tools==0.6.0 --with klayout==0.30.10 klt"`)
so a `--check` run can pin a klt version.

Standard library only.
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class BuildError(Exception):
    pass


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def logical_lines(text: str) -> list[str]:
    """Lines with `+` continuations joined onto the line they continue."""
    out: list[str] = []
    for raw in text.splitlines():
        if raw.startswith("+") and out:
            out[-1] += " " + raw[1:].strip()
        else:
            out.append(raw.rstrip())
    return out


def subckt_block(text: str, name: str, where: str) -> list[str]:
    """Raw lines of `.subckt name` .. `.ends` (exactly one definition)."""
    lines = text.splitlines()
    starts = [
        i for i, l in enumerate(lines)
        if re.match(rf"^\.subckt\s+{re.escape(name)}\s", l + " ", re.I)
    ]
    if len(starts) != 1:
        raise BuildError(f"{where}: expected one .subckt {name}, found {len(starts)}")
    start = starts[0]
    end = next((i for i in range(start, len(lines)) if re.match(r"^\.ends\b", lines[i], re.I)), None)
    if end is None:
        raise BuildError(f"{where}: .subckt {name} has no .ends")
    return lines[start : end + 1]


def dut_header(text: str, top: str, dut: Path) -> list[str]:
    """Port names of `.subckt <top>` in a rendered DUT (parameters dropped)."""
    for line in logical_lines(text):
        if re.match(rf"^\.subckt\s+{top}\b", line, re.I):
            return [t for t in line.split()[2:] if "=" not in t]
    raise BuildError(f"{rel(dut)}: no .subckt {top}")


def check_testbench(port_names: list[str], top: str, testbench: Path) -> None:
    """Fail unless the testbench's `xdut` line is exactly the DUT's port order."""
    xdut = next(
        (l for l in logical_lines(testbench.read_text()) if l.lower().startswith("xdut ")),
        None,
    )
    want = ["xdut", *port_names, top]
    if xdut is None or xdut.split() != want:
        raise BuildError(f"{rel(testbench)}: xdut line must read {' '.join(want)!r}")


def extract(outdir: Path, gds: str, top: str) -> str:
    """Run `klt extract --parasitics` over `gds` and return the netlist text."""
    out = outdir / f"{top}.extracted.spice"
    klt = shlex.split(os.environ.get("KLT", "klt"))
    subprocess.run(
        [*klt, "extract", gds, "--deck", "gf180mcu", "--pdk", "gf180mcuD",
         "--top", top, "--parasitics", "-o", str(out), "--format", "json"],
        cwd=REPO_ROOT, check=True, stdout=subprocess.DEVNULL,
    )
    return out.read_text()
