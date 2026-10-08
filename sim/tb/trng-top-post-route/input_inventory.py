"""The local source files one post-route run actually consumes (#350).

``run_demo.py`` pins this inventory into the run's raw ``sources.json`` and
``signoff/check.py`` re-hashes every entry against the working tree, so the
published item-7 digital citation goes stale when any RTL source, included
header, testbench file, stimulus module or behavioural-model dependency
changes -- not only the netlist and SDF.

The inventory is *derived*, not listed twice:

* Verilog: the RTL sources the reference leg is handed, plus every file their
  ``include`` directives resolve to (transitively), searched first next to the
  including file and then in the include directories the request passes.
* Python: the behavioural model, the stimulus and the cocotb modules, plus
  every repository-local module they import (transitively, found by parsing
  the imports, so a new ``import`` is picked up without editing a list).
* The testbench directory's own ``*.py`` files and ``run_demo.py`` itself,
  which build the request and the comparison.

Cell-library, simulator and tool versions are not source files and are not
covered here; ``signoff/check.py`` says so in ``ITEM7_LIMITS``.

Stdlib only.
"""

from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path

_INCLUDE = re.compile(r'^\s*`include\s+"([^"]+)"', re.MULTILINE)


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def python_search_roots(repo_root: Path) -> list[Path]:
    """Directories the run puts on ``sys.path`` (design/*, sim, sim/tb/*)."""
    roots = [repo_root, repo_root / "sim"]
    for parent in (repo_root / "design", repo_root / "sim" / "tb"):
        roots += sorted(p for p in parent.iterdir() if p.is_dir()) if parent.is_dir() else []
    return roots


def _resolve_module(dotted: str, roots: list[Path]) -> list[Path]:
    """Files a ``import a.b.c`` loads inside ``roots`` (packages included)."""
    parts = dotted.split(".")
    for root in roots:
        found: list[Path] = []
        base = root
        for i, part in enumerate(parts):
            pkg = base / part
            mod = base / f"{part}.py"
            if i == len(parts) - 1 and mod.is_file():
                found.append(mod)
                break
            if pkg.is_dir():
                if (pkg / "__init__.py").is_file():
                    found.append(pkg / "__init__.py")
                base = pkg
                if i == len(parts) - 1:
                    break
            else:
                found = []
                break
        if found:
            return found
    return []


def _python_imports(path: Path, roots: list[Path]) -> list[Path]:
    tree = ast.parse(path.read_text(), filename=str(path))
    out: list[Path] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out += _resolve_module(alias.name, roots)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            out += _resolve_module(node.module, roots)
            for alias in node.names:  # `from pkg import submodule`
                out += [
                    p for p in _resolve_module(f"{node.module}.{alias.name}", roots)
                    if p.name != "__init__.py"
                ]
    return out


def _verilog_includes(path: Path, include_dirs: list[Path]) -> list[Path]:
    out: list[Path] = []
    for name in _INCLUDE.findall(path.read_text()):
        for d in [path.parent, *include_dirs]:
            if (d / name).is_file():
                out.append(d / name)
                break
        else:
            raise FileNotFoundError(f"{path}: `include \"{name}\" not found")
    return out


def collect(
    repo_root: Path,
    rtl_sources: list[Path],
    include_dirs: list[Path],
    python_entries: list[Path],
    extra_files: list[Path],
) -> dict[str, str]:
    """Return ``{repo-relative path: sha256}`` of every consumed local file."""
    repo_root = repo_root.resolve()
    roots = python_search_roots(repo_root)
    seen: set[Path] = set()

    def walk(path: Path, expand) -> None:
        path = path.resolve()
        if path in seen:
            return
        seen.add(path)
        for dep in expand(path):
            walk(dep, expand)

    for p in rtl_sources:
        walk(p, lambda f: _verilog_includes(f, include_dirs))
    for p in python_entries:
        walk(p, lambda f: _python_imports(f, roots))
    seen.update(p.resolve() for p in extra_files)
    return {
        str(p.relative_to(repo_root)): _sha256(p)
        for p in sorted(seen)
        if p.is_file()
    }
