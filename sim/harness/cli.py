"""Command line front end: ``python3 sim/run_corners.py <testbench> [...]``.

One invocation runs a testbench across a PVT grid (process corner x supply
x temperature) and writes ONE evidence record per grid point into
``sim/records/``, per the format ratified in ``sim/README.md``. No manual
netlist edits are needed to move between corners.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import HARNESS_VERSION, corners as corners_mod, pdk_models, report, runner, testbench as tb_mod
from .pdk import PdkNotFound, find_all_variant_dirs, find_pdk
from .runner import NgspiceMissing

REPO_ROOT = Path(__file__).resolve().parents[2]
SIM_DIR = REPO_ROOT / "sim"
TB_DIR = SIM_DIR / tb_mod.TB_ROOT_DIRNAME
RECORDS_DIR = SIM_DIR / report.RECORDS_DIRNAME
WORK_DIR = SIM_DIR / ".work"

EXIT_OK = 0
EXIT_CHECK_FAILED = 1
EXIT_ENVIRONMENT = 3
# Records were written but their raw.files checksums no longer match the
# files on disk -- the evidence is not trustworthy and must not be committed.
EXIT_RECORD_CORRUPT = 4
# A PDK model file the decks consume changed between the pre-run capture and
# the pre-publication re-check (#562): the affected records are withheld.
EXIT_PDK_MODELS_CHANGED = 5


def _resolve_tb_path(argument: str) -> Path:
    candidates = [Path(argument), TB_DIR / argument]
    for candidate in candidates:
        manifest = candidate if candidate.name == tb_mod.MANIFEST_NAME else candidate / tb_mod.MANIFEST_NAME
        if manifest.is_file():
            return candidate
    raise FileNotFoundError(
        f"no testbench {argument!r}; tried: " + ", ".join(str(c) for c in candidates)
        + ".\nAvailable: " + ", ".join(p.name for p in tb_mod.discover(TB_DIR))
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_corners.py",
        description="Run a testbench across the gf180mcu PVT corner grid; "
        "one evidence record per grid point, per sim/README.md.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 sim/run_corners.py smoke-op\n"
            "  python3 sim/run_corners.py corner-sanity-nfet-id --corner-set mos\n"
            "  python3 sim/run_corners.py noise-floor-resistor --corners tt --seeds 1 2 3\n"
            "  python3 sim/run_corners.py --list\n"
            "  python3 sim/run_corners.py --check-env\n"
        ),
    )
    parser.add_argument(
        "testbench", nargs="?", metavar="TESTBENCH",
        help="testbench slug under sim/tb/ (i.e. sim/tb/<slug>/tb.json)",
    )
    parser.add_argument("--list", action="store_true", help="list testbenches and corners")
    parser.add_argument("--check-env", action="store_true", help="report ngspice / PDK availability and exit")
    parser.add_argument(
        "--print-env", action="store_true",
        help="print shell exports for the resolved PDK",
    )
    parser.add_argument("--corners", nargs="+", metavar="NAME", help="explicit corner or corner-set names")
    parser.add_argument("--corner-set", choices=sorted(corners_mod.CORNER_SETS), help="shorthand for --corners <set>")
    parser.add_argument("--temps", nargs="+", type=float, metavar="C", help="temperatures in degrees C")
    parser.add_argument("--supply", type=float, metavar="V", help="nominal supply in volts")
    parser.add_argument("--supply-tol", type=float, metavar="FRAC", help="supply tolerance as a fraction, e.g. 0.10")
    parser.add_argument(
        "--seeds", nargs="+", type=int, metavar="N",
        help="explicit seed list for a stochastic testbench (one run per seed, per PVT point); "
             "seeds must be distinct",
    )
    parser.add_argument(
        "-j", "--jobs", type=int, default=1,
        help="parallel ngspice runs across the whole (PVT point x seed) task list "
             "(default 1 = sequential). Records are still written in grid order.",
    )
    parser.add_argument(
        "--timeout", type=int, default=runner.DEFAULT_TIMEOUT_S,
        help="per-run ngspice wall-clock bound in seconds, enforced by an OS-level "
             "watchdog (timeout(1)/gtimeout, see --check-env) so it survives even if "
             "run_corners.py itself is killed; a killed run reports as FAILED-TIMEOUT",
    )
    parser.add_argument("--supersedes", default="", metavar="RECORD", help="prior record stem this run corrects or replaces")
    parser.add_argument("--no-write", action="store_true", help="run but do not record evidence (debugging only)")
    parser.add_argument("--quiet", action="store_true", help="only print the summary")
    parser.add_argument("--version", action="version", version=f"gf180-trng harness {HARNESS_VERSION}")
    return parser


def cmd_list() -> int:
    print("Testbenches (sim/tb/<slug>/tb.json):")
    for directory in tb_mod.discover(TB_DIR):
        try:
            tb = tb_mod.load(directory)
            print(f"  {directory.name:<28} {tb.description or tb.slug}")
        except Exception as exc:  # noqa: BLE001 - surface bad manifests, keep listing
            print(f"  {directory.name:<28} !! {exc}")
    print("\nCorner sets:")
    for name, members in sorted(corners_mod.CORNER_SETS.items()):
        print(f"  {name:<12} {', '.join(members)}")
    print("\nCorners:")
    for name, corner in corners_mod.CORNERS.items():
        print(f"  {name:<12} {corner.description}")
    return EXIT_OK


def cmd_check_env() -> int:
    status = EXIT_OK
    try:
        version = runner.ngspice_version()
        print(f"ngspice : OK   {version}")
    except NgspiceMissing as exc:
        print(f"ngspice : MISSING\n{exc}")
        status = EXIT_ENVIRONMENT
    watchdog = runner.timeout_bin()
    if watchdog is not None:
        print(f"watchdog: OK   {watchdog}")
    else:
        # Not fatal -- ngspice still runs, just without the OS-level bound
        # (see issue #83) that lets a hung run get killed even if this
        # harness process itself dies mid-run. --check-env stays EXIT_OK so
        # this degraded-but-functional mode doesn't block CI/smoke runs.
        print(
            "watchdog: MISSING (no timeout(1)/gtimeout on PATH -- a hung ngspice run\n"
            "          will only be bounded while run_corners.py itself stays alive.\n"
            "          macOS: brew install coreutils   Debian: apt-get install coreutils)"
        )
    try:
        pdk = find_pdk()
        print(f"PDK     : OK   {pdk.path} (open_pdks {pdk.version}, via {pdk.source})")
        print(f"  models: {pdk.model_lib}")
        winner = pdk.path.resolve()
        for shadowed_path, shadowed_source in find_all_variant_dirs(pdk.variant):
            if shadowed_path.resolve() == winner:
                continue
            root = shadowed_source.removeprefix("search_root:")
            print(f"  note: {pdk.variant} also found under {root} ({shadowed_source}) -- shadowed, not used")
    except PdkNotFound as exc:
        print(f"PDK     : MISSING\n{exc}")
        status = EXIT_ENVIRONMENT
    return status


def cmd_print_env() -> int:
    try:
        pdk = find_pdk()
    except PdkNotFound as exc:
        print(f"# gf180mcu PDK not found\n# {exc.args[0].splitlines()[0]}", file=sys.stderr)
        return EXIT_ENVIRONMENT
    print(f'export PDK_ROOT="{pdk.path.parent}"')
    print(f'export PDK="{pdk.variant}"')
    print(f'export GF180_PDK_PATH="{pdk.path}"')
    return EXIT_OK


def _fmt(value) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _deck_sections(tb, point) -> tuple[str, ...]:
    """The model-library sections ``runner.compose_deck`` ``.lib``-includes."""
    return tuple(tb.extra_lib_sections or point.corner.sections)


def _model_caveats(manifest) -> list[str]:
    caveats = [
        f"PDK model identity (pdk_content) covers only the {len(manifest.files)} "
        f"file(s) listed in {pdk_models.MANIFEST_NAME}, reached from the deck's "
        ".include/.lib entry points; it was captured before the run and re-checked "
        "before this record was written, so an edit made and reverted between "
        "those two checks is not detected (see sim/README.md).",
    ]
    if not manifest.complete:
        caveats.append(
            "PDK model identity is INCOMPLETE -- references the scanner could not "
            "follow: " + "; ".join(manifest.problems)
        )
    return caveats


def _default_caveats(tb, point, jobs: int = 1, manifest=None) -> list[str]:
    caveats = [
        f"Single corner ({point.corner.name} / {point.vdd:.2f} V / {point.temp_c:g} C). "
        "Says nothing about any other corner.",
    ]
    if manifest is not None:
        caveats.extend(_model_caveats(manifest))
    if jobs > 1:
        caveats.append(
            f"Run concurrently (-j {jobs}); wall_time is the SUMMED per-run ngspice "
            "cost for this point, not elapsed time, and is inflated relative to a "
            "quiet machine by contention between concurrent runs."
        )
    if tb.design_netlist is not None:
        caveats.append(
            f"DUT is the schematic-derived netlist {tb.design_netlist.name}; netlist.sha above "
            "is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it "
            "to the schematic it claims to come from."
        )
    elif tb.netlist.parent == tb.directory:
        caveats.append(
            "Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet "
            "for this block, so testbench.path and netlist.path are the same self-contained "
            "demo fragment. Real DUT netlists will get their own netlist.path once design/ "
            "has content."
        )
    if tb.extra_lib_sections:
        caveats.append(
            f"corner.process ({point.corner.name}) is bookkeeping only for this testbench -- "
            f"the actually-loaded model section is {', '.join(tb.extra_lib_sections)} "
            "(see pdk.models), which replaces the plain per-family corner sections."
        )
    # Testbench-specific method limits, declared once in tb.json rather than
    # re-typed into every record of a PVT sweep. sim/README.md: "Stating a
    # limit is not a weakness in the record; an unstated limit is a defect."
    caveats.extend(tb.caveats)
    return caveats


def run(args: argparse.Namespace) -> int:
    tb_path = _resolve_tb_path(args.testbench)
    tb = tb_mod.load(tb_path)

    try:
        pdk = find_pdk()
        ngspice = runner.ngspice_version()
    except (PdkNotFound, NgspiceMissing) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    corner_names = args.corners or ([args.corner_set] if args.corner_set else list(tb.corners))
    corner_list = corners_mod.resolve_corners(corner_names)
    temperatures = args.temps if args.temps is not None else list(tb.temperatures_c)
    nominal = args.supply if args.supply is not None else tb.nominal_supply_v
    tolerance = args.supply_tol if args.supply_tol is not None else tb.supply_tolerance
    try:
        supplies = corners_mod.supply_points(nominal, tolerance)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ENVIRONMENT
    points = corners_mod.build_grid(corner_list, temperatures, supplies)

    if tb.stochastic:
        seeds = args.seeds or list(range(1, tb.default_runs + 1))
    else:
        if args.seeds:
            print(
                f"error: {tb.slug} is not stochastic (analysis_type={tb.analysis_type!r}); "
                "--seeds is only meaningful for stochastic testbenches",
                file=sys.stderr,
            )
            return EXIT_ENVIRONMENT
        seeds = None

    # Validate the complete execution plan -- distinct seeds, distinct PVT
    # points, non-colliding output ids -- before anything is allocated: no
    # record stem is reserved, no scratch directory is created and no
    # simulator is launched for a plan that would double-count a seed or
    # schedule two points into the same deck/log paths. The serial (-j 1)
    # and parallel paths below share this one plan.
    try:
        corners_mod.validate_grid(points)
        plan = runner.plan_runs(tb, seeds)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    git = report.git_provenance(REPO_ROOT)

    # PDK model-content identity (#562), captured once per distinct set of
    # library sections BEFORE any simulator starts; each point is re-checked
    # against it before its record is published (see _emit).
    pre_manifests: dict[tuple[str, ...], pdk_models.ModelManifest] = {}
    for point in points:
        sections = _deck_sections(tb, point)
        if sections not in pre_manifests:
            pre_manifests[sections] = pdk_models.manifest_for_deck(pdk, sections)

    if not args.quiet:
        print(f"testbench : {tb.slug}" + (f"  ({tb.description})" if tb.description else ""))
        print(f"pdk       : {pdk.variant} @ {pdk.version}  ({pdk.path})")
        print(f"ngspice   : {ngspice}")
        print(f"corners   : {', '.join(c.name for c in corner_list)}")
        print(f"temps (C) : {', '.join(_fmt(t) for t in temperatures)}")
        print(f"supply (V): {', '.join(_fmt(v) for v in supplies)} (nominal {_fmt(nominal)} +/-{tolerance * 100:g}%)")
        print(f"points    : {len(points)}")
        if seeds:
            print(f"seeds     : {seeds}")
        for sections, manifest in pre_manifests.items():
            state = (
                "complete" if manifest.complete
                else f"INCOMPLETE, {len(manifest.problems)} unfollowed reference(s)"
            )
            print(
                f"models    : {manifest.identity}  ({len(manifest.files)} files, {state}; "
                f"sections {' '.join(sections)})"
            )
        print()

    overall_ok = True
    models_changed: list[tuple[str, Path, list[str]]] = []
    written_paths: list[Path] = []
    written_records: list[dict] = []

    completed_utc = _dt.datetime.now(_dt.timezone.utc)
    date_str = completed_utc.strftime("%Y-%m-%d")

    if args.no_write:
        stems: list[str] = ["" for _ in points]
        # Every invocation gets its own scratch directory, created atomically
        # by mkdtemp, so two overlapping --no-write runs of the same testbench
        # and point (even from separate processes) never share, delete or
        # overwrite each other's deck/log. Nothing is ever removed here: a
        # run's scratch output is retained for diagnostics and is only ever
        # this invocation's own. See sim/README.md ("Scratch directories").
        scratch_parent = WORK_DIR / tb.slug
        scratch_parent.mkdir(parents=True, exist_ok=True)
        scratch_root = Path(tempfile.mkdtemp(prefix="run-", dir=scratch_parent))
        workdirs = [scratch_root / p.corner_id for p in points]
        if not args.quiet:
            print(f"scratch   : {scratch_root}  (retained; not evidence)")
            print()
    else:
        # Reserved for the whole grid up front so concurrent points cannot
        # race for the same append-only sequence number, and reserved by
        # *creating* raw/<stem>/ (an atomic mkdir) rather than by scanning
        # for a free number, so a second run_corners.py invocation for the
        # same date+slug cannot be handed a stem this one is using -- an
        # hours-long run must claim its numbers before it starts, not when
        # it finishes.
        stems = report.reserve_record_stems(RECORDS_DIR, date_str, tb.slug, len(points))
        workdirs = [RECORDS_DIR / report.RAW_DIRNAME / stem for stem in stems]

    jobs = max(1, int(args.jobs))
    tasks = [(pi, seed, index) for pi in range(len(points)) for seed, index in plan]
    results_by_point: dict[int, list] = {pi: [None] * len(plan) for pi in range(len(points))}
    remaining_by_point: dict[int, int] = {pi: len(plan) for pi in range(len(points))}

    def _work(task):
        point_index, seed, run_index = task
        result = runner.run_one(
            tb, pdk, points[point_index], workdirs[point_index],
            seed=seed, run_index=run_index, timeout_s=args.timeout,
        )
        return point_index, run_index, result

    def _emit(point_index: int) -> None:
        """Print + write the record for one PVT point as soon as every seed
        it needs has completed.

        Emitting per-point as results arrive (rather than after the whole
        grid finishes) means a crash, timeout, or Ctrl-C partway through a
        large -j grid still leaves every already-finished point recorded --
        sim/README.md's evidence is meant to be an artifact of runs that
        actually completed, not something withheld until the slowest point
        in the grid also finishes.
        """
        nonlocal overall_ok
        point = points[point_index]
        i = point_index + 1
        results = results_by_point[point_index]
        # Summed per-run cost, not elapsed: under -j the runs overlap, and a
        # wall_time that shrank because the machine had spare cores would be
        # useless for the coverage/cost trade-offs sim/README.md wants it for.
        wall = sum(r.seconds for r in results)
        point_ok = all(r.status == "ok" for r in results)

        # Re-check the model files before anything is published: a record
        # citing a model identity ngspice may not have read is not evidence.
        sections = _deck_sections(tb, point)
        pre = pre_manifests[sections]
        post = pdk_models.manifest_for_deck(pdk, sections)
        changed = post.identity != pre.identity
        if changed:
            # Diagnostics stay beside the raw output; no record is written.
            report.write_model_manifest(pre, workdirs[point_index])
            report.write_model_manifest(
                post, workdirs[point_index], pdk_models.CHANGED_MANIFEST_NAME
            )
            models_changed.append(
                (point.corner_id, workdirs[point_index], pre.describe_differences(post))
            )
            point_ok = False
        overall_ok = overall_ok and point_ok

        if not args.quiet:
            if changed:
                flag = "FAILED-PDK-CHANGED"
                detail = "PDK model files changed during the run; record withheld"
            elif point_ok:
                flag = "ok  "
                parts = []
                for name in tb.measure:
                    values = [r.measurements[name] for r in results if name in r.measurements]
                    if values:
                        parts.append(f"{name}={_fmt(sum(values) / len(values))}")
                detail = "  ".join(parts)
            else:
                # A killed corner must stand out from an ordinary
                # convergence/parse failure in the printed summary -- see
                # issue #83: a silently-hung corner is what took a whole
                # worker offline for hours, and "FAIL" alone reads the same
                # as any other failure.
                flag = "FAILED-TIMEOUT" if any(r.status == "timeout" for r in results) else "FAIL"
                first_failure = next((r for r in results if r.status != "ok"), None)
                detail = first_failure.message if first_failure else "no runs"
            print(f"[{i:>3}/{len(points)}] {flag} {point.corner_id:<22} {detail}")

        if changed:
            return
        if not args.no_write:
            record = report.build_record(
                tb=tb, pdk=pdk, point=point, results=results, ngspice=ngspice,
                repo_root=REPO_ROOT, stem=stems[point_index], completed_utc=completed_utc,
                wall_seconds=wall, raw_dir=workdirs[point_index], git=git,
                supersedes=args.supersedes, timeout_s=args.timeout,
                model_manifest=pre,
            )
            path = report.write_record(
                record, tb, RECORDS_DIR, _default_caveats(tb, point, jobs, pre)
            )
            written_paths.append(path)
            written_records.append(record)

    try:
        if jobs == 1:
            for task in tasks:
                point_index, run_index, result = _work(task)
                results_by_point[point_index][run_index] = result
                remaining_by_point[point_index] -= 1
                if remaining_by_point[point_index] == 0:
                    _emit(point_index)
        else:
            with ThreadPoolExecutor(max_workers=jobs) as pool:
                futures = [pool.submit(_work, task) for task in tasks]
                for future in as_completed(futures):
                    point_index, run_index, result = future.result()
                    results_by_point[point_index][run_index] = result
                    remaining_by_point[point_index] -= 1
                    if remaining_by_point[point_index] == 0:
                        _emit(point_index)
    except NgspiceMissing as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    print()
    if models_changed:
        _report_models_changed(models_changed)
    if args.no_write:
        print("evidence  : not recorded (--no-write)")
        print(f"scratch   : {scratch_root}  (retained; delete when no longer needed)")
    else:
        print(f"records   : {len(written_paths)} written under {RECORDS_DIR}/")
        for path in written_paths:
            print(f"  - {_display_path(path)}")
        corrupt = _verify_written_records(written_records)
        if corrupt:
            _report_corrupt_records(corrupt)
            print("status    : FAIL (raw output does not match the recorded checksums)")
            return EXIT_RECORD_CORRUPT
    if models_changed:
        print("status    : FAIL (PDK model files changed during the run)")
        return EXIT_PDK_MODELS_CHANGED
    print(f"status    : {'OK' if overall_ok else 'FAIL'}")

    return EXIT_OK if overall_ok else EXIT_CHECK_FAILED


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:  # pragma: no cover - only under a relocated RECORDS_DIR
        return str(path)


def _verify_written_records(records: list[dict]) -> list[tuple[str, list[str]]]:
    """Re-hash every record's raw output after the whole grid has finished.

    write_record() already checks each record as it is written; this second
    pass is what catches raw output clobbered *later* -- e.g. by a second
    run_corners.py invocation that was handed an overlapping stem, the
    failure mode #60 reports, which produced a full grid of plausible
    records with wrong provenance and exited OK.
    """
    corrupt: list[tuple[str, list[str]]] = []
    for record in records:
        problems = report.verify_record(record)
        if problems:
            corrupt.append((record["record"], problems))
    return corrupt


def _report_models_changed(changed: list[tuple[str, Path, list[str]]]) -> None:
    print(file=sys.stderr)
    print(
        f"error: PDK model files changed while {len(changed)} point(s) were "
        "simulating; their records were NOT written. The model content captured "
        "before the run no longer matches the installation, so the numbers cannot "
        "be tied to one model identity.",
        file=sys.stderr,
    )
    for corner_id, workdir, differences in changed:
        print(f"  {corner_id}: raw output retained in {_display_path(workdir)}", file=sys.stderr)
        print(
            f"    ({pdk_models.MANIFEST_NAME} = before the run, "
            f"{pdk_models.CHANGED_MANIFEST_NAME} = at the re-check)",
            file=sys.stderr,
        )
        for line in differences:
            print(f"    - {line}", file=sys.stderr)
    print(
        "\nThe retained raw directories are diagnostics, not evidence: do not "
        "commit them. Re-run once the PDK installation is stable.",
        file=sys.stderr,
    )


def _report_corrupt_records(corrupt: list[tuple[str, list[str]]]) -> None:
    print(file=sys.stderr)
    print(
        f"error: {len(corrupt)} record(s) no longer match their raw output. "
        "The raw files changed after they were hashed -- most likely another "
        "run_corners.py invocation wrote into the same sim/records/raw/ "
        "directories.",
        file=sys.stderr,
    )
    for stem, problems in corrupt:
        print(f"  {stem}:", file=sys.stderr)
        for problem in problems:
            print(f"    - {problem}", file=sys.stderr)
    print(
        "\nDo NOT commit these records: their numbers cannot be tied to the raw "
        "output they cite. Delete them together with their raw directories "
        "(they are not committed evidence yet, so the append-only rule does not "
        "apply) and re-run with no other invocation of this testbench in "
        "flight.",
        file=sys.stderr,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        return cmd_list()
    if args.check_env:
        return cmd_check_env()
    if args.print_env:
        return cmd_print_env()
    if not args.testbench:
        parser.print_help()
        return EXIT_ENVIRONMENT
    try:
        return run(args)
    except report.RawFilesMismatch as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_RECORD_CORRUPT
    except (FileNotFoundError, ValueError, KeyError, report.RecordExists) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ENVIRONMENT
