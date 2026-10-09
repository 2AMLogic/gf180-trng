"""Tests for sim/tools/verify_record_checksums.py's git-aware half and CLI.

The checksum half is covered through ``harness.report`` in test_report.py.
These cases pin the committed-to-git check (``verify_one`` with a ``tracked``
set from ``git_tracked_raw_files``) and ``main()``'s exit paths, against a
real ``git init`` in a temporary directory -- never the repository's own
records corpus. The module globals REPO_ROOT, SIM_DIR and RECORDS_DIR are
pointed at the temporary repository for the duration of each test.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(SIM_DIR / "tools"))

import verify_record_checksums as vrc  # noqa: E402

GIT = shutil.which("git")

STEM = "2026-01-01-example-01"


def _record_text(raw_rel: str, files: dict[str, bytes]) -> str:
    lines = ["---", "status: valid", "raw:", f"  path: {raw_rel}", "  files:"]
    for name, data in files.items():
        lines.append(f"    - {name}  sha256:{hashlib.sha256(data).hexdigest()}")
    lines += ["---", "", "# Example record", ""]
    return "\n".join(lines)


@unittest.skipIf(GIT is None, "git is not installed")
class _TempRepoCase(unittest.TestCase):
    """A throwaway git repo laid out as sim/records/ + sim/records/raw/<stem>/."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name).resolve()
        # Keep git from walking up into an enclosing repository and from
        # honouring a GIT_DIR/GIT_WORK_TREE inherited from the caller (e.g. a
        # hook), so every git call below sees only the temporary repo.
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env["GIT_CEILING_DIRECTORIES"] = str(self.repo.parent)
        env["LC_ALL"] = "C"  # git messages asserted below are the untranslated ones
        env.pop("LANGUAGE", None)
        patcher = mock.patch.dict(os.environ, env, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.sim = self.repo / "sim"
        self.records = self.sim / "records"
        self.raw_dir = self.records / "raw" / STEM
        self.raw_dir.mkdir(parents=True)
        for name, value in (
            ("REPO_ROOT", self.repo), ("SIM_DIR", self.sim), ("RECORDS_DIR", self.records),
        ):
            old = getattr(vrc, name)
            setattr(vrc, name, value)
            self.addCleanup(setattr, vrc, name, old)

    def git(self, *args: str) -> None:
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.com",
             "-c", "commit.gpgsign=false", *args],
            cwd=self.repo, check=True, capture_output=True, text=True,
        )

    def init_repo(self) -> None:
        self.git("init", "-q")

    def write_record(self, files: dict[str, bytes]) -> Path:
        for name, data in files.items():
            (self.raw_dir / name).write_bytes(data)
        raw_rel = str(self.raw_dir.relative_to(self.repo)) + "/"
        path = self.records / f"{STEM}.md"
        path.write_text(_record_text(raw_rel, files))
        return path

    def run_cli(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = vrc.main(argv)
        return rc, out.getvalue(), err.getvalue()


class CommittedFileCheckTests(_TempRepoCase):
    FILES = {"deck.cir": b"* deck\n", "out.log": b"result 1.0\n"}

    def test_all_raw_files_committed_verifies(self):
        self.init_repo()
        record = self.write_record(self.FILES)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "record")
        tracked = vrc.git_tracked_raw_files()
        self.assertEqual(
            tracked, {f"sim/records/raw/{STEM}/deck.cir", f"sim/records/raw/{STEM}/out.log"}
        )
        self.assertEqual(vrc.verify_one(record, tracked), [])

    def test_untracked_raw_file_is_reported_not_committed(self):
        self.init_repo()
        record = self.write_record(self.FILES)
        self.git("add", str(record), str(self.raw_dir / "deck.cir"))
        self.git("commit", "-q", "-m", "record without its log")
        problems = vrc.verify_one(record, vrc.git_tracked_raw_files())
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("out.log: not committed", problems[0])
        self.assertIn(f"git add sim/records/raw/{STEM}/out.log", problems[0])

    def test_untracked_raw_file_passes_when_git_check_is_skipped(self):
        """The pair to the case above: the failure is the git half, not checksums."""
        self.init_repo()
        record = self.write_record(self.FILES)
        self.assertEqual(vrc.verify_one(record, None), [])

    def test_staged_but_uncommitted_file_counts_as_tracked(self):
        self.init_repo()
        record = self.write_record(self.FILES)
        self.git("add", "-A")  # staged, no commit yet
        self.assertEqual(vrc.verify_one(record, vrc.git_tracked_raw_files()), [])

    def test_empty_tracked_set_flags_every_raw_file(self):
        """A tracked set that names nothing must not read as "all committed"."""
        self.init_repo()
        record = self.write_record(self.FILES)
        problems = vrc.verify_one(record, set())
        self.assertEqual(sorted(p.split(":", 1)[0] for p in problems), ["deck.cir", "out.log"])

    def test_absolute_paths_in_tracked_set_do_not_satisfy_the_check(self):
        """`tracked` is repo-relative; an absolute path must not match by accident."""
        self.init_repo()
        record = self.write_record({"deck.cir": b"* deck\n"})
        absolute = {str(self.raw_dir / "deck.cir")}
        self.assertEqual(len(vrc.verify_one(record, absolute)), 1)


