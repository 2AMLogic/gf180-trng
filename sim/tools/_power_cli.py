"""Adapter helpers shared by the power tools (``power_switch``, ``power_switch_decay``,
``power_retention``, ``liveness_sampler_power``; ``fs_sf_capture``, ``supply_ripple`` and
``starved_hot_corner`` use only ``render``/``vals``): the "emit request / run / record /
analyze" layer that was identical in each, plus the ``plan | emit | run | record [| summarize] |
analyze`` CLI front end (``build_parser``/``main``) that was copy-pasted with it. Per-script pieces
(``build_request``, ``derive``, ``checks``, ``render_*``) stay in the
tools; they differ for real. Everything here either is pure or takes the per-script pieces as
arguments, so each tool's emitted requests and minted records are unchanged.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness import klt_request as _kreq  # noqa: E402
from harness import record_mint as _mint  # noqa: E402
import _record_parsing as _rp  # noqa: E402


def fmt(x: float) -> str:
    return f"{x:.6e}"


def label(rec: dict) -> str:
    proc, temp, vdd = rec["corner"]
    return f"{proc}/{temp:g}C/{vdd:.2f}V"


def vals(corner: dict) -> dict[str, float]:
    return {x["name"]: x["value"] for x in corner.get("measurements", []) if x.get("value") is not None}


def render(req: dict) -> str:
    return json.dumps(req, indent=1) + "\n"


def analyse_report(report: dict, derive: Callable, checks: Callable, derivation_error: type[Exception]) -> list[dict]:
    rows = []
    for c in report.get("corners", []):
        v = vals(c)
        vdd = float(c.get("supply_v", {}).get("vsup", 3.3))
        key = f"{c.get('process')}/{c.get('temperature_c')}/{vdd:.2f}"
        row = {"corner": key, "process": c.get("process"), "temperature_c": c.get("temperature_c"),
               "vdd": vdd, "status": c.get("status")}
        try:
            row.update(derive(v, vdd))
            row["problems"] = checks(row)
            row["verdict"] = "OK" if not row["problems"] else "SUSPECT"
        except derivation_error as exc:
            row["problems"] = [str(exc)]
            row["verdict"] = "UNMEASURED"
        rows.append(row)
    return rows


def load_records(records_dir: Path, slug: str) -> list[dict]:
    """The current measurement records for ``slug``: corner plus Result bullets."""
    out = []
    for path in _rp.current_records(records_dir, f"*-{slug}-[0-9]*.md"):
        text = path.read_text()
        proc, temp, vdd = _rp.parse_corner(text, label=path.stem)
        out.append({"stem": path.stem, "corner": (proc, temp, vdd),
                    "values": _rp.parse_values(_rp.result_section(text, label=path.stem), label=path.stem)})
    return out


def cmd_emit(check: bool, *, path: Path, text: str, repo_root: Path, n_units: int) -> int:
    return _kreq.emit_requests(
        [(path, text)], check, repo_root=repo_root,
        ok=lambda: print(f"ok: {path.relative_to(repo_root)} matches the declared grid ({n_units} units)"))


def cmd_run(outdir: str, backend: str, klt_cmd: str, only: str | None, *, request: Path, tb_dir: Path,
            build_request: Callable) -> int:
    return _kreq.run_probe_or_grid(
        outdir, backend, klt_cmd, only, request=request, tb_dir=tb_dir,
        render_probe=lambda point: render(build_request(point)), probe_hint="--only PROCESS/TEMP/VDD")


def cmd_record(paths: list[str], note: str, records_dir: Path | None, *, repo_root: Path, slug: str,
               analyse_report: Callable, render_measured: Callable, render_unmeasured: Callable) -> int:
    return _mint.mint_records(
        paths, note, records_dir, repo_root=repo_root, slug=slug, slug_attempt=f"{slug}-attempt",
        analyse_report=analyse_report, render_measured=render_measured, render_unmeasured=render_unmeasured)


def cmd_analyze(paths: list[str], as_json: bool, *, analyse_report: Callable, table: Callable) -> int:
    rows: list[dict] = []
    for p in paths:
        rows += analyse_report(json.loads(Path(p).read_text()))
    if as_json:
        print(json.dumps(rows, indent=1))
    else:
        print(table(rows))
        bad = [r for r in rows if r["verdict"] != "OK"]
        print(f"\n{len(rows) - len(bad)}/{len(rows)} units usable"
              + ("" if not bad else "; not usable: " + ", ".join(f"{r['corner']} ({r['verdict']})" for r in bad)))
    return 0


def build_parser(doc: str | None, *, only_example: str, has_summarize: bool = True) -> argparse.ArgumentParser:
    """The power tools' CLI: ``plan | emit | run | record [| summarize] | analyze``.

    The subparser set was identical in every tool bar the ``--only`` example and whether the
    tool has a ``summarize`` subcommand, so those are the only arguments: help text that had
    drifted between the copies (a missing ``--note`` / ``summarize`` help, "table" vs
    "tables") is unified here rather than carried per tool.
    """
    ap = argparse.ArgumentParser(description=(doc or "").split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    e = sub.add_parser("emit")
    e.add_argument("--check", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("--outdir", required=True)
    r.add_argument("--only", help=f"ONE grid point PROCESS/TEMP_C/VDD (e.g. {only_example}): a local debug probe")
    r.add_argument("--backend", default="batch", choices=("batch", "local"))
    r.add_argument("--klt", default="klt", dest="klt_cmd",
                   help="klt command; e.g. 'uvx --from klayout-tools==X.Y.Z klt'")
    rec = sub.add_parser("record", help="mint append-only records from klt reports")
    rec.add_argument("reports", nargs="+")
    rec.add_argument("--note", default="", help="prose appended to an UNMEASURED record")
    if has_summarize:
        sub.add_parser("summarize", help="tables over the committed records, for the characterization report")
    a = sub.add_parser("analyze")
    a.add_argument("reports", nargs="+")
    a.add_argument("--json", action="store_true")
    return ap


def main(argv: list[str] | None, *, doc: str | None, only_example: str, plan_text: Callable[[], str],
         cmd_emit: Callable[..., int], cmd_run: Callable[..., int], cmd_record: Callable[..., int],
         cmd_analyze: Callable[..., int], cmd_summarize: Callable[..., int] | None = None) -> int:
    """Parse ``argv`` and dispatch to the tool's own command functions.

    ``cmd_summarize=None`` is a tool without a ``summarize`` subcommand (the parser then does
    not offer one), not a tool whose ``summarize`` does nothing.
    """
    ap = build_parser(doc, only_example=only_example, has_summarize=cmd_summarize is not None)
    args = ap.parse_args(argv)
    if args.cmd == "plan":
        print(plan_text())
        return 0
    if args.cmd == "emit":
        return cmd_emit(args.check)
    if args.cmd == "run":
        return cmd_run(args.outdir, args.backend, args.klt_cmd, args.only)
    if args.cmd == "record":
        return cmd_record(args.reports, args.note)
    if args.cmd == "summarize" and cmd_summarize is not None:
        return cmd_summarize()
    return cmd_analyze(args.reports, args.json)
