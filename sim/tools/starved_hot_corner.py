#!/usr/bin/env python3
"""Batch-fleet run and record ingestion for the starved-cell jitter bench (issue #628).

    python3 sim/tools/starved_hot_corner.py plan
    python3 sim/tools/starved_hot_corner.py emit [--check]
    python3 sim/tools/starved_hot_corner.py run --outdir DIR [--backend batch]
    python3 sim/tools/starved_hot_corner.py ingest --report DIR/ring5-hot.report.json \
        [--stderr FILE] [--request FILE]

Why this exists. ``sim/tb/ro-ring5-starved-jitter-long/`` measures with an ngspice
``.control`` loop that only the local harness (``sim/run_corners.py``) can run, and
eight seeded runs at ~111 min of ngspice each do not belong on a shared worker. A
``klt sim`` request has no ``.control`` escape hatch, so this tool asks the fleet for
the *primitives* of the same bench -- the 769 mid-supply rising-edge times of the
ring output, two charge readings and the mean supply, as ``.meas`` cards -- and then
computes the family's estimators from them *here*, with the definitions in that
bench's ``tb.json`` (``sigma_L``, per-block periods, energy per cycle, ...). The record
it writes is therefore directly comparable to the family's existing records and is read
by ``sim/tools/starved_cell_jitter_energy.py`` unchanged.

The declared grid is one corner (ss / +125 C / 3.63 V, the entropy-binding corner of
DR-0015) and eight units. The eight units share every setting; the request sweeps the
marker source ``vseed`` 1..8 only so they are eight distinct units. It does not seed
the noise: ``trnoise`` draws come from each ngspice process (DR-0031), and ``ingest``
refuses a report whose units carry bit-identical edge times (a duplicated realization).

The shared-host rule is enforced by ``sim/harness/klt_request.py``: the grid is
submitted to the batch fleet and never swept locally. Nothing here runs under CI beyond
the offline unit tests and ``emit --check``.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import platform
import statistics
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import klt_request as _kreq  # noqa: E402
from harness import report as _rep  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
TB_DIR = REPO_ROOT / "sim" / "tb" / "ro-ring5-starved-jitter-long-batch"
DECK = "tb_ro_ring5_starved_jitter_long_batch.sp"
DUT_PATH = "design/ro_array_sanity.spice"
SLUG = "ro-ring5-starved-jitter-long"
REQUEST_NAME = "ring5-hot"

PROCESS = "ss"
SECTIONS = ["ss", "bjt_ss", "diode_ss", "res_ss", "moscap_ss", "mimcap_ss"]
TEMP_C = 125
VDD_V = 3.63
SEEDS = tuple(range(1, 9))
#: Fleet shards. The fleet caps concurrent instances (a first attempt with one shard
#: per unit was refused at the cap), so the 8 units share 2 shard jobs.
HOSTS = 2
#: The family's bench stops at 2.4 us, sized for periods up to ~3 ns. The ss/+125 C ring
#: runs at ~3.78 ns, so the 770th rising crossing the window needs lands near 2.92 us and
#: a 2.4 us run would end ~640 edges in with the window's last cards unmeasurable.
TSTOP = "3.1u"
TSTEP = "1p"

#: Window geometry, identical to sim/tb/ro-ring5-starved-jitter-long/tb.json.
SKIP = 256            # periods discarded before the window opens
WINDOW = 512          # periods in the window
N_EDGES = SKIP + WINDOW + 1   # tc[0..768]; tc[k] is the (k+2)-th rising crossing
LAGS = (1, 2, 4, 8, 16, 32, 64, 128)
STARTUP_N = 16
STARTUP_LAGS = (1, 2, 4, 8)
BLOCK = 48
N_BLOCKS = 16
CQ_F = 1e-9
N_STAGES = 5

DESCRIPTION_NOISE = (
    "per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD "
    "1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources, one in series with every stage input"
)

# --------------------------------------------------------------------------
# Request construction
# --------------------------------------------------------------------------


def edge_name(k: int) -> str:
    return f"tc_{k}"


def measurements() -> list[dict]:
    """769 edge-time cards, two charge readings and the mean supply, all ``.meas`` cards.

    ``tc_k`` is the (k+2)-th rising crossing of v(x1) through 0 V, exactly the family's
    ``meas tran tk when v(x1)=0 rise=$&ri`` with ri = k + 2. (klt sim also has a
    ``crossings`` series form that needs no per-edge card, but the fleet's runner was
    older than the client and refused it, so the cards are the form that runs there.)
    """
    m = [{"name": edge_name(k), "unit": "s",
          "spice": f".meas tran {edge_name(k)} when v(x1)=0 rise={k + 2}"}
         for k in range(N_EDGES)]
    m.append({"name": "qw0", "unit": "V",
              "spice": f".meas tran qw0 find v(q1) when v(x1)=0 rise={SKIP + 2}"})
    m.append({"name": "qw1", "unit": "V",
              "spice": f".meas tran qw1 find v(q1) when v(x1)=0 rise={SKIP + WINDOW + 2}"})
    m.append({"name": "vsup_avg", "unit": "V", "spice": ".meas tran vsup_avg avg v(vsup)"})
    return m


def build_request() -> dict:
    n = len(SEEDS)
    return {
        "_comment": (
            f"issue #628: starved-cell jitter bench at {PROCESS}/{TEMP_C} C/{VDD_V} V, "
            f"{n} units. Generated by sim/tools/starved_hot_corner.py; do not edit by hand "
            "(`emit --check` fails if this drifts)."
        ),
        "netlist": DECK,
        "engine": "ngspice",
        "models": {"pdk": "gf180mcuD", "lib": "libs.tech/ngspice/sm141064.ngspice"},
        "corners": {
            "process": [{"name": PROCESS, "sections": SECTIONS}],
            "supply_v": {"vsup": [VDD_V] * n, "vseed": [float(s) for s in SEEDS]},
            "temperature_c": [TEMP_C],
        },
        "analysis": {"kind": "tran", "args": f"{TSTEP} {TSTOP}"},
        "measurements": measurements(),
        # shard jobs: the whole-job ceiling (3600 s) is checked against
        # the serial sum of the units' timeouts, not against one unit
        "remote": {"hosts": HOSTS},
        "options": {
            "timeout_s": 3480,
            "keep_artifacts": True,
            "waveforms": False,
            "save_mode": "netlist",
            "ngspice_init": ["set measureprec=12", "set numdgt=12"],
        },
    }


def render(req: dict) -> str:
    return json.dumps(req, indent=1) + "\n"


def request_path() -> Path:
    return TB_DIR / f"request-{REQUEST_NAME}.json"


def plan_text() -> str:
    return (
        f"{SLUG} at {PROCESS}/{TEMP_C} C/{VDD_V} V: {len(SEEDS)} units, "
        f"{len(measurements())} measurement cards each, tstop {TSTOP}.\n"
        f"request: {request_path().relative_to(REPO_ROOT)}\n"
        "backend: batch (never local; see sim/harness/klt_request.py)"
    )


# --------------------------------------------------------------------------
# Estimators (definitions copied from sim/tb/ro-ring5-starved-jitter-long/tb.json)
# --------------------------------------------------------------------------


def _lag_sigma(tc: list[float], lo: int, hi: int, lag: int, tbar: float, n_win: int) -> float:
    """sqrt(mean(r^2) / (1 - lag/n_win)) with r_i = (tc[i+lag] - tc[i]) - lag*tbar over
    i = lo .. hi-lag (inclusive tc[lo+lag..hi] minus tc[lo..hi-lag])."""
    r = [(tc[i + lag] - tc[i]) - lag * tbar for i in range(lo, hi - lag + 1)]
    return math.sqrt(sum(x * x for x in r) / len(r) / (1.0 - lag / n_win))


def derive(m: dict[str, float]) -> dict[str, float]:
    """The tb.json measurement set of the family, from one unit's primitives."""
    tc = list(m["tc"])
    lo, hi = SKIP, SKIP + WINDOW
    tbar = (tc[hi] - tc[lo]) / WINDOW
    tbars = (tc[STARTUP_N] - tc[0]) / STARTUP_N
    qw0, qw1, vavg = m["qw0"], m["qw1"], m["vsup_avg"]
    out: dict[str, float] = {"period": tbar, "f_osc": 1.0 / tbar, "period_startup16": tbars}
    for b in range(N_BLOCKS):
        out[f"period_b{b:02d}"] = (tc[(b + 1) * BLOCK] - tc[b * BLOCK]) / BLOCK
    for lag in LAGS:
        out[f"sigma_{lag}"] = _lag_sigma(tc, lo, hi, lag, tbar, WINDOW)
    for lag in STARTUP_LAGS:
        out[f"sigma_startup16_{lag}"] = _lag_sigma(tc, 0, STARTUP_N, lag, tbars, STARTUP_N)
    q = -CQ_F * (qw1 - qw0)
    out["i_ring_a"] = q / (tc[hi] - tc[lo])
    out["p_active_w"] = out["i_ring_a"] * vavg
    out["e_per_cycle_j"] = q / WINDOW * vavg
    out["c_eff_node_f"] = q / (WINDOW * N_STAGES * vavg)
    out["vsup_v"] = vavg
    return out


