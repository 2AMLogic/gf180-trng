#!/usr/bin/env python3
"""Publish the mismatch Monte Carlo campaign as T1 item 6's analog citation.

    uv venv .venv-klt && uv pip install --python .venv-klt/bin/python "klayout-tools[yield]==0.9.0"
    KLT=.venv-klt/bin/klt python3 signoff/publish_item6.py
    python3 signoff/check.py --write

What it does:

* It reads the per-seed ``m_period_r1`` / ``m_dtrip_v`` values from the raw
  ngspice logs of the committed campaign (``sim/records/raw/``, read only,
  nothing is re-simulated) and writes them, one measurement per PVT point, to
  ``signoff/evidence/mc-yield/sample_set.json``.
* The limits come from ``signoff/evidence/mc-yield/limits.json``, which
  implements DR-0033 and nothing else. They are never edited here to make a
  report pass.
* It runs ``klt yield`` (klayout-tools[yield] 0.9.0, see ``YIELD_PIN``) over
  both with its default confidence and sample-size target, and writes the
  native response to ``signoff/evidence/mc-yield/klt_yield_response.json``.
  The response's own ``sample_size.verdict`` is recorded as it comes.

``publication.json`` pins the raw logs the sample set was read from by sha256;
``publication_problems()`` re-reads them so a stale sample set can be refused.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402

REPO_ROOT = check.REPO_ROOT
OUT = REPO_ROOT / "signoff" / "evidence" / "mc-yield"
YIELD_PIN = "0.9.0"

#: measurement name -> (raw record stem, log value name)
CAMPAIGN = {
    "period_r1@tt_27c_3.30v": ("2026-08-17-ro-array-core-mc-freq-01", "m_period_r1"),
    "period_r1@ss_125c_3.63v": ("2026-08-17-ro-array-core-mc-freq-02", "m_period_r1"),
    "dtrip_v@tt_27c_3.30v": ("2026-08-17-sampler-dff-mc-offset-03", "m_dtrip_v"),
    "dtrip_v@ss_125c_3.63v": ("2026-08-17-sampler-dff-mc-offset-02", "m_dtrip_v"),
}


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def read_samples(stem: str, name: str) -> tuple[list[float], dict[str, str]]:
    raw = REPO_ROOT / "sim" / "records" / "raw" / stem
    logs = sorted(raw.glob("*-run*.log"), key=lambda p: int(re.search(r"run(\d+)", p.name).group(1)))
    values, pins = [], {}
    for log in logs:
        m = re.search(rf"^{name} = (\S+)$", log.read_text(), re.M)
        if not m:
            raise SystemExit(f"{log}: no `{name} =` line")
        values.append(float(m.group(1)))
        pins[log.relative_to(REPO_ROOT).as_posix()] = sha256(log)
    return values, pins


def build() -> tuple[dict, dict]:
    limits = json.loads((OUT / "limits.json").read_text())["measurements"]
    measurements, pins = [], {}
    for mname, (stem, vname) in CAMPAIGN.items():
        samples, p = read_samples(stem, vname)
        pins.update(p)
        measurements.append({"name": mname, "samples": samples, "limits": limits[mname]})
    return {"measurements": measurements}, pins


def publication_problems() -> list[str]:
    """Problems with the committed sample set / publication."""
    pub = json.loads((OUT / "publication.json").read_text())
    problems = []
    fresh, pins = build()
    if pins != pub["raw_logs"]:
        problems.append("signoff/evidence/mc-yield/publication.json: raw log pins differ from the tree")
    if json.loads((OUT / "sample_set.json").read_text()) != fresh:
        problems.append("signoff/evidence/mc-yield/sample_set.json no longer matches the raw logs and limits.json")
    return problems


def main() -> int:
    doc, pins = build()
    (OUT / "sample_set.json").write_text(json.dumps(doc, indent=2) + "\n")
    argv = [*shlex.split(os.environ.get("KLT", "klt")), "yield", (OUT / "sample_set.json").relative_to(REPO_ROOT).as_posix(), "--format", "json"]
    print(shlex.join(argv), file=sys.stderr)
    done = subprocess.run(argv, cwd=REPO_ROOT, capture_output=True, text=True)
    if not done.stdout.strip():
        print(done.stderr, file=sys.stderr)
        print(f"klt yield failed (exit {done.returncode}); nothing published", file=sys.stderr)
        return 1
    resp = json.loads(done.stdout)
    (OUT / "klt_yield_response.json").write_text(json.dumps(resp, indent=2) + "\n")
    (OUT / "publication.json").write_text(
        json.dumps({"klayout_tools_yield_pin": YIELD_PIN, "klt_exit": done.returncode, "raw_logs": pins}, indent=2) + "\n"
    )
    print(f"klt yield exit {done.returncode}; response written", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
