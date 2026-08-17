#!/usr/bin/env python3
"""Synthesize `trng_top`'s digital wiring against gf180mcu, headless.

    python3 design/synth.py            # (re-)synthesize, write netlist + report
    python3 design/synth.py --check    # re-synthesize to scratch and diff; never writes

This is the digital-half analogue of `design/netlist.py`: a committed,
regenerable artefact plus a `--check` staleness guard, so that a claim about
the digital partition's gate count/area is backed by a netlist a reader can
actually fetch rather than a number typed into a PR description. Where
`netlist.py` drives xschem over the analog schematics, this drives `klt
synthesize` (Yosys + bundled ABC, via `layout/_klt.py`'s shared subprocess
plumbing) over the digital RTL under `design/trng_top/`, `design/conditioner/`,
`design/health_test/` and `design/interface/`.

One netlist, not five
----------------------
This script synthesizes exactly one unit: `trng_top` with its four child
modules as `sources`, `hdl_toplevel="trng_top"`. The reason is what
*consumes* a gate-level netlist, not what verifies the RTL. Both named
consumers want the whole digital partition as one design:

- place-and-route (#111) places a single flattened top-level design; four
  separate per-block netlists would have to be re-stitched into exactly
  that before P&R could start;
- digital STA/characterization (#145) times the assembled digital
  partition, including the paths that cross between sub-blocks — paths
  that only exist in the stitched-together design.

Splitting the *synthesis* output per sub-block would therefore create work
(re-stitching) with no consumer asking for the split. This is the ordinary
way a synthesis-for-P&R target is scoped: to the unit that gets placed.

Note that this is a **different** rationale from the analog side's
per-block split (`design/README.md`: `ro_array_core`, `sampler_core`,
`meta_arb`, ... each exported and committed separately). DR-0009's analog
split follows the transistor-level testbenches under `sim/tb/`, and the
digital half does have that same per-block verification structure — each
of the four sub-blocks is elaborated standalone in its own RTL-equivalence
testbench (`sim/tb/conditioner-crc32/tb_rtl_equivalence.v`,
`sim/tb/health-test-fault-injection/tb_rtl_equivalence.v`,
`sim/tb/ring-liveness-fault-injection/tb_rtl_equivalence.v`,
`sim/tb/interface-regfile/tb_rtl_equivalence.v`, driven from
`sim/tests/test_conditioner.py`, `test_health_test.py`,
`test_ring_liveness.py` and `test_interface.py` respectively), alongside
`sim/tests/test_trng_top.py`'s combined elaboration of all five together.
Those testbenches are RTL-vs-behavioral-model equivalence checks, which is
a different kind of evidence than a per-block synthesized netlist would
be: none of them reads a gate-level netlist, so none of them would gain
anything from one. Per-block RTL coverage is therefore not an argument for
per-block synthesis targets either way — the flattening decision rests on
the consumers above.

What `klt synthesize` is, and is not
--------------------------------------
`klt synthesize` runs Yosys's `read_verilog` -> `hierarchy` -> `synth` ->
`dfflibmap` -> `abc -liberty` -> `clean` -> `stat`/`write_verilog` pipeline
against a resolved liberty and reports `instance_count`, `area_um2`,
`sequential_area_um2` and `instance_counts_by_type` — the netlist and the
counts this script commits. It does **not** place or route anything (that
is `klt place-and-route`, #111's still-open scope) and it does **not**
perform signoff timing analysis.

The response does carry a `timing` object (`{"source": "abc_stime",
"wire_load": null, "critical_path_ps": ..., "delay_target_ps": null}`) —
ABC's own `stime -p` estimate over the mapped netlist, wired in by
klayout-tools issue #807 after this repo's own #143 was filed expecting a
bare `timing: null`. It is real output, so this script commits it verbatim
rather than fabricating the `null` the issue anticipated. But it is, in
`klayout_tools.synthesize`'s own words, "a pre-layout, wire-free estimate"
(`wire_load` reports `"none"`) — no wire delay, no parasitics, no SDC, not
even a real static-timing walk of the netlist (that is the separate,
also-null-here `sta` field, gated on the optional `klt_statime_native`
extension) — "never signoff STA". **Nothing in this repository derives an
Fmax or any other timing claim from this field.** Digital timing closure is
DR-0009 rule 6's still-open item and a future characterization issue's job
(#145), not this script's.

Liberty corner
--------------
`CORNER` below pins the mapping deck explicitly, rather than trusting `klt`'s
own nominal-corner resolution (`klt pdk cells`'s documented "lowest of the
characterised supplies" pick, `tt_025C_1v80` for this library) the way this
script used to. This block does not run at 1.8 V: `design/README.md` calls
3.3 V "the block's ratified supply", and DR-0003's raw-rate row binds at
`ss` / −10 % supply / +125 degC (3.3 V − 10 % = 2.97 V), for which this
library's closest shipped deck is `ss_125C_3v00`. That is exactly the
reasoning `layout/digital/build.py`'s own `CORNER` constant uses to pin its
P&R run — but this script pins a **different** deck, `tt_025C_3v30`, and the
difference is deliberate, not an oversight:

`klt synthesize`'s ABC step performs *delay-driven mapping*: it picks cells
and drive strengths to meet a timing estimate at whichever corner the request
names, and it does not do signoff timing analysis or any form of timing
closure (see "What `klt synthesize` is, and is not" below) — that is
`layout/digital/build.py`'s job, which re-optimizes (resizes cells during
CTS/placement) against `ss_125C_3v00`, the ratified binding corner, on
*this* script's output. Mapping the initial netlist against the same
worst-case slow/hot/low-voltage corner would only bias ABC toward
larger-than-typical drive strengths before P&R gets a chance to size
anything itself, inflating the pre-place netlist's area without changing
what actually gets signed off. `tt_025C_3v30` — typical process, 25 degC,
3.30 V — is the conventional synthesis target for exactly this reason: a
balanced starting point at the block's real operating voltage (3.3 V, unlike
the old 1.8 V pick), leaving corner-specific timing closure to the P&R stage
that is actually equipped to perform it. `layout/digital/README.md`'s
"Corners" section reasons through this same `tt_025C_3v30`-vs-`ss_125C_3v00`
question for the P&R step and reaches the opposite answer for a P&R-specific
reason (implementing *at* the binding corner is what makes P&R's own slack
figure meaningful) — that reasoning is P&R-specific and does not transfer to
a pre-place, non-closing synthesis mapping step.

Provenance
----------
The committed `design/trng_top/trng_top.synth.json` report carries, inside
its `provenance` block (from `klayout_tools._provenance.build_provenance`,
the same helper `klt drc`/`klt lvs`/`klt extract` use): the installed `klt`
version, the KLayout engine build, the resolved PDK variant + open_pdks
version, and the liberty deck's own name + content hash (`<cell_library>__
<corner>`, i.e. `gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30` per `CORNER` above —
no longer `klt`'s own nominal-corner resolution; see "Liberty corner" above
for why it is now pinned). On top of that this script adds its own
`rtl_sources` array — one `{path, content_hash}` entry per source file —
because `provenance.input` alone only carries one combined, order-independent
hash across all five sources (`klayout_tools.synthesize._combined_content_hash`),
which cannot say *which* file changed. `rtl_sources` can.

Determinism
-----------
Unlike xschem's SPICE export (`netlist.py`'s own docstring), Yosys's
`write_verilog -noattr` here embeds no absolute filesystem path and no
timestamp — verified empirically by running this script's own synthesis
twice from two different scratch directories and diffing the two netlists
byte-for-byte (identical). So no rewrap/normalisation step is needed the way
`netlist.py` needs one for xschem's continuation-line wrapping; the netlist
`klt synthesize` writes is committed as-is. The one field that *does* embed
an invocation-specific path is the JSON envelope's own `netlist_path`
(pointing at the scratch `.klt/synthesize/` directory this run used), which
this script restates to the committed path before writing/comparing — the
same "restate the one field that names a scratch location" treatment
`layout/verify.py`'s own `_committed_view` gives `klt extract`'s
`netlist_path`. `script_path` (the generated `.ys` script) is restated to
`null` rather than committed: it is a pure, deterministic function of this
script's own constants below plus `layout/_klt.py`'s PDK resolution, so
committing it would duplicate information already in this file without
adding anything a reader could not regenerate with
`python3 design/synth.py`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DESIGN_DIR = REPO_ROOT / "design"
TRNG_TOP_DIR = DESIGN_DIR / "trng_top"

sys.path.insert(0, str(REPO_ROOT))

from layout._klt import FlowError, _run_klt, klt_origin, klt_version, resolve_pdk  # noqa: E402

#: The one synthesized unit -- see the module docstring's "One netlist, not
#: five" section. `trng_top.v` is `hdl_toplevel`; the other four are its
#: instantiated children (design/trng_top/trng_top.v's own instance list).
TOP = "trng_top"
SOURCES = (
    "design/trng_top/trng_top.v",
    "design/conditioner/crc32_conditioner.v",
    "design/health_test/rct_apt.v",
    "design/health_test/ring_liveness.v",
    "design/interface/trng_interface.v",
)

#: The gf180mcu digital standard-cell library -- NOT sky130 (klayout-tools#629,
#: resolved upstream via klayout-tools#631; see layout/cells/README.md).
CELL_LIBRARY = "gf180mcu_fd_sc_mcu9t5v0"

#: The liberty corner `klt synthesize`'s ABC step maps against, named
#: explicitly rather than left to `klt`'s own nominal-corner resolution --
#: see the module docstring's "Liberty corner" section for the full
#: reasoning, including why this deliberately differs from
#: `layout/digital/build.py`'s `ss_125C_3v00` P&R corner.
CORNER = "tt_025C_3v30"

NETLIST_PATH = TRNG_TOP_DIR / f"{TOP}.synth.v"
REPORT_PATH = TRNG_TOP_DIR / f"{TOP}.synth.json"

EXIT_OK = 0
EXIT_STALE = 1
EXIT_ENVIRONMENT = 3


class SynthError(RuntimeError):
    """A synthesis run could not even be attempted or did not complete."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return f"sha256:{digest.hexdigest()}"


