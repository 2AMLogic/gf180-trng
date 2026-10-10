#!/usr/bin/env python3
"""Per-net switching-activity capture and validation for the post-route
netlist (#453; DR-0023's named follow-up).

    python3 sim/tb/digital-sta-power/activity.py capture            # all workloads
    python3 sim/tb/digital-sta-power/activity.py capture --workload backpressure
    python3 sim/tb/digital-sta-power/activity.py validate           # re-check the manifest on disk
    python3 sim/tb/digital-sta-power/activity.py --list

What it does
------------
1. Builds each seeded workload of
   ``sim/tb/trng-top-post-route/activity_workloads.py`` (declared capture
   windows: reset / start-up / steady), packs it into a stimulus file and
   simulates the **as-built** ``layout/digital/trng_top.pnr.v`` (CTS buffers
   and resized cells included) with Icarus Verilog against the PDK's cell
   models, ``-gno-specify`` (zero delay: activity is a logic property here,
   timing stays with OpenSTA), at the ratified 1 MHz clock.
2. Dumps a VCD of the whole DUT hierarchy (cell instances and their ports),
   because OpenSTA binds ``read_vcd`` activity to *pins* by hierarchical path;
   a net-only dump annotates the top-level ports and nothing else (verified
   while bringing this up: 109 of 5371 pins).
3. Normalises the one non-reproducible VCD header field (``$date``) so the
   file's sha256 is a stable identity, and writes ``manifest.json`` with the
   trace hashes, stimulus hashes, seeds, windows, and the netlist / cell
   model / simulator identities.
4. Validates each trace *before* it can be used (``validate_trace``):
   empty traces, a missing/wrong DUT scope, a netlist whose instance set does
   not match the trace's, a clock that does not toggle as declared, and a
   window outside the trace are all rejected with ``ActivityError``. The
   OpenSTA-side annotation check is ``validate_annotation``.

What this is not
----------------
Not a silicon current measurement, and not a worst case: five declared
workloads, each a synthetic stimulus (the raw bits make no entropy claim).
Zero-delay simulation also means no glitches beyond same-timestamp delta
activity, which ``summarize_vcd`` counts separately so the optimism is
visible rather than assumed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

TB_DIR = Path(__file__).resolve().parent
SIM_DIR = TB_DIR.parents[1]
REPO_ROOT = SIM_DIR.parent

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(SIM_DIR / "tb" / "trng-top-post-route"))

from harness import report  # noqa: E402

import activity_workloads as wl  # noqa: E402

PNR_NETLIST = REPO_ROOT / "layout" / "digital" / "trng_top.pnr.v"
DEF_PATH = REPO_ROOT / "layout" / "digital" / "trng_top.def"
TB_SOURCE = TB_DIR / "activity_tb.v"
CELL_LIBRARY = "gf180mcu_fd_sc_mcu9t5v0"
WORK_DIR = REPO_ROOT / "layout" / ".work" / "digital-sta-activity"
MANIFEST_NAME = "manifest.json"
#: Scope the DUT is instantiated at in `activity_tb.v`; passed to OpenSTA's
#: `read_vcd -scope` (hierarchy divider `/`).
DUT_SCOPE = ("tb", "dut")
STA_SCOPE = "/".join(DUT_SCOPE)

#: OpenSTA must bind at least this fraction of the design's pins to VCD
#: activity, or the trace is rejected as an annotation failure. Everything
#: below 100 % is reported as unannotated (fallback) pins in the record.
MIN_ANNOTATED_FRACTION = 0.99

#: The VCD time unit the capture is run in (picoseconds, from `activity_tb.v`'s
#: `timescale 1ns/1ps` -- Icarus dumps in the precision unit).
VCD_TICKS_PER_NS = 1000

_TIMESCALE_UNIT_PS = {"s": 10**12, "ms": 10**9, "us": 10**6, "ns": 10**3, "ps": 1, "fs": 1e-3}


class ActivityError(RuntimeError):
    """A trace cannot be used as activity evidence. Never downgraded to a
    warning: an unusable trace must not become a number."""


# --------------------------------------------------------------------------- #
# VCD summary
# --------------------------------------------------------------------------- #


@dataclass
class VcdSummary:
    timescale_ps: float = 0.0
    end_time_ticks: int = 0
    n_vars: int = 0
    n_value_changes: int = 0
    dut_found: bool = False
    #: Names of the DUT's direct child scopes (the netlist's cell instances),
    #: backslash-escaping removed.
    instances: set = field(default_factory=set)
    #: Port-level variables directly in the DUT scope.
    ports: set = field(default_factory=set)
    #: window name -> {"clk_toggles", "changes", "toggling_vars"}.
    windows: dict = field(default_factory=dict)
    #: Variables that ever carried an x/z value, and how many value-change
    #: events were x/z.
    xz_vars: int = 0
    xz_events: int = 0
    #: Value changes that were not the first on their (var, timestamp):
    #: zero-delay delta activity that a VCD records but OpenSTA counts as
    #: ordinary toggles.
    same_timestamp_extra_changes: int = 0

    def as_dict(self) -> dict:
        d = dict(self.__dict__)
        d["instances"] = len(self.instances)
        d["ports"] = sorted(self.ports)
        return d


def _unescape(name: str) -> str:
    return name[1:] if name.startswith("\\") else name


def summarize_vcd(path: Path, windows_ticks: dict[str, tuple[int, int]]) -> VcdSummary:
    """One streaming pass over a VCD (hundreds of thousands of lines).

    ``windows_ticks`` maps a window name to a half-open ``[begin, end)``
    interval in the file's own time ticks.
    """
    s = VcdSummary(windows={n: {"clk_toggles": 0, "changes": 0, "toggling_vars": set()}
                            for n in windows_ticks})
    scope: list[str] = []
    id_scope_depth: dict[str, int] = {}
    id_is_clk: set[str] = set()
    var_ids: set[str] = set()
    xz_ids: set[str] = set()
    last_val: dict[str, str] = {}
    last_time_of: dict[str, int] = {}
    now = 0
    in_defs = True
    saw_enddefs = False
    timescale_pending = False
    ts_text = ""

    def window_of(t: int):
        for name, (lo, hi) in windows_ticks.items():
            if lo <= t < hi:
                yield name

    def record(vid: str, val: str) -> None:
        s.n_value_changes += 1
        if "x" in val or "z" in val or "X" in val or "Z" in val:
            s.xz_events += 1
            xz_ids.add(vid)
        if last_time_of.get(vid) == now:
            s.same_timestamp_extra_changes += 1
        last_time_of[vid] = now
        prev = last_val.get(vid)
        last_val[vid] = val
        if prev is None or prev == val:
            return
        for w in window_of(now):
            win = s.windows[w]
            win["changes"] += 1
            win["toggling_vars"].add(vid)
            if vid in id_is_clk:
                win["clk_toggles"] += 1

    with path.open("r", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if in_defs:
                if timescale_pending or line.startswith("$timescale"):
                    ts_text += " " + line.replace("$timescale", "")
                    timescale_pending = "$end" not in line
                    if not timescale_pending:
                        m = re.search(r"(\d+)\s*(fs|ps|ns|us|ms|s)\b", ts_text)
                        if m:
                            s.timescale_ps = int(m.group(1)) * _TIMESCALE_UNIT_PS[m.group(2)]
                    continue
                if line.startswith("$scope"):
                    scope.append(_unescape(line.split()[2]))
                    if tuple(scope[:2]) == DUT_SCOPE:
                        s.dut_found = True
                        if len(scope) == 3:
                            s.instances.add(scope[2])
                    continue
                if line.startswith("$upscope"):
                    if scope:
                        scope.pop()
                    continue
                if line.startswith("$var"):
                    parts = line.split()
                    vid, name = parts[3], _unescape(parts[4])
                    s.n_vars += 1
                    var_ids.add(vid)
                    if tuple(scope) == DUT_SCOPE:
                        s.ports.add(name)
                        if name == "clk":
                            id_is_clk.add(vid)
                    continue
                if line.startswith("$enddefinitions"):
                    in_defs = False
                    saw_enddefs = True
                continue
            # --- value-change section ---
            c = line[0]
            if c == "#":
                try:
                    now = int(line[1:])
                except ValueError:
                    continue
                s.end_time_ticks = max(s.end_time_ticks, now)
            elif c in "01xXzZ":
                record(line[1:], c.lower())
            elif c in "bBrR":
                parts = line.split()
                if len(parts) == 2:
                    record(parts[1], parts[0][1:].lower())
            # $dumpvars / $end / $comment lines fall through.
    if not saw_enddefs:
        s.n_vars = 0
    s.xz_vars = len(xz_ids)
    for win in s.windows.values():
        win["toggling_vars"] = len(win["toggling_vars"])
    return s


# --------------------------------------------------------------------------- #
# Netlist
# --------------------------------------------------------------------------- #

_INST = re.compile(
    rf"^\s*{CELL_LIBRARY}__\w+\s+(\\\S+|\S+)\s*\(", re.M
)


def netlist_instances(path: Path = PNR_NETLIST) -> set[str]:
    return {_unescape(m.group(1)) for m in _INST.finditer(path.read_text())}


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #


def windows_to_ticks(windows: dict[str, tuple[int, int]], period_ns: float,
                     ticks_per_ns: int = VCD_TICKS_PER_NS) -> dict[str, tuple[int, int]]:
    per_cycle = int(round(period_ns * ticks_per_ns))
    return {n: (a * per_cycle, b * per_cycle) for n, (a, b) in windows.items()}


def validate_trace(summary: VcdSummary, *, netlist_insts: set[str],
                   windows: dict[str, tuple[int, int]], period_ns: float,
                   total_cycles: int) -> dict:
    """Raise ``ActivityError`` unless the trace is usable; else return the
    coverage numbers the record quotes."""
    if summary.n_vars == 0 or summary.n_value_changes == 0:
        raise ActivityError(
            f"empty trace: {summary.n_vars} variables, "
            f"{summary.n_value_changes} value changes"
        )
    if not summary.dut_found:
        raise ActivityError(
            f"no DUT scope {'.'.join(DUT_SCOPE)!r} in the trace -- a wrong "
            "scope would annotate nothing"
        )
    if summary.timescale_ps <= 0:
        raise ActivityError("trace declares no parseable $timescale")
    expected_ps = total_cycles * period_ns * 1000
    got_ps = summary.end_time_ticks * summary.timescale_ps
    if got_ps < expected_ps - period_ns * 1000:
        raise ActivityError(
            f"trace ends at {got_ps / 1000:.0f} ns but the workload spans "
            f"{expected_ps / 1000:.0f} ns"
        )
    missing = netlist_insts - summary.instances
    extra = summary.instances - netlist_insts
    if missing or extra:
        raise ActivityError(
            f"trace does not describe this netlist: {len(missing)} netlist "
            f"instances absent from the trace (e.g. {sorted(missing)[:3]}), "
            f"{len(extra)} trace instances not in the netlist "
            f"(e.g. {sorted(extra)[:3]})"
        )
    if "clk" not in summary.ports:
        raise ActivityError("trace has no `clk` variable in the DUT scope")
    per_cycle = int(round(period_ns * VCD_TICKS_PER_NS * 1000 / summary.timescale_ps / 1000))
    ticks = windows_to_ticks(windows, period_ns, int(round(1000 / summary.timescale_ps)))
    coverage = {}
    for name, (lo, hi) in windows.items():
        win = summary.windows.get(name)
        if win is None or win["changes"] == 0:
            raise ActivityError(f"capture window {name!r} contains no value changes")
        cycles = hi - lo
        # clk starts low and toggles twice per cycle; the very first window
        # begins with a settled initial value, so allow the unavoidable 1.
        if abs(win["clk_toggles"] - 2 * cycles) > 1:
            raise ActivityError(
                f"window {name!r}: clk toggled {win['clk_toggles']} times, "
                f"expected {2 * cycles} for {cycles} cycles"
            )
        coverage[name] = {
            "cycles": cycles,
            "clk_toggles": win["clk_toggles"],
            "value_changes": win["changes"],
            "toggling_vars": win["toggling_vars"],
        }
    del per_cycle, ticks
    return {
        "netlist_instances": len(netlist_insts),
        "trace_instances": len(summary.instances),
        "instances_matched": len(netlist_insts & summary.instances),
        "trace_vars": summary.n_vars,
        "xz_vars": summary.xz_vars,
        "xz_events": summary.xz_events,
        "same_timestamp_extra_changes": summary.same_timestamp_extra_changes,
        "windows": coverage,
    }


_ANNOT = re.compile(r"^Annotated\s+(\d+)\s+pin activities", re.M)
_ANNOT_VCD = re.compile(r"^vcd\s+(\d+)\s*$", re.M)
_ANNOT_UNANN = re.compile(r"^unannotated\s+(\d+)\s*$", re.M)


def parse_annotation_report(text: str) -> dict:
    """Parse the lines OpenSTA's `report_activity_annotation` prints.

    Absent counters are 0 (OpenSTA omits a source row it never used), but an
    output with no ``Annotated N pin activities`` line at all is a parse
    failure, not "zero annotated"."""
    m = _ANNOT.search(text)
    if not m:
        raise ActivityError("OpenSTA printed no activity-annotation summary")
    vcd = _ANNOT_VCD.search(text)
    un = _ANNOT_UNANN.search(text)
    return {
        "annotated": int(m.group(1)),
        "vcd": int(vcd.group(1)) if vcd else 0,
        "unannotated": int(un.group(1)) if un else 0,
    }


def validate_annotation(ann: dict, label: str = "") -> dict:
    total = ann["vcd"] + ann["unannotated"]
    if ann["vcd"] == 0 or total == 0:
        raise ActivityError(
            f"{label}OpenSTA bound no VCD activity to any pin "
            f"(vcd={ann['vcd']}, unannotated={ann['unannotated']}) -- wrong "
            "scope, wrong netlist or empty trace"
        )
    frac = ann["vcd"] / total
    if frac < MIN_ANNOTATED_FRACTION:
        raise ActivityError(
            f"{label}only {frac:.1%} of {total} pins annotated from the VCD "
            f"(< {MIN_ANNOTATED_FRACTION:.0%}); {ann['unannotated']} pins "
            "would run on fallback activity"
        )
    return {**ann, "total_pins": total, "annotated_fraction": frac}


# --------------------------------------------------------------------------- #
# Capture
# --------------------------------------------------------------------------- #


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def normalize_vcd(path: Path) -> None:
    """Replace the `$date` block (the only run-dependent header field) so the
    file's sha256 identifies its content."""
    text = path.read_text(errors="replace")
    text = re.sub(r"\$date\n.*?\$end\n", "$date\n\t(normalized for checksum stability)\n$end\n",
                  text, count=1, flags=re.S)
    path.write_text(text)


