#!/usr/bin/env python3
"""Generate the schematic-side DUT for the `klt pex` run over combiner_sampler.

    python3 sim/tb/combiner-sampler-pex/build_dut.py            # extract, write the DUT
    python3 sim/tb/combiner-sampler-pex/build_dut.py --check    # extract to scratch, fail if it would change
    python3 sim/tb/combiner-sampler-pex/build_dut.py --check-source
                                                                # offline: DUT vs design source, no klt
    python3 sim/tb/combiner-sampler-pex/build_dut.py --verify-netlist <extracted.spice>
                                                                # hold a klt-pex-written netlist to the DUT

`--check` and the default mode run `klt extract`; set `KLT` to choose the
binary (for example `KLT="uvx --from klayout-tools==0.6.0 --with
klayout==0.30.10 klt"` for DR-0026's producer build). The other two modes
need no klt, ngspice or PDK.

Why this file exists
--------------------
`klt pex` (klt 0.6.0) re-runs one `klt sim` testbench twice: once as written,
with its one `.include` naming the schematic DUT, and once with that line
re-pointed at the netlist it extracted from the layout. The testbench's
`xdut` line is reused byte for byte, so the two `.SUBCKT combiner_sampler`
headers must agree position by position.

`klt extract` over `layout/blocks/combiner_sampler/combiner_sampler.gds`
promotes fourteen ports, named after whatever labels sit on each net inside
the instanced cells: `a a$1 a|d|y b|d|y clk d|vdd d|y q q$1 q$2 q$3 rst_n
vss vsubs` as of klt 0.6.0. Five of those (`a`, `a$1`, `q` .. `q$3`) say
nothing about which schematic net they are, and three more are merged-label
names. The layout's own LVS reference (`combiner_sampler.spice`) uses a
different port list again. This script writes a schematic `combiner_sampler`
whose header carries, at each extraction position, the schematic net that
sits there in the layout, so the block's internal buffer outputs (`ro1`,
`ro2`) and XOR output (`xo`) become observable ports on both sides.

How each port is identified
---------------------------
By connectivity and device evidence, never by the extractor's names alone.
Both netlists are reduced to a bipartite graph of MOSFETs and nets:

* extracted side: every parasitic resistor's two nodes are merged into one
  net (the lumped star the deck writes per net); resistors to the global
  ground node `0` (the deck's `vsubs` DC tie) are not wires and are skipped;
  capacitors are ignored;
* schematic side: the rendered DUT, flattened through its subcircuits;
* each device is labelled by (model, W, L); each net by which devices touch
  it as gate or as source/drain (source and drain are interchangeable).
  Bulk terminals are ignored -- the extraction puts every PMOS body on an
  anonymous floating well net and every NMOS body on `vsubs`, the schematic
  ties them to `vdd`/`vss`; that difference is the documented `body_bias`
  limitation, not a connectivity difference to resolve here.

Colour refinement (1-dimensional Weisfeiler-Leman) runs over both graphs
jointly until the partition stops splitting. Every colour class must hold
equally many devices and nets on both sides, else the two netlists are not
the same circuit and the mapping is refused. Each extracted port must then
land in a class holding exactly one extracted net and exactly one schematic
net; a class with two or more nets is an ambiguity (a symmetry refinement
cannot break) and is refused rather than guessed. Finally, any extracted port
whose label set names a schematic top-level net (`clk`, `rst_n`, `vss`,
`vdd`) must resolve to that net, so the labels can veto but never decide.
`vsubs` has no schematic counterpart and is passed through by name; it must
touch no gate, source or drain.

`--verify-netlist` runs the same derivation over the netlist a `klt pex` run
actually extracted and simulated and fails unless it reproduces the committed
DUT header exactly.

Source identity
---------------
The DUT body is transcribed from two generated design sources:
`design/ro_array_core.spice` (the `xb1`/`xb2`/`xa1` instances and the
`ro_buf`/`xor2` subcircuits) and `design/sampler_core.spice` (the
`xsb`/`xsv`/`xsr1`/`xsr2` instances and the `sampler_dff` subcircuit).
`design/sampler_core.spice` also embeds its own copies of `ro_buf`, `xor2`
and the three `ro_array_core` instance lines; those must agree with
`design/ro_array_core.spice` (comments and whitespace aside) or the render is
refused. `source_identity()` hashes exactly the consumed sections, so edits to
the rings, to other cells or to comments do not invalidate evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shlex
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
ARRAY_SRC = REPO_ROOT / "design" / "ro_array_core.spice"
SAMPLER_SRC = REPO_ROOT / "design" / "sampler_core.spice"
GDS = "layout/blocks/combiner_sampler/combiner_sampler.gds"
TOP = "combiner_sampler"
DUT = HERE / "combiner_sampler_schematic.spice"
TESTBENCH = HERE / "tb_combiner_sampler_pex.sp"

#: (source file, parent subckt, instance names) whose lines form the DUT body.
CONSUMED_INSTANCES = (
    (ARRAY_SRC, "ro_array_core", ("xb1", "xb2", "xa1")),
    (SAMPLER_SRC, "sampler_core", ("xsb", "xsv", "xsr1", "xsr2")),
)
#: (source file, subckt) leaf cells transcribed verbatim into the DUT.
CONSUMED_SUBCKTS = (
    (ARRAY_SRC, "ro_buf"),
    (ARRAY_SRC, "xor2"),
    (SAMPLER_SRC, "sampler_dff"),
)
#: Copies inside design/sampler_core.spice that must equal the ARRAY_SRC ones.
MIRRORED_IN_SAMPLER = ("ro_buf", "xor2")
#: Schematic top-level nets an extracted label may name (labels veto only).
LABEL_VETO_NETS = ("clk", "rst_n", "vss", "vdd")
#: Extracted ports with no schematic counterpart, passed through by name.
PASSTHROUGH_PORTS = ("vsubs",)
MOS_MODELS = ("nfet_03v3", "pfet_03v3")

_PARAM = re.compile(r"^([A-Za-z_]\w*)=(.*)$")
_SCALE = {"t": 1e12, "g": 1e9, "meg": 1e6, "k": 1e3, "m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15}


class BuildError(Exception):
    pass


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------- source

def _logical_lines(text: str) -> list[str]:
    out: list[str] = []
    for raw in text.splitlines():
        if raw.startswith("+") and out:
            out[-1] += " " + raw[1:].strip()
        else:
            out.append(raw.rstrip())
    return out


def _subckt_block(text: str, name: str, where: str) -> list[str]:
    """Raw lines of `.subckt name` .. `.ends` (exactly one definition)."""
    lines = text.splitlines()
    starts = [i for i, l in enumerate(lines) if re.match(rf"^\.subckt\s+{re.escape(name)}\s", l + " ", re.I)]
    if len(starts) != 1:
        raise BuildError(f"{where}: expected one .subckt {name}, found {len(starts)}")
    start = starts[0]
    end = next((i for i in range(start, len(lines)) if re.match(r"^\.ends\b", lines[i], re.I)), None)
    if end is None:
        raise BuildError(f"{where}: .subckt {name} has no .ends")
    return lines[start : end + 1]


def _canonical(lines: list[str]) -> list[str]:
    """Logical lines without comments/blank lines, whitespace collapsed."""
    return [
        " ".join(l.split())
        for l in _logical_lines("\n".join(lines))
        if l.strip() and not l.lstrip().startswith("*")
    ]


def _instance_line(text: str, parent: str, inst: str, where: str) -> str:
    body = _canonical(_subckt_block(text, parent, where))
    hits = [l for l in body if l.split()[0].lower() == inst]
    if len(hits) != 1:
        raise BuildError(f"{where}: expected one {inst} in .subckt {parent}, found {len(hits)}")
    return hits[0]


def _read_sources(sources: dict[Path, str] | None) -> dict[Path, str]:
    if sources is not None:
        return sources
    return {ARRAY_SRC: ARRAY_SRC.read_text(), SAMPLER_SRC: SAMPLER_SRC.read_text()}


def audit_sources(sources: dict[Path, str] | None = None) -> None:
    """Refuse when design/sampler_core.spice's embedded copies of the
    combiner cells disagree with design/ro_array_core.spice's."""
    src = _read_sources(sources)
    for name in MIRRORED_IN_SAMPLER:
        a = _canonical(_subckt_block(src[ARRAY_SRC], name, _rel(ARRAY_SRC)))
        b = _canonical(_subckt_block(src[SAMPLER_SRC], name, _rel(SAMPLER_SRC)))
        if a != b:
            raise BuildError(
                f".subckt {name} differs between {_rel(ARRAY_SRC)} and {_rel(SAMPLER_SRC)}; "
                f"regenerate the design netlists (design/netlist.py)"
            )
    for inst in ("xb1", "xb2", "xa1"):
        a = _instance_line(src[ARRAY_SRC], "ro_array_core", inst, _rel(ARRAY_SRC))
        b = _instance_line(src[SAMPLER_SRC], "ro_array_core", inst, _rel(SAMPLER_SRC))
        if a != b:
            raise BuildError(
                f"instance {inst} differs between {_rel(ARRAY_SRC)} ({a!r}) and "
                f"{_rel(SAMPLER_SRC)} ({b!r})"
            )


