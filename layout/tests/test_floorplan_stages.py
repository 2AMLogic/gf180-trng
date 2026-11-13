#!/usr/bin/env python3
"""Unit tests for `layout/floorplan/floorplan.py`'s tool-free build stages.

`build()` runs eight numbered stages. Six of them shell out to `klt` and need
an installed PDK, so until issue #854 split them into functions the only check
on the other two -- stage 1, the per-region cell inventories, and stage 5, the
area rollup -- was the whole-report comparison in the tool-gated nightly job.
This file is the per-push half: stdlib only, no `klt`, no PDK, no network.

Two kinds of check, deliberately:

* **Synthetic**, pinning the arithmetic's *rules* on inputs small enough to
  verify by hand -- that a channel is charged against the taller of the two
  regions it separates, that a subtotal charges only the channels lying wholly
  between regions it picked, that the DR-0016 liveness monitor is priced and
  excluded rather than silently dropped.
* **Differential against committed evidence**, re-deriving stage 1 and stage 5
  from the committed `reports/area.json`'s own regions and asserting they
  reproduce that same report's `rollup` field for field. This is the check that
  would catch an arithmetic change that is self-consistent but wrong, which no
  synthetic fixture can.

The differential tests read the committed report; they never write one.

Stage-1 helpers one level down (`read_subckts`, `instance_counts`,
`starve_geometry` and friends) are tested in `test_floorplan_expansion.py`;
this file tests the stage functions built on top of them.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "design"))

from layout.floorplan import floorplan  # noqa: E402

AREA_REPORT = REPO_ROOT / "layout" / "floorplan" / "reports" / "area.json"
RO_ARRAY_CORE = REPO_ROOT / "design" / "ro_array_core.spice"
SAMPLER_CORE = REPO_ROOT / "design" / "sampler_core.spice"

_KEEPALIVE: list[tempfile.TemporaryDirectory] = []


def tearDownModule() -> None:
    for tmp in _KEEPALIVE:
        tmp.cleanup()
    _KEEPALIVE.clear()


def _write(text: str) -> Path:
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name) / "fixture.spice"
    path.write_text(text)
    _KEEPALIVE.append(tmp)
    return path


def _committed() -> dict:
    return json.loads(AREA_REPORT.read_text())


def _region(
    rid: str,
    role: str,
    guarded_h_um: float,
    guarded_area_um2: float,
    cell_area_um2: float = 0.0,
) -> dict:
    """A region dict carrying only the fields stage 5 actually reads."""
    return {
        "id": rid,
        "role": role,
        "guarded_h_um": guarded_h_um,
        "guarded_area_um2": guarded_area_um2,
        "cell_area_um2": cell_area_um2,
        "placed_area_um2": {"60pct": 0.0, "80pct": 0.0},
    }


# --------------------------------------------------------------------------- #
# Stage 1 -- inventories
# --------------------------------------------------------------------------- #

#: Two rings and a sampler, shaped like the real export but small enough to
#: count by eye: one stoppable `ro_nand2` and two `ro_stage` per ring, one
#: output buffer per ring, one combiner, two sampler flops.
SYNTHETIC_CORE = """\
.subckt ro_ring a y wstv=1u lstv=2u
xn a n1 ro_nand2
x1 n1 n2 ro_stage
x2 n2 y ro_stage
.ends

