#!/usr/bin/env python3
"""PDK-free probe: does any startup or seed control make ngspice ``trnoise``
waveforms replay across separate processes? (issue #574)

Every run is one sequential ``ngspice -b`` process in a fresh ``mktemp``
directory; no machine-wide or user init file is read for writing or modified.
The harness start-up policy is applied through ``sim/harness/startup.py``
itself (``batch_flags``, ``environment``, ``write_snapshot``) using the
committed copy ``startup/harness-spinit`` of the pinned script.

Usage (from the repository root; ``PYTHONPATH=.`` makes ``sim.harness``
importable without the script editing ``sys.path``):

    PYTHONPATH=. python3 sim/tool-experiments/2026-10-11-ngspice-trnoise-seed-replay/probe.py OUTDIR

Writes ``OUTDIR/<run>.log`` (combined ngspice output), ``OUTDIR/runs.json``
(argv with temporary paths replaced by ``<tmp>``, exit status, parsed
samples) and ``OUTDIR/compare.txt`` (the numerical comparison).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from sim.harness import startup

HERE = Path(__file__).resolve().parent

#: Times (ns) at which ``trnoise(1 1n 0 0)`` holds a fresh sample.
SAMPLE_NS = tuple(range(1, 17))

#: ``(group, run, deck, mode, startup file or None)``. Modes:
#: ``harness``  -- startup.batch_flags() + startup.environment() at a snapshot
#:                 of ``startup/harness-spinit``; hostile HOME and work-dir
#:                 ``.spiceinit`` present (must not be read);
#: ``spinit``   -- as ``harness`` but the snapshot is the given startup file;
#: ``userinit`` -- no ``-n``; HOME holds the given file as ``.spiceinit``,
#:                 clean work directory, harness ``SPICE_SCRIPTS`` snapshot;
#: ``pidns``    -- ``harness`` run wrapped in ``unshare --user --pid --fork``
#:                 (a diagnostic of the process-id hypothesis, not a control).
RUNS = (
    ("H", "H_seed11_run1", "seed11.cir", "harness", None),
    ("H", "H_seed11_run2", "seed11.cir", "harness", None),
    ("H", "H_seed12", "seed12.cir", "harness", None),
    ("S", "S_spinit_setseed11_run1", "seed11.cir", "spinit", "spinit-setseed11"),
    ("S", "S_spinit_setseed11_run2", "seed11.cir", "spinit", "spinit-setseed11"),
    ("S", "S_spinit_setseed12", "seed12.cir", "spinit", "spinit-setseed12"),
    ("R", "R_spinit_rndseed11_run1", "seed11.cir", "spinit", "spinit-rndseed11"),
    ("R", "R_spinit_rndseed11_run2", "seed11.cir", "spinit", "spinit-rndseed11"),
    ("R", "R_spinit_rndseed12", "seed12.cir", "spinit", "spinit-rndseed12"),
    ("U", "U_userinit_setseed11_run1", "seed11.cir", "userinit", "spiceinit-setseed11"),
    ("U", "U_userinit_setseed11_run2", "seed11.cir", "userinit", "spiceinit-setseed11"),
    ("U", "U_userinit_setseed12", "seed12.cir", "userinit", "spiceinit-setseed12"),
    ("C", "C_ctl_setseed11_run1", "ctl_setseed11.cir", "harness", None),
    ("C", "C_ctl_setseed11_run2", "ctl_setseed11.cir", "harness", None),
    ("C", "C_ctl_setseed12", "ctl_setseed12.cir", "harness", None),
    ("P", "P_pidns_seed11_run1", "seed11.cir", "pidns", None),
    ("P", "P_pidns_seed11_run2", "seed11.cir", "pidns", None),
    ("P", "P_pidns_seed12", "seed12.cir", "pidns", None),
)

GROUPS = {
    "H": "harness policy (-n, SPICE_SCRIPTS at pinned spinit), .option seed only",
    "S": "harness policy, isolated spinit adds 'setseed N'",
    "R": "harness policy, isolated spinit adds 'set rndseed=N'",
    "U": "manual 11.3: '.spiceinit' with 'setseed N' read as user init (no -n)",
    "C": "harness policy, control block 'setseed N' before tran",
    "P": "harness policy inside a new PID namespace (diagnostic, not a control)",
}


def parse(text: str) -> dict:
    """``v(n1)`` at SAMPLE_NS, ``p[0]`` and ``g[0..2]`` as printed strings."""
    rows: dict[int, str] = {}
    p0 = None
    g: list[str] = []
    column = None  # the vector named by the most recent "Index time <vec>" header
    for line in text.splitlines():
        parts = line.split()
        if parts[:2] == ["Index", "time"] and len(parts) == 3:
            column = parts[2]
        elif line.startswith("p[0] ="):
            p0 = parts[-1]
        elif len(parts) == 3 and parts[0].isdigit():
            if column == "g":
                g.append(parts[2])
            elif column == "v(n1)":
                t_ns = float(parts[1]) * 1e9
                k = round(t_ns)
                if k in SAMPLE_NS and abs(t_ns - k) < 1e-6:
                    rows.setdefault(k, parts[2])
    return {"v_n1": [rows.get(k) for k in SAMPLE_NS], "p0": p0, "g": g}


def run_one(tmp: Path, name: str, deck: str, mode: str, startup_file: str | None) -> dict:
    root = tmp / name
    work, home, scripts = root / "work", root / "home", root / "scripts"
    for d in (work, home):
        d.mkdir(parents=True)
    shutil.copyfile(HERE / "decks" / deck, work / deck)
    hostile = (HERE / "startup" / "spiceinit-hostile").read_bytes()
    spinit_name = startup_file if mode == "spinit" else "harness-spinit"
    snapshot = startup.Snapshot((HERE / "startup" / spinit_name).read_bytes())
    startup.write_snapshot(snapshot, scripts)
    base = {k: v for k, v in os.environ.items()
            if not k.startswith("SPICE_") and k != "HOME"}
    base["HOME"] = str(home)
    env = startup.environment(base, scripts_dir=scripts)
    if mode == "userinit":
        (home / ".spiceinit").write_bytes((HERE / "startup" / startup_file).read_bytes())
        argv = ["ngspice", "-b", deck]
    else:
        (home / ".spiceinit").write_bytes(hostile)
        (work / ".spiceinit").write_bytes(hostile)
        argv = ["ngspice", *startup.batch_flags(), deck]
    if mode == "pidns":
        argv = ["unshare", "--user", "--pid", "--fork", *argv]
    proc = subprocess.run(argv, cwd=work, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, timeout=120, check=False)
    text = proc.stdout.decode("utf-8", errors="replace")
    return {
        "argv": argv,
        "cwd": "<tmp>/work",
        "env": {"HOME": "<tmp>/home", "SPICE_SCRIPTS": "<tmp>/scripts"},
        "spice_scripts_spinit": spinit_name,
        "spice_scripts_spinit_sha256": snapshot.sha256,
        "home_spiceinit": startup_file if mode == "userinit" else "spiceinit-hostile",
        "work_spiceinit": None if mode == "userinit" else "spiceinit-hostile",
        "exit": proc.returncode,
        "sentinels": sorted({w for w in text.split() if w.startswith("STARTUP_")}),
        **parse(text),
        "_log": proc.stdout,
    }


def compare(results: dict) -> list[str]:
    lines = ["# Numerical comparison (printed values, numdgt=8)", ""]
    for group, label in GROUPS.items():
        names = [r[1] for r in RUNS if r[0] == group]
        a, b, c = (results[n] for n in names)
        lines.append(f"## {group}: {label}")
        for n in names:
            r = results[n]
            lines.append(f"- {n}: exit={r['exit']} sentinels={r['sentinels'] or 'none'} "
                         f"p0={r['p0']} g={r['g']} v(n1)@1..4ns={r['v_n1'][:4]}")
        same = sum(x == y for x, y in zip(a["v_n1"], b["v_n1"]))
        diff = sum(x == y for x, y in zip(a["v_n1"], c["v_n1"]))
        lines.append(f"- same seed, two processes: v(n1) equal at {same} of "
                     f"{len(SAMPLE_NS)} samples; p0 equal={a['p0'] == b['p0']}; "
                     f"g equal={a['g'] == b['g']}")
        lines.append(f"- seed 11 vs seed 12: v(n1) equal at {diff} of "
                     f"{len(SAMPLE_NS)} samples; p0 equal={a['p0'] == c['p0']}; "
                     f"g equal={a['g'] == c['g']}")
        lines.append("")
    return lines


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    out = Path(argv[1])
    out.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict] = {}
    with tempfile.TemporaryDirectory(prefix="trnoise-replay-") as t:
        for _group, name, deck, mode, startup_file in RUNS:
            results[name] = run_one(Path(t), name, deck, mode, startup_file)
            (out / f"{name}.log").write_bytes(results[name].pop("_log"))
            print(f"{name} exit={results[name]['exit']}")
    (out / "runs.json").write_text(json.dumps(results, indent=2) + "\n")
    (out / "compare.txt").write_text("\n".join(compare(results)))
    return 0 if all(r["exit"] == 0 for r in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
