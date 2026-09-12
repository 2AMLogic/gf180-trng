#!/usr/bin/env python3
"""Corner-swept static timing and power analysis of the placed-and-routed
digital section, for issue #145 (T1 checklist items 5 and 8, digital column).

    python3 sim/tb/digital-sta-power/run_sta.py --no-write   # run, print, mint nothing
    python3 sim/tb/digital-sta-power/run_sta.py              # run and mint records
    python3 sim/tb/digital-sta-power/run_sta.py --list       # the corner grid

What this is
------------
`layout/digital/build.py` (#111) placed and routed
`design/trng_top/trng_top.synth.v` (#143) and committed the routed DEF, the
as-built gate-level netlist and one implementation-corner report. That run
answered "does this design route at all". It did **not** answer "does it
close timing, and what does it cost, across the corner set" -- its own
README says so, and hands the question here.

This script is that answer. It re-opens the **committed** routed DEF
(`layout/digital/trng_top.def`), extracts real parasitics from the real
routing with OpenRCX, back-annotates them as SPEF, and runs OpenSTA over
the result once per corner:

- **timing** -- worst setup and hold slack against the P&R run's own 50 ns
  (20 MHz) constraint, with a propagated (not ideal) clock through the
  CTS-built tree, plus an Fmax found by bisecting the clock period rather
  than extrapolated from one slack number;
- **power** -- `report_power` at that same 20 MHz constraint *and* at the
  ratified 1 MHz raw-sample rate ([DR-0003]), the operating point
  `design/digital_power_estimate.py`'s library-based estimate prices, so
  the measured and estimated figures can be compared without a frequency
  correction in between;
- **area** -- the placed standard-cell area OpenROAD reports from the DEF
  itself (corner-independent; recorded in every record so no record has to
  be read together with another one to be complete).

Why OpenROAD directly, and not `klt`
------------------------------------
Every other physical-flow driver in this repository goes through `klt`
(`layout/_klt.py`), and this one deliberately does not, because there is no
`klt` verb that re-times an already-routed DEF. `klt place-and-route` does
run OpenSTA, but only *inside* a place-and-route run, at the one liberty
corner the request names, over an ideal clock, with placement-estimated
parasitics and no parasitic-corner control at all (its tech LEF is pinned
to the PDK's `nom` deck). Re-running the whole flow once per corner would
also give each corner a *different placement*, which is exactly what a
corner sweep must not do: the design under test has to be one fixed piece
of geometry. Filed generically upstream as klayout-tools#1099 (a signoff
STA verb over an existing DEF/netlist) and klayout-tools#1100 (parasitic-
corner selection); when those land, this script is the caller that should
switch to them. `openroad` is invoked here the same way `klt` invokes it --
`openroad -no_init -exit <script>` -- and the script it runs is written
into the record's own raw output, so the whole thing is auditable without
this file.

The corner set
--------------
`sim/harness/corners.py` sweeps the analog side over {tt, ss, ff} x
{-40, 27, 125} degC x {2.97, 3.30, 3.63} V = 27 points. A liberty corner is
not a free P/V/T choice: the library ships *characterised* bundles, and
`gf180mcu_fd_sc_mcu9t5v0` ships exactly five in the block's ratified 3.3 V
family (`design/README.md`) --

    ss_125C_3v00  ss_n40C_3v00  tt_025C_3v30  ff_125C_3v60  ff_n40C_3v60

-- which are the five corners of the analog grid's own P/V/T box that the
library actually characterises (the 1.8 V and 5.0 V families it also ships
describe a supply this block does not run at, and are excluded here for the
same reason `layout/digital/build.py` excludes them). Every one of the five
is swept against all three of the PDK's OpenRCX interconnect corners
(`min`/`nom`/`max`), because a timing corner for a routed block is a
(device, interconnect) pair and this repository has no basis for assuming
which pairing binds. 5 x 3 = 15 points, one record each, per DR-0005.

The six digital-facing inter-region trunks (#233)
--------------------------------------------------
Six of the fourteen inter-region trunks #222 drew (`clk`, `rst_n`,
`raw_bit`, `raw_valid`, `ring_bit1`/`ring_bit[0]`, `ring_bit2`/
`ring_bit[1]`) terminate on `trng_top`'s own pins -- DR-0025 scoped a
full-chip parasitic extraction (#232) away from them because `digital`'s
~2500 standard cells are abstracted in every existing extraction, but left
open the question this sweep now answers: what does each trunk's own
Metal4 RC do to the edge arriving at that pin. `digital_facing_trunks()`
reads `layout/floorplan/reports/interregion.json` at run time (never
transcribed by hand) and `_tcl()` states each trunk's lumped R/C as a
`set_input_transition` on the corresponding port, permanently (every run,
not a flag-gated scenario), in the transition convention the corner's own
liberty deck declares (`SlewConvention`).

`set_load` -- the construct issue #233 was filed expecting for the four
`combiner_sampler`-driven ports -- is deliberately **not** used, and the
reason is stronger than the port direction: all six ports are `DIRECTION
INPUT` on `trng_top` (`layout/digital/trng_top.def`'s `PINS` section) with
no driver inside this single-region netlist, whether the real upstream
driver is `combiner_sampler` (`raw_bit`/`raw_valid`/`ring_bit[0]`/
`ring_bit[1]`) or an off-chip pad (`clk`/`rst_n`). With no driver arc at
the port there is nothing for a load to attach to, and OpenSTA reports
bit-identical slack, slew and power whether these six ports carry no
`set_load`, their as-built 15.6-30.7 fF, or 10 pF. `set_load` here would
be a no-op wearing the costume of a measurement -- exactly what DR-0025
declined to do with an ngspice run, one level removed.
`sdc_treatment_probe.py` in this directory re-runs that comparison, and
the `set_input_transition` / `max_transition` domain check behind
`SlewConvention`, on demand.

What this is not
----------------
Not silicon, and not a signoff sign-off. The parasitics are OpenRCX's own
extraction from the routed DEF against the PDK's shipped rule decks, which
is a real extraction and not an estimate -- but it is not a foundry-signed
extraction, the flow it re-opens has no power delivery at all
(klayout-tools#1091, #171), and the DEF it reads carries no `SPECIALNETS`,
so nothing here sees IR drop. Only reg-to-reg paths are timed: the design
has no `set_input_delay`/`set_output_delay` constraints, so port paths are
unconstrained, and every record states how many endpoints that leaves
untimed. Power carries a declared, uniform switching activity (see
`ACTIVITY`); it is a corner sweep of a *model*, not a measured supply
current, and `sim/characterization-digital-sta-area-power.md` says at
length what follows from that and what does not.

[DR-0003]: ../../../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

TB_DIR = Path(__file__).resolve().parent
SIM_DIR = TB_DIR.parents[1]
REPO_ROOT = SIM_DIR.parent

sys.path.insert(0, str(SIM_DIR))

from harness import report  # noqa: E402
from harness import pdk as pdk_mod  # noqa: E402

SLUG = "digital-sta-power"

#: The committed geometry under test. Never re-placed, never re-routed by
#: this script -- one design, fifteen corners.
DEF_PATH = REPO_ROOT / "layout" / "digital" / "trng_top.def"
PNR_NETLIST_PATH = REPO_ROOT / "layout" / "digital" / "trng_top.pnr.v"
PNR_REPORT_PATH = REPO_ROOT / "layout" / "digital" / "reports" / "place_and_route.json"

CELL_LIBRARY = "gf180mcu_fd_sc_mcu9t5v0"
HDL_TOPLEVEL = "trng_top"
CLOCK_PORT = "clk"

#: Scratch root. Under `layout/.work/` like every other physical-flow
#: driver's (gitignored) working directory -- the SPEF this script writes is
#: 3.3 MB per corner and is deliberately not committed; its sha256 and its
#: summed capacitance are (see `_spef_summary`).
WORK_DIR = REPO_ROOT / "layout" / ".work" / "digital-sta"

#: The P&R run's own timing constraint (`layout/digital/build.py`'s
#: `CONSTRAINTS`), restated here so this sweep times the design against the
#: constraint it was built to and not a new one. NOT a spec row: no issue in
#: this repository sets a digital-section Fmax requirement.
CONSTRAINT_PERIOD_NS = 50.0

#: [DR-0003]'s ratified raw rate, one raw bit per `clk` edge => 1 MHz. The
#: second operating point every corner's power is reported at, because it is
#: the one `design/digital_power_estimate.py` prices and a power comparison
#: across two different clock rates would be measuring the clock rate.
RATIFIED_RATE_PERIOD_NS = 1000.0

#: Uniform switching activity handed to OpenSTA, in **transitions per net
#: per clock cycle**, with a 50 % duty. `design/digital_power_estimate.py`'s
#: own `DEFAULT_ACTIVITY = 0.125` counts *rising* transitions per net per
#: cycle; a net that rises 0.125 times per cycle also falls 0.125 times per
#: cycle, so the same assumption is 0.25 transitions per cycle here. Stated
#: as a number rather than left at OpenSTA's own default precisely so the
#: measured-vs-estimated comparison is not a comparison of two different
#: activity models.
ACTIVITY = 0.25
ACTIVITY_DUTY = 0.5

#: Liberty corners: the five the library characterises in this block's
#: ratified 3.3 V family. Ordered slow -> fast, which is also the order the
#: setup and hold sides bind in.
LIBERTY_CORNERS = (
    "ss_125C_3v00",
    "ss_n40C_3v00",
    "tt_025C_3v30",
    "ff_125C_3v60",
    "ff_n40C_3v60",
)

#: OpenRCX interconnect (parasitic) corners the PDK ships, under
#: `libs.tech/<RCX_DIRS>/rules.openrcx.<variant>.<corner>`. Orthogonal to the
#: liberty axis: the liberty deck models the devices, these model the wires.
RC_CORNERS = ("min", "nom", "max")

#: Where open_pdks stages those decks, newest naming first. The directory was
#: `libs.tech/openlane/` when this sweep was first written and is
#: `libs.tech/librelane/` in the open_pdks revision `sim/harness/pdk.py`'s own
#: install hint (and `.github/workflows/pdk-nightly.yml`) pins today --
#: OpenLane 2 was renamed LibreLane upstream and open_pdks followed. Both are
#: accepted, resolved by existence at run time by `deck_paths` rather than
#: pinned to one spelling: a checkout that resolved only the old name reports
#: "OpenRCX rule deck not found" against a perfectly good PDK install, which
#: is what a `pdk-copy` shim under `layout/.work/` was silently papering over.
RCX_DIRS = ("librelane", "openlane")

#: Which tech LEF the DEF is read against. Held at `nom` for every point on
#: purpose: the tech LEF supplies the *geometry* the committed DEF was routed
#: on (klt's own place-and-route pins it to `nom` too), so varying it would
#: change the design rather than the corner. The interconnect corner is
#: expressed through the OpenRCX rule deck above, which is what those decks
#: are for.
TECH_LEF_CORNER = "nom"

#: Bisection bounds and resolution for the Fmax search, in ns. The lower
#: bound is not a claim that a 0.1 ns period is meaningful -- it is a bracket
#: endpoint, and the search reports the period it converged to.
FMAX_MIN_PERIOD_NS = 0.1
FMAX_TOLERANCE_NS = 1e-3

OPENROAD_TIMEOUT_S = 1800

# --------------------------------------------------------------------------- #
# Interface load: the six digital-facing inter-region trunks (#233)
# --------------------------------------------------------------------------- #

#: `layout/floorplan/reports/interregion.json` -- the as-built geometry of
#: every inter-region trunk #222 drew. Read at run time, never transcribed by
#: hand, so this sweep's interface load follows the floorplan's own routing
#: if it moves (#233's first acceptance criterion).
INTERREGION_REPORT = REPO_ROOT / "layout" / "floorplan" / "reports" / "interregion.json"

#: Metal4 sheet parasitics, at `WIRE_W = 0.30 um` (`layout/floorplan/
#: interregion.py`, the width every trunk is drawn at). Not independently
#: measured by this repository: the same `klt` gf180mcu deck coefficients
#: DR-0025 (`spec/decision-records/DR-0025-full-chip-pex-scope.md`) and
#: `sim/characterization-post-layout-extracted.md` cite, and not committed
#: anywhere else as a reusable constant as of DR-0025's own writing -- cited
#: here rather than transcribed silently a second time. `git grep
#: cap_area/cap_perim/0.007602` before touching these numbers to confirm
#: that is still true.
METAL4_SHEET_RES_OHM_PER_SQ = 0.09
METAL4_CAP_AREA_FF_PER_UM2 = 0.007602
METAL4_CAP_PERIM_FF_PER_UM = 0.028153
METAL4_WIRE_W_UM = 0.30

#: 10-90 % is the transition convention most RC hand-calculations are quoted
#: in (`t = ln(9) * R * C`), including DR-0025's own prose. It is *not* the
#: convention this sweep hands OpenSTA -- see `SlewConvention` -- but every
#: record reports it alongside, so a reader comparing against a textbook
#: number does not have to redo the conversion.
RC_TRANSITION_10_90 = math.log(9.0)


@dataclass(frozen=True)
class SlewConvention:
    """How one liberty deck defines a transition time.

    A transition time is meaningless without the thresholds it is measured
    between, and a liberty deck states its own: `slew_lower_threshold_pct_*`
    / `slew_upper_threshold_pct_*` (30 %/70 % in every
    `gf180mcu_fd_sc_mcu9t5v0` deck) plus `slew_derate_from_library`, the
    factor relating the numbers *stored in the tables* to that measurement
    (0.5 in every deck: a table value of 13.2 describes a 6.6 ns 30-70 %
    edge). `max_transition` and the slew a `set_input_transition` states are
    both in the **table** domain, not the measured one -- verified directly
    against this library rather than assumed, by walking
    `set_input_transition` across `max_transition` and watching where
    OpenSTA's own `report_check_types -max_slew -violators` flips: at
    `ss_125C_3v00` (`max_transition` 13.2) a stated 13.1 is clean, 13.3
    violates by exactly 0.10, and 26.5 violates by 13.30 -- i.e. the stated
    number is compared against the limit 1:1, with no derate applied. See
    `sdc_treatment_probe.py`, which re-runs that walk on demand.
    """

    lower_pct: float
    upper_pct: float
    derate: float

    @property
    def rc_factor(self) -> float:
        """Table-domain transition time of a single-pole RC step response,
        in units of `R * C`.

        A step into a lumped RC settles as `1 - exp(-t / RC)`, so the time
        between two threshold fractions is `RC * ln((1 - lo) / (1 - hi))` --
        `ln(7/3) ~= 0.847 RC` at this library's 30/70 %. Dividing by
        `derate` expresses it in the same domain as the library's tables and
        its `max_transition` limit, which is the domain
        `set_input_transition` is read in.
        """
        lo = self.lower_pct / 100.0
        hi = self.upper_pct / 100.0
        return math.log((1.0 - lo) / (1.0 - hi)) / self.derate


@dataclass(frozen=True)
class InterfaceTrunk:
    """One inter-region trunk that terminates on the abstracted `digital`
    region -- a #233 "digital-facing" trunk. `def_pin` is read from the
    endpoint's own declared pin name (not derived from `net`), which is what
    correctly resolves the DEF's bus-notation names (`ring_bit[0]`/
    `ring_bit[1]`) against `INTERREGION_REPORT`'s net names (`ring_bit1`/
    `ring_bit2`) without a hand-maintained lookup table.
    """

    net: str
    def_pin: str
    chip_pin: bool
    trunk_length_um: float

    @property
    def cap_fF(self) -> float:
        """Lumped trunk capacitance: area term + both-side fringe term."""
        return self.trunk_length_um * (
            METAL4_CAP_AREA_FF_PER_UM2 * METAL4_WIRE_W_UM
            + 2 * METAL4_CAP_PERIM_FF_PER_UM
        )

    @property
    def res_ohm(self) -> float:
        return METAL4_SHEET_RES_OHM_PER_SQ * self.trunk_length_um / METAL4_WIRE_W_UM

    @property
    def rc_ns(self) -> float:
        """`R * C` as a time. R is in ohm and C in fF, so the product is in
        femtoseconds * 1e0 -- 1 ohm * 1 fF = 1e-15 s = 1e-6 ns."""
        return 1e-6 * self.res_ohm * self.cap_fF

    @property
    def transition_10_90_ns(self) -> float:
        """The textbook 10-90 % figure, for comparison only: not what this
        sweep states to OpenSTA (see `transition_ns`)."""
        return RC_TRANSITION_10_90 * self.rc_ns

    def transition_ns(self, slew: SlewConvention) -> float:
        """The trunk's own RC transition time, in the domain the given
        liberty deck's `set_input_transition` / `max_transition` use.

        Two deliberate conservatisms, both of which make this an upper bound
        on the trunk's own contribution rather than a best estimate:

        * **Lumped, not distributed.** The whole trunk's R and the whole
          trunk's C are multiplied together; a distributed line of the same
          total R and C responds roughly twice as fast.
        * **Ideal source.** The edge arriving at the trunk's far end is
          treated as a step, so the number is the wire's own contribution
          and nothing upstream of it. For `raw_bit`/`raw_valid`/`ring_bit[*]`
          the real driver is a `combiner_sampler` device this netlist does
          not contain; for `clk`/`rst_n` it is an off-chip pad driver no
          netlist in this repository models at all (#233). Neither can be
          priced here without inventing it, so neither is.
        """
        return slew.rc_factor * self.rc_ns


def digital_facing_trunks(report_path: Path | None = None) -> list[InterfaceTrunk]:
    """Every inter-region trunk with an endpoint on `digital`, read live from
    `report_path` (module-level `INTERREGION_REPORT` if omitted -- resolved
    at *call* time, not bound as a default-argument value at import time, so
    a test can point this at a synthetic report by reassigning the module
    attribute). DR-0025 names exactly six today (`clk`, `rst_n`, `raw_bit`,
    `raw_valid`, `ring_bit1`, `ring_bit2`) -- not hard-coded here, so a
    future floorplan/routing change (#222-style) that adds, removes or
    re-lengthens a digital-facing trunk is picked up the next time this
    sweep runs rather than silently going stale.
    """
    if report_path is None:
        report_path = INTERREGION_REPORT
    data = json.loads(report_path.read_text())
    trunks: list[InterfaceTrunk] = []
    for route in data["routes"]:
        digital_ep = next(
            (ep for ep in route["endpoints"] if ep["region"] == "digital"), None
        )
        if digital_ep is None:
            continue
        trunks.append(
            InterfaceTrunk(
                net=route["net"],
                def_pin=digital_ep["pin"],
                chip_pin=bool(route["chip_pin"]),
                trunk_length_um=float(route["trunk_length_um"]),
            )
        )
    return trunks

_METRIC = re.compile(r"^STA_METRIC\s+(\S+)\s+(\S+)\s*$", re.M)
_POWER_ROW = re.compile(
    r"^(Sequential|Combinational|Clock|Macro|Pad|Total)\s+"
    r"([\d.e+-]+)\s+([\d.e+-]+)\s+([\d.e+-]+)\s+([\d.e+-]+)",
    re.M,
)
_MISSING_INPUT = re.compile(r"There are (\d+) input ports missing set_input_delay")
_MISSING_OUTPUT = re.compile(r"There are (\d+) output ports missing set_output_delay")
_UNCONSTRAINED = re.compile(r"There are (\d+) unconstrained endpoints")
_LIB_ATTR = re.compile(r"^\s*(nom_process|nom_temperature|nom_voltage)\s*:\s*([-\d.]+)\s*;", re.M)
_LIB_SLEW_ATTR = re.compile(
    r"^\s*(slew_lower_threshold_pct_rise|slew_upper_threshold_pct_rise|"
    r"slew_derate_from_library)\s*:\s*([-\d.]+)\s*;",
    re.M,
)
_MAX_SLEW_VIOLATORS_BLOCK = re.compile(
    r"STA_MAX_SLEW_VIOLATORS_BEGIN\n(.*?)\nSTA_MAX_SLEW_VIOLATORS_END", re.S
)
_MAX_SLEW_VIOLATOR_PIN = re.compile(r"^Pin\s+(\S+?)(?:\s+[\^v])?\s*$", re.M)
#: `STA_IFACE_PIN <port> <pin>` -- every pin OpenSTA itself finds on one of
#: the six trunk nets, emitted by the generated Tcl so a violator pin can be
#: attributed to a trunk without this script guessing the netlist's internal
#: names.
_IFACE_PIN = re.compile(r"^STA_IFACE_PIN\s+(\S+)\s+(\S+)\s*$", re.M)


class StaError(RuntimeError):
    """The sweep could not be attempted, or a run did not produce metrics."""


@dataclass
class Corner:
    """One (liberty deck, interconnect deck) point of the grid."""

    liberty: str
    rc: str

    @property
    def process(self) -> str:
        return self.liberty.split("_")[0]

    @property
    def temp_c(self) -> float:
        raw = self.liberty.split("_")[1]
        value = float(raw.lstrip("n").rstrip("C"))
        return -value if raw.startswith("n") else value

    @property
    def vdd(self) -> float:
        raw = self.liberty.split("_")[2]
        return float(raw.replace("v", "."))

    @property
    def label(self) -> str:
        return f"{self.liberty}/rc-{self.rc}"


@dataclass
class Point:
    """Everything one record needs about one corner."""

    corner: Corner
    metrics: dict = field(default_factory=dict)
    power: dict = field(default_factory=dict)
    spef: dict = field(default_factory=dict)
    logs: dict = field(default_factory=dict)
    wall_s: float = 0.0
    #: The six digital-facing trunks (#233). The geometry is corner-
    #: independent; the transition time stated for it is not, because it is
    #: expressed in the liberty deck's own declared convention.
    interface_loads: list = field(default_factory=list)
    #: This corner's liberty deck's own transition-time convention (#233).
    slew_convention: SlewConvention | None = None
    #: Which trunks carry a pin OpenSTA itself named in a `-max_slew`
    #: violator block, at this corner's constraint-period session.
    interface_load_max_slew_violators: set = field(default_factory=set)


# --------------------------------------------------------------------------- #
# Environment
# --------------------------------------------------------------------------- #


def openroad_version() -> str | None:
    if shutil.which("openroad") is None:
        return None
    done = subprocess.run(
        ["openroad", "-version"], capture_output=True, text=True, check=False
    )
    return done.stdout.strip().splitlines()[0].strip() if done.stdout.strip() else None


def resolve_pdk():
    try:
        return pdk_mod.find_pdk()
    except Exception:
        return None


def deck_paths(pdk) -> dict[str, Path]:
    libs_ref = Path(pdk.path) / "libs.ref" / CELL_LIBRARY
    libs_tech = Path(pdk.path) / "libs.tech"
    # First `RCX_DIRS` entry that actually exists in this install; the first
    # entry regardless when none does, so `check_environment` reports a
    # concrete missing path rather than a list of candidates.
    rcx_dir = next(
        (libs_tech / name for name in RCX_DIRS if (libs_tech / name).is_dir()),
        libs_tech / RCX_DIRS[0],
    )
    return {
        "lib_dir": libs_ref / "lib",
        "tech_lef": libs_ref / "techlef" / f"{CELL_LIBRARY}__{TECH_LEF_CORNER}.tlef",
        "cell_lef": libs_ref / "lef" / f"{CELL_LIBRARY}.lef",
        "rcx_dir": rcx_dir,
    }


def liberty_path(pdk, corner: str) -> Path:
    return deck_paths(pdk)["lib_dir"] / f"{CELL_LIBRARY}__{corner}.lib"


def rcx_rules_path(pdk, rc: str) -> Path:
    return deck_paths(pdk)["rcx_dir"] / f"rules.openrcx.{pdk.variant}.{rc}"


def check_environment(pdk) -> list[str]:
    missing: list[str] = []
    if openroad_version() is None:
        missing.append(
            "openroad is not on PATH (see layout/digital/README.md's 'OpenROAD' "
            "section for the pinned ORFS image, or install a native build)"
        )
    if pdk is None:
        missing.append("no gf180mcu PDK install found (see sim/harness/pdk.py)")
    else:
        paths = deck_paths(pdk)
        for name in ("tech_lef", "cell_lef"):
            if not paths[name].is_file():
                missing.append(f"{name} not found at {paths[name]}")
        for corner in LIBERTY_CORNERS:
            path = liberty_path(pdk, corner)
            if not path.is_file():
                missing.append(f"liberty deck not found at {path}")
        for rc in RC_CORNERS:
            path = rcx_rules_path(pdk, rc)
            if not path.is_file():
                missing.append(f"OpenRCX rule deck not found at {path}")
    for path in (DEF_PATH, PNR_NETLIST_PATH):
        if not path.is_file():
            missing.append(
                f"{path.relative_to(REPO_ROOT)} is missing -- run "
                "`python3 layout/digital/build.py` first (#111)"
            )
    if not INTERREGION_REPORT.is_file():
        missing.append(
            f"{INTERREGION_REPORT.relative_to(REPO_ROOT)} is missing -- run "
            "`python3 layout/floorplan/floorplan.py` first (#222); it is "
            "this sweep's source for the six digital-facing trunks' "
            "interface load (#233)"
        )
    return missing


def liberty_operating_conditions(path: Path) -> dict:
    """`nom_process`/`nom_temperature`/`nom_voltage` from a liberty header.

    Read from the deck itself rather than parsed out of its filename, so a
    record's stated corner is the corner the timing came from and not a
    naming convention this script believes in.
    """
    head = []
    with path.open(errors="replace") as handle:
        for i, line in enumerate(handle):
            head.append(line)
            if i > 200:
                break
    found = {m.group(1): float(m.group(2)) for m in _LIB_ATTR.finditer("".join(head))}
    return found


def liberty_slew_convention(path: Path) -> SlewConvention:
    """The deck's own transition-time definition (see `SlewConvention`).

    Read from the liberty header, never assumed: the number this sweep hands
    `set_input_transition` is only meaningful in the convention the deck it
    is timed against declares, and a deck that declared different thresholds
    would need a different number for the same physical edge. Raises if any
    of the three attributes is absent rather than falling back to a default,
    because a silent default here would be an unsourced constant in a
    recorded result.
    """
    head = []
    with path.open(errors="replace") as handle:
        for i, line in enumerate(handle):
            head.append(line)
            if i > 200:
                break
    found = {m.group(1): float(m.group(2)) for m in _LIB_SLEW_ATTR.finditer("".join(head))}
    missing = {
        "slew_lower_threshold_pct_rise",
        "slew_upper_threshold_pct_rise",
        "slew_derate_from_library",
    } - set(found)
    if missing:
        raise StaError(
            f"{path.name} declares no {sorted(missing)} -- this sweep cannot "
            "state a transition time in a convention the deck does not declare "
            "(#233)"
        )
    return SlewConvention(
        lower_pct=found["slew_lower_threshold_pct_rise"],
        upper_pct=found["slew_upper_threshold_pct_rise"],
        derate=found["slew_derate_from_library"],
    )


# --------------------------------------------------------------------------- #
# The OpenROAD session
# --------------------------------------------------------------------------- #


def _tcl(
    *,
    pdk,
    corner: Corner,
    period_ns: float,
    spef_path: Path,
    bisect: bool,
) -> str:
    """One OpenROAD session's script: read the committed DEF, extract, time.

    One session per (corner, clock period) on purpose. OpenSTA caches a
    design's clock-derived activity densities on the first power query, so a
    `create_clock` that *replaces* an existing clock mid-session updates
    every slack correctly but leaves `report_power`'s switching term at the
    old rate. Verified live during this script's own bring-up: re-creating
    the 50 ns clock at 1000 ns in one session left combinational switching
    power bit-identical (1.031943e-03 W) instead of falling 20x, while a
    fresh session at 1000 ns reported exactly 1/20th of the 50 ns session's
    total. The clock bisection below is therefore run *after* every power
    query in its session, and the 1 MHz power point gets a session of its
    own.
    """
    paths = deck_paths(pdk)
    trunks = digital_facing_trunks()
    slew = liberty_slew_convention(liberty_path(pdk, corner.liberty))
    lines = [
        f"read_liberty {liberty_path(pdk, corner.liberty)}",
        f"read_lef {paths['tech_lef']}",
        f"read_lef {paths['cell_lef']}",
        f"read_def {DEF_PATH}",
        f"create_clock -name {CLOCK_PORT} -period {period_ns} [get_ports {CLOCK_PORT}]",
        "",
        "# The six inter-region trunks that terminate on `digital` (#233),",
        "# sourced from layout/floorplan/reports/interregion.json at run time",
        "# -- permanent, not a one-off scenario, because re-deriving it costs",
        "# nothing on every run while a pinned constant would go stale the",
        "# moment #222's routing moves.",
        "#",
        "# All six are DIRECTION INPUT on trng_top (layout/digital/",
        "# trng_top.def's own PINS section): raw_bit/raw_valid/ring_bit[0]/",
        "# ring_bit[1] are genuinely combiner_sampler-driven inputs, and",
        "# clk/rst_n are chip-pin-sourced inputs that also fan out to",
        "# combiner_sampler along the same trunk (issue #233's Curator-",
        "# verified correction). Neither group has a driver inside this",
        "# digital-only netlist, which is what rules `set_load` out as the",
        "# technique for all six rather than just for clk/rst_n: with no",
        "# driver arc at the port there is nothing for a load to attach to,",
        "# and OpenSTA reports bit-identical slack, slew and power with the",
        "# trunks' as-built 15.6-30.7 fF and with 10 pF -- i.e. set_load",
        "# here is a no-op that only looks like a measurement. Re-run that",
        "# comparison with sdc_treatment_probe.py.",
        "#",
        "# What each port genuinely has is an edge arriving from off this",
        f"# netlist degraded by the trunk's own RC. At {corner.liberty}'s own",
        f"# declared convention ({slew.lower_pct:g}-{slew.upper_pct:g} % thresholds,",
        f"# slew_derate_from_library {slew.derate:g}) a single-pole RC edge is",
        f"# {slew.rc_factor:.4f} * R * C in the table domain set_input_transition and",
        "# max_transition both use -- lumped R and C, ideal source, so an",
        "# upper bound on the trunk's own contribution (see InterfaceTrunk).",
    ]
    for trunk in trunks:
        lines.append(
            f"set_input_transition {trunk.transition_ns(slew):.6f} "
            f"[get_ports {{{trunk.def_pin}}}]"
            f"  ;# {trunk.net}: {trunk.trunk_length_um:.2f} um, "
            f"{trunk.res_ohm:.2f} ohm, {trunk.cap_fF:.3f} fF"
        )
    lines += [
        "",
        "define_process_corner -ext_model_index 0 X",
        f"extract_parasitics -ext_model_file {rcx_rules_path(pdk, corner.rc)}",
        f"write_spef {spef_path}",
        f"read_spef {spef_path}",
        # The ideal-clock slack is read FIRST, at the same corner and with the
        # same extracted parasitics, purely so this sweep can be reconciled
        # against `layout/digital/reports/place_and_route.json` -- which
        # reports an ideal (SDC-only) clock. Everything else in this session
        # is the propagated-clock number: a CTS-built tree exists in this DEF,
        # and timing it as ideal credits the design with zero insertion delay
        # and zero skew.
        'puts "STA_METRIC worst_setup_slack_ideal_s [sta::worst_slack_cmd max]"',
        'puts "STA_METRIC worst_hold_slack_ideal_s [sta::worst_slack_cmd min]"',
        "set_propagated_clock [all_clocks]",
        f"set_power_activity -global -activity {ACTIVITY} -duty {ACTIVITY_DUTY}",
        # Machine-readable metrics. The human-readable reports below land in
        # the same log and are the record's raw evidence.
        f'puts "STA_METRIC period_ns {period_ns}"',
        'puts "STA_METRIC worst_setup_slack_s [sta::worst_slack_cmd max]"',
        'puts "STA_METRIC worst_hold_slack_s [sta::worst_slack_cmd min]"',
        'puts "STA_METRIC tns_setup_s [sta::total_negative_slack_cmd max]"',
        'puts "STA_METRIC tns_hold_s [sta::total_negative_slack_cmd min]"',
        'puts "STA_METRIC clock_skew_setup_s [sta::worst_clk_skew_cmd max 0]"',
        'puts "STA_METRIC clock_skew_hold_s [sta::worst_clk_skew_cmd min 0]"',
        'puts "STA_METRIC cell_area_m2 [rsz::design_area]"',
        'puts "STA_METRIC utilization [rsz::utilization]"',
        "report_worst_slack -max -digits 4",
        "report_worst_slack -min -digits 4",
        "report_tns -digits 4",
        "report_checks -path_delay max -group_count 5 -digits 4 -format summary",
        "report_checks -path_delay min -group_count 5 -digits 4 -format summary",
        "report_clock_skew -setup -digits 4",
        "report_power -digits 6",
        "report_design_area",
        "check_setup",
        # Interface-load acceptance criterion #3 (#233): does any of the six
        # trunk-loaded ports' transition now violate the library's own
        # max_transition constraint. Answered three ways, because OpenSTA
        # reports a max-slew violation at the *load pins* a slew reaches and
        # not at the input port that stated it -- intersecting violators
        # against the six port names alone would be a silent false negative:
        #
        #   1. the library's own limit at this corner and the design-wide
        #      worst max-slew slack, as numbers (so a record says how much
        #      margin there is, not just "no violation");
        #   2. every pin OpenSTA itself finds on the six trunk nets, so a
        #      violator can be attributed to a trunk by name;
        #   3. the verbose violator list, as the record's raw evidence.
        'set _mslim [sta::max_slew_check_limit]',
        'if {$_mslim eq ""} { set _mslim nan }',
        'puts "STA_METRIC max_slew_limit_ns $_mslim"',
        'set _msslack [sta::max_slew_check_slack]',
        'if {$_msslack eq ""} { set _msslack nan }',
        'puts "STA_METRIC max_slew_slack_ns $_msslack"',
        'puts "STA_METRIC max_slew_violations [sta::max_slew_violation_count]"',
    ]
    for trunk in trunks:
        lines.append(
            f"foreach _p [get_pins -of_objects [get_nets {{{trunk.def_pin}}}]] "
            f'{{ puts "STA_IFACE_PIN {trunk.def_pin} [get_full_name $_p]" }}'
        )
    lines += [
        'puts "STA_MAX_SLEW_VIOLATORS_BEGIN"',
        "report_check_types -max_slew -violators -verbose",
        'puts "STA_MAX_SLEW_VIOLATORS_END"',
    ]
    if bisect:
        lines += [
            "",
            "# Fmax by bisection on the clock period: the smallest period at",
            "# which worst setup slack is still >= 0. Reported alongside the",
            "# linear 1/(T - WNS) extrapolation the P&R flow's own",
            "# report_fmax_metric uses, so the two can be compared rather",
            "# than one of them assumed.",
            "proc setup_slack_at {p} {",
            f"  create_clock -name {CLOCK_PORT} -period $p [get_ports {CLOCK_PORT}]",
            "  set_propagated_clock [all_clocks]",
            "  return [sta::worst_slack_cmd max]",
            "}",
            f"set lo {FMAX_MIN_PERIOD_NS}",
            f"set hi {period_ns}",
            'puts "STA_METRIC bisect_slack_at_lo_s [setup_slack_at $lo]"',
            "if {[setup_slack_at $lo] >= 0} {",
            '  puts "STA_METRIC min_period_ns $lo"',
            "} else {",
            f"  while {{[expr {{$hi - $lo}}] > {FMAX_TOLERANCE_NS}}} {{",
            "    set mid [expr {($lo + $hi) / 2.0}]",
            "    if {[setup_slack_at $mid] >= 0} { set hi $mid } else { set lo $mid }",
            "  }",
            '  puts "STA_METRIC min_period_ns $hi"',
            '  puts "STA_METRIC min_period_slack_s [setup_slack_at $hi]"',
            '  puts "STA_METRIC min_period_hold_slack_s [sta::worst_slack_cmd min]"',
            "}",
        ]
    return "\n".join(lines) + "\n"


def _run_openroad(script_path: Path, log_path: Path) -> str:
    done = subprocess.run(
        ["openroad", "-no_init", "-exit", str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=OPENROAD_TIMEOUT_S,
        check=False,
    )
    text = done.stdout + ("\n" + done.stderr if done.stderr.strip() else "")
    log_path.write_text(text)
    if done.returncode != 0:
        raise StaError(
            f"openroad exited {done.returncode} for {script_path.name}; "
            f"see {log_path}"
        )
    return text


def _parse_metrics(text: str) -> dict:
    return {m.group(1): float(m.group(2)) for m in _METRIC.finditer(text)}


def _parse_power(text: str) -> dict:
    """The `report_power` table, per group and total, in watts."""
    out: dict[str, dict[str, float]] = {}
    for m in _POWER_ROW.finditer(text):
        out[m.group(1).lower()] = {
            "internal_w": float(m.group(2)),
            "switching_w": float(m.group(3)),
            "leakage_w": float(m.group(4)),
            "total_w": float(m.group(5)),
        }
    if "total" not in out:
        raise StaError("no report_power table in the OpenROAD log")
    return out


def _parse_setup_checks(text: str) -> dict:
    def _one(pattern) -> int | None:
        m = pattern.search(text)
        return int(m.group(1)) if m else 0

    return {
        "inputs_missing_delay": _one(_MISSING_INPUT),
        "outputs_missing_delay": _one(_MISSING_OUTPUT),
        "unconstrained_endpoints": _one(_UNCONSTRAINED),
    }


def _parse_max_slew_violators(text: str) -> set[str]:
    """Every pin name `report_check_types -max_slew -violators` names,
    between this session's own begin/end markers.

    Global by construction (not just the six trunk ports): a `VIOLATED`
    block names the *pin*, not just the port, so this also catches a
    violation the added interface load causes one hop downstream of a
    trunk port without this sweep having to guess which internal pin that
    would be.
    """
    block = _MAX_SLEW_VIOLATORS_BLOCK.search(text)
    if block is None:
        return set()
    return {m.group(1) for m in _MAX_SLEW_VIOLATOR_PIN.finditer(block.group(1))}


def _parse_iface_pins(text: str) -> dict[str, set[str]]:
    """`{trunk port -> every pin OpenSTA found on that trunk's net}`, from the
    `STA_IFACE_PIN` lines the generated Tcl emits."""
    out: dict[str, set[str]] = {}
    for m in _IFACE_PIN.finditer(text):
        out.setdefault(m.group(1), set()).add(m.group(2))
    return out


def interface_load_max_slew_violations(text: str, trunks: list) -> set[str]:
    """Which digital-facing trunks (#233) carry a pin OpenSTA's own
    `-max_slew` check reports as violating -- issue #233's acceptance
    criterion 3 ("does any of the six ports' transition now violate the
    library's max-transition constraint"), read off the tool's check rather
    than inferred from a slack number.

    Attribution is by **net**, not by port name, because OpenSTA reports a
    max-slew violation at each load pin the slew reaches and never at the
    input port that stated it: walking `set_input_transition` past
    `max_transition` on `raw_bit` at `ss_125C_3v00` names that net's fifteen
    load pins and not `raw_bit` itself. Matching port names against the
    violator list alone would therefore report zero violations for a port
    whose own stated transition exceeds the limit -- the one false negative
    this check exists to avoid.
    """
    violators = _parse_max_slew_violators(text)
    pins = _parse_iface_pins(text)
    hit = set()
    for trunk in trunks:
        on_net = pins.get(trunk.def_pin, set()) | {trunk.def_pin}
        if on_net & violators:
            hit.add(trunk.def_pin)
    return hit


def _spef_summary(spef_path: Path) -> dict:
    """Total grounded (wire-to-ground) and coupling capacitance in the SPEF.

    OpenROAD writes this SPEF with `PIN_CAP NONE`, so every grounded entry is
    interconnect capacitance and none of it is a standard cell's own input
    pin -- which makes the per-net figure directly comparable against
    `design/digital_power_estimate.py`'s flat `DEFAULT_WIRE_CAP_F` allowance,
    the one term in that estimate that had no layout behind it at all.

    `*CAP` entries with two fields are node-to-ground; three fields are
    node-to-node coupling. Units come from the header (`*C_UNIT`), never
    assumed.
    """
    unit_f = 1e-12
    total_ground = 0.0
    total_coupling = 0.0
    nets = 0
    in_cap = False
    with spef_path.open(errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("*C_UNIT"):
                parts = line.split()
                scale = {"F": 1.0, "MF": 1e-3, "UF": 1e-6, "NF": 1e-9,
                         "PF": 1e-12, "FF": 1e-15}[parts[2].upper()]
                unit_f = float(parts[1]) * scale
            elif line.startswith("*D_NET"):
                nets += 1
                in_cap = False
            elif line.startswith("*CAP"):
                in_cap = True
            elif line.startswith("*RES") or line.startswith("*END"):
                in_cap = False
            elif in_cap and line and line[0].isdigit():
                fields = line.split()
                if len(fields) == 3:
                    total_ground += float(fields[2])
                elif len(fields) == 4:
                    total_coupling += float(fields[3])
    return {
        "nets": nets,
        "ground_cap_f": total_ground * unit_f,
        "coupling_cap_f": total_coupling * unit_f,
        "sha256": report.sha256_file(spef_path),
        "bytes": spef_path.stat().st_size,
    }


def run_point(pdk, corner: Corner, work_dir: Path) -> Point:
    """One corner: two OpenROAD sessions (20 MHz + 1 MHz), one Point."""
    started = time.time()
    point = Point(corner=corner)
    spef_path = work_dir / f"{HDL_TOPLEVEL}.{corner.liberty}.{corner.rc}.spef"

    for tag, period, bisect in (
        ("constraint", CONSTRAINT_PERIOD_NS, True),
        ("ratified-rate", RATIFIED_RATE_PERIOD_NS, False),
    ):
        script_path = work_dir / f"sta-{tag}.{corner.liberty}.{corner.rc}.tcl"
        log_path = work_dir / f"sta-{tag}.{corner.liberty}.{corner.rc}.log"
        script = _tcl(
            pdk=pdk, corner=corner, period_ns=period, spef_path=spef_path,
            bisect=bisect,
        )
        script_path.write_text(script)
        text = _run_openroad(script_path, log_path)
        metrics = _parse_metrics(text)
        power = _parse_power(text)
        point.logs[tag] = {"script": script_path, "log": log_path}
        point.power[tag] = power
        if tag == "constraint":
            point.metrics = metrics
            point.metrics.update(_parse_setup_checks(text))
            point.spef = _spef_summary(spef_path)
            point.interface_loads = digital_facing_trunks()
            point.slew_convention = liberty_slew_convention(
                liberty_path(pdk, corner.liberty)
            )
            point.interface_load_max_slew_violators = interface_load_max_slew_violations(
                text, point.interface_loads
            )
        else:
            point.metrics["ratified_rate_period_ns"] = metrics["period_ns"]

    point.wall_s = time.time() - started
    return point


# --------------------------------------------------------------------------- #
# Derived quantities
# --------------------------------------------------------------------------- #


def derive(point: Point) -> dict:
    """Everything a record's Result section quotes, in SI units.

    Only arithmetic on what the two sessions reported -- no modelling, and
    nothing that is not either a direct OpenROAD output or a ratio of two of
    them.
    """
    m = point.metrics
    c = point.corner
    constraint_ns = m["period_ns"]
    setup_ns = m["worst_setup_slack_s"] * 1e9
    hold_ns = m["worst_hold_slack_s"] * 1e9
    min_period_ns = m.get("min_period_ns")
    cell_area_um2 = m["cell_area_m2"] * 1e12
    p20 = point.power["constraint"]
    p1 = point.power["ratified-rate"]
    leakage_w = p20["total"]["leakage_w"]
    out = {
        "constraint_period_ns": constraint_ns,
        "constraint_freq_mhz": 1e3 / constraint_ns,
        "worst_setup_slack_ns": setup_ns,
        "worst_hold_slack_ns": hold_ns,
        "worst_setup_slack_ideal_clock_ns": m["worst_setup_slack_ideal_s"] * 1e9,
        "worst_hold_slack_ideal_clock_ns": m["worst_hold_slack_ideal_s"] * 1e9,
        "clock_tree_cost_ns": (m["worst_setup_slack_ideal_s"]
                               - m["worst_setup_slack_s"]) * 1e9,
        "tns_setup_ns": m["tns_setup_s"] * 1e9,
        "tns_hold_ns": m["tns_hold_s"] * 1e9,
        "clock_skew_setup_ns": m["clock_skew_setup_s"] * 1e9,
        "fmax_linear_mhz": 1e3 / (constraint_ns - setup_ns),
        "cell_area_um2": cell_area_um2,
        "utilization_pct": m["utilization"] * 100.0,
        "wire_cap_total_f": point.spef["ground_cap_f"],
        "wire_cap_per_net_f": point.spef["ground_cap_f"] / max(point.spef["nets"], 1),
        "coupling_cap_total_f": point.spef["coupling_cap_f"],
        "spef_nets": float(point.spef["nets"]),
        "p_total_20mhz_w": p20["total"]["total_w"],
        "p_internal_20mhz_w": p20["total"]["internal_w"],
        "p_switching_20mhz_w": p20["total"]["switching_w"],
        "p_clock_20mhz_w": p20["clock"]["total_w"],
        "p_sequential_20mhz_w": p20["sequential"]["total_w"],
        "p_combinational_20mhz_w": p20["combinational"]["total_w"],
        "p_total_1mhz_w": p1["total"]["total_w"],
        "p_internal_1mhz_w": p1["total"]["internal_w"],
        "p_switching_1mhz_w": p1["total"]["switching_w"],
        "p_clock_1mhz_w": p1["clock"]["total_w"],
        "p_clock_internal_1mhz_w": p1["clock"]["internal_w"],
        "p_clock_switching_1mhz_w": p1["clock"]["switching_w"],
        "p_sequential_1mhz_w": p1["sequential"]["total_w"],
        "p_sequential_internal_1mhz_w": p1["sequential"]["internal_w"],
        "p_sequential_switching_1mhz_w": p1["sequential"]["switching_w"],
        "p_combinational_1mhz_w": p1["combinational"]["total_w"],
        "p_combinational_internal_1mhz_w": p1["combinational"]["internal_w"],
        "p_combinational_switching_1mhz_w": p1["combinational"]["switching_w"],
        "p_leakage_w": leakage_w,
        "i_leakage_a": leakage_w / c.vdd,
        "i_total_1mhz_a": p1["total"]["total_w"] / c.vdd,
        "unconstrained_endpoints": float(m["unconstrained_endpoints"]),
        "inputs_missing_delay": float(m["inputs_missing_delay"]),
        "outputs_missing_delay": float(m["outputs_missing_delay"]),
        # #233: the six digital-facing trunks' interface load.
        "interface_load_ports": float(len(point.interface_loads)),
        "interface_load_max_slew_violations": float(
            len(point.interface_load_max_slew_violators)
        ),
        "max_slew_violations": float(m.get("max_slew_violations", float("nan"))),
        "max_slew_limit_ns": m.get("max_slew_limit_ns", float("nan")),
        "max_slew_slack_ns": m.get("max_slew_slack_ns", float("nan")),
    }
    if point.interface_loads and point.slew_convention is not None:
        worst = max(
            t.transition_ns(point.slew_convention) for t in point.interface_loads
        )
        out["interface_load_worst_transition_ns"] = worst
        limit = out["max_slew_limit_ns"]
        # Margin of the worst-loaded trunk port against the library's own
        # max_transition limit at this corner, in the same (table) domain --
        # the number acceptance criterion 3 (#233) asks for. Positive is
        # margin; negative would be a violation.
        out["interface_load_transition_margin_ns"] = limit - worst
    if min_period_ns is not None:
        out["min_period_ns"] = min_period_ns
        out["fmax_bisect_mhz"] = 1e3 / min_period_ns
    return out


# --------------------------------------------------------------------------- #
# Records
# --------------------------------------------------------------------------- #


def _voltage_label(vdd: float) -> str:
    offset = (vdd - 3.3) / 3.3 * 100.0
    if abs(offset) < 0.05:
        return f"{vdd:.2f} V (nominal 3.3 V)"
    sign = "+" if offset > 0 else ""
    return f"{vdd:.2f} V (nominal 3.3 V, {sign}{offset:.1f}%)"


def _frontmatter(stem: str, point: Point, values: dict, pdk, git: dict,
                 raw_files, openroad: str, lib_conditions: dict) -> str:
    c = point.corner
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lib = liberty_path(pdk, c.liberty)
    paths = deck_paths(pdk)
    rcx = rcx_rules_path(pdk, c.rc)
    lines = [
        "---",
        f"record: {stem}",
        f"date: {now}",
        "status: valid",
        "",
        "level: gate (see spec/decision-records/"
        "DR-0021-gate-level-timing-and-power-records.md)",
        "",
        "testbench:",
        f"  path: sim/tb/{SLUG}/run_sta.py",
        f"  sha: {report.blob_sha(REPO_ROOT, TB_DIR / 'run_sta.py')}",
        "netlist:",
        "  path: layout/digital/trng_top.def",
        f"  sha: {report.blob_sha(REPO_ROOT, DEF_PATH)}",
        "  note: >-",
        "    The committed routed DEF from layout/digital/build.py (#111) -- one",
        "    fixed placement and routing, re-timed at this corner. The matching",
        "    as-built gate-level netlist is layout/digital/trng_top.pnr.v",
        f"    (sha {report.blob_sha(REPO_ROOT, PNR_NETLIST_PATH)}); OpenROAD reads the",
        "    instance set from the DEF, so the DEF is the DUT this record names.",
        f"repo_commit: {report.repo_commit_field(git)}",
        "",
        f"pdk: {pdk.variant} @ {pdk.version}",
        "pdk.models:",
        f"  - {lib} (liberty corner {c.liberty}, sha256:{report.sha256_file(lib)})",
        f"  - {paths['tech_lef']} (tech LEF, {TECH_LEF_CORNER} deck, "
        f"sha256:{report.sha256_file(paths['tech_lef'])})",
        f"  - {paths['cell_lef']} (cell LEF, sha256:{report.sha256_file(paths['cell_lef'])})",
        f"  - {rcx} (OpenRCX interconnect corner {c.rc}, sha256:{report.sha256_file(rcx)})",
        "",
        "tool:",
        '  ngspice: "n/a (gate-level record -- timing and power come from '
        'OpenSTA/OpenRCX inside OpenROAD, not from a device-level simulation)"',
        f'  openroad: "{openroad}"',
        f'  python: "{platform.python_version()} ({platform.python_implementation()})"',
        f"  platform: {platform.platform()}",
        "",
        "corner:",
        f"  process: {c.process}",
        f"  voltage: {_voltage_label(c.vdd)}",
        f"  temperature: {c.temp_c:g}",
        f"  liberty: {CELL_LIBRARY}__{c.liberty}",
        f"  interconnect: {c.rc} (OpenRCX rule deck; the parasitic corner, "
        "orthogonal to the liberty deck's device corner)",
    ]
    if lib_conditions:
        stated = ", ".join(
            f"{k} {v:g}" for k, v in sorted(lib_conditions.items())
        )
        lines.append(f"  liberty_operating_conditions: {stated} (read from the deck)")
    lines += [
        "",
        "analysis:",
        "  type: sta+power (OpenSTA over the committed routed DEF, OpenRCX-extracted "
        "parasitics back-annotated as SPEF)",
        "  tstop: n/a (static analysis -- no time-domain window)",
        "  tstep: n/a (static analysis)",
        "  tmax: n/a (static analysis)",
        "  noise_params: n/a (no device noise in a liberty-table analysis)",
        "  runs: 2 (one OpenROAD session per clock rate -- see the testbench "
        "docstring on why the two rates cannot share a session)",
        f"  clock: {CLOCK_PORT}, {CONSTRAINT_PERIOD_NS:g} ns "
        f"({1e3 / CONSTRAINT_PERIOD_NS:g} MHz) -- the P&R run's own constraint; "
        f"power also reported at {RATIFIED_RATE_PERIOD_NS:g} ns "
        f"({1e3 / RATIFIED_RATE_PERIOD_NS:g} MHz), DR-0003's ratified raw rate",
        "  clock_model: propagated (the CTS-built tree in the DEF), not ideal",
        f"  power_activity: {ACTIVITY} transitions/net/cycle, duty {ACTIVITY_DUTY} "
        "(set_power_activity -global; = design/digital_power_estimate.py's 0.125 "
        "RISING transitions/net/cycle)",
        "seeds: n/a (deterministic analysis)",
        "",
        "parasitics:",
        f"  spef_sha256: {point.spef['sha256']}",
        f"  spef_bytes: {point.spef['bytes']}",
        "  note: >-",
        "    The SPEF is regenerated by the reproduce command below and is NOT",
        "    committed (3.3 MB per corner, 15 corners). Its sha256 and its summed",
        "    capacitance are, so a re-run is checkable against this record.",
        "",
        "interface_loads:",
        "  note: >-",
        "    The inter-region trunks terminating on `digital` (#233, DR-0025's",
        "    'Alternative B' follow-up), stated to OpenSTA as a",
        "    set_input_transition on each port -- derived from interregion_json",
        "    below at run time, not a pinned constant, and permanent rather than a",
        "    one-off scenario. set_load is NOT used, and not because of the",
        "    input/output direction alone: all six ports are DIRECTION INPUT on",
        "    trng_top with no driver inside this netlist, so there is no driver arc",
        "    for a load to attach to, and OpenSTA reports bit-identical slack, slew",
        "    and power whether these ports carry no set_load, their as-built",
        "    15.6-30.7 fF, or 10 pF. sdc_treatment_probe.py re-runs that comparison.",
        "    Metal4 coefficients per DR-0025 (spec/decision-records/",
        "    DR-0025-full-chip-pex-scope.md): sheet_res "
        f"{METAL4_SHEET_RES_OHM_PER_SQ:g} ohm/sq, cap_area "
        f"{METAL4_CAP_AREA_FF_PER_UM2:g} fF/um^2, cap_perim "
        f"{METAL4_CAP_PERIM_FF_PER_UM:g} fF/um at WIRE_W {METAL4_WIRE_W_UM:g} um.",
        f"  interregion_json: {INTERREGION_REPORT.relative_to(REPO_ROOT)} "
        f"(sha256:{report.sha256_file(INTERREGION_REPORT)})",
    ]
    if point.slew_convention is not None:
        s = point.slew_convention
        lines += [
            f"  slew_convention: {s.lower_pct:g}-{s.upper_pct:g}% thresholds, "
            f"slew_derate_from_library {s.derate:g} (read from this record's own "
            f"liberty deck) => a single-pole RC edge is {s.rc_factor:.4f} * R * C "
            "in the table domain set_input_transition and max_transition share",
            "  transition_model: >-",
            "    Lumped whole-trunk R times whole-trunk C, driven by an ideal step:",
            "    an upper bound on the trunk's own contribution, not a best estimate",
            "    (a distributed line of the same total R and C responds roughly twice",
            "    as fast), and it prices nothing upstream of the wire -- the real",
            "    drivers are a combiner_sampler device this netlist does not contain",
            "    and an off-chip pad no netlist in this repository models.",
        ]
    lines.append("  ports:")
    for trunk in point.interface_loads:
        stated = (
            f"{trunk.transition_ns(point.slew_convention):.6f}"
            if point.slew_convention is not None
            else "n/a"
        )
        lines.append(
            f"    - {trunk.def_pin}: net {trunk.net}, trunk "
            f"{trunk.trunk_length_um:.2f} um, R {trunk.res_ohm:.2f} ohm, "
            f"C {trunk.cap_fF:.3f} fF, R*C {trunk.rc_ns * 1e3:.3f} ps, "
            f"set_input_transition {stated} ns "
            f"(10-90% reference {trunk.transition_10_90_ns:.6f} ns)"
        )
    lines += [
        "",
        "raw:",
        f"  path: sim/records/raw/{stem}/",
        "  files:",
    ]
    for name, digest in raw_files:
        lines.append(f"    - {name}  sha256:{digest}")
    lines.append(f"wall_time: {point.wall_s:.1f}s")
    lines.append("---")
    return "\n".join(lines)


def _result_lines(values: dict) -> str:
    order = [
        "constraint_period_ns", "constraint_freq_mhz",
        "worst_setup_slack_ns", "worst_hold_slack_ns",
        "worst_setup_slack_ideal_clock_ns", "worst_hold_slack_ideal_clock_ns",
        "clock_tree_cost_ns", "tns_setup_ns", "tns_hold_ns", "clock_skew_setup_ns",
        "min_period_ns", "fmax_bisect_mhz", "fmax_linear_mhz",
        "cell_area_um2", "utilization_pct",
        "spef_nets", "wire_cap_total_f", "wire_cap_per_net_f", "coupling_cap_total_f",
        "p_total_20mhz_w", "p_internal_20mhz_w", "p_switching_20mhz_w",
        "p_clock_20mhz_w", "p_sequential_20mhz_w", "p_combinational_20mhz_w",
        "p_total_1mhz_w", "p_internal_1mhz_w", "p_switching_1mhz_w",
        "p_clock_1mhz_w", "p_clock_internal_1mhz_w", "p_clock_switching_1mhz_w",
        "p_sequential_1mhz_w", "p_sequential_internal_1mhz_w",
        "p_sequential_switching_1mhz_w",
        "p_combinational_1mhz_w", "p_combinational_internal_1mhz_w",
        "p_combinational_switching_1mhz_w",
        "p_leakage_w", "i_leakage_a", "i_total_1mhz_a",
        "unconstrained_endpoints", "inputs_missing_delay", "outputs_missing_delay",
        "interface_load_ports", "interface_load_worst_transition_ns",
        "interface_load_transition_margin_ns", "interface_load_max_slew_violations",
        "max_slew_limit_ns", "max_slew_slack_ns", "max_slew_violations",
    ]
    out = []
    for key in order:
        if key in values:
            out.append(f"- `{key}`: {values[key]:.6e}")
    return "\n".join(out)


def _body(point: Point, values: dict) -> str:
    c = point.corner
    return f"""
## Result

{_result_lines(values)}

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-sta-area-power.md` for what the fifteen
records of this family, read together, do and do not establish.

## How to reproduce

```sh
python3 sim/tb/{SLUG}/run_sta.py --liberty {c.liberty} --rc {c.rc} --no-write
```

Drop `--liberty`/`--rc` for the full 15-point grid, and `--no-write` to mint
records. Records are append-only: a re-run mints a new stem, it never
overwrites this one. Needs `openroad` on `PATH` and the gf180mcu PDK
(`python3 sim/run_corners.py --check-env` reports the PDK; the OpenROAD
provisioning is `layout/digital/README.md`'s "OpenROAD" section).

## Caveats

- **One corner** ({c.liberty}, interconnect `{c.rc}`). Says nothing about any
  other corner. A liberty deck bundles process, voltage and temperature
  together, so this record's P/V/T is the deck's, not a free choice.
- **Gate level, not device level.** Cell delays, internal energies and
  leakages are the library's characterised tables, not a device-model
  simulation of this netlist. That is what makes a corner sweep affordable
  here and it is also its ceiling: nothing in this record re-derives the
  library.
- **Reg-to-reg paths only.** The design carries no `set_input_delay`/
  `set_output_delay`, so port paths are unconstrained and untimed --
  `unconstrained_endpoints` above says how many endpoints that leaves out.
  This matches the constraint set the P&R run itself used.
- **Extraction, not signoff extraction.** Parasitics are OpenRCX's own
  extraction of the committed routed DEF against the PDK's shipped
  `rules.openrcx` deck. Real geometry, real coupling -- but not a
  foundry-signed extraction, and no IR drop: the DEF has no `SPECIALNETS`
  section and the flow that produced it builds no power delivery at all
  (#171, klayout-tools#1091).
- **Power carries a declared uniform switching activity**
  ({ACTIVITY} transitions/net/cycle, duty {ACTIVITY_DUTY}), applied globally.
  It is not a measured supply current and not a simulation of this design's
  real data. Leakage is the one power column with no activity assumption in
  it.
- **The clock constraint is this run's input, not a spec row.** No issue in
  this repository sets a digital-section Fmax requirement; the ratified rate
  row is DR-0003's > 1 Mbps at the raw tap.
- **Area is corner-independent** and is repeated in every record of this
  family so no record has to be read alongside another to be complete; it is
  the DEF's own placed standard-cell area, not a die area.
- **Interface load (#233) is a port-local edge-transition model, and it is an
  upper bound, not an estimate.** `interface_load_ports`
  (= {values.get('interface_load_ports', 0):.0f}) is the number of
  `digital`-facing inter-region trunks priced this way; the stated transition
  for each is in the `interface_loads:` block above, lumped-R-times-lumped-C
  driven by an ideal step. The worst of them is
  `interface_load_worst_transition_ns`, against this corner's own library
  `max_slew_limit_ns` -- `interface_load_transition_margin_ns` is the
  difference, and `interface_load_max_slew_violations`
  (= {values.get('interface_load_max_slew_violations', 0):.0f}) counts the
  trunks with a pin OpenSTA's own `-max_slew` check calls violating (attributed
  by net, because the tool reports such a violation at a net's load pins and
  never at the input port that stated the slew).
- **What the interface load cannot move, and why.** `raw_bit`/`raw_valid`/
  `ring_bit[0]`/`ring_bit[1]` carry no `set_input_delay`, so no reg-to-reg
  path starts at one and `worst_setup_slack_ns`/`worst_hold_slack_ns`/`fmax_*`
  cannot move from those four trunks at all -- their effect is confined to the
  transition time at the port and at the pins it drives. `clk` and `rst_n`
  reach the clock tree and the flops' reset pins, so they can in principle
  move a slack: measured at `ss_125C_3v00`/`min` against an otherwise
  identical session with no interface load, `worst_setup_slack_ns` and
  `worst_hold_slack_ns` were unchanged in every digit of double precision, and
  a deliberate 10x overstatement of all six transitions moved worst setup
  slack by +3.6 fs. The residual sign is **not** guaranteed to be a
  degradation: launch and capture share the clock root, so a slower root edge
  largely cancels, and what is left is numerical residue rather than a
  measured effect. The degradation that *is* monotonic in the trunks' RC is
  the slew at the six ports and at the pins they drive.

---

Written by `sim/tb/{SLUG}/run_sta.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here via
`supersedes` (see `sim/README.md`).
"""


def write_record(point: Point, values: dict, pdk, git: dict, openroad: str,
                 records_dir: Path) -> Path:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def render(stem: str, raw_dir: Path) -> str:
        names = []
        for tag in ("constraint", "ratified-rate"):
            for kind in ("script", "log"):
                src = point.logs[tag][kind]
                name = f"{tag}.{'tcl' if kind == 'script' else 'log'}"
                shutil.copyfile(src, raw_dir / name)
                names.append(name)
        raw_files = [(n, report.sha256_file(raw_dir / n)) for n in names]

        lib_conditions = liberty_operating_conditions(liberty_path(pdk, point.corner.liberty))
        return (
            _frontmatter(stem, point, values, pdk, git, raw_files, openroad, lib_conditions)
            + "\n"
            + _body(point, values)
        )

    return report.finalize_record(records_dir, date, SLUG, render)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def grid(liberty: list[str] | None, rc: list[str] | None) -> list[Corner]:
    libs = liberty or list(LIBERTY_CORNERS)
    rcs = rc or list(RC_CORNERS)
    for name in libs:
        if name not in LIBERTY_CORNERS:
            raise StaError(
                f"unknown liberty corner {name!r}; known: {', '.join(LIBERTY_CORNERS)}"
            )
    for name in rcs:
        if name not in RC_CORNERS:
            raise StaError(f"unknown interconnect corner {name!r}; known: {', '.join(RC_CORNERS)}")
    return [Corner(liberty=lib, rc=r) for lib in libs for r in rcs]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--liberty", action="append", help="liberty corner(s) to run")
    ap.add_argument("--rc", action="append", help="OpenRCX interconnect corner(s) to run")
    ap.add_argument("--no-write", action="store_true",
                    help="run and print without minting evidence records")
    ap.add_argument("--list", action="store_true", help="print the corner grid and exit")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    try:
        corners = grid(args.liberty, args.rc)
    except StaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.list:
        for c in corners:
            print(f"{c.label:32s} process={c.process} temp={c.temp_c:g}C vdd={c.vdd:.2f}V")
        return 0

    pdk = resolve_pdk()
    missing = check_environment(pdk)
    if missing:
        for reason in missing:
            print(f"ERROR  {reason}", file=sys.stderr)
        return 3

    openroad = openroad_version() or "unknown"
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    git = report.git_provenance(REPO_ROOT)
    records_dir = SIM_DIR / "records"

    results = []
    for c in corners:
        point = run_point(pdk, c, WORK_DIR)
        values = derive(point)
        results.append((point, values))
        print(
            f"{c.label:32s} setup {values['worst_setup_slack_ns']:8.3f} ns  "
            f"hold {values['worst_hold_slack_ns']:7.3f} ns  "
            f"fmax {values.get('fmax_bisect_mhz', float('nan')):7.2f} MHz  "
            f"P(1MHz) {values['p_total_1mhz_w'] * 1e3:7.3f} mW  "
            f"leak {values['p_leakage_w'] * 1e6:7.2f} uW  "
            f"[{point.wall_s:.1f}s]"
        )
        if not args.no_write:
            path = write_record(point, values, pdk, git, openroad, records_dir)
            print(f"  wrote {path.relative_to(REPO_ROOT)}")

    if args.json:
        print(json.dumps(
            [{"corner": p.corner.label, **v} for p, v in results], indent=2
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
