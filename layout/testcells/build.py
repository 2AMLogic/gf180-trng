#!/usr/bin/env python3
"""Emit the three layout-verification fixtures under `layout/testcells/`.

    python3 layout/testcells/build.py            # write the .gds files
    python3 layout/testcells/build.py --check    # rebuild in memory, compare bytes

The fixtures are a single trivial cell -- a CMOS inverter, `trng_tc_inv` --
in three variants that differ from each other by one deliberate edit. All
three streams declare the same top cell (`TOP_CELL`, see below); the variant
is carried by the file name:

| file stem             | DRC      | LVS vs `trng_tc_inv.spice` | what it proves             |
|-----------------------|----------|----------------------------|----------------------------|
| `trng_tc_inv`         | clean    | match                      | the flow passes good input |
| `trng_tc_inv_drcbad`  | 2 rules  | (not run)                  | DRC flags the right rules  |
| `trng_tc_inv_lvsbad`  | clean    | mismatch                   | LVS catches what DRC can't |

`trng_tc_inv_lvsbad` being *DRC-clean* is the point of that third variant: a
broken net that every geometric rule is happy with is exactly the class of
defect a DRC-only flow would ship.

None of these are design cells. They exist to exercise `klt drc`, `klt
extract` and `klt lvs` end to end, and nothing here should be read as a
statement about the TRNG's own layout. See `layout/README.md`.

Geometry is drawn on the curated-deck layer subset only (Nwell, Comp, Poly2,
Contact, Metal1, and Metal1's 34/10 label purpose) -- the layers `klt`'s
gf180mcu DRC and extraction decks actually read. Implant (Nplus/Pplus) and
the other sign-off layers are deliberately absent: adding them would not
change any result the curated decks produce, and drawing them here would
imply a fab-readiness these fixtures do not have.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gdsii import Label, Rect, write_gds  # noqa: E402

# --------------------------------------------------------------------------- #
# Layer numbers -- gf180mcu drawn layers, matching klt's curated decks.
# --------------------------------------------------------------------------- #
NWELL = (21, 0)
COMP = (22, 0)
POLY2 = (30, 0)
CONTACT = (33, 0)
METAL1 = (34, 0)
METAL1_LABEL = (34, 10)  # pin/label purpose the extraction deck reads

#: Drawn device dimensions, echoed into the reference netlist. `W` is the
#: Comp height crossed by the gate stripe; `L` is the gate stripe width.
DEVICE_W_UM = 0.80
DEVICE_L_UM = 0.28

TESTCELL_DIR = os.path.dirname(os.path.abspath(__file__))


def _rect(layer: tuple[int, int], x0: float, y0: float, x1: float, y1: float) -> Rect:
    return Rect(layer[0], layer[1], x0, y0, x1, y1)


def _label(layer: tuple[int, int], x: float, y: float, text: str) -> Label:
    return Label(layer[0], layer[1], x, y, text)


def _inverter_common() -> list[Rect]:
    """Every shape shared by all three variants.

    Coordinates in micrometres. The margins were chosen so that each
    curated gf180mcu DRC rule clears with room to spare, so that a future
    threshold correction in the deck does not turn the known-good fixture
    red for a reason unrelated to the flow:

    * Comp width 0.80 um (rule minimum 0.22), Comp-to-Comp 1.20 (min 0.28)
    * Poly2 width 0.28 um (min 0.18); one merged poly shape, so no spacing
    * Poly2/Comp overlap of every contact >= 0.09 um (min 0.07)
    * Contact 0.22 x 0.22 um (the deck's minimum, which is also the PDK's
      fixed contact size), closest contact-to-contact 0.43 (min 0.25)
    * Nwell overlap of the PMOS Comp 0.50 um on every side (min 0.12)
    """
    return [
        # --- diffusion ---------------------------------------------------
        _rect(COMP, 0.00, 0.00, 1.60, 0.80),  # NMOS active
        _rect(COMP, 0.00, 2.00, 1.60, 2.80),  # PMOS active
        _rect(NWELL, -0.50, 1.50, 2.10, 3.30),  # well around the PMOS
        # --- gate: one merged poly shape, stripe + landing pad ------------
        _rect(POLY2, 0.66, -0.30, 0.94, 3.10),  # gate stripe over both Comps
        _rect(POLY2, -0.60, 1.20, 0.94, 1.60),  # contact landing pad
        # --- contacts ----------------------------------------------------
        _rect(CONTACT, 0.15, 0.29, 0.37, 0.51),  # NMOS source -> VSS
        _rect(CONTACT, 1.23, 0.29, 1.45, 0.51),  # NMOS drain  -> ZN
        _rect(CONTACT, 0.15, 2.29, 0.37, 2.51),  # PMOS source -> VDD
        _rect(CONTACT, 1.23, 2.29, 1.45, 2.51),  # PMOS drain  -> ZN
        _rect(CONTACT, -0.50, 1.29, -0.28, 1.51),  # gate       -> A
        # --- metal1 ------------------------------------------------------
        _rect(METAL1, 0.08, 0.22, 0.44, 0.58),  # VSS pad
        _rect(METAL1, 0.08, 2.22, 0.44, 2.58),  # VDD pad
        _rect(METAL1, -0.57, 1.22, -0.21, 1.58),  # A pad
    ]


def _labels() -> list[Label]:
    """Metal1 pin labels, one per port net.

    Placed inside the metal shape that carries the net so `klt extract`
    names the extracted nets `A` / `ZN` / `VDD` / `VSS` instead of `$1`,
    `$2`, ... -- which is what makes the LVS report legible.
    """
    return [
        _label(METAL1_LABEL, -0.39, 1.40, "A"),
        _label(METAL1_LABEL, 1.34, 0.40, "ZN"),
        _label(METAL1_LABEL, 0.26, 2.40, "VDD"),
        _label(METAL1_LABEL, 0.26, 0.40, "VSS"),
    ]


def cell_good() -> list[Rect]:
    """`trng_tc_inv`: DRC-clean, LVS-matching."""
    shapes = _inverter_common()
    # Output strap: one metal run tying the NMOS drain to the PMOS drain.
    shapes.append(_rect(METAL1, 1.16, 0.22, 1.52, 2.58))
    return shapes


def cell_drc_bad() -> list[Rect]:
    """`trng_tc_inv_drcbad`: the good cell plus two deliberate defects.

    Both defects are *added* shapes rather than edits to the good geometry,
    so the two cells differ by exactly the two rectangles below and nothing
    else. Each defect targets one named rule:

    * a 0.15 um-wide Metal1 stub off the VSS pad -> `metal1.width.1`
      (deck minimum 0.23 um)
    * a Metal1 rectangle 0.16 um from the VDD pad -> `metal1.space.1`
      (deck minimum 0.23 um)
    """
    shapes = cell_good()
    shapes.append(_rect(METAL1, 0.20, 0.58, 0.35, 0.90))  # 0.15 um neck
    shapes.append(_rect(METAL1, 0.60, 2.22, 0.90, 2.58))  # 0.16 um gap to VDD
    return shapes


def cell_lvs_bad() -> list[Rect]:
    """`trng_tc_inv_lvsbad`: the good cell with the output strap cut.

    The single continuous drain strap is replaced by two stubs separated by
    1.64 um, so the NMOS drain and the PMOS drain land on different nets --
    an open circuit. Every geometric rule still clears (the gap is far
    wider than the 0.23 um Metal1 minimum), which is precisely why this
    variant is here: it is the defect class DRC structurally cannot see.
    """
    shapes = _inverter_common()
    shapes.append(_rect(METAL1, 1.16, 0.22, 1.52, 0.58))  # NMOS drain only
    shapes.append(_rect(METAL1, 1.16, 2.22, 1.52, 2.58))  # PMOS drain only
    return shapes


#: All three fixtures declare the *same* top-cell name. They are three
#: drawings of one cell -- one right, one geometrically wrong, one
#: electrically wrong -- and the variant lives in the file name, not the cell
#: name.
#:
#: This is load-bearing for LVS, not cosmetic: `klt lvs` pairs circuits by
#: name, and when the layout's top cell and the reference's `.SUBCKT` have
#: different names it cannot pair them at all. It still returns the correct
#: `status: mismatch` verdict, but every finding collapses to a generic
#: `topology` / "circuit could not be matched to a counterpart" entry instead
#: of naming the broken net and the orphaned device. Keeping the names equal
#: is what makes the known-bad LVS report diagnostic. (Filed as tool
#: friction -- see `layout/README.md`, "Tool friction".)
TOP_CELL = "trng_tc_inv"

#: file stem -> (builder, one-line purpose). The flow driver
#: (`layout/verify.py`) reads this, so adding a fixture here is enough to
#: put it in front of the tools.
FIXTURES = {
    "trng_tc_inv": (cell_good, "known-good inverter: DRC-clean, LVS-matching"),
    "trng_tc_inv_drcbad": (
        cell_drc_bad,
        "known-bad geometry: metal1.width.1 + metal1.space.1",
    ),
    "trng_tc_inv_lvsbad": (
        cell_lvs_bad,
        "known-bad connectivity: cut output strap, still DRC-clean",
    ),
}


def gds_path(stem: str) -> str:
    return os.path.join(TESTCELL_DIR, f"{stem}.gds")


def build(stem: str, path: str | None = None) -> bytes:
    """Write one fixture's GDSII stream and return its bytes."""
    builder, _purpose = FIXTURES[stem]
    return write_gds(
        path or gds_path(stem),
        library_name=TOP_CELL,
        structures=[(TOP_CELL, builder(), _labels())],
    )


