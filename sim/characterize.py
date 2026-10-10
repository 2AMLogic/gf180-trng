#!/usr/bin/env python3
"""Full ngspice PVT/corner characterization campaign behind
``docs/chipalooza/challenge-3-proposal.md``'s target-specification table
(issue #203).

    python3 sim/characterize.py                  # run the full campaign
    python3 sim/characterize.py --jobs 4          # override concurrency
    python3 sim/characterize.py --dry-run         # print the run_corners.py
                                                   # invocations without running them
    python3 sim/characterize.py --rows A F        # run only the campaigns that
                                                   # feed the named spec-table row(s)

This is a thin driver over ``sim/run_corners.py`` -- it changes nothing about
how a testbench runs or how an evidence record is written (``sim/README.md``'s
append-only format is unchanged). What it adds is a single command that,
from a clean clone with the gf180mcu PDK installed, regenerates the
transistor-level evidence the proposal's spec-table rows are re-derived from,
instead of a reviewer having to read the table's ``sim/`` citations and
reconstruct the ``run_corners.py`` invocations by hand.

See the top-level README's "Independent verification (Chipalooza)" section
for prerequisites, expected wall-clock, core count, and the full row ->
output-file mapping (also summarized in ROWS_NOT_COVERED below).

Scope: this script wraps the ngspice-based analog PVT sweep only -- the
"sim/ harness" sim/README.md and CLAUDE.md describe. Row D's required
liveness-sampler term (``sim/tb/sampler-core-liveness-active/``, #463/#528) is
NOT run here either: it has no tb.json by design and its full grid is opt-in
through ``klt sim --backend batch`` (see ROW_D_EVIDENCE below). Rows D/E/G's
digital-gate-level term (``sim/tb/digital-sta-power/``, needs OpenROAD),
Row H's health-test-cutoff formula (``design/health_test/rct_apt.py``) and
Row I's layout area estimate (``layout/floorplan/floorplan.py``, needs
klayout-tools) are each a different flow with different prerequisites and
are deliberately not invoked here; the README section names the command for
each of those too.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = REPO_ROOT / "sim"
RUN_CORNERS = SIM_DIR / "run_corners.py"

EXIT_OK = 0
EXIT_CAMPAIGN_FAILED = 1
EXIT_ENVIRONMENT = 3


@dataclass(frozen=True)
class Campaign:
    """One ``sim/run_corners.py`` invocation on the way to regenerating the
    evidence behind one or more challenge-3-proposal.md spec-table rows."""

    testbench: str
    rows: tuple[str, ...]
    extra_args: tuple[str, ...] = field(default_factory=tuple)
    note: str = ""

    def command(self, jobs: int) -> list[str]:
        return [
            sys.executable,
            str(RUN_CORNERS),
            self.testbench,
            "--jobs",
            str(jobs),
            *self.extra_args,
        ]


# Order matters only for readability of --dry-run/progress output; each step
# is independent and any subset can be re-run with --rows.
CAMPAIGNS: tuple[Campaign, ...] = (
    Campaign(
        "ro-array-core-pvt-q",
        rows=("A", "D"),
        note="Row A's per-ring frequency/current grid (27 points, the full "
        "covered {tt,ff,ss} x {-40,27,125} C x {2.97,3.30,3.63} V PVT grid); "
        "also the array's own active-power term for Row D via power_rollup.py.",
    ),
    Campaign(
        "ro-array-core-startup",
        rows=("F",),
        note="Oscillator start-up time across the same 27-point grid, feeding "
        "Row F (time-to-first-valid) via time_to_first_valid.py.",
    ),
    Campaign(
        "sampler-dff-active-current",
        rows=("D",),
        note="Sampler's own active-power term (45-point {mos} x {-40,27,125} C "
        "x {2.97,3.30,3.63} V grid) feeding Row D via power_rollup.py.",
    ),
    Campaign(
        "sampler-core-idle-leakage",
        rows=("E",),
        note="Analog idle-current term (45-point grid) feeding Row E via "
        "power_rollup.py.",
    ),
    Campaign(
        "sampler-array-digitize",
        rows=("C",),
        extra_args=("--corners", "tt", "--temps", "27", "--supply", "3.30", "--supply-tol", "0"),
        note="Row C raw-bitstream functional demonstration at tt/27C/3.30V -- "
        "one of the three corners a real bitstream exists for (see the "
        "proposal's Row C caveats: this is not an entropy measurement). "
        "Default seeds (1001..1003), the convention every prior record uses.",
    ),
    Campaign(
        "sampler-array-digitize",
        rows=("C",),
        extra_args=("--corners", "ss", "--temps", "-40", "--supply", "3.63", "--supply-tol", "0"),
        note="Row C raw-bitstream functional demonstration at ss/-40C/3.63V -- "
        "the second of the three corners a real bitstream exists for.",
    ),
    Campaign(
        "sampler-array-digitize",
        rows=("C",),
        extra_args=("--corners", "ss", "--temps", "125", "--supply", "3.63", "--supply-tol", "0"),
        note="Row C raw-bitstream functional demonstration at ss/+125C/3.63V -- "
        "the measured entropy-binding corner (#13, re-run in #406). Ten "
        "of ten bits were 1 at every seed there: a stuck-high observation, "
        "not an entropy measurement.",
    ),
)

# Row D (active power) is the sum of the terms power_rollup.LEDGER_TERMS names
# plus the digital section. This table declares, per required term, how a
# reviewer reproduces it, so a term cannot be required by the ledger and left
# out of the independent-verification recipe (sim/tests/test_characterize.py
# ties the two together offline). "flow" is "campaign" (a CAMPAIGNS testbench
# run by this script), "separate" (a different tool/backend, not run here).
LIVENESS_TB = "sampler-core-liveness-active"
LIVENESS_TOOL = "python3 sim/tools/liveness_sampler_power.py"
LIVENESS_SUMMARY = (
    "request-generation `emit [--check]`, opt-in batch run `run --outdir DIR` "
    "(klt sim --backend batch), record ingestion `record REPORT...`, via "
    + LIVENESS_TOOL
)
LIVENESS_COMMANDS: tuple[tuple[str, str], ...] = (
    (f"{LIVENESS_TOOL} plan", "print the declared 27-unit grid and method; offline"),
    (f"{LIVENESS_TOOL} emit --check", "fail if the committed request-grid.json drifted from the grid; offline"),
    (f"{LIVENESS_TOOL} emit", "(re)generate sim/tb/sampler-core-liveness-active/request-grid.json; offline"),
    (f"{LIVENESS_TOOL} run --outdir DIR", "OPT-IN: submit the whole grid with `klt sim --backend batch`; "
     "needs klt and batch-backend access; a failed submit is reported, never rerun locally"),
    (f"{LIVENESS_TOOL} analyze DIR/grid.report.json", "derive the ledger terms from the report; offline"),
    (f"{LIVENESS_TOOL} record DIR/grid.report.json", "mint NEW append-only records "
     "sim/records/<date>-sampler-core-liveness-active-NN.md; existing records are never edited"),
)


@dataclass(frozen=True)
class RowDEvidence:
    """How one Row D active-power term is reproduced."""

    term: str  # power_rollup.LEDGER_TERMS name, or "digital"
    flow: str  # "campaign" | "separate"
    testbenches: tuple[str, ...]
    how: str
    prerequisites: str


ROW_D_EVIDENCE: tuple[RowDEvidence, ...] = (
    RowDEvidence(
        "array", "campaign", ("ro-array-core-pvt-q",),
        "make characterize (this script)", "ngspice >= 46 + gf180mcu PDK",
    ),
    RowDEvidence(
        "sampler_raw", "campaign", ("sampler-dff-active-current",),
        "make characterize (this script)", "ngspice >= 46 + gf180mcu PDK",
    ),
    RowDEvidence(
        "liveness", "separate", (LIVENESS_TB,),
        "opt-in klt campaign: " + LIVENESS_SUMMARY,
        "klayout-tools (klt) with batch-backend access; NOT run by make characterize "
        "or CI, and without new records the committed ones are reused, not regenerated",
    ),
    RowDEvidence(
        "digital", "separate", ("digital-sta-power",),
        "python3 sim/tb/digital-sta-power/run_sta.py", "OpenROAD on PATH",
    ),
)


def row_d_summary() -> list[str]:
    """Lines for the dry-run's Row D section: every required evidence family."""
    lines = ["# Row D evidence (all required active-power terms; roll up with power_rollup.py):"]
    for e in ROW_D_EVIDENCE:
        where = "make characterize" if e.flow == "campaign" else "SEPARATE flow, not run by make characterize"
        lines.append(f"#   {e.term} [{where}]: {', '.join(e.testbenches)}")
        lines.append(f"#     how: {e.how}")
        lines.append(f"#     needs: {e.prerequisites}")
    lines.append(f"# liveness campaign commands (all from {LIVENESS_TOOL}):")
    for cmd, what in LIVENESS_COMMANDS:
        lines.append(f"#   {cmd}   -- {what}")
    return lines


