#!/usr/bin/env python3
"""Run the gf180mcu DRC + LVS flow over `layout/testcells/` (and any real
design cell wired in below) and check it.

    python3 layout/verify.py                # run the flow, assert expectations
    python3 layout/verify.py --write        # ... and refresh layout/reports/
    python3 layout/verify.py --require-tools  # fail (not skip) if klt/PDK absent
    python3 layout/verify.py --list         # print the fixture/expectation table

This is the layout-side analogue of `sim/selftest.sh`: it exists so that
"the DRC/LVS flow works" is a claim somebody can re-run in one command
instead of a claim somebody has to believe.

What it does, per entry in `EXPECTATIONS` (each entry's own `dir`/`build`
module owns the geometry -- `layout/testcells/build.py` for the flow-bringup
fixtures, `layout/cells/<cell>/build.py` for a real design cell):

1. `klt drc  <stem>.gds --deck gf180mcu`
2. `klt extract <stem>.gds --deck gf180mcu --pdk <variant>`
3. `klt lvs  <request>`  -- only for entries with an LVS expectation

...then compares each result against the expectation declared in
`EXPECTATIONS` below. **The expectations are the test.** A tool upgrade that
silently stopped reporting `metal1.width.1`, or a comparer that started
calling the cut-strap fixture a match, fails here -- which is the whole
reason the known-bad fixtures exist. A run that merely *ran* is not a pass.

Reports land under `layout/reports/` as the verbatim JSON `klt` emitted,
plus the extracted netlists. Those are the checked-in evidence; this script
is what regenerates them. See `layout/README.md`.

Standard library only, like the rest of the repo's tooling: everything that
touches KLayout goes through the `klt` command line, which is the point --
the flow is the tool's public interface, not a Python API this repo pins.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LAYOUT_DIR = REPO_ROOT / "layout"
TESTCELL_DIR = LAYOUT_DIR / "testcells"
CELLS_DIR = LAYOUT_DIR / "cells"
REPORT_DIR = LAYOUT_DIR / "reports"

#: Scratch space (git-ignored). Every tool that writes a file writes it here
#: first, in both `--write` and check mode, so that a check run never touches
#: a committed artefact -- and so that the paths echoed into the reports are
#: the same either way. `layout/reports/` is then updated by copy, or diffed
#: against, from here.
WORK_DIR = LAYOUT_DIR / ".work"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(TESTCELL_DIR))

import build as testcells  # noqa: E402  (layout/testcells/build.py)
from layout._klt import FlowError, _run_klt, klt_version, resolve_pdk  # noqa: E402


def _load_build_module(name: str, path: Path):
    """Load a `build.py` under a unique module name.

    Every fixture/cell directory names its geometry module `build.py` (see
    `layout/README.md`, "Adding a cell to the flow"), so a second plain
    `import build` would just return the *first* one back out of
    `sys.modules` under a different local alias -- `layout/testcells/build`
    and `layout/cells/ro_stage/build` are two different files that happen to
    share a bare module name, not the same module. Loading each one from its
    own path, under its own `sys.modules` key, is what keeps them distinct.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RINGS_DIR = LAYOUT_DIR / "rings"
BLOCKS_DIR = LAYOUT_DIR / "blocks"

ro_stage_cell = _load_build_module(
    "layout_cells_ro_stage_build", CELLS_DIR / "ro_stage" / "build.py"
)
ro_stage_ring2_cell = _load_build_module(
    "layout_cells_ro_stage_ring2_build", CELLS_DIR / "ro_stage_ring2" / "build.py"
)
ro_nand2_cell = _load_build_module(
    "layout_cells_ro_nand2_build", CELLS_DIR / "ro_nand2" / "build.py"
)
ro_nand2_ring2_cell = _load_build_module(
    "layout_cells_ro_nand2_ring2_build", CELLS_DIR / "ro_nand2_ring2" / "build.py"
)
ro_buf_cell = _load_build_module(
    "layout_cells_ro_buf_build", CELLS_DIR / "ro_buf" / "build.py"
)
xor2_cell = _load_build_module("layout_cells_xor2_build", CELLS_DIR / "xor2" / "build.py")
sampler_dff_cell = _load_build_module(
    "layout_cells_sampler_dff_build", CELLS_DIR / "sampler_dff" / "build.py"
)
ro_ring11_cell = _load_build_module(
    "layout_rings_ro_ring11_build", RINGS_DIR / "ro_ring11" / "build.py"
)
ro_ring11_ring2_cell = _load_build_module(
    "layout_rings_ro_ring11_ring2_build", RINGS_DIR / "ro_ring11_ring2" / "build.py"
)
combiner_sampler_block = _load_build_module(
    "layout_blocks_combiner_sampler_build", BLOCKS_DIR / "combiner_sampler" / "build.py"
)

