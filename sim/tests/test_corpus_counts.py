#!/usr/bin/env python3
"""Hold sim/tools/corpus_counts.py to both halves of its contract (#320).

The guard keeps README.md's corpus totals (decision records,
characterization summaries, evidence records) in step with the tree. Each
test here is a pair in the style of layout/tests/test_verify.py: a correct
figure must pass, and a stale, missing or malformed one must fail. Every
case runs over a synthetic tree in a temporary directory, so nothing here
depends on the size of the real corpus. Stdlib only; no PDK, no ngspice.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
TOOL = SIM_DIR / "tools" / "corpus_counts.py"
sys.path.insert(0, str(SIM_DIR / "tools"))

import corpus_counts as cc  # noqa: E402

GOOD_README = """\
# demo

As of this writing the repository contains
[three decision records](spec/decision-records/), and two characterization
summaries (`sim/characterization-*.md`) resting on 4 append-only evidence
records under [`sim/records/`](sim/records/).
"""


def build_tree(root: Path, readme: str = GOOD_README,
               sim_readme: str | None = None) -> None:
    """A minimal corpus: 3 DR ids, 2 summaries, 4 records."""
    dr = root / "spec" / "decision-records"
    dr.mkdir(parents=True)
    for name in ("DR-0001-a.md", "DR-0002-b.md", "DR-0002-c.md",
                 "DR-0003-d.md", "TEMPLATE.md", "README.txt"):
        (dr / name).write_text("x\n")
    sim = root / "sim"
    (sim / "records" / "raw" / "run-01").mkdir(parents=True)
    for i in range(4):
        (sim / "records" / f"rec-{i:02d}.md").write_text("x\n")
    (sim / "records" / "raw" / "run-01" / "nested.md").write_text("x\n")
    (sim / "records" / "notes.txt").write_text("x\n")
    (sim / "characterization-a.md").write_text("x\n")
    (sim / "characterization-b.md").write_text("x\n")
    (sim / "nested").mkdir()
    (sim / "nested" / "characterization-c.md").write_text("x\n")
    (root / "README.md").write_text(readme)
    if sim_readme is not None:
        (sim / "README.md").write_text(sim_readme)


def snapshot(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*")) if p.is_file()
    }


class TreeCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()


class DeriveCounts(TreeCase):
    def test_populations(self) -> None:
        build_tree(self.root)
        # Duplicate DR-0002 counts once; TEMPLATE.md, nested raw .md,
        # non-.md files and the nested characterization file do not count.
        self.assertEqual(cc.derive_counts(self.root), {
            cc.DECISION: 3, cc.SUMMARIES: 2, cc.EVIDENCE: 4})

    def test_adding_one_file_moves_only_its_category(self) -> None:
        build_tree(self.root)
        base = cc.derive_counts(self.root)
        additions = {
            cc.DECISION: self.root / "spec/decision-records/DR-0004-e.md",
            cc.SUMMARIES: self.root / "sim/characterization-z.md",
            cc.EVIDENCE: self.root / "sim/records/rec-99.md",
        }
        for category, path in additions.items():
            with self.subTest(category=category):
                path.write_text("x\n")
                got = cc.derive_counts(self.root)
                expected = dict(base)
                expected[category] += 1
                self.assertEqual(got, expected)
                path.unlink()


class ParseNumber(unittest.TestCase):
    def test_accepts(self) -> None:
        cases = {"975": 975, "1,024": 1024, "twelve": 12, "twenty": 20,
                 "twenty-one": 21, "Ninety-Nine": 99, "[twenty-six": 26}
        for tok, want in cases.items():
            with self.subTest(tok=tok):
                self.assertEqual(cc.parse_number(tok), want)

    def test_rejects(self) -> None:
        for tok in ("the", "no", "real", "twenty-", "twelve-one",
                    "twenty-zero", "9x"):
            with self.subTest(tok=tok):
                self.assertIsNone(cc.parse_number(tok))


class CheckText(unittest.TestCase):
    COUNTS = {cc.DECISION: 3, cc.SUMMARIES: 2, cc.EVIDENCE: 4}

    def check(self, text: str, required: bool = True) -> list[str]:
        return cc.check_text("README.md", text, self.COUNTS, required)

    def test_correct_counts_pass(self) -> None:
        self.assertEqual(self.check(GOOD_README), [])

    def test_digits_and_spelled_out_both_parse(self) -> None:
        text = ("3 decision records, two characterization summaries and "
                "four evidence records")
        self.assertEqual(self.check(text), [])

    def test_each_wrong_count_fails_independently(self) -> None:
        stale = {
            cc.DECISION: GOOD_README.replace("three decision",
                                             "twenty-one decision"),
            cc.SUMMARIES: GOOD_README.replace("two characterization",
                                              "twelve characterization"),
            cc.EVIDENCE: GOOD_README.replace("4 append-only",
                                             "975 append-only"),
        }
        for category, text in stale.items():
            with self.subTest(category=category):
                self.assertNotEqual(text, GOOD_README)
                problems = self.check(text)
                self.assertEqual(len(problems), 1, problems)
                self.assertIn(category, problems[0])
                self.assertIn("README.md", problems[0])
                self.assertIn(f"derived {self.COUNTS[category]}",
                              problems[0])

    def test_missing_required_claim_fails(self) -> None:
        text = GOOD_README.replace("three decision records", "the records")
        problems = self.check(text)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn(cc.DECISION, problems[0])
        self.assertIn("missing/unparseable", problems[0])

    def test_malformed_required_claim_fails(self) -> None:
        text = GOOD_README.replace("three decision", "thre decision")
        problems = self.check(text)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("missing/unparseable", problems[0])

    def test_non_number_phrases_are_not_claims(self) -> None:
        text = GOOD_README + (
            "\nThe job writes no evidence records; see the decision records."
            "\nThe gate-level sweep is fifteen records.\n")
        self.assertEqual(self.check(text), [])

    def test_optional_document_absent_claim_passes(self) -> None:
        self.assertEqual(self.check("APPEND-ONLY evidence records\n",
                                    required=False), [])

    def test_optional_document_stale_repeat_fails(self) -> None:
        problems = self.check("There are 975 evidence records.\n",
                              required=False)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("quoted 975, derived 4", problems[0])


class Cli(TreeCase):
    def run_tool(self, *args: str) -> subprocess.CompletedProcess:
        # Run from an unrelated directory: the tool must not depend on cwd.
        with tempfile.TemporaryDirectory() as elsewhere:
            return subprocess.run(
                [sys.executable, str(TOOL), "--root", str(self.root), *args],
                cwd=elsewhere, capture_output=True, text=True, check=False)

    def test_agreement_exits_zero_and_writes_nothing(self) -> None:
        build_tree(self.root, sim_readme="APPEND-ONLY evidence records\n")
        before = snapshot(self.root)
        proc = self.run_tool("--check")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("OK", proc.stdout)
        self.assertEqual(snapshot(self.root), before)

    def test_mismatch_exits_nonzero_with_diagnostic(self) -> None:
        build_tree(self.root,
                   sim_readme="The corpus holds 5 evidence records.\n")
        before = snapshot(self.root)
        proc = self.run_tool("--check")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("sim/README.md: evidence records: quoted 5, derived 4",
                      proc.stderr)
        self.assertEqual(snapshot(self.root), before)

    def test_missing_claim_exits_nonzero(self) -> None:
        build_tree(self.root, readme="# demo\nNo totals here.\n")
        proc = self.run_tool("--check")
        self.assertEqual(proc.returncode, 1)
        for category in cc.CATEGORIES:
            self.assertIn(f"README.md: {category}: quoted missing/unparseable",
                          proc.stderr)

    def test_without_check_reports_only(self) -> None:
        build_tree(self.root, readme="# demo\n")
        proc = self.run_tool()
        self.assertEqual(proc.returncode, 0)
        self.assertIn("evidence records: 4", proc.stdout)


class RepositoryReadme(unittest.TestCase):
    def test_committed_readme_agrees_with_tree(self) -> None:
        counts, problems = cc.check_tree(cc.REPO_ROOT)
        self.assertEqual(problems, [], counts)


if __name__ == "__main__":
    unittest.main()