# Rows this script does not produce evidence for, and where that evidence
# comes from instead -- kept alongside CAMPAIGNS so --dry-run's summary and
# the README table can be generated from (or checked against) one place.
ROWS_NOT_COVERED: dict[str, str] = {
    "B": "not a PVT sweep -- derived by sim/tools/jitter_energy_law.py and "
    "starved_cell_jitter_energy.py --check from the existing rostage-noise / "
    "ro-ring5-starved-jitter-long records (npm run check:spec).",
    "D (liveness term)": "REQUIRED power-ledger term, opt-in batch campaign -- "
    "not a tb.json, never swept locally: " + LIVENESS_SUMMARY + " (see the dry-run "
    "'Row D evidence' section or the README for the exact commands).",
    "D (digital term)": "gate-level, not ngspice: python3 sim/tb/digital-sta-power/run_sta.py "
    "(needs OpenROAD on PATH).",
    "E (digital term)": "same gate-level flow as the Row D digital term above.",
    "G": "gate-level Fmax: python3 sim/tb/digital-sta-power/run_sta.py (needs OpenROAD).",
    "H": "closed-form, no PVT dependency (rct_apt.py is a library, not a CLI): "
    'python3 -c "from design.health_test.rct_apt import c_rct, c_apt, H0; print(c_rct(H0), c_apt(H0))"',
    "I": "layout area, no PVT dependency: python3 layout/floorplan/floorplan.py "
    "(needs klayout-tools + PDK).",
}


