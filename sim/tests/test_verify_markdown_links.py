#!/usr/bin/env python3
"""Hold sim/tools/verify_markdown_links.py to its documented contract (#570).

Most cases feed a synthetic document and file listing to the core
(`check_documents`), so nothing here depends on the state of the real tree;
the CLI is exercised against a throwaway git repository. Stdlib only.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR / "tools"))

import verify_markdown_links as vml  # noqa: E402

# A fake tree: the document under test lives at docs/guide.md.
FILES = ["docs/guide.md", "docs/other.md", "spec/dr/DR-0001-x.md",
         "sim/tools/tool.py", "README.md", "docs/my file.md"]


def broken(doc_text: str, doc: str = "docs/guide.md", files=FILES,
           allowlist=None) -> list[tuple[int, str]]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / doc).parent.mkdir(parents=True, exist_ok=True)
        (root / doc).write_text(textwrap.dedent(doc_text), encoding="utf-8")
        findings = vml.check_documents(root, [doc], files,
                                       {} if allowlist is None else allowlist)
    return [(f.line, f.target) for f in findings]


class InlineLinks(unittest.TestCase):
    def test_good_relative_links_pass(self):
        self.assertEqual(broken("""\
            See [other](other.md), [the DR](../spec/dr/DR-0001-x.md),
            [a dir](../sim/tools/), [root](/README.md) and ![img](./other.md).
            [titled](other.md "Title") and [angled](<my file.md>), [enc](my%20file.md).
            """), [])

    def test_broken_relative_link_is_reported_with_line(self):
        self.assertEqual(broken("ok [a](other.md)\n\nbad [b](missing.md)\n"),
                         [(3, "missing.md")])

    def test_repo_root_relative_written_as_doc_relative_is_reported(self):
        # The #570 bug: a path written from the repo root inside a subdirectory.
        self.assertEqual(broken("[DR](spec/dr/DR-0001-x.md)\n"),
                         [(1, "spec/dr/DR-0001-x.md")])

    def test_fragment_and_query_are_dropped_but_file_must_exist(self):
        self.assertEqual(broken("[a](other.md#sec) [b](other.md?x=1) [c](gone.md#sec)\n"),
                         [(1, "gone.md#sec")])

    def test_external_and_anchor_targets_are_ignored(self):
        self.assertEqual(broken("""\
            [w](https://example.com/x.md) [m](mailto:a@b.c) [p](//host/x)
            [anchor](#section) [ftp](ftp://h/f)
            """), [])

    def test_path_above_repo_root_is_reported(self):
        self.assertEqual(broken("[up](../../README.md)\n"), [(1, "../../README.md")])


class ReferenceStyle(unittest.TestCase):
    def test_good_and_broken_definitions(self):
        self.assertEqual(broken("""\
            Uses [DR-1] and [gone].

            [DR-1]: ../spec/dr/DR-0001-x.md
            [gone]: spec/dr/DR-0001-x.md "title"
            """), [(4, "spec/dr/DR-0001-x.md")])

    def test_prose_opening_with_bracket_colon_is_not_a_definition(self):
        self.assertEqual(broken("""\
            Same correctability as [DR-0009], [DR-0021] and
            [DR-0022]: it fixes what a record is.
            """), [])

    def test_footnote_definition_is_not_a_link(self):
        self.assertEqual(broken("text[^n]\n\n[^n]: The footnote body.\n"), [])


class CodeIsIgnored(unittest.TestCase):
    def test_fenced_code_block_is_skipped(self):
        self.assertEqual(broken("""\
            ```markdown
            [x](missing-in-backtick-fence.md)
            [ref]: missing-ref.md
            ```
            ~~~~
            [y](missing-in-tilde-fence.md)
            ```
            still inside the tilde fence [z](missing.md)
            ~~~~
            after [real](missing-after.md)
            """), [(10, "missing-after.md")])

    def test_inline_code_span_is_skipped(self):
        self.assertEqual(broken("Write `[x](missing.md)` or ``[y](gone.md)``.\n"), [])


class Selection(unittest.TestCase):
    def test_excluded_trees_are_not_scanned(self):
        docs = vml.select_documents(["sim/records/r.md", ".loom/a.md", "sim/x.md",
                                     "README.md", "sim/x.py", "spec/Y.MD"])
        self.assertEqual(docs, ["README.md", "sim/x.md", "spec/Y.MD"])

    def test_allowlist_suppresses_only_its_pair(self):
        allow = {("docs/guide.md", "dry-runs/"): "reason"}
        self.assertEqual(broken("[d](dry-runs/) [e](other-missing/)\n", allowlist=allow),
                         [(1, "other-missing/")])

    def test_untracked_file_does_not_satisfy_a_link(self):
        # Only tracked paths count; the document itself exists on disk here
        # but is left out of the listing.
        self.assertEqual(broken("[self](guide.md)\n", files=["docs/other.md"]),
                         [(1, "guide.md")])

    def test_real_allowlist_is_truthful(self):
        files = set(vml.tracked_files(vml.ROOT))
        present = vml._existing(files)
        for (doc, target), reason in vml.ALLOWLIST.items():
            self.assertTrue(reason.strip(), f"{doc}: allowlist entry needs a reason")
            self.assertIn(doc, files, f"{doc}: allowlisted document is not tracked")
            self.assertNotIn(vml.resolve(doc, target), present,
                             f"{doc} -> {target} now resolves; drop the allowlist entry")
            text = (vml.ROOT / doc).read_text(encoding="utf-8")
            self.assertIn(target, [t for _, t in vml.link_targets(text)],
                          f"{doc} no longer links {target}; drop the allowlist entry")


class Cli(unittest.TestCase):
    def test_exit_codes_and_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git = ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t"]
            subprocess.run(git[:3] + ["init", "-q"], check=True)
            (root / "docs").mkdir()
            (root / "docs" / "a.md").write_text("[b](b.md)\n")
            (root / "docs" / "b.md").write_text("# b\n")
            (root / "sim" / "records").mkdir(parents=True)
            (root / "sim" / "records" / "r.md").write_text("[x](nope.md)\n")
            subprocess.run(git + ["add", "-A"], check=True)
            cmd = [sys.executable, "-m", "sim.tools.verify_markdown_links",
                   "--check", "--root", str(root)]
            repo = SIM_DIR.parent
            ok = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
            self.assertIn("OK (2 document(s) scanned)", ok.stdout)
            (root / "docs" / "a.md").write_text("intro\n[b](spec/b.md)\n")
            bad = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1, bad.stderr)
            self.assertIn("docs/a.md:2: broken link: spec/b.md", bad.stdout)


if __name__ == "__main__":
    unittest.main()
