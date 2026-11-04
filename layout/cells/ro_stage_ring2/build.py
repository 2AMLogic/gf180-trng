#!/usr/bin/env python3
"""Draw and check `ro_stage` at ring2's sizing (`wstv=0.240u`).

    python3 layout/cells/ro_stage_ring2/build.py            # write ro_stage_ring2.gds
    python3 layout/cells/ro_stage_ring2/build.py --check     # rebuild, compare bytes

Same cell, same topology, as `layout/cells/ro_stage/build.py` (`ro_stage`,
`design/ro_array_core.spice`'s `.subckt ro_stage`). The only difference is the
starve width: ring1's `ro_stage` draws `wstv=0.220u`; this cell draws ring2's
own instantiation (`design/ro_array_core.spice`'s `xr2 ... wstv=0.240u`).

That 0.020u difference is not cosmetic. `design/ro_array_core.spice`
deliberately gives the array's two rings different starve widths -- and
therefore different oscillation frequencies -- so that ring1 and ring2 are
not frequency-matched (`layout/floorplan/README.md`, "Mechanism 1": a
non-integer frequency ratio is load-bearing for the two rings' independence
argument the entropy source's isolation floorplan depends on). A layout that
reused ring1's drawn geometry under a new label would silently defeat that
mechanism -- DRC/LVS cannot see it, since both variants are legal, connected,
four-device inverters; only drawing the starve device at its own width
represents the design ring2 actually specifies.

The generator code is shared with `ro_stage` (`layout/cells/_ro_stage_shapes.py`,
which holds the device-list and layout-technique account); the geometry is
not. `W_STARVE` stays a per-ring constant here, it moves the starve channel
bands and splits ring2's NMOS channel into separate per-device bands, so the
two `.gds` files are distinct and -- per `layout/cells/README.md` --
independently byte-checked, DRC'd and LVS'd.
"""

from __future__ import annotations

import os
import sys

_TESTCELL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "testcells"
)
sys.path.insert(0, os.path.abspath(_TESTCELL_DIR))
_CELLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.abspath(_CELLS_DIR))

from _build_cli import gds_file, make_check, make_main  # noqa: E402
from gdsii import write_gds  # noqa: E402
from _ro_stage_shapes import build_shapes  # noqa: E402

CELL_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_CELL = "ro_stage_ring2"

# Device sizing -- design/ro_array_core.spice's ring2 instantiation
# (`xr2 en2 rn2 vddr2 vss ro_ring11 wstv=0.240u lstv=2u cld=0.5f`). Echoed
# into ro_stage_ring2.spice; a change here must be mirrored there. Only
# W_STARVE differs from layout/cells/ro_stage/build.py's own 0.22 (ring1's
# value).
W_STARVE = 0.24  # Mph, Mnt (wstv, ring2)


def gds_path() -> str:
    return gds_file(CELL_DIR, TOP_CELL)


def build(path: str | None = None) -> bytes:
    rects, labels = build_shapes(W_STARVE)
    return write_gds(
        path or gds_path(),
        library_name=TOP_CELL,
        structures=[(TOP_CELL, rects, labels)],
    )


# The check/CLI tail is the shared one (`_build_cli.py`, #589);
# `layout/verify.py`'s `_STALENESS_CHECKS` calls this module's `check()`
# with no arguments.
check = make_check(
    gds_path=gds_path, build=build, script="layout/cells/ro_stage_ring2/build.py"
)
main = make_main(
    check=check,
    gds_path=gds_path,
    build=build,
    description=__doc__.splitlines()[0],
)


if __name__ == "__main__":
    raise SystemExit(main())