#: (relative-to-repo-root fixture/cell dir, its build module) for every
#: `EXPECTATIONS` entry's `staleness` field -- see "Adding a cell to the
#: flow" in layout/README.md. Each module owns its own `.gds` and exposes
#: either `check_all()` (layout/testcells/build.py, several fixtures) or
#: `check()` (a single-cell module like layout/cells/ro_stage/build.py).
_STALENESS_CHECKS = (
    ("layout/testcells", testcells.check_all),
    ("layout/cells/ro_stage", ro_stage_cell.check),
    ("layout/cells/ro_stage_ring2", ro_stage_ring2_cell.check),
    ("layout/cells/ro_nand2", ro_nand2_cell.check),
    ("layout/cells/ro_nand2_ring2", ro_nand2_ring2_cell.check),
    ("layout/cells/ro_buf", ro_buf_cell.check),
    ("layout/cells/xor2", xor2_cell.check),
    ("layout/cells/sampler_dff", sampler_dff_cell.check),
    ("layout/rings/ro_ring11", ro_ring11_cell.check),
    ("layout/rings/ro_ring11_ring2", ro_ring11_ring2_cell.check),
    ("layout/blocks/combiner_sampler", combiner_sampler_block.check),
)

#: The DRC deck / extraction deck name `klt` knows this PDK family by. Not
#: the PDK *variant* (gf180mcuA..D) -- klt's curated decks are per-family.
DECK = "gf180mcu"

#: Exit codes. Mirrors sim/selftest.sh: 0 pass or deliberate skip, 1 fail.
EXIT_OK = 0
EXIT_FAIL = 1


