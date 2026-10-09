#!/usr/bin/env python3
"""Generate the schematic-side DUT for the `klt pex` run over ring1's layout.

    python3 sim/tb/ro-ring11-pex/build_dut.py            # extract, write ro_ring11_schematic.spice
    python3 sim/tb/ro-ring11-pex/build_dut.py --check    # extract to scratch, fail if it would change
    python3 sim/tb/ro-ring11-pex/build_dut.py --check-source
                                                         # offline: DUT vs design source, no klt
    python3 sim/tb/ro-ring11-pex/build_dut.py --verify-netlist <extracted.spice>
                                                         # hold a klt-pex-written netlist to the DUT

Ring selection (#423): every mode takes `--ring ring1|ring2` (default ring1).
Ring2 (`layout/rings/ro_ring11_ring2/`, instance `xr2`, subcircuit
`ro_ring11_ring2`) writes its fixture under sim/tb/ro-ring11-ring2-pex/; its
sizing is read from `xr2`, never from ring1's constants.

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

Source identity
---------------
`source_identity()` hashes `consumed_source()`: the `ro_ring11`, `ro_nand2`
and `ro_stage` subcircuits (comments and whitespace normalised away) plus the
`xr1` sizing -- the consumed circuit sections, not the whole file, so edits to
other cells or to ring2 do not invalidate evidence. Three identities are kept
distinct: the source identity (this hash, current design), the generated
fixture identity (sha256 of the committed DUT, pinned in publication.json) and
the simulated fixture identity (what the `klt pex` run hashed). `--check-source`
and signoff/check.py require the committed DUT to equal `render_dut()` of the
current source, and `RING1_PARAMS` to equal `xr1`'s own sizing.

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
import hashlib
import re
import subprocess
import sys
import tempfile
from collections import namedtuple
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
DESIGN = REPO_ROOT / "design" / "ro_array_core.spice"


class Ring(namedtuple("Ring", "key top instance params gds dut testbench")):
    """One physically separate ring this fixture can be built for.

    `top` is the extracted `.SUBCKT` name (the layout's top cell); `instance`
    is the canonical instance in design/ro_array_core.spice whose sizing the
    DUT must carry. The schematic *body* is always that file's `ro_ring11`
    subcircuit; only the instance sizing and the layout differ per ring.
    """

    __slots__ = ()


#: Ring1's instance parameters (`xr1` in design/ro_array_core.spice).
RING1_PARAMS = "wstv=0.220u lstv=2u cld=0.5f"
#: Ring2's instance parameters (`xr2`): the separately sized oscillator (#423).
RING2_PARAMS = "wstv=0.240u lstv=2u cld=0.5f"
RING1 = Ring(
    "ring1", "ro_ring11", "xr1", RING1_PARAMS,
    "layout/rings/ro_ring11/ro_ring11.gds",
    HERE / "ro_ring11_schematic.spice", HERE / "tb_ro_ring11_pex.sp",
)
_RING2_DIR = HERE.parent / "ro-ring11-ring2-pex"
RING2 = Ring(
    "ring2", "ro_ring11_ring2", "xr2", RING2_PARAMS,
    "layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds",
    _RING2_DIR / "ro_ring11_ring2_schematic.spice", _RING2_DIR / "tb_ro_ring11_ring2_pex.sp",
)
RINGS = {r.key: r for r in (RING1, RING2)}

# Ring1 module-level names, kept for existing callers.
GDS = RING1.gds
TOP = RING1.top
DUT = RING1.dut
TESTBENCH = RING1.testbench
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


def extraction_port_map(netlist_text: str, ring: Ring = RING1) -> list[str]:
    """Schematic node name for each port position of the extracted
    `.SUBCKT <ring.top>` header -- see the module docstring."""
    lines = _logical_lines(netlist_text)
    header = next(
        (l.split()[2:] for l in lines if re.match(rf"^\.SUBCKT\s+{ring.top}\b", l, re.I)),
        None,
    )
    if header is None:
        raise BuildError(f"extracted netlist declares no .SUBCKT {ring.top}")
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


#: Subcircuits of design/ro_array_core.spice the DUT body is transcribed from.
CONSUMED_SUBCKTS = ("ro_ring11", "ro_nand2", "ro_stage")
#: The schematic cell every ring instance (xr1, xr2) instantiates.
SCHEMATIC_CELL = "ro_ring11"
#: The canonical instance whose sizing RING1_PARAMS restates.
RING1_INSTANCE = RING1.instance


def ring_instance_params(design: str, ring: Ring = RING1) -> str:
    """The ring's canonical instance parameter tokens, as written in the design
    source. The instance's model is always `ro_ring11` (the schematic cell),
    whatever the layout's top cell is called."""
    for line in _logical_lines(design):
        toks = line.split()
        if toks and toks[0].lower() == ring.instance and SCHEMATIC_CELL in toks:
            return " ".join(t for t in toks[toks.index(SCHEMATIC_CELL) + 1 :] if "=" in t)
    raise BuildError(
        f"{DESIGN.relative_to(REPO_ROOT)}: no {ring.instance} {SCHEMATIC_CELL} instance"
    )


def ring1_instance_params(design: str) -> str:
    return ring_instance_params(design, RING1)


def audit_ring_params(design: str, ring: Ring = RING1) -> None:
    """Fail unless the ring's restated sizing equals its canonical instance's,
    and (for any other ring) differs from ring1's -- a ring2 fixture carrying
    ring1's widths is a substitution, not a ring2 comparison."""
    canonical = ring_instance_params(design, ring)
    if canonical.split() != ring.params.split():
        raise BuildError(
            f"{ring.key} params {ring.params!r} disagrees with {ring.instance} in "
            f"{DESIGN.relative_to(REPO_ROOT)}: {canonical!r}"
        )
    if ring is not RING1 and canonical.split() == ring_instance_params(design, RING1).split():
        raise BuildError(
            f"{ring.instance} has ring1's sizing in {DESIGN.relative_to(REPO_ROOT)}; "
            f"refusing to build a {ring.key} fixture that is really ring1"
        )


def audit_ring1_params(design: str) -> None:
    """Fail unless RING1_PARAMS equals the canonical `xr1` sizing."""
    audit_ring_params(design, RING1)


def consumed_source(design: str, ring: Ring = RING1) -> str:
    """Canonical text of the source the DUT is built from.

    Scope: the `.subckt` blocks named in CONSUMED_SUBCKTS plus the `xr1`
    sizing -- NOT the whole file. Comments, blank lines, continuation layout
    and the order of other subcircuits do not matter, so an unrelated edit to
    design/ro_array_core.spice (another cell, the ring2 instance, a comment)
    leaves the identity unchanged; any change to a consumed device or to
    ring1's sizing changes it.
    """
    parts = [f"{ring.instance}: {ring_instance_params(design, ring)}"]
    for name in CONSUMED_SUBCKTS:
        block = _logical_lines("\n".join(_subckt_block(design, name)))
        parts += [" ".join(l.split()) for l in block if l.strip() and not l.lstrip().startswith("*")]
    return "\n".join(parts) + "\n"


def source_identity(design: str | None = None, ring: Ring = RING1) -> str:
    """`sha256:<hex>` of consumed_source() for the current (or given) design."""
    text = DESIGN.read_text() if design is None else design
    return "sha256:" + hashlib.sha256(consumed_source(text, ring).encode()).hexdigest()


def dut_source_problem(
    dut_text: str | None = None, design: str | None = None, ring: Ring = RING1
) -> str | None:
    """None if the committed DUT is exactly what render_dut() produces from the
    current source at the DUT's own header; otherwise a diagnostic. Needs no
    klt, ngspice or PDK: the header is read back from the committed DUT."""
    try:
        dut = ring.dut.read_text() if dut_text is None else dut_text
        design_text = DESIGN.read_text() if design is None else design
        want = render_dut(dut_header(dut, ring), design_text, ring)
    except BuildError as exc:
        return str(exc)
    if dut == want:
        return None
    import difflib

    diff = [
        l for l in difflib.unified_diff(
            dut.splitlines(), want.splitlines(), "committed DUT", "rendered from source", lineterm="", n=0
        ) if not l.startswith(("---", "+++", "@@"))
    ]
    return (
        f"{ring.dut.relative_to(REPO_ROOT)} does not match {DESIGN.relative_to(REPO_ROOT)} "
        f"(first differences: {'; '.join(diff[:4])}); re-run build_dut.py"
        f"{'' if ring is RING1 else ' --ring ' + ring.key}, then "
        f"signoff/publish_item7_analog.py{'' if ring is RING1 else ' --ring ' + ring.key}"
    )


def render_dut(port_names: list[str], design: str | None = None, ring: Ring = RING1) -> str:
    design = DESIGN.read_text() if design is None else design
    audit_ring_params(design, ring)
    block = _subckt_block(design, SCHEMATIC_CELL)
    body = [l for l in _logical_lines("\n".join(block[1:-1])) if l and not l.startswith("*")]
    out = [
        f"* {ring.top} schematic-side DUT for the klt pex run over {ring.key}'s layout.",
        "* GENERATED by sim/tb/ro-ring11-pex/build_dut.py"
        + ("" if ring is RING1 else f" --ring {ring.key}") + " -- do not edit by hand.",
        "*",
        f"* The header is klt extract's fifteen-port order for",
        f"* {ring.gds}, with each position carrying the schematic",
        "* node that sits there in the layout (identified from the extracted",
        "* netlist's own device geometry; see build_dut.py). The body is",
        f"* design/ro_array_core.spice's .subckt {SCHEMATIC_CELL} and its two leaf",
        f"* subcircuits, transcribed unchanged, at {ring.key}'s {ring.instance} sizing. vsubs is",
        "* declared and unused: the schematic has no substrate-tap net.",
        "",
        f".subckt {ring.top} {' '.join(port_names)} {ring.params}",
        *body,
        ".ends",
        "",
    ]
    for leaf in ("ro_nand2", "ro_stage"):
        out += _subckt_block(design, leaf) + [""]
    return "\n".join(out)


def check_testbench(port_names: list[str], ring: Ring = RING1) -> None:
    xdut = next(
        (l for l in _logical_lines(ring.testbench.read_text()) if l.lower().startswith("xdut ")),
        None,
    )
    want = ["xdut", *port_names, ring.top]
    if xdut is None or xdut.split() != want:
        raise BuildError(
            f"{ring.testbench.relative_to(REPO_ROOT)}: xdut line must read {' '.join(want)!r}"
        )


def extract(outdir: Path, ring: Ring = RING1) -> str:
    out = outdir / f"{ring.top}.extracted.spice"
    subprocess.run(
        ["klt", "extract", ring.gds, "--deck", "gf180mcu", "--pdk", "gf180mcuD",
         "--top", ring.top, "--parasitics", "-o", str(out), "--format", "json"],
        cwd=REPO_ROOT, check=True, stdout=subprocess.DEVNULL,
    )
    return out.read_text()


def dut_header(text: str, ring: Ring = RING1) -> list[str]:
    for line in _logical_lines(text):
        if re.match(rf"^\.subckt\s+{ring.top}\b", line, re.I):
            return [t for t in line.split()[2:] if "=" not in t]
    raise BuildError(f"{ring.dut.relative_to(REPO_ROOT)}: no .subckt {ring.top}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ring", choices=sorted(RINGS), default="ring1",
                    help="which ring's fixture to build or check (default: ring1)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--verify-netlist", type=Path)
    mode.add_argument(
        "--check-source", action="store_true",
        help="offline: hold the committed DUT to design/ro_array_core.spice (no klt)",
    )
    args = ap.parse_args(argv)
    ring = RINGS[args.ring]
    rel = ring.dut.relative_to(REPO_ROOT)
    try:
        if args.check_source:
            problem = dut_source_problem(ring=ring)
            if problem:
                raise BuildError(problem)
            print(f"build_dut: {rel} matches source {source_identity(ring=ring)}")
            return 0
        if args.verify_netlist:
            got = extraction_port_map(args.verify_netlist.read_text(), ring)
            want = dut_header(ring.dut.read_text(), ring)
            if got != want:
                raise BuildError(
                    f"{args.verify_netlist}: ring positions resolve to {got}, "
                    f"but the committed DUT header is {want}"
                )
            print(f"build_dut: {args.verify_netlist} matches the DUT header position for position")
            return 0
        with tempfile.TemporaryDirectory() as tmp:
            ports = extraction_port_map(extract(Path(tmp), ring), ring)
        text = render_dut(ports, None, ring)
        if args.check:
            check_testbench(ports, ring)
            if not ring.dut.is_file() or ring.dut.read_text() != text:
                raise BuildError(f"{rel} is stale; re-run build_dut.py --ring {ring.key}")
            print(f"build_dut: {rel} is current")
            return 0
        ring.dut.parent.mkdir(parents=True, exist_ok=True)
        ring.dut.write_text(text)
        check_testbench(ports, ring)
        print(f"build_dut: wrote {rel} (ports: {' '.join(ports)})")
        return 0
    except (BuildError, subprocess.CalledProcessError) as exc:
        print(f"build_dut: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
