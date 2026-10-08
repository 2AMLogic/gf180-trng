#!/usr/bin/env python3
"""Hold sim/tools/klt_pin_sites.py to both halves of its contract (#344).

The guard keeps every restated ``klayout-tools==`` / ``klayout==`` pin in
step with signoff/check.py's KLT_PIN and KLAYOUT_PIN. Each case runs over a
synthetic git repository in a temporary directory, so nothing here depends
on where the real tree happens to restate the pin. Matching pins must pass;
a mismatching pin must fail unless its own line carries the historical
marker, and a marker that exempts nothing must fail too.

The pin strings in this file are assembled at run time (``pin()``) because
this file is itself tracked *.py and therefore scanned by the real guard.
Stdlib only (plus git); no klt, no PDK.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
TOOL = SIM_DIR / "tools" / "klt_pin_sites.py"
sys.path.insert(0, str(SIM_DIR / "tools"))

import klt_pin_sites as kps  # noqa: E402

KLT = "1.2.3"
ENGINE = "0.30.9"
MARK = kps.MARKER


def pin(package: str, version: str) -> str:
    return package + "==" + version


CHECK_PY = f'''\
KLT_PIN = "{KLT}"
KLAYOUT_PIN = "{ENGINE}"
KLT_INSTALL_HINT = f'pip install "klayout-tools=={{KLT_PIN}}"'
'''


def build_repo(root: Path, files: dict[str, str],
               check_py: str = CHECK_PY) -> None:
    """A git repo with signoff/check.py plus ``files``, all tracked."""
    tree = {"signoff/check.py": check_py, **files}
    for rel, text in tree.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)


GOOD = {
    ".github/workflows/ci.yml":
        f'      run: pip install "{pin("klayout-tools", KLT)}"\n',
    "layout/README.md":
        f'pip install "{pin("klayout-tools", KLT)}" '
        f'"{pin("klayout", ENGINE)}"\n',
    "layout/_klt.py":
        f'"""(`pip install "{pin("klayout-tools", KLT)}"`)."""\n',
}


class KltPinSitesTest(unittest.TestCase):

    def run_tree(self, files: dict[str, str], **kw) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root, files, **kw)
            _, _, problems = kps.check_tree(root)
            return problems

    def test_matching_pins_pass(self):
        self.assertEqual(self.run_tree(GOOD), [])

    def test_mentions_are_found_in_every_scanned_kind(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root, GOOD)
            pins, mentions, _ = kps.check_tree(root)
        self.assertEqual(pins, {"klayout-tools": KLT, "klayout": ENGINE})
        self.assertEqual(
            sorted((m.path, m.package) for m in mentions),
            [(".github/workflows/ci.yml", "klayout-tools"),
             ("layout/README.md", "klayout"),
             ("layout/README.md", "klayout-tools"),
             ("layout/_klt.py", "klayout-tools")])

    def test_stale_klt_pin_in_workflow_fails(self):
        files = dict(GOOD)
        files[".github/workflows/ci.yml"] = \
            f'      run: pip install "{pin("klayout-tools", "1.2.2")}"\n'
        problems = self.run_tree(files)
        self.assertEqual(len(problems), 1)
        self.assertIn(".github/workflows/ci.yml:1:", problems[0])
        self.assertIn(pin("klayout-tools", "1.2.2"), problems[0])

    def test_stale_engine_pin_in_markdown_fails(self):
        files = dict(GOOD)
        files["sim/tb/x/README.md"] = f"text\n`{pin('klayout', '0.30.12')}`\n"
        problems = self.run_tree(files)
        self.assertEqual(len(problems), 1)
        self.assertIn("sim/tb/x/README.md:2:", problems[0])

    def test_constant_change_alone_fails_every_restated_site(self):
        bumped = CHECK_PY.replace(f'"{KLT}"', '"1.3.0"')
        problems = self.run_tree(GOOD, check_py=bumped)
        self.assertEqual(len(problems), 3)

    def test_historical_marker_exempts_its_own_line_only(self):
        files = dict(GOOD)
        old = pin("klayout-tools", "0.2.0")
        files["layout/README.md"] += (
            f"a `pip install {old}` run <!-- {MARK} -->\n"
            f"and again `pip install {old}`\n")
        problems = self.run_tree(files)
        self.assertEqual(len(problems), 1)
        self.assertIn("layout/README.md:3:", problems[0])

    def test_marker_works_inside_a_python_docstring(self):
        files = dict(GOOD)
        files["layout/verify.py"] = (
            f'"""Measured with `{pin("klayout", "0.30.12")}` ({MARK})."""\n')
        self.assertEqual(self.run_tree(files), [])

    def test_marker_on_a_current_or_pinless_line_fails(self):
        for line in (f"`{pin('klayout-tools', KLT)}` <!-- {MARK} -->",
                     f"no pin here # {MARK}"):
            with self.subTest(line=line):
                files = dict(GOOD)
                files["doc.md"] = line + "\n"
                problems = self.run_tree(files)
                self.assertEqual(len(problems), 1)
                self.assertIn("doc.md:1:", problems[0])
                self.assertIn("exempts no mismatching pin", problems[0])

    def test_append_only_evidence_and_untracked_files_are_not_scanned(self):
        stale = f"`{pin('klayout-tools', '0.1.0')}`\n"
        files = dict(GOOD)
        files["sim/records/2026-01-01-x.md"] = stale
        files["signoff/evidence/note.md"] = stale
        files["notes.txt"] = stale
        # Under the workflow directory only *.yml/*.yaml are scanned.
        files[".github/workflows/readme.md"] = stale
        self.assertEqual(self.run_tree(files), [])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root, GOOD)
            (root / "untracked.md").write_text(stale, encoding="utf-8")
            self.assertEqual(kps.check_tree(root)[2], [])

    def test_name_boundaries(self):
        text = (f"{pin('foo-klayout', '9.9')} {pin('klayout-toolsx', '9.9')} "
                f"see {pin('klayout', ENGINE)}.\n")
        found = kps.find_mentions("x.md", text)
        self.assertEqual([(m.package, m.version) for m in found],
                         [("klayout", ENGINE)])

    def test_missing_or_non_literal_constant_is_an_error(self):
        for check_py in (f'KLT_PIN = "{KLT}"\n',
                         f'KLT_PIN = "{KLT}"\nKLAYOUT_PIN = str(1)\n'):
            with self.subTest(check_py=check_py):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    build_repo(root, GOOD, check_py=check_py)
                    with self.assertRaises(ValueError):
                        kps.check_tree(root)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root, GOOD)
            ok = subprocess.run(
                [sys.executable, str(TOOL), "--check", "--root", str(root)],
                capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            (root / "layout/README.md").write_text(
                f"`{pin('klayout', '0.0.1')}`\n", encoding="utf-8")
            bad = subprocess.run(
                [sys.executable, str(TOOL), "--check", "--root", str(root)],
                capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            self.assertIn("FAIL: layout/README.md:1:", bad.stderr)

    def test_real_tree_agrees(self):
        _, mentions, problems = kps.check_tree(kps.REPO_ROOT)
        self.assertEqual(problems, [])
        self.assertTrue(mentions)


if __name__ == "__main__":
    unittest.main()
