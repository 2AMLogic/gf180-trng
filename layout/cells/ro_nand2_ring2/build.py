#!/usr/bin/env python3
"""Draw and check `ro_nand2` at ring2's sizing (`wstv=0.240u`).

    python3 layout/cells/ro_nand2_ring2/build.py            # write ro_nand2_ring2.gds
    python3 layout/cells/ro_nand2_ring2/build.py --check     # rebuild, compare bytes

Same cell, same topology, as `layout/cells/ro_nand2/build.py` (`ro_nand2`,
`design/ro_array_core.spice`'s `.subckt ro_nand2`). The only difference is the
starve width: ring1's `ro_nand2` draws `wstv=0.220u`; this cell draws ring2's
own instantiation (`design/ro_array_core.spice`'s
`xr2 ... ro_ring11 wstv=0.240u ...`), the same `wstv=0.220u -> 0.240u`
single-dimension change `layout/cells/ro_stage_ring2/build.py` made relative
to `layout/cells/ro_stage/build.py`.

The generator code is shared with `ro_nand2` (`layout/cells/_ro_nand2_shapes.py`,
which holds the device-list and layout-technique account); the geometry is not.
That 0.020u difference shifts the `XMph`/`XMnt` channel bands' own Y
coordinates, so the two `.gds` files are distinct, and -- per
`layout/cells/README.md` -- independently byte-checked, DRC'd and LVS'd.
Ring1/ring2 are deliberately frequency-mismatched
(`layout/floorplan/README.md`'s "Mechanism 1"); that is a property of the
differing `W_STARVE`, which stays a per-ring constant here.
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
from gdsii import add_implants, write_gds  # noqa: E402
from _ro_nand2_shapes import build_shapes  # noqa: E402

CELL_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_CELL = "ro_nand2_ring2"

# Device sizing -- design/ro_array_core.spice's ring2 instantiation
# (`xr2 en2 rn2 vddr2 vss ro_ring11 wstv=0.240u lstv=2u cld=0.5f`). Echoed
# into ro_nand2_ring2.spice; a change here must be mirrored there. Only
# W_STARVE differs from layout/cells/ro_nand2/build.py's own 0.22 (ring1's
# value).
W_STARVE = 0.24  # XMph, XMnt (wstv)


def gds_path() -> str:
    return gds_file(CELL_DIR, TOP_CELL)


def build(path: str | None = None) -> bytes:
    rects, labels = build_shapes(W_STARVE)
    return write_gds(
        path or gds_path(),
        library_name=TOP_CELL,
        structures=[(TOP_CELL, add_implants(rects), labels)],
    )


# The check/CLI tail is the shared one (`_build_cli.py`, #589);
# `layout/verify.py`'s `_STALENESS_CHECKS` calls this module's `check()`
# with no arguments.
check = make_check(
    gds_path=gds_path, build=build, script="layout/cells/ro_nand2_ring2/build.py"
)
main = make_main(
    check=check,
    gds_path=gds_path,
    build=build,
    description=__doc__.splitlines()[0],
)


if __name__ == "__main__":
    raise SystemExit(main())