# --------------------------------------------------------------------------- #
# Expectations -- the actual test
# --------------------------------------------------------------------------- #
#
# `drc.rule_counts` is compared for exact equality, not "at least": a
# known-bad fixture that starts reporting a *third* rule has drifted and the
# report no longer says what this file claims it says.
#
# `lvs.category_counts` is compared the same way. `lvs.reference` names the
# schematic-side netlist under layout/testcells/; a fixture with no `lvs`
# key is not LVS'd at all.
#
# `lvs.error_count` is how many of the reported mismatches carry
# `severity: "error"`. It exists because `category_counts` alone cannot say
# whether a category is a finding or a disclosure, and this table has to
# carry two `severity: "warning"` categories on *every* fixture:
#
#   device.body_unverified x2   one per MOS: the deck compares each device's
#                               body terminal against a net it synthesized
#                               (`vsubs` for NMOS, an anonymous well net for
#                               PMOS) rather than a real schematic net, so
#                               that terminal was not actually verified.
#                               This is the deck limitation layout/README.md
#                               has always documented in prose under "Bulk
#                               terminals are approximated"; klayout-tools
#                               #281 made the tool state it per run instead.
#   topology x1                 a device class the deck declares (bjt,
#                               cap_mim, resistor -- klayout-tools #219/#227)
#                               has no counterpart on the reference side, and
#                               zero devices of it were extracted. The tool
#                               says so itself: "not a real topology
#                               mismatch".
#
# Both appeared on 2026-08-02 without any version string moving -- see
# layout/README.md, "Pinning the tool", for why `klt --version` could not
# have told us and what identifies a klt build instead. They are recorded
# rather than filtered out because the point of this table is that a report
# says the same thing tomorrow as today; and `error_count` is checked
# alongside them so that absorbing two warnings did not quietly buy a pass
# for a future *error* landing in the same category.
EXPECTATIONS: dict[str, dict] = {
    "trng_tc_inv": {
        "why": "known-good: the flow must pass a correct cell",
        "drc": {"status": "clean", "rule_counts": {}},
        "lvs": {
            "reference": "trng_tc_inv.spice",
            "status": "match",
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            # Nothing the tool calls an error. That, not `status: match`
            # alone, is what "the flow accepts a correct cell" means now.
            "error_count": 0,
        },
    },
    "trng_tc_inv_drcbad": {
        "why": "known-bad geometry: DRC must flag these two rules and no others",
        "drc": {
            "status": "violations",
            "rule_counts": {"metal1.width.1": 1, "metal1.space.1": 1},
        },
        # Deliberately not LVS'd: its defects are geometric, and running LVS
        # on it would only prove that a shape nobody connected anything to
        # does not change the netlist.
    },
    "trng_tc_inv_lvsbad": {
        "why": "known-bad connectivity: DRC must stay clean and LVS must fail",
        "drc": {"status": "clean", "rule_counts": {}},
        "lvs": {
            "reference": "trng_tc_inv.spice",
            "status": "mismatch",
            # The two `severity: "error"` categories below are the defect
            # this fixture exists to catch, and they are what `error_count`
            # counts. The two warning categories are the same deck
            # disclosures the known-good fixture carries -- present here
            # because they describe the deck, not the defect.
            "category_counts": {
                "net.unmatched": 1,
                "device.unmatched": 1,
                "device.body_unverified": 2,
                "topology": 1,
            },
            "error_count": 2,
        },
    },
    "ro_stage": {
        # A real design cell, not a flow-bringup fixture -- see
        # layout/cells/README.md for scope and layout/cells/ro_stage/build.py
        # for the geometry and why it is hand-drawn. `dir`/`top` override the
        # `layout/testcells/`-and-`trng_tc_inv` default every other entry
        # above uses; every stage function below reads them with that
        # default, per "Adding a cell to the flow" in layout/README.md.
        "why": (
            "design/ro_array_core.spice's ro_stage (ring1 sizing): the "
            "entropy source's repeated ring-stage cell must be DRC-clean "
            "and LVS-match its hand-written schematic-side reference"
        ),
        "dir": "layout/cells/ro_stage",
        "top": "ro_stage",
        "drc": {"status": "clean", "rule_counts": {}},
        "lvs": {
            "reference": "ro_stage.spice",
            "status": "match",
            # Same two deck-level disclosures every fixture above carries
            # (see the module-level comment above `EXPECTATIONS`) -- this
            # cell's four devices are all MOS, so nothing else is declared.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "error_count": 0,
        },
    },
    "ro_stage_ring2": {
        # A real design cell, not a flow-bringup fixture -- see
        # layout/cells/README.md for scope and
        # layout/cells/ro_stage_ring2/build.py for the geometry and why it
        # is hand-drawn. `dir`/`top` override the defaults, same as the
        # `ro_stage` entry above.
        "why": (
            "design/ro_array_core.spice's ro_stage at ring2's own sizing "
            "(wstv=0.240u, distinct drawn geometry from ring1's ro_stage/ "
            "-- see layout/cells/README.md, 'Mechanism 1') must be "
            "DRC-clean and LVS-match its hand-written schematic-side "
            "reference"
        ),
        "dir": "layout/cells/ro_stage_ring2",
        "top": "ro_stage_ring2",
        "drc": {"status": "clean", "rule_counts": {}},
        "lvs": {
            "reference": "ro_stage_ring2.spice",
            "status": "match",
            # Same two deck-level disclosures every fixture above carries
            # (see the module-level comment above `EXPECTATIONS`) -- this
            # cell's four devices are all MOS, so nothing else is declared.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "error_count": 0,
        },
    },
    "ro_nand2": {
        # A real design cell, not a flow-bringup fixture -- see
        # layout/cells/README.md for scope and layout/cells/ro_nand2/build.py
        # for the geometry (including the drawn parallel-pull-up technique)
        # and why it is hand-drawn. `dir`/`top` override the defaults, same
        # as the `ro_stage` entry above.
        "why": (
            "design/ro_array_core.spice's ro_nand2 (the ring's one "
            "stoppable stage) must be DRC-clean and LVS-match its "
            "hand-written schematic-side reference"
        ),
        "dir": "layout/cells/ro_nand2",
        "top": "ro_nand2",
        "drc": {"status": "clean", "rule_counts": {}},
        "lvs": {
            "reference": "ro_nand2.spice",
            "status": "match",
            # Same two deck-level disclosures every fixture above carries
            # (see the module-level comment above `EXPECTATIONS`) -- this
            # cell's six devices are all MOS, so nothing else is declared.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "error_count": 0,
        },
    },
    "ro_nand2_ring2": {
        # A real design cell, not a flow-bringup fixture -- see
        # layout/cells/README.md for scope and
        # layout/cells/ro_nand2_ring2/build.py for the geometry (the same
        # drawn parallel-pull-up technique as ro_nand2/, at ring2's own
        # starve width) and why it is hand-drawn. `dir`/`top` override the
        # defaults, same as the `ro_stage_ring2` entry above.
        "why": (
            "design/ro_array_core.spice's ro_nand2 at ring2's own sizing "
            "(wstv=0.240u, distinct drawn geometry from ring1's ro_nand2/ "
            "-- see layout/cells/README.md, 'Mechanism 1') must be "
            "DRC-clean and LVS-match its hand-written schematic-side "
            "reference"
        ),
        "dir": "layout/cells/ro_nand2_ring2",
        "top": "ro_nand2_ring2",
        "drc": {"status": "clean", "rule_counts": {}},
        "lvs": {
            "reference": "ro_nand2_ring2.spice",
            "status": "match",
            # Same two deck-level disclosures every fixture above carries
            # (see the module-level comment above `EXPECTATIONS`) -- this
            # cell's six devices are all MOS, so nothing else is declared.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "error_count": 0,
        },
    },
    "ro_buf": {
        # A real design cell, not a flow-bringup fixture -- see
        # layout/cells/README.md for scope and layout/cells/ro_buf/build.py
        # for the geometry and why it is hand-drawn. `dir`/`top` override
        # the defaults, same as the `ro_stage` entry above.
        #
        # One drawn cell, two instances: design/ro_array_core.spice's `xb1`
        # and `xb2` both take the bare `ro_buf` subcircuit with no parameter
        # override, so there is no ring1/ring2 split here of the kind
        # ro_stage/ro_stage_ring2 and ro_nand2/ro_nand2_ring2 need.
        "why": (
            "design/trng_top.spice's ro_buf (the per-ring output buffer "
            "DR-0018 adopted, instantiated twice in ro_array_core as "
            "xb1/xb2) must be DRC-clean and LVS-match its hand-written "
            "schematic-side reference"
        ),
        "dir": "layout/cells/ro_buf",
        "top": "ro_buf",
        "drc": {"status": "clean", "rule_counts": {}},
        "lvs": {
            "reference": "ro_buf.spice",
            "status": "match",
            # Same two deck-level disclosures every fixture above carries
            # (see the module-level comment above `EXPECTATIONS`) -- this
            # cell's two devices are both MOS, so nothing else is declared.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "error_count": 0,
        },
    },
    "xor2": {
        # A real design cell, not a flow-bringup fixture -- see
        # layout/cells/README.md for scope and layout/cells/xor2/build.py
        # for the geometry and why it is hand-drawn. `dir`/`top` override
        # the `layout/testcells/`-and-`trng_tc_inv` default, per
        # "Adding a cell to the flow" in layout/README.md.
        "why": (
            "design/ro_array_core.spice's xor2 (the entropy source's "
            "combiner gate) must be DRC-clean and LVS-match its "
            "hand-written schematic-side reference"
        ),
        "dir": "layout/cells/xor2",
        "top": "xor2",
        "drc": {"status": "clean", "rule_counts": {}},
        "lvs": {
            "reference": "xor2.spice",
            "status": "match",
            # Same two deck-level disclosures every fixture above carries
            # (see the module-level comment above `EXPECTATIONS`) -- this
            # cell's twelve devices are all MOS, so nothing else is
            # declared.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "error_count": 0,
        },
    },
    "sampler_dff": {
        # A real design cell, not a flow-bringup fixture -- see
        # layout/cells/README.md for scope and
        # layout/cells/sampler_dff/build.py for the geometry and why it is
        # hand-drawn. `dir`/`top` override the `layout/testcells/`-and-
        # `trng_tc_inv` default, per "Adding a cell to the flow" in
        # layout/README.md.
        "why": (
            "design/sampler_core.spice's sampler_dff (the sampler's "
            "transmission-gate master-slave DFF, instantiated four times "
            "unmodified in sampler_core) must be DRC-clean and LVS-match "
            "its hand-written schematic-side reference"
        ),
        "dir": "layout/cells/sampler_dff",
        "top": "sampler_dff",
        "drc": {"status": "clean", "rule_counts": {}},
        "lvs": {
            "reference": "sampler_dff.spice",
            "status": "match",
            # Same two deck-level disclosures every fixture above carries
            # (see the module-level comment above `EXPECTATIONS`) -- this
            # cell's twenty-two devices are all MOS, so nothing else is
            # declared.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "error_count": 0,
        },
    },
    "ro_ring11": {
        # An assembled block, not a hand-drawn single cell -- see
        # layout/rings/README.md for scope and
        # layout/rings/ro_ring11/build.py for how ten already-verified
        # `ro_stage` instances plus one `ro_nand2` are placed into a row and
        # wired (issue #110). `dir`/`top` override the defaults, same as
        # every other real-design entry above.
        "why": (
            "design/ro_array_core.spice's ro_ring11 (ring1 sizing, "
            "wstv=0.220u): the assembled entropy-source ring must be "
            "DRC-clean and LVS-match a reference netlist mechanically "
            "expanded from ro_stage.spice/ro_nand2.spice per the ring's "
            "own declared connectivity"
        ),
        "dir": "layout/rings/ro_ring11",
        "top": "ro_ring11",
        "drc": {"status": "clean", "rule_counts": {}},
        "lvs": {
            "reference": "ro_ring11.spice",
            "status": "match",
            # Same two deck-level disclosures every fixture above carries
            # (see the module-level comment above `EXPECTATIONS`) -- all
            # forty-six devices here are MOS, so nothing else is declared.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "error_count": 0,
        },
    },
    "ro_ring11_ring2": {
        # An assembled block, not a hand-drawn single cell -- see
        # layout/rings/README.md for scope and
        # layout/rings/ro_ring11_ring2/build.py for how ten already-verified
        # `ro_stage_ring2` instances plus one `ro_nand2_ring2` are placed
        # into a row and wired, the same technique `ro_ring11/build.py`
        # (ring1 sizing) uses (issue #118). `dir`/`top` override the
        # defaults, same as every other real-design entry above.
        "why": (
            "design/ro_array_core.spice's ro_ring11 (ring2 sizing, "
            "wstv=0.240u): the assembled entropy-source ring must be "
            "DRC-clean and LVS-match a reference netlist mechanically "
            "expanded from ro_stage_ring2.spice/ro_nand2_ring2.spice per "
            "the ring's own declared connectivity"
        ),
        "dir": "layout/rings/ro_ring11_ring2",
        "top": "ro_ring11_ring2",
        "drc": {"status": "clean", "rule_counts": {}},
        "lvs": {
            "reference": "ro_ring11_ring2.spice",
            "status": "match",
            # Same two deck-level disclosures every fixture above carries
            # (see the module-level comment above `EXPECTATIONS`) -- all
            # forty-six devices here are MOS, so nothing else is declared.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "error_count": 0,
        },
    },
    "combiner_sampler": {
        # An assembled block, not a hand-drawn single cell -- see
        # layout/blocks/README.md for scope and layout/blocks/
        # combiner_sampler/build.py for how two already-verified `ro_buf`
        # instances, one already-verified `xor2` instance and four
        # already-verified `sampler_dff` instances are placed into a row
        # and wired (issues #134 and #151). `dir`/`top` override the
        # defaults, same as every other real-design entry above.
        #
        # Placed inside layout/floorplan/'s own `combiner_sampler` guarded
        # region -- that region is sized from this block's own real bbox
        # (issue #135) and fit-checked against it (`check_ring_fit`,
        # layout/floorplan/floorplan.py).
        "why": (
            "design/ro_array_core.spice's xb1/xb2 (ro_buf) plus design/"
            "sampler_core.spice's combiner_sampler (xa1/xsb/xsv/xsr1/"
            "xsr2): the assembled buffer+combiner+sampler block must be "
            "DRC-clean and LVS-match a reference netlist mechanically "
            "expanded from ro_buf.spice/xor2.spice/sampler_dff.spice per "
            "the block's own declared connectivity"
        ),
        "dir": "layout/blocks/combiner_sampler",
        "top": "combiner_sampler",
        "drc": {"status": "clean", "rule_counts": {}},
        "lvs": {
            "reference": "combiner_sampler.spice",
            "status": "match",
            # Same two deck-level disclosures every fixture above carries
            # (see the module-level comment above `EXPECTATIONS`) -- all
            # one hundred and four devices here are MOS, so nothing else is
            # declared.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "error_count": 0,
        },
    },
}