def tool_version(cmd: list[str]) -> str | None:
    if shutil.which(cmd[0]) is None:
        return None
    done = subprocess.run(cmd, capture_output=True, text=True, check=False)
    first = (done.stdout or done.stderr).strip().splitlines()
    return first[0] if first else None


def library_verilog(pdk) -> list[Path]:
    d = Path(pdk.path) / "libs.ref" / CELL_LIBRARY / "verilog"
    return [d / f"{CELL_LIBRARY}.v", d / "primitives.v"]


def compile_bench(pdk, work: Path) -> Path:
    vvp = work / "activity_tb.vvp"
    cmd = ["iverilog", "-g2012", "-gno-specify", "-o", str(vvp), str(TB_SOURCE),
           str(PNR_NETLIST), *(str(p) for p in library_verilog(pdk))]
    done = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise ActivityError(f"iverilog failed:\n{done.stderr[-2000:]}")
    return vvp


def capture_workload(name: str, vvp: Path, work: Path) -> dict:
    rows, windows = wl.build(name)
    stim = work / f"{name}.stim.hex"
    stim.write_text(wl.stimulus_hex(rows))
    vcd = work / f"{name}.vcd"
    done = subprocess.run(
        ["vvp", str(vvp), f"+STIM={stim}", f"+CYCLES={len(rows)}",
         f"+VCD={vcd}", f"+PERIOD_NS={wl.SIM_CLOCK_NS}"],
        capture_output=True, text=True, check=False,
    )
    if done.returncode != 0 or not vcd.is_file():
        raise ActivityError(f"vvp failed for {name}: {done.stdout[-500:]}{done.stderr[-500:]}")
    normalize_vcd(vcd)
    insts = netlist_instances()
    summary = summarize_vcd(vcd, windows_to_ticks(windows, wl.SIM_CLOCK_NS))
    coverage = validate_trace(summary, netlist_insts=insts, windows=windows,
                              period_ns=wl.SIM_CLOCK_NS, total_cycles=len(rows))
    w = wl.WORKLOADS[name]
    return {
        "workload": name,
        "why": w.why,
        "seed": w.seed,
        "base_seed": wl.BASE_SEED,
        "clock": w.clock,
        "clock_period_ns": wl.SIM_CLOCK_NS,
        "cycles": len(rows),
        "windows_cycles": {k: list(v) for k, v in windows.items()},
        "windows_ps": {k: [a * int(wl.SIM_CLOCK_NS * 1000), b * int(wl.SIM_CLOCK_NS * 1000)]
                       for k, (a, b) in windows.items()},
        "stimulus_sha256": wl.stimulus_sha256(rows),
        "vcd_path": _rel(vcd),
        "vcd_sha256": report.sha256_file(vcd),
        "vcd_bytes": vcd.stat().st_size,
        "vcd_time_unit_ps": summary.timescale_ps,
        "validation": coverage,
    }


