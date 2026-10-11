#!/usr/bin/env python3
"""Shared `--check`/CLI tail for the standalone layout generators.

Every generator that writes one committed `.gds` next to its own `build.py`
-- the seven cells under `layout/cells/*/`, the two rings under
`layout/rings/*/` and the `combiner_sampler` block under
`layout/blocks/combiner_sampler/` -- used to carry its own verbatim copy of
the same tail: `check()` (rebuild into a scratch stream, byte-compare it
against the committed one) and a `main()` exposing `--check` (plus, for the
generators that shell out to `klt`, the `--require-tools` flag and the
skip-when-absent tool probe). Ten near-identical copies meant a fix to the
check -- say, the scratch-file handling -- had to be applied ten times, so
#589 factored the tail into this module; each generator now binds the
factories below to its own module-level `check`/`main` names.

The factories, not a base class
-------------------------------
`layout/verify.py`'s `_STALENESS_CHECKS` calls each generator module's
`check()` with no arguments and treats a nonzero return as a hard failure,
so a generator's whole remaining obligation is: define `gds_path()` and
`build()`, then

    check = make_check(gds_path=gds_path, build=build, script=SCRIPT)
    main = make_main(
        check=check, gds_path=gds_path, build=build,
        description=__doc__.splitlines()[0],
    )

and the printed `MISSING:` / `STALE:` / `ok:` lines come out byte-identical
to the pre-#589 copies. Those messages (and the klt/PDK family's
`SKIP-AS-STALE:` / `SKIP:` / `FAIL:`) are part of the contract -- committed
sim/ evidence and docs quote them -- and must not be reworded.

Two families, deliberately separate
------------------------------------
- The hand-drawn cells (`make_check`/`make_main`) draw with stdlib Python
  only: `build(path)` returns the stream's bytes and needs no external
  tool, so `check()` has no skip path.
- The `klt`-assembled generators (`make_pdk_check`/`make_pdk_main`) build
  by running `klt` against a resolved PDK variant, so `check()` reports
  `SKIP-AS-STALE` when no gf180mcu PDK install is found, and `main()` probes
  for both tools up front (`--require-tools` turns that skip into a
  failure). `klt_version`/`resolve_pdk` are injected hooks (they live in
  `layout/_klt.py`) so this module stays stdlib-only and importable from
  both the flat-`sys.path` context the cells run in and the repo-root
  context the rings/block run in.

`layout/testcells/build.py` is intentionally not served from here: its
fixtures are known-bad by design and its `check_all()` walks several
streams in one call -- a different contract, not a stale copy of this one.
"""

from __future__ import annotations

import argparse
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

#: The `--check` flag's help text, identical in every generator's parser.
_CHECK_HELP = "verify the committed .gds matches this script, and exit"

#: The `--require-tools` flag's help text, same deal.
_REQUIRE_TOOLS_HELP = "fail instead of skipping when klt or the PDK is absent"


def gds_file(cell_dir: str, top_cell: str) -> str:
    """A generator's committed stream: `<cell_dir>/<top_cell>.gds`."""
    return os.path.join(cell_dir, f"{top_cell}.gds")


def make_check(
    *,
    gds_path: Callable[[], str],
    build: Callable[..., bytes],
    script: str,
) -> Callable[[], int]:
    """Return the stdlib-only generators' `check()`.

    `gds_path`/`build` are the generator module's own functions; `script` is
    the generator's repo-relative script path, quoted verbatim in the
    `MISSING:`/`STALE:` hints. Rebuilds into `<gds>.check` (removed again in
    a `finally`) and byte-compares against the committed stream.
    """

    def check() -> int:
        path = gds_path()
        shown = os.path.relpath(path, os.getcwd())
        if not os.path.exists(path):
            print(f"MISSING: {shown} -- run `python3 {script}`")
            return 1
        scratch = path + ".check"
        try:
            rebuilt = build(scratch)
        finally:
            if os.path.exists(scratch):
                os.remove(scratch)
        with open(path, "rb") as handle:
            committed = handle.read()
        if rebuilt != committed:
            print(
                f"STALE: {shown} does not match build.py "
                f"({len(committed)} bytes committed, {len(rebuilt)} rebuilt) -- "
                f"run `python3 {script}`"
            )
            return 1
        print(f"ok: {shown}")
        return 0

    return check