# --------------------------------------------------------------------------- #
# Environment
# --------------------------------------------------------------------------- #


#: Asks the `klt` venv's own interpreter what it installed. `importlib.metadata`
#: only sees distributions on the interpreter running it, and `klt` lives in its
#: own pipx/uv venv, so the question has to be asked over there.
_KLT_ORIGIN_PROBE = (
    "import importlib.metadata as m;"
    "print(m.distribution('klayout-tools').read_text('direct_url.json') or '')"
)


def klt_origin() -> dict | None:
    """Return what a `klt` install was built from, or None if unknowable.

    `klt --version` reports `0.1.0` for every build of klayout-tools to date,
    including installs straight off the tip of its main branch -- which is
    what `pipx install klayout-tools` / `uv tool install klayout-tools` from
    the repository URL gives you. So the version string does not identify a
    build, and on 2026-08-02 two `0.1.0` installs produced different LVS
    reports for the same fixture (#73). The commit does identify it.

    Best effort by construction: an install from a wheel has no upstream
    commit to report, and a layout this does not recognise reports nothing
    rather than guessing. A None here means "not recorded", never "the same
    as last time".
    """
    executable = shutil.which("klt")
    if executable is None:
        return None
    try:
        # The console script's shebang names the interpreter of the venv the
        # distribution is installed into -- the one that can answer.
        script = Path(executable).resolve().read_text(errors="replace")
    except OSError:
        return None
    shebang = script.split("\n", 1)[0]
    if not shebang.startswith("#!"):
        return None
    try:
        done = subprocess.run(
            [shebang[2:].strip(), "-c", _KLT_ORIGIN_PROBE],
            capture_output=True,
            text=True,
            timeout=60,
        )
        record = json.loads(done.stdout.strip())
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return None
    if not isinstance(record, dict):
        return None
    return {
        "url": record.get("url"),
        "commit": (record.get("vcs_info") or {}).get("commit_id"),
    }


