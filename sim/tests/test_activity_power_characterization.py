#!/usr/bin/env python3
"""The committed observed-activity records and companion document are
internally consistent and current (#453). Stdlib only; reads committed
records, needs no PDK or simulator."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import activity_power_characterization as apc  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tb" / "digital-sta-power"))
import activity as act  # noqa: E402


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


def synthetic_manifest() -> dict:
    """A tool-free manifest describing the current capture program (valid control)."""
    traces = {}
    for name in act.wl.WORKLOADS:
        traces[name] = dict(act.expected_trace_semantics(name), workload=name)
    return {
        "schema": 1,
        "identities": {
            "netlist": {"git_blob_sha": act.report.blob_sha(act.REPO_ROOT, act.PNR_NETLIST)},
            "testbench": {"git_blob_sha": act.report.blob_sha(act.REPO_ROOT, act.TB_SOURCE)},
        },
        "traces": traces,
    }


class CaptureSourceFreshnessTests(unittest.TestCase):
    def test_valid_control_passes(self):
        act.verify_capture_source(synthetic_manifest())

    def test_stale_testbench_is_rejected(self):
        m = synthetic_manifest()
        m["identities"]["testbench"]["git_blob_sha"] = "0" * 40
        with self.assertRaisesRegex(act.ActivityError, "stale capture testbench"):
            act.verify_capture_source(m)

    def test_stale_testbench_rejected_before_vcd_checks(self):
        m = synthetic_manifest()
        m["identities"]["testbench"]["git_blob_sha"] = "0" * 40
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "manifest.json"
            path.write_text(json.dumps(m))
            with self.assertRaisesRegex(act.ActivityError, "stale capture testbench"):
                act.load_manifest(path)  # traces name no VCDs: never reached

    def test_window_only_change_is_rejected(self):
        # Stimulus bytes, cycles and netlist unchanged; only a boundary moved.
        m = synthetic_manifest()
        t = m["traces"]["raw-streaming"]
        t["windows_cycles"]["steady"][0] += 1
        with self.assertRaisesRegex(act.ActivityError, r"raw-streaming.*windows_cycles"):
            act.verify_capture_source(m)

    def test_window_ps_clock_cycles_and_seed_changes_are_rejected(self):
        for fld, val in (("windows_ps", {"reset": [0, 1]}), ("clock_period_ns", 500.0),
                         ("cycles", 1), ("seed", 12345)):
            m = synthetic_manifest()
            m["traces"]["raw-streaming"][fld] = val
            with self.assertRaisesRegex(act.ActivityError, fld):
                act.verify_capture_source(m)

    def test_missing_and_malformed_fields_are_named(self):
        m = synthetic_manifest()
        del m["traces"]["raw-streaming"]["windows_cycles"]
        with self.assertRaisesRegex(act.ActivityError, r"raw-streaming.*`windows_cycles` is missing"):
            act.verify_capture_source(m)
        m = synthetic_manifest()
        m["traces"]["raw-streaming"]["cycles"] = "many"
        with self.assertRaisesRegex(act.ActivityError, r"`cycles` is malformed"):
            act.verify_capture_source(m)
        m = synthetic_manifest()
        del m["identities"]["testbench"]
        with self.assertRaisesRegex(act.ActivityError, r"identities.*testbench"):
            act.verify_capture_source(m)
        m = synthetic_manifest()
        m["traces"] = {}
        with self.assertRaisesRegex(act.ActivityError, "empty"):
            act.verify_capture_source(m)

    def test_workloads_module_blob_is_semantic_not_strict(self):
        m = synthetic_manifest()
        m["identities"]["workloads_module_git_blob_sha"] = "0" * 40
        act.verify_capture_source(m)  # a source-only edit does not stale evidence


class CampaignCoverageTests(unittest.TestCase):
    def test_workload_removed_from_every_corner_is_incomplete(self):
        fam = apc.load_family()
        for r in fam.values():
            r.traces = [t for t in r.traces if t[0] != "backpressure"]
        problems = apc.check(fam)
        self.assertTrue(any("incomplete campaign" in p and "backpressure" in p for p in problems))

    def test_duplicate_and_extra_workloads_are_named(self):
        fam = apc.load_family()
        r = next(iter(fam.values()))
        r.traces = r.traces + [r.traces[0], ("mystery",) + r.traces[0][1:]]
        problems = apc.check(fam)
        self.assertTrue(any("duplicate workload trace" in p for p in problems))
        self.assertTrue(any("undeclared workload" in p and "mystery" in p for p in problems))

    def test_explicit_subset_is_accepted_only_when_declared(self):
        fam = apc.load_family()
        names = tuple(t[0] for t in next(iter(fam.values())).traces)
        self.assertEqual(apc.campaign_problems(next(iter(fam.values())), names), [])
        self.assertTrue(apc.campaign_problems(next(iter(fam.values())), names + ("extra-one",)))

    def test_record_with_stale_testbench_pin_is_flagged(self):
        fam = apc.load_family()
        r = next(iter(fam.values()))
        r.testbench_sha = "0" * 40
        self.assertTrue(any("stale capture testbench" in p for p in apc.check(fam)))

    def test_record_whose_manifest_has_moved_windows_is_flagged(self):
        fam = apc.load_family()
        r = next(iter(fam.values()))
        m = copy.deepcopy(r.manifest())
        m["traces"]["raw-streaming"]["windows_cycles"]["steady"][1] -= 1
        r._manifest = m
        self.assertTrue(any("windows_cycles" in p for p in apc.check(fam)))

    def test_malformed_record_metadata_fails_by_name(self):
        text = (apc.RECORDS / "2026-10-10-digital-sta-activity-01.md").read_text()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x-digital-sta-activity-01.md"
            p.write_text(text.replace("  testbench_sha:", "  testbench_removed:"))
            with self.assertRaisesRegex(apc.CheckError, "testbench_sha"):
                apc.Rec(p)


if __name__ == "__main__":
    unittest.main()
