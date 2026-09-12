#!/usr/bin/env python3
"""Unit tests for `layout/pex/build.py`'s full-chip (inter-region) delta
composition (issue #232, DR-0025).

DR-0025 authorises pricing the `ro1`/`ro2` inter-region trunks as a DELTA
over what `layout/pex/ro_ring11(_ring2).routed.extracted.spice` and
`layout/pex/combiner_sampler.routed.extracted.spice` already carry for that
same physical net -- summing the full-chip extraction's own merged value on
top of those would double-count. `_reconcile_delta` is the one function that
arithmetic runs through, and it must raise (compose nothing) rather than
silently return a number that does not close.

These tests hold that claim two ways:

1. **The arithmetic itself** (`_reconcile_delta`), directly, with synthetic
   inputs -- including a deliberately mismatched one that must raise. This
   needs no `klt` and no PDK.
2. **The committed report and netlist**, if `--fullchip-extract` has been
   run at least once (`layout/pex/reports/fullchip_parasitics.json` and
   `layout/pex/sampler_core.fullchip.extracted.spice` both exist): the
   report's own recorded `fullchip`/`ring_intra_region`/
   `combiner_sampler_intra_region`/`delta` figures must reconcile with each
   other, and the composed netlist's inserted `R`/`C` values must equal the
   report's own `delta` figures -- so the JSON report and the SPICE artefact
   it fed can never silently drift apart. Skipped (not failed) if that
   report does not exist yet, the same convention
   `layout/tests/test_verify.py` uses for a machine-local PDK absence --
   see `layout/pex/build.py`'s own docstring for why the full-chip
   extraction is never run unconditionally.
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

LAYOUT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAYOUT_DIR.parent
PEX_DIR = LAYOUT_DIR / "pex"
FULLCHIP_REPORT = PEX_DIR / "reports" / "fullchip_parasitics.json"
FULLCHIP_NETLIST = PEX_DIR / "sampler_core.fullchip.extracted.spice"

sys.path.insert(0, str(REPO_ROOT))

from layout.pex.build import (  # noqa: E402
    FlowError,
    _coupling_total_ff,
    _fullchip_cache_key,
    _net_labels,
    _parasitics_entry_by_label,
    _reconcile_cached_report,
    _reconcile_delta,
)


class NetLabelResolutionTests(unittest.TestCase):
    """`_parasitics_entry_by_label` in isolation.

    Flat extraction of the composed stream joins every drawn label on a net
    into one name, so the inter-region net `design/floorplan_netlist.py`
    calls `ro1` arrives as `a|ro1|y`. Resolving it by exact name silently
    finds nothing; resolving it by substring would match `ro10` or
    `foo_ro1`. These tests hold the middle ground -- label-component
    matching -- and, more importantly, hold the failure modes to a raise
    rather than a guess.
    """

    @staticmethod
    def _payload(*names):
        return {
            "parasitics": {
                "nets": [
                    {"net": n, "net_id": i, "resistance_ohm": 1.0, "capacitance_ff": 1.0}
                    for i, n in enumerate(names)
                ]
            }
        }

    def test_splits_on_both_label_separators(self):
        self.assertEqual(_net_labels("a|ro1|y"), {"a", "ro1", "y"})
        self.assertEqual(_net_labels("q,raw_bit"), {"q", "raw_bit"})
        self.assertEqual(_net_labels("clk"), {"clk"})

    def test_resolves_a_label_inside_a_joined_name(self):
        entry = _parasitics_entry_by_label(self._payload("a|ro1|y", "a|ro2|y", "clk"), "ro1")
        self.assertEqual(entry["net"], "a|ro1|y")

    def test_a_label_that_is_only_a_substring_does_not_match(self):
        """`ro1` must not resolve against `ro10`, and must not resolve
        against a net merely because some other label contains it."""
        with self.assertRaises(FlowError):
            _parasitics_entry_by_label(self._payload("a|ro10|y", "ro1x"), "ro1")

    def test_an_ambiguous_label_raises_rather_than_picking_one(self):
        with self.assertRaises(FlowError):
            _parasitics_entry_by_label(self._payload("a|ro1|y", "ro1|z"), "ro1")

    def test_an_extraction_without_parasitics_raises(self):
        with self.assertRaises(FlowError):
            _parasitics_entry_by_label({"parasitics": None}, "ro1")


class CouplingTotalTests(unittest.TestCase):
    """Coupling capacitance is reported beside the delta, never folded into
    it -- see `layout/pex/build.py`'s docstring. A net with no `coupled[]`
    entry at all must read 0.0, not raise."""

    def test_sums_every_coupled_pair(self):
        entry = {"coupled": [{"capacitance_ff": 0.04}, {"capacitance_ff": 0.0373}]}
        self.assertAlmostEqual(_coupling_total_ff(entry), 0.0773)

    def test_no_coupling_reads_zero(self):
        self.assertEqual(_coupling_total_ff({}), 0.0)
        self.assertEqual(_coupling_total_ff({"coupled": []}), 0.0)


class FullchipCacheKeyTests(unittest.TestCase):
    """The iteration cache is keyed on the invocation, minus `-o`.

    A flag, a pin or an input path that changes what the extractor computes
    MUST miss the cache -- composing tens-of-minutes-old numbers from a
    different run is exactly the failure this cache could cause. The output
    path is the one argument that changes nothing about the result, and
    keying on it would cost a full re-extraction for a scratch-directory
    move."""

    def test_output_path_is_not_part_of_the_key(self):
        a = ["extract", "x.gds", "--parasitics", "-o", "one/place.spice"]
        b = ["extract", "x.gds", "--parasitics", "-o", "another/place.spice"]
        self.assertEqual(_fullchip_cache_key(a), _fullchip_cache_key(b))
        self.assertEqual(_fullchip_cache_key(a), ["extract", "x.gds", "--parasitics"])

    def test_the_long_output_flag_is_dropped_too(self):
        self.assertEqual(
            _fullchip_cache_key(["extract", "--output", "p.spice", "--parasitics"]),
            ["extract", "--parasitics"],
        )

    def test_any_other_argument_change_changes_the_key(self):
        base = ["extract", "x.gds", "--parasitics", "--pins", "a,b"]
        self.assertNotEqual(
            _fullchip_cache_key(base),
            _fullchip_cache_key(["extract", "x.gds", "--parasitics", "--pins", "a,b,c"]),
        )
        self.assertNotEqual(
            _fullchip_cache_key(base),
            _fullchip_cache_key(["extract", "y.gds", "--parasitics", "--pins", "a,b"]),
        )


class ReconcileDeltaArithmeticTests(unittest.TestCase):
    """`_reconcile_delta` in isolation -- no `klt`, no PDK, no committed
    artefact required."""

    def test_delta_is_fullchip_less_every_part(self):
        fullchip = {"resistance_ohm": 39.0, "capacitance_ff": 7.5}
        parts = [
            {"resistance_ohm": 10.0, "capacitance_ff": 2.0},
            {"resistance_ohm": 5.0, "capacitance_ff": 0.5},
        ]
        delta = _reconcile_delta("ro1", fullchip, parts)
        self.assertAlmostEqual(delta["resistance_ohm"], 39.0 - 15.0)
        self.assertAlmostEqual(delta["capacitance_ff"], 7.5 - 2.5)

    def test_single_part_subtracts_cleanly(self):
        fullchip = {"resistance_ohm": 20.0, "capacitance_ff": 3.0}
        parts = [{"resistance_ohm": 1.0, "capacitance_ff": 0.4}]
        delta = _reconcile_delta("raw_bit", fullchip, parts)
        self.assertAlmostEqual(delta["resistance_ohm"], 19.0)
        self.assertAlmostEqual(delta["capacitance_ff"], 2.6)

    def test_a_negative_residual_within_float_tolerance_is_clamped_to_zero(self):
        # klt's own JSON rounds resistance_ohm to 4 decimals and
        # capacitance_ff to 6 -- a part sum that lands a hair above the
        # merged total by pure rounding must not raise, and must not write
        # a negative R/C card.
        fullchip = {"resistance_ohm": 10.0, "capacitance_ff": 1.0}
        parts = [{"resistance_ohm": 10.0000005, "capacitance_ff": 1.00000005}]
        delta = _reconcile_delta("ro2", fullchip, parts)
        self.assertEqual(delta["resistance_ohm"], 0.0)
        self.assertEqual(delta["capacitance_ff"], 0.0)

    def test_arithmetic_that_does_not_close_raises_flowerror(self):
        """The load-bearing negative case: a merged net materially SMALLER
        than the sum of its own already-extracted intra-region parts can
        only be a labelling/positional-identification bug (parasitics are
        only ever added by more wire, never removed) -- this must raise,
        never silently compose a wrong number."""
        fullchip = {"resistance_ohm": 5.0, "capacitance_ff": 7.5}
        parts = [
            {"resistance_ohm": 10.0, "capacitance_ff": 2.0},
            {"resistance_ohm": 5.0, "capacitance_ff": 0.5},
        ]
        with self.assertRaises(FlowError):
            _reconcile_delta("ro1", fullchip, parts)

    def test_capacitance_alone_failing_to_close_also_raises(self):
        fullchip = {"resistance_ohm": 39.0, "capacitance_ff": 1.0}
        parts = [{"resistance_ohm": 10.0, "capacitance_ff": 2.0}]
        with self.assertRaises(FlowError):
            _reconcile_delta("ro1", fullchip, parts)


def _fake_block(pin: str, resistance_ohm: float, capacitance_ff: float) -> tuple[dict, dict]:
    """A minimal stand-in for one `klt extract` response plus its resolved
    `{pin_index: port name}` map: one promoted port, one parasitics entry."""
    payload = {
        "pin_count": 1,
        "nets": [{"name": pin, "net_id": 7, "pin_index": 0}],
        "parasitics": {
            "nets": [
                {
                    "net": pin,
                    "net_id": 7,
                    "resistance_ohm": resistance_ohm,
                    "capacitance_ff": capacitance_ff,
                }
            ]
        },
    }
    return payload, {0: pin}


class CachedReportStalenessGuardTests(unittest.TestCase):
    """`_reconcile_cached_report` is what lets every ordinary
    `layout/pex/build.py` / `--check` run be cheap AND honest: it composes
    from the committed report rather than re-running a tens-of-minutes
    extraction, so something has to notice when that committed report stops
    describing the geometry on disk. It re-reads the cheap intra-region
    extractions (which `build()` runs anyway, for the routing-level path)
    and holds the report's own recorded intra-region R/C to them.

    These tests are the reason the composed netlist can be trusted without
    re-extracting: the guard fires on drift instead of composing from a
    stale number.
    """

    def _fixture(self, ring_r=105.8341, ring_c=7.889961, cs_r=88.1193, cs_c=0.585014):
        ring1, ring1_ports = _fake_block("ro", ring_r, ring_c)
        ring2, ring2_ports = _fake_block("ro", ring_r, ring_c)
        cs, cs_ports = _fake_block("rn1", cs_r, cs_c)
        cached = {
            "entropy_tap": {
                "ro1": {
                    "ring_region": "ring1",
                    "ring_pin": "ro",
                    "cs_pin": "rn1",
                    "ring_intra_region": {
                        "resistance_ohm": 105.8341,
                        "capacitance_ff": 7.889961,
                    },
                    "combiner_sampler_intra_region": {
                        "resistance_ohm": 88.1193,
                        "capacitance_ff": 0.585014,
                    },
                }
            },
            "driver_side_load": {},
        }
        return (
            cached,
            {"ro_ring11": ring1, "ro_ring11_ring2": ring2},
            {"ro_ring11": ring1_ports, "ro_ring11_ring2": ring2_ports},
            cs,
            cs_ports,
        )

    def test_a_report_matching_a_fresh_extraction_passes(self):
        _reconcile_cached_report(*self._fixture())

    def test_drifted_ring_side_capacitance_raises(self):
        with self.assertRaises(FlowError):
            _reconcile_cached_report(*self._fixture(ring_c=8.4))

    def test_drifted_combiner_sampler_side_resistance_raises(self):
        with self.assertRaises(FlowError):
            _reconcile_cached_report(*self._fixture(cs_r=91.0))


@unittest.skipUnless(
    FULLCHIP_REPORT.is_file(),
    f"{FULLCHIP_REPORT.relative_to(REPO_ROOT)} does not exist yet -- run "
    "`python3 layout/pex/build.py --fullchip-extract` first (requires klt "
    "and the gf180mcu PDK; see layout/pex/build.py's own docstring for why "
    "this is a separate, opt-in step)",
)
class CommittedFullchipReportReconciliationTests(unittest.TestCase):
    """The COMMITTED report and netlist, if a `--fullchip-extract` run has
    ever produced one. Skipped (not failed) otherwise -- this is a
    staleness guard on artefacts that exist, not a mandate that they do
    (`layout/tests/test_verify.py`'s own PDK-absence convention)."""

    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(FULLCHIP_REPORT.read_text())

    def test_every_entropy_tap_delta_reconciles(self):
        for name, entry in self.report["entropy_tap"].items():
            with self.subTest(net=name):
                expected_r = (
                    entry["fullchip"]["resistance_ohm"]
                    - entry["ring_intra_region"]["resistance_ohm"]
                    - entry["combiner_sampler_intra_region"]["resistance_ohm"]
                )
                expected_c = (
                    entry["fullchip"]["capacitance_ff"]
                    - entry["ring_intra_region"]["capacitance_ff"]
                    - entry["combiner_sampler_intra_region"]["capacitance_ff"]
                )
                self.assertAlmostEqual(entry["delta"]["resistance_ohm"], max(expected_r, 0.0), places=4)
                self.assertAlmostEqual(entry["delta"]["capacitance_ff"], max(expected_c, 0.0), places=4)

    def test_every_driver_side_load_delta_reconciles(self):
        for name, entry in self.report["driver_side_load"].items():
            with self.subTest(net=name):
                expected_c = (
                    entry["fullchip"]["capacitance_ff"]
                    - entry["combiner_sampler_intra_region"]["capacitance_ff"]
                )
                self.assertAlmostEqual(entry["delta"]["capacitance_ff"], max(expected_c, 0.0), places=4)

    def test_deltas_are_non_negative(self):
        """Parasitics are only ever added by more wire -- a committed delta
        below zero would mean the report itself was written from an
        arithmetic that should have raised instead."""
        for name, entry in self.report["entropy_tap"].items():
            with self.subTest(net=name):
                self.assertGreaterEqual(entry["delta"]["resistance_ohm"], 0.0)
                self.assertGreaterEqual(entry["delta"]["capacitance_ff"], 0.0)
        for name, entry in self.report["driver_side_load"].items():
            with self.subTest(net=name):
                self.assertGreaterEqual(entry["delta"]["capacitance_ff"], 0.0)

    @unittest.skipUnless(
        FULLCHIP_NETLIST.is_file(),
        f"{FULLCHIP_NETLIST.relative_to(REPO_ROOT)} does not exist yet",
    )
    def test_composed_netlist_carries_the_reports_own_delta_values(self):
        """The JSON report and the SPICE artefact it fed must never
        silently drift apart: every `r`/`c` card `_pi_delta_lines` writes is
        held here to the report's own `delta` figures, byte-for-byte in the
        formatting `layout/pex/build.py` itself uses."""
        text = FULLCHIP_NETLIST.read_text()
        entropy = self.report["entropy_tap"]
        loads = self.report["driver_side_load"]

        for prefix, name in (("delta1", "ro1"), ("delta2", "ro2")):
            delta = entropy[name]["delta"]
            c_half = delta["capacitance_ff"] * 1e-15 / 2
            r_line = f"r{prefix} "
            found_r = [line for line in text.splitlines() if line.startswith(r_line)]
            self.assertEqual(len(found_r), 1, f"expected exactly one {r_line!r} card")
            self.assertIn(f"{delta['resistance_ohm']:.6f}", found_r[0])

            for suffix in ("a", "b"):
                c_line_prefix = f"c{prefix}{suffix} "
                found_c = [line for line in text.splitlines() if line.startswith(c_line_prefix)]
                self.assertEqual(len(found_c), 1, f"expected exactly one {c_line_prefix!r} card")
                self.assertIn(f"{c_half:.6e}", found_c[0])

        for name in ("raw_bit", "raw_valid", "ring_bit1", "ring_bit2"):
            c_f = loads[name]["delta"]["capacitance_ff"] * 1e-15
            load_prefix = f"cload_{name} "
            found = [line for line in text.splitlines() if line.startswith(load_prefix)]
            self.assertEqual(len(found), 1, f"expected exactly one {load_prefix!r} card")
            self.assertIn(f"{c_f:.6e}", found[0])

    def test_report_records_a_runtime_and_klt_version(self):
        """`--fullchip-extract`'s own cost (DR-0025's own budgeted-runtime
        requirement) must be a recorded fact, not merely a claim made
        elsewhere."""
        meta = self.report["extraction"]
        self.assertIn("runtime_s", meta)
        self.assertGreater(meta["runtime_s"], 0)
        self.assertIn("klt_version", meta)


if __name__ == "__main__":
    unittest.main()
