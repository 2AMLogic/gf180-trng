#!/usr/bin/env python3
"""Unit tests for `layout/verify.py`'s freshness-gate comparison logic --
`_stable()` and `compare_reports()` (issue #148).

These exercise the comparison functions directly with synthetic report
payloads, so they need neither `klt` nor an installed PDK -- the point is
the *comparison logic*, not a live DRC/LVS run (that coverage already lives
in `layout/verify.py`'s own `--require-tools` invocation, run nightly
against real tools by `.github/workflows/pdk-nightly.yml`).

Two things this suite must prove, per #148's acceptance criteria:

1. Two reports that differ *only* in a machine-local field (`pdk.root`,
   `provenance.pdk.source`, `environment.engine_version`) compare equal --
   this is the false-positive #148 exists to fix.
2. Two reports that differ in anything else -- a verdict, a rule/error
   count, a content hash, the PDK variant/version actually used -- compare
   UNEQUAL. Without this half, "fix" #1 by widening `_stable()` too far
   would turn the freshness gate into a no-op, which the issue explicitly
   calls out as worse than today's false positives.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

LAYOUT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAYOUT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# `layout/verify.py` is a flat module, not a package member of anything else
# under `layout/` (see `layout/_klt.py`'s own docstring on the same point),
# and it eagerly loads every cell/block/ring `build.py` at import time. All
# of those live under the checked-in `layout/` tree, so this costs one real
# (fast) import, not a live tool run -- loaded from its own file, the same
# way `verify.py`'s own `_load_build_module` loads its cell/block modules,
# so a second, unrelated test module named `verify` elsewhere can't shadow
# it via `sys.modules`.
_SPEC = importlib.util.spec_from_file_location(
    "layout_tests_verify_module", LAYOUT_DIR / "verify.py"
)
verify = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(verify)


#: A representative `klt extract` report -- the only report kind that ever
#: carries a non-null `pdk` / `provenance.pdk` block (DRC and LVS reports do
#: not resolve one; see `_stable()`'s own docstring). Trimmed to the fields
#: `_stable()` and `compare_reports()` actually look at; real reports carry
#: many more (device lists, nets, ...) that both simply pass through
#: unexamined.
def _extract_payload(stem: str = "ro_stage") -> dict:
    return {
        "schema_version": 1,
        # `_committed_view()` always overwrites this to the same
        # `layout/reports/<stem>.extracted.spice` string for stage
        # "extract" (see its own docstring) -- set to the post-restatement
        # value directly here so a fixture built by this helper already
        # matches what `compare_reports()` would treat as "on disk".
        "netlist_path": f"layout/reports/{stem}.extracted.spice",
        "netlist_sha256": "content-hash-of-the-extracted-devices",
        "status": "extracted",
        "device_count": 4,
        "pdk": {
            "variant": "gf180mcuD",
            "root": "/Users/rwalters/.volare",
            "version": "open_pdks c6d73a35f524070e85faff4a6a9eef49553ebc2b",
        },
        "provenance": {
            "klt_version": "0.2.0",
            "klayout_version": "0.30.10",
            "pdk": {
                "name": "gf180mcuD",
                "source": "search root: ~/.volare",
                "version": "open_pdks c6d73a35f524070e85faff4a6a9eef49553ebc2b",
            },
            "deck": {"name": "gf180mcu", "content_hash": "sha256:deck-hash"},
            "input": {"content_hash": "sha256:input-hash"},
        },
    }


def _lvs_payload() -> dict:
    return {
        "schema_version": 1,
        "status": "match",
        "category_counts": {"device.body_unverified": 2, "topology": 1},
        "environment": {
            "engine": "klayout",
            "engine_version": "0.30.10",
            "layout_sha256": "layout-hash",
            "reference_sha256": "reference-hash",
        },
        "provenance": {
            "klt_version": "0.2.0",
            "klayout_version": "0.30.10",
            "pdk": None,
            "deck": {"name": "gf180mcu", "content_hash": "sha256:deck-hash"},
            "input": None,
        },
    }


class StableMachineLocalFieldsTests(unittest.TestCase):
    """`_stable()` drops exactly the machine-local fields it documents."""

    def test_differing_pdk_root_compares_equal(self):
        a = _extract_payload()
        b = copy.deepcopy(a)
        b["pdk"]["root"] = "/home/ubuntu/.volare"
        self.assertEqual(verify._stable(a), verify._stable(b))

    def test_differing_provenance_pdk_source_compares_equal(self):
        a = _extract_payload()
        b = copy.deepcopy(a)
        b["provenance"]["pdk"]["source"] = "--pdk-root flag"
        self.assertEqual(verify._stable(a), verify._stable(b))

    def test_both_machine_local_fields_together_compare_equal(self):
        a = _extract_payload()
        b = copy.deepcopy(a)
        b["pdk"]["root"] = "/home/ubuntu/.volare"
        b["provenance"]["pdk"]["source"] = "search_root:~/.ciel"
        self.assertEqual(verify._stable(a), verify._stable(b))

    def test_differing_engine_version_compares_equal(self):
        # Pre-existing behavior (#73) -- still covered directly so a future
        # edit to `_stable()` cannot silently regress it.
        a = _lvs_payload()
        b = copy.deepcopy(a)
        b["environment"]["engine_version"] = "0.31.0"
        self.assertEqual(verify._stable(a), verify._stable(b))

    def test_drc_report_with_no_pdk_block_is_unaffected(self):
        # DRC reports never carry `pdk` / non-null `provenance.pdk` -- this
        # must be a no-op, not a KeyError.
        payload = {
            "schema_version": 1,
            "status": "clean",
            "rule_counts": {},
            "provenance": {
                "klt_version": "0.2.0",
                "klayout_version": "0.30.10",
                "pdk": None,
                "deck": {"name": "gf180mcu", "content_hash": "sha256:deck-hash"},
                "input": {"content_hash": "sha256:input-hash"},
            },
        }
        self.assertEqual(verify._stable(payload), payload)


class StableContentFieldsStillCompareTests(unittest.TestCase):
    """The regression test #148's Scope requires: a real change must still
    trip the gate. Every field named in `_stable()`'s own "stays" list gets
    one case here."""

    def test_differing_verdict_status_compares_unequal(self):
        a = _extract_payload()
        b = copy.deepcopy(a)
        b["status"] = "error"
        self.assertNotEqual(verify._stable(a), verify._stable(b))

    def test_differing_netlist_sha256_compares_unequal(self):
        a = _extract_payload()
        b = copy.deepcopy(a)
        b["netlist_sha256"] = "a-different-content-hash"
        self.assertNotEqual(verify._stable(a), verify._stable(b))

    def test_differing_device_count_compares_unequal(self):
        a = _extract_payload()
        b = copy.deepcopy(a)
        b["device_count"] = 5
        self.assertNotEqual(verify._stable(a), verify._stable(b))

    def test_differing_deck_content_hash_compares_unequal(self):
        a = _extract_payload()
        b = copy.deepcopy(a)
        b["provenance"]["deck"]["content_hash"] = "sha256:a-different-deck"
        self.assertNotEqual(verify._stable(a), verify._stable(b))

    def test_differing_input_content_hash_compares_unequal(self):
        a = _extract_payload()
        b = copy.deepcopy(a)
        b["provenance"]["input"]["content_hash"] = "sha256:a-different-gds"
        self.assertNotEqual(verify._stable(a), verify._stable(b))

    def test_differing_pdk_variant_compares_unequal(self):
        # Which PDK was targeted is what was verified against, not where it
        # happened to be sitting -- unlike `root`, it must stay compared.
        a = _extract_payload()
        b = copy.deepcopy(a)
        b["pdk"]["variant"] = "gf180mcuC"
        self.assertNotEqual(verify._stable(a), verify._stable(b))

    def test_differing_pdk_version_compares_unequal(self):
        a = _extract_payload()
        b = copy.deepcopy(a)
        b["pdk"]["version"] = "open_pdks 0000000000000000000000000000000000000000"
        self.assertNotEqual(verify._stable(a), verify._stable(b))

    def test_differing_lvs_status_compares_unequal(self):
        a = _lvs_payload()
        b = copy.deepcopy(a)
        b["status"] = "mismatch"
        self.assertNotEqual(verify._stable(a), verify._stable(b))

    def test_differing_category_counts_compares_unequal(self):
        a = _lvs_payload()
        b = copy.deepcopy(a)
        b["category_counts"] = {"net.unmatched": 1, **a["category_counts"]}
        self.assertNotEqual(verify._stable(a), verify._stable(b))

    def test_differing_layout_sha256_compares_unequal(self):
        # The other half of the `environment` block `engine_version` lives
        # in -- #73's own point: dropping the whole block would have hidden
        # this too.
        a = _lvs_payload()
        b = copy.deepcopy(a)
        b["environment"]["layout_sha256"] = "a-different-layout-hash"
        self.assertNotEqual(verify._stable(a), verify._stable(b))

    def test_differing_klt_version_compares_unequal(self):
        # Deliberately NOT normalized -- a klt upgrade that changes a
        # verdict is meant to turn this gate red (pdk-nightly.yml's own
        # comment) so `layout/reports/` gets regenerated, not silently pass.
        a = _extract_payload()
        b = copy.deepcopy(a)
        b["provenance"]["klt_version"] = "0.3.0"
        self.assertNotEqual(verify._stable(a), verify._stable(b))


class CompareReportsIntegrationTests(unittest.TestCase):
    """End-to-end through `compare_reports()`: committed-report-on-disk vs.
    a live run's in-memory payload, the exact comparison the freshness gate
    performs -- with `REPORT_DIR`/`WORK_DIR` redirected to a scratch
    directory so this needs no real `layout/reports/` fixture."""

    def setUp(self):
        # `compare_reports()` formats its drift messages with
        # `path.relative_to(REPO_ROOT)`, so the scratch dir has to sit under
        # `REPO_ROOT` like the real `layout/reports/`/`layout/.work/` do --
        # anywhere else raises a `ValueError` before the comparison this
        # test is checking even runs.
        self.tmp = tempfile.TemporaryDirectory(dir=REPO_ROOT)
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.report_dir = root / "reports"
        self.work_dir = root / "work"
        self.report_dir.mkdir()
        self.work_dir.mkdir()
        patcher_reports = mock.patch.object(verify, "REPORT_DIR", self.report_dir)
        patcher_work = mock.patch.object(verify, "WORK_DIR", self.work_dir)
        patcher_reports.start()
        patcher_work.start()
        self.addCleanup(patcher_reports.stop)
        self.addCleanup(patcher_work.stop)

    def _commit(self, stem: str, stage: str, payload: dict) -> None:
        path = self.report_dir / f"{stem}.{stage}.json"
        path.write_text(json.dumps(payload, indent=2) + "\n")

    def _write_matching_spice(self, stem: str) -> None:
        # `compare_reports()` diffs `<stem>.extracted.spice` unconditionally
        # (see `_text_artifacts()`) regardless of which JSON stage a test
        # cares about, so every case below has to give it a byte-identical
        # pair in both directories or that unrelated check adds its own
        # "is missing"/"does not match" entry to `drift`.
        content = f"* {stem} extracted netlist (identical on both sides)\n"
        (self.report_dir / f"{stem}.extracted.spice").write_text(content)
        (self.work_dir / f"{stem}.extracted.spice").write_text(content)

    def test_different_machine_same_content_produces_no_drift(self):
        committed = _extract_payload()
        self._commit("ro_stage", "extract", committed)
        self._write_matching_spice("ro_stage")

        live = copy.deepcopy(committed)
        live["pdk"]["root"] = "/home/ubuntu/.volare"
        live["provenance"]["pdk"]["source"] = "search_root:~/.ciel"

        drift = verify.compare_reports(
            "ro_stage", {}, {"extract": live}
        )
        self.assertEqual(drift, [])

    def test_genuine_verdict_drift_is_still_caught(self):
        committed = _lvs_payload()
        self._commit("ro_stage", "lvs", committed)
        self._write_matching_spice("ro_stage")

        live = copy.deepcopy(committed)
        live["status"] = "mismatch"  # a real LVS regression, not a path change

        drift = verify.compare_reports("ro_stage", {}, {"lvs": live})
        self.assertEqual(len(drift), 1)
        self.assertIn("ro_stage.lvs.json does not match this run", drift[0])

    def test_extracted_spice_byte_diff_is_still_caught(self):
        # The text-artifact half of compare_reports(): unaffected by
        # `_stable()`, still exercised here so a future change to
        # `_text_artifacts()` handling can't silently stop diffing it.
        (self.report_dir / "ro_stage.extracted.spice").write_text("* v1\n")
        (self.work_dir / "ro_stage.extracted.spice").write_text("* v2\n")

        drift = verify.compare_reports("ro_stage", {}, {})
        self.assertEqual(len(drift), 1)
        self.assertIn("ro_stage.extracted.spice does not match this run", drift[0])

    def test_identical_extracted_spice_produces_no_drift(self):
        (self.report_dir / "ro_stage.extracted.spice").write_text("* same\n")
        (self.work_dir / "ro_stage.extracted.spice").write_text("* same\n")

        drift = verify.compare_reports("ro_stage", {}, {})
        self.assertEqual(drift, [])


if __name__ == "__main__":
    unittest.main()