def make_main(
    *,
    check: Callable[[], int],
    gds_path: Callable[[], str],
    build: Callable[..., bytes],
    description: str,
) -> Callable[[list[str] | None], int]:
    """Return the stdlib-only generators' `main()` (`--check`, else write)."""

    def main(argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--check", action="store_true", help=_CHECK_HELP)
        args = parser.parse_args(argv)
        if args.check:
            return check()
        build()
        print(f"wrote {gds_path()}")
        return 0

    return main


def make_pdk_check(
    *,
    gds_path: Callable[[], Path],
    build: Callable[..., bytes],
    resolve_pdk: Callable[[], Any],
    work_dir: Path,
    top_cell: str,
    script: str,
) -> Callable[[], int]:
    """Return the klt/PDK-assembled generators' `check()`.

    Same byte-compare contract as `make_check`, but `build` runs `klt`
    against a resolved PDK variant (`build(variant, scratch_path)`), so a
    missing PDK install is reported as `SKIP-AS-STALE` -- a stale-looking
    stream the flow cannot re-verify here must not read as fresh. `klt`/the
    PDK are already confirmed present by the time `layout/verify.py` reaches
    this call, so the skip path exists for standalone runs only.
    """

    def check() -> int:
        path = gds_path()
        shown = os.path.relpath(path, os.getcwd())
        if not path.exists():
            print(f"MISSING: {shown} -- run `python3 {script}`")
            return 1
        pdk = resolve_pdk()
        if pdk is None:
            print(f"SKIP-AS-STALE: {shown} -- no gf180mcu PDK install found")
            return 1
        scratch = work_dir / f"{top_cell}.check.gds"
        rebuilt = build(pdk.variant, scratch)
        committed = path.read_bytes()
        if rebuilt != committed:
            print(
                f"STALE: {shown} does not match build.py "
                f"({len(committed)} bytes committed, {len(rebuilt)} rebuilt) -- "
                f"run `python3 {script}`"
            )
            return 1
        print(f"ok: {shown}")
        return 0

    return check


def make_pdk_main(
    *,
    check: Callable[[], int],
    gds_path: Callable[[], Path],
    build: Callable[..., bytes],
    resolve_pdk: Callable[[], Any],
    klt_version: Callable[[], Any],
    top_cell: str,
    description: str,
) -> Callable[[list[str] | None], int]:
    """Return the klt/PDK-assembled generators' `main()`.

    Probes for `klt` and the PDK before doing anything: with either absent
    it prints the missing tools and skips (exit 0), or fails under
    `--require-tools`. With both present, `--check` runs `check()` and the
    default path writes the committed stream.
    """

    def main(argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--check", action="store_true", help=_CHECK_HELP)
        parser.add_argument(
            "--require-tools", action="store_true", help=_REQUIRE_TOOLS_HELP
        )
        args = parser.parse_args(argv)

        version = klt_version()
        pdk = resolve_pdk()
        missing = []
        if version is None:
            missing.append("klayout-tools (`klt`) is not on PATH")
        if pdk is None:
            missing.append("no gf180mcu PDK install found (see sim/harness/pdk.py)")
        if missing:
            for line in missing:
                print(f"  - {line}")
            if args.require_tools:
                print("FAIL: --require-tools was given and the flow cannot run")
                return 1
            print(f"SKIP: {top_cell} build -- the tools above are not available.")
            return 0

        if args.check:
            return check()
        build(pdk.variant)
        print(f"wrote {gds_path()}")
        return 0

    return main
