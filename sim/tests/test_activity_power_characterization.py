#!/usr/bin/env python3
"""The committed observed-activity records and companion document are
internally consistent and current (#453). Stdlib only; reads committed
records, needs no PDK or simulator."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import activity_power_characterization as apc  # noqa: E402


class CommittedFamilyTests(unittest.TestCase):
    def test_check_passes_on_the_committed_family(self):
        fam = apc.load_family()
        self.assertEqual(set(fam), set(apc.EXPECTED))
        self.assertEqual(apc.check(fam), [])

    def test_document_block_is_current(self):
        fam = apc.load_family()
        text = apc.DOC.read_text()
        body = text.split(apc.BEGIN, 1)[1].split(apc.END, 1)[0].strip("\n")
        self.assertEqual(body, apc.markdown(fam))

    def test_a_perturbed_uniform_baseline_is_caught(self):
        fam = apc.load_family()
        victim = next(iter(fam.values()))
        victim.values["uniform_total_w"] *= 1.01
        self.assertTrue(any("uniform baseline" in p for p in apc.check(fam)))

    def test_unannotated_pins_are_caught(self):
        fam = apc.load_family()
        victim = next(iter(fam.values()))
        k = apc.key("raw-streaming", "steady", "unannotated_pins")
        victim.values[k] = 500.0
        self.assertTrue(any("unannotated" in p for p in apc.check(fam)))

    def test_a_changed_workload_makes_the_records_stale(self):
        fam = apc.load_family()
        victim = next(iter(fam.values()))
        name, vcd, size, stim, cycles, win = victim.traces[0]
        victim.traces[0] = (name, vcd, size, "0" * 64, cycles, win)
        for r in fam.values():
            r.traces = victim.traces
        self.assertTrue(any("stale" in p for p in apc.check(fam)))


if __name__ == "__main__":
    unittest.main()
