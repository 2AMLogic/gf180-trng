#!/usr/bin/env python3
"""The committed observed-activity records and companion document are
internally consistent and current (#453). Stdlib only; reads committed
records, needs no PDK or simulator."""

from __future__ import annotations

import copy
import json
import re
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


def perturb(text: str, snippet: str, replacement: str) -> str:
    """Replace one pinned snippet in a hard-wrapped document.

    The snippet is matched across line wrapping (the tool flattens whitespace
    before searching), so the sentence it lands in may be re-wrapped; nothing
    else in the document moves.
    """
    pat = re.compile(r"\s+".join(re.escape(w) for w in snippet.split()))
    new, n = pat.subn(lambda _m: replacement, text, count=1)
    if n != 1:
        raise AssertionError(f"snippet is not in the document exactly once: {snippet!r}")
    return new


def bump_first_digit(snippet: str) -> str:
    """The snippet with its first digit changed -- a hand-perturbed figure."""
    m = re.search(r"\d", snippet)
    if m is None:
        raise AssertionError(f"pinned snippet quotes no figure: {snippet!r}")
    i = m.start()
    return snippet[:i] + str((int(snippet[i]) + 1) % 10) + snippet[i + 1:]


class ProseAgreesWithTheGeneratedBlockTests(unittest.TestCase):
    """Sections 0, 4 and 5 restate figures the generated block holds, and
    nothing read those sentences until #883 -- so two re-captures left a
    document saying `348.2 uW` ninety lines above a table saying `339.35`."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.fam = apc.load_family()
        cls.pins = apc.prose_pins(cls.fam)
        cls.texts = {p: p.read_text() for p in cls.pins}

    def test_committed_documents_pass(self):
        self.assertEqual(apc.document_problems(self.fam, self.texts), [])

    def test_every_pinned_prose_figure_is_caught_when_perturbed(self):
        # One subTest per pinned figure: the guard is only worth having if
        # each pin is load-bearing, not merely present.
        self.assertGreaterEqual(sum(len(v) for v in self.pins.values()), 15)
        for path, pins in self.pins.items():
            for label, snippet in pins:
                with self.subTest(document=path.name, figure=label):
                    texts = dict(self.texts)
                    texts[path] = perturb(texts[path], snippet, bump_first_digit(snippet))
                    problems = apc.document_problems(self.fam, texts)
                    self.assertTrue(
                        any(label in p for p in problems),
                        f"perturbing {label} in {path.name} was not reported; got {problems}")

    def test_a_figure_only_inside_the_generated_block_does_not_satisfy_its_pin(self):
        # Both ends of section 0.1's ratio range also stand in the block's
        # ratio column. Deleting the sentence that restates them must still
        # fail: a generated table is not a finding.
        label, snippet = next((lab, s) for lab, s in self.pins[apc.DOC]
                              if "ratio range" in lab)
        texts = dict(self.texts)
        texts[apc.DOC] = perturb(texts[apc.DOC], snippet, "of the uniform figure")
        problems = apc.document_problems(self.fam, texts)
        self.assertTrue(any(label in p for p in problems))
        body = texts[apc.DOC].split(apc.BEGIN, 1)[1].split(apc.END, 1)[0]
        for bound in re.findall(r"\d\.\d+", snippet):
            self.assertIn(bound, body)

    def test_pins_are_derived_from_the_records_not_written_down(self):
        # Move a figure in the records: the expected snippet must move with it
        # and the unchanged document must fail. This is what makes the fix
        # rule-based rather than a second snapshot -- the next re-capture
        # (PR #878 is one) fails the document instead of outdating it.
        before = {lab: s for lab, s in self.pins[apc.DOC]}
        fam = apc.load_family()
        fam[apc.BINDING].values["uniform_clock_w"] *= 1.05
        after = {lab: s for lab, s in apc.prose_pins(fam)[apc.DOC]}
        moved = [lab for lab in before if before[lab] != after[lab]]
        self.assertEqual(moved, ["§4 clock group at the binding corner"])
        problems = apc.document_problems(fam, self.texts)
        self.assertTrue(any("clock group" in p for p in problems), problems)

    def test_section_2_historical_pin_counts_are_left_alone(self):
        # The `5371` figures in section 2 are quotes from an earlier bring-up
        # run on the DEF of the day, explicitly marked as such. The guard
        # pins the current count without touching them.
        doc = self.texts[apc.DOC]
        self.assertIn("5371", doc)
        self.assertNotIn("5371", "".join(s for _l, s in self.pins[apc.DOC]))
        self.assertEqual(apc.document_problems(self.fam, self.texts), [])

    def test_fewer_digits_than_the_generator_prints_is_accepted(self):
        # The documented tolerance: a pin formats the live value to the digits
        # its sentence quotes. Section 5 quotes the rollup's one decimal for a
        # term the generated block prints to two -- derived, not written down
        # here, or this test would be the snapshot the guard exists to prevent.
        term = next(s for lab, s in self.pins[apc.DOC] if "ratified digital term" in lab)
        self.assertRegex(term, r"ratified \d+\.\d uW$")
        self.assertIn(f"{apc.rollup_figures()['digital_uw']:.1f} uW", term)
        uniform_uw = self.fam[apc.BINDING].v("uniform_total_w") * 1e6
        self.assertIn(f"{uniform_uw:.2f}", apc.markdown(self.fam))
        self.assertEqual(apc.document_problems(self.fam, self.texts), [])


class NoRecordFamilyIsNamedInProseTests(unittest.TestCase):
    """Section 1 states the selection rule the tool implements instead of
    naming a family. The filed defect in #883 was exactly such a pointer,
    annotated `(current)` while naming the oldest of three families."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.fam = apc.load_family()
        cls.doc = apc.DOC.read_text()

    def test_the_committed_document_names_none(self):
        self.assertIsNone(apc.FAMILY_LITERAL.search(self.doc))

    def test_a_reintroduced_family_literal_is_caught(self):
        for lit in ("2026-11-09-digital-sta-activity-01",
                    "sim/records/2026-10-10-digital-sta-activity-{16..30}.md` (current)"):
            with self.subTest(literal=lit):
                texts = {apc.DOC: self.doc.replace(
                    "One record per corner, under", f"One record per corner, {lit}, under")}
                problems = apc.document_problems(self.fam, texts)
                self.assertTrue(any("names the record family" in p for p in problems), problems)

    def test_section_1_states_the_rule_and_annotates_no_pointer(self):
        method = apc._flat(self.doc.split("## 1. Method", 1)[1].split("## 2.", 1)[0])
        # The rule `load_family` implements, stated where the pointer was.
        self.assertIn("the newest *valid* record per corner is the one read", method)
        self.assertIn("trng_top.def", method)
        self.assertIn("trng_top.pnr.v", method)
        # Section 6 still mentions `(current)` when describing the defect this
        # guard closed; what must not come back is the annotation itself, on a
        # pointer in section 1.
        self.assertNotIn("(current)", method)


if __name__ == "__main__":
    unittest.main()
