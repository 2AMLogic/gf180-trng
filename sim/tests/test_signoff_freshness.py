"""Signoff freshness gate: an envelope must still describe its input on disk.

check_envelope_against_its_input() is what stops stale evidence from being
cited, so both halves are pinned: a matching digest passes, and every way an
envelope can fail to prove freshness is rejected with a message. Synthetic
envelopes live under a temp dir that stands in for the repo root.
"""

import contextlib
import hashlib
import io
import json
import tempfile
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
from sim.tools.pathload import load_module_from_path  # noqa: E402  (#553)
check = load_module_from_path("signoff_check", ROOT / "signoff" / "check.py")

PAYLOAD = b"synthetic layout bytes\n"
DIGEST = "sha256:" + hashlib.sha256(PAYLOAD).hexdigest()
WRONG = "sha256:" + "0" * 64


class EnvelopeFreshness(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        patch = mock.patch.object(check, "REPO_ROOT", self.root)
        patch.start()
        self.addCleanup(patch.stop)
        (self.root / "art").mkdir()
        (self.root / "art" / "in.gds").write_bytes(PAYLOAD)
        self.env_path = self.root / "ev" / "report.json"
        self.env_path.parent.mkdir()
        self.failures: list[str] = []

    def run_check(self, envelope):
        return check.check_envelope_against_its_input(self.env_path, envelope, self.failures)

    def prov(self, digest=DIGEST):
        return {"input": {"content_hash": digest}} if digest else {}

    def test_matching_digest_passes(self):
        env = {"file": "art/in.gds", "provenance": self.prov()}
        self.assertTrue(self.run_check(env))
        self.assertEqual(self.failures, [])

    def test_source_field_matching_digest_passes(self):
        env = {"source": "art/in.gds", "provenance": self.prov()}
        self.assertTrue(self.run_check(env))
        self.assertEqual(self.failures, [])

    def test_input_relative_to_envelope_dir_passes(self):
        (self.env_path.parent / "local.gds").write_bytes(PAYLOAD)
        env = {"layout": "local.gds", "environment": {"layout_sha256": DIGEST[7:]}}
        self.assertTrue(self.run_check(env))
        self.assertEqual(self.failures, [])

    def test_digest_mismatch_rejected(self):
        env = {"file": "art/in.gds", "provenance": self.prov(WRONG)}
        self.assertFalse(self.run_check(env))
        self.assertEqual(len(self.failures), 1)
        self.assertIn("hashes to", self.failures[0])

    def test_missing_input_rejected(self):
        env = {"file": "art/gone.gds", "provenance": self.prov()}
        self.assertFalse(self.run_check(env))
        self.assertEqual(len(self.failures), 1)
        self.assertIn("does not exist", self.failures[0])

    def test_input_named_without_digest_rejected(self):
        env = {"file": "art/in.gds", "provenance": {}}
        self.assertFalse(self.run_check(env))
        self.assertEqual(len(self.failures), 1)
        self.assertIn("records no", self.failures[0])

    def test_no_input_field_rejected(self):
        self.assertFalse(self.run_check({"provenance": self.prov()}))
        self.assertEqual(len(self.failures), 1)
        self.assertIn("names no input artifact", self.failures[0])

    def test_layout_environment_digest_form(self):
        good = {"layout": "art/in.gds", "environment": {"layout_sha256": DIGEST[7:]}}
        self.assertTrue(self.run_check(good))
        self.assertEqual(self.failures, [])
        bad = {"layout": "art/in.gds", "environment": {"layout_sha256": "0" * 64}}
        self.assertFalse(self.run_check(bad))
        self.assertIn("environment.layout_sha256", self.failures[0])
        self.failures.clear()
        self.assertFalse(self.run_check({"layout": "art/in.gds", "environment": {}}))
        self.assertIn("records no", self.failures[0])

    def test_layout_object_form_uses_provenance_digest(self):
        env = {"layout": {"path": "art/in.gds", "scope": "repo"}, "provenance": self.prov()}
        self.assertTrue(self.run_check(env))
        self.assertEqual(self.failures, [])
        env = {"layout": {"path": "art/in.gds", "scope": "repo"}, "provenance": self.prov(WRONG)}
        self.assertFalse(self.run_check(env))
        # a non-repo-scoped object names no checkable input
        self.failures.clear()
        env = {"layout": {"path": "art/in.gds", "scope": "other"}, "provenance": self.prov()}
        self.assertFalse(self.run_check(env))
        self.assertIn("names no input artifact", self.failures[0])


class Helpers(unittest.TestCase):
    def test_pinned_input_hash(self):
        self.assertEqual(check.pinned_input_hash({"provenance": {"input": {"content_hash": "x"}}}), "x")
        self.assertIsNone(check.pinned_input_hash({}))
        self.assertIsNone(check.pinned_input_hash({"provenance": None}))

    def test_manifest_entries_flattens_lists_and_skips_non_objects(self):
        manifest = {"evidence": {"b": {"file": "b"}, "a": [{"file": "a1"}, "text", {"file": "a2"}], "c": "x"}}
        got = [(k, p["file"]) for k, p in check.manifest_entries(manifest)]
        self.assertEqual(got, [("a", "a1"), ("a", "a2"), ("b", "b")])
        self.assertEqual(list(check.manifest_entries({})), [])


class CommittedManifest(unittest.TestCase):
    def test_freshness_gate_passes_on_committed_manifest(self):
        manifest = json.loads((ROOT / "signoff" / "block-manifest.json").read_text())
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(check.freshness_gate(manifest), 0)

    def test_place_and_route_envelope_is_cited_unpinned(self):
        manifest = json.loads((ROOT / "signoff" / "block-manifest.json").read_text())
        parts = manifest["evidence"]["11.digital"]
        pnr = [p for p in parts if p["file"] == check.PNR_ENVELOPE]
        self.assertEqual(len(pnr), 1)
        self.assertNotIn("content_hash", pnr[0])

    def test_item6_yield_envelope_is_cited_unpinned(self):
        """A committed `klt yield` response must be cited as 6.analog (#885).

        The citation was added by c3ed2b9f and lost in merge 742bb2af's
        conflict resolution, and nothing failed: step 1b' of freshness_gate()
        is gated on the manifest carrying the key, and the envelope lives in a
        subdirectory that step 1's non-recursive EVIDENCE_DIR sweep never
        reaches. So the evidence stayed committed while the grader rendered
        the row no_evidence for eight days. This fails if it is dropped again.
        """
        manifest = json.loads((ROOT / "signoff" / "block-manifest.json").read_text())
        if not (ROOT / check.ITEM6_ENVELOPE).is_file():
            self.skipTest(f"{check.ITEM6_ENVELOPE} is not committed in this tree")
        part = manifest["evidence"].get("6.analog")
        self.assertIsNotNone(
            part, f"{check.ITEM6_ENVELOPE} is committed but no 6.analog entry cites it"
        )
        self.assertEqual(part.get("file"), check.ITEM6_ENVELOPE)
        # Unpinned on purpose: the envelope carries no provenance block, so
        # ITEM6_ENVELOPE is exempt from the envelope-vs-input step and a
        # content_hash here would be compared against nothing (see check.py).
        self.assertNotIn("content_hash", part)

    def test_step1_exempt_envelopes_are_cited_when_committed(self):
        """Every envelope step 1 exempts must still be cited by the manifest.

        check.py skips these three in the envelope-vs-input sweep because they
        carry no provenance block, and each has its own freshness step keyed
        on its manifest citation -- so losing the citation silently disables
        the only check that covers it. Generalizes the item-6 guard above to
        items 7 and 11, the other two with the same failure mode.
        """
        manifest = json.loads((ROOT / "signoff" / "block-manifest.json").read_text())
        cited = {part.get("file") for _key, part in check.manifest_entries(manifest)}
        for envelope in (check.ITEM6_ENVELOPE, check.ITEM7_ENVELOPE, check.PNR_ENVELOPE):
            with self.subTest(envelope=envelope):
                if not (ROOT / envelope).is_file():
                    self.skipTest(f"{envelope} is not committed in this tree")
                self.assertIn(
                    envelope,
                    cited,
                    f"{envelope} is committed and exempt from step 1, but no "
                    f"manifest entry cites it -- its freshness step is disabled",
                )

    def test_stale_pin_on_item_11_lvs_entry_fails(self):
        manifest = json.loads((ROOT / "signoff" / "block-manifest.json").read_text())
        for part in manifest["evidence"]["11.analog"]:
            if part["file"].endswith(".lvs.json"):
                part["content_hash"] = WRONG
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            self.assertEqual(check.freshness_gate(manifest), 1)
        self.assertIn("11.analog", err.getvalue())


class CommittedEnvelopeSweep(unittest.TestCase):
    """committed_envelopes(): step 1's sweep must reach any depth (#916).

    The old selector was a non-recursive EVIDENCE_DIR.glob("*.json"), so an
    envelope committed under a subdirectory, cited by no manifest entry, was
    invisible to every freshness step: step 1 could not see it and the
    citation-keyed steps are each gated on a manifest key that is absent by
    assumption. These tests pin the recursive, shape-tested selector, the
    by-name step-1 exemptions, and the gate behaviour on a nested envelope.
    """

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        # EVIDENCE_DIR is derived from REPO_ROOT at import time, so patching
        # REPO_ROOT alone does not move it; both are patched and the temp
        # evidence dir is passed to committed_envelopes() directly.
        self.evidence = self.root / "signoff" / "evidence"
        for attr, value in (
            ("REPO_ROOT", self.root),
            ("EVIDENCE_DIR", self.evidence),
        ):
            patch = mock.patch.object(check, attr, value)
            patch.start()
            self.addCleanup(patch.stop)
        self.evidence.mkdir(parents=True)
        # The gate tests below must be attributable to the nested envelope
        # alone, so the two freshness steps that run regardless of the
        # manifest are stubbed out: ring2's fixture check (step 1c') reads
        # the real testbench tree, and step 1e re-derives every T1 item
        # inventory from the live tree. An empty manifest already silences
        # the citation-keyed steps (1b/1b'/1c) and the combiner/sampler
        # sidecar check (1d) finds no committed publication under the temp
        # root.
        ring2 = mock.patch.object(
            check, "verify_ring2_pex_publication", lambda manifest=None: []
        )
        ring2.start()
        self.addCleanup(ring2.stop)
        inventories = mock.patch.object(
            check,
            "inventories",
            mock.Mock(all_units=lambda: [], verify_item=lambda *args: []),
        )
        inventories.start()
        self.addCleanup(inventories.stop)

    def write(self, rel, envelope):
        path = self.evidence / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(envelope))
        return path

    def write_input(self):
        (self.root / "art").mkdir()
        (self.root / "art" / "in.gds").write_bytes(PAYLOAD)

    def test_finds_envelopes_at_any_depth_and_omits_sidecars(self):
        env = {"file": "art/in.gds", "provenance": {"input": {"content_hash": DIGEST}}}
        top = self.write("top.json", env)
        nested = self.write("sub/env.json", env)
        deeper = self.write("sub/deeper/env.json", env)
        # The 9 non-envelope sidecar kinds committed under signoff/evidence/*/
        # (requests, limits, sample sets, publications) name no input.
        self.write("sub/request.json", {"corners": {"supply_v": {"typ": [3.3]}}})
        self.write("sub/limits.json", {"min": 0.0, "max": 1.0})
        self.write("sub/sample_set.json", {"samples": [1, 2, 3]})
        self.write("sub/publication.json", {"verdict": "pass"})
        self.assertEqual(
            check.committed_envelopes(self.evidence), {top, nested, deeper}
        )

    def test_inventory_prefix_omitted_at_any_depth(self):
        env = {"file": "art/in.gds", "provenance": {"input": {"content_hash": DIGEST}}}
        # Both name an input, so only the inventory- name rule excludes them.
        self.write("inventory-units.json", env)
        self.write("sub/inventory-units.json", env)
        self.assertEqual(check.committed_envelopes(self.evidence), set())

    def test_step1_exempt_envelopes_omitted_by_name(self):
        """ITEM6/ITEM7 are exempt by NAME, not by their current payload shape.

        Both carry a synthetic repo-scoped input here, so the shape test
        alone would select them -- only the by-name exemption keeps them out.
        """
        exempt = {
            "source": {"path": "art/in.gds", "scope": "repo"},
            "provenance": {"input": {"content_hash": DIGEST}},
        }
        self.write("mc-yield/klt_yield_response.json", exempt)
        self.write("post-route/gate_klt_response.json", exempt)
        self.assertEqual(check.committed_envelopes(self.evidence), set())

    def test_repo_scoped_object_counts_and_other_scope_does_not(self):
        self.write("layout_obj.json", {"layout": {"path": "art/in.gds", "scope": "repo"}})
        self.write("def_obj.json", {"def_path": {"path": "art/in.gds", "scope": "repo"}})
        self.write("other_scope.json", {"layout": {"path": "art/in.gds", "scope": "other"}})
        self.write("empty_obj.json", {"layout": {}})
        got = check.committed_envelopes(self.evidence)
        self.assertEqual({p.name for p in got}, {"layout_obj.json", "def_obj.json"})

    def test_gate_fails_when_nested_uncited_envelope_is_stale(self):
        """The biting case (#916): a nested, uncited, STALE envelope fails.

        A fresh uncited envelope would only raise the verified count, which
        a broken (non-recursive) selector also passes -- the stale digest is
        what makes the recursion observable.
        """
        self.write_input()
        self.write(
            "sub/stale.json",
            {"file": "art/in.gds", "provenance": {"input": {"content_hash": WRONG}}},
        )
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            self.assertEqual(check.freshness_gate({}), 1)
        self.assertIn("signoff/evidence/sub/stale.json", err.getvalue())

    def test_gate_counts_nested_uncited_fresh_envelope(self):
        self.write_input()
        self.write(
            "sub/fresh.json",
            {"file": "art/in.gds", "provenance": {"input": {"content_hash": DIGEST}}},
        )
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(check.freshness_gate({}), 0)
        self.assertIn("1 cited envelope(s)", out.getvalue())


