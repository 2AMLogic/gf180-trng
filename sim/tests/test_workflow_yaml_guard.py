#!/usr/bin/env python3
"""Hold sim/tools/workflow_yaml_guard.py to its contract (issues #1003, #1011).

The guard is a line scanner, not a YAML parser: it flags the one defect
class measured in issue #1003 -- a plain ``name:`` mapping value containing
``": "`` (or ending in ``:``), which every YAML parser reads as a nested
mapping and which therefore turns the workflow into a zero-job startup
failure -- while leaving quoted values, block scalars, flow collections,
comments and URL colons alone. Issue #1011 extends the cover: a plain
value that ends in a block-scalar indicator is a defect, not a header,
and nested sequence dashes bound blocks at the key's column. Issue
#1015 pins the docstring's measured exceptions: three block-header
shapes (explicit-key, anchored, tagged) report a finding on a document
that parses -- unrepresentable in a working Actions workflow, so
documented and pinned, not fixed. Every case
feeds a literal document to findings(); nothing depends on the state of
the real tree except the final guard-on-this-tree case. Stdlib only;
the PyYAML cross-checks skip when it is not installed.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR / "tools"))

import workflow_yaml_guard as guard  # noqa: E402

try:
    import yaml  # PyYAML is not a repo dependency; cross-checks are opt-in
except ImportError:
    yaml = None

OFFENDING = ("jobs:\n"
             "  t:\n"
             "    steps:\n"
             "      - name: Self-checks (the one check list: sim/check.sh ci)\n")


class Findings(unittest.TestCase):
    def finding(self, doc: str, path: str = "wf.yml") -> str:
        found = guard.findings(doc, path)
        self.assertEqual(len(found), 1, found)
        return found[0]

    def clean(self, doc: str, path: str = "wf.yml") -> None:
        self.assertEqual(guard.findings(doc, path), [])

    # -- the defect class -------------------------------------------------

    def test_list_item_name_with_interior_colon_space_is_flagged(self):
        f = self.finding(OFFENDING)
        self.assertTrue(f.startswith("wf.yml:4:"), f)
        self.assertIn("- name", f)

    def test_top_level_name_is_flagged(self):
        self.assertEqual(len(guard.findings("name: TRNG (the: thing)\n")), 1)

    def test_trailing_colon_is_flagged(self):
        self.assertEqual(len(guard.findings("- name: Steps:\n")), 1)

    def test_name_under_with_is_flagged(self):
        doc = ("steps:\n"
               "  - uses: x\n"
               "    with:\n"
               "      name: bad: value\n")
        f = self.finding(doc)
        self.assertTrue(f.startswith("wf.yml:4:"), f)

    def test_finding_names_line_and_value(self):
        f = self.finding("name: a: b\n", "ci.yml")
        self.assertTrue(f.startswith("ci.yml:1:"), f)
        self.assertIn("a: b", f)

    # -- non-defects that must not false-positive -------------------------

    def test_double_quoted_value_is_clean(self):
        self.clean('- name: "Self-checks (check list: sim/check.sh ci)"\n')

    def test_single_quoted_value_is_clean(self):
        self.clean("- name: 'Self-checks (check list: sim/check.sh ci)'\n")

    def test_trailing_comment_is_clean(self):
        self.clean("- name: Build # note: this does: stuff\n")

    def test_comment_only_line_is_clean(self):
        self.clean("#   - name: not: a real step\n")

    def test_url_colon_is_clean(self):
        self.clean("name: see http://example.com/x\n")

    def test_colon_without_space_is_clean(self):
        self.clean("name: a:b\n")

    def test_flow_value_is_clean(self):
        self.clean("name: {a: b}\n")

    def test_empty_value_is_clean(self):
        self.clean("name:\n")

    def test_longer_key_is_ignored(self):
        # `display-name:` and `run-name:` are different keys; so is `name:foo`.
        self.clean("display-name: a: b\n")
        self.clean("run-name: a: b\n")
        self.clean("name:foo: bar\n")

    def test_block_scalar_name_value_is_clean(self):
        self.clean("name: |\n  a: b\n")

    def test_line_inside_block_scalar_is_clean(self):
        doc = ("      - name: Build\n"
               "        run: |\n"
               "          name: looks: like the trap\n"
               "          make all\n")
        self.clean(doc)

    def test_dedent_exits_block_scalar(self):
        doc = ("steps:\n"
               "  - name: Build\n"
               "    run: |\n"
               "      name: inside: block\n"
               "  - name: a: b\n")
        self.assertEqual(len(guard.findings(doc)), 1)

    def test_sequence_item_block_value_is_clean(self):
        doc = ("env:\n"
               "  - |\n"
               "    A: B: C\n")
        self.clean(doc)

    # -- block headers on dash-led steps (run: first, name: after) --------

    def test_name_after_dash_led_block_scalar_is_flagged(self):
        # `- run: |` before `name:`: the sibling key lives at the key's
        # column, not the dash's, so it ends the block and is scanned.
        doc = ("jobs:\n"
               "  j:\n"
               "    steps:\n"
               "      - run: |\n"
               "          echo\n"
               "        name: Self-checks (the one check list: sim/check.sh ci)\n")
        f = self.finding(doc)
        self.assertTrue(f.startswith("wf.yml:6:"), f)

    def test_name_after_folded_dash_led_block_is_flagged(self):
        doc = ("steps:\n"
               "      - run: >\n"
               "          echo\n"
               "        name: check list: sim/check.sh ci\n")
        self.assertEqual(len(guard.findings(doc)), 1)

    def test_name_after_chomped_dash_led_block_is_flagged(self):
        doc = ("steps:\n"
               "      - run: |-\n"
               "          echo\n"
               "        name: Steps:\n")
        self.assertEqual(len(guard.findings(doc)), 1)

    def test_name_after_indicator_pair_dash_led_block_is_flagged(self):
        doc = ("steps:\n"
               "      - run: >-\n"
               "          echo\n"
               "        name: Steps:\n")
        self.assertEqual(len(guard.findings(doc)), 1)

    def test_block_header_with_trailing_comment_stays_clean(self):
        # `run: | # note` is a valid block header: its content lines are
        # literal, not mapping lines to scan.
        doc = ("jobs:\n"
               "  j:\n"
               "    steps:\n"
               "      - name: ok\n"
               "        run: | # note\n"
               "          name: looks: trap\n")
        self.clean(doc)

    def test_chomped_header_with_trailing_comment_stays_clean(self):
        doc = ("      - name: ok\n"
               "        run: >- # note\n"
               "          name: looks: trap\n")
        self.clean(doc)

    def test_bare_dash_block_still_bounds_at_dash_indent(self):
        # A bare `- |` item is bounded by the dash column (unchanged); the
        # next item at the dash indent is scanned and flagged.
        doc = ("env:\n"
               "  - |\n"
               "    A: B: C\n"
               "  - name: a: b\n")
        f = self.finding(doc)
        self.assertTrue(f.startswith("wf.yml:4:"), f)

    # -- plain values that END in a block indicator (issue #1011) ---------

    def test_name_value_ending_in_literal_bar_is_flagged(self):
        # The header decision is made from the value after the FIRST colon
        # (the key's own), so `build a: |` is a plain value containing
        # ": ", not a block header that hides the line.
        f = self.finding("name: build a: |\non: push\n")
        self.assertTrue(f.startswith("wf.yml:1:"), f)

    def test_name_value_ending_in_folded_gt_is_flagged(self):
        self.assertEqual(len(guard.findings("name: build a: >\non: push\n")), 1)

    def test_name_value_ending_in_chomped_bar_is_flagged(self):
        self.assertEqual(len(guard.findings("name: build a: |-\non: push\n")), 1)

    def test_step_name_value_ending_in_bar_is_flagged(self):
        doc = ("jobs:\n"
               "  j:\n"
               "    steps:\n"
               "      - name: a: |\n"
               "        run: echo\n")
        f = self.finding(doc)
        self.assertTrue(f.startswith("wf.yml:4:"), f)

    def test_indicator_ending_line_is_not_a_block_header_for_other_keys(self):
        # A non-name key with the same trailing shape is not a header
        # either; its body is scanned, and a defective `name:` inside it
        # is flagged (the document cannot parse either way).
        doc = ("run: echo: |\n"
               "  name: a: b\n")
        self.assertEqual(len(guard.findings(doc)), 1)

    # -- nested sequence dashes (issue #1011) ------------------------------

    def test_nested_dash_run_block_is_bounded_by_key_column(self):
        # `- - run: |`: the block is bounded by the key's column (after
        # every dash), so the sibling `name:` ends it and is scanned.
        doc = ("a:\n"
               "  - - run: |\n"
               "        echo\n"
               "      name: x: y\n")
        f = self.finding(doc)
        self.assertTrue(f.startswith("wf.yml:4:"), f)

    def test_nested_dash_name_is_flagged(self):
        self.assertEqual(len(guard.findings("a:\n  - - name: x: y\n")), 1)

    def test_nested_bare_dash_block_content_is_clean(self):
        # `- - |`: the bare item's block is bounded by the innermost
        # dash's column; its literal content is not scanned.
        doc = ("a:\n"
               "  - - |\n"
               "        name: x: y\n")
        self.clean(doc)

    def test_quoted_key_block_header_still_opens_block(self):
        # `"a: b": |` carries its own colons; recognized by shape so the
        # body stays literal and the document (which parses) stays clean.
        doc = ('"a: b": |\n'
               '  name: x: y\n')
        self.clean(doc)

    def test_flow_key_block_header_still_opens_block(self):
        doc = ("{a: b}: |\n"
               "  name: x: y\n")
        self.clean(doc)

    # -- documented exceptions to the soundness claim (issue #1015) -------

    def test_explicit_key_block_scalar_is_a_documented_exception(self):
        # `? a: b` / `: |`: the value line has no key text, so KEY_BLOCK
        # cannot match it; the block body is scanned and its `name:` line
        # is flagged even though the document parses. No Actions key is a
        # complex node, so the shape is unrepresentable in a working
        # workflow: pinned as a documented exception, not fixed.
        doc = "? a: b\n: |\n  name: x: y\n"
        f = self.finding(doc)
        self.assertTrue(f.startswith("wf.yml:3:"), f)

    def test_anchored_block_scalar_is_a_documented_exception(self):
        # `a: &anc |`: the indicator is not the value's first token, so
        # the line is not recognised as a header; the block body is
        # scanned and flagged even though the document parses. Anchors
        # are not accepted in workflow files, so the shape is
        # unrepresentable in a working workflow: pinned, not fixed.
        doc = "a: &anc |\n  name: x: y\n"
        f = self.finding(doc)
        self.assertTrue(f.startswith("wf.yml:2:"), f)

    def test_tagged_block_scalar_is_a_documented_exception(self):
        # `a: !!str |`: as with the anchored shape, the indicator is not
        # the value's first token; the body is scanned and flagged even
        # though the document parses. Tags are not accepted in workflow
        # files either: pinned, not fixed.
        doc = "a: !!str |\n  name: x: y\n"
        f = self.finding(doc)
        self.assertTrue(f.startswith("wf.yml:2:"), f)


@unittest.skipUnless(yaml, "PyYAML not installed (not a repo dependency)")
class PyYamlAgreement(unittest.TestCase):
    """Cross-check the issue-#1011 shapes against a real parser.

    PyYAML is present on some hosts but is not a repo dependency, so this
    class skips rather than fails when it is absent; the Findings cases
    above carry the contract on their own. The issue-#1015 documented
    exceptions live here too: each parses, unlike the defect shapes, and
    that half of the pin is what PyYAML contributes.
    """

    DEFECT_DOCS = [
        "name: build a: |\non: push\n",
        "name: build a: >\non: push\n",
        "name: build a: |-\non: push\n",
        "jobs:\n  j:\n    steps:\n      - name: a: |\n        run: echo\n",
        "a:\n  - - run: |\n        echo\n      name: x: y\n",
        "a:\n  - - name: x: y\n",
    ]
    CLEAN_DOCS = [
        "name: |\n  a: b\n",
        "steps:\n  - run: |\n      echo\n    name: ok\n",
        '"a: b": |\n  name: x: y\n',
        "{a: b}: |\n  name: x: y\n",
        "a:\n  - - |\n        name: x: y\n",
    ]
    EXCEPTION_DOCS = [
        "? a: b\n: |\n  name: x: y\n",
        "a: &anc |\n  name: x: y\n",
        "a: !!str |\n  name: x: y\n",
    ]

    def test_defect_shapes_do_not_parse_and_are_flagged(self):
        for doc in self.DEFECT_DOCS:
            with self.subTest(doc=doc):
                with self.assertRaises(yaml.YAMLError):
                    yaml.compose(doc)
                self.assertEqual(len(guard.findings(doc, "wf.yml")), 1)

    def test_clean_shapes_parse_and_stay_clean(self):
        # yaml.compose is the parse oracle: it builds the node tree without
        # constructing Python objects, so a valid flow-collection key
        # (`{a: b}: |`, unhashable for safe_load) still counts as parsing.
        for doc in self.CLEAN_DOCS:
            with self.subTest(doc=doc):
                yaml.compose(doc)
                self.assertEqual(guard.findings(doc, "wf.yml"), [])

    def test_exception_shapes_parse_but_are_flagged(self):
        # The issue-#1015 documented exceptions: each document parses
        # (compose succeeds) and still reports exactly one finding -- the
        # opposite half of the DEFECT_DOCS contract.
        for doc in self.EXCEPTION_DOCS:
            with self.subTest(doc=doc):
                yaml.compose(doc)
                self.assertEqual(len(guard.findings(doc, "wf.yml")), 1)


class Main(unittest.TestCase):
    def test_this_tree_is_clean(self):
        self.assertEqual(guard.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
