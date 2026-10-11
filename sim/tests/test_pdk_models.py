#!/usr/bin/env python3
"""Unit tests for sim/harness/pdk_models.py and its use in evidence records
(#562): PDK model-content identity, captured before a run and re-checked
before publication.

Synthetic PDK fixtures only -- no ngspice, no installed PDK.
"""

from __future__ import annotations

import datetime as _dt
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import cli, corners, pdk_models, report, runner, testbench  # noqa: E402
from harness.pdk import Pdk  # noqa: E402

TT_SECTIONS = corners.CORNERS["tt"].sections
SS_SECTIONS = corners.CORNERS["ss"].sections


def _section(name: str, body: str) -> str:
    return f".LIB {name}\n{body}.ENDL {name}\n"


def make_fixture_pdk(root: Path, *, sources: str = "open_pdks deadbeef\n",
                     card: str = "* mos card v1\n") -> Pdk:
    """A minimal gf180mcu-shaped variant directory.

    ``sm141064.ngspice`` defines every section a tt/ss deck selects. The MOS
    sections reach a transitive chain -- ``.lib`` into ``mos.ngspice``, whose
    section ``.include``s ``cards/mos_card.ngspice`` -- and ``mimcap_ss``
    alone reaches ``mim_ss_only.ngspice``.
    """
    ng = root / "libs.tech" / "ngspice"
    (ng / "cards").mkdir(parents=True, exist_ok=True)
    (root / "SOURCES").write_text(sources)
    (ng / "design.ngspice").write_text("* design switches\n.param sw_stat_global=0\n")
    lib = ["* model library\n"]
    for name in TT_SECTIONS + SS_SECTIONS:
        if name in ("typical", "ss"):
            body = " .lib 'mos.ngspice' mos_core\n"
        elif name == "mimcap_ss":
            body = " .lib 'mim_ss_only.ngspice' mim\n"
        else:
            body = f" .param {name}_p=1\n"
        lib.append(_section(name, body))
    (ng / "sm141064.ngspice").write_text("".join(lib))
    (ng / "mos.ngspice").write_text(
        "* top level of mos.ngspice is not loaded by a .lib reference\n"
        ".include 'never_loaded.ngspice'\n"
        + _section("mos_core", ' .include "cards/mos_card.ngspice"\n')
    )
    (ng / "cards" / "mos_card.ngspice").write_text(card)
    (ng / "mim_ss_only.ngspice").write_text(_section("mim", " .param mim=1\n"))
    return Pdk(path=root, variant=root.name, source="test")


class ManifestIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def _manifest(self, pdk, sections=TT_SECTIONS):
        return pdk_models.manifest_for_deck(pdk, sections)

    def test_same_sources_label_different_model_bytes_differ(self):
        a = make_fixture_pdk(self.base / "a" / "gf180mcuD", card="* card A\n")
        b = make_fixture_pdk(self.base / "b" / "gf180mcuD", card="* card B (patched)\n")
        self.assertEqual(a.version, b.version)
        self.assertEqual(a.provenance()["open_pdks_version"], b.provenance()["open_pdks_version"])
        ma, mb = self._manifest(a), self._manifest(b)
        self.assertTrue(ma.complete and mb.complete, (ma.problems, mb.problems))
        self.assertNotEqual(ma.identity, mb.identity)

    def test_transitive_dependency_is_covered_and_its_edit_detected(self):
        pdk = make_fixture_pdk(self.base / "gf180mcuD")
        before = self._manifest(pdk)
        self.assertEqual(
            [p for p, _ in before.files],
            [
                "libs.tech/ngspice/cards/mos_card.ngspice",
                "libs.tech/ngspice/design.ngspice",
                "libs.tech/ngspice/mos.ngspice",
                "libs.tech/ngspice/sm141064.ngspice",
            ],
        )
        (pdk.path / "libs.tech/ngspice/cards/mos_card.ngspice").write_text("* edited\n")
        after = self._manifest(pdk)
        self.assertNotEqual(before.identity, after.identity)
        self.assertEqual(
            before.describe_differences(after)[0].split(":")[0],
            "libs.tech/ngspice/cards/mos_card.ngspice",
        )

    def test_identity_is_deterministic_and_independent_of_install_root(self):
        a = make_fixture_pdk(self.base / "one" / "gf180mcuD")
        b = make_fixture_pdk(self.base / "elsewhere" / "deeper" / "gf180mcuD")
        self.assertEqual(self._manifest(a).identity, self._manifest(a).identity)
        self.assertEqual(self._manifest(a).identity, self._manifest(b).identity)
        self.assertEqual(self._manifest(a).to_json_bytes(), self._manifest(b).to_json_bytes())
        doc = self._manifest(a).to_json_bytes().decode()
        self.assertNotIn(str(self.base), doc)

    def test_only_selected_sections_are_followed(self):
        pdk = make_fixture_pdk(self.base / "gf180mcuD")
        tt = self._manifest(pdk, TT_SECTIONS)
        ss = self._manifest(pdk, SS_SECTIONS)
        self.assertNotIn("libs.tech/ngspice/mim_ss_only.ngspice", dict(tt.files))
        self.assertIn("libs.tech/ngspice/mim_ss_only.ngspice", dict(ss.files))
        # A file reached only by an unselected section does not move tt.
        (pdk.path / "libs.tech/ngspice/mim_ss_only.ngspice").write_text(_section("mim", "* x\n"))
        self.assertEqual(tt.identity, self._manifest(pdk, TT_SECTIONS).identity)
        self.assertNotEqual(ss.identity, self._manifest(pdk, SS_SECTIONS).identity)
        # Top-level content of a file reached via .lib is not loaded either.
        self.assertNotIn("libs.tech/ngspice/never_loaded.ngspice", dict(tt.files))
        self.assertTrue(tt.complete, tt.problems)

    def test_section_selection_is_part_of_the_identity(self):
        pdk = make_fixture_pdk(self.base / "gf180mcuD")
        self.assertNotEqual(
            self._manifest(pdk, ["typical"]).identity, self._manifest(pdk, ["ss"]).identity
        )

    def test_missing_dependencies_are_reported_not_hidden(self):
        pdk = make_fixture_pdk(self.base / "gf180mcuD")
        (pdk.path / "libs.tech/ngspice/cards/mos_card.ngspice").unlink()
        m = self._manifest(pdk)
        self.assertFalse(m.complete)
        self.assertIn(
            "missing file libs.tech/ngspice/cards/mos_card.ngspice "
            "(referenced from libs.tech/ngspice/mos.ngspice:4)",
            m.problems,
        )
        missing_section = self._manifest(pdk, ["no_such_section"])
        self.assertIn(
            "missing section 'no_such_section' in libs.tech/ngspice/sm141064.ngspice "
            "(referenced from deck)",
            missing_section.problems,
        )

    def test_unsupported_include_forms_are_reported(self):
        pdk = make_fixture_pdk(self.base / "gf180mcuD")
        outside = self.base / "outside.ngspice"
        outside.write_text("* outside\n")
        (pdk.path / "libs.tech/ngspice/design.ngspice").write_text(
            "* design\n"
            ".include {model_dir}/x.ngspice\n"
            ".include $PDK_ROOT/x.ngspice\n"
            ".include a.ngspice b.ngspice\n"
            ".lib 'only_one_argument_is_a_definition_this_has_three' a b\n"
            f".include '{outside}'\n"
            ".include '../../../outside.ngspice'\n"
            ".osdi 'model.osdi'\n"
            ".control\n"
            "source extra.ngspice\n"
            ".endc\n"
        )
        m = self._manifest(pdk)
        self.assertFalse(m.complete)
        text = "\n".join(m.problems)
        where = "libs.tech/ngspice/design.ngspice"
        for expected in (
            f"{where}:2: unsupported parameterized path '{{model_dir}}/x.ngspice'",
            f"{where}:3: unsupported parameterized path '$PDK_ROOT/x.ngspice'",
            f"{where}:4: unsupported .include form (2 arguments)",
            f"{where}:5: unsupported .lib form (3 arguments)",
            f"{where}:6: reference to an absolute path outside the PDK variant directory",
            f"{where}:7: reference to '../../../outside.ngspice' outside the PDK variant directory",
            f"{where}:8: unsupported file-loading directive '.osdi'",
            f"{where}:10: unsupported file-loading command 'source'",
        ):
            self.assertIn(expected, text)
        # No host path leaks into the problems (they feed the identity).
        self.assertNotIn(str(self.base), text)

    def test_continuations_comments_and_cycles(self):
        pdk = make_fixture_pdk(self.base / "gf180mcuD")
        ng = pdk.path / "libs.tech/ngspice"
        (ng / "design.ngspice").write_text(
            "* .include 'commented_out.ngspice'\n"
            ".include\n+ 'loop_a.ngspice' $ inline comment\n"
        )
        (ng / "loop_a.ngspice").write_text(".inc loop_b.ngspice ; trailing\n")
        (ng / "loop_b.ngspice").write_text(".INCLUDE \"loop_a.ngspice\"\n")
        m = self._manifest(pdk)
        self.assertTrue(m.complete, m.problems)
        self.assertIn("libs.tech/ngspice/loop_a.ngspice", dict(m.files))
        self.assertIn("libs.tech/ngspice/loop_b.ngspice", dict(m.files))
        self.assertNotIn("libs.tech/ngspice/commented_out.ngspice", dict(m.files))

    def test_document_identity_round_trips(self):
        m = self._manifest(make_fixture_pdk(self.base / "gf180mcuD"))
        doc = json.loads(m.to_json_bytes())
        self.assertEqual(doc["identity"], m.identity)
        self.assertEqual(pdk_models.identity_from_document(doc), m.identity)
        doc["files"][0]["sha256"] = "0" * 64
        self.assertNotEqual(pdk_models.identity_from_document(doc), m.identity)