#: A miniature ratified table: two deterministic rows and one statistical
#: (`period_r1`), mirroring the real one's shape.
SYNTH_README = """# block

## Target specification (ratified 2026-07-31)

| Parameter | Target | Stretch | Status |
|---|---|---|---|
| Entropy source | **N-way array of rings**, XOR-combined | metastability hybrid | specified |
| Interface | streaming raw / conditioned | — | specified |
| Ring period under mismatch (`period_r1`) | ≤ 9.151 ns over the mismatch Monte Carlo draw | — | specified |

## After
"""

SYNTH_IDS = ["entropy_source", "interface", "period_r1"]

SYNTH_STATEMENT = {
    "rows": [
        {
            "id": "entropy_source",
            "class": "architectural",
            "reason": "a design decision, not a measured quantity",
        },
        {
            "id": "interface",
            "class": "functional",
            "reason": "deterministic logic, verified bit-exact",
        },
        {
            "id": "period_r1",
            "class": "statistical",
            "reason": "Statistical (mismatch Monte Carlo); evidenced under 6.analog.",
        },
        # dtrip_v deliberately absent: the synthetic table has one
        # statistical row, so ITEM6D_STATISTICAL_ROWS is not consulted for
        # rows the projection does not carry -- coverage against the
        # projection's own ids is the rule under test.
    ]
}