MEASURE_ORDER = (
    ["period", "f_osc", "period_startup16"]
    + [f"period_b{b:02d}" for b in range(N_BLOCKS)]
    + [f"sigma_{lag}" for lag in LAGS]
    + [f"sigma_startup16_{lag}" for lag in STARTUP_LAGS]
    + ["i_ring_a", "p_active_w", "e_per_cycle_j", "c_eff_node_f", "vsup_v"]
)


def unit_values(corner: dict) -> dict:
    """A unit's primitives: ``tc`` (the family's tc[0..768], present edges only up to the
    first gap) plus the scalar readings."""
    got = {x["name"]: x["value"] for x in corner.get("measurements", [])
           if x.get("value") is not None}
    out: dict = {k: v for k, v in got.items() if not k.startswith("tc_")}
    tc = []
    for k in range(N_EDGES):
        if edge_name(k) not in got:
            break
        tc.append(got[edge_name(k)])
    out["tc"] = tc
    return out


def unit_problems(corner: dict) -> list[str]:
    """Why a unit cannot feed the record, or [] when its primitives are complete."""
    if corner.get("status") not in ("ok", "pass", "passed"):
        return [f"unit status {corner.get('status')!r}"]
    v = unit_values(corner)
    miss = [n for n in ("qw0", "qw1", "vsup_avg") if n not in v]
    if miss:
        return [f"readings missing: {', '.join(miss)}"]
    tc = v.get("tc", [])
    if len(tc) < N_EDGES:
        return [f"only {len(tc)} of the {N_EDGES} edges the window needs were crossed "
                "(run too short for this corner's period)"]
    if any(b <= a for a, b in zip(tc, tc[1:])):
        return ["edge times are not strictly increasing"]
    return []


