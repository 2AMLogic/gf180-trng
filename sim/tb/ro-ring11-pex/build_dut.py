#!/usr/bin/env python3
"""Generate the schematic-side DUT for the `klt pex` run over ring1's layout.

    python3 sim/tb/ro-ring11-pex/build_dut.py            # extract, write ro_ring11_schematic.spice
    python3 sim/tb/ro-ring11-pex/build_dut.py --check    # extract to scratch, fail if it would change
    python3 sim/tb/ro-ring11-pex/build_dut.py --verify-netlist <extracted.spice>
                                                         # hold a klt-pex-written netlist to the DUT

Why this file exists
--------------------
`klt pex` (klt 0.6.0) re-runs one `klt sim` testbench twice: once as written,
with its one `.include` naming the schematic DUT, and once with that line
re-pointed at the netlist `klt pex` just extracted from the layout. The
testbench's `xdut` line is reused byte for byte on both sides, so the two
`.SUBCKT ro_ring11` headers have to agree position by position.

`klt extract` over `layout/rings/ro_ring11/ro_ring11.gds` promotes fifteen
ports: the eleven ring nodes, which flat extraction names `a|y`, `a|y$1`, ...
`a|y$10` (each is one stage's `y` merged with the next stage's `a`), then
`en`, `vddr`, `vss`, `vsubs`. The schematic ring (`design/ro_array_core.spice`,
`.subckt ro_ring11 en ro vddr vss`) exposes only four of those. This script
writes a schematic `ro_ring11` with the extraction's fifteen-port header, each
position carrying the schematic node that sits there in the layout, and the
body transcribed from `design/ro_array_core.spice` unchanged.

How each ring position is identified
------------------------------------
From the extracted netlist itself, not from net names: the parasitic
resistors tie each port to its device-terminal nodes, so each port's net is
the resistor-connected cluster around it. The ring's devices sit in one row
in `ROW_ORDER` (`xg`, `x1` .. `x10`, left to right, from
`layout/rings/ro_ring11/build.py`), and each stage's input net is the gate
of that stage's devices. Ordering the eleven ring ports by the leftmost
x-coordinate of any device whose gate they drive therefore gives the input
of `xg`, then of `x1`, ... `x10` -- that is, `ro`, `n1`, ... `n10` in the
schematic's own names. Anything other than exactly eleven ring ports, or a
port that drives no gate, or two ports tied on that coordinate, raises
rather than guessing.

`--verify-netlist` runs the same derivation over the netlist a `klt pex`
run actually extracted and simulated, and fails unless it reproduces the
committed DUT header exactly. That is what makes the positional match a
checked property of the evidence rather than an assumption about the
extractor's port ordering being stable between two runs.

What the schematic side is
--------------------------
`vsubs` has no schematic counterpart (the schematic ties NMOS bulk to `vss`
and PMOS bulk to `vddr`); it is declared and unused here, and the testbench
holds it at 0 V. The ring1 sizing (`wstv=0.220u lstv=2u cld=0.5f`) is the
`xr1` instance's own, from `design/ro_array_core.spice`. `cld` is the
schematic's lumped wiring-load estimate on each stage output; the extracted
side has none and carries the drawn parasitics instead, which is the point
of the comparison.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
DESIGN = REPO_ROOT / "design" / "ro_array_core.spice"
GDS = "layout/rings/ro_ring11/ro_ring11.gds"
TOP = "ro_ring11"
DUT = HERE / "ro_ring11_schematic.spice"
TESTBENCH = HERE / "tb_ro_ring11_pex.sp"

#: Ring1's instance parameters (`xr1` in design/ro_array_core.spice).
RING1_PARAMS = "wstv=0.220u lstv=2u cld=0.5f"
#: Ports the extraction names uniquely; every other port is a ring node.
NAMED_PORTS = ("en", "vddr", "vss", "vsubs")
#: Schematic names of the eleven ring nodes, in ROW_ORDER (input of xg first).
RING_NODES = ["ro"] + [f"n{i}" for i in range(1, 11)]

_DEVICE_COMMENT = re.compile(
    r"^\*\s*device instance\s+(\S+)\s+\S+\s+\S+\s+(-?[\d.]+),(-?[\d.]+)\s+(\w+)"
)


class BuildError(Exception):
    pass


def _logical_lines(text: str) -> list[str]:
    out: list[str] = []
    for raw in text.splitlines():
        if raw.startswith("+") and out:
            out[-1] += " " + raw[1:].strip()
        else:
            out.append(raw.rstrip())
    return out


def _subckt_block(text: str, name: str) -> list[str]:
    lines = text.splitlines()
    start = next(
        (i for i, l in enumerate(lines) if re.match(rf"^\.subckt\s+{name}\b", l, re.I)),
        None,
    )
    if start is None:
        raise BuildError(f"{DESIGN.relative_to(REPO_ROOT)}: no .subckt {name}")
    end = next(i for i in range(start, len(lines)) if re.match(r"^\.ends\b", lines[i], re.I))
    return lines[start : end + 1]


def extraction_port_map(netlist_text: str) -> list[str]:
    """Schematic node name for each port position of the extracted
    `.SUBCKT ro_ring11` header -- see the module docstring."""
    lines = _logical_lines(netlist_text)
    header = next(
        (l.split()[2:] for l in lines if re.match(rf"^\.SUBCKT\s+{TOP}\b", l, re.I)),
        None,
    )
    if header is None:
        raise BuildError(f"extracted netlist declares no .SUBCKT {TOP}")
    for name in NAMED_PORTS:
        if header.count(name) != 1:
            raise BuildError(f"extracted header names {name!r} {header.count(name)} times")
    ring_ports = [p for p in header if p not in NAMED_PORTS]
    if len(ring_ports) != len(RING_NODES):
        raise BuildError(
            f"expected {len(RING_NODES)} ring-node ports, extraction has {len(ring_ports)}: "
            f"{ring_ports}"
        )

    # Union every parasitic resistor's two nodes: a port's net is its cluster.
    parent: dict[str, str] = {}

    def find(n: str) -> str:
        parent.setdefault(n, n)
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n

    gates: list[tuple[str, float]] = []
    pending_x: float | None = None
    for line in lines:
        m = _DEVICE_COMMENT.match(line)
        if m:
            pending_x = float(m.group(2))
            continue
        toks = line.split()
        if not toks:
            continue
        if toks[0][0] in "Rr" and len(toks) >= 4:
            parent[find(toks[1])] = find(toks[2])
        elif toks[0][0] in "Xx" and pending_x is not None and len(toks) >= 6:
            gates.append((toks[2], pending_x))  # X<name> d g s b model
            pending_x = None

    leftmost: dict[str, float] = {}
    for gate, x in gates:
        root = find(gate)
        leftmost[root] = min(x, leftmost.get(root, x))
    keyed = []
    for port in ring_ports:
        x = leftmost.get(find(port))
        if x is None:
            raise BuildError(f"ring port {port!r} drives no device gate")
        keyed.append((x, port))
    keyed.sort()
    xs = [x for x, _ in keyed]
    if len(set(xs)) != len(xs):
        raise BuildError(f"two ring ports tie on leftmost gate x: {keyed}")
    names = {port: node for (_x, port), node in zip(keyed, RING_NODES)}
    return [names.get(p, p) for p in header]


def render_dut(port_names: list[str]) -> str:
    design = DESIGN.read_text()
    ring = _subckt_block(design, "ro_ring11")
    body = [l for l in _logical_lines("\n".join(ring[1:-1])) if l and not l.startswith("*")]
    out = [
        "* ro_ring11 schematic-side DUT for the klt pex run over ring1's layout.",
        "* GENERATED by sim/tb/ro-ring11-pex/build_dut.py -- do not edit by hand.",
        "*",
        "* The header is klt extract's fifteen-port order for",
        f"* {GDS}, with each position carrying the schematic",
        "* node that sits there in the layout (identified from the extracted",
        "* netlist's own device geometry; see build_dut.py). The body is",
        "* design/ro_array_core.spice's .subckt ro_ring11 and its two leaf",
        "* subcircuits, transcribed unchanged, at ring1's xr1 sizing. vsubs is",
        "* declared and unused: the schematic has no substrate-tap net.",
        "",
        f".subckt ro_ring11 {' '.join(port_names)} {RING1_PARAMS}",
        *body,
        ".ends",
        "",
    ]
    for leaf in ("ro_nand2", "ro_stage"):
        out += _subckt_block(design, leaf) + [""]
    return "\n".join(out)


def check_testbench(port_names: list[str]) -> None:
    xdut = next(
        (l for l in _logical_lines(TESTBENCH.read_text()) if l.lower().startswith("xdut ")),
        None,
    )
    want = ["xdut", *port_names, TOP]
    if xdut is None or xdut.split() != want:
        raise BuildError(
            f"{TESTBENCH.relative_to(REPO_ROOT)}: xdut line must read {' '.join(want)!r}"
        )


def extract(outdir: Path) -> str:
    out = outdir / "ro_ring11.extracted.spice"
    subprocess.run(
        ["klt", "extract", GDS, "--deck", "gf180mcu", "--pdk", "gf180mcuD",
         "--top", TOP, "--parasitics", "-o", str(out), "--format", "json"],
        cwd=REPO_ROOT, check=True, stdout=subprocess.DEVNULL,
    )
    return out.read_text()


def dut_header(text: str) -> list[str]:
    for line in _logical_lines(text):
        if re.match(rf"^\.subckt\s+{TOP}\b", line, re.I):
            return [t for t in line.split()[2:] if "=" not in t]
    raise BuildError(f"{DUT.relative_to(REPO_ROOT)}: no .subckt {TOP}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--verify-netlist", type=Path)
    args = ap.parse_args(argv)
    try:
        if args.verify_netlist:
            got = extraction_port_map(args.verify_netlist.read_text())
            want = dut_header(DUT.read_text())
            if got != want:
                raise BuildError(
                    f"{args.verify_netlist}: ring positions resolve to {got}, "
                    f"but the committed DUT header is {want}"
                )
            print(f"build_dut: {args.verify_netlist} matches the DUT header position for position")
            return 0
        with tempfile.TemporaryDirectory() as tmp:
            ports = extraction_port_map(extract(Path(tmp)))
        text = render_dut(ports)
        check_testbench(ports)
        if args.check:
            if not DUT.is_file() or DUT.read_text() != text:
                raise BuildError(f"{DUT.relative_to(REPO_ROOT)} is stale; re-run build_dut.py")
            print(f"build_dut: {DUT.relative_to(REPO_ROOT)} is current")
            return 0
        DUT.write_text(text)
        print(f"build_dut: wrote {DUT.relative_to(REPO_ROOT)} (ports: {' '.join(ports)})")
        return 0
    except (BuildError, subprocess.CalledProcessError) as exc:
        print(f"build_dut: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
