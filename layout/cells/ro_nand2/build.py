#!/usr/bin/env python3
"""Draw and check `ro_nand2`, the ring's one stoppable stage.

    python3 layout/cells/ro_nand2/build.py            # write ro_nand2.gds
    python3 layout/cells/ro_nand2/build.py --check     # rebuild, compare bytes

The geometry generator is shared with `ro_nand2_ring2` (`layout/cells/_ro_nand2_shapes.py`,
which also holds the full device-list and layout-technique account); this file
supplies ring1's starve width and owns the committed `ro_nand2.gds`.
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
TOP_CELL = "ro_nand2"

# Device sizing -- design/xschem/ro_nand2.sch's own default parameters
# (`wstv=0.22u`, ring1's value). Echoed into ro_nand2.spice; a change here
# must be mirrored there.
W_STARVE = 0.22  # XMph, XMnt (wstv)


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
    gds_path=gds_path, build=build, script="layout/cells/ro_nand2/build.py"
)
main = make_main(
    check=check,
    gds_path=gds_path,
    build=build,
    description=__doc__.splitlines()[0],
)


if __name__ == "__main__":
    raise SystemExit(main())