def _rtl_sources() -> list[dict]:
    """`{path, content_hash}` for every RTL source, in `SOURCES` order.

    `path` is repo-relative (stable across machines/checkouts); see the
    module docstring's "Provenance" section for why this exists alongside
    `klt`'s own combined `provenance.input.content_hash`.
    """
    return [
        {"path": src, "content_hash": _sha256_file(REPO_ROOT / src)}
        for src in SOURCES
    ]


def _check_environment() -> list[str]:
    """Human-readable reasons a synthesis run cannot proceed, or `[]`."""
    missing = []
    if klt_version() is None:
        missing.append("klayout-tools (`klt`) is not on PATH")
    if shutil.which("yosys") is None:
        missing.append(
            "yosys is not on PATH (`klt synthesize` shells out to it as a "
            "subprocess -- install Yosys and put it on PATH)"
        )
    if resolve_pdk() is None:
        missing.append("no gf180mcu PDK install found (see sim/harness/pdk.py)")
    return missing


def _write_request(request_path: Path) -> None:
    """Write the `klt synthesize` request document `request_path` names.

    `sources` are absolute so the request resolves correctly regardless of
    where `request_path` itself lives (a fresh `tempfile.TemporaryDirectory()`
    every call, per `synthesize()` below) -- the same "every path absolute"
    discipline `klayout_tools.synthesize._write_script` itself documents for
    the `.ys` script it generates from this request.
    """
    request = {
        "sources": [str(REPO_ROOT / src) for src in SOURCES],
        "hdl_toplevel": TOP,
        "pdk": {"cell_library": CELL_LIBRARY, "corner": CORNER},
    }
    request_path.write_text(json.dumps(request, indent=2) + "\n")


