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
from layout._klt import (  # noqa: E402
    FlowError,
    _run_klt,
    klt_origin,
    klt_version,
    resolve_pdk,
)


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
#   device.body_unverified x2   one entry per MOS device class, each
#                               counting that class's devices whose body
#                               terminal reached no real net:
#                               - nfet: compared against `vsubs`, a net the
#                                 deck synthesized, because no fixture here
#                                 draws a substrate tap;
#                               - pfet: compared against an anonymous,
#                                 KLayout-synthesized well net, because no
#                                 fixture here draws a well tap either.
#                               This is the deck limitation layout/README.md
#                               documents in prose under "Bulk terminals are
#                               approximated"; klayout-tools #281 made the
#                               tool state it per run. History of the count,
#                               none of which changed what is verified:
#                               x2 before #170; x1 from #170's re-pin
#                               (klayout-tools#1113: the PMOS arm became
#                               deck-structural, silent whenever the deck
#                               merely *declared* a well-tap mechanism);
#                               x2 again from #281's re-pin to the 0.6.0
#                               release (klayout-tools#2048: the PMOS arm is
#                               per-device again, so a PMOS whose body landed
#                               on an anonymous net is disclosed). The NMOS
#                               entry's per-fixture device count did not move
#                               across that re-pin on any fixture; the PMOS
#                               entry's equals it on every fixture (each is
#                               complementary CMOS), and nfet + pfet equals
#                               the extracted device count -- i.e. no MOS
#                               body in any fixture here is verified, which
#                               is what the README already said. Each
#                               fixture's `body_unverified` key below pins
#                               the per-class counts from the report's own
#                               `body_verification.findings`, so the next
#                               time this disclosure moves it fails by class
#                               and by count, not just as "2 != 1".
#   topology x1                 a device class the deck declares (bjt,
#                               cap_mim, resistor -- klayout-tools #219/#227)
#                               has no counterpart on the reference side, and
#                               zero devices of it were extracted. The tool
#                               says so itself: "not a real topology
#                               mismatch".
#
# Both first appeared on 2026-08-02 without any version string moving -- see
# layout/README.md, "Pinning the tool", for why `klt --version` could not
# have told us and what identifies a klt build instead. They are recorded
# rather than filtered out because the point of this table is that a report
# says the same thing tomorrow as today; and `error_count` is checked
# alongside them so that absorbing two warnings did not quietly buy a pass
# for a future *error* landing in the same category.
#
# Two more keys on every `lvs` entry, both read from report blocks klt 0.6.0
# added (klayout-tools#1983 / #2048) and both checked for exact equality:
#
#   body_unverified       {device class: count} from
#                         `body_verification.findings`, alongside
#                         `body_verification.status` == "unverified". The
#                         machine-checkable form of the warning above.
#   power_connectivity    `power_connectivity.status`. "unchecked" on every
#                         fixture: the tool's own reason is that a
#                         `plain-element` reference "carries its own
#                         power/ground pins and nets -- they take part in the
#                         ordinary compare, so this check (which exists to
#                         cover the signal-only 'gate-level-verilog' form)
#                         does not apply". Pinned so the day it changes is
#                         visible; "unchecked" is not "match", and nothing
#                         here should be read as a power-delivery verdict.
EXPECTATIONS: dict[str, dict] = {
    "trng_tc_inv": {
        "why": "known-good: the flow must pass a correct cell",
        "drc": {"status": "clean", "rule_counts": {}},
        "lvs": {
            "reference": "trng_tc_inv.spice",
            "status": "match",
            # One inverter: 1 NMOS + 1 PMOS, neither body tied to a drawn
            # tap, so one disclosure per class (see the comment above).
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "body_unverified": {"nfet": 1, "pfet": 1},
            "power_connectivity": "unchecked",
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
            # because they describe the deck, not the defect. The cut strap
            # does not touch either body, so the per-class body counts are
            # the known-good cell's: 1 NMOS + 1 PMOS. The two errors -- the
            # defect -- are unchanged by the 0.6.0 re-pin.
            "category_counts": {
                "net.unmatched": 1,
                "device.unmatched": 1,
                "device.body_unverified": 2,
                "topology": 1,
            },
            "body_unverified": {"nfet": 1, "pfet": 1},
            "power_connectivity": "unchecked",
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
            # Starved inverter: 2 NMOS + 2 PMOS, no drawn taps, so all four
            # bodies are disclosed (2 per class).
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "body_unverified": {"nfet": 2, "pfet": 2},
            "power_connectivity": "unchecked",
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
            # Same topology as ro_stage at a different starve width: 2 NMOS
            # + 2 PMOS, all four bodies untapped.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "body_unverified": {"nfet": 2, "pfet": 2},
            "power_connectivity": "unchecked",
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
            # Starved NAND2: 3 NMOS + 3 PMOS as extracted, all untapped.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "body_unverified": {"nfet": 3, "pfet": 3},
            "power_connectivity": "unchecked",
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
            # Same topology as ro_nand2 at ring2's starve width: 3 NMOS + 3
            # PMOS, all untapped.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "body_unverified": {"nfet": 3, "pfet": 3},
            "power_connectivity": "unchecked",
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
            # One inverter stage: 1 NMOS + 1 PMOS, both untapped.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "body_unverified": {"nfet": 1, "pfet": 1},
            "power_connectivity": "unchecked",
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
            # declared. 6 NMOS + 6 PMOS, all untapped.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "body_unverified": {"nfet": 6, "pfet": 6},
            "power_connectivity": "unchecked",
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
            # declared. 11 NMOS + 11 PMOS (transmission gates count one of
            # each), all untapped.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "body_unverified": {"nfet": 11, "pfet": 11},
            "power_connectivity": "unchecked",
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
            # 10 x ro_stage (2+2) + 1 x ro_nand2 (3+3) = 23 NMOS + 23 PMOS:
            # exactly the leaf cells' counts summed -- the assembly adds no
            # tap, so it resolves no body the leaves left unresolved.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "body_unverified": {"nfet": 23, "pfet": 23},
            "power_connectivity": "unchecked",
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
            # 10 x ro_stage_ring2 (2+2) + 1 x ro_nand2_ring2 (3+3) = 23
            # NMOS + 23 PMOS, the leaf counts summed, as for ro_ring11.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "body_unverified": {"nfet": 23, "pfet": 23},
            "power_connectivity": "unchecked",
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
            # declared. 2 x ro_buf (1+1) + 1 x xor2 (6+6) + 4 x sampler_dff
            # (11+11) = 52 NMOS + 52 PMOS, the leaf counts summed. This is
            # the envelope signoff/block-manifest.json cites for T1 item 4
            # (analog), so its `body_verification` and `power_connectivity`
            # verdicts are quoted in signoff/README.md.
            "category_counts": {"device.body_unverified": 2, "topology": 1},
            "body_unverified": {"nfet": 52, "pfet": 52},
            "power_connectivity": "unchecked",
            "error_count": 0,
        },
    },
}


