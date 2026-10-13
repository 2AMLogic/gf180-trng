import io
import unittest
from contextlib import redirect_stdout

from sim.tools import lint_shell


class SelectScripts(unittest.TestCase):
    def test_excludes_vendored_and_non_shell(self) -> None:
        got = lint_shell.select_scripts([
            "sim/selftest.sh", ".loom/hooks/a.sh", ".claude/x/b.sh",
            "loom.sh", "README.md", "sim/tools/x.py"])
        self.assertEqual(got, ["loom.sh", "sim/selftest.sh"])


class Availability(unittest.TestCase):
    def _run(self, require: bool) -> tuple[int, str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lint_shell.run(require, which=lambda _n: None)
        return rc, buf.getvalue()

    def test_missing_tool_skips(self) -> None:
        rc, out = self._run(False)
        self.assertEqual(rc, 0)
        self.assertIn("shellcheck unavailable", out)

    def test_missing_tool_fails_when_required(self) -> None:
        rc, out = self._run(True)
        self.assertEqual(rc, 1)
        self.assertIn("shellcheck unavailable", out)


if __name__ == "__main__":
    unittest.main()
