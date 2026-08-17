#!/usr/bin/env python3
"""Generate a cell-delay SDF for the post-route netlist (#147).

    python3 layout/digital/gen_sdf.py            # generate, check, commit
    python3 layout/digital/gen_sdf.py --check     # regenerate to scratch and diff; never writes

This is the digital half of item 7's ("post-layout verification") gate-level
re-run: back-annotated timing for
[`trng_top.pnr.v`](trng_top.pnr.v) (#111's as-built, post-route netlist),
consumed by `sim/tb/trng-top-post-route/` (#147) through
`klt functional-verification`'s `options.sdf` block.

What this generates, and what it deliberately does not
--------------------------------------------------------
`klt place-and-route`'s own `request.post_route_sdf` (issue #1002 upstream)
writes an SDF from a session with *real routed parasitics*, but it can only
do that after its own `request.post_route_spef` extracts those parasitics
from the merged DEF-to-GDS stream via `klt extract --parasitics` -- and that
merge is geometrically wrong for this design (2x scale factor in every
DEF-derived dimension, [klayout-tools#1090][klt1090], `layout/digital/README.md`'s
"Two defects this bring-up found" #1). Asking for `post_route_spef` here
would extract parasitics from that broken geometry and silently write an
SDF whose interconnect delays are wrong by a data-dependent factor -- worse
than not modeling interconnect delay at all, and not distinguishable from a
correct run without independently re-deriving the geometry bug's effect on
every net's RC.

So this script does not touch parasitic extraction. It links
`trng_top.pnr.v` directly against the resolved liberty at
[`CORNER`](#corner-and-clock) through OpenSTA (via `openroad -no_init -exit`,
no DEF, no floorplan, no placement) and writes the delays OpenSTA computes
from the library timing arcs and each net's own fan-out load -- real,
per-instance *cell* delay from the as-built (CTS-buffered, resized) netlist,
with **zero interconnect (wire) delay**, the same "lumped, zero-length net"
assumption a pre-layout SDF makes. `sim/tb/trng-top-post-route/README.md`
states this in the same "coverage honesty" style as
`layout/digital/README.md`'s DRC-deck gaps; this module's own docstring is
the authority on what the artefact contains.

Two more filters this script applies before committing the SDF, both
mechanical, both because Icarus Verilog 13.0 -- the simulator
`klt functional-verification`'s `engine: "icarus"` drives -- cannot consume
OpenSTA's raw `write_sdf` output against this design unedited. Neither
changes what is modeled (both only touch **already-zero** delay data or an
arc Icarus never created in the first place):

1. **The top-level, empty-`(INSTANCE)` `CELL` block.** `write_sdf` puts every
   net-level `INTERCONNECT` entry (net -> pin wiring, all zero here, per the
   note above) in one design-scope `CELL` block. Icarus's `$sdf_annotate`
   cannot resolve an `INTERCONNECT` entry whose source or destination is the
   design's own top-level port (`clk`, `raw_bit`, `str_data[31]`, ...) against
   the scope this repo's `$sdf_annotate` shim passes (`klt`'s own generated
   `klt_sdf_annotate` root, matching `hdl_toplevel` -- see
   `docs/design/sdf-annotate-feasibility-spike.md` upstream) -- every such
   entry fails with `SDF ERROR: ... Could not find intermodpath!` or
   `Could not find net`, regardless of the SDF's `DIVIDER`/`INSTANCE` naming
   (both tried live; neither resolves it). Since every entry in this block is
   `(0.000:0.000:0.000)` by construction (this script models no interconnect
   delay at all), dropping the whole block changes no delay value -- it only
   removes a diagnostic Icarus would otherwise raise over content that was
   always zero.
2. **`IOPATH` arcs Icarus's own parser cannot elaborate.** A handful of
   `gf180mcu_fd_sc_mcu9t5v0` cells (`xor2`/`xor3`/`xnor2`/`xnor3`/`mux2`/
   `mux4`/`addf`/`addh`) declare their select/toggle-input timing arc as an
   `ifnone`-qualified, edge-sensitive `specify` path (e.g. `mux2`'s
   `(posedge S => (Z:S))`). Icarus 13.0 rejects this shape at compile time
   (`sorry: ifnone with an edge-sensitive path is not supported`) and
   silently omits that one arc's `specify` entry -- non-fatal to the build,
   but it means the arc's `ModPath` never exists at simulation time, so
   `write_sdf`'s `IOPATH` for it fails to apply (`SDF ERROR: Unable to match
   ModPath S -> Z in ...`) even though every *other* arc on the same cell
   (its data-path arcs, unaffected) applies cleanly. `_ICARUS_UNSUPPORTED_ARCS`
   below is derived mechanically from the cell library's own Verilog model
   (see that constant's docstring) and this script drops exactly those
   `(celltype, from_pin, to_pin)` `IOPATH` entries -- the same "this exact
   arc was never applied on this exact simulator" statement `klt`'s own SDF
   diagnostic scan makes for `TIMINGCHECK` sections, at one level of
   granularity finer.

Both gaps are generic to Icarus + `write_sdf` + this cell library, not
specific to this design's netlist; see `layout/digital/README.md`'s "SDF
export" section for the friction-protocol issue this filed upstream (the
gf180-trng-specific write-up lives there, not in this docstring).

OpenROAD provisioning is the same story as `build.py`'s own: `openroad` has
no Homebrew formula, so `_ensure_openroad_reachable` falls back to
`../openroad_docker.sh` (the pinned `openroad/orfs` image) when no native
binary is on `$PATH`.

Corner and clock
-----------------
`CORNER = "ss_125C_3v00"` -- the same STA-binding corner `build.py` places
and routes against (`layout/digital/README.md`'s "Corners" section), not a
new pick. `CLOCK_PERIOD_NS = 50.0` mirrors `build.py`'s own
`CONSTRAINTS["clock_period_ns"]`. Neither is a ratified spec value; both are
restated here, not imported from `build.py`, to avoid a fragile
cross-script `import build` (this repo runs a `build.py` under every
`layout/{cells,blocks,rings}/<name>/` directory -- importing one by its bare
module name risks shadowing a different sibling script's `build` module in
whatever process ends up loading more than one).

[klt1090]: https://github.com/2AMLogic/klayout-tools/issues/1090
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DIGITAL_DIR = REPO_ROOT / "layout" / "digital"
REPORTS_DIR = DIGITAL_DIR / "reports"

sys.path.insert(0, str(REPO_ROOT))

from layout._klt import klt_version, resolve_pdk  # noqa: E402

HDL_TOPLEVEL = "trng_top"
CELL_LIBRARY = "gf180mcu_fd_sc_mcu9t5v0"
#: Same STA-binding corner `build.py` places and routes against -- see the
#: module docstring's "Corner and clock" section.
CORNER = "ss_125C_3v00"
#: Tech-LEF parasitic-extraction corner (`min`/`nom`/`max`) -- `nom` is what
#: `klt` itself resolves by default (`klayout_tools.pdk.lef_files`'s own
#: `_NOMINAL_TECH_LEF_CORNER`); restated here for the same "no cross-package
#: import of a private constant" reason as `CORNER` above. LEF is loaded so
#: `openroad`'s technology/library setup is complete before `link_design`;
#: this script never places or routes, so the tech LEF's own geometry is
#: unused, only its layer/via declarations OpenROAD's Tcl API expects to
#: exist before `read_liberty`/`link_design`.
TECH_LEF_CORNER = "nom"
CLOCK_PORT = "clk"
CLOCK_PERIOD_NS = 50.0

NETLIST_PATH = DIGITAL_DIR / f"{HDL_TOPLEVEL}.pnr.v"
SDF_PATH = DIGITAL_DIR / f"{HDL_TOPLEVEL}.sdf"
REPORT_PATH = REPORTS_DIR / "sdf_export.json"

#: `openroad_docker.sh` bind-mounts `$(pwd)` (== `REPO_ROOT`, since this
#: script always runs `openroad` with `cwd=REPO_ROOT`) into the container at
#: the identical absolute path -- the system tempdir (`/var/folders/...` on
#: macOS, `/tmp/...` on Linux) is *not* under that mount, so a scratch dir
#: there is invisible inside the container and `openroad` fails with
#: `cannot open '<path>'` the moment it tries to read the generated Tcl.
#: `build.py`'s own `WORK_DIR` docstring names this exact constraint; this
#: mirrors it rather than using `tempfile.TemporaryDirectory()`.
WORK_DIR = REPO_ROOT / "layout" / ".work" / "gen-sdf"

EXIT_OK = 0
EXIT_ENVIRONMENT = 3
EXIT_FLOW_FAILURE = 4
EXIT_STALE = 5

#: Every `(celltype, from_pin, to_pin)` IOPATH arc Icarus Verilog 13.0
#: cannot elaborate from `gf180mcu_fd_sc_mcu9t5v0`'s own Verilog timing
#: model, derived mechanically (2026-08-17) by scanning
#: `libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/gf180mcu_fd_sc_mcu9t5v0.v` for
#: `sorry: ifnone with an edge-sensitive path is not supported` compiler
#: diagnostics (`iverilog -g2012`, no design attached) and reading each
#: diagnostic's own preceding `// comb arc <edge> <pin> --> (<out>:<pin>)`
#: comment for the arc it names -- both directions (`posedge`/`negedge`)
#: collapse to the same unqualified `(IOPATH <pin> <out> ...)` text in
#: OpenSTA's `write_sdf` output (no edge qualifier survives), so the edge is
#: dropped from this key. Every cell in this set keeps its *other* arcs
#: (e.g. `mux2`'s `I0`/`I1` data paths); only the listed select/toggle arc is
#: unmodeled. See the module docstring's numbered filter list, item 2.
_ICARUS_UNSUPPORTED_ARCS: frozenset[tuple[str, str, str]] = frozenset(
    {
        (f"{CELL_LIBRARY}__{cell}", frm, to)
        for cell, frm, to in (
            ("addf_1", "A", "S"), ("addf_1", "B", "S"), ("addf_1", "CI", "S"),
            ("addf_2", "A", "S"), ("addf_2", "B", "S"), ("addf_2", "CI", "S"),
            ("addf_4", "A", "S"), ("addf_4", "B", "S"), ("addf_4", "CI", "S"),
            ("addh_1", "A", "S"), ("addh_1", "B", "S"),
            ("addh_2", "A", "S"), ("addh_2", "B", "S"),
            ("addh_4", "A", "S"), ("addh_4", "B", "S"),
            ("mux2_1", "S", "Z"), ("mux2_2", "S", "Z"), ("mux2_4", "S", "Z"),
            ("mux4_1", "S0", "Z"), ("mux4_1", "S1", "Z"),
            ("mux4_2", "S0", "Z"), ("mux4_2", "S1", "Z"),
            ("mux4_4", "S0", "Z"), ("mux4_4", "S1", "Z"),
            ("xnor2_1", "A1", "ZN"), ("xnor2_1", "A2", "ZN"),
            ("xnor2_2", "A1", "ZN"), ("xnor2_2", "A2", "ZN"),
            ("xnor2_4", "A1", "ZN"), ("xnor2_4", "A2", "ZN"),
            ("xnor3_1", "A1", "ZN"), ("xnor3_1", "A2", "ZN"), ("xnor3_1", "A3", "ZN"),
            ("xnor3_2", "A1", "ZN"), ("xnor3_2", "A2", "ZN"), ("xnor3_2", "A3", "ZN"),
            ("xnor3_4", "A1", "ZN"), ("xnor3_4", "A2", "ZN"), ("xnor3_4", "A3", "ZN"),
            ("xor2_1", "A1", "Z"), ("xor2_1", "A2", "Z"),
            ("xor2_2", "A1", "Z"), ("xor2_2", "A2", "Z"),
            ("xor2_4", "A1", "Z"), ("xor2_4", "A2", "Z"),
            ("xor3_1", "A1", "Z"), ("xor3_1", "A2", "Z"), ("xor3_1", "A3", "Z"),
            ("xor3_2", "A1", "Z"), ("xor3_2", "A2", "Z"), ("xor3_2", "A3", "Z"),
            ("xor3_4", "A1", "Z"), ("xor3_4", "A2", "Z"), ("xor3_4", "A3", "Z"),
        )
    }
)


class SdfError(RuntimeError):
    """An SDF generation run could not even be attempted, or produced no
    usable artefact."""


# --------------------------------------------------------------------------- #
# OpenROAD provisioning (same fallback build.py's own `_ensure_openroad_reachable`
# implements; duplicated rather than imported -- see the module docstring's
# "Corner and clock" note on why this file does not `import build`).
# --------------------------------------------------------------------------- #


def _openroad_on_path() -> bool:
    return shutil.which("openroad") is not None


def _ensure_openroad_reachable() -> list[str]:
    if _openroad_on_path():
        return []
    if shutil.which("docker") is None:
        return [
            "openroad is not on PATH and docker is not on PATH either -- "
            "see layout/digital/README.md's 'OpenROAD' section"
        ]
    shim_dir = Path(tempfile.mkdtemp(prefix="klt-openroad-shim-"))
    shim = shim_dir / "openroad"
    shim.symlink_to(REPO_ROOT / "layout" / "openroad_docker.sh")
    os.environ["PATH"] = f"{shim_dir}{os.pathsep}{os.environ.get('PATH', '')}"
    return []


def _check_environment() -> list[str]:
    missing = []
    if not NETLIST_PATH.is_file():
        missing.append(
            f"{NETLIST_PATH.relative_to(REPO_ROOT)} is missing -- run "
            "`python3 layout/digital/build.py` first (#111)"
        )
    pdk = resolve_pdk()
    if pdk is None:
        missing.append("no gf180mcu PDK install found (see sim/harness/pdk.py)")
    missing += _ensure_openroad_reachable()
    return missing


def _openroad_version() -> str | None:
    try:
        done = subprocess.run(
            ["openroad", "-version"], capture_output=True, text=True, timeout=60
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return (done.stdout or done.stderr).strip() or None


# --------------------------------------------------------------------------- #
# OpenSTA session: link the as-built netlist against the resolved liberty,
# no DEF, no placement, no routing -- write_sdf is purely a function of the
# netlist + liberty + clock constraint at that point.
# --------------------------------------------------------------------------- #


def _lib_paths(pdk) -> dict[str, Path]:
    lib_dir = pdk.path / "libs.ref" / CELL_LIBRARY
    return {
        "tech_lef": lib_dir / "techlef" / f"{CELL_LIBRARY}__{TECH_LEF_CORNER}.tlef",
        "cell_lef": lib_dir / "lef" / f"{CELL_LIBRARY}.lef",
        "liberty": lib_dir / "lib" / f"{CELL_LIBRARY}__{CORNER}.lib",
    }


def _write_tcl(tcl_path: Path, *, liberty: Path, tech_lef: Path, cell_lef: Path,
                raw_sdf_path: Path) -> None:
    lines = [
        f"read_lef {tech_lef}",
        f"read_lef {cell_lef}",
        f"read_liberty {liberty}",
        f"read_verilog {NETLIST_PATH}",
        f"link_design {HDL_TOPLEVEL}",
        f"create_clock -name {CLOCK_PORT} -period {CLOCK_PERIOD_NS} "
        f"[get_ports {CLOCK_PORT}]",
        f"write_sdf -divider . -include_typ {raw_sdf_path}",
    ]
    tcl_path.write_text("\n".join(lines) + "\n")


def _run_opensta(work_dir: Path) -> Path:
    """Run the Tcl script above through `openroad -no_init -exit`, and return
    the raw `write_sdf` output path.

    Raises `SdfError` on anything that stops a trustworthy SDF from coming
    out -- a missing binary, a non-zero `openroad` exit, or a run that wrote
    no file (`write_sdf` failing silently has not been observed, but the
    check costs nothing and matches every other flow driver in this
    directory's "never assume a tool wrote what it claims to" posture).
    """
    pdk = resolve_pdk()
    if pdk is None:
        raise SdfError("no gf180mcu PDK install found")
    paths = _lib_paths(pdk)
    for name, path in paths.items():
        if not path.is_file():
            raise SdfError(f"resolved PDK is missing its {name}: {path}")

    tcl_path = work_dir / "write_sdf.tcl"
    raw_sdf_path = work_dir / "raw.sdf"
    _write_tcl(
        tcl_path,
        liberty=paths["liberty"],
        tech_lef=paths["tech_lef"],
        cell_lef=paths["cell_lef"],
        raw_sdf_path=raw_sdf_path,
    )
    try:
        done = subprocess.run(
            ["openroad", "-no_init", "-exit", str(tcl_path)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=900,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise SdfError(f"could not launch openroad: {exc}") from exc
    if done.returncode != 0:
        tail = "\n".join((done.stdout + done.stderr).splitlines()[-20:])
        raise SdfError(f"openroad exited {done.returncode}:\n{tail}")
    if not raw_sdf_path.is_file():
        raise SdfError(
            "openroad reported success but wrote no SDF file -- "
            f"transcript tail:\n{(done.stdout + done.stderr)[-2000:]}"
        )
    return raw_sdf_path


# --------------------------------------------------------------------------- #
# SDF filtering -- a real S-expression parse/rewrite/serialize (not a
# line-based regex edit: SDF's `(...)` nesting is deep enough, and this
# design's own escaped instance names contain literal `/` characters, that a
# naive line-oriented strip corrupts the paren balance -- verified the hard
# way while building this script; the parser below round-trips an unedited
# file byte-for-byte before any filtering is applied).
# --------------------------------------------------------------------------- #

_TOKEN_RE = re.compile(r"\(|\)|[^\s()]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text)


def _parse(tokens: list[str]) -> list:
    pos = [0]

    def parse_one():
        assert tokens[pos[0]] == "("
        pos[0] += 1
        node: list = []
        while tokens[pos[0]] != ")":
            if tokens[pos[0]] == "(":
                node.append(parse_one())
            else:
                node.append(tokens[pos[0]])
                pos[0] += 1
        pos[0] += 1
        return node

    top = []
    while pos[0] < len(tokens):
        top.append(parse_one())
    return top


def _serialize(node: list) -> str:
    parts = [_serialize(c) if isinstance(c, list) else c for c in node]
    return "(" + " ".join(parts) + ")"


def _celltype_of(cell_node: list) -> str | None:
    for c in cell_node:
        if isinstance(c, list) and c and c[0] == "CELLTYPE":
            return c[1].strip('"')
    return None


def filter_sdf(raw_text: str) -> tuple[str, dict]:
    """Apply both filters the module docstring describes and return
    `(filtered_text, stats)`.

    `stats` records `dropped_interconnect_block` (bool),
    `dropped_iopath_arcs` (count) and `dropped_empty_cells` (count -- a cell
    whose *every* arc was in `_ICARUS_UNSUPPORTED_ARCS`, e.g. a 2-input
    `xnor2` whose only two arcs are both the select-adjacent one) so the
    committed report can state exactly how much was removed, not just that
    something was.
    """
    top = _parse(_tokenize(raw_text))
    if len(top) != 1 or top[0][0] != "DELAYFILE":
        raise SdfError("write_sdf output does not start with (DELAYFILE ...)")
    delayfile = top[0]

    new_children: list = []
    dropped_interconnect_block = False
    dropped_iopath_arcs = 0
    dropped_empty_cells = 0

    for child in delayfile[1:]:
        is_cell = isinstance(child, list) and child and child[0] == "CELL"
        if not is_cell:
            new_children.append(child)
            continue

        instance_node = next(
            (c for c in child if isinstance(c, list) and c and c[0] == "INSTANCE"),
            None,
        )
        is_top_scope_block = instance_node is not None and len(instance_node) == 1
        if is_top_scope_block:
            # The one design-scope CELL block: every entry inside it is an
            # INTERCONNECT, and every INTERCONNECT this script ever writes is
            # (0.000:0.000:0.000) (no interconnect delay is modeled) -- see
            # the module docstring's filter list, item 1.
            dropped_interconnect_block = True
            continue

        ctype = _celltype_of(child)
        new_cell = []
        for c in child:
            if isinstance(c, list) and c and c[0] == "DELAY":
                new_delay = ["DELAY"]
                for d in c[1:]:
                    if isinstance(d, list) and d and d[0] == "ABSOLUTE":
                        new_abs = ["ABSOLUTE"]
                        for entry in d[1:]:
                            if (
                                isinstance(entry, list)
                                and entry
                                and entry[0] == "IOPATH"
                                and (ctype, entry[1], entry[2]) in _ICARUS_UNSUPPORTED_ARCS
                            ):
                                dropped_iopath_arcs += 1
                                continue
                            new_abs.append(entry)
                        new_delay.append(new_abs)
                    else:
                        new_delay.append(d)
                new_cell.append(new_delay)
            else:
                new_cell.append(c)

        delay_node = next(c for c in new_cell if isinstance(c, list) and c[0] == "DELAY")
        abs_node = next(
            (c for c in delay_node if isinstance(c, list) and c and c[0] == "ABSOLUTE"),
            None,
        )
        if abs_node is not None and len(abs_node) == 1:
            dropped_empty_cells += 1
            continue

        new_children.append(new_cell)

    filtered = _serialize(["DELAYFILE"] + new_children) + "\n"
    stats = {
        "dropped_interconnect_block": dropped_interconnect_block,
        "dropped_iopath_arcs": dropped_iopath_arcs,
        "dropped_empty_cells": dropped_empty_cells,
    }
    return filtered, stats


# --------------------------------------------------------------------------- #
# entry points
# --------------------------------------------------------------------------- #


def generate(work_dir: Path) -> tuple[str, dict]:
    """Run the full pipeline into `work_dir` and return `(filtered_sdf_text,
    stats)`. Raises `SdfError` on any failure; writes nothing under
    `layout/digital/` itself -- that is `main()`'s job, once this succeeds."""
    missing = _check_environment()
    if missing:
        raise SdfError("; ".join(missing))
    raw_sdf_path = _run_opensta(work_dir)
    raw_text = raw_sdf_path.read_text()
    return filter_sdf(raw_text)


def _report(stats: dict, sdf_text: str) -> dict:
    pdk = resolve_pdk()
    return {
        "schema_version": 1,
        "engine": "opensta",
        "engine_version": _openroad_version(),
        "klt_version": klt_version(),
        "hdl_toplevel": HDL_TOPLEVEL,
        "netlist_path": str(NETLIST_PATH.relative_to(REPO_ROOT)),
        "sdf_path": str(SDF_PATH.relative_to(REPO_ROOT)),
        "pdk": {
            "name": pdk.variant if pdk else None,
            "cell_library": CELL_LIBRARY,
            "corner": CORNER,
            "tech_lef_corner": TECH_LEF_CORNER,
        },
        "clock": {"port": CLOCK_PORT, "period_ns": CLOCK_PERIOD_NS},
        "coverage": {
            "cell_delay": "modeled (per-instance IOPATH from the resolved "
            "liberty timing arcs, at the as-built netlist's real fan-out)",
            "interconnect_delay": "not modeled -- zero-length/zero-RC net "
            "assumption; no DEF, no placement, no parasitic extraction "
            "(see this script's own module docstring)",
            "min_typ_max": "identical -- one liberty corner only, no "
            "min/max variation written",
            "icarus_unsupported_arcs_excluded": stats["dropped_iopath_arcs"],
            "icarus_unsupported_cells_dropped_entirely": stats["dropped_empty_cells"],
            "top_level_interconnect_block_dropped": stats["dropped_interconnect_block"],
        },
        #: The committed file, byte for byte -- what an evidence record cites to
        #: pin down exactly which artefact it simulated.
        "sdf_sha256": hashlib.sha256(sdf_text.encode()).hexdigest(),
        #: The same text with `write_sdf`'s own wall-clock `(DATE ...)` line
        #: normalised away -- the *reproducible* hash, and the one `--check`
        #: compares. Both are recorded because they answer different
        #: questions: `sdf_sha256` identifies this file, `sdf_content_sha256`
        #: identifies its content independently of when it was generated.
        #: Recording only the byte hash makes `--check` unsatisfiable (the
        #: timestamp differs on every run); recording only the content hash
        #: leaves an evidence record unable to say which file it read.
        "sdf_content_sha256": hashlib.sha256(
            _normalize_for_diff(sdf_text).encode()
        ).hexdigest(),
    }


def _normalize_for_diff(sdf_text: str) -> str:
    """Drop the one non-deterministic field (`write_sdf`'s own wall-clock
    `(DATE ...)` line) before comparing two runs -- everything else this
    script produces is a pure function of the committed netlist + the
    resolved liberty + the constants above, so a real change shows up as a
    real diff."""
    return re.sub(r'\(DATE "[^"]*"\)', '(DATE "<normalized>")', sdf_text, count=1)


def _fresh_work_dir(work_dir: Path) -> None:
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)


