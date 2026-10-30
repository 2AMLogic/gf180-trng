"""One copy of the "mint append-only records from klt reports" scaffold.

``sim/tools/liveness_sampler_power.py`` and ``sim/tools/power_switch.py`` each
carried a byte-identical ``cmd_record``. The record text (``render_measured`` /
``render_unmeasured``, the result fields, the caveats) stays per-tool and is
injected; everything that decides which files land under ``sim/records/`` and
what bytes the raw artifacts carry lives here, once.
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Callable

from . import report as _report


def sanitize(text: str, repo_root: Path) -> str:
    """Strip this host's absolute paths from a raw artifact before it is hashed."""
    return text.replace(str(repo_root), "<repo>").replace(str(Path.home()), "~")


def mint_records(paths: list[str], note: str, records_dir: Path | None, *, repo_root: Path,
                 slug: str, slug_attempt: str, analyse_report: Callable[[dict], list[dict]],
                 render_measured: Callable[..., str], render_unmeasured: Callable[..., str]) -> int:
    """Mint append-only records from klt reports: one measured record per usable
    corner, and one UNMEASURED record for the units that did not produce data."""
    records_dir = records_dir or repo_root / "sim" / "records"
    now = _dt.datetime.now(_dt.timezone.utc)
    date = now.strftime("%Y-%m-%d")
    git = _report.git_provenance(repo_root)
    for path in paths:
        rep = json.loads(Path(path).read_text())
        rows = analyse_report(rep)
        good = [(r, c) for r, c in zip(rows, rep.get("corners", [])) if r["verdict"] == "OK"]
        bad = [c for r, c in zip(rows, rep.get("corners", [])) if r["verdict"] != "OK"]
        stems = _report.reserve_record_stems(records_dir, date, slug, len(good)) if good else []
        for (row, corner), stem in zip(good, stems):
            raw = records_dir / _report.RAW_DIRNAME / stem
            files: list[tuple[str, str]] = []
            for name, key in (("corner.cir", "deck"), ("ngspice.log", "log")):
                src = (corner.get("artifacts") or {}).get(key)
                if src and Path(src).is_file():
                    (raw / name).write_text(sanitize(Path(src).read_text(errors="replace"), repo_root))
                    files.append((name, _report.sha256_file(raw / name)))
            sl = {"environment": rep.get("environment"), "provenance": rep.get("provenance"), "corner": corner}
            (raw / "report-unit.json").write_text(sanitize(json.dumps(sl, indent=1), repo_root) + "\n")
            files.append(("report-unit.json", _report.sha256_file(raw / "report-unit.json")))
            (records_dir / f"{stem}.md").write_text(render_measured(stem, row, corner, rep, files, now, git))
            print(f"wrote {stem}.md  ({row['corner']})")
        if bad:
            stem = _report.reserve_record_stems(records_dir, date, slug_attempt, 1)[0]
            raw = records_dir / _report.RAW_DIRNAME / stem
            slim = dict(rep)
            slim["corners"] = [{k: v for k, v in c.items() if k != "measurements"} for c in bad]
            (raw / "report-errored.json").write_text(sanitize(json.dumps(slim, indent=1), repo_root) + "\n")
            files = [("report-errored.json", _report.sha256_file(raw / "report-errored.json"))]
            (records_dir / f"{stem}.md").write_text(render_unmeasured(stem, bad, rep, files, now, git, note))
            print(f"wrote {stem}.md  (UNMEASURED, {len(bad)} units)")
    return 0
