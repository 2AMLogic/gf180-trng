#!/usr/bin/env python3
"""Conservative unused-name check for `npm run lint` (#494).

Dead imports and dead simple locals kept coming back (#127, #129, #228,
#259, #478). The harness has no install step, so a third-party linter is not
an option; this is a deliberately narrow, standard-library-only checker
built on `ast` (locations, suppression, `__all__`, supported assignment
forms) and `symtable` (lexical-block ownership and reference information).

Reported:

  F401  an imported alias that is not referenced in its lexical block (or,
        for a binding that closures can capture, in any closure below it)
  F841  a simple named target of `Assign` / `AnnAssign` inside a function
        that is assigned but never read in that block or a child closure

Not reported (outside the supported contract, so never a finding):

  * `from ... import *`, `__future__` imports, imports in `__init__.py`,
    and any name beginning with `_`
  * module imports named by a module-level literal `__all__`
  * tuple/list destructuring, loop targets, `with ... as`, exception
    targets, pattern bindings, assignment expressions
  * a whole lexical block that directly calls exec / eval / globals /
    locals / vars (other blocks are still checked)
  * a statement carrying `# noqa`, `# noqa: F401` or `# noqa: F841`
    (as relevant) on one of its physical lines

A syntax error, or an AST / symbol-table block that cannot be matched
unambiguously, is a checker failure (exit 2) with file and line context --
never a silent skip. Findings exit 1; a clean tree exits 0.

Inputs are the git-tracked `*.py` files under design/, layout/, signoff/
and sim/. Usage:

  python3 -m sim.tools.unused_names --check
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import subprocess
import symtable
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

ROOT = Path(__file__).resolve().parents[2]

SCAN_DIRS = ("design", "layout", "signoff", "sim")
# Defensive: tracked files that live in tooling / environment trees.
EXCLUDED_PARTS = frozenset(
    {".loom", ".claude", ".agents", ".venv", "venv", "node_modules",
     "site-packages", "__pycache__"}
)
DYNAMIC_CALLS = frozenset({"exec", "eval", "globals", "locals", "vars"})
_COMP_NAMES = frozenset({"listcomp", "setcomp", "dictcomp", "genexpr", "lambda"})

_FUNC_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)
_COMP_NODES = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_NOQA = re.compile(r"#\s*noqa\b(?:\s*:\s*(?P<codes>[A-Za-z0-9]+(?:[\s,]+[A-Za-z0-9]+)*))?",
                   re.IGNORECASE)


class CheckerError(Exception):
    """The checker could not analyse a file (not a finding)."""

    def __init__(self, path: str, line: int, message: str) -> None:
        super().__init__(f"{path}:{line}: checker error: {message}")
        self.path = path
        self.line = line


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    col: int
    code: str
    name: str

    def format(self) -> str:
        what = "imported but unused" if self.code == "F401" else \
            "local variable is assigned to but never used"
        return f"{self.path}:{self.line}:{self.col}: {self.code} '{self.name}' {what}"


# --------------------------------------------------------------------------
# File discovery


def select_files(paths: Iterable[str]) -> list[str]:
    """Filter a tracked-file listing down to the in-scope Python files."""
    out = set()
    for raw in paths:
        parts = Path(raw).parts
        if not parts or parts[0] not in SCAN_DIRS or not raw.endswith(".py"):
            continue
        if EXCLUDED_PARTS.intersection(parts):
            continue
        out.add(Path(raw).as_posix())
    return sorted(out)


def tracked_files(root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", *SCAN_DIRS],
        capture_output=True, check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(
            f"error: git ls-files failed in {root}: "
            f"{proc.stderr.decode(errors='replace').strip()}"
        )
    return [p for p in proc.stdout.decode().split("\0") if p]


# --------------------------------------------------------------------------
# Scope ownership (AST side)


@dataclass
class _Owned:
    nodes: list[ast.AST]
    defs: list[ast.AST]  # FunctionDef / AsyncFunctionDef / ClassDef
    annotations: list[ast.AST]  # annotation expressions this block evaluates


def _header_nodes(node: ast.AST) -> list[ast.AST]:
    """Parts of a def/class evaluated in the *enclosing* scope."""
    out: list[ast.AST] = list(node.decorator_list)
    if isinstance(node, ast.ClassDef):
        out.extend(node.bases)
        out.extend(k.value for k in node.keywords)
        return out
    a = node.args
    out.extend(a.defaults)
    out.extend(d for d in a.kw_defaults if d is not None)
    for arg in (*a.posonlyargs, *a.args, *a.kwonlyargs, a.vararg, a.kwarg):
        if arg is not None and arg.annotation is not None:
            out.append(arg.annotation)
    if node.returns is not None:
        out.append(node.returns)
    return out


def _annotation_nodes(node: ast.AST) -> list[ast.AST]:
    if isinstance(node, _FUNC_NODES):
        a = node.args
        out = [arg.annotation
               for arg in (*a.posonlyargs, *a.args, *a.kwonlyargs, a.vararg, a.kwarg)
               if arg is not None and arg.annotation is not None]
        if node.returns is not None:
            out.append(node.returns)
        return out
    if isinstance(node, ast.AnnAssign):
        return [node.annotation]
    return []


def _own(roots: Iterable[ast.AST]) -> _Owned:
    """Every node a lexical block owns, not descending into nested blocks."""
    nodes: list[ast.AST] = []
    defs: list[ast.AST] = []
    annotations: list[ast.AST] = []
    stack = list(roots)
    while stack:
        n = stack.pop()
        nodes.append(n)
        annotations.extend(_annotation_nodes(n))
        if isinstance(n, (*_FUNC_NODES, ast.ClassDef)):
            defs.append(n)
            stack.extend(_header_nodes(n))
        elif isinstance(n, ast.Lambda):
            stack.extend(n.args.defaults)
            stack.extend(d for d in n.args.kw_defaults if d is not None)
        elif isinstance(n, _COMP_NODES):
            stack.append(n.generators[0].iter)  # evaluated in the parent
        else:
            stack.extend(ast.iter_child_nodes(n))
    return _Owned(nodes, defs, annotations)


# --------------------------------------------------------------------------
# Scope matching (symtable side)


def _blocks(table: symtable.SymbolTable) -> Iterator[symtable.SymbolTable]:
    """Child function/class blocks, seeing through helper blocks
    (type-parameter / annotation scopes) that newer Pythons interpose."""
    for child in table.get_children():
        kind = child.get_type()
        if kind not in ("function", "class"):
            if kind == "module":
                continue
            yield from _blocks(child)
        elif kind == "function" and child.get_name().strip("<>") in _COMP_NAMES:
            continue
        else:
            yield child


def _match(path: str, table: symtable.SymbolTable,
           defs: list[ast.AST]) -> list[tuple[symtable.SymbolTable, ast.AST]]:
    by_key: dict[tuple[str, str, int], list[symtable.SymbolTable]] = {}
    for child in _blocks(table):
        key = (child.get_name(), child.get_type(), child.get_lineno())
        by_key.setdefault(key, []).append(child)
    nodes: dict[tuple[str, str, int], list[ast.AST]] = {}
    for d in defs:
        kind = "class" if isinstance(d, ast.ClassDef) else "function"
        nodes.setdefault((d.name, kind, d.lineno), []).append(d)
    pairs = []
    for key in sorted(set(by_key) | set(nodes), key=lambda k: (k[2], k[0])):
        tabs, ns = by_key.get(key, []), nodes.get(key, [])
        if len(tabs) != 1 or len(ns) != 1:
            raise CheckerError(
                path, key[2],
                f"cannot match {key[1]} '{key[0]}' to one symbol-table block "
                f"({len(ns)} AST node(s), {len(tabs)} block(s)); refusing to guess")
        pairs.append((tabs[0], ns[0]))
    return pairs


def _used_below(table: symtable.SymbolTable, name: str, module_level: bool) -> bool:
    """Is `name`, bound in `table`, read by a block lexically below it?"""
    for child in table.get_children():
        if name in child.get_identifiers():
            sym = child.lookup(name)
            if sym.is_free():
                return True
            if sym.is_global():
                if module_level and sym.is_referenced():
                    return True
            elif child.get_type() != "class":
                continue  # shadowed: reads below here are not ours
        if _used_below(child, name, module_level):
            return True
    return False


def _target_names(target: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(target)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}


def _reads(node: ast.AST, bound: frozenset[str]) -> Iterator[str]:
    """Names read in an expression subtree, honouring the comprehension
    and lambda bindings that shadow them."""
    if isinstance(node, ast.Name):
        if isinstance(node.ctx, ast.Load) and node.id not in bound:
            yield node.id
    elif isinstance(node, _COMP_NODES):
        first, *rest = node.generators
        yield from _reads(first.iter, bound)
        inner = bound
        for i, gen in enumerate((first, *rest)):
            inner = inner | _target_names(gen.target)
            if i:
                yield from _reads(gen.iter, inner)
            yield from _reads(gen.target, inner)
            for cond in gen.ifs:
                yield from _reads(cond, inner)
        for part in ((node.key, node.value) if isinstance(node, ast.DictComp)
                     else (node.elt,)):
            yield from _reads(part, inner)
    elif isinstance(node, ast.Lambda):
        a = node.args
        params = {x.arg for x in (*a.posonlyargs, *a.args, *a.kwonlyargs, a.vararg, a.kwarg)
                  if x is not None}
        for d in (*a.defaults, *(d for d in a.kw_defaults if d is not None)):
            yield from _reads(d, bound)
        yield from _reads(node.body, bound | params)
    else:
        for child in ast.iter_child_nodes(node):
            yield from _reads(child, bound)


def _annotation_reads(ann: ast.AST) -> Iterator[str]:
    """Names in an annotation, including quoted (string) annotations."""
    for n in ast.walk(ann):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            yield n.id
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            try:
                inner = ast.parse(n.value.strip(), mode="eval")
            except SyntaxError:
                continue
            yield from _annotation_reads(inner)


def _supplementary_reads(owned: _Owned) -> set[str]:
    """Reads symtable does not attribute to the owning block.

    CPython 3.12+ inlines comprehensions into the enclosing block and drops
    their reads from `is_referenced`; with `from __future__ import
    annotations` (and for quoted annotations) annotation reads are not
    recorded at all. The AST supplies both, scope-exactly.
    """
    names: set[str] = set()
    for n in owned.nodes:
        if isinstance(n, _COMP_NODES):
            names.update(_reads(n, frozenset()))
    for ann in owned.annotations:
        names.update(_annotation_reads(ann))
    return names


# --------------------------------------------------------------------------
# Suppression comments


def _noqa_lines(path: str, source: str) -> dict[int, str | None]:
    """line -> None (blanket noqa) or the upper-cased code list."""
    out: dict[int, str | None] = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == tokenize.COMMENT:
                m = _NOQA.search(tok.string)
                if m:
                    codes = m.group("codes")
                    out[tok.start[0]] = codes.upper() if codes else None
    except (tokenize.TokenError, IndentationError) as exc:
        raise CheckerError(path, 1, f"tokenize failed: {exc}") from exc
    return out


def _suppressed(noqa: dict[int, str | None], first: int, last: int, code: str) -> bool:
    for line in range(first, last + 1):
        if line in noqa:
            codes = noqa[line]
            if codes is None or code in re.split(r"[\s,]+", codes):
                return True
    return False


# --------------------------------------------------------------------------
# Analysis


def _literal_all(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            hit = any(isinstance(t, ast.Name) and t.id == "__all__" for t in stmt.targets)
            value = stmt.value
        elif isinstance(stmt, (ast.AnnAssign, ast.AugAssign)):
            hit = isinstance(stmt.target, ast.Name) and stmt.target.id == "__all__"
            value = stmt.value
        else:
            continue
        if hit and isinstance(value, (ast.List, ast.Tuple, ast.Set)):
            names.update(e.value for e in value.elts
                         if isinstance(e, ast.Constant) and isinstance(e.value, str))
    return names


def _has_dynamic_call(nodes: list[ast.AST]) -> bool:
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id in DYNAMIC_CALLS for n in nodes)


def check_source(source: str, path: str = "<string>") -> list[Finding]:
    """Analyse one module's source; return findings in deterministic order."""
    try:
        tree = ast.parse(source, filename=path)
        top = symtable.symtable(source, path, "exec")
    except SyntaxError as exc:
        raise CheckerError(path, exc.lineno or 1, f"syntax error: {exc.msg}") from exc
    except (ValueError, RecursionError) as exc:
        raise CheckerError(path, 1, f"cannot parse: {exc}") from exc

    noqa = _noqa_lines(path, source)
    is_init = Path(path).name == "__init__.py"
    exported = _literal_all(tree)
    # Annotation reads anywhere in the file credit an import in any block:
    # symtable records none of them under `from __future__ import annotations`
    # or for quoted annotations. Conservative (no shadowing analysis).
    annotated = {name for n in ast.walk(tree) for ann in _annotation_nodes(n)
                 for name in _annotation_reads(ann)}
    findings: list[Finding] = []

    def visit(table: symtable.SymbolTable, roots: list[ast.AST], kind: str) -> None:
        owned = _own(roots)
        if not _has_dynamic_call(owned.nodes):
            # `del x` and `x += 1` touch the binding; treat both as uses.
            deleted = {n.id for n in owned.nodes
                       if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Del)}
            deleted.update(n.target.id for n in owned.nodes
                           if isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name))
            module_level = kind == "module"
            extra = _supplementary_reads(owned)

            def is_read(name: str) -> bool:
                sym = table.lookup(name)
                return (sym.is_referenced() or name in deleted or name in extra
                        or _used_below(table, name, module_level))

            if not is_init:
                for n in owned.nodes:
                    if isinstance(n, (ast.Import, ast.ImportFrom)):
                        _imports(n, table, module_level, is_read, exported)
            if kind == "function":
                for n in owned.nodes:
                    if isinstance(n, (ast.Assign, ast.AnnAssign)):
                        _assigns(n, table, is_read)
        for child_table, child in _match(path, table, owned.defs):
            child_kind = "class" if isinstance(child, ast.ClassDef) else "function"
            visit(child_table, list(child.body), child_kind)

    def _imports(stmt, table, module_level, is_read, exported) -> None:
        if isinstance(stmt, ast.ImportFrom) and stmt.module == "__future__":
            return
        for alias in stmt.names:
            if alias.name == "*":
                continue
            bound = alias.asname or alias.name.split(".")[0]
            if bound.startswith("_") or (module_level and bound in exported):
                continue
            if bound not in table.get_identifiers():
                raise CheckerError(path, stmt.lineno,
                                   f"import '{bound}' missing from its symbol table")
            sym = table.lookup(bound)
            if ((not module_level and sym.is_global()) or bound in annotated
                    or is_read(bound)):
                continue
            first = getattr(alias, "lineno", stmt.lineno)
            last = getattr(alias, "end_lineno", None) or first
            if (_suppressed(noqa, stmt.lineno, stmt.lineno, "F401")
                    or _suppressed(noqa, first, last, "F401")):
                continue
            findings.append(Finding(path, first, getattr(alias, "col_offset", stmt.col_offset),
                                    "F401", alias.name if not alias.asname else
                                    f"{alias.name} as {alias.asname}"))

    def _assigns(stmt, table, is_read) -> None:
        if isinstance(stmt, ast.Assign):
            targets = [t for t in stmt.targets if isinstance(t, ast.Name)]
        elif stmt.value is not None and isinstance(stmt.target, ast.Name):
            targets = [stmt.target]
        else:
            return
        for tgt in targets:
            if tgt.id.startswith("_"):
                continue
            if tgt.id not in table.get_identifiers():
                raise CheckerError(path, tgt.lineno,
                                   f"local '{tgt.id}' missing from its symbol table")
            sym = table.lookup(tgt.id)
            if (sym.is_global() or sym.is_free() or sym.is_parameter()
                    or sym.is_nonlocal() or is_read(tgt.id)):
                continue
            if _suppressed(noqa, stmt.lineno, stmt.end_lineno or stmt.lineno, "F841"):
                continue
            findings.append(Finding(path, tgt.lineno, tgt.col_offset, "F841", tgt.id))

    visit(top, list(tree.body), "module")
    return sorted(findings)


def check_files(root: Path, files: Iterable[str]) -> list[Finding]:
    findings: list[Finding] = []
    for rel in files:
        try:
            source = (root / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise CheckerError(rel, 1, f"cannot read: {exc}") from exc
        findings.extend(check_source(source, rel))
    return sorted(findings)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Report unused imports (F401) and simple unused function "
                    "locals (F841) in tracked first-party Python files.")
    ap.add_argument("--check", action="store_true", required=True,
                    help="scan and exit non-zero on findings")
    ap.add_argument("--root", type=Path, default=ROOT,
                    help="repository root (default: this checkout)")
    args = ap.parse_args(argv)

    files = select_files(tracked_files(args.root))
    try:
        findings = check_files(args.root, files)
    except CheckerError as exc:
        print(exc, file=sys.stderr)
        return 2
    for f in findings:
        print(f.format())
    if findings:
        print(f"unused_names: {len(findings)} finding(s) in {len(files)} file(s)",
              file=sys.stderr)
        return 1
    print(f"unused_names: OK ({len(files)} file(s) scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
