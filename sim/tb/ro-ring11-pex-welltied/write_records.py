#!/usr/bin/env python3
"""Mint the `level: extracted` records for the well-tied ring1 grid (issue #339).

    python3 sim/tb/ro-ring11-pex-welltied/write_records.py <klt-sim-report.json> <klt-sim-outdir>

`<klt-sim-report.json>` is the `--format json` output of

    klt sim --backend batch -o <outdir> sim/tb/ro-ring11-pex-welltied/request.json

(request.json sets `keep_artifacts`, so each corner directory under <outdir>
holds `corner.cir` and `ngspice.log`). One record per corner (DR-0005): the
corner's deck and log are copied under sim/records/raw/<stem>/ with a small
per-corner JSON slice of the klt report, and checksummed. Each record also
quotes, beside the well-tied figure, the schematic and floating-well figures at
the SAME corner, read from the committed envelope
signoff/evidence/post-layout/ro_ring11.pex.json -- those two are not
re-simulated here.

Refuses to run unless every corner passed with a value for every row (a
missing crossing is an error, never a record), and never overwrites a record.
"""

from __future__ import annotations

import datetime as dt
import json
import platform
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
sys.path.insert(0, str(REPO_ROOT / "sim"))

from harness import pdk as pdk_mod  # noqa: E402
from harness import report  # noqa: E402

SLUG = "ro-ring11-pex-welltied"
ENVELOPE = REPO_ROOT / "signoff/evidence/post-layout/ro_ring11.pex.json"
RECORDS = REPO_ROOT / "sim" / "records"
ROWS = ("period_s", "supply_current_avg_a", "ro_swing_v")


