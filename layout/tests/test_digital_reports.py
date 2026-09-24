#!/usr/bin/env python3
"""Unit tests for the shape of `layout/digital/reports/{drc,lvs}.json`
(issue #273) -- that they are committed as full, *gradeable* `klt`
envelopes rather than reduced summaries, and that the pins
`signoff/block-manifest.json` cites them by actually resolve.

Why a test and not a convention
-------------------------------
From #170 until #273, `layout/digital/build.py` and `layout/digital/lvs.py`
reduced `klt drc`/`klt lvs`'s responses to a handful of verdict fields
before writing them. Every number in those digests was true. What they
dropped -- `schema_version`, the `violations`/`mismatches` array, and the
`provenance` block -- is exactly what `klt signoff` reads to decide what
kind of evidence a cited file *is*, so the digital partition's clean DRC and
matching LVS graded `unmet`/`no_evidence` on T1 items 3 and 4 for want of a
file shape, while the analog partition's own envelopes graded `met`.

Nothing in CI would catch that regression recurring. `layout/verify.py`'s
freshness gate covers `layout/reports/` (the analog fixtures) and not
`layout/digital/reports/`; `.github/workflows/pdk-nightly.yml` never re-runs
`layout/digital/build.py` or `layout/digital/lvs.py` at all, because a
place-and-route rebuild is stochastic and hours long. So a future edit to
either `_committed_view` could silently re-reduce these two reports and the
only symptom would be the T1 verdict of record quietly dropping two items --
a number nobody re-reads by hand. **These tests are that alarm**, and they
run on the PR-blocking path (`npm run test:layout`, wired into
`npm run check:ci`) with no `klt`, no PDK and no network: they read the
committed JSON and hash committed files, nothing more.

They deliberately do *not* assert a verdict. Whether the digital section is
DRC-clean or LVS-matching is a question for the tools, re-answered by
re-running the scripts; asserting `status == "clean"` here would just be
this repo marking its own homework from a file it also writes. What is
asserted is that whatever the tools said was committed in a form a third
party can re-grade.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

LAYOUT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAYOUT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DIGITAL_DIR = LAYOUT_DIR / "digital"
REPORTS_DIR = DIGITAL_DIR / "reports"
DRC_REPORT = REPORTS_DIR / "drc.json"
LVS_REPORT = REPORTS_DIR / "lvs.json"
MANIFEST = REPO_ROOT / "signoff" / "block-manifest.json"


def _load(name: str, path: Path):
    """Load a flat `layout/digital/*.py` driver as a module.

    The same `importlib.util.spec_from_file_location` pattern
    `layout/tests/test_verify.py` and `layout/verify.py`'s own
    `_load_build_module` use: these are scripts run by path, not package
    members, so there is no import path to reach them by.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


build = _load("layout_digital_build", DIGITAL_DIR / "build.py")
lvs = _load("layout_digital_lvs", DIGITAL_DIR / "lvs.py")


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class CommittedViewTests(unittest.TestCase):
    """The two `_committed_view` functions must pass the envelope through,
    not select fields out of it."""

    def test_drc_committed_view_drops_nothing(self):
        payload = {
            "schema_version": 2,
            "file": "layout/digital/trng_top.gds",
            "deck": "gf180mcu",
            "status": "clean",
            "violation_count": 0,
            "rule_counts": {},
            "violations": [],
            "coverage": {"rules_skipped": ["mim.space.1"]},
            "provenance": {"input": {"content_hash": "sha256:abc"}},
        }
        self.assertEqual(build._drc_committed_view(payload), payload)

    def test_drc_committed_view_copies_rather_than_aliases(self):
        """A caller that mutates the payload afterwards (as `build()` does,
        via `_drc_summary`) must not retroactively edit what was written."""
        payload = {"schema_version": 2, "status": "clean"}
        view = build._drc_committed_view(payload)
        payload["status"] = "dirty"
        self.assertEqual(view["status"], "clean")

    def test_drc_summary_is_still_the_digest_for_the_nested_field(self):
        """`_drc_summary` keeps its old four-field shape -- it is what
        `reports/place_and_route.json`'s nested `drc` carries, and #273 did
        not widen that."""
        payload = {
            "status": "clean",
            "deck": "gf180mcu",
            "violation_count": 0,
            "rule_counts": {},
            "violations": [],
            "provenance": {"klt_version": "0.6.0"},
        }
        self.assertEqual(
            build._drc_summary(payload),
            {
                "status": "clean",
                "deck": "gf180mcu",
                "violation_count": 0,
                "rule_counts": {},
            },
        )

    def test_lvs_committed_view_keeps_every_envelope_key(self):
        payload = {
            "schema_version": 1,
            "engine": "klayout",
            "layout": "trng_top.extracted.spice",
            "reference": "trng_top.lvs_reference.spice",
            "top": "TRNG_TOP",
            "status": "match",
            "mismatch_count": 0,
            "mismatches": [],
            "power_connectivity": {"status": "unchecked"},
            "body_verification": {"status": "unchecked"},
            "provenance": {"input": {"content_hash": "sha256:abc"}},
        }
        view = lvs._committed_view(payload, {"instance_count": 3})
        for key in payload:
            self.assertIn(key, view, f"{key} was dropped from the committed view")

    def test_lvs_committed_view_restates_paths_repo_root_relative(self):
        """`klt lvs` echoes the request's own directory-relative paths. The
        report lands a directory deeper, so an unrestated path resolves from
        neither the repo root nor the report's own directory -- and both
        `signoff/check.py` and `klt signoff` re-hash the input an envelope
        names, from the repo root."""
        payload = {
            "layout": "trng_top.extracted.spice",
            "reference": "trng_top.lvs_reference.spice",
            "status": "match",
        }
        view = lvs._committed_view(payload, {})
        self.assertEqual(view["layout"], "layout/digital/trng_top.extracted.spice")
        self.assertEqual(
            view["reference"], "layout/digital/trng_top.lvs_reference.spice"
        )
        for field in ("layout", "reference"):
            self.assertTrue(
                (REPO_ROOT / view[field]).is_file(),
                f"{field}={view[field]!r} does not resolve from the repo root",
            )

    def test_lvs_committed_view_does_not_shadow_the_reference_field(self):
        """This script's own reference-generation record lives under
        `reference_generation`. Before #273 it was written to `reference`,
        which is the envelope's own field for the reference netlist path."""
        view = lvs._committed_view(
            {"reference": "trng_top.lvs_reference.spice"}, {"instance_count": 7}
        )
        self.assertIsInstance(view["reference"], str)
        self.assertEqual(view["reference_generation"]["instance_count"], 7)
        self.assertEqual(
            view["reference_generation"]["generator"], "layout/digital/lvs.py"
        )