def identities(pdk) -> dict:
    return {
        "netlist": {
            "path": str(PNR_NETLIST.relative_to(REPO_ROOT)),
            "git_blob_sha": report.blob_sha(REPO_ROOT, PNR_NETLIST),
            "instances": len(netlist_instances()),
        },
        "def_git_blob_sha": report.blob_sha(REPO_ROOT, DEF_PATH),
        "cell_models": [
            {"path": f"<pdk>/{p.relative_to(Path(pdk.path))}", "sha256": report.sha256_file(p)}
            for p in library_verilog(pdk)
        ],
        "testbench": {
            "path": str(TB_SOURCE.relative_to(REPO_ROOT)),
            "git_blob_sha": report.blob_sha(REPO_ROOT, TB_SOURCE),
        },
        "workloads_module_git_blob_sha": report.blob_sha(
            REPO_ROOT, SIM_DIR / "tb" / "trng-top-post-route" / "activity_workloads.py"),
        "simulator": tool_version(["iverilog", "-V"]),
        "simulator_flags": "-g2012 -gno-specify (zero delay; specify blocks ignored)",
        "x_z_handling": (
            "x/z values are kept verbatim in the VCD and counted in "
            "`validation.xz_events`/`xz_vars` (FIFO memory flops without a "
            "reset port hold x until written); how OpenSTA's VCD reader "
            "treats a transition through x/z is that tool's behaviour and "
            "is not independently verified here"
        ),
        "clock_activity": (
            "clk is simulated at the stated period, 50 % duty, and its toggle "
            "count is checked against the window length; OpenSTA derives "
            "clock-network activity from the propagated clock"
        ),
    }


