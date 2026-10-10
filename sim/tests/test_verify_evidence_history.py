#!/usr/bin/env python3
"""Hold sim/tools/verify_evidence_history.py to both halves of its contract.

Each case builds a small throwaway git repository, commits a "base" evidence
tree, makes a change on top, and runs the checker against the base. Nothing
here touches the committed sim/records/. Stdlib only; needs only `git`.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR / "tools"))

import verify_evidence_history as veh  # noqa: E402

OLD = "2026-01-01-demo-01"
NEW = "2026-01-02-demo-02"

OLD_VALID = f"---\nrecord: {OLD}\nstatus: valid\n\nvalue: 1.0\n---\nprose\n"
OLD_SUPERSEDED = (
    f"---\nrecord: {OLD}\nstatus: superseded\nsuperseded_by: {NEW}\n\nvalue: 1.0\n---\nprose\n"
)
NEW_REC = f"---\nrecord: {NEW}\nstatus: valid\nsupersedes: {OLD} -- re-run\n---\nprose\n"


class Repo:
    def __init__(self, root: Path):
        self.root = root
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.invalid")
        self.git("config", "user.name", "t")
        self.git("config", "commit.gpgsign", "false")
        # No detached gc/maintenance may outlive a test and race tempdir cleanup.
        self.git("config", "gc.auto", "0")
        self.git("config", "maintenance.auto", "false")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def write(self, rel: str, text: str) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def commit(self, msg: str = "c") -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.r = Repo(Path(self._tmp.name))
        self.r.write(f"sim/records/{OLD}.md", OLD_VALID)
        self.r.write(f"sim/records/raw/{OLD}/out.log", "raw bytes\n")
        self.r.write("README.md", "unrelated\n")
        self.base = self.r.commit("base")

    def check(self):
        return veh.check_history(self.r.root, self.base, "HEAD")

    def assertFails(self, needle: str = ""):
        problems = self.check()
        self.assertTrue(problems, "expected a violation")
        self.assertIn(needle, "\n".join(problems))

    def test_additions_pass(self):
        self.r.write(f"sim/records/{NEW}.md", NEW_REC)
        self.r.write(f"sim/records/raw/{NEW}/out.log", "new\n")
        self.r.write("README.md", "unrelated edit\n")
        self.r.commit()
        self.assertEqual(self.check(), [])

    def test_no_change_passes(self):
        self.assertEqual(self.check(), [])

    def test_valid_supersession_passes(self):
        self.r.write(f"sim/records/{NEW}.md", NEW_REC)
        self.r.write(f"sim/records/{OLD}.md", OLD_SUPERSEDED)
        self.r.commit()
        self.assertEqual(self.check(), [])

    def test_prose_edit_fails(self):
        self.r.write(f"sim/records/{OLD}.md", OLD_VALID.replace("prose", "better prose"))
        self.r.commit()
        self.assertFails("supersession")

    def test_number_edit_fails(self):
        self.r.write(f"sim/records/{OLD}.md", OLD_VALID.replace("1.0", "2.0"))
        self.r.commit()
        self.assertFails(OLD)

    def test_raw_edit_fails(self):
        self.r.write(f"sim/records/raw/{OLD}/out.log", "tampered\n")
        self.r.commit()
        self.assertFails("raw")

    def test_raw_and_checksum_rewrite_fails(self):
        self.r.write(f"sim/records/raw/{OLD}/out.log", "tampered\n")
        self.r.write(f"sim/records/{OLD}.md", OLD_VALID.replace("1.0", "1.0 sha256 changed"))
        self.r.commit()
        self.assertEqual(len(self.check()), 2)

    def test_delete_record_and_raw_fails(self):
        self.r.git("rm", "-rq", f"sim/records/{OLD}.md", f"sim/records/raw/{OLD}")
        self.r.commit()
        self.assertEqual(len(self.check()), 2)

    def test_rename_fails(self):
        self.r.git("mv", f"sim/records/{OLD}.md", "sim/records/renamed.md")
        self.r.git("mv", f"sim/records/raw/{OLD}", "sim/records/raw/renamed")
        self.r.commit()
        problems = self.check()
        self.assertEqual(len([p for p in problems if "deleted or renamed" in p]), 2)

    def test_type_change_fails(self):
        p = self.r.root / f"sim/records/raw/{OLD}/out.log"
        p.unlink()
        p.symlink_to("/etc/hostname")
        self.r.commit()
        self.assertFails("type changed")

    def test_added_symlink_fails(self):
        (self.r.root / "sim/records/raw/link").symlink_to("/etc/hostname")
        self.r.commit()
        self.assertFails("unsupported mode")

    def test_missing_replacement_fails(self):
        self.r.write(f"sim/records/{OLD}.md", OLD_SUPERSEDED)
        self.r.commit()
        self.assertFails("does not exist")

    def test_replacement_without_backlink_fails(self):
        self.r.write(f"sim/records/{NEW}.md", NEW_REC.replace(OLD, "some-other-stem"))
        self.r.write(f"sim/records/{OLD}.md", OLD_SUPERSEDED)
        self.r.commit()
        self.assertFails("does not declare")

    def test_extra_edit_with_transition_fails(self):
        self.r.write(f"sim/records/{NEW}.md", NEW_REC)
        self.r.write(f"sim/records/{OLD}.md", OLD_SUPERSEDED.replace("prose", "edited"))
        self.r.commit()
        self.assertFails("beyond")

    def test_status_only_without_pointer_fails(self):
        self.r.write(f"sim/records/{OLD}.md", OLD_VALID.replace("status: valid", "status: superseded"))
        self.r.commit()
        self.assertFails("superseded_by")

    def test_resupersede_fails(self):
        self.r.write(f"sim/records/{NEW}.md", NEW_REC)
        self.r.write(f"sim/records/{OLD}.md", OLD_SUPERSEDED)
        self.base = self.r.commit()
        self.r.write(f"sim/records/{OLD}.md", OLD_SUPERSEDED.replace(NEW, "other"))
        self.r.commit()
        self.assertFails("base status")

    def test_pointer_in_body_not_front_matter_fails(self):
        self.r.write(f"sim/records/{NEW}.md", NEW_REC)
        text = OLD_VALID.replace("status: valid", "status: superseded") + f"superseded_by: {NEW}\n"
        self.r.write(f"sim/records/{OLD}.md", text)
        self.r.commit()
        self.assertFails(OLD)

    def test_edit_then_revert_nets_to_nothing(self):
        self.r.write(f"sim/records/raw/{OLD}/out.log", "tampered\n")
        self.r.commit()
        self.r.write(f"sim/records/raw/{OLD}/out.log", "raw bytes\n")
        self.r.commit()
        self.assertEqual(self.check(), [])

    def test_merge_base_used_when_base_advanced(self):
        self.r.git("checkout", "-q", "-b", "topic")
        self.r.write(f"sim/records/{NEW}.md", NEW_REC)
        self.r.commit()
        self.r.git("checkout", "-q", "main")
        self.r.write("sim/records/2026-01-03-other-01.md", OLD_VALID)
        self.base = self.r.commit("main moves on")
        self.r.git("checkout", "-q", "topic")
        self.assertEqual(self.check(), [])

    def test_unresolvable_base_is_an_error(self):
        for bad in ("0" * 40, "no-such-ref"):
            with self.assertRaises(veh.HistoryError):
                veh.check_history(self.r.root, bad, "HEAD")

    def test_shallow_clone_without_base_is_an_error(self):
        self.r.write(f"sim/records/{NEW}.md", NEW_REC)
        self.r.commit()
        self.r.write("README.md", "x\n")
        self.r.commit()
        clone = Path(self._tmp.name) / "shallow"
        subprocess.run(
            ["git", "clone", "-q", "--depth", "1", f"file://{self.r.root}", str(clone)],
            check=True, capture_output=True,
        )
        with self.assertRaises(veh.HistoryError):
            veh.check_history(clone, self.base, "HEAD")

    def test_cli_exit_codes(self):
        tool = SIM_DIR / "tools" / "verify_evidence_history.py"

        def run(base):
            return subprocess.run(
                [sys.executable, str(tool), "--repo", str(self.r.root), "--base", base],
                capture_output=True, text=True,
            ).returncode

        self.assertEqual(run(self.base), 0)
        self.r.write(f"sim/records/raw/{OLD}/out.log", "tampered\n")
        self.r.commit()
        self.assertEqual(run(self.base), 1)
        self.assertEqual(run("0" * 40), 2)


if __name__ == "__main__":
    unittest.main()