class RecordProvenanceTests(unittest.TestCase):
    """The manifest is a checksummed raw artifact; legacy records stay valid."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        tb_dir = self.root / "tb" / "an-experiment"
        tb_dir.mkdir(parents=True)
        (tb_dir / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (tb_dir / "tb.json").write_text(json.dumps(
            {"name": "an-experiment", "netlist": "x.spice", "measure": {"vout": "v(out)"}}
        ))
        self.tb = testbench.load(tb_dir)
        self.pdk = make_fixture_pdk(self.root / "pdk" / "gf180mcuD")
        self.point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]
        self.stem = "2026-07-31-an-experiment-01"
        self.raw_dir = self.root / "records" / "raw" / self.stem
        self.raw_dir.mkdir(parents=True)
        (self.raw_dir / "d.spice").write_text("* deck\n")
        (self.raw_dir / "d.log").write_text("m_vout = 1\n")
        testbench.write_input_snapshots(self.tb, self.raw_dir)
        results = [runner.RunResult(
            point=self.point, seed=None, status="ok", measurements={"vout": 1.0},
            deck_name="d.spice", log_name="d.log",
        )]
        self.record = report.build_record(
            tb=self.tb, pdk=self.pdk, point=self.point, results=results,
            ngspice="ngspice-46", repo_root=self.root, stem=self.stem,
            completed_utc=_dt.datetime(2026, 7, 31, 12, 0, 0, tzinfo=_dt.timezone.utc),
            wall_seconds=1.0, raw_dir=self.raw_dir, git={"commit": "f" * 40, "dirty": False},
        )

    def _write(self, record=None) -> Path:
        return report.write_record(record or self.record, self.tb, self.root / "records", ["c"])

    def test_manifest_is_listed_in_raw_files_and_declared_in_frontmatter(self):
        listed = dict(self.record["raw_files"])
        self.assertIn(pdk_models.MANIFEST_NAME, listed)
        expected = pdk_models.manifest_for_deck(self.pdk, TT_SECTIONS)
        self.assertEqual(self.record["pdk_content_identity"], expected.identity)
        text = report.render_frontmatter(self.record)
        self.assertIn("pdk_content:\n", text)
        self.assertIn(f"  manifest_file: {pdk_models.MANIFEST_NAME}\n", text)
        self.assertIn(f"  sha256: {listed[pdk_models.MANIFEST_NAME]}\n", text)
        self.assertIn(f"  identity: {expected.identity}\n", text)
        self.assertIn("  file_count: 4\n  complete: true\n  problems: 0\n", text)
        self.assertEqual(report.verify_record_file(self._write(), self.root), [])

    def test_tampered_manifest_is_detected(self):
        path = self._write()
        manifest = self.raw_dir / pdk_models.MANIFEST_NAME
        manifest.write_text(manifest.read_text().replace("design.ngspice", "other.ngspice"))
        problems = report.verify_record_file(path, self.root)
        self.assertTrue(any(pdk_models.MANIFEST_NAME in p for p in problems), problems)

    def test_declared_identity_must_match_the_manifest(self):
        path = self._write()
        text = path.read_text()
        forged = text.replace(self.record["pdk_content_identity"], "sha256:" + "0" * 64, 1)
        path.write_text(forged)
        problems = report.verify_record_file(path, self.root)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("pdk_content.identity", problems[0])
        path.write_text(text.replace("  file_count: 4", "  file_count: 3", 1))
        self.assertIn(
            "pdk_content.file_count", "\n".join(report.verify_record_file(path, self.root))
        )

    def test_manifest_digest_must_match_raw_files_entry(self):
        text = report.render_frontmatter(self.record)
        digest = self.record["pdk_content_sha256"]
        bad = text.replace(f"  sha256: {digest}", "  sha256: " + "0" * 64, 1)
        problems = report.verify_pdk_content_reference(bad, self.record["raw_files"])
        self.assertEqual(len(problems), 1, problems)

    def test_legacy_record_without_block_is_unchanged_and_valid(self):
        legacy = dict(self.record, pdk_content_sha256="")
        legacy["raw_files"] = [
            f for f in self.record["raw_files"] if f[0] != pdk_models.MANIFEST_NAME
        ]
        (self.raw_dir / pdk_models.MANIFEST_NAME).unlink()
        text = report.render_frontmatter(legacy)
        self.assertNotIn("pdk_content", text)
        self.assertEqual(report.parse_pdk_content_section(text), {})
        self.assertEqual(report.verify_pdk_content_reference(text, legacy["raw_files"]), [])
        self.assertEqual(report.verify_record_file(self._write(legacy), self.root), [])

    def test_incomplete_identity_is_recorded_as_such(self):
        (self.pdk.path / "libs.tech/ngspice/cards/mos_card.ngspice").unlink()
        manifest = pdk_models.manifest_for_deck(self.pdk, TT_SECTIONS)
        record = report.build_record(
            tb=self.tb, pdk=self.pdk, point=self.point, results=self.record["results"],
            ngspice="ngspice-46", repo_root=self.root, stem=self.stem,
            completed_utc=_dt.datetime(2026, 7, 31, 12, 0, 0, tzinfo=_dt.timezone.utc),
            wall_seconds=1.0, raw_dir=self.raw_dir, git={"commit": "f" * 40, "dirty": False},
            model_manifest=manifest,
        )
        text = report.render_frontmatter(record)
        self.assertIn("  complete: false\n  problems: 1\n", text)
        caveats = cli._model_caveats(manifest)
        self.assertTrue(any("INCOMPLETE" in c and "mos_card" in c for c in caveats), caveats)
        self.assertEqual(report.verify_record_file(self._write(record), self.root), [])


class MidRunModelChangeTests(unittest.TestCase):
    """A model edit during execution withholds the record, keeps the raw
    output and both manifests, and fails the run with its own exit code."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.records_dir = self.root / "records"
        self.tb_dir = self.root / "tb" / "an-experiment"
        self.tb_dir.mkdir(parents=True)
        (self.tb_dir / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (self.tb_dir / "tb.json").write_text(json.dumps(
            {"name": "an-experiment", "netlist": "x.spice", "measure": {"vout": "v(out)"}}
        ))
        self.pdk = make_fixture_pdk(self.root / "pdk" / "gf180mcuD")
        patches = [
            mock.patch.object(cli, "RECORDS_DIR", self.records_dir),
            mock.patch.object(cli, "REPO_ROOT", self.root),
            mock.patch.object(cli, "find_pdk", lambda: self.pdk),
            mock.patch.object(
                cli.report, "git_provenance", lambda _r: {"commit": "f" * 40, "dirty": False}
            ),
            mock.patch.object(cli.runner, "ngspice_version", return_value="ngspice-46"),
        ]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def _install_runner(self, on_run=None):
        def fake_run_one(tb, pdk, point, workdir, seed=None, run_index=0, timeout_s=0):
            workdir.mkdir(parents=True, exist_ok=True)
            deck = workdir / f"{point.corner_id}.spice"
            log = workdir / f"{point.corner_id}.log"
            deck.write_text(f"* deck for {point.corner_id}\n")
            log.write_text("m_vout = 1.65\n")
            if on_run is not None:
                on_run(point)
            return runner.RunResult(
                point=point, seed=seed, status="ok", measurements={"vout": 1.65},
                seconds=0.1, deck_name=deck.name, log_name=log.name,
            )

        patcher = mock.patch.object(cli.runner, "run_one", side_effect=fake_run_one)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _run(self, *extra):
        argv = [str(self.tb_dir), "--corners", "tt", "ss", "--temps", "27",
                "--supply-tol", "0", *extra]
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = cli.main(argv)
        return status, out.getvalue(), err.getvalue()

    def test_clean_run_records_identity_and_verifies(self):
        self._install_runner()
        status, out, _err = self._run()
        self.assertEqual(status, cli.EXIT_OK, out)
        self.assertIn("models    : sha256:", out)
        records = sorted(self.records_dir.glob("*.md"))
        self.assertEqual(len(records), 2)
        for path in records:
            text = path.read_text()
            self.assertIn("pdk_content:", text)
            self.assertIn("PDK model identity (pdk_content) covers only", text)
            self.assertEqual(report.verify_record_file(path, self.root), [])

    def test_model_change_during_execution_withholds_the_record(self):
        card = self.pdk.path / "libs.tech/ngspice/cards/mos_card.ngspice"

        def edit_models_during_ss(point):
            if point.corner.name == "ss":
                card.write_text("* card edited mid-run\n")

        self._install_runner(on_run=edit_models_during_ss)
        status, out, err = self._run()

        self.assertEqual(status, cli.EXIT_PDK_MODELS_CHANGED)
        self.assertIn("FAILED-PDK-CHANGED", out)
        self.assertIn("status    : FAIL (PDK model files changed during the run)", out)
        self.assertNotIn("status    : OK", out)
        self.assertIn("libs.tech/ngspice/cards/mos_card.ngspice: sha256", err)
        # tt finished and was re-checked before the edit: it is published.
        records = sorted(self.records_dir.glob("*.md"))
        self.assertEqual(len(records), 1)
        self.assertEqual(report.verify_record_file(records[0], self.root), [])
        # ss is withheld; its raw output and both manifests are retained.
        raw_dirs = sorted(p for p in (self.records_dir / "raw").iterdir() if p.is_dir())
        withheld = [d for d in raw_dirs if not (self.records_dir / f"{d.name}.md").exists()]
        self.assertEqual(len(withheld), 1)
        kept = {p.name for p in withheld[0].iterdir()}
        self.assertLessEqual(
            {pdk_models.MANIFEST_NAME, pdk_models.CHANGED_MANIFEST_NAME}, kept
        )
        self.assertTrue(any(name.endswith(".log") for name in kept), kept)
        before = json.loads((withheld[0] / pdk_models.MANIFEST_NAME).read_text())
        after = json.loads((withheld[0] / pdk_models.CHANGED_MANIFEST_NAME).read_text())
        self.assertNotEqual(before["identity"], after["identity"])

    def test_model_change_fails_a_no_write_run_too(self):
        work = self.root / "work"
        patcher = mock.patch.object(cli, "WORK_DIR", work)
        patcher.start()
        self.addCleanup(patcher.stop)
        card = self.pdk.path / "libs.tech/ngspice/cards/mos_card.ngspice"
        self._install_runner(on_run=lambda point: card.write_text(f"* {point.corner_id}\n"))
        status, out, _err = self._run("--no-write")
        self.assertEqual(status, cli.EXIT_PDK_MODELS_CHANGED)
        self.assertEqual(list(self.records_dir.glob("*.md")), [])
        self.assertTrue(list(work.rglob(pdk_models.CHANGED_MANIFEST_NAME)))


if __name__ == "__main__":
    unittest.main()
