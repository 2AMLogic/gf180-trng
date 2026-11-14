"""One copy of the ``--scenario`` / ``--no-write`` CLI the scenario testbenches share.

``sim/tb/conditioner-crc32``, ``sim/tb/health-test-fault-injection``,
``sim/tb/ring-liveness-fault-injection`` and ``sim/tb/interface-regfile`` each
carried a byte-identical ``main()``: build the two-flag parser, resolve the
scenario list, collect git provenance, run each scenario, print a header, and
mint one record per result unless ``--no-write`` (#888). That is one contract --
*how a scenario testbench is invoked and how its evidence gets minted* -- and it
now lives here once. The per-scenario result lines stay per-testbench and are
injected as ``print_result``, as do ``run_scenario`` and ``write_record``.

The repository root and the records directory are **arguments, not derived
here**: a runner resolves them from its own module-level constants
(``REPO_ROOT``, ``SIM_DIR``), and resolving them relative to this package
instead would change the provenance and the record path of every minted
record. The record bytes a runner mints are therefore exactly what it minted
before this module existed.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Mapping

from . import report as _report


def run_scenarios(
    argv: list[str] | None,
    *,
    description: str | None,
    scenarios: Mapping[str, object],
    run_scenario: Callable[[str], dict],
    write_record: Callable[[dict, Path, dict], Path],
    print_result: Callable[[dict], None],
    repo_root: Path,
    records_dir: Path,
) -> int:
    """Run the requested scenarios and return the process exit code.

    ``--scenario`` is repeatable and restricted to ``scenarios``; omitting it
    runs all of them in declaration order. ``--no-write`` prints results
    without minting evidence records.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--scenario",
        action="append",
        choices=sorted(scenarios),
        help="run only this scenario (repeatable); default is all of them",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="print the results without minting evidence records",
    )
    args = parser.parse_args(argv)

    names = args.scenario or list(scenarios)
    git = _report.git_provenance(repo_root)

    for name in names:
        result = run_scenario(name)
        print(f"== {name} ==")
        print_result(result)
        if not args.no_write:
            path = write_record(result, records_dir, git)
            print(f"   record: {path.relative_to(repo_root)}")
    return 0