def _committed_view(payload: dict) -> dict:
    """The form of `klt synthesize`'s response that belongs in the committed
    report -- see the module docstring's "Determinism" section for why
    `netlist_path`/`script_path` are restated, and adds `rtl_sources`.

    One more field is restated here that the module docstring does not cover:
    `provenance.pdk.source`, `klayout_tools.pdk.find_pdk`'s own record of
    *how* it found the PDK on this machine (a search root, an env var, an
    explicit `--pdk-root`) -- machine-local, not part of what was verified.
    `layout/verify.py`'s own `_stable()` drops the identical field from its
    committed reports for the same reason and with the same justification
    (issue #148); `provenance.pdk.name`/`.version` (which PDK, which
    open_pdks commit) stay, because those *are* what was verified against.
    """
    restated = dict(payload)
    restated["netlist_path"] = f"design/trng_top/{TOP}.synth.v"
    restated["script_path"] = None
    provenance = dict(restated.get("provenance") or {})
    pdk = provenance.get("pdk")
    if isinstance(pdk, dict):
        pdk = dict(pdk)
        pdk.pop("source", None)
        provenance["pdk"] = pdk
    restated["provenance"] = provenance
    restated["rtl_sources"] = _rtl_sources()
    return restated


def synthesize(work_dir: Path) -> tuple[dict, Path]:
    """Run `klt synthesize` with `work_dir` as the request's own directory.

    Returns `(committed-shaped report, path to the netlist klt just wrote)`.
    Raises `SynthError` for a missing tool/PDK or a failed run -- never
    partially writes anything under `work_dir` that this function's own
    return value does not already account for.
    """
    missing = _check_environment()
    if missing:
        raise SynthError("; ".join(missing))

    request_path = work_dir / "request.json"
    _write_request(request_path)

    args = ["synthesize", str(request_path)]
    pdk = resolve_pdk()
    if pdk is not None:
        args += ["--pdk", pdk.variant]

    try:
        payload = _run_klt(args, timeout_s=900)
    except FlowError as exc:
        raise SynthError(str(exc)) from exc

    netlist_path = Path(payload["netlist_path"])
    if not netlist_path.is_file():
        raise SynthError(
            f"klt synthesize reported netlist_path={netlist_path} but it "
            "does not exist"
        )

    return _committed_view(payload), netlist_path


