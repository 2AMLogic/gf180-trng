import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sim.tools import _git_files


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True,
                   capture_output=True)


class TrackedFiles(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        _git(self.root, "init", "-q")
        (self.root / "a.sh").write_text("")
        (self.root / "d").mkdir()
        (self.root / "d" / "b.py").write_text("")
        _git(self.root, "add", "-A")

    def test_lists_all_tracked(self) -> None:
        self.assertEqual(sorted(_git_files.tracked_files(self.root)),
                         ["a.sh", "d/b.py"])

    def test_pathspec_restricts(self) -> None:
        self.assertEqual(_git_files.tracked_files(self.root, "*.sh"),
                         ["a.sh"])

    def test_not_a_repository_raises_git_error(self) -> None:
        with tempfile.TemporaryDirectory() as bare:
            with self.assertRaises(_git_files.GitError) as ctx:
                _git_files.tracked_files(Path(bare))
        self.assertIn("failed (exit", str(ctx.exception))

    def test_missing_git_raises_git_error(self) -> None:
        with mock.patch.object(_git_files.subprocess, "run",
                               side_effect=FileNotFoundError("git")):
            with self.assertRaises(_git_files.GitError) as ctx:
                _git_files.tracked_files(self.root)
        self.assertIn("cannot run git", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
