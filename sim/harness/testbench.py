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

FORBIDDEN_DIRECTIVES = (".control", ".endc", ".end", ".lib", ".temp", ".include")

#: analysis.type values sim/README.md's frontmatter recognizes as stochastic
#: (i.e. subject to the "no seed, no evidence" rule).
STOCHASTIC_ANALYSIS_TYPES = ("tran-noise", "mc")


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
    def netlist_sha256(self) -> str:
        return hashlib.sha256(self.netlist.read_bytes()).hexdigest()

    @property
    def manifest_path(self) -> Path:
        return self.directory / MANIFEST_NAME

    @property
    def manifest_sha256(self) -> str:
        return hashlib.sha256(self.manifest_path.read_bytes()).hexdigest()


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

    manifest = json.loads(manifest_path.read_text())

    netlist = directory / _require(manifest, "netlist", manifest_path)
    if not netlist.is_file():
        raise FileNotFoundError(f"{manifest_path}: netlist {netlist} does not exist")

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

    design_netlist = None
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
        analysis_type=manifest.get("analysis_type", "op"),
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
    )
    validate_netlist(tb)
    if tb.stochastic and tb.default_runs < 1:
        raise ValueError(f"{manifest_path}: stochastic testbench must set default_runs >= 1")
    return tb


def validate_netlist(tb: Testbench) -> None:
    """Reject fragments that try to own what the harness owns.

    Catching this here is much friendlier than debugging a duplicated
    ``.end`` or a hardcoded ``.temp 27`` that silently pins every corner to
    room temperature -- exactly the failure mode sim/README.md and this
    issue's acceptance criteria call out.
    """
    problems: list[str] = []
    for lineno, raw in enumerate(tb.netlist.read_text().splitlines(), start=1):
        line = raw.strip().lower()
        if not line.startswith("."):
            continue
        directive = line.split()[0]
        if directive in FORBIDDEN_DIRECTIVES:
            problems.append(f"  line {lineno}: {raw.strip()}")
    if problems:
        raise ValueError(
            f"{tb.netlist}: netlist fragments must not contain "
            f"{', '.join(FORBIDDEN_DIRECTIVES)} -- the harness supplies the models, "
            "corner libs, temperature and control block:\n" + "\n".join(problems)
        )


def discover(root: str | Path) -> list[Path]:
    """Every testbench directory under ``root`` (``sim/tb/``).

    Looks for ``<root>/<slug>/tb.json`` and returns the ``<slug>``
    directories, sorted.
    """
    root = Path(root)
    return sorted(p.parent for p in root.glob(f"*/{MANIFEST_NAME}"))