class Item6DigitalProjection(unittest.TestCase):
    """project_item6_digital_spec(): README's ratified table -> the spec
    document, id for id, cell for cell."""

    def test_projection_ids_are_pinned_against_the_committed_table(self):
        projection = check.project_item6_digital_spec(
            (ROOT / "README.md").read_text()
        )
        self.assertEqual(projection["status"], "ratified")
        self.assertEqual(
            [row["id"] for row in projection["rows"]],
            [
                "entropy_source", "raw_rate", "raw_min_entropy_per_bit", "quality",
                "conditioning", "delivered_post_conditioning_rate", "health_tests",
                "time_to_first_valid", "power", "area", "operating_envelope",
                "interface", "period_r1", "dtrip_v",
            ],
        )

    def test_committed_spec_document_is_the_current_projection(self):
        """The freshness wire: the committed document cannot drift from the
        table it renders (README edits it does not carry fail the gate)."""
        projection = check.project_item6_digital_spec(
            (ROOT / "README.md").read_text()
        )
        committed = json.loads((ROOT / check.ITEM6D_SPEC).read_text())
        self.assertEqual(committed, projection)

    def test_committed_statement_accounts_for_every_ratified_row(self):
        projection = check.project_item6_digital_spec(
            (ROOT / "README.md").read_text()
        )
        statement = json.loads((ROOT / check.ITEM6D_STATEMENT).read_text())
        self.assertEqual(
            sorted(row["id"] for row in statement["rows"]),
            sorted(row["id"] for row in projection["rows"]),
        )
        for row in statement["rows"]:
            if row["id"] in check.ITEM6D_STATISTICAL_ROWS:
                self.assertEqual(row["class"].lower(), "statistical")
                self.assertIn("6.analog", row["reason"])
            else:
                self.assertNotEqual(row["class"].lower(), "statistical")

    def test_backticked_id_and_slug_rules(self):
        projection = check.project_item6_digital_spec(SYNTH_README)
        self.assertEqual([row["id"] for row in projection["rows"]], SYNTH_IDS)
        # Cells are carried verbatim, escapes and all.
        self.assertEqual(
            projection["rows"][0]["target"], "**N-way array of rings**, XOR-combined"
        )
        self.assertEqual(projection["rows"][1]["stretch"], "—")

    def test_malformed_table_raises_rather_than_projecting_partially(self):
        bad = SYNTH_README.replace(
            "| Interface | streaming raw / conditioned | — | specified |",
            "| Interface | streaming | specified |",  # one cell short
        )
        with self.assertRaises(ValueError):
            check.project_item6_digital_spec(bad)
        with self.assertRaises(ValueError):
            check.project_item6_digital_spec("# no such heading\n")

    def test_duplicate_projected_ids_raise(self):
        bad = SYNTH_README.replace("| Interface |", "| Entropy source |", 1)
        with self.assertRaises(ValueError):
            check.project_item6_digital_spec(bad)