# --------------------------------------------------------------------------- #
# Environment
# --------------------------------------------------------------------------- #


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
        # The machine-checkable form of the `device.body_unverified`
        # warnings, per device class (see the comment above `EXPECTATIONS`).
        # A report with no `body_verification` block (klt < 0.6.0) reads as
        # `None` here and fails against any pinned expectation, rather than
        # passing vacuously.
        body = lvs.get("body_verification")
        if isinstance(body, dict):
            body_counts = {
                f.get("class"): f.get("device_count")
                for f in body.get("findings") or []
                if isinstance(f, dict)
            }
            body_status = body.get("status")
        else:
            body_counts, body_status = None, None
        expected_body = lvs_expect["body_unverified"]
        _check(
            f"{stem} lvs.body_verification.status",
            "unverified" if expected_body else "verified",
            body_status,
            failures,
        )
        _check(
            f"{stem} lvs.body_verification.findings",
            expected_body,
            body_counts,
            failures,
        )
        power = lvs.get("power_connectivity")
        _check(
            f"{stem} lvs.power_connectivity.status",
            lvs_expect["power_connectivity"],
            power.get("status") if isinstance(power, dict) else None,
            failures,
        )
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

    Four fields are dropped, each because it records *where this machine
    happened to find something* or *how this run happened to number
    something*, not *what was verified*. Every field beside these four --
    including every content hash, every verdict, every count, and the PDK's
    own `variant`/`version` -- stays in the comparison, so a real change
    still trips the gate:

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

    - `nets[].net_id` (`klt extract` reports), but *only* for a `nets[]`
      entry whose `name` is not shared with any other entry in the same
      report. `net_id` is klt's own per-net cluster id, added by
      klayout-tools#1543 specifically to disambiguate multiple `nets[]`
      entries that collide on the same `name` -- `ro_ring11`'s own ten
      genuinely distinct internal `a|y` chain nodes, all sharing that one
      literal string, are exactly the case it exists for (see
      `layout/pex/build.py`'s "Why leaf cells" section). Where a net's
      `name` is unique in the report, `name` alone already identifies it
      completely and `net_id` adds no distinguishing information -- so a
      swap between two uniquely-named nets' `net_id` values changes nothing
      any consumer reads by identity. Confirmed empirically (issue #294):
      pinning klt/PDK bit-for-bit identical (`klayout-tools@3fbb4478`,
      `klayout==0.30.12` (klt-pin: historical), gf180mcu `f6eeac7d`) and
      running `klt extract` on the committed `ro_ring11.gds` under both
      this repository's macOS arm64 development host and a Linux x86_64
      container matching
      `pdk-nightly.yml`'s runner produced reports differing in exactly two
      fields -- the uniquely-named `en` and `vss` nets' `net_id` values
      (`1`/`2`, swapped) -- with every other field, including
      `netlist_sha256`, `device_count`/`net_count`, every device's own
      `nets{}` mapping, and both `a|y`-collision-group nets' own `net_id`
      values, byte-identical across repeated runs on each host (three
      independent runs on the macOS host, three more on the Linux
      container, each run its own process). The sibling `ro_ring11_ring2`
      fixture (same wiring geometry, same
      `build.py` technique, only its leaf cells' device widths differ --
      see that module's own docstring) showed zero difference across the
      same two hosts, which is why only `ro_ring11` ever tripped this gate:
      the tie this net-numbering pass has to break only exists for ring1's
      own sizing. `net_id` for a *collided*-name net is deliberately NOT
      stripped -- a regression that scrambled `net_id` there would silently
      break the one thing `layout/pex/build.py`'s routing-level composition
      path actually depends on it for, and this gate must still catch that.

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

    nets = trimmed.get("nets")
    if isinstance(nets, list):
        name_counts: dict = {}
        for net in nets:
            if isinstance(net, dict):
                name_counts[net.get("name")] = name_counts.get(net.get("name"), 0) + 1
        stripped_nets = []
        for net in nets:
            if isinstance(net, dict) and name_counts.get(net.get("name")) == 1:
                net = dict(net)
                net.pop("net_id", None)
            stripped_nets.append(net)
        trimmed["nets"] = stripped_nets

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
