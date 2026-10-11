"""Content identity of the PDK model files a generated deck consumes (#562).

``Pdk.version`` is read from the installation's ``SOURCES`` metadata, so two
installations carrying the same label but different model bytes (a locally
patched model card, a partially updated install) cannot be told apart by it.
This module records *what the models actually were*: starting from the two
model entry points every deck composed by ``runner.compose_deck`` names --

* ``libs.tech/ngspice/design.ngspice``, pulled in whole by ``.include``, and
* ``libs.tech/ngspice/sm141064.ngspice``, pulled in by ``.lib <file>
  <section>`` once per selected library section --

it follows every ``.include``/``.inc`` and ``.lib <file> <section>``
reference reachable from the selected content, and hashes each file read
with SHA-256. Only the content ngspice would load is followed: for a
``.lib`` reference that is the named section (``.lib <name>`` ... ``.endl``)
of the referenced file, and for an ``.include`` it is the whole file except
section definitions (which an include defines but does not load). A file is
hashed in full whenever any part of it is read.

The result is a :class:`ModelManifest`: the entry points and sections, the
sorted ``(PDK-relative path, sha256)`` list of every file reached, and a list
of *problems* -- references that are missing, or written in a form this
scanner does not follow (parameterized or environment-variable paths,
unexpected argument counts, paths that leave the PDK variant directory,
file-loading directives other than ``.include``/``.lib``). A manifest with
problems is still recorded, but is marked incomplete rather than claiming a
complete model identity. Paths are relative to the PDK variant directory, so
an identical set of files yields an identical identity wherever the PDK is
installed.

Limits (also stated in ``sim/README.md``): ngspice resolves a relative
include against the including file's directory first, and this scanner
assumes that is where it is found (ngspice's fallbacks -- the working
directory, ``sourcepath`` -- are not modelled). The identity is captured
before execution and re-checked before a record is published; an edit that
is made and reverted entirely between those two checks is not detected.

Stdlib only, like the rest of the harness.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

#: File name of the manifest kept in each record's raw directory.
MANIFEST_NAME = "pdk-models.json"
#: Name the post-run manifest is saved under when a mid-run change is found.
CHANGED_MANIFEST_NAME = "pdk-models.after-run.json"
SCHEMA = "gf180-trng/pdk-model-manifest/v1"

# Directives that load another file and that this scanner deliberately does
# not follow; seeing one makes the identity incomplete instead of silently
# narrower than what ngspice loaded.
_UNFOLLOWED_DIRECTIVES = frozenset({".incl", ".includex", ".libx", ".osdi", ".hdl", ".load"})
# Interactive commands inside a ``.control`` block that read a file.
_UNFOLLOWED_CONTROL = frozenset({"source", "pre_osdi", "osdi", "codemodel", "load"})

_TOKEN_RE = re.compile(r"'[^']*'|\"[^\"]*\"|\S+")


@dataclass(frozen=True)
class ModelManifest:
    """Deterministic description of the model files one deck consumes."""

    entries: tuple[dict, ...]
    files: tuple[tuple[str, str], ...]
    problems: tuple[str, ...] = field(default_factory=tuple)

    @property
    def complete(self) -> bool:
        return not self.problems

    def payload(self) -> dict:
        """Everything the identity covers -- no host paths, no timestamps."""
        return {
            "schema": SCHEMA,
            "entries": [dict(e) for e in self.entries],
            "files": [{"path": p, "sha256": d} for p, d in self.files],
            "problems": list(self.problems),
        }

    @property
    def identity(self) -> str:
        return identity_of(self.payload())

    def to_json_bytes(self) -> bytes:
        doc = dict(self.payload())
        doc["complete"] = self.complete
        doc["identity"] = self.identity
        return (json.dumps(doc, indent=2, sort_keys=True) + "\n").encode("utf-8")

    def describe_differences(self, other: "ModelManifest") -> list[str]:
        """Human-readable lines saying how ``other`` differs from ``self``."""
        lines: list[str] = []
        before, after = dict(self.files), dict(other.files)
        for path in sorted(set(before) | set(after)):
            if path not in after:
                lines.append(f"{path}: no longer reached")
            elif path not in before:
                lines.append(f"{path}: newly reached (sha256 {after[path]})")
            elif before[path] != after[path]:
                lines.append(f"{path}: sha256 {before[path]} -> {after[path]}")
        if self.entries != other.entries:
            lines.append("entry points or selected sections differ")
        for problem in sorted(set(other.problems) - set(self.problems)):
            lines.append(f"new problem: {problem}")
        for problem in sorted(set(self.problems) - set(other.problems)):
            lines.append(f"problem no longer present: {problem}")
        return lines


def identity_of(payload: dict) -> str:
    """``sha256:<hex>`` over the canonical JSON of a manifest payload."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def identity_from_document(doc: dict) -> str:
    """Recompute the identity of a parsed ``pdk-models.json`` document."""
    payload = {key: doc.get(key) for key in ("schema", "entries", "files", "problems")}
    return identity_of(payload)