def duplicated_realizations(units: list[dict]) -> list[tuple[int, int]]:
    """Index pairs of units with bit-identical edge times: duplicated trnoise draws (DR-0031)."""
    seen: dict[tuple, int] = {}
    dup = []
    for i, u in enumerate(units):
        key = tuple(u["tc"])
        if key in seen:
            dup.append((seen[key], i))
        else:
            seen[key] = i
    return dup


# --------------------------------------------------------------------------
# Record ingestion
# --------------------------------------------------------------------------


def _fmt(x: float) -> str:
    return f"{x:.6e}" if abs(x) < 1e-3 or abs(x) >= 1e5 else f"{x:.6g}"


def result_lines(per_unit: list[dict[str, float]]) -> list[str]:
    lines = []
    for name in MEASURE_ORDER:
        vals = [u[name] for u in per_unit]
        mean = sum(vals) / len(vals)
        sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
        rel = f", {sd / abs(mean) * 100:.1f}% of mean" if mean else ""
        lines.append(f"- `{name}`: mean {_fmt(mean)} over {len(vals)} seeds "
                     f"(sd {_fmt(sd)}{rel}; min {_fmt(min(vals))}, max {_fmt(max(vals))})")
    return lines


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True,
                          check=True).stdout.strip()


def render_record(stem: str, report: dict, per_unit: list[dict[str, float]],
                  raw_files: list[tuple[str, str]], wall_s: float, date: str,
                  commit: str, tb_sha: str, dut_sha: str) -> str:
    env = report.get("environment", {})
    prov = report.get("provenance", {})
    fleet = (env.get("remote") or {}).get("fleet") or []
    # The simulating PDK is the fleet worker's, not the submitting host's (the client's
    # provenance names the host's own install, which the batch job does not read).
    stamps = sorted({(f.get("worker_environment") or {}).get("pdk", {}).get("stamp_text", "")
                     for f in fleet} - {""})
    pdk_ver = (stamps[0].replace("open_pdks ", "") if len(stamps) == 1
               else ("; ".join(stamps) or (prov.get("pdk") or {}).get("version") or "unknown"))
    klt_ver = prov.get("klt_version") or "unknown"
    jobs = [f.get("job_id") for f in fleet if f.get("job_id")]
    banners = sorted({((f.get("worker_environment") or {}).get("simulator") or {})
                      .get("version_banner", "").split("\n")[1].strip("* ").strip()
                      for f in fleet if ((f.get("worker_environment") or {}).get("simulator") or {})
                      .get("version_banner")})
    repro = _rep.reproduction_scope("tran-noise")
    seeds = ", ".join(str(s) for s in SEEDS[:len(per_unit)])
    job = ", ".join(jobs) if jobs else "not reported"
    ngspice = banners[0] if len(banners) == 1 else f"ngspice-{env.get('engine_version', 'unknown')}"
    fm = [
        "---", f"record: {stem}", f"date: {date}", "status: valid", "",
        "testbench:", f"  path: sim/tb/ro-ring5-starved-jitter-long-batch/{DECK}", f"  sha: {tb_sha}",
        "netlist:", f"  path: {DUT_PATH}", f"  sha: {dut_sha}",
        f"repo_commit: {commit}", "",
        f"pdk: gf180mcuD @ {pdk_ver}", "pdk.models:",
        f"  - libs.tech/ngspice/sm141064.ngspice (sections: {' '.join(SECTIONS)})", "",
        "tool:", f"  klt: {klt_ver} (client; batch backend)",
        f"  ngspice: \"{ngspice} (batch fleet)\"",
        f"  platform: \"{platform.platform()} (submitting host)\"", "",
        "corner:", f"  process: {PROCESS}", f"  voltage: {VDD_V:.3f} V (nominal 3.3 V, +10%)",
        f"  temperature: {TEMP_C}", "",
        "analysis:", "  type: tran-noise", f"  tstop: {TSTOP}",
        f"  tstep: {TSTEP} (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)",
        "  tmax: n/a", f"  noise_params: \"{DESCRIPTION_NOISE}\"", f"  runs: {len(per_unit)}",
        f"seeds: [{seeds}]",
    ]
    if repro:
        fm += ["reproduction:", f"  scope: {repro['scope']}",
               f"  trnoise_waveform_replay: {'true' if repro['trnoise_waveform_replay'] else 'false'}",
               f"  basis: {repro['basis']}", f"  decision: {repro['decision']}"]
    fm += ["", "raw:", f"  path: sim/records/raw/{stem}/", "  files:"]
    fm += [f"    - {n}  sha256:{d}" for n, d in raw_files]
    fm += [f"wall_time: {_rep._fmt_wall(wall_s)}", "---", ""]
    body = ["## Result", "",
            f"Executed on the batch fleet through `klt sim` (fleet jobs: {job}). Each unit returned the "
            "769 rising mid-supply edge times of the ring output and the charge readings; the "
            "figures below are the family's estimators computed from them by "
            "`sim/tools/starved_hot_corner.py` (definitions as in "
            "`sim/tb/ro-ring5-starved-jitter-long/tb.json`). The `seeds` are unit indices, not "
            "noise seeds.", ""]
    body += result_lines(per_unit)
    body += ["", f"Runs: {len(per_unit)} of {len(SEEDS)} successful. Summaries above use "
             "successful runs only.", "",
             "Numbers only. No entropy-rate or spec-compliance claim is made by this record.", "",
             "## How to reproduce", "", "```sh",
             f"python3 sim/tools/starved_hot_corner.py emit --check",
             f"python3 sim/tools/starved_hot_corner.py run --outdir DIR --backend batch",
             f"python3 sim/tools/starved_hot_corner.py ingest --report DIR/{REQUEST_NAME}.report.json",
             "```", ""]
    if repro and not repro["trnoise_waveform_replay"]:
        body += ["These commands replay the deck and configuration. They do not reproduce the "
                 "`trnoise` waveforms: on the ngspice-46 build measured in "
                 f"`{repro['basis']}` a re-run draws a fresh noise realization, so its measured "
                 "values will differ from the ones above. Exact waveform replay is not claimed. "
                 f"See `spec/decision-records/{repro['decision']}.md`.", ""]
    body += ["## Caveats", "",
             f"- Single corner ({PROCESS} / {VDD_V} V / {TEMP_C} C). Says nothing about any other corner.",
             "- Same circuit and stimulus as `sim/tb/ro-ring5-starved-jitter-long/`, but the "
             "estimators are computed from fleet-measured edge times rather than inside ngspice; "
             "edge times come from `.meas ... when` cards, interpolated as in the family's own bench.",
             "- `vsup_v` is the mean of v(vsup) over the whole run (the supply is an ideal DC "
             "source), not over the measurement window.",
             "- The PDK model content on the fleet is the one named in `pdk:` above, which may "
             "differ from the PDK of the family's earlier records; compare `pdk:` lines before "
             "pooling across records.",
             "", "---", "",
             "Written by `sim/tools/starved_hot_corner.py ingest`. Append-only: never edit or "
             "delete this file -- a re-run or correction mints a new record and points back "
             "here via `supersedes` (see `sim/README.md`).", ""]
    return "\n".join(fm + body)