def build_all() -> list[str]:
    return [gds_path(name) for name in FIXTURES if build(name) is not None]


def check_all() -> int:
    """Rebuild every fixture in memory and diff against the committed file.

    Returns a process exit code. This is the staleness guard: a geometry
    edit that is not accompanied by a regenerated `.gds` (and therefore by
    regenerated reports) fails here rather than silently invalidating every
    committed report.
    """
    failures = 0
    for stem in FIXTURES:
        path = gds_path(stem)
        shown = os.path.relpath(path, os.getcwd())
        if not os.path.exists(path):
            print(f"MISSING: {shown} -- run `python3 layout/testcells/build.py`")
            failures += 1
            continue
        # write_gds() must write somewhere; use a scratch path, then discard.
        scratch = path + ".check"
        try:
            rebuilt = build(stem, scratch)
        finally:
            if os.path.exists(scratch):
                os.remove(scratch)
        with open(path, "rb") as handle:
            committed = handle.read()
        if rebuilt != committed:
            print(
                f"STALE: {shown} does not match build.py "
                f"({len(committed)} bytes committed, {len(rebuilt)} rebuilt) -- "
                f"run `python3 layout/testcells/build.py`"
            )
            failures += 1
        else:
            print(f"ok: {shown}")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed .gds files match this script, and exit",
    )
    args = parser.parse_args(argv)

    if args.check:
        return check_all()

    for path in build_all():
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