def consumed_source(sources: dict[Path, str] | None = None) -> str:
    """Canonical text of exactly the design sections the DUT is built from."""
    src = _read_sources(sources)
    parts: list[str] = []
    for path, parent, insts in CONSUMED_INSTANCES:
        for inst in insts:
            parts.append(f"{_rel(path)}:{parent}: {_instance_line(src[path], parent, inst, _rel(path))}")
    for path, name in CONSUMED_SUBCKTS:
        parts.append(f"{_rel(path)}:")
        parts += _canonical(_subckt_block(src[path], name, _rel(path)))
    return "\n".join(parts) + "\n"


def source_identity(sources: dict[Path, str] | None = None) -> str:
    return "sha256:" + hashlib.sha256(consumed_source(sources).encode()).hexdigest()


def body_nets(sources: dict[Path, str] | None = None) -> list[str]:
    """Every net the DUT's top-level instance lines touch, first-seen order."""
    src = _read_sources(sources)
    nets: list[str] = []
    for path, parent, insts in CONSUMED_INSTANCES:
        for inst in insts:
            toks = _instance_line(src[path], parent, inst, _rel(path)).split()
            for n in toks[1:-1]:
                if "=" not in n and n not in nets:
                    nets.append(n)
    return nets


def render_dut(port_names: list[str], sources: dict[Path, str] | None = None) -> str:
    src = _read_sources(sources)
    audit_sources(src)
    known = set(body_nets(src)) | set(PASSTHROUGH_PORTS)
    unknown = [p for p in port_names if p not in known]
    if unknown:
        raise BuildError(f"DUT header names nets the design body does not have: {unknown}")
    if len(set(port_names)) != len(port_names):
        raise BuildError(f"DUT header repeats a port: {port_names}")
    out = [
        f"* {TOP} schematic-side DUT for the klt pex run over its layout.",
        "* GENERATED by sim/tb/combiner-sampler-pex/build_dut.py -- do not edit by hand.",
        "*",
        "* The header is klt extract's port order for",
        f"* {GDS}, with each position carrying the",
        "* schematic net that sits there in the layout (identified by connectivity;",
        "* see build_dut.py). The instance lines are design/ro_array_core.spice's",
        "* xb1/xb2/xa1 and design/sampler_core.spice's xsb/xsv/xsr1/xsr2; the leaf",
        "* subcircuits are transcribed unchanged. vsubs is declared and unused: the",
        "* schematic has no substrate-tap net.",
        "",
        f".subckt {TOP} {' '.join(port_names)}",
    ]
    for path, parent, insts in CONSUMED_INSTANCES:
        for inst in insts:
            out.append(_instance_line(src[path], parent, inst, _rel(path)))
    out += [".ends", ""]
    for path, name in CONSUMED_SUBCKTS:
        out += _subckt_block(src[path], name, _rel(path)) + [""]
    return "\n".join(out)


