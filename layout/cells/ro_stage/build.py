#!/usr/bin/env python3
"""Draw and check `ro_stage`, the entropy source's repeated ring-stage cell.

    python3 layout/cells/ro_stage/build.py            # write ro_stage.gds
    python3 layout/cells/ro_stage/build.py --check     # rebuild, compare bytes

`ro_stage` is `design/ro_array_core.spice`'s `.subckt ro_stage` (from
`design/xschem/ro_stage.sch`): the series-starved minimum-width inverter that
is the ring's repeated delay element, drawn at ring1's sizing
(`wstv=0.220u`, the schematic's own default). The generator code, with the
full device-list and why-hand-drawn / why-dog-boned account, is shared with
`ro_stage_ring2` in `layout/cells/_ro_stage_shapes.py`; this file holds only
ring1's own constants and committed `.gds`.

Ring2's `ro_stage_ring2` draws `wstv=0.240u` from the same generator; see
`layout/cells/README.md` and `layout/cells/ro_stage_ring2/build.py` for why
the two committed streams stay distinct.
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
TOP_CELL = "ro_stage"

# Device sizing -- from design/xschem/ro_stage.sch's own default parameters
# (`G {wstv=0.22u lstv=2u cld=0.5f}`), which is also ring1's instantiation in
# design/ro_array_core.spice (`xr1 ... wstv=0.220u`). Echoed into
# ro_stage.spice; a change here must be mirrored there. Only W_STARVE differs
# from layout/cells/ro_stage_ring2/build.py's own 0.24 (ring2's value).
W_STARVE = 0.22  # Mph, Mnt (wstv)


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
    gds_path=gds_path, build=build, script="layout/cells/ro_stage/build.py"
)
main = make_main(
    check=check,
    gds_path=gds_path,
    build=build,
    description=__doc__.splitlines()[0],
)


if __name__ == "__main__":
    raise SystemExit(main())
