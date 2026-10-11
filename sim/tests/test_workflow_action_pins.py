#!/usr/bin/env python3
"""Guard: every third-party GitHub Action is pinned to a full commit SHA.

A mutable ref (tag, branch, short SHA, or no ref) lets upstream change the code
a workflow runs without any diff here. Local `uses: ./...` actions are exempt.
Parsing is deliberately narrow: only `uses:` / `- uses:` lines are inspected,
and any value that is not a recognised form fails with a clear message rather
than escaping the check. Stdlib only.
"""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[2] / ".github" / "workflows"

USES_LINE = re.compile(r"^\s*(?:-\s+)?uses:\s*(?P<value>.*?)\s*$")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
OWNER_REPO_PATH = re.compile(r"^[\w.-]+/[\w.-]+(?:/[\w./-]+)?$")


def _strip_comment(value: str) -> str:
    return value.split(" #", 1)[0].strip()


def check_reference(value: str) -> str | None:
    """Return a problem description for one `uses:` value, or None if fine."""
    ref = _strip_comment(value)
    if not ref:
        return "empty uses: value"
    if ref[0] in "\"'":
        return f"quoted uses: value {ref!r} is unsupported; write it unquoted"
    if ref.startswith("./"):
        return None  # local action
    if ref.startswith("docker://"):
        return f"docker reference {ref!r} is unsupported; pin by digest in a reviewed change"
    if "@" not in ref:
        return f"{ref!r} has no ref; pin to a 40-character commit SHA"
    name, _, pin = ref.partition("@")
    if not OWNER_REPO_PATH.match(name):
        return f"unsupported action reference {ref!r}"
    if not FULL_SHA.match(pin):
        return f"{name}@{pin} is not a full 40-character lowercase hex commit SHA"
    return None


def scan(path: Path) -> list[str]:
    problems = []
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        match = USES_LINE.match(line)
        if match:
            problem = check_reference(match["value"])
            if problem:
                problems.append(f"{path.name}:{lineno}: {problem}")
    return problems


def workflow_files(root: Path) -> list[Path]:
    return sorted(p for ext in ("*.yml", "*.yaml") for p in root.glob(ext))


def scan_all(root: Path) -> list[str]:
    return [p for f in workflow_files(root) for p in scan(f)]


SHA = "a" * 40


class CheckReferenceFixtures(unittest.TestCase):
    def test_rejected(self) -> None:
        for value in (
            "actions/checkout@v4",
            "actions/checkout@v4.4.0",
            "actions/checkout@main",
            "actions/checkout",
            "actions/checkout@",
            "actions/checkout@" + "a" * 7,
            "actions/checkout@" + "a" * 39,
            "actions/checkout@" + "a" * 41,
            "actions/checkout@" + "A" * 40,
            "actions/checkout@" + "g" * 40,
            "docker://alpine:3",
            "'actions/checkout@v4'",
            "",
        ):
            with self.subTest(value=value):
                self.assertIsNotNone(check_reference(value))

    def test_accepted(self) -> None:
        for value in (
            f"actions/checkout@{SHA}",
            f"actions/checkout@{SHA} # v4.4.0",
            f"actions/cache/restore@{SHA}",
            "./.github/actions/local",
            "./",
        ):
            with self.subTest(value=value):
                self.assertIsNone(check_reference(value))


class ScanFixtures(unittest.TestCase):
    def _scan(self, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "w.yml"
            path.write_text(text)
            return scan(path)

    def test_list_and_plain_syntax(self) -> None:
        text = (
            "steps:\n"
            "  - uses: actions/checkout@v4\n"
            "  - name: x\n"
            "    uses: actions/cache@main\n"
            f"  - uses: actions/setup-python@{SHA}\n"
            "  - uses: ./local\n"
        )
        problems = self._scan(text)
        self.assertEqual(len(problems), 2)
        self.assertIn("w.yml:2:", problems[0])
        self.assertIn("w.yml:4:", problems[1])

    def test_commented_out_reference_ignored(self) -> None:
        self.assertEqual(self._scan("# uses: actions/checkout@v4\n"), [])

    def test_new_workflow_file_is_inventoried(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ci.yml").write_text(f"- uses: actions/checkout@{SHA}\n")
            self.assertEqual(scan_all(root), [])
            (root / "new.yaml").write_text("- uses: actions/checkout@v4\n")
            self.assertEqual(
                [workflow_files(root)[i].name for i in range(2)], ["ci.yml", "new.yaml"]
            )
            problems = scan_all(root)
            self.assertEqual(len(problems), 1)
            self.assertIn("new.yaml:1:", problems[0])


class RepositoryWorkflows(unittest.TestCase):
    def test_workflows_exist(self) -> None:
        names = {p.name for p in workflow_files(WORKFLOWS)}
        self.assertTrue({"ci.yml", "pdk-nightly.yml"} <= names)

    def test_all_actions_pinned(self) -> None:
        problems = scan_all(WORKFLOWS)
        self.assertEqual(problems, [], "\n" + "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