def cmd_ingest(report_path: Path, stderr_path: Path | None, request: Path | None,
               records_dir: Path, now: _dt.datetime | None = None) -> int:
    report = json.loads(report_path.read_text())
    corners = report.get("corners", [])
    if len(corners) != len(SEEDS):
        print(f"refused: report has {len(corners)} units, the declared grid has {len(SEEDS)}",
              file=sys.stderr)
        return 2
    bad = [(i, unit_problems(c)) for i, c in enumerate(corners) if unit_problems(c)]
    if bad:
        for i, p in bad:
            print(f"refused: unit {i + 1}: {'; '.join(p)}", file=sys.stderr)
        return 2
    vals = [unit_values(c) for c in corners]
    dup = duplicated_realizations(vals)
    if dup:
        print("refused: bit-identical edge times (duplicated trnoise realization) in unit pairs "
              + ", ".join(f"{a + 1}&{b + 1}" for a, b in dup), file=sys.stderr)
        return 2
    per_unit = [derive(v) for v in vals]
    now = now or _dt.datetime.now(_dt.timezone.utc)
    day = now.strftime("%Y-%m-%d")
    stem = _rep.allocate_record_stems(records_dir, day, SLUG, 1)[0]
    raw_dir = records_dir / "raw" / stem
    raw_dir.mkdir(parents=True, exist_ok=False)
    (raw_dir / "report.json").write_text(json.dumps(report, indent=1) + "\n")
    (raw_dir / "request.json").write_text((request or request_path()).read_text())
    if stderr_path and stderr_path.exists():
        (raw_dir / "stderr.txt").write_text(stderr_path.read_text())
    names = sorted(p.name for p in raw_dir.iterdir())
    raw_files = [(n, _rep.sha256_file(raw_dir / n)) for n in names]
    wall = sum(float(c.get("runtime_s") or 0.0) for c in corners)
    commit = _git("rev-parse", "HEAD") + ("-dirty" if _git("status", "--porcelain") else "")
    tb_sha = _rep.git_blob_sha1((TB_DIR / DECK).read_bytes())
    dut_sha = _rep.git_blob_sha1((REPO_ROOT / DUT_PATH).read_bytes())
    text = render_record(stem, report, per_unit, raw_files, wall,
                         now.strftime("%Y-%m-%dT%H:%M:%SZ"), commit, tb_sha, dut_sha)
    _rep.publish_record_text(records_dir / f"{stem}.md", text)
    print(f"wrote sim/records/{stem}.md")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def cmd_emit(check: bool) -> int:
    return _kreq.emit_requests(
        [(request_path(), render(build_request()))], check, repo_root=REPO_ROOT,
        ok=lambda: print("ok: request matches the declared grid"))


def cmd_run(outdir: str, backend: str, klt_cmd: str) -> int:
    return _kreq.run_klt_request(outdir, REQUEST_NAME, request_path(), backend, klt_cmd)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    e = sub.add_parser("emit")
    e.add_argument("--check", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("--outdir", required=True)
    r.add_argument("--backend", default="batch", choices=("batch", "local"))
    r.add_argument("--klt", default="klt", dest="klt_cmd")
    i = sub.add_parser("ingest")
    i.add_argument("--report", required=True)
    i.add_argument("--stderr")
    i.add_argument("--request")
    args = ap.parse_args(argv)
    if args.cmd == "plan":
        print(plan_text())
        return 0
    if args.cmd == "emit":
        return cmd_emit(args.check)
    if args.cmd == "run":
        return cmd_run(args.outdir, args.backend, args.klt_cmd)
    return cmd_ingest(Path(args.report), Path(args.stderr) if args.stderr else None,
                      Path(args.request) if args.request else None,
                      REPO_ROOT / "sim" / "records")


if __name__ == "__main__":
    sys.exit(main())