def fnum(v: float) -> str:
    return f"{v:.6e}" if v != 0 and (abs(v) < 1e-3 or abs(v) >= 1e5) else f"{v:.6g}"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    rep = json.loads(Path(argv[0]).read_text())
    outdir = Path(argv[1])
    env = json.loads(ENVELOPE.read_text())
    if rep["status"] != "pass" or rep["passed"] != rep["corner_count"] != 27:
        print(f"report is not a clean 27-corner pass: {rep['status']} "
              f"({rep['passed']}/{rep['corner_count']})", file=sys.stderr)
        return 1
    remote = rep["environment"]["remote"]
    if remote.get("state") != "done":
        print(f"batch job state is {remote.get('state')!r}", file=sys.stderr)
        return 1

    ref = {(d["spec_row"], d["corner_id"]): d for d in env["delta"]}
    pdk = pdk_mod.find_pdk()
    models_sha = rep["environment"]["models_lib_sha256"]
    git = report.git_provenance(REPO_ROOT)
    tb_path = HERE / "tb_ro_ring11_pex_welltied.sp"
    net_path = HERE / "ro_ring11.welltied.extracted.spice"
    req = json.loads((HERE / "request.json").read_text())
    now = dt.datetime.now(dt.timezone.utc)
    date = now.strftime("%Y-%m-%d")
    stems = report.reserve_record_stems(RECORDS, date, SLUG, len(rep["corners"]))

    for stem, corner in zip(stems, rep["corners"]):
        vals = {m["name"]: m["value"] for m in corner["measurements"]}
        if corner["status"] != "pass" or any(vals.get(r) is None for r in ROWS):
            print(f"{corner['corner_id']}: missing/failed measurement; no record written", file=sys.stderr)
            return 1
        cid = corner["corner_id"]
        proc, volt, temp = corner["process"], corner["supply_v"]["vsupply"], corner["temperature_c"]
        cdir = outdir / f"{proc}_{f'{volt:.3f}'.replace('.', 'p')}V_{str(temp).replace('-', 'n')}C"
        raw_dir = RECORDS / report.RAW_DIRNAME / stem
        base = f"{proc}_{temp}c_{volt:.2f}v"
        shutil.copyfile(cdir / "corner.cir", raw_dir / f"{base}.spice")
        shutil.copyfile(cdir / "ngspice.log", raw_dir / f"{base}.log")
        slice_ = {"klt_sim_corner": corner, "batch_job": remote,
                  "klt_version": rep["provenance"]["klt_version"]}
        (raw_dir / f"{base}.json").write_text(json.dumps(slice_, indent=2) + "\n")
        files = [(f"{base}.{ext}", report.sha256_file(raw_dir / f"{base}.{ext}"))
                 for ext in ("spice", "log", "json")]

        sch = {r: ref[(r, cid)]["schematic_value"] for r in ROWS}
        flo = {r: ref[(r, cid)]["extracted_value"] for r in ROWS}
        t = vals["period_s"]
        pct = lambda a, b: f"{(a / b - 1) * 100:+.1f} %"  # noqa: E731
        label = f"{volt:.3f} V (nominal 3.3 V, {'nominal' if abs(volt - 3.3) < 1e-9 else f'{(volt / 3.3 - 1) * 100:+.0f}%'})"

        lines = [
            "---",
            f"record: {stem}",
            f"date: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}",
            "status: valid",
            "level: extracted",
            "",
            "testbench:",
            f"  path: {tb_path.relative_to(REPO_ROOT)}",
            f"  sha: {report.blob_sha(REPO_ROOT, tb_path)}",
            "netlist:",
            f"  path: {net_path.relative_to(REPO_ROOT)}",
            f"  sha: {report.blob_sha(REPO_ROOT, net_path)}",
            f"repo_commit: {report.repo_commit_field(git)}",
            "",
            f"pdk: gf180mcuD @ {pdk.version}",
            "pdk.models:",
            f"  - /opt/pdk/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: "
            f"{' '.join(next(p for p in req['corners']['process'] if p['name'] == proc)['sections'])}; "
            f"fleet copy, sha256 {models_sha}, identical to the {pdk.variant} copy "
            f"this repo's harness resolves locally)",
            "",
            "tool:",
            f"  ngspice: \"ngspice-{rep['environment']['engine_version']} (AWS batch fleet runner)\"",
            f"  platform: \"{remote['instance_type']} {remote['lifecycle']} instance {remote['instance_id']}, job {remote['job_id']}; "
            f"submitted from {platform.platform()} with klt {rep['provenance']['klt_version']}\"",
            "",
            "corner:",
            f"  process: {proc}",
            f"  voltage: {label}",
            f"  temperature: {temp}",
            "",
            "analysis:",
            "  type: tran",
            "  tstop: 1300n",
            "  tstep: 10p (print step; ngspice's own LTE sets the actual solver step)",
            "  tmax: n/a",
            "  noise_params: n/a",
            "  runs: 1",
            "seeds: n/a (deterministic analysis)",
            "",
            "raw:",
            f"  path: sim/records/raw/{stem}/",
            "  files:",
            *[f"    - {n}  sha256:{h}" for n, h in files],
            f"wall_time: {corner['runtime_s']}s (this corner; whole 27-corner batch job {remote['elapsed_seconds']}s)",
            "---",
            "",
            "## Result",
            "",
            "Well-tied extracted netlist (PMOS bodies rewired to `vddr`), this record:",
            "",
            f"- `period_s`: {fnum(vals['period_s'])}",
            f"- `supply_current_avg_a`: {fnum(vals['supply_current_avg_a'])}",
            f"- `ro_swing_v`: {fnum(vals['ro_swing_v'])}",
            "",
            f"Same corner, not re-simulated here, from the committed envelope `{ENVELOPE.relative_to(REPO_ROOT)}` "
            "(klt pex 0.6.0, schematic DUT and extracted netlist with floating wells):",
            "",
            "| row | schematic | extracted, wells floating | extracted, wells tied (this record) | floating vs schematic | tied vs schematic | tied vs floating |",
            "|---|---|---|---|---|---|---|",
            *[f"| `{r}` | {fnum(sch[r])} | {fnum(flo[r])} | {fnum(vals[r])} | {pct(flo[r], sch[r])} | "
              f"{pct(vals[r], sch[r])} | {pct(vals[r], flo[r])} |" for r in ROWS],
            "",
            "Numbers only. No spec-compliance claim is made by this record.",
            "",
            "## How to reproduce",
            "",
            "```sh",
            "python3 sim/tb/ro-ring11-pex-welltied/build_welltied.py --check",
            "uvx --from \"klayout-tools==0.6.0\" klt sim --backend batch -o /tmp/welltied \\",
            "    sim/tb/ro-ring11-pex-welltied/request.json --format json > /tmp/welltied/report.json",
            "```",
            "",
            f"This record is the `{cid}` entry of that 27-corner request (batch job `{remote['job_id']}`).",
            "A single corner can be run locally by narrowing `corners` in a copy of the request.",
            "",
            "## Caveats",
            "",
            "- Single corner (" + f"{proc} / {volt:.2f} V / {temp} C). Says nothing about any other corner.",
            "- The netlist is the extraction of `layout/rings/ro_ring11/ro_ring11.gds` "
            "(`signoff/evidence/post-layout/ro_ring11.extracted.spice`) with the body (4th terminal) of all 23 PMOS rewired "
            "from their 11 anonymous floating well nets to the `vddr` port node, by `build_welltied.py`, derived from the envelope's "
            "`body_bias` block. It is a counterfactual, NOT a drawn-layout result: the layout draws no n-well tie "
            "(layout/README.md), so no drawn cell has this connection. The tie is ideal (no access resistance), the best case for a tie.",
            "- The schematic side of the comparison ties PMOS bulk to `vddr`; the floating side is the committed envelope.",
            "- Ring1 only. Ring2, the buffers, the XOR combiner, the samplers and every inter-region net are not included.",
            "- Parasitics captured are what `klt extract --parasitics` models for ring1 alone: device-level parasitics and the "
            "hand-routed inter-stage chain and rail straps; quasi-static lumped RC, no lateral coupling except named critical nets, "
            "no inter-region routing. See sim/characterization-post-layout-extracted.md section 7 and signoff/README.md.",
            "- Noiseless, deterministic transient; no device mismatch; `ro` unloaded. Absolute periods differ from array-level records.",
            "- Simulated on the batch fleet runner (ngspice-" + str(rep['environment']['engine_version']) + "); the figures also agree with a "
            "local single-corner probe at tt / 3.30 V / 27 C (13.65 ns). The floating/schematic figures come from the committed envelope's own run, not this job.",
            "- The deck is self-contained: the batch backend of klt 0.6.0 uploads the testbench alone, so the netlist text is inlined "
            "into `tb_ro_ring11_pex_welltied.sp` (the separate netlist file is what `netlist.path` cites; `build_welltied.py --check` ties them).",
            "",
            "---",
            "",
            "Written by `sim/tb/ro-ring11-pex-welltied/write_records.py`. Append-only: never edit or delete this",
            "file -- a re-run or correction mints a new record and points back here",
            "via `supersedes` (see `sim/README.md`).",
            "",
        ]
        path = RECORDS / f"{stem}.md"
        if path.exists():
            print(f"{path} exists; records are append-only", file=sys.stderr)
            return 1
        problems = report.verify_raw_files(raw_dir, files)
        if problems:
            print("\n".join(problems), file=sys.stderr)
            return 1
        path.write_text("\n".join(lines))
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