def dut_header(text: str) -> list[str]:
    for line in _logical_lines(text):
        if re.match(rf"^\.subckt\s+{TOP}\b", line, re.I):
            return [t for t in line.split()[2:] if "=" not in t]
    raise BuildError(f"{_rel(DUT)}: no .subckt {TOP}")


def dut_source_problem(dut_text: str | None = None, sources: dict[Path, str] | None = None) -> str | None:
    """None if the committed DUT is exactly render_dut() of the current source
    at the DUT's own header; otherwise a diagnostic. No klt/ngspice/PDK."""
    try:
        dut = DUT.read_text() if dut_text is None else dut_text
        want = render_dut(dut_header(dut), sources)
    except (BuildError, OSError) as exc:
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
        f"{_rel(DUT)} does not match the design source (first differences: "
        f"{'; '.join(diff[:4])}); re-run build_dut.py, then signoff/publish_combiner_sampler_pex.py"
    )


# ------------------------------------------------------- connectivity graph

def _num(tok: str) -> float:
    m = re.match(r"^([-+]?[\d.]+(?:e[-+]?\d+)?)([a-z]*)$", tok.strip().lower())
    if not m:
        raise BuildError(f"cannot read {tok!r} as a number")
    scale = 1.0
    for suffix, factor in _SCALE.items():
        if m.group(2).startswith(suffix):
            scale = factor
            break
    return float(m.group(1)) * scale


