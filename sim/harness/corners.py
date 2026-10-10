"""Process / voltage / temperature corner definitions for gf180mcu.

The gf180mcu ngspice model library (``sm141064.ngspice``) exposes one
top-level ``.LIB`` section per device family per skew:

    MOS        typical | ff | ss | fs | sf
    BJT        bjt_typical | bjt_ff | bjt_ss
    diode      diode_typical | diode_ff | diode_ss
    resistor   res_typical | res_ff | res_ss
    MOS cap    moscap_typical | moscap_ff | moscap_ss
    MIM cap    mimcap_typical | mimcap_ff | mimcap_ss

A *named corner* here is therefore a bundle of sections, one per family.
``design.ngspice`` is always included ahead of them because it defines the
global switch params (``sw_stat_global``, ``fnoicor``, ...) the sections
reference.

This module is adapted from the corner-runner architecture bootstrapped in
2AMLogic/gf180-bandgap (gf180-bandgap#23); the section-name bundle is
generic gf180mcu PDK structure (public PDK fact, not this design's IP) and
was independently verified against the installed PDK before being reused
here (see the corner-sanity testbench under sim/tb/corner-sanity-nfet-id/,
which fails loudly if a corner selection stops changing device behavior).
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field

# Default PVT axes. CLAUDE.md mandates these on every recorded result.
DEFAULT_TEMPERATURES_C: tuple[float, ...] = (-40.0, 27.0, 125.0)
DEFAULT_SUPPLY_TOLERANCE: float = 0.10  # +/-10 %
DEFAULT_NOMINAL_SUPPLY_V: float = 3.3   # gf180mcu 3.3 V flavor


def _bundle(mos: str, bjt: str, diode: str, res: str, moscap: str, mimcap: str) -> tuple[str, ...]:
    return (mos, bjt, diode, res, moscap, mimcap)


@dataclass(frozen=True)
class Corner:
    """A named process corner: an ordered list of model ``.LIB`` sections."""

    name: str
    sections: tuple[str, ...]
    description: str = ""


def _all(skew: str, description: str) -> Corner:
    """Global corner: every device family skewed the same direction."""
    suffix = {"ff": "ff", "ss": "ss"}[skew]
    return Corner(
        name=skew,
        sections=_bundle(
            mos=suffix,
            bjt=f"bjt_{suffix}",
            diode=f"diode_{suffix}",
            res=f"res_{suffix}",
            moscap=f"moscap_{suffix}",
            mimcap=f"mimcap_{suffix}",
        ),
        description=description,
    )


_TYPICAL = _bundle(
    mos="typical",
    bjt="bjt_typical",
    diode="diode_typical",
    res="res_typical",
    moscap="moscap_typical",
    mimcap="mimcap_typical",
)

_FAMILY_INDEX = {"mos": 0, "bjt": 1, "diode": 2, "res": 3, "moscap": 4, "mimcap": 5}


def _mos_only(name: str, mos_section: str, description: str) -> Corner:
    """MOS skewed, passives at typical."""
    sections = (mos_section,) + _TYPICAL[1:]
    return Corner(name=name, sections=sections, description=description)


def _passive_only(name: str, family: str, section: str, description: str) -> Corner:
    sections = list(_TYPICAL)
    sections[_FAMILY_INDEX[family]] = section
    return Corner(name=name, sections=tuple(sections), description=description)


CORNERS: dict[str, Corner] = {
    "tt": Corner("tt", _TYPICAL, "all device families typical"),
    "ff": _all("ff", "all device families fast"),
    "ss": _all("ss", "all device families slow"),
    "fs": _mos_only("fs", "fs", "fast NMOS / slow PMOS, passives typical"),
    "sf": _mos_only("sf", "sf", "slow NMOS / fast PMOS, passives typical"),
    # Passive-dominated corners: some circuits' behavior rides on resistor
    # sheet rho or BJT Is/beta at least as much as on the MOS skew.
    "res_ff": _passive_only("res_ff", "res", "res_ff", "resistors fast (low rho), rest typical"),
    "res_ss": _passive_only("res_ss", "res", "res_ss", "resistors slow (high rho), rest typical"),
    "bjt_ff": _passive_only("bjt_ff", "bjt", "bjt_ff", "BJTs fast, rest typical"),
    "bjt_ss": _passive_only("bjt_ss", "bjt", "bjt_ss", "BJTs slow, rest typical"),
}

CORNER_SETS: dict[str, tuple[str, ...]] = {
    # Minimum bar for a quick smoke run.
    "tt": ("tt",),
    # The five classic MOS corners -- the default.
    "mos": ("tt", "ff", "ss", "fs", "sf"),
    # Everything: MOS corners plus resistor / BJT skews.
    "full": ("tt", "ff", "ss", "fs", "sf", "res_ff", "res_ss", "bjt_ff", "bjt_ss"),
}
DEFAULT_CORNER_SET = "mos"


def resolve_corners(names: list[str] | tuple[str, ...] | None) -> list[Corner]:
    """Turn a list of corner *or* corner-set names into Corner objects."""
    if not names:
        names = [DEFAULT_CORNER_SET]
    resolved: list[Corner] = []
    seen: set[str] = set()
    for name in names:
        expanded = CORNER_SETS.get(name, (name,))
        for corner_name in expanded:
            if corner_name in seen:
                continue
            if corner_name not in CORNERS:
                raise KeyError(
                    f"unknown corner {corner_name!r}; "
                    f"known corners: {', '.join(sorted(CORNERS))}; "
                    f"known sets: {', '.join(sorted(CORNER_SETS))}"
                )
            seen.add(corner_name)
            resolved.append(CORNERS[corner_name])
    return resolved


def supply_points(
    nominal_v: float = DEFAULT_NOMINAL_SUPPLY_V,
    tolerance: float = DEFAULT_SUPPLY_TOLERANCE,
) -> list[float]:
    """Nominal supply and its +/- tolerance rails, low to high.

    Raises :class:`ValueError` for a non-finite or non-positive nominal
    supply, a non-finite or negative tolerance, or a tolerance so large that
    a generated rail is not positive. A tolerance of exactly zero is the
    supported single-supply request. Values outside the ratified operating
    envelope are accepted: diagnostics may probe beyond it.
    """
    problems: list[str] = []
    if not (isinstance(nominal_v, (int, float)) and math.isfinite(nominal_v) and nominal_v > 0):
        problems.append(f"nominal supply must be finite and > 0 V, got {nominal_v!r}")
    if not (isinstance(tolerance, (int, float)) and math.isfinite(tolerance) and tolerance >= 0):
        problems.append(f"supply tolerance must be finite and >= 0, got {tolerance!r}")
    if problems:
        raise ValueError("invalid PVT plan -- " + "; ".join(problems))
    if tolerance == 0:
        return [round(nominal_v, 6)]
    rails = [
        round(nominal_v * (1.0 - tolerance), 6),
        round(nominal_v, 6),
        round(nominal_v * (1.0 + tolerance), 6),
    ]
    bad = [r for r in rails if not (math.isfinite(r) and r > 0)]
    if bad:
        raise ValueError(
            f"invalid PVT plan -- supply tolerance {tolerance!r} with nominal "
            f"{nominal_v!r} V generates non-positive or non-finite rail(s) {bad!r}"
        )
    return rails


@dataclass(frozen=True)
class PvtPoint:
    """One point in the PVT grid -- exactly one evidence record."""

    corner: Corner
    temp_c: float
    vdd: float
    index: int = field(default=0, compare=False)

    @property
    def corner_id(self) -> str:
        """The ``<process>_<temp>c_<supply>v`` id used for raw filenames."""
        return f"{self.corner.name}_{self.temp_c:g}c_{self.vdd:.2f}v"


def build_grid(
    corners: list[Corner],
    temperatures: list[float] | tuple[float, ...],
    supplies: list[float],
) -> list[PvtPoint]:
    """Full factorial P x V x T grid, in a stable, reproducible order."""
    points = [
        PvtPoint(corner=corner, temp_c=float(temp), vdd=float(vdd), index=i)
        for i, (corner, temp, vdd) in enumerate(
            itertools.product(corners, temperatures, supplies)
        )
    ]
    return points


def validate_grid(points: list[PvtPoint]) -> None:
    """Reject a grid that would schedule competing writes.

    Every point owns one evidence record and one raw/scratch directory named
    by its :attr:`PvtPoint.corner_id`, so the grid must contain no repeated
    effective point (e.g. a temperature passed twice) and no two distinct
    points whose formatted ids collide (supply is formatted to 10 mV and
    temperature with ``:g``, so e.g. 3.301 V and 3.304 V alias). Raises
    :class:`ValueError` naming every offending value, and also for an empty
    grid or a non-finite temperature / non-finite or non-positive supply; valid grids are left
    untouched, in their original order. Repeated points are rejected rather
    than silently dropped so the requested and executed plans never differ.
    """
    problems: list[str] = []
    if not points:
        raise ValueError(
            "invalid PVT plan -- the grid is empty (no corner, temperature or "
            "supply to simulate); check for an empty temperature or corner list"
        )
    for point in points:
        if not math.isfinite(point.temp_c):
            problems.append(
                f"temperature must be finite, got {point.temp_c!r} C "
                f"(corner={point.corner.name})"
            )
        if not (math.isfinite(point.vdd) and point.vdd > 0):
            problems.append(
                f"supply must be finite and > 0 V, got {point.vdd!r} V "
                f"(corner={point.corner.name})"
            )
    if problems:
        raise ValueError("invalid PVT plan -- " + "; ".join(dict.fromkeys(problems)))
    first_by_key: dict[tuple, PvtPoint] = {}
    first_by_id: dict[str, PvtPoint] = {}
    reported_keys: set[tuple] = set()
    reported_ids: set[str] = set()
    for point in points:
        key = (point.corner.name, point.temp_c, point.vdd)
        cid = point.corner_id
        if key in first_by_key:
            if key not in reported_keys:
                reported_keys.add(key)
                problems.append(
                    f"repeated PVT point {cid} (corner={point.corner.name}, "
                    f"temp={point.temp_c:g} C, vdd={point.vdd!r} V)"
                )
            continue
        first_by_key[key] = point
        if cid in first_by_id:
            if cid not in reported_ids:
                reported_ids.add(cid)
                other = first_by_id[cid]
                problems.append(
                    f"distinct PVT points share the output id {cid} "
                    f"(temp={other.temp_c!r} C, vdd={other.vdd!r} V vs "
                    f"temp={point.temp_c!r} C, vdd={point.vdd!r} V)"
                )
            continue
        first_by_id[cid] = point
    if problems:
        raise ValueError(
            "invalid PVT plan -- " + "; ".join(problems)
            + ". Each point must be distinct and map to its own output id; "
            "run repeated diagnostics as separate invocations."
        )