def build() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _fresh_work_dir(WORK_DIR)
    try:
        sdf_text, stats = generate(WORK_DIR)
    except SdfError as exc:
        print(f"ERROR  {exc}", file=sys.stderr)
        return EXIT_FLOW_FAILURE
    SDF_PATH.write_text(sdf_text)
    report = _report(stats, sdf_text)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote  {SDF_PATH.relative_to(REPO_ROOT)}")
    print(f"wrote  {REPORT_PATH.relative_to(REPO_ROOT)}")
    print(f"corner: {CELL_LIBRARY}__{CORNER}  clock: {CLOCK_PERIOD_NS}ns")
    print(
        f"dropped {stats['dropped_iopath_arcs']} Icarus-unsupported IOPATH "
        f"arcs, {stats['dropped_empty_cells']} now-empty CELL blocks, "
        f"top-level INTERCONNECT block: {stats['dropped_interconnect_block']}"
    )
    return EXIT_OK


def check() -> int:
    if not SDF_PATH.is_file() or not REPORT_PATH.is_file():
        print(
            f"MISSING: {SDF_PATH.relative_to(REPO_ROOT)} / "
            f"{REPORT_PATH.relative_to(REPO_ROOT)} -- run "
            "`python3 layout/digital/gen_sdf.py`"
        )
        return EXIT_STALE
    check_dir = WORK_DIR.parent / "gen-sdf-check"
    _fresh_work_dir(check_dir)
    try:
        fresh_text, stats = generate(check_dir)
    except SdfError as exc:
        print(f"ERROR  {exc}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    committed_text = SDF_PATH.read_text()
    if _normalize_for_diff(committed_text) != _normalize_for_diff(fresh_text):
        print(
            f"STALE  {SDF_PATH.relative_to(REPO_ROOT)}: committed SDF does "
            "not match a fresh run (DATE line excluded)"
        )
        return EXIT_STALE

    # The committed report must describe the committed *file*, byte for byte --
    # this is what catches a hand-edited SDF, which the fresh-run diff above
    # cannot (it deliberately normalises the timestamp away).
    committed_report = json.loads(REPORT_PATH.read_text())
    committed_digest = hashlib.sha256(committed_text.encode()).hexdigest()
    if committed_report.get("sdf_sha256") != committed_digest:
        print(
            f"STALE  {REPORT_PATH.relative_to(REPO_ROOT)}: its sdf_sha256 does "
            f"not match {SDF_PATH.relative_to(REPO_ROOT)} as committed "
            f"({committed_report.get('sdf_sha256')} vs {committed_digest})"
        )
        return EXIT_STALE

    # Everything else must match a fresh run. `sdf_sha256` is excluded because
    # it hashes `write_sdf`'s own wall-clock `(DATE ...)` line and therefore
    # differs on every run by construction -- comparing it here would make
    # `--check` permanently unsatisfiable. `sdf_content_sha256`, which is the
    # same text with that line normalised, IS compared, so the artefact's
    # content is still checked rather than trusted.
    fresh_report = _report(stats, fresh_text)
    volatile = ("sdf_sha256",)
    fresh_view = {k: v for k, v in fresh_report.items() if k not in volatile}
    committed_view = {k: v for k, v in committed_report.items() if k not in volatile}
    if fresh_view != committed_view:
        differing = sorted(
            k
            for k in set(fresh_view) | set(committed_view)
            if fresh_view.get(k) != committed_view.get(k)
        )
        print(
            f"STALE  {REPORT_PATH.relative_to(REPO_ROOT)}: committed report "
            f"does not match a fresh run (fields: {', '.join(differing)})"
        )
        return EXIT_STALE

    print(f"OK  {SDF_PATH.relative_to(REPO_ROOT)} matches a fresh run")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gen_sdf.py",
        description=(
            "Generate a cell-delay SDF for trng_top's post-route netlist "
            "(#147) and commit it."
        ),
    )
    parser.add_argument(
        "--check", action="store_true",
        help="regenerate to scratch and diff against the committed SDF/report; never writes",
    )
    args = parser.parse_args(argv)
    return check() if args.check else build()


if __name__ == "__main__":
    raise SystemExit(main())