class Graph:
    """MOSFETs as (kind, gate net, frozenset of source/drain nets)."""

    def __init__(self) -> None:
        self.devices: list[tuple[tuple[str, float, float], str, tuple[str, str]]] = []

    def add(self, model: str, w: float, l: float, d: str, g: str, s: str) -> None:
        # W/L rounded to 1 pm so "0.44u" and "0.44U" agree.
        self.devices.append(((model.lower(), round(w * 1e12), round(l * 1e12)), g, (d, s)))

    def nets(self) -> set[str]:
        out: set[str] = set()
        for _k, g, sd in self.devices:
            out.add(g)
            out.update(sd)
        return out


def _device_params(toks: list[str]) -> tuple[str, dict[str, str], list[str]]:
    params = {}
    pos = []
    for t in toks:
        m = _PARAM.match(t)
        if m:
            params[m.group(1).lower()] = m.group(2)
        else:
            pos.append(t)
    return pos[-1], params, pos[:-1]


def schematic_graph(dut_text: str) -> tuple[Graph, list[str]]:
    """Flatten the DUT text from `.subckt combiner_sampler` down to MOSFETs."""
    lines = _logical_lines(dut_text)
    subckts: dict[str, tuple[list[str], list[str]]] = {}
    cur: str | None = None
    for line in lines:
        toks = line.split()
        if not toks or toks[0].startswith("*"):
            continue
        if toks[0].lower() == ".subckt":
            cur = toks[1].lower()
            subckts[cur] = ([t for t in toks[2:] if "=" not in t], [])
        elif toks[0].lower() == ".ends":
            cur = None
        elif cur is not None:
            subckts[cur][1].append(line)
    if TOP not in subckts:
        raise BuildError(f"schematic DUT declares no .subckt {TOP}")
    graph = Graph()

    def expand(name: str, binding: dict[str, str], prefix: str, depth: int) -> None:
        if depth > 8:
            raise BuildError("schematic hierarchy too deep")
        ports, body = subckts[name]
        local = lambda n: binding.get(n, f"{prefix}{n}")  # noqa: E731
        for line in body:
            # Quoted expressions (`ad='int((nf+1)/2) * W/nf * 0.18u'`) are one token.
            toks = shlex.split(line)
            if toks[0][0] in "Xx":
                target, params, nodes = _device_params(toks[1:])
                if target.lower() in MOS_MODELS:
                    if len(nodes) != 4:
                        raise BuildError(f"schematic device {toks[0]}: expected d g s b")
                    d, g, s, _b = (local(n) for n in nodes)
                    graph.add(target, _num(params["w"]), _num(params["l"]), d, g, s)
                elif target.lower() in subckts:
                    sub_ports = subckts[target.lower()][0]
                    if len(nodes) != len(sub_ports):
                        raise BuildError(f"schematic instance {toks[0]}: pin count mismatch")
                    expand(
                        target.lower(),
                        {p: local(n) for p, n in zip(sub_ports, nodes)},
                        f"{prefix}{toks[0].lower()}/",
                        depth + 1,
                    )
                else:
                    raise BuildError(f"schematic instance {toks[0]}: unknown subckt/model {target}")
            elif toks[0][0] in "Cc":
                continue  # lumped wiring estimates do not change connectivity
            elif toks[0][0] in "Mm":
                raise BuildError(f"schematic line {toks[0]}: bare M devices are not expected here")
            # other elements (none in the consumed cells) are ignored

    expand(TOP, {p: p for p in subckts[TOP][0]}, "", 0)
    return graph, subckts[TOP][0]


