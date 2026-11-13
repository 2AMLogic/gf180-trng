#!/usr/bin/env python3
"""Hold sim/tools/klt_pin_sites.py to both halves of its contract (#344).

The guard keeps every restated ``klayout==`` pin in step with
signoff/check.py's KLAYOUT_PIN and every ``klayout-tools==`` line that
restates the grader in step with KLT_GRADER_PIN. The producer klayout-tools is
deliberately unpinned (DR-0026, 2026-11-09 amendment): an unmarked
``klayout-tools==X.Y.Z`` mention fails. Each case runs over a
synthetic git repository in a temporary directory, so nothing here depends
on where the real tree happens to restate the pin. Matching pins must pass;
a mismatching or producer pin must fail unless its own line carries the
historical marker, and a marker that exempts nothing must fail too.

The guard's second half (#858) reads the engine a committed report under
`layout/` *records*, not the one an install line names, and holds it to
KLAYOUT_PIN as well. The cases below cover both fields it reads
(``klayout_version`` always, ``engine_version`` only beside an
``engine: "klayout"`` sibling), the non-KLayout engines it must leave
alone, and that nothing outside `layout/` is scanned.

The pin strings in this file are assembled at run time (``pin()``) because
this file is itself tracked *.py and therefore scanned by the real guard.
Stdlib only (plus git); no klt, no PDK.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
TOOL = SIM_DIR / "tools" / "klt_pin_sites.py"
sys.path.insert(0, str(SIM_DIR / "tools"))

import klt_pin_sites as kps  # noqa: E402

GRADER = "2.0.0"
ENGINE = "0.30.9"
MARK = kps.MARKER
GMARK = kps.GRADER_MARKER


def pin(package: str, version: str) -> str:
    return package + "==" + version


CHECK_PY = f'''\
KLAYOUT_PIN = "{ENGINE}"
KLT_GRADER_PIN = "{GRADER}"
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
        f'      run: pip install "{pin("klayout-tools", GRADER)}"  # {GMARK}\n',
    "layout/README.md":
        f'pip install klayout-tools "{pin("klayout", ENGINE)}"\n',
    "layout/_klt.py":
        '"""(`pip install klayout-tools`)."""\n',
}


def report(engine: str = ENGINE, **extra) -> str:
    """A minimal `klt lvs`-shaped report recording ``engine``."""
    payload = {
        "schema_version": 3,
        "engine": "klayout",
        "status": "match",
        "environment": {"engine": "klayout", "engine_version": engine},
        "provenance": {"klayout_version": engine},
    }
    payload.update(extra)
    return json.dumps(payload, indent=2) + "\n"


class KltPinSitesTest(unittest.TestCase):

    def run_tree(self, files: dict[str, str], **kw) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root, files, **kw)
            _, _, _, problems = kps.check_tree(root)
            return problems

    def test_matching_pins_pass(self):
        self.assertEqual(self.run_tree(GOOD), [])

    def test_producer_is_unpinned_and_only_engine_and_grader_are_constants(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root, GOOD)
            pins, mentions, _, _ = kps.check_tree(root)
        self.assertEqual(
            pins, {"klayout-tools": None, "klayout": ENGINE, kps.GRADER_KEY: GRADER})
        self.assertEqual(
            sorted((m.path, m.package) for m in mentions),
            [(".github/workflows/ci.yml", "klayout-tools"),
             ("layout/README.md", "klayout")])

    def test_producer_pin_in_workflow_fails(self):
        files = dict(GOOD)
        files[".github/workflows/nightly.yml"] = \
            f'      run: pip install "{pin("klayout-tools", "1.2.2")}"\n'
        problems = self.run_tree(files)
        self.assertEqual(len(problems), 1)
        self.assertIn(".github/workflows/nightly.yml:1:", problems[0])
        self.assertIn("not pinned here", problems[0])

    def test_stale_engine_pin_in_markdown_fails(self):
        files = dict(GOOD)
        files["sim/tb/x/README.md"] = f"text\n`{pin('klayout', '0.30.12')}`\n"
        problems = self.run_tree(files)
        self.assertEqual(len(problems), 1)
        self.assertIn("sim/tb/x/README.md:2:", problems[0])

    def test_engine_constant_change_alone_fails_every_restated_site(self):
        bumped = CHECK_PY.replace(f'"{ENGINE}"', '"0.30.10"')
        problems = self.run_tree(GOOD, check_py=bumped)
        self.assertEqual(len(problems), 1)

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
        for line in (f"`{pin('klayout', ENGINE)}` <!-- {MARK} -->",
                     f"no pin here # {MARK}"):
            with self.subTest(line=line):
                files = dict(GOOD)
                files["doc.md"] = line + "\n"
                problems = self.run_tree(files)
                self.assertEqual(len(problems), 1)
                self.assertIn("doc.md:1:", problems[0])
                self.assertIn("exempts no mismatching pin", problems[0])

    def test_grader_marker_holds_a_line_to_the_grader_pin(self):
        files = dict(GOOD)
        files["ci.yml.md"] = f"`{pin('klayout-tools', GRADER)}` # {GMARK}\n"
        self.assertEqual(self.run_tree(files), [])
        # A wrong version on a grader line, and the grader pin on an
        # unmarked line, both fail.
        files["ci.yml.md"] = f"`{pin('klayout-tools', '1.0.0')}` # {GMARK}\n"
        files["other.md"] = f"`{pin('klayout-tools', GRADER)}`\n"
        problems = self.run_tree(files)
        self.assertEqual(len(problems), 2)
        self.assertIn(f"pins klayout-tools=={GRADER}", problems[0])
        self.assertIn("not pinned here", problems[1])

    def test_grader_marker_without_a_pin_fails(self):
        files = dict(GOOD)
        files["doc.md"] = f"no pin here # {GMARK}\n"
        problems = self.run_tree(files)
        self.assertEqual(len(problems), 1)
        self.assertIn("no klayout-tools== mention", problems[0])

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
            self.assertEqual(kps.check_tree(root)[3], [])

    def test_name_boundaries(self):
        text = (f"{pin('foo-klayout', '9.9')} {pin('klayout-toolsx', '9.9')} "
                f"see {pin('klayout', ENGINE)}.\n")
        found = kps.find_mentions("x.md", text)
        self.assertEqual([(m.package, m.version) for m in found],
                         [("klayout", ENGINE)])

    def test_missing_or_non_literal_constant_is_an_error(self):
        for check_py in ('KLT_GRADER_PIN = "1.0.0"\n',
                         f'KLAYOUT_PIN = str(1)\nKLT_GRADER_PIN = "{GRADER}"\n'):
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

    # ---- recorded engines in committed layout reports (#858) ----------

    def test_on_pin_report_passes_and_off_pin_report_fails(self):
        files = dict(GOOD)
        files["layout/reports/xor2.lvs.json"] = report()
        self.assertEqual(self.run_tree(files), [])

        files["layout/reports/xor2.lvs.json"] = report("0.30.13")
        problems = self.run_tree(files)
        self.assertEqual(len(problems), 2)
        for got, field in zip(problems, ("$.environment.engine_version",
                                         "$.provenance.klayout_version")):
            self.assertIn("layout/reports/xor2.lvs.json:", got)
            self.assertIn(field, got)
            self.assertIn("records the KLayout engine as 0.30.13", got)
            self.assertIn(f"pins klayout=={ENGINE}", got)

    def test_nested_klayout_version_is_found(self):
        # floorplan.drc.json carries its provenance one level down.
        files = dict(GOOD)
        files["layout/floorplan/reports/floorplan.drc.json"] = json.dumps(
            {"drc": {"provenance": {"klayout_version": "0.30.13"}}}) + "\n"
        problems = self.run_tree(files)
        self.assertEqual(len(problems), 1)
        self.assertIn("$.drc.provenance.klayout_version", problems[0])

    def test_engine_version_of_another_engine_is_left_alone(self):
        # place_and_route.json / sdf_export.json record an OpenROAD or
        # OpenSTA build in the same field name; KLAYOUT_PIN says nothing
        # about those, and a sibling klayout_version is still held.
        files = dict(GOOD)
        files["layout/digital/reports/place_and_route.json"] = json.dumps({
            "engine": "openroad",
            "engine_version": "26Q3-1510-g6cb3f2b704",
            "provenance": {"klayout_version": ENGINE},
        }) + "\n"
        self.assertEqual(self.run_tree(files), [])

    def test_engine_version_with_no_engine_sibling_is_left_alone(self):
        files = dict(GOOD)
        files["layout/reports/x.json"] = json.dumps(
            {"environment": {"engine_version": "26Q3-1510"}}) + "\n"
        self.assertEqual(self.run_tree(files), [])

    def test_reports_inside_lists_are_scanned(self):
        files = dict(GOOD)
        files["layout/reports/runs.json"] = json.dumps(
            {"runs": [{"provenance": {"klayout_version": "0.30.13"}}]}) + "\n"
        problems = self.run_tree(files)
        self.assertEqual(len(problems), 1)
        self.assertIn("$.runs[0].provenance.klayout_version", problems[0])

    def test_only_tracked_json_under_layout_is_scanned(self):
        off_pin = report("0.30.13")
        files = dict(GOOD)
        # Outside layout/: append-only evidence naming its own producer.
        files["signoff/evidence/post-layout/ro_ring11.pex.json"] = off_pin
        files["sim/records/2026-01-01-x.json"] = off_pin
        # Under layout/, but not JSON.
        files["layout/notes.md"] = "klayout_version 0.30.13\n"
        self.assertEqual(self.run_tree(files), [])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root, GOOD)
            (root / "layout" / "reports").mkdir(parents=True, exist_ok=True)
            (root / "layout/reports/untracked.json").write_text(
                off_pin, encoding="utf-8")
            self.assertEqual(kps.check_tree(root)[3], [])

    def test_null_engine_field_does_not_pass(self):
        files = dict(GOOD)
        files["layout/reports/x.json"] = json.dumps(
            {"provenance": {"klayout_version": None}}) + "\n"
        problems = self.run_tree(files)
        self.assertEqual(len(problems), 1)
        self.assertIn("records the KLayout engine as null", problems[0])

    def test_malformed_report_is_reported_not_skipped(self):
        files = dict(GOOD)
        files["layout/reports/broken.json"] = "{not json\n"
        problems = self.run_tree(files)
        self.assertEqual(len(problems), 1)
        self.assertIn("layout/reports/broken.json: not valid JSON", problems[0])

    def test_engine_constant_change_alone_fails_every_recorded_engine(self):
        files = dict(GOOD)
        files["layout/reports/xor2.lvs.json"] = report()
        bumped = CHECK_PY.replace(f'"{ENGINE}"', '"0.30.10"')
        # The README's restated pin, plus both recorded engine fields.
        self.assertEqual(len(self.run_tree(files, check_py=bumped)), 3)

    def test_cli_fails_on_an_off_pin_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = dict(GOOD)
            files["layout/reports/xor2.lvs.json"] = report("0.30.13")
            build_repo(root, files)
            done = subprocess.run(
                [sys.executable, str(TOOL), "--check", "--root", str(root)],
                capture_output=True, text=True)
            self.assertEqual(done.returncode, 1)
            self.assertIn("FAIL: layout/reports/xor2.lvs.json:", done.stderr)

    def test_real_tree_agrees(self):
        _, mentions, recordings, problems = kps.check_tree(kps.REPO_ROOT)
        self.assertEqual(problems, [])
        self.assertTrue(mentions)
        self.assertTrue(recordings)


if __name__ == "__main__":
    unittest.main()