def environment_report() -> dict:
    version = klt_version()
    pdk = resolve_pdk()
    return {
        "klt": version,
        "klt_origin": klt_origin(),
        "deck": DECK,
        "pdk": pdk.provenance() if pdk is not None else None,
        "platform": f"{os.uname().sysname} {os.uname().release} {os.uname().machine}",
    }


# --------------------------------------------------------------------------- #
# klt invocations
# --------------------------------------------------------------------------- #


def _fixture_dir(spec: dict) -> str:
    """Repo-root-relative directory holding one `EXPECTATIONS` entry's `.gds`.

    Defaults to `layout/testcells` (every flow-bringup fixture); a real
    design cell overrides this with its own `dir`, e.g.
    `layout/cells/ro_stage` -- see "Adding a cell to the flow" in
    `layout/README.md`.
    """
    return spec.get("dir", "layout/testcells")


def _fixture_top(spec: dict) -> str:
    """The `.gds` top-cell name for one `EXPECTATIONS` entry.

    Defaults to `testcells.TOP_CELL` (`trng_tc_inv`, shared by all three
    fixtures there -- see `layout/testcells/build.py`'s own docstring on why
    that name is shared). A real design cell overrides this with its own
    `top`, matching its `.SUBCKT` name.
    """
    return spec.get("top", testcells.TOP_CELL)


def run_drc(stem: str, spec: dict) -> dict:
    return _run_klt([
        "drc",
        f"{_fixture_dir(spec)}/{stem}.gds",
        "--deck",
        DECK,
    ])


def run_extract(stem: str, spec: dict, pdk_variant: str | None) -> dict:
    """Extract into the scratch dir. The netlist is copied/diffed later.

    `layout/.work/` sits at the same depth as `layout/reports/`, so the
    relative paths *inside* an emitted artefact (notably the LVS request's
    `../testcells/...` / `../cells/<cell>/...`) mean the same thing from
    either directory. The one field that does depend on where the file
    landed is the extract report's own `netlist_path`, which `klt` echoes
    back from `-o`; `_committed_view` below restates it before the report is
    written or compared.
    """
    args = [
        "extract",
        f"{_fixture_dir(spec)}/{stem}.gds",
        "--deck",
        DECK,
        "--top",
        _fixture_top(spec),
        "-o",
        f"layout/.work/{stem}.extracted.spice",
    ]
    if pdk_variant:
        args += ["--pdk", pdk_variant]
    return _run_klt(args)