class Item6DigitalNotApplicable(unittest.TestCase):
    """verify_item6_digital_publication(): the 6.digital gate.

    The grader stops at the first refusal -- on this tree the spec scan's
    `not_applicable_statistical_row`, which returns before the statement's
    coverage is ever looked at -- so every check here must bite on its own:
    a stale pin, a statement row removed or duplicated *with its pin
    recomputed*, a README edit the spec document does not carry, and the
    two statistical rows classified honestly.
    """

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        patch = mock.patch.object(check, "REPO_ROOT", self.root)
        patch.start()
        self.addCleanup(patch.stop)
        self.spec_path = self.root / "signoff" / "evidence" / "item6-digital-spec.json"
        self.statement_path = (
            self.root / "signoff" / "evidence" / "item6-digital-statement.json"
        )
        self.spec_path.parent.mkdir(parents=True)
        self.readme = self.root / "README.md"
        self.readme.write_text(SYNTH_README)
        self.write_spec()
        self.write_statement(SYNTH_STATEMENT)

    def write_spec(self):
        projection = check.project_item6_digital_spec(self.readme.read_text())
        self.spec_path.write_text(json.dumps(projection, indent=2) + "\n")

    def write_statement(self, doc):
        self.statement_path.write_text(json.dumps(doc, indent=2) + "\n")

    def pin(self, path):
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()

    def manifest(self):
        return {
            "evidence": {
                "6.digital": {
                    "not_applicable": {
                        "spec": {
                            "file": "signoff/evidence/item6-digital-spec.json",
                            "content_hash": self.pin(self.spec_path),
                        },
                        "statement": {
                            "file": "signoff/evidence/item6-digital-statement.json",
                            "content_hash": self.pin(self.statement_path),
                        },
                    }
                }
            }
        }

    def test_clean_documents_pass(self):
        self.assertEqual(check.verify_item6_digital_publication(self.manifest()), [])

    def test_absent_entry_is_not_a_problem(self):
        self.assertEqual(check.verify_item6_digital_publication({}), [])
        self.assertEqual(
            check.verify_item6_digital_publication({"evidence": {}}), []
        )

    def test_missing_statement_row_fails_despite_a_fresh_pin(self):
        doc = json.loads(json.dumps(SYNTH_STATEMENT))
        doc["rows"] = [r for r in doc["rows"] if r["id"] != "interface"]
        self.write_statement(doc)
        problems = check.verify_item6_digital_publication(self.manifest())
        self.assertTrue(any("uncovered: ['interface']" in p for p in problems))

    def test_empty_statement_rows_report_every_uncovered_id_despite_a_fresh_pin(self):
        self.write_statement({"rows": []})
        problems = check.verify_item6_digital_publication(self.manifest())
        self.assertIn(f"uncovered: {SYNTH_IDS}", "\n".join(problems))

    def test_non_list_statement_rows_fail_despite_a_fresh_pin(self):
        for rows in ({}, "", 1, False, None):
            with self.subTest(rows=rows):
                self.write_statement({"rows": rows})
                problems = check.verify_item6_digital_publication(self.manifest())
                self.assertIn("'rows' must be a list", "\n".join(problems))

    def test_duplicate_statement_row_fails_despite_a_fresh_pin(self):
        doc = json.loads(json.dumps(SYNTH_STATEMENT))
        doc["rows"].append(dict(doc["rows"][0]))
        self.write_statement(doc)
        problems = check.verify_item6_digital_publication(self.manifest())
        self.assertTrue(any("duplicated: ['entropy_source']" in p for p in problems))

    def test_unknown_statement_row_fails(self):
        doc = json.loads(json.dumps(SYNTH_STATEMENT))
        doc["rows"][1]["id"] = "no_such_row"
        self.write_statement(doc)
        problems = check.verify_item6_digital_publication(self.manifest())
        self.assertTrue(any("unknown: ['no_such_row']" in p for p in problems))

    def test_empty_class_or_reason_fails(self):
        doc = json.loads(json.dumps(SYNTH_STATEMENT))
        doc["rows"][0]["reason"] = "   "
        self.write_statement(doc)
        problems = check.verify_item6_digital_publication(self.manifest())
        self.assertTrue(any("nonempty string id, class and reason" in p for p in problems))

    def test_statistical_row_must_be_classified_statistical(self):
        doc = json.loads(json.dumps(SYNTH_STATEMENT))
        doc["rows"][2]["class"] = "corner-bounded"  # period_r1, one of the two
        self.write_statement(doc)
        problems = check.verify_item6_digital_publication(self.manifest())
        self.assertTrue(any("statistical rows but is classified" in p for p in problems))

    def test_statistical_row_reason_must_name_the_analog_citation(self):
        doc = json.loads(json.dumps(SYNTH_STATEMENT))
        doc["rows"][2]["reason"] = "Statistical, but evidenced elsewhere."
        self.write_statement(doc)
        problems = check.verify_item6_digital_publication(self.manifest())
        self.assertTrue(any("evidenced under 6.analog" in p for p in problems))

    def test_deterministic_row_may_not_claim_to_be_statistical(self):
        doc = json.loads(json.dumps(SYNTH_STATEMENT))
        doc["rows"][1]["class"] = "statistical"
        self.write_statement(doc)
        problems = check.verify_item6_digital_publication(self.manifest())
        self.assertTrue(any("claims to be statistical" in p for p in problems))

    def test_stale_spec_pin_fails_by_name(self):
        manifest = self.manifest()  # pins the bytes on disk right now
        self.spec_path.write_text(
            json.dumps({"status": "ratified", "rows": [{"id": "x"}]}, indent=2) + "\n"
        )
        problems = check.verify_item6_digital_publication(manifest)
        self.assertTrue(any(p.startswith("spec: STALE") for p in problems))
        self.assertTrue(any("is not the current projection" in p for p in problems))

    def test_stale_statement_pin_fails_by_name(self):
        manifest = self.manifest()
        self.statement_path.write_text('{"rows": []}\n')
        problems = check.verify_item6_digital_publication(manifest)
        self.assertTrue(any(p.startswith("statement: STALE") for p in problems))

    def test_readme_edit_the_spec_does_not_carry_fails(self):
        self.readme.write_text(
            SYNTH_README.replace("streaming raw / conditioned", "packet interface")
        )
        # The spec document's pin is still fresh (the file did not change);
        # only the projection comparison can catch the drift.
        problems = check.verify_item6_digital_publication(self.manifest())
        self.assertTrue(any("is not the current projection" in p for p in problems))

    def test_missing_documents_fail_by_name(self):
        manifest = self.manifest()
        self.spec_path.unlink()
        self.statement_path.unlink()
        problems = check.verify_item6_digital_publication(manifest)
        self.assertTrue(any("item6-digital-spec.json is missing" in p for p in problems))
        self.assertTrue(any("item6-digital-statement.json is missing" in p for p in problems))

    def test_entry_without_the_form_is_rejected(self):
        problems = check.verify_item6_digital_publication(
            {"evidence": {"6.digital": {"file": "signoff/evidence/x.json"}}}
        )
        self.assertEqual(len(problems), 1)
        self.assertIn("not_applicable", problems[0])


if __name__ == "__main__":
    unittest.main()