def check() -> int:
    if not REPORT_PATH.is_file() or not NETLIST_PATH.is_file():
        print(
            f"MISSING: {NETLIST_PATH.relative_to(REPO_ROOT)} / "
            f"{REPORT_PATH.relative_to(REPO_ROOT)} -- run `python3 design/synth.py`"
        )
        return EXIT_STALE

    with tempfile.TemporaryDirectory() as tmp:
        try:
            fresh_report, fresh_netlist_path = synthesize(Path(tmp))
        except SynthError as exc:
            print(f"ERROR  {exc}", file=sys.stderr)
            return EXIT_ENVIRONMENT
        fresh_netlist = fresh_netlist_path.read_bytes()

        committed_report = json.loads(REPORT_PATH.read_text())
        committed_netlist = NETLIST_PATH.read_bytes()

        stale = False
        if committed_report != fresh_report:
            print(
                f"STALE  {REPORT_PATH.relative_to(REPO_ROOT)}: committed "
                "report does not match a fresh synthesis run"
            )
            for key in sorted(set(committed_report) | set(fresh_report)):
                if committed_report.get(key) != fresh_report.get(key):
                    print(f"       field {key!r} differs")
            stale = True
        if committed_netlist != fresh_netlist:
            print(
                f"STALE  {NETLIST_PATH.relative_to(REPO_ROOT)}: committed "
                "netlist does not match a fresh synthesis run"
            )
            stale = True

    if stale:
        print("       run `python3 design/synth.py` and commit the diff")
        return EXIT_STALE
    print(
        f"ok     {NETLIST_PATH.relative_to(REPO_ROOT)} / "
        f"{REPORT_PATH.relative_to(REPO_ROOT)} match a fresh synthesis run"
    )
    return EXIT_OK


def build() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        try:
            report, netlist_path = synthesize(Path(tmp))
        except SynthError as exc:
            print(f"ERROR  {exc}", file=sys.stderr)
            return EXIT_ENVIRONMENT

        TRNG_TOP_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(netlist_path, NETLIST_PATH)
        REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    origin = klt_origin()
    commit = (origin or {}).get("commit")
    print(f"klt:  {klt_version()}" + (f" (built from {commit})" if commit else ""))
    print(
        f"wrote  {NETLIST_PATH.relative_to(REPO_ROOT)} "
        f"({report['instance_count']} instances, {report['area_um2']} um^2)"
    )
    print(f"wrote  {REPORT_PATH.relative_to(REPO_ROOT)}")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="synth.py",
        description=(
            "Synthesize trng_top's digital wiring against gf180mcu via "
            "`klt synthesize` (or verify the committed result is fresh)."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write: re-synthesize and fail if the committed result is stale",
    )
    args = parser.parse_args(argv)
    return check() if args.check else build()


if __name__ == "__main__":
    raise SystemExit(main())