def _logical_lines(text: str) -> list[tuple[int, str]]:
    """Join ``+`` continuation lines; return ``(first physical line, text)``."""
    out: list[tuple[int, str]] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("+") and out:
            start, prior = out[-1]
            out[-1] = (start, prior + " " + stripped[1:])
            continue
        out.append((number, stripped))
    return out


def _tokens(line: str) -> list[str]:
    """Split a directive into tokens, dropping an inline ``$ ``/``;`` comment."""
    tokens: list[str] = []
    for token in _TOKEN_RE.findall(line):
        if token == "$" or token.startswith(";"):
            break
        tokens.append(token)
    return tokens


def _unquote(token: str) -> str:
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "'\"":
        return token[1:-1]
    return token


class _Scanner:
    def __init__(self, variant_dir: Path):
        self.root = Path(os.path.normpath(os.path.abspath(variant_dir)))
        self.hashes: dict[str, str] = {}
        self.texts: dict[str, str | None] = {}
        self.problems: set[str] = set()
        self.visited: set[tuple[str, str | None]] = set()

    def rel(self, path: Path) -> str | None:
        normal = Path(os.path.normpath(os.path.abspath(path)))
        try:
            return PurePosixPath(normal.relative_to(self.root)).as_posix()
        except ValueError:
            return None

    def read(self, rel: str) -> str | None:
        if rel not in self.texts:
            path = self.root / rel
            try:
                data = path.read_bytes()
            except (FileNotFoundError, IsADirectoryError, NotADirectoryError):
                self.texts[rel] = None
            else:
                self.hashes[rel] = hashlib.sha256(data).hexdigest()
                # latin-1 maps every byte, so a stray non-UTF-8 byte in a
                # comment can never abort the scan; the hash covers the bytes.
                self.texts[rel] = data.decode("latin-1")
        return self.texts[rel]

    def visit(self, rel: str, section: str | None, origin: str) -> None:
        key = (rel, section.lower() if section is not None else None)
        if key in self.visited:
            return
        self.visited.add(key)
        text = self.read(rel)
        if text is None:
            self.problems.add(f"missing file {rel} (referenced from {origin})")
            return
        lines = _logical_lines(text)
        if section is None:
            region = self._outside_sections(rel, lines)
        else:
            region = self._section(rel, lines, section)
            if region is None:
                self.problems.add(
                    f"missing section {section!r} in {rel} (referenced from {origin})"
                )
                return
        self._follow(rel, region)

    def _outside_sections(self, rel: str, lines):
        region = []
        depth = 0
        for number, line in lines:
            head = line.split(None, 1)[0].lower() if line else ""
            if head == ".lib" and len(_tokens(line)) == 2:
                depth += 1
                continue
            if head == ".endl":
                depth = max(0, depth - 1)
                continue
            if depth == 0:
                region.append((number, line))
        return region

    def _section(self, rel: str, lines, section: str):
        wanted = section.lower()
        region = None
        for number, line in lines:
            head = line.split(None, 1)[0].lower() if line else ""
            if region is None:
                tokens = _tokens(line)
                if head == ".lib" and len(tokens) == 2 and _unquote(tokens[1]).lower() == wanted:
                    region = []
                continue
            if head == ".endl":
                return region
            if head == ".lib" and len(_tokens(line)) == 2:
                self.problems.add(
                    f"{rel}:{number}: nested .lib section definition inside {section!r}"
                )
                continue
            region.append((number, line))
        if region is not None:
            self.problems.add(f"{rel}: section {section!r} is not closed by .endl")
        return region

    def _follow(self, rel: str, region) -> None:
        in_control = False
        for number, line in region:
            if not line or line.startswith("*"):
                continue
            tokens = _tokens(line)
            if not tokens:
                continue
            head = tokens[0].lower()
            where = f"{rel}:{number}"
            if head == ".control":
                in_control = True
                continue
            if head == ".endc":
                in_control = False
                continue
            if in_control:
                if head in _UNFOLLOWED_CONTROL:
                    self.problems.add(f"{where}: unsupported file-loading command {tokens[0]!r}")
                continue
            if head in (".include", ".inc"):
                if len(tokens) != 2:
                    self.problems.add(f"{where}: unsupported {tokens[0]} form ({len(tokens) - 1} arguments)")
                    continue
                self._reference(rel, where, tokens[1], None)
            elif head == ".lib":
                if len(tokens) != 3:
                    self.problems.add(f"{where}: unsupported .lib form ({len(tokens) - 1} arguments)")
                    continue
                self._reference(rel, where, tokens[1], _unquote(tokens[2]))
            elif head in _UNFOLLOWED_DIRECTIVES:
                self.problems.add(f"{where}: unsupported file-loading directive {tokens[0]!r}")

    def _reference(self, rel: str, where: str, token: str, section: str | None) -> None:
        target = _unquote(token)
        if not target or any(ch in target for ch in "{}$~`"):
            self.problems.add(f"{where}: unsupported parameterized path {target!r}")
            return
        if section is not None and any(ch in section for ch in "{}$"):
            self.problems.add(f"{where}: unsupported parameterized section {section!r}")
            return
        if os.path.isabs(target):
            resolved = Path(target)
        else:
            resolved = (self.root / rel).parent / target
        target_rel = self.rel(resolved)
        if target_rel is None:
            # Never echo an absolute literal: it would be a host path.
            shown = "an absolute path" if os.path.isabs(target) else repr(target)
            self.problems.add(f"{where}: reference to {shown} outside the PDK variant directory")
            return
        self.visit(target_rel, section, where)


