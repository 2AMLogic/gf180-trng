#!/usr/bin/env python3
"""Relative markdown link guard for `npm run lint` (#570).

Relative links in tracked documents are the audit trail for spec claims
(decision-record citations, evidence cross-references), and nothing else
checks that they resolve. This is a deliberately narrow, standard-library-only
checker: file existence only, no anchor validation.

Checked:

  * inline links and images, `[text](target)` / `![alt](target)`, with an
    optional `"title"` and optional `<...>` around the target
  * reference-style definitions, `[label]: target`

A target resolves relative to the document's own directory; a target starting
with `/` resolves relative to the repository root (as GitHub renders it). The
`#fragment` and `?query` parts are dropped and `%XX` escapes decoded before
the lookup. A target resolves if it names a git-tracked file, or a directory
containing one -- an untracked local file does not count, because it would
not exist for anyone else reading the document.

Not checked (outside the supported contract, so never a finding):

  * URLs with a scheme (`https:`, `mailto:`, ...), protocol-relative `//...`
    targets and pure `#anchor` links
  * anything inside a fenced code block (``` or ~~~) or an inline code span
  * HTML `<a href>` / `<img src>` and indented code blocks
  * documents under EXCLUDED_PREFIXES, and (document, target) pairs listed in
    ALLOWLIST -- each with its reason

Findings are printed as `file:line: broken link: target` and exit 1; a clean
tree exits 0; a document that cannot be read exits 2. Usage:

  python3 -m sim.tools.verify_markdown_links --check
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Iterator
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _git_files  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

# Tracked document trees this check does not scan, with the reason.
EXCLUDED_PREFIXES = {
    "sim/records/": (
        "append-only evidence (sim/README.md): a broken link in a committed "
        "record cannot be fixed in place, only superseded"
    ),
    ".loom/": "installed Loom surfaces, overwritten on resync; fixes belong upstream",
    ".claude/": "installed agent surfaces, overwritten on resync; fixes belong upstream",
    ".agents/": "installed agent surfaces, overwritten on resync; fixes belong upstream",
}

# (document, target as written) -> why the missing target is acceptable.
# Prefer fixing or unlinking; an entry here must name a real reason.
ALLOWLIST: dict[tuple[str, str], str] = {
    ("ratification/ee-key/SKILL.md", "dry-runs/"): (
        "generated file (its MANIFEST.md says do not hand-edit; regenerate "
        "instead); the link names the output directory a dry run creates, "
        "which does not exist until the first dry run is filed"
    ),
}

_FENCE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
_CODE_SPAN = re.compile(r"(?P<ticks>`+)(?:.+?)(?P=ticks)")
# `](target)` or `](target "title")` / `](<target> 'title')`.
_INLINE = re.compile(
    r"\]\(\s*(?:<(?P<angle>[^>\n]*)>|(?P<bare>[^\s()<>]+))"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
)
# `[label]: target` with only an optional title after it, as CommonMark
# requires -- so prose that happens to open a line with `[DR-0009]: it ...`
# is not a definition. Footnote definitions (`[^note]: ...`) are not links.
_REFDEF = re.compile(
    r"^ {0,3}\[(?P<label>[^\]^][^\]]*)\]:\s*(?:<(?P<angle>[^>]*)>|(?P<bare>\S+))"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*$"
)
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    target: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: broken link: {self.target}"


class CheckerError(Exception):
    """A document could not be read (not a finding)."""


def tracked_files(root: Path) -> list[str]:
    return sorted(_git_files.tracked_files(root))


def select_documents(files: Iterable[str]) -> list[str]:
    return sorted(
        f for f in files
        if f.lower().endswith(".md")
        and not any(f.startswith(prefix) for prefix in EXCLUDED_PREFIXES)
    )


def _strip_code_spans(line: str) -> str:
    return _CODE_SPAN.sub(lambda m: " " * len(m.group(0)), line)


def link_targets(text: str) -> Iterator[tuple[int, str]]:
    """Yield (1-based line, target as written) for every link outside code."""
    fence: str | None = None
    for lineno, raw in enumerate(text.splitlines(), start=1):
        m = _FENCE.match(raw)
        if fence is not None:
            # A closing fence uses the same character, at least as long, and
            # carries no info string.
            if m and m.group("fence")[0] == fence[0] and len(m.group("fence")) >= len(fence) \
                    and not m.group("info").strip():
                fence = None
            continue
        if m and not (m.group("fence")[0] == "`" and "`" in m.group("info")):
            fence = m.group("fence")
            continue
        line = _strip_code_spans(raw)
        ref = _REFDEF.match(line)
        if ref:
            yield lineno, ref.group("angle") if ref.group("angle") is not None else ref.group("bare")
            continue
        for link in _INLINE.finditer(line):
            angle = link.group("angle")
            yield lineno, angle if angle is not None else link.group("bare")


def _is_external(target: str) -> bool:
    return (not target or target.startswith("#") or target.startswith("//")
            or bool(_SCHEME.match(target)))


def resolve(doc: str, target: str) -> str | None:
    """Repo-relative POSIX path a relative target points at (None = not checked).

    A path that climbs above the repository root resolves to `..`-prefixed
    text, which never matches a tracked file and so is reported.
    """
    if _is_external(target):
        return None
    path = unquote(re.split(r"[#?]", target, maxsplit=1)[0])
    if not path:
        return None
    if path.startswith("/"):
        joined = PurePosixPath(path.lstrip("/"))
    else:
        joined = PurePosixPath(doc).parent / path
    parts: list[str] = []
    for part in joined.parts:
        if part in ("", "."):
            continue
        if part == ".." and parts and parts[-1] != "..":
            parts.pop()
        else:
            parts.append(part)
    return "/".join(parts)


def _existing(files: Iterable[str]) -> set[str]:
    present: set[str] = {""}
    for f in files:
        present.add(f)
        parent = PurePosixPath(f).parent
        while str(parent) != ".":
            present.add(str(parent))
            parent = parent.parent
    return present


def check_documents(root: Path, docs: Iterable[str], files: Iterable[str],
                    allowlist: dict[tuple[str, str], str] | None = None) -> list[Finding]:
    allow = ALLOWLIST if allowlist is None else allowlist
    present = _existing(files)
    findings: list[Finding] = []
    for doc in docs:
        try:
            text = (root / doc).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise CheckerError(f"{doc}:1: checker error: cannot read: {exc}") from exc
        for lineno, target in link_targets(text):
            resolved = resolve(doc, target)
            if resolved is None or resolved in present or (doc, target) in allow:
                continue
            findings.append(Finding(doc, lineno, target))
    return sorted(findings)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Report relative markdown links in tracked documents whose "
                    "target is not a tracked file or directory.")
    ap.add_argument("--check", action="store_true", required=True,
                    help="scan and exit non-zero on findings")
    ap.add_argument("--root", type=Path, default=ROOT,
                    help="repository root (default: this checkout)")
    args = ap.parse_args(argv)

    try:
        files = tracked_files(args.root)
    except _git_files.GitError as exc:
        print(exc, file=sys.stderr)
        return 2
    docs = select_documents(files)
    try:
        findings = check_documents(args.root, docs, files)
    except CheckerError as exc:
        print(exc, file=sys.stderr)
        return 2
    for f in findings:
        print(f.format())
    if findings:
        print(f"verify_markdown_links: {len(findings)} broken link(s) in "
              f"{len(docs)} document(s)", file=sys.stderr)
        return 1
    print(f"verify_markdown_links: OK ({len(docs)} document(s) scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