.subckt ro_array_core y1 y2 q
xr1 e1 y1 ro_ring wstv=0.22u lstv=2u
xr2 e2 y2 ro_ring wstv=0.44u lstv=2u
xb1 y1 b1 ro_buf
xb2 y2 b2 ro_buf
xa1 b1 b2 q xor2
.ends
"""

SYNTHETIC_SAMPLER = """\
.subckt sampler_core d q
xd0 d q sampler_dff
xd1 d q sampler_dff
.ends
"""


class RegionInventoriesTest(unittest.TestCase):
    """Stage 1: `region_inventories`."""

    def setUp(self) -> None:
        self.core = floorplan.read_subckts(_write(SYNTHETIC_CORE))
        self.sampler = floorplan.read_subckts(_write(SYNTHETIC_SAMPLER))

    def test_rings_are_counted_per_instance(self) -> None:
        got = floorplan.region_inventories(self.core, self.sampler)
        self.assertEqual(got["ring1"], Counter({"ro_stage": 2, "ro_nand2": 1}))
        self.assertEqual(got["ring2"], Counter({"ro_stage": 2, "ro_nand2": 1}))

    def test_combiner_sampler_collects_buffers_and_flops(self) -> None:
        # The buffers are `vdd`-supplied per DR-0018, so they belong to this
        # region and not to the ring that feeds them (issue #144).
        got = floorplan.region_inventories(self.core, self.sampler)
        self.assertEqual(
            got["combiner_sampler"],
            Counter({"ro_buf": 2, "sampler_dff": 2, "xor2": 1}),
        )

    def test_buffers_are_found_by_cell_name_not_instance_name(self) -> None:
        # The claim the implementation comment makes: a third buffer appearing
        # in a future export is counted without an edit to floorplan.py.
        core = floorplan.read_subckts(
            _write(SYNTHETIC_CORE.replace("xa1 b1 b2 q xor2", "xb3 y1 b3 ro_buf\nxa1 b1 b2 q xor2"))
        )
        got = floorplan.region_inventories(core, self.sampler)
        self.assertEqual(got["combiner_sampler"]["ro_buf"], 3)

    def test_no_region_is_silently_dropped(self) -> None:
        got = floorplan.region_inventories(self.core, self.sampler)
        self.assertEqual(set(got), {"ring1", "ring2", "combiner_sampler"})

    def test_matches_the_committed_report(self) -> None:
        # Differential: the real netlists must still produce the per-region
        # cell counts the committed report was written from.
        core = floorplan.read_subckts(RO_ARRAY_CORE)
        sampler = floorplan.read_subckts(SAMPLER_CORE)
        got = floorplan.region_inventories(core, sampler)
        committed = {r["id"]: r for r in _committed()["regions"]}
        for rid, inventory in got.items():
            with self.subTest(region=rid):
                self.assertEqual(sum(inventory.values()), committed[rid]["cell_count"])
                self.assertEqual(
                    " + ".join(f"{c}x {n}" for n, c in sorted(inventory.items())),
                    committed[rid]["contents"],
                )


class StarveGeometriesTest(unittest.TestCase):
    """Stage 1: `starve_geometries`."""

    def test_reads_each_ring_instance_separately(self) -> None:
        core = floorplan.read_subckts(_write(SYNTHETIC_CORE))
        got = floorplan.starve_geometries(core)
        self.assertEqual(set(got), {"ring1", "ring2"})
        self.assertEqual(got["ring1"], {"w_um": 0.22, "l_um": 2.0})
        # Not assumed equal to ring1's -- each is read from its own instance.
        self.assertEqual(got["ring2"], {"w_um": 0.44, "l_um": 2.0})

    def test_real_netlist_resolves_both_rings(self) -> None:
        got = floorplan.starve_geometries(floorplan.read_subckts(RO_ARRAY_CORE))
        for rid in ("ring1", "ring2"):
            with self.subTest(region=rid):
                self.assertGreater(got[rid]["w_um"], 0.0)
                self.assertGreater(got[rid]["l_um"], 0.0)


class StarveAreaTest(unittest.TestCase):
    """The former `build()` closure, now a module-level function."""

    STARVE = {"ring1": {"w_um": 0.22, "l_um": 2.0}}
    FOOTPRINTS = {
        "nfet_w0.220_l2.000": {"footprint_um2": 1.25},
        "pfet_w0.220_l2.000": {"footprint_um2": 2.5},
    }

    def test_looks_up_by_flavour_and_drawn_geometry(self) -> None:
        self.assertEqual(
            floorplan.starve_area(self.STARVE, self.FOOTPRINTS, "ring1", "nfet"), 1.25
        )
        self.assertEqual(
            floorplan.starve_area(self.STARVE, self.FOOTPRINTS, "ring1", "pfet"), 2.5
        )

    def test_key_is_the_drawn_width_not_the_generated_one(self) -> None:
        # `measure_starve_devices` keys on the drawn W even when it generates
        # at GEN_MIN_W_UM, so a sub-minimum ring must still resolve.
        starve = {"ring1": {"w_um": 0.001, "l_um": 2.0}}
        footprints = {"nfet_w0.001_l2.000": {"footprint_um2": 9.0}}
        self.assertEqual(
            floorplan.starve_area(starve, footprints, "ring1", "nfet"), 9.0
        )

    def test_unmeasured_device_raises_rather_than_pricing_at_zero(self) -> None:
        with self.assertRaises(KeyError):
            floorplan.starve_area(self.STARVE, {}, "ring1", "nfet")


# --------------------------------------------------------------------------- #
# Stage 5 -- channels, subtotals, rollup
# --------------------------------------------------------------------------- #


class IsolationChannelsTest(unittest.TestCase):
    """Stage 5: `isolation_channels`."""

    def test_one_channel_between_each_neighbouring_pair(self) -> None:
        regions = [
            _region("a", "entropy", 10.0, 100.0),
            _region("b", "entropy", 20.0, 200.0),
            _region("c", "deterministic", 30.0, 300.0),
        ]
        channels = floorplan.isolation_channels(regions)
        self.assertEqual(
            [c["between"] for c in channels], [["a", "b"], ["b", "c"]]
        )

    def test_charged_against_the_taller_of_the_pair(self) -> None:
        # The rule the stage's own docstring argues for: charging the full row
        # height instead would bill a 7 um ring for the digital block's 398 um.
        regions = [
            _region("short", "entropy", 7.0, 100.0),
            _region("tall", "deterministic", 400.0, 200.0),
        ]
        (channel,) = floorplan.isolation_channels(regions)
        self.assertEqual(channel["span_um"], 400.0)
        self.assertEqual(channel["width_um"], floorplan.ISOLATION_CHANNEL_UM)
        self.assertEqual(
            channel["area_um2"], round(floorplan.ISOLATION_CHANNEL_UM * 400.0, 2)
        )

    def test_single_region_has_no_channel(self) -> None:
        self.assertEqual(
            floorplan.isolation_channels([_region("only", "entropy", 1.0, 1.0)]), []
        )

    def test_matches_the_committed_report(self) -> None:
        committed = _committed()
        self.assertEqual(
            floorplan.isolation_channels(committed["regions"]),
            committed["rollup"]["channels"],
        )


class SubtotalTest(unittest.TestCase):
    """Stage 5: `_subtotal`."""

    REGIONS = [
        _region("a", "entropy", 10.0, 100.0, cell_area_um2=10.0),
        _region("b", "boundary", 10.0, 200.0, cell_area_um2=20.0),
        _region("c", "deterministic", 10.0, 400.0, cell_area_um2=40.0),
    ]

    def setUp(self) -> None:
        self.channels = floorplan.isolation_channels(self.REGIONS)

    def test_charges_only_channels_lying_wholly_inside_the_selection(self) -> None:
        # a|b is inside the analog selection; b|c straddles it and must not be
        # charged to either side.
        analog = floorplan._subtotal(
            self.REGIONS, self.channels, lambda r: r["role"] in ("entropy", "boundary")
        )
        self.assertEqual(analog["regions"], ["a", "b"])
        self.assertEqual(analog["guarded_area_um2"], 300.0)
        self.assertEqual(analog["isolation_channel_area_um2"], self.channels[0]["area_um2"])
        self.assertEqual(
            analog["area_um2"], round(300.0 + self.channels[0]["area_um2"], 2)
        )

    def test_a_lone_region_is_charged_no_channel(self) -> None:
        digital = floorplan._subtotal(
            self.REGIONS, self.channels, lambda r: r["role"] == "deterministic"
        )
        self.assertEqual(digital["regions"], ["c"])
        self.assertEqual(digital["isolation_channel_area_um2"], 0)
        self.assertEqual(digital["area_um2"], 400.0)

    def test_share_of_budget_is_against_the_readme_area_row(self) -> None:
        digital = floorplan._subtotal(
            self.REGIONS, self.channels, lambda r: r["role"] == "deterministic"
        )
        self.assertAlmostEqual(
            digital["share_of_budget_pct"],
            round(100.0 * 400.0 / floorplan.AREA_BUDGET_UM2, 2),
        )

    def test_matching_nothing_yields_empty_rather_than_raising(self) -> None:
        none = floorplan._subtotal(self.REGIONS, self.channels, lambda r: False)
        self.assertEqual(none["regions"], [])
        self.assertEqual(none["area_um2"], 0)


class BuildRollupTest(unittest.TestCase):
    """Stage 5: `build_rollup`."""

    ROW_BBOX = {"x0": 0.0, "y0": 0.0, "x1": 50.0, "y1": 25.0}

    def _rollup(self, regions, digital_blocks=(), stdcells=None):
        channels = floorplan.isolation_channels(regions)
        return floorplan.build_rollup(
            regions, channels, self.ROW_BBOX, list(digital_blocks), stdcells or {}
        )

    def test_totals_are_the_sum_of_the_parts(self) -> None:
        regions = [
            _region("a", "entropy", 10.0, 100.0, cell_area_um2=10.0),
            _region("b", "deterministic", 20.0, 200.0, cell_area_um2=20.0),
        ]
        rollup = self._rollup(regions)
        channel_area = rollup["channels"][0]["area_um2"]
        self.assertEqual(rollup["cell_area_um2"], 30.0)
        self.assertEqual(rollup["guarded_region_area_um2"], 300.0)
        self.assertEqual(rollup["isolation_channel_area_um2"], channel_area)
        self.assertEqual(rollup["floorplan_area_um2"], round(300.0 + channel_area, 2))
        self.assertEqual(rollup["budget_um2"], floorplan.AREA_BUDGET_UM2)

    def test_row_bbox_is_reported_as_width_and_height(self) -> None:
        rollup = self._rollup([_region("a", "entropy", 10.0, 100.0)])
        self.assertEqual(rollup["row_bbox_um"], {"w": 50.0, "h": 25.0})

    def test_liveness_monitor_is_priced_and_excluded_not_dropped(self) -> None:
        # DR-0016: shipped RTL (#71) but flagged shipped=False in
        # digital_power_estimate.BLOCKS, so it must appear under `excluded`
        # with its own area and stay out of every total above.
        stdcells = {f"{floorplan.area_estimate.STDCELL_LIB}__inv_1": 4.0}
        blocks = [
            ("core", Counter({"inv_1": 10}), True),
            ("ring_liveness", Counter({"inv_1": 3}), False),
        ]
        rollup = self._rollup(
            [_region("digital", "deterministic", 10.0, 100.0, cell_area_um2=40.0)],
            digital_blocks=blocks,
            stdcells=stdcells,
        )
        excluded = rollup["excluded"]["ring_liveness_monitor_DR0016"]
        self.assertEqual(excluded["cells"], 3)
        self.assertEqual(excluded["cell_area_um2"], 12.0)
        # ... and the shipped block's area is not double-counted into it.
        self.assertEqual(rollup["cell_area_um2"], 40.0)

    def test_no_unshipped_block_prices_at_zero(self) -> None:
        blocks = [("core", Counter({"inv_1": 10}), True)]
        rollup = self._rollup(
            [_region("digital", "deterministic", 10.0, 100.0)],
            digital_blocks=blocks,
            stdcells={f"{floorplan.area_estimate.STDCELL_LIB}__inv_1": 4.0},
        )
        excluded = rollup["excluded"]["ring_liveness_monitor_DR0016"]
        self.assertEqual(excluded["cells"], 0)
        self.assertEqual(excluded["cell_area_um2"], 0)

    def test_matches_the_committed_report(self) -> None:
        # The differential that makes the rest of this file worth having: the
        # committed report's own regions, pushed back through stage 5, must
        # reproduce its own rollup field for field. `excluded` is left out
        # because it is the one part of the rollup that needs the PDK's LEF
        # areas; it has its own synthetic tests above.
        committed = _committed()
        rollup = floorplan.build_rollup(
            committed["regions"],
            floorplan.isolation_channels(committed["regions"]),
            {
                "x0": 0.0,
                "y0": 0.0,
                "x1": committed["rollup"]["row_bbox_um"]["w"],
                "y1": committed["rollup"]["row_bbox_um"]["h"],
            },
            [],
            {},
        )
        expected = {k: v for k, v in committed["rollup"].items() if k != "excluded"}
        self.assertEqual({k: v for k, v in rollup.items() if k != "excluded"}, expected)


if __name__ == "__main__":
    unittest.main()