def lvs_request(stem: str, spec: dict, reference: str) -> dict:
    """The LVS request document for one fixture/cell.

    Committed under `layout/reports/` so the exact invocation is
    reproducible by hand. Paths are relative to the request file's own
    directory, which is how `klt lvs` resolves them -- computed here from
    `_fixture_dir(spec)` rather than hard-coded, so a `dir` override (a real
    design cell living outside `layout/testcells/`) still resolves.
    """
    rel_dir = os.path.relpath(str(REPO_ROOT / _fixture_dir(spec)), str(REPORT_DIR))
    top = _fixture_top(spec)
    return {
        "_comment": (
            "Generated by layout/verify.py. Paths are relative to this file. "
            "Re-run by hand with: klt lvs layout/reports/"
            f"{stem}.lvs-request.json --format json"
        ),
        "layout": {
            "file": f"{rel_dir}/{stem}.gds",
            "deck": DECK,
            "top": top,
        },
        "reference": {
            "netlist": f"{rel_dir}/{reference}",
            "top": top,
        },
    }


def run_lvs(stem: str, spec: dict, reference: str) -> dict:
    """Run LVS from a scratch copy of the request and return the report."""
    path = WORK_DIR / f"{stem}.lvs-request.json"
    path.write_text(json.dumps(lvs_request(stem, spec, reference), indent=2) + "\n")
    return _run_klt(["lvs", f"layout/.work/{stem}.lvs-request.json"])


# --------------------------------------------------------------------------- #
# Expectation checking
# --------------------------------------------------------------------------- #


def _check(label: str, expected, actual, failures: list[str]) -> bool:
    if expected == actual:
        print(f"    ok   {label}: {actual}")
        return True
    print(f"    FAIL {label}: expected {expected}, got {actual}")
    failures.append(f"{label}: expected {expected}, got {actual}")
    return False


def verify_fixture(stem: str, spec: dict, pdk_variant: str | None) -> tuple[dict, list[str]]:
    """Run every stage declared for one fixture and check its expectations."""
    failures: list[str] = []
    results: dict[str, dict] = {}

    print(f"  {stem} -- {spec['why']}")

    drc_expect = spec["drc"]
    drc = run_drc(stem, spec)
    results["drc"] = drc
    _check(f"{stem} drc.status", drc_expect["status"], drc.get("status"), failures)
    _check(
        f"{stem} drc.rule_counts",
        drc_expect["rule_counts"],
        drc.get("rule_counts"),
        failures,
    )

    extract = run_extract(stem, spec, pdk_variant)
    results["extract"] = extract
    print(
        f"    ok   {stem} extract: {extract.get('device_count')} devices, "
        f"{extract.get('net_count')} nets"
    )

    lvs_expect = spec.get("lvs")
    if lvs_expect:
        lvs = run_lvs(stem, spec, lvs_expect["reference"])
        results["lvs"] = lvs
        _check(f"{stem} lvs.status", lvs_expect["status"], lvs.get("status"), failures)
        _check(
            f"{stem} lvs.category_counts",
            lvs_expect["category_counts"],
            lvs.get("category_counts"),
            failures,
        )
        mismatches = lvs.get("mismatches") or []
        errors = sum(1 for m in mismatches if m.get("severity") == "error")
        _check(f"{stem} lvs.error_count", lvs_expect["error_count"], errors, failures)
        # Printed, not checked: the engine version is machine state, and
        # `_stable` drops it from the report comparison for that reason. It
        # is echoed here so that "did the tool move under me?" is a question
        # a plain run answers, instead of one that costs a --write and a
        # git diff to ask (#73).
        engine = (lvs.get("environment") or {}).get("engine_version")
        print(f"    --   {stem} lvs engine_version: {engine}")

    return results, failures


def _text_artifacts(stem: str, spec: dict) -> list[str]:
    """Scratch files that are committed verbatim alongside the JSON reports.

    The extracted netlist is the actual thing LVS compared, and the request
    is the actual invocation -- both belong in the checked-in evidence, and
    both must be diffed, not just regenerated.
    """
    names = [f"{stem}.extracted.spice"]
    if spec.get("lvs"):
        names.append(f"{stem}.lvs-request.json")
    return names


def _committed_view(stem: str, stage: str, payload: dict) -> dict:
    """The form of one stage's report that belongs in `layout/reports/`.

    Everything the tools emit is recorded verbatim except a single field.
    `klt extract` echoes its `-o` argument back as `netlist_path`, and this
    flow always extracts into the git-ignored scratch dir so that a check run
    can never overwrite a committed artefact. Recorded literally, the
    committed report would name `layout/.work/<stem>.extracted.spice` -- a
    path absent from a fresh checkout -- while the netlist it describes is
    committed beside it in `layout/reports/`. So the committed copy names the
    committed netlist.

    This restatement cannot hide a difference: `netlist_sha256` sits directly
    beside it, is emitted by the tool, and IS compared, and the netlist itself
    is byte-compared by `compare_reports`. Write mode and check mode apply it
    identically, so every other field is still compared exactly.
    """
    if stage != "extract":
        return payload
    restated = dict(payload)
    restated["netlist_path"] = f"layout/reports/{stem}.extracted.spice"
    return restated