def extracted_graph(netlist_text: str) -> tuple[Graph, list[str], dict[str, str]]:
    """(graph over resistor-merged nets, header ports, port -> net root)."""
    lines = _logical_lines(netlist_text)
    header = next(
        (l.split()[2:] for l in lines if re.match(rf"^\.SUBCKT\s+{TOP}\b", l, re.I)),
        None,
    )
    if header is None:
        raise BuildError(f"extracted netlist declares no .SUBCKT {TOP}")
    parent: dict[str, str] = {}

    def find(n: str) -> str:
        parent.setdefault(n, n)
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n

    raw_devices = []
    for line in lines:
        toks = line.split()
        if not toks or toks[0].startswith(("*", ".")):
            continue
        if toks[0][0] in "Rr" and len(toks) >= 4:
            a, b = toks[1], toks[2]
            if "0" in (a, b):
                continue  # a DC tie to ground (the deck's vsubs tie), not a wire
            parent[find(a)] = find(b)
        elif toks[0][0] in "Xx":
            model, params, nodes = _device_params(toks[1:])
            if model.lower() not in MOS_MODELS:
                raise BuildError(f"extracted device {toks[0]}: unexpected model {model}")
            if len(nodes) != 4:
                raise BuildError(f"extracted device {toks[0]}: expected d g s b")
            raw_devices.append((model, _num(params["w"]), _num(params["l"]), nodes))
    graph = Graph()
    for model, w, l, (d, g, s, _b) in raw_devices:
        graph.add(model, w, l, find(d), find(g), find(s))
    return graph, header, {p: find(p) for p in header}


def _refine(ref: Graph, ext: Graph) -> tuple[dict[str, int], dict[str, int]]:
    """Joint colour refinement; returns final net colours for each side."""
    sides = []
    for g in (ref, ext):
        nets = sorted(g.nets())
        attached: dict[str, list[tuple[int, str]]] = defaultdict(list)
        for i, (_k, gate, sd) in enumerate(g.devices):
            attached[gate].append((i, "g"))
            for n in sd:
                attached[n].append((i, "sd"))
        sides.append({"g": g, "nets": nets, "att": attached})

    def relabel(sigs_by_side: list[dict]) -> list[dict]:
        palette = {s: i for i, s in enumerate(sorted({repr(v) for side in sigs_by_side for v in side.values()}))}
        return [{k: palette[repr(v)] for k, v in side.items()} for side in sigs_by_side]

    dev_col = relabel([{i: d[0] for i, d in enumerate(s["g"].devices)} for s in sides])
    net_col = relabel([{n: 0 for n in s["nets"]} for s in sides])
    classes = -1
    for _ in range(4 * (len(ref.devices) + 4)):
        new_dev = relabel([
            {
                i: (dev_col[k][i], net_col[k][gate], tuple(sorted(net_col[k][n] for n in sd)))
                for i, (_kind, gate, sd) in enumerate(s["g"].devices)
            }
            for k, s in enumerate(sides)
        ])
        new_net = relabel([
            {
                n: (net_col[k][n], tuple(sorted((dev_col[k][i], role) for i, role in s["att"][n])))
                for n in s["nets"]
            }
            for k, s in enumerate(sides)
        ])
        count = len({c for side in new_dev for c in side.values()}) + len(
            {c for side in new_net for c in side.values()}
        )
        dev_col, net_col = new_dev, new_net
        if count == classes:
            break
        classes = count
    # Every class must be equally populated on both sides.
    for what, cols in (("device", dev_col), ("net", net_col)):
        a, b = Counter(cols[0].values()), Counter(cols[1].values())
        if a != b:
            diff = sum(((a - b) + (b - a)).values())
            raise BuildError(
                f"schematic and extracted netlists are not the same circuit: {diff} {what} "
                f"class member(s) unmatched after refinement (schematic {len(ref.devices)} "
                f"devices / {len(ref.nets())} nets, extracted {len(ext.devices)} / {len(ext.nets())})"
            )
    return net_col[0], net_col[1]


