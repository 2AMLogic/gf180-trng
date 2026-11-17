import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sim.tools import lint_shell


class SelectScripts(unittest.TestCase):
    def test_excludes_vendored_and_non_shell(self) -> None:
        got = lint_shell.select_scripts([
            "sim/selftest.sh", ".loom/hooks/a.sh", ".claude/x/b.sh",
            "loom.sh", "README.md", "sim/tools/x.py"])
        self.assertEqual(got, ["loom.sh", "sim/selftest.sh"])

    def test_extensionless_bash_shebang_is_selected(self) -> None:
        # Regression for #993: .github/scripts/install-xschem (no .sh
        # extension, `#!/usr/bin/env bash`) must reach shellcheck.
        got = lint_shell.select_scripts(
            [".github/scripts/install-xschem", "sim/selftest.sh"],
            first_line=lambda p: "#!/usr/bin/env bash\n")
        self.assertEqual(got,
                         [".github/scripts/install-xschem", "sim/selftest.sh"])

    def test_direct_shell_shebangs_are_selected(self) -> None:
        got = lint_shell.select_scripts(
            ["a/run", "b/run"], first_line=lambda p: {
                "a/run": "#!/bin/sh\n", "b/run": "#!/bin/bash -eu\n"}[p])
        self.assertEqual(got, ["a/run", "b/run"])

    def test_non_shell_shebang_is_not_selected(self) -> None:
        got = lint_shell.select_scripts(
            ["sim/run_corners.py"], first_line=lambda _: "#!/usr/bin/env python3\n")
        self.assertEqual(got, [])

    def test_no_shebang_is_not_selected(self) -> None:
        got = lint_shell.select_scripts(
            ["Makefile"], first_line=lambda _: "all:\n")
        self.assertEqual(got, [])

    def test_empty_or_blank_first_line_is_not_selected(self) -> None:
        got = lint_shell.select_scripts(
            ["empty", "blank"], first_line=lambda _: "")
        self.assertEqual(got, [])

    def test_vendored_extensionless_bash_is_excluded(self) -> None:
        got = lint_shell.select_scripts(
            [".loom/bin/loom", ".claude/x/tool"],
            first_line=lambda _: "#!/usr/bin/env bash\n")
        self.assertEqual(got, [])

    def test_crlf_shebang_is_selected(self) -> None:
        got = lint_shell.select_scripts(
            [".github/scripts/crlf"], first_line=lambda _: "#!/usr/bin/env bash\r\n")
        self.assertEqual(got, [".github/scripts/crlf"])


class ReadFirstLine(unittest.TestCase):
    def _line_of(self, text: str, tmp: Path) -> str:
        path = tmp / "probe"
        path.write_bytes(text.encode())
        return lint_shell.read_first_line(str(path), root=tmp)

    def test_reads_first_line(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self._line_of("#!/usr/bin/env bash\nx\n", Path(d)),
                             "#!/usr/bin/env bash\n")

    def test_empty_file_is_empty_string(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self._line_of("", Path(d)), "")

    def test_crlf_file_reads_normalized_line(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self._line_of("#!/bin/sh\r\n", Path(d)),
                             "#!/bin/sh\n")

    def test_missing_file_is_empty_string(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(lint_shell.read_first_line("nope", root=Path(d)), "")


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