def write_reports(stem: str, spec: dict, results: dict) -> list[Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for stage, payload in results.items():
        path = REPORT_DIR / f"{stem}.{stage}.json"
        path.write_text(
            json.dumps(_committed_view(stem, stage, payload), indent=2) + "\n"
        )
        written.append(path)
    for name in _text_artifacts(stem, spec):
        destination = REPORT_DIR / name
        shutil.copyfile(WORK_DIR / name, destination)
        written.append(destination)
    return written


def _stable(payload: dict) -> dict:
    """Strip the fields that legitimately move between machines.

    Exactly three fields are dropped, each because it records *where this
    machine happened to find something*, not *what was verified*. Every
    field beside these three -- including every content hash, every verdict,
    every count, and the PDK's own `variant`/`version` -- stays in the
    comparison, so a real change still trips the gate:

    - `environment.engine_version` (`klt lvs` reports): an engine upgrade
      changes this without changing any verdict. The rest of that block --
      `layout_sha256` / `reference_sha256`, content hashes of the exact
      bytes LVS compared -- is a function of the committed fixtures, not the
      machine, and stays. Dropping the whole block, as this did before #73,
      discarded those two alongside the version for no reason.

    - `pdk.root` (`klt extract` reports, top-level `pdk` block): the
      absolute filesystem path to wherever *this run's* PDK install happens
      to live -- `/Users/<you>/.volare`, `/home/ubuntu/.volare`, CI's
      `~/.ciel`, or an explicit `--pdk-root`. Two machines with the same PDK
      release mounted at different paths must compare equal; `pdk.variant`
      (which PDK) and `pdk.version` (which open_pdks commit) are what was
      actually verified against, and both stay.

    - `provenance.pdk.source` (`klt extract` reports, nested one level under
      `provenance.pdk`): the same idea one level down -- klt's own record of
      *how* it resolved the PDK for this invocation (a search root, an env
      var, an explicit `--pdk-root` flag), which describes the invocation's
      environment, not the PDK. `provenance.pdk.name`/`.version` stay, for
      the same reason `pdk.variant`/`.version` do above.

    Verified empirically (issue #148): running `klt extract` twice over the
    same `.gds`, identical in every argument except `--pdk-root` pointed at
    two different filesystem locations for the same PDK release, produced
    reports differing in exactly these two keys (`pdk.root` and
    `provenance.pdk.source`) -- nothing else moved, including the extracted
    device list and its `netlist_sha256`. `discovered_via` (the equivalent
    field `sim/harness/pdk.py`'s own `Pdk.provenance()` writes into
    `layout/reports/environment.json`) never appears in the *per-fixture*
    reports this function is applied to -- `environment.json` is written by
    `--write` but is not part of `compare_reports`'s diff at all, so nothing
    there needs stripping.

    DRC reports never carry a `pdk`/`provenance.pdk` block (DRC's curated
    deck does not resolve one), so this is a no-op for them. `klt_version`
    and `provenance.klayout_version` are deliberately NOT stripped: per
    `.github/workflows/pdk-nightly.yml`'s own comment, a tool upgrade that
    changes a verdict, a rule id, or the shape of a report is meant to turn
    this gate red so `layout/reports/` gets regenerated -- that is a real
    signal, not machine-local noise, and collapsing it away would be exactly
    the "no-op gate" this fix exists to avoid.
    """
    trimmed = dict(payload)

    environment = trimmed.get("environment")
    if isinstance(environment, dict):
        environment = dict(environment)
        environment.pop("engine_version", None)
        trimmed["environment"] = environment

    pdk = trimmed.get("pdk")
    if isinstance(pdk, dict):
        pdk = dict(pdk)
        pdk.pop("root", None)
        trimmed["pdk"] = pdk

    provenance = trimmed.get("provenance")
    if isinstance(provenance, dict):
        provenance = dict(provenance)
        provenance_pdk = provenance.get("pdk")
        if isinstance(provenance_pdk, dict):
            provenance_pdk = dict(provenance_pdk)
            provenance_pdk.pop("source", None)
            provenance["pdk"] = provenance_pdk
        trimmed["provenance"] = provenance

    return trimmed


_REGENERATE = "-- re-run `python3 layout/verify.py --write`"


def compare_reports(stem: str, spec: dict, results: dict) -> list[str]:
    """Diff live results against the committed reports (stable fields only).

    The JSON reports go through `_stable()` first, for the machine-local
    fields documented there. The text artifacts below it -- the extracted
    `.spice` netlist and the `.lvs-request.json` invocation -- get no such
    treatment, but not because they were overlooked: neither format has
    anywhere to put a machine-local value in the first place.
    `.extracted.spice` is a bare SPICE device/connectivity listing (no
    embedded paths -- verified empirically alongside `_stable()`, #148: the
    same `--pdk-root` A/B run that moved `pdk.root` left the netlist
    byte-identical); `.lvs-request.json` is generated by `lvs_request()`
    above from repo-root-relative paths only. So the byte-for-byte compare
    here is already exactly as strict as `_stable()` makes the JSON compare
    -- both check content, neither checks a filesystem location.
    """
    drift: list[str] = []
    for stage, payload in results.items():
        path = REPORT_DIR / f"{stem}.{stage}.json"
        if not path.exists():
            drift.append(f"{path.relative_to(REPO_ROOT)} is missing {_REGENERATE}")
            continue
        committed = json.loads(path.read_text())
        if _stable(committed) != _stable(_committed_view(stem, stage, payload)):
            drift.append(
                f"{path.relative_to(REPO_ROOT)} does not match this run {_REGENERATE}"
            )
    for name in _text_artifacts(stem, spec):
        path = REPORT_DIR / name
        if not path.exists():
            drift.append(f"{path.relative_to(REPO_ROOT)} is missing {_REGENERATE}")
            continue
        if path.read_bytes() != (WORK_DIR / name).read_bytes():
            drift.append(
                f"{path.relative_to(REPO_ROOT)} does not match this run {_REGENERATE}"
            )
    return drift


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #


def print_table() -> None:
    print("fixture                DRC expectation                 LVS expectation")
    print("-" * 78)
    for stem, spec in EXPECTATIONS.items():
        drc = spec["drc"]
        rules = ", ".join(f"{k}x{v}" for k, v in drc["rule_counts"].items()) or "-"
        lvs = spec.get("lvs")
        lvs_text = (
            f"{lvs['status']}"
            + (
                " (" + ", ".join(f"{k}x{v}" for k, v in lvs["category_counts"].items()) + ")"
                if lvs["category_counts"]
                else ""
            )
            if lvs
            else "not run"
        )
        print(f"{stem:<22} {drc['status']:<10} {rules:<20} {lvs_text}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--write",
        action="store_true",
        help="refresh the committed reports under layout/reports/",
    )
    parser.add_argument(
        "--require-tools",
        action="store_true",
        help="fail instead of skipping when klt or the gf180mcu PDK is absent",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="print the fixture/expectation table and exit",
    )
    args = parser.parse_args(argv)

    if args.list:
        print_table()
        return EXIT_OK

    version = klt_version()
    pdk = resolve_pdk()
    missing = []
    if version is None:
        missing.append("klayout-tools (`klt`) is not on PATH")
    if pdk is None:
        missing.append("no gf180mcu PDK install found (see sim/harness/pdk.py)")
    if missing:
        for line in missing:
            print(f"  - {line}")
        if args.require_tools:
            print("FAIL: --require-tools was given and the flow cannot run")
            return EXIT_FAIL
        print(
            "SKIP: layout verification -- the tools above are not available.\n"
            "      Install them to run the DRC/LVS flow (see layout/README.md)."
        )
        return EXIT_OK

    origin = klt_origin()
    commit = (origin or {}).get("commit")
    print(f"klt:  {version}" + (f" (built from {commit})" if commit else ""))
    print(f"pdk:  {pdk.variant} @ {pdk.version} ({pdk.source})")
    print(f"deck: {DECK}")
    print()

    # `klt extract -o` refuses to create its own output directory, so the
    # scratch directory has to exist before the first invocation.
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    # A stale fixture (or cell) invalidates every report downstream of it,
    # so the geometry staleness guard runs first, over every directory in
    # `_STALENESS_CHECKS`, and hard-fails.
    print("== fixtures ==")
    stale = False
    for label, check_fn in _STALENESS_CHECKS:
        if check_fn() != 0:
            print(f"FAIL: committed .gds under {label} does not match its build.py")
            stale = True
    if stale:
        return EXIT_FAIL
    print()

    print("== flow ==")
    all_failures: list[str] = []
    all_results: dict[str, dict] = {}
    for stem, spec in EXPECTATIONS.items():
        try:
            results, failures = verify_fixture(stem, spec, pdk.variant)
        except FlowError as exc:
            print(f"    FAIL {stem}: {exc}")
            all_failures.append(str(exc))
            continue
        all_results[stem] = results
        all_failures.extend(failures)
    print()

    if args.write:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        (REPORT_DIR / "environment.json").write_text(
            json.dumps(environment_report(), indent=2) + "\n"
        )
        written: list[Path] = []
        for stem, results in all_results.items():
            written.extend(write_reports(stem, EXPECTATIONS[stem], results))
        print(f"== reports ==\n  wrote {len(written) + 1} files under layout/reports/")
    else:
        drift: list[str] = []
        for stem, results in all_results.items():
            drift.extend(compare_reports(stem, EXPECTATIONS[stem], results))
        print("== reports ==")
        if drift:
            for line in drift:
                print(f"  FAIL {line}")
            all_failures.extend(drift)
        else:
            print("  ok   committed reports match this run")
    print()

    if all_failures:
        print(f"FAIL: {len(all_failures)} expectation(s) not met")
        return EXIT_FAIL
    print("PASS: DRC/LVS flow is functional end to end.")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