def extraction_port_map(netlist_text: str, dut_text: str | None = None,
                        sources: dict[Path, str] | None = None) -> list[str]:
    """Schematic net name for each port position of the extracted header."""
    if dut_text is None:
        # The order the DUT is rendered in does not affect its connectivity.
        dut_text = render_dut(body_nets(sources) + list(PASSTHROUGH_PORTS), sources)
    ref, ref_ports = schematic_graph(dut_text)
    ext, header, port_net = extracted_graph(netlist_text)
    if len(set(header)) != len(header):
        raise BuildError(f"extracted header repeats a port name: {header}")
    for p in PASSTHROUGH_PORTS:
        if header.count(p) != 1:
            raise BuildError(f"extracted header names {p!r} {header.count(p)} times")
    roots = [port_net[p] for p in header]
    if len(set(roots)) != len(roots):
        raise BuildError("two extracted ports resolve to one net through the parasitic resistors")
    ref_col, ext_col = _refine(ref, ext)
    ref_by_col: dict[int, list[str]] = defaultdict(list)
    for n, c in ref_col.items():
        ref_by_col[c].append(n)
    ext_by_col: dict[int, list[str]] = defaultdict(list)
    for n, c in ext_col.items():
        ext_by_col[c].append(n)
    ext_nets = ext.nets()
    out: list[str] = []
    for p in header:
        if p in PASSTHROUGH_PORTS:
            if port_net[p] in ext_nets:
                raise BuildError(f"{p!r} touches a device gate/source/drain; it should be bulk-only")
            out.append(p)
            continue
        net = port_net[p]
        if net not in ext_nets:
            raise BuildError(f"extracted port {p!r} touches no device gate, source or drain")
        col = ext_col[net]
        if len(ext_by_col[col]) != 1 or len(ref_by_col[col]) != 1:
            raise BuildError(
                f"extracted port {p!r} is ambiguous: its connectivity class holds "
                f"{len(ext_by_col[col])} extracted and {len(ref_by_col[col])} schematic net(s) "
                f"({sorted(ref_by_col[col])}); refusing to guess"
            )
        name = ref_by_col[col][0]
        if name not in ref_ports:
            raise BuildError(
                f"extracted port {p!r} resolves to schematic net {name!r}, which is internal "
                f"to a cell, not a {TOP} net"
            )
        labels = set(p.replace("$", "|").split("|"))
        for veto in LABEL_VETO_NETS:
            if veto in labels and name != veto:
                raise BuildError(
                    f"extracted port {p!r} carries label {veto!r} but resolves to {name!r} by connectivity"
                )
        out.append(name)
    if len(set(out)) != len(out):
        raise BuildError(f"two extracted ports resolve to one schematic net: {out}")
    return out


# -------------------------------------------------------------------- CLI

def check_testbench(port_names: list[str]) -> None:
    xdut = next(
        (l for l in _logical_lines(TESTBENCH.read_text()) if l.lower().startswith("xdut ")),
        None,
    )
    want = ["xdut", *port_names, TOP]
    if xdut is None or xdut.split() != want:
        raise BuildError(f"{_rel(TESTBENCH)}: xdut line must read {' '.join(want)!r}")


def extract(outdir: Path) -> str:
    out = outdir / f"{TOP}.extracted.spice"
    klt = shlex.split(os.environ.get("KLT", "klt"))
    subprocess.run(
        [*klt, "extract", GDS, "--deck", "gf180mcu", "--pdk", "gf180mcuD",
         "--top", TOP, "--parasitics", "-o", str(out), "--format", "json"],
        cwd=REPO_ROOT, check=True, stdout=subprocess.DEVNULL,
    )
    return out.read_text()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--verify-netlist", type=Path)
    mode.add_argument("--check-source", action="store_true",
                      help="offline: hold the committed DUT to the design source (no klt)")
    args = ap.parse_args(argv)
    try:
        if args.check_source:
            problem = dut_source_problem()
            if problem:
                raise BuildError(problem)
            print(f"build_dut: {_rel(DUT)} matches source {source_identity()}")
            return 0
        if args.verify_netlist:
            got = extraction_port_map(args.verify_netlist.read_text(), DUT.read_text())
            want = dut_header(DUT.read_text())
            if got != want:
                raise BuildError(
                    f"{args.verify_netlist}: ports resolve to {got}, but the committed DUT header is {want}"
                )
            print(f"build_dut: {args.verify_netlist} matches the DUT header position for position")
            return 0
        with tempfile.TemporaryDirectory() as tmp:
            ports = extraction_port_map(extract(Path(tmp)))
        text = render_dut(ports)
        check_testbench(ports)
        if args.check:
            if not DUT.is_file() or DUT.read_text() != text:
                raise BuildError(f"{_rel(DUT)} is stale; re-run build_dut.py")
            print(f"build_dut: {_rel(DUT)} is current")
            return 0
        DUT.write_text(text)
        print(f"build_dut: wrote {_rel(DUT)} (ports: {' '.join(ports)})")
        return 0
    except (BuildError, subprocess.CalledProcessError, OSError) as exc:
        print(f"build_dut: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