def build_manifest(variant_dir: Path, entries: list[tuple[Path, list[str] | None]]) -> ModelManifest:
    """Scan ``entries`` -- ``(entry file, sections or None for .include)`` --
    under ``variant_dir`` and return their :class:`ModelManifest`."""
    scanner = _Scanner(variant_dir)
    entry_docs: list[dict] = []
    for path, sections in entries:
        rel = scanner.rel(path)
        if rel is None:
            scanner.problems.add("entry point outside the PDK variant directory")
            continue
        if sections is None:
            entry_docs.append({"file": rel, "mode": "include"})
            scanner.visit(rel, None, "deck")
        else:
            entry_docs.append({"file": rel, "mode": "lib", "sections": list(sections)})
            for section in sections:
                scanner.visit(rel, section, "deck")
    return ModelManifest(
        entries=tuple(entry_docs),
        files=tuple(sorted(scanner.hashes.items())),
        problems=tuple(sorted(scanner.problems)),
    )


def manifest_for_deck(pdk, sections) -> ModelManifest:
    """The manifest for a deck ``runner.compose_deck`` builds against ``pdk``
    with library ``sections`` (``tb.extra_lib_sections`` or the corner's)."""
    return build_manifest(
        pdk.path,
        [(pdk.design_include, None), (pdk.model_lib, list(sections))],
    )
