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


if __name__ == "__main__":
    unittest.main()