class GitFailureTests(_TempRepoCase):
    """Without a usable git, the check fails closed and says git is why."""

    def test_outside_a_repository_raises(self):
        # No `git init`: the ceiling stops git finding any enclosing repo.
        with self.assertRaises(vrc.GitTrackingError) as ctx:
            vrc.git_tracked_raw_files()
        self.assertIn("git ls-files", str(ctx.exception))
        self.assertIn("not a git repository", str(ctx.exception).lower())

    def test_git_missing_raises(self):
        self.init_repo()
        with mock.patch.dict(os.environ, {"PATH": str(self.repo / "no-such-bin")}):
            with self.assertRaises(vrc.GitTrackingError) as ctx:
                vrc.git_tracked_raw_files()
        self.assertIn("cannot run git", str(ctx.exception))

    def test_cli_outside_a_repository_exits_2_naming_git(self):
        record = self.write_record({"deck.cir": b"* deck\n"})
        rc, out, err = self.run_cli([str(record)])
        self.assertEqual(rc, 2)
        self.assertIn("cannot check that raw output is committed", err)
        self.assertIn("--no-git", err)
        self.assertNotIn("not committed (git add", err)
        self.assertNotIn("PASS", out)

    def test_cli_outside_a_repository_with_no_git_passes(self):
        record = self.write_record({"deck.cir": b"* deck\n"})
        rc, out, _err = self.run_cli(["--no-git", str(record)])
        self.assertEqual(rc, 0)
        self.assertIn("PASS: 1 record(s) match their raw output.", out)


class MainExitPathTests(_TempRepoCase):
    def setUp(self):
        super().setUp()
        self.init_repo()

    def test_no_records_exits_0(self):
        rc, out, _err = self.run_cli([])
        self.assertEqual(rc, 0)
        self.assertIn("no records to check", out)

    def test_missing_record_path_exits_1(self):
        missing = self.records / "2026-01-01-absent-01.md"
        rc, _out, err = self.run_cli(["--no-git", str(missing)])
        self.assertEqual(rc, 1)
        self.assertIn(f"FAIL {missing}: no such record", err)

    def test_checksum_mismatch_exits_1(self):
        record = self.write_record({"deck.cir": b"* deck\n"})
        self.git("add", "-A")
        (self.raw_dir / "deck.cir").write_bytes(b"* overwritten\n")
        rc, _out, err = self.run_cli([str(record)])
        self.assertEqual(rc, 1)
        self.assertIn("deck.cir: sha256 on disk", err)

    def test_unreadable_record_exits_1(self):
        path = self.records / f"{STEM}.md"
        path.write_bytes(b"---\n\xff\xfe not utf-8\n---\n")
        rc, _out, err = self.run_cli([str(path)])
        self.assertEqual(rc, 1)
        self.assertIn("cannot read record", err)

    def test_uncommitted_raw_file_exits_1(self):
        record = self.write_record({"deck.cir": b"* deck\n"})
        rc, _out, err = self.run_cli([str(record)])
        self.assertEqual(rc, 1)
        self.assertIn("deck.cir: not committed", err)

    def test_clean_committed_record_exits_0(self):
        self.write_record({"deck.cir": b"* deck\n"})
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "record")
        rc, out, err = self.run_cli([])  # default: every record under RECORDS_DIR
        self.assertEqual(rc, 0, err)
        self.assertIn(f"ok   {STEM}.md", out)
        self.assertIn("PASS: 1 record(s) match their committed raw output.", out)


if __name__ == "__main__":
    unittest.main()
