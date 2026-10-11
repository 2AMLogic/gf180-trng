"""Testbench manifests.

Testbenches follow the directory convention ratified in ``sim/README.md``:

    sim/tb/<testbench-slug>/tb.json            the manifest (this module)
    sim/tb/<testbench-slug>/<something>.spice  a *netlist fragment*

The fragment must NOT contain ``.include`` of models, ``.lib``, ``.temp``,
``.control``, ``.endc`` or ``.end``: the harness owns all of those so that
one netlist can be swept across the whole PVT grid without editing. The
harness hands the fragment these parameters:

    vdd_val   the supply for this PVT point (nominal, +tol or -tol)
    vdd_nom   the nominal supply, for ratio-style measurements
    temp_c    the temperature for this PVT point (also set via .temp)

plus anything in the manifest's ``params`` map, and (for stochastic
testbenches) the seed injected via ``.option seed=<value>``.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path

from .corners import (
    DEFAULT_CORNER_SET,
    DEFAULT_NOMINAL_SUPPLY_V,
    DEFAULT_SUPPLY_TOLERANCE,
    DEFAULT_TEMPERATURES_C,
)

MANIFEST_NAME = "tb.json"

#: Every testbench lives directly under sim/tb/<slug>/, per sim/README.md.
TB_ROOT_DIRNAME = "tb"

#: ``.inc`` is ngspice's abbreviation of ``.include``. Includes are rejected
#: in the testbench fragment. The DUT netlist may ``.include`` sibling files
#: (the extracted-parasitics netlists do); those are captured and frozen with
#: it -- see ``DUT_INCLUDE_DIRECTIVES`` and ``_capture_dut_dependencies``.
FORBIDDEN_DIRECTIVES = (
    ".control", ".endc", ".end", ".lib", ".temp", ".include", ".inc",
)

#: Directives the DUT netlist may use to pull in sibling files. Only a bare
#: file name resolving next to the DUT is supported (it is snapshotted next to
#: the DUT snapshot under the same name, so ngspice resolves it identically);
#: anything else is rejected before launch.
DUT_INCLUDE_DIRECTIVES = (".include", ".inc")

#: Fixed file names of the per-invocation input snapshots (raw dir / deck dir).
FRAGMENT_SNAPSHOT_NAME = "tb.fragment.spice"
DUT_SNAPSHOT_NAME = "dut.netlist.spice"

#: analysis.type values sim/README.md's frontmatter recognizes as stochastic
#: (i.e. subject to the "no seed, no evidence" rule).
STOCHASTIC_ANALYSIS_TYPES = ("tran-noise", "mc")

#: Every analysis type a manifest may declare. ``op`` is the default when
#: ``analysis_type`` is absent. The type is metadata that drives seed
#: enforcement, so an unrecognised token (e.g. a misspelt ``tran-noise``)
#: is rejected at load rather than silently planned as deterministic.
SUPPORTED_ANALYSIS_TYPES = ("op", "tran", "tran-noise", "noise", "ac", "dc", "mc")

assert set(STOCHASTIC_ANALYSIS_TYPES) <= set(SUPPORTED_ANALYSIS_TYPES)


@dataclass
class Testbench:
    directory: Path
    slug: str
    netlist: Path
    description: str = ""
    nominal_supply_v: float = DEFAULT_NOMINAL_SUPPLY_V
    supply_tolerance: float = DEFAULT_SUPPLY_TOLERANCE
    temperatures_c: tuple[float, ...] = DEFAULT_TEMPERATURES_C
    corners: tuple[str, ...] = (DEFAULT_CORNER_SET,)
    analysis_type: str = "op"
    analyses: tuple[str, ...] = ("op",)
    measure: dict[str, str] = field(default_factory=dict)
    params: dict[str, str | float] = field(default_factory=dict)
    options: tuple[str, ...] = ()
    default_runs: int = 1
    noise_params: str = ""
    tstop: str = ""
    tstep: str = ""
    tmax: str = ""
    design_params: dict[str, str | float] = field(default_factory=dict)
    extra_lib_sections: tuple[str, ...] = ()
    design_netlist: Path | None = None
    #: Testbench-specific entries appended to every record's Caveats
    #: section. ``sim/README.md`` requires each record to state what the run
    #: does NOT show, and the method limits that matter are properties of
    #: the testbench (a relaxed solver tolerance, a clock frequency scaled
    #: away from the target, an accumulation window that truncates), not of
    #: the PVT point -- so they belong in the manifest, next to the settings
    #: that cause them, rather than being re-typed per record.
    caveats: tuple[str, ...] = ()
    #: The exact ``tb.json`` bytes this object was built from (read once, in
    #: ``load``). Records snapshot these rather than re-reading the file, so
    #: the recorded manifest is the configuration the decks were composed
    #: from even if the working tree changes mid-run. ``None`` for a
    #: Testbench constructed by hand rather than via ``load``.
    manifest_bytes: bytes | None = None
    #: The exact testbench-fragment and DUT-netlist bytes read once in
    #: ``load`` (``design_netlist_bytes`` is ``None`` when the fragment is
    #: itself the DUT). Decks include snapshots of these, and records hash
    #: them, so the circuit ngspice consumed is the one recorded even if the
    #: working-tree files change mid-sweep. ``None`` for hand-built objects,
    #: which fall back to the live files.
    netlist_bytes: bytes | None = None
    design_netlist_bytes: bytes | None = None
    #: ``(bare file name, bytes)`` of every sibling file the DUT netlist
    #: transitively ``.include``s, captured at load next to the DUT.
    design_dependencies: tuple[tuple[str, bytes], ...] = ()

    @property
    def dut_netlist_bytes(self) -> bytes | None:
        if self.design_netlist is not None:
            return self.design_netlist_bytes
        return self.netlist_bytes

    def input_snapshots(self) -> list[tuple[str, bytes]]:
        """``(snapshot name, captured bytes)`` for each distinct SPICE input."""
        out: list[tuple[str, bytes]] = []
        if self.netlist_bytes is not None:
            out.append((FRAGMENT_SNAPSHOT_NAME, self.netlist_bytes))
        if self.design_netlist is not None and self.design_netlist_bytes is not None:
            out.append((DUT_SNAPSHOT_NAME, self.design_netlist_bytes))
            out.extend(self.design_dependencies)
        return out

    @property
    def fragment_snapshot_name(self) -> str | None:
        return FRAGMENT_SNAPSHOT_NAME if self.netlist_bytes is not None else None

    @property
    def dut_snapshot_name(self) -> str | None:
        if self.design_netlist is None:
            return self.fragment_snapshot_name
        return DUT_SNAPSHOT_NAME if self.design_netlist_bytes is not None else None

    @property
    def manifest_sha256(self) -> str | None:
        if self.manifest_bytes is None:
            return None
        return hashlib.sha256(self.manifest_bytes).hexdigest()

    @property
    def stochastic(self) -> bool:
        return self.analysis_type in STOCHASTIC_ANALYSIS_TYPES

    @property
    def dut_netlist(self) -> Path:
        """The netlist that defines the device under test.

        For a bootstrap testbench that carries its own devices this is the
        fragment itself. For a testbench that instantiates a cell from
        ``design/`` it is the schematic-derived netlist -- which is what
        ``sim/README.md``'s ``netlist.path``/``netlist.sha`` fields are for.
        """
        return self.design_netlist or self.netlist

    @property
    def manifest_path(self) -> Path:
        return self.directory / MANIFEST_NAME


def _require(manifest: dict, key: str, path: Path):
    if key not in manifest:
        raise ValueError(f"{path}: missing required key {key!r}")
    return manifest[key]


def load(directory: str | Path) -> Testbench:
    """Load a testbench manifest into a :class:`Testbench`.

    Accepts the testbench directory (``sim/tb/<slug>/``) or the ``tb.json``
    path itself.
    """
    directory = Path(directory).resolve()
    if directory.is_file() and directory.name == MANIFEST_NAME:
        directory = directory.parent
    manifest_path = directory / MANIFEST_NAME
    if not manifest_path.is_file():
        raise FileNotFoundError(f"no {MANIFEST_NAME} in {directory}")

    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8"))

    netlist = directory / _require(manifest, "netlist", manifest_path)
    if not netlist.is_file():
        raise FileNotFoundError(f"{manifest_path}: netlist {netlist} does not exist")
    netlist_bytes = netlist.read_bytes()

    measure = dict(_require(manifest, "measure", manifest_path))
    if not measure:
        raise ValueError(f"{manifest_path}: 'measure' must define at least one measurement")
    for key in measure:
        if not key.replace("_", "").isalnum():
            raise ValueError(
                f"{manifest_path}: measurement name {key!r} must be alphanumeric/underscore "
                "(it becomes an ngspice vector name)"
            )

    analyses = tuple(manifest.get("analyses", ("op",)))
    if not analyses:
        raise ValueError(f"{manifest_path}: 'analyses' must not be empty")

    analysis_type = manifest.get("analysis_type", "op")
    if not isinstance(analysis_type, str) or analysis_type not in SUPPORTED_ANALYSIS_TYPES:
        raise ValueError(
            f"{manifest_path}: unsupported analysis_type {analysis_type!r}; "
            f"supported types: {', '.join(SUPPORTED_ANALYSIS_TYPES)}"
        )

    design_netlist = None
    design_netlist_bytes = None
    design_dependencies: tuple[tuple[str, bytes], ...] = ()
    if "design_netlist" in manifest:
        # Repo-relative (e.g. "design/ro_array_core.spice"): the DUT is a
        # schematic-derived netlist shared by several testbenches, not a
        # copy living inside this testbench directory.
        repo_root = Path(__file__).resolve().parents[2]
        design_netlist = (repo_root / manifest["design_netlist"]).resolve()
        if not design_netlist.is_file():
            raise FileNotFoundError(
                f"{manifest_path}: design_netlist {design_netlist} does not exist "
                "-- run `python3 design/netlist.py` to export it"
            )
        design_netlist_bytes = design_netlist.read_bytes()
        design_dependencies = _capture_dut_dependencies(design_netlist, design_netlist_bytes)

    tb = Testbench(
        directory=directory,
        slug=manifest.get("name", directory.name),
        netlist=netlist,
        description=manifest.get("description", ""),
        nominal_supply_v=float(manifest.get("nominal_supply_v", DEFAULT_NOMINAL_SUPPLY_V)),
        supply_tolerance=float(manifest.get("supply_tolerance", DEFAULT_SUPPLY_TOLERANCE)),
        temperatures_c=tuple(
            float(t) for t in manifest.get("temperatures_c", DEFAULT_TEMPERATURES_C)
        ),
        corners=tuple(manifest.get("corners", (DEFAULT_CORNER_SET,))),
        analysis_type=analysis_type,
        analyses=analyses,
        measure=measure,
        params={k: v for k, v in manifest.get("params", {}).items()},
        options=tuple(manifest.get("options", ())),
        default_runs=int(manifest.get("default_runs", 1)),
        noise_params=manifest.get("noise_params", ""),
        tstop=str(manifest.get("tstop", "")),
        tstep=str(manifest.get("tstep", "")),
        tmax=str(manifest.get("tmax", "")),
        design_params={k: v for k, v in manifest.get("design_params", {}).items()},
        extra_lib_sections=tuple(manifest.get("extra_lib_sections", ())),
        design_netlist=design_netlist,
        caveats=tuple(manifest.get("caveats", ())),
        manifest_bytes=manifest_bytes,
        netlist_bytes=netlist_bytes,
        design_netlist_bytes=design_netlist_bytes,
        design_dependencies=design_dependencies,
    )
    validate_netlist(tb)
    # The manifest drives deck composition and measurement interpretation, so
    # refuse to proceed if it was edited while we were loading it: the
    # snapshot would otherwise not be the configuration actually used.
    if manifest_path.read_bytes() != manifest_bytes:
        raise ValueError(
            f"{manifest_path}: changed while it was being loaded; re-run once "
            "the file is stable"
        )
    if tb.stochastic and tb.default_runs < 1:
        raise ValueError(f"{manifest_path}: stochastic testbench must set default_runs >= 1")
    return tb


def _scan_forbidden(data: bytes, forbidden: tuple[str, ...] = FORBIDDEN_DIRECTIVES) -> list[str]:
    problems: list[str] = []
    for lineno, raw in enumerate(data.decode("utf-8", errors="replace").splitlines(), start=1):
        line = raw.strip().lower()
        if not line.startswith("."):
            continue
        if line.split()[0] in forbidden:
            problems.append(f"  line {lineno}: {raw.strip()}")
    return problems


#: Directives a DUT netlist must not contain (it is ``.include``d into the
#: harness's own deck, so it cannot own the models, temperature or control).
DUT_FORBIDDEN_DIRECTIVES = tuple(
    d for d in FORBIDDEN_DIRECTIVES if d not in DUT_INCLUDE_DIRECTIVES
)

_RESERVED_SNAPSHOT_NAMES = (FRAGMENT_SNAPSHOT_NAME, DUT_SNAPSHOT_NAME)


def _include_target(line: str) -> str | None:
    """The file named by a ``.include``/``.inc`` line (``None`` if not one)."""
    parts = line.strip().split(None, 1)
    if len(parts) != 2 or parts[0].lower() not in DUT_INCLUDE_DIRECTIVES:
        return None
    target = parts[1].strip()
    if len(target) >= 2 and target[0] == target[-1] and target[0] in "\"'":
        target = target[1:-1]
    return target


def _capture_dut_dependencies(
    dut: Path, data: bytes
) -> tuple[tuple[str, bytes], ...]:
    """Read, once, every sibling file the DUT netlist transitively includes.

    Supported form: ``.include "name.spice"`` where ``name.spice`` is a bare
    file name next to the including file. Absolute paths, sub-directories and
    ``..`` are rejected: they would resolve to a mutable original (or to a
    layout the flat snapshot directory cannot reproduce). Returns
    ``(name, bytes)`` in first-encounter order; every file is also scanned for
    the directives the harness owns.
    """
    found: dict[str, bytes] = {}
    stack: list[str] = []

    def visit(owner: Path, owner_name: str, content: bytes) -> None:
        problems = _scan_forbidden(content, DUT_FORBIDDEN_DIRECTIVES)
        if problems:
            raise ValueError(
                f"{owner}: DUT netlists must not contain "
                f"{', '.join(DUT_FORBIDDEN_DIRECTIVES)} -- the harness supplies the "
                "models, corner libs, temperature and control block:\n" + "\n".join(problems)
            )
        text = content.decode("utf-8", errors="replace")
        for lineno, raw in enumerate(text.splitlines(), start=1):
            target = _include_target(raw)
            if target is None:
                continue
            where = f"{owner}:{lineno}: {raw.strip()}"
            if (
                not target
                or "/" in target
                or "\\" in target
                or target in (".", "..")
                or target in _RESERVED_SNAPSHOT_NAMES
                or target.startswith(".")
            ):
                raise ValueError(
                    f"{where}\n  unsupported include form: only a bare file name "
                    "next to the including file is frozen with the DUT snapshot "
                    "(absolute paths, sub-directories and '..' would read a mutable "
                    "original); move the dependency next to the netlist or inline it"
                )
            if target == dut.name or target in stack:
                raise ValueError(f"{where}\n  include cycle through {target}")
            dep = dut.parent / target
            if not dep.is_file():
                raise FileNotFoundError(f"{where}\n  included file {dep} does not exist")
            if target in found:
                continue
            dep_bytes = dep.read_bytes()
            found[target] = dep_bytes
            stack.append(target)
            visit(dep, target, dep_bytes)
            stack.pop()

    visit(dut, dut.name, data)
    return tuple(found.items())


def validate_netlist(tb: Testbench) -> None:
    """Reject fragments and DUT netlists that try to own what the harness owns.

    Catching this here is much friendlier than debugging a duplicated
    ``.end`` or a hardcoded ``.temp 27`` that silently pins every corner to
    room temperature -- exactly the failure mode sim/README.md and this
    issue's acceptance criteria call out. It scans the bytes captured at load
    (the bytes that will be snapshotted), not a second read of the file.

    The fragment may not include anything. The DUT netlist is validated (and
    its sibling includes captured) by ``_capture_dut_dependencies`` during
    ``load``; a hand-built ``Testbench`` with a ``design_netlist`` is
    re-checked here from the live file.
    """
    fragment = tb.netlist_bytes if tb.netlist_bytes is not None else tb.netlist.read_bytes()
    problems = _scan_forbidden(fragment)
    if problems:
        raise ValueError(
            f"{tb.netlist}: netlist fragments must not contain "
            f"{', '.join(FORBIDDEN_DIRECTIVES)} -- the harness supplies the models, "
            "corner libs, temperature and control block:\n" + "\n".join(problems)
        )
    if tb.design_netlist is not None and tb.design_netlist_bytes is None:
        _capture_dut_dependencies(tb.design_netlist, tb.design_netlist.read_bytes())


def write_input_snapshots(tb: Testbench, directory: Path) -> list[tuple[str, str]]:
    """Materialize the captured SPICE inputs into ``directory``.

    Returns ``(name, sha256)`` per snapshot (empty for a hand-built ``tb``
    with no captured bytes). Idempotent and safe for concurrent callers
    writing the same bytes (temp file + rename). An existing file whose
    content differs from the captured bytes means a snapshot was mutated
    mid-run and raises rather than being overwritten, so the record can never
    hash bytes ngspice did not consume.
    """
    directory.mkdir(parents=True, exist_ok=True)
    out: list[tuple[str, str]] = []
    for name, data in tb.input_snapshots():
        path = directory / name
        if path.exists():
            if path.read_bytes() != data:
                raise RuntimeError(
                    f"{path}: input snapshot differs from the bytes captured at load; "
                    "it was modified during the run"
                )
        else:
            tmp = directory / f".{name}.{os.getpid()}.{threading.get_ident()}.tmp"
            tmp.write_bytes(data)
            os.replace(tmp, path)
        out.append((name, hashlib.sha256(data).hexdigest()))
    return out


def discover(root: str | Path) -> list[Path]:
    """Every testbench directory under ``root`` (``sim/tb/``).

    Looks for ``<root>/<slug>/tb.json`` and returns the ``<slug>``
    directories, sorted.
    """
    root = Path(root)
    return sorted(p.parent for p in root.glob(f"*/{MANIFEST_NAME}"))