def capture(names: list[str], work: Path) -> dict:
    pdk = _pdk()
    work.mkdir(parents=True, exist_ok=True)
    vvp = compile_bench(pdk, work)
    traces = {}
    for name in names:
        traces[name] = capture_workload(name, vvp, work)
        t = traces[name]
        print(f"{name:26s} {t['cycles']:5d} cycles  {t['vcd_bytes'] / 1e6:6.2f} MB  "
              f"vcd sha256:{t['vcd_sha256'][:16]}  stim sha256:{t['stimulus_sha256'][:16]}")
    manifest = {"schema": 1, "identities": identities(pdk), "traces": traces}
    (work / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def _pdk():
    from harness import pdk as pdk_mod
    try:
        return pdk_mod.find_pdk()
    except Exception as exc:
        raise ActivityError(f"no gf180mcu PDK install found: {exc}") from exc


def load_manifest(path: Path) -> dict:
    """Load a manifest and re-verify what it pins: the netlist, the VCD
    bytes and the regenerated stimulus. A stale manifest is an error, not a
    warning -- it would put a number next to a netlist it never described."""
    manifest = json.loads(path.read_text())
    ident = manifest["identities"]
    current = report.blob_sha(REPO_ROOT, PNR_NETLIST)
    if ident["netlist"]["git_blob_sha"] != current:
        raise ActivityError(
            f"manifest was captured from netlist blob {ident['netlist']['git_blob_sha']}, "
            f"layout/digital/trng_top.pnr.v is now {current}; re-run `capture`"
        )
    for name, t in manifest["traces"].items():
        vcd = REPO_ROOT / t["vcd_path"]
        if not vcd.is_file():
            raise ActivityError(f"trace for {name} missing: {t['vcd_path']}")
        if report.sha256_file(vcd) != t["vcd_sha256"]:
            raise ActivityError(f"trace for {name} no longer matches its recorded sha256")
        rows, _ = wl.build(name)
        if wl.stimulus_sha256(rows) != t["stimulus_sha256"]:
            raise ActivityError(
                f"workload {name} no longer generates the stimulus this trace was captured from"
            )
    return manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", nargs="?", choices=("capture", "validate"))
    ap.add_argument("--workload", action="append", help="workload(s); default all")
    ap.add_argument("--out", type=Path, default=WORK_DIR)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)
    if args.list or not args.command:
        for name, w in wl.WORKLOADS.items():
            rows, win = wl.build(name)
            print(f"{name:26s} {len(rows):5d} cycles  seed {w.seed}  {win}")
        return 0
    names = args.workload or list(wl.WORKLOADS)
    for n in names:
        if n not in wl.WORKLOADS:
            print(f"error: unknown workload {n!r}", file=sys.stderr)
            return 2
    try:
        if args.command == "capture":
            capture(names, args.out)
        else:
            load_manifest(args.out / MANIFEST_NAME)
            print(f"manifest {args.out / MANIFEST_NAME} verifies")
    except ActivityError as exc:
        print(f"REJECTED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