def _default_jobs() -> int:
    return os.cpu_count() or 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="characterize.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--jobs", "-j", type=int, default=_default_jobs(),
        help="parallel ngspice runs per testbench, forwarded to run_corners.py "
        "-j (default: os.cpu_count())",
    )
    parser.add_argument(
        "--rows", nargs="+", metavar="ROW",
        help="only run campaigns feeding the named spec-table row letter(s) "
        "(e.g. --rows A F); default: the full campaign",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="print the run_corners.py invocations this would make, and the "
        "rows not covered, without running anything",
    )
    return parser


def _select(rows: list[str] | None) -> list[Campaign]:
    if not rows:
        return list(CAMPAIGNS)
    wanted = {r.strip().upper() for r in rows}
    covered = {r for c in CAMPAIGNS for r in c.rows}
    # Recognized rows handled by a separate flow, keyed by their leading letter.
    out_of_scope = {k.split()[0].upper(): v for k, v in ROWS_NOT_COVERED.items()}
    problems: list[str] = []
    for row in sorted(wanted - covered):
        if row in out_of_scope:
            problems.append(
                f"  row {row}: not produced by this script (separate flow): "
                f"{out_of_scope[row]}"
            )
        else:
            problems.append(f"  row {row}: unknown")
    if problems:
        raise SystemExit(
            "error: unsupported row selection; refusing to run a partial "
            f"campaign. Covered rows: {sorted(covered)}\n" + "\n".join(problems)
        )
    selected = [c for c in CAMPAIGNS if wanted & set(c.rows)]
    return selected


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    campaigns = _select(args.rows)

    if args.dry_run:
        print(f"# make characterize -- dry run (jobs={args.jobs})")
        for c in campaigns:
            print(f"\n# rows {','.join(c.rows)}: {c.note}")
            print("  " + " ".join(c.command(args.jobs)))
        if not args.rows or "D" in {r.strip().upper() for r in args.rows}:
            print()
            print("\n".join(row_d_summary()))
        if not args.rows:
            print("\n# rows not produced by this script (see README for how to regenerate them):")
            for row, where in ROWS_NOT_COVERED.items():
                print(f"#   {row}: {where}")
        return EXIT_OK

    # Fail fast with one clear message instead of every campaign step
    # failing for the same reason.
    env_check = subprocess.run(
        [sys.executable, str(RUN_CORNERS), "--check-env"], cwd=REPO_ROOT
    )
    if env_check.returncode != 0:
        print(
            "\ncharacterize: environment check failed (see above) -- "
            "install ngspice >= 46 and the gf180mcu PDK before running "
            "make characterize. See the README's 'Independent verification "
            "(Chipalooza)' section.",
            file=sys.stderr,
        )
        return EXIT_ENVIRONMENT

    print(f"\ncharacterize: {len(campaigns)} campaign step(s), jobs={args.jobs}\n")

    failures: list[str] = []
    for i, campaign in enumerate(campaigns, start=1):
        print(f"==== [{i}/{len(campaigns)}] {campaign.testbench}  ({','.join(campaign.rows)}) ====")
        print(f"     {campaign.note}")
        result = subprocess.run(campaign.command(args.jobs), cwd=REPO_ROOT)
        if result.returncode != 0:
            failures.append(f"{campaign.testbench} {' '.join(campaign.extra_args)}".strip())
        print()

    if failures:
        print("characterize: FAILED -- the following campaign step(s) did not succeed:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return EXIT_CAMPAIGN_FAILED

    print("characterize: all campaign steps completed; new records written under sim/records/.")
    print("Roll up the fresh evidence with:")
    print("  python3 sim/tools/power_rollup.py")
    print("  python3 sim/tools/time_to_first_valid.py")
    print("\nRow D is NOT fully reproduced by this run: the liveness and digital terms are")
    print("separate flows (see --dry-run --rows D). Run them, then re-run power_rollup.py.")
    print("\nRows not produced by this script (see README for how to regenerate them):")
    for row, where in ROWS_NOT_COVERED.items():
        print(f"  {row}: {where}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