class CommittedEnvelopeTests(unittest.TestCase):
    """The two committed reports must be gradeable envelopes on disk --
    the regression #273 fixed, asserted against the artifacts themselves
    rather than against the functions that write them."""

    def setUp(self):
        self.drc = json.loads(DRC_REPORT.read_text())
        self.lvs = json.loads(LVS_REPORT.read_text())

    def test_both_declare_a_schema_version(self):
        for name, report in (("drc.json", self.drc), ("lvs.json", self.lvs)):
            with self.subTest(report=name):
                self.assertIn("schema_version", report)

    def test_each_carries_its_kind_discriminating_array(self):
        """`klt signoff`'s classifier tells a DRC envelope from an LVS one by
        which of these two arrays is present."""
        self.assertIsInstance(self.drc.get("violations"), list)
        self.assertIsInstance(self.lvs.get("mismatches"), list)

    def test_each_pins_its_own_input(self):
        for name, report in (("drc.json", self.drc), ("lvs.json", self.lvs)):
            with self.subTest(report=name):
                pinned = (
                    (report.get("provenance") or {}).get("input") or {}
                ).get("content_hash")
                self.assertTrue(
                    pinned, f"{name} records no provenance.input.content_hash"
                )

    def test_each_pin_matches_the_artifact_it_names_on_disk(self):
        """A pin that does not match the committed artifact is a citation
        describing a revision this tree does not contain."""
        for name, report, field in (
            ("drc.json", self.drc, "file"),
            ("lvs.json", self.lvs, "layout"),
        ):
            with self.subTest(report=name):
                artifact = REPO_ROOT / report[field]
                self.assertTrue(
                    artifact.is_file(),
                    f"{name} names {report[field]!r}, which is not in this tree",
                )
                self.assertEqual(
                    _sha256(artifact),
                    report["provenance"]["input"]["content_hash"],
                    f"{name}'s pin does not describe {report[field]} as committed",
                )

    def test_lvs_keeps_the_reference_generation_disclosure(self):
        """The digital reference is a mechanical transcription of
        `trng_top.pnr.v`, not an independently captured schematic netlist.
        That caveat is not in `klt`'s envelope, so it must stay in ours."""
        generation = self.lvs.get("reference_generation") or {}
        self.assertEqual(generation.get("generator"), "layout/digital/lvs.py")
        self.assertEqual(
            generation.get("source"), "layout/digital/trng_top.pnr.v"
        )

    def test_lvs_records_both_coverage_verdicts_it_is_asked_to_disclose(self):
        """`power_connectivity` and `body_verification` are what
        `signoff/README.md` must quote for item 4. They may say
        `"unchecked"` -- what they may not do is be absent."""
        for field in ("power_connectivity", "body_verification"):
            with self.subTest(field=field):
                self.assertIsInstance(self.lvs.get(field), dict)
                self.assertIn("status", self.lvs[field])


class ManifestCitationTests(unittest.TestCase):
    """`signoff/block-manifest.json` must cite these two envelopes, and its
    pins must agree with theirs -- the half-finished-re-pin failure
    `signoff/check.py` also guards, asserted here without needing `klt`."""

    def setUp(self):
        self.evidence = json.loads(MANIFEST.read_text())["evidence"]

    def test_digital_drc_and_lvs_are_both_cited(self):
        self.assertEqual(
            self.evidence["3.digital"]["file"], "layout/digital/reports/drc.json"
        )
        self.assertEqual(
            self.evidence["4.digital"]["file"], "layout/digital/reports/lvs.json"
        )

    def test_manifest_pins_agree_with_the_envelopes_own_pins(self):
        for key in ("3.digital", "4.digital"):
            with self.subTest(item=key):
                entry = self.evidence[key]
                envelope = json.loads((REPO_ROOT / entry["file"]).read_text())
                self.assertEqual(
                    entry["content_hash"],
                    envelope["provenance"]["input"]["content_hash"],
                )


if __name__ == "__main__":
    unittest.main()
