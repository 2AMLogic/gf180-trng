"""Adapter helpers shared by the power-switch tools (``power_switch``, ``power_switch_decay``,
``power_retention``): the "emit request / run / record / analyze" layer that was identical in
each. Per-script pieces (``build_request``, ``derive``, ``checks``, ``render_*``) stay in the
tools; they differ for real. Everything here either is pure or takes the per-script pieces as
arguments, so each tool's emitted requests and minted records are unchanged.
"""

from __future__ import annotations

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
