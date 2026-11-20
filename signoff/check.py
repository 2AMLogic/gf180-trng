#!/usr/bin/env python3
"""Re-grade this block's T1 state and fail when the committed verdict has rotted.

    python3 signoff/check.py                  # verify; self-skips the re-grade if klt is absent
    python3 signoff/check.py --require-tools  # verify; fail instead of skipping (CI, check:all)
    python3 signoff/check.py --write          # rebuild the item 1/2/9/10 inventories, the item-6
                                              # digital spec projection, then signoff/records/t1-tier-report.json

`signoff/records/t1-tier-report.json` is this block's **verdict of record**
against the klayout-tools design-evidence ladder: the literal output of

    klt signoff --manifest signoff/block-manifest.json --format json

A verdict that is generated once and then never re-run is prose again within a
week, so this script exists to re-run it on every push. It fails on separable
conditions, in order, so a red build says which one:

1. **A cited envelope no longer describes the artifact it ran on.** The
   manifest's pinned `content_hash` is compared by `klt signoff` against the
   *envelope's own* `provenance.input.content_hash` -- two committed files
   agreeing with each other, which proves nothing if both came from the same
   stale run. Since klayout-tools#2196 the grader also re-hashes the artifact
   itself where it can, reporting `citation.input_verified`, but that only
   reaches a citation that both pins a hash and names a resolvable path: in
   this repo's committed report it is `true` for the `drc` citation and
   `null` for the `lvs` and `generic` ones. This step covers the whole set by
   re-hashing the actual input artifact on disk, whatever the envelope kind:

   - a `drc`/`extract` envelope names its stream in `file` and pins
     `provenance.input.content_hash`;
   - an `lvs` envelope names its stream in `layout` and records its digest as
     `environment.layout_sha256`, which is what this step re-hashes. Since
     #281 every committed LVS report here is produced by klt 0.6.0, which also
     populates `provenance.input.content_hash` (klayout-tools#1969), so the
     manifest pins it and `klt signoff`'s own staleness gate reaches it too;
     an older klt 0.4.0 envelope leaves `provenance.input` null and is still
     checkable here through `environment.layout_sha256` alone;
   - a `generic` envelope names its backing record in `source` and pins it in
     `provenance.input.content_hash`;
   - a `pex` envelope names its stream as a `{path, scope}` object in
     `layout` and pins it in `provenance.input.content_hash`. Its testbench
     side is not fingerprinted by the envelope at all; see ITEM7A_* below.

   Edit `layout/blocks/combiner_sampler/combiner_sampler.gds` or
   `sim/characterization-digital-sta-area-power.md` without re-running the
   evidence, and this fails. That is the point: a citation that cannot rot is
   a citation that proves nothing.

2. **The manifest and the envelope disagree about the pin.** A re-pin that
   touched only one of the two files would otherwise silently render the item
   `stale_evidence` instead of failing loudly.

3. **`klt signoff --manifest` could not run.** Exit 0 (every T1 item met) and
   exit 3 (ran fine, not yet T1) are both clean runs of the grader; 1 and 2
   mean a broken manifest or a tier doc this `klt` cannot parse.

4. **The committed record no longer matches a fresh run.** Either this block's
   evidence moved or the checklist did. Both are real news, and neither should
   be discoverable only by someone re-reading prose.

Before the re-grade, the designated current-status blocks of README.md and
signoff/README.md (fenced by `current-t1-status` marker comments) are compared
with the committed record's tier, met count, item count and the names of its
`unmet` T1 rows (stdlib-only, always run, fails on mismatch or a
missing/malformed block). The row names are what make the block a unique name
for the verdict: a count alone is a sum, so two rows changing in opposite
directions would leave it unmoved.

Both files this script writes -- `signoff/block-manifest.json` and
`signoff/records/t1-tier-report.json` -- must also stay byte-equal to the
canonical form it writes them in, `json.dumps(json.loads(raw), indent=2) +
"\n"`: a hand edit or a lossy re-save fails by name, with `--write` as the
remedy. That gate is stdlib-only and always runs in verify mode -- including
when `klt` is absent and the re-grade self-skips -- but not in `--write` mode,
which rewrites both files canonically. `signoff/evidence/**` is out of scope:
it has other writers (publish_*.py, klt responses) and is append-only.

T1 items 1, 2, 9 and 10 have no `klt` verb behind them, so each of the eight
(item, partition) citations is an artifact-anchored generic envelope
(klayout-tools 0.7.0) bound to an inventory in `signoff/evidence/`, built by
`signoff/inventories.py`. Step 1 also re-derives every inventory from the live
tree: an inventoried file that changed, vanished or appeared fails by name, and
`--write` is the only way to re-pin. That re-derivation proves the files still
hash to what was inventoried; it does not run the regeneration or DRC/LVS
gates the inventories name (they need the PDK, xschem or Yosys and run in
`pdk-nightly.yml`).

T1 item 6 digital instead cites the `not_applicable` form's two documents
(klayout-tools#2865): a generated projection of README.md's ratified
target-spec table and a hand-written per-row statement, pinned by content hash
inside the manifest entry. Step 1b'' holds the spec document to a fresh
projection of the table and the statement to exact row coverage -- checks that
run independently of where the grader's own scan of the same documents
stopped (on this tree it refuses at the first statistical row before ever
looking at the statement; see verify_item6_digital_publication).

Step 1 and step 2 are stdlib-only and always run -- they need no `klt`, no
PDK and no network, which is why the freshness half of this gate is on the
PR-blocking path unconditionally. Steps 3 and 4 need the grader; without it
on `PATH` they self-skip (exit 0, loudly), the same convention
`layout/verify.py` and `layout/floorplan/floorplan.py` use for a missing PDK.
`--require-tools` turns that skip into a failure, and is what CI and
`npm run check:all` pass, so a skip can never silently stand in for a pass
where it matters.

Why the grader's version is pinned
----------------------------------
`klt signoff` parses the T1 item list out of klayout-tools' own
`docs/design-evidence-tiers.md`, bundled inside the installed wheel. The tool
version therefore *is* the yardstick: klayout-tools 0.5.0 renders a ten-item
checklist and no item-11 row at all, because T1 item 11 ("Power delivery
(structural)", klayout-tools#2025) landed after that release. `KLT_GRADER_PIN` below
is a published PyPI release so a third party can reproduce the committed
record with one `pip install`, and the record itself carries `build.version`,
`build.grading_ruleset_id` and `source_doc_content_hash`, so a bump is visible
in the diff rather than inferred. Bumping the pin is a real change to the
yardstick: expect the record to move in the same commit, and re-read
signoff/README.md's per-item notes against anything the bump adds or rewords.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Appended, not prepended: this file is run by path (so `signoff/`, not the
# repository root, is on `sys.path`) and only needs the shared path loader.
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from sim.tools.pathload import load_module_from_path  # noqa: E402  (#553)

inventories = load_module_from_path("signoff_inventories", REPO_ROOT / "signoff" / "inventories.py")
MANIFEST = REPO_ROOT / "signoff" / "block-manifest.json"
RECORD = REPO_ROOT / "signoff" / "records" / "t1-tier-report.json"
EVIDENCE_DIR = REPO_ROOT / "signoff" / "evidence"

#: There is no producer pin (DR-0026, 2026-11-09 amendment): the
#: repo tracks the fleet's klayout-tools version. Each committed record names
#: the release that produced it (`provenance.klt_version`, or a publisher's
#: `producer_build`); records produced by older releases stay valid as written.
#:
#: The klayout-tools release that GRADES this block (`klt signoff`). Since
#: #653 it has been newer than the producer was: 0.7.0 is the first release that grades
#: the artifact-anchored generic envelopes for T1 items 1, 2, 9 and 10
#: (klayout-tools#2718/#2843), and moving it re-renders the verdict but does
#: not re-produce any report. sim/tools/klt_pin_sites.py holds every
#: restatement of the grader pin (see that tool's "Grader mentions") to this constant.
KLT_GRADER_PIN = "0.8.0"
#: The KLayout engine release klt is installed with (DR-0026): the engine
#: the release records it was tested against. Not checked by this script --
#: `klt signoff` does not depend on it -- but it is half of the normative
#: build, so it is defined here next to the grader pin. Every `klayout==` /
#: grader `klayout-tools==` pin restated in workflows, READMEs and docstrings is held to
#: these two constants by sim/tools/klt_pin_sites.py --check (npm run
#: check:spec); a pin bump edits them here first, then the sites it lists.
#: That tool also holds the engine every committed JSON report under
#: `layout/` *records* (`klayout_version`, and `engine_version` beside an
#: `engine: "klayout"` sibling) to KLAYOUT_PIN, so an off-pin engine cannot
#: reach `main` through a report the PDK-dependent freshness checks only
#: compare on a host that has klt and the PDK (#858).
KLAYOUT_PIN = "0.30.10"
KLT_INSTALL_HINT = f'pip install "klayout-tools=={KLT_GRADER_PIN}"'

#: `klt signoff` exit codes that mean "the grader ran fine".
#: 0 = every T1 item met; 3 = ran fine, not yet T1.
CLEAN_EXITS = (0, 3)


#: T1 item 7 (digital): the native `klt functional-verification` response of a
#: post-route, SDF-annotated gate run, published by signoff/publish_item7.py.
#: That envelope has no `provenance` block, so the manifest cannot pin it; the
#: sidecar below carries the freshness pins and verify_item7_publication()
#: re-checks them (see its docstring).
#: T1 item 11 (digital) cites the committed `klt place-and-route` response
#: unpinned. It records `provenance.input.content_hash` (role: netlist) but no
#: `file`/`layout`/`source` naming that input, and the digest matches no
#: committed file, so the generic envelope-vs-input step cannot check it. Like
#: ITEM7_ENVELOPE it is exempt from that step and carries no manifest pin.
PNR_ENVELOPE = "layout/digital/reports/place_and_route.json"
#: Item 6 analog: the native `klt yield` response of publish_item6.py. Like
#: ITEM7_ENVELOPE it carries no provenance block, so it is exempt from the
#: input-digest step and its freshness is publish_item6.publication_problems().
ITEM6_ENVELOPE = "signoff/evidence/mc-yield/klt_yield_response.json"
#: Item 6 digital: the two documents of the `not_applicable` form
#: (klayout-tools#2865, shipped in the 0.8.0 grader this repo pins; the
#: digital partition of a mixed-signal block may use it, re-ruled
#: klayout-tools#4183). `spec` is a JSON projection of README.md's ratified
#: target-spec table; `statement` is the hand-written per-row classification.
#: Both are pinned by content hash inside the manifest's
#: `evidence["6.digital"].not_applicable` -- nested, so the manifest_entries
#: loops above (which read top-level `file`/`content_hash`) do not see them;
#: verify_item6_digital_publication() is their freshness step.
ITEM6D_SPEC = "signoff/evidence/item6-digital-spec.json"
ITEM6D_STATEMENT = "signoff/evidence/item6-digital-statement.json"
#: The README heading that introduces the ratified target-spec table: the
#: single source the spec document projects.
ITEM6D_SPEC_HEADING = "## Target specification (ratified 2026-07-31)"
#: The two DR-0033 rows that ARE statistical. They are analog-partition rows
#: evidenced under `6.analog`, so the statement must classify exactly these
#: as statistical and say where they are evidenced -- and no other row may
#: claim to be, because the ratified table has exactly two statistical rows.
ITEM6D_STATISTICAL_ROWS = frozenset({"period_r1", "dtrip_v"})

ITEM7_DIR = "signoff/evidence/post-route"
ITEM7_ENVELOPE = f"{ITEM7_DIR}/gate_klt_response.json"
ITEM7_PUBLICATION = f"{ITEM7_DIR}/publication.json"
ITEM7_NETLIST = "layout/digital/trng_top.pnr.v"
ITEM7_SDF = "layout/digital/trng_top.sdf"
ITEM7_RAW_FILES = (
    "environment.json",
    "gate_comparison.json",
    "gate_klt_response.json",
    "gate_request.json",
    "gate_transcript_digest.json",
    "rtl_comparison.json",
    "rtl_klt_response.json",
    "rtl_request.json",
    "rtl_transcript_digest.json",
    "sources.json",
    "verdict.json",
)
ITEM7_LIMITS = (
    "Single corner (SDF corner typ from the ss_125C_3v00 liberty), not a PVT "
    "claim. Cell IOPATH delay only: no interconnect delay. Icarus 13.0 "
    "enforces no setup/hold/width checks and drops SDF TIMINGCHECK, so no "
    "timing violation is reported or ruled out. IOPATH arcs of ifnone-"
    "qualified edge-sensitive specify paths (xor/xnor/mux/addf/addh select/"
    "toggle) run at library default delay. Functional equivalence with the "
    "applied delays is not timing signoff; see "
    "sim/tb/trng-top-post-route/README.md. Local source files the run "
    "consumed (RTL, included headers, behavioural model, testbench and "
    "stimulus, with their local imports) are pinned by sha256; the cell "
    "library, PDK, simulator and klt versions are not source-pinned."
)


def _item7_source_problems(pub: dict) -> list[str]:
    """Freshness of the RTL/testbench/model sources the run consumed (#350)."""
    pinned = pub.get("sources")
    if not isinstance(pinned, dict) or not pinned:
        return [
            "sources: no source inventory pinned (a run that predates source "
            "pinning cannot be published; re-run run_demo.py)"
        ]
    out: list[str] = []
    for rel, sha in sorted(pinned.items()):
        path = (REPO_ROOT / rel).resolve()
        if Path(rel).is_absolute() or REPO_ROOT.resolve() not in path.parents:
            out.append(f"source {rel}: not a repository-relative path")
        elif not path.is_file():
            out.append(f"source {rel}: missing")
        elif sha256_file(path) != sha:
            out.append(
                f"source {rel}: STALE -- the run used {sha}, but it hashes to "
                f"{sha256_file(path)} today; re-run sim/tb/trng-top-post-route/"
                f"run_demo.py and re-publish"
            )
    sj = REPO_ROOT / str(pub.get("raw_dir", "")) / "sources.json"
    if sj.is_file():
        try:
            recorded = json.loads(sj.read_text()).get("files")
        except ValueError:
            recorded = None
        if recorded != pinned:
            out.append("sources: publication differs from the raw run's sources.json")
    return out


def item7_problems(pub: dict, envelope: dict) -> list[str]:
    """Every reason this publication must not be treated as current evidence."""
    out: list[str] = []
    env = envelope.get("environment") or {}
    sdf = env.get("sdf") if isinstance(env.get("sdf"), dict) else {}
    if envelope.get("status") != "pass" or envelope.get("failed_count") != 0:
        out.append("gate response is not a pass")
    if sdf.get("annotated") is not True:
        out.append("gate response is not SDF-annotated (environment.sdf.annotated)")
    # Freshness of BOTH inputs: the envelope can pin neither, so we do.
    for key, rel in (("netlist", ITEM7_NETLIST), ("sdf", ITEM7_SDF)):
        pinned = (pub.get(key) or {}).get("sha256")
        path = REPO_ROOT / rel
        if not pinned:
            out.append(f"{key}: no sha256 pinned")
        elif not path.is_file():
            out.append(f"{key}: {rel} is missing")
        elif sha256_file(path) != pinned:
            out.append(
                f"{key}: STALE -- the run used {pinned}, but {rel} hashes to "
                f"{sha256_file(path)} today; re-run sim/tb/trng-top-post-route/"
                f"run_demo.py and re-publish"
            )
    # Source inputs of both legs, as hashed by the run itself (sources.json).
    out += _item7_source_problems(pub)
    # Raw evidence: the independent comparison and annotation controls.
    raw = REPO_ROOT / str(pub.get("raw_dir", ""))
    pinned_raw = pub.get("raw_sha256") or {}
    for name in ITEM7_RAW_FILES:
        f = raw / name
        if name not in pinned_raw or not f.is_file():
            out.append(f"raw evidence {name}: missing from {pub.get('raw_dir')}")
        elif sha256_file(f) != pinned_raw[name]:
            out.append(f"raw evidence {name}: changed since publication")
    if (raw / "verdict.json").is_file():
        verdict = json.loads((raw / "verdict.json").read_text())
        if verdict.get("pass") is not True:
            out.append("verdict.json: pass is not true")
        for name, ok in sorted((verdict.get("checks") or {}).items()):
            if ok is not True:
                out.append(f"verdict.json: check {name} did not hold")
        if not verdict.get("checks"):
            out.append("verdict.json: records no checks")
    rtl = raw / "rtl_klt_response.json"
    if rtl.is_file() and json.loads(rtl.read_text()).get("status") != "pass":
        out.append("RTL reference leg is not a pass")
    pinned_env = (pub.get("envelope") or {}).get("sha256")
    env_path = REPO_ROOT / ITEM7_ENVELOPE
    if env_path.is_file() and pinned_env != sha256_file(env_path):
        out.append("published envelope differs from the sha256 in publication.json")
    if pinned_raw.get("gate_klt_response.json") != pinned_env:
        out.append("published envelope is not the raw run's gate_klt_response.json")
    return out


def verify_item7_publication(manifest: dict) -> list[str]:
    """Freshness gate for the `7.digital` citation (stdlib only, always runs).

    `klt functional-verification` responses carry no provenance block, so a
    manifest `content_hash` for one renders `unverifiable_provenance`. The
    pins live in publication.json instead, covering the post-route netlist
    and the SDF separately, and the manifest entry must not pin a hash.
    """
    entry = (manifest.get("evidence") or {}).get("7.digital")
    if entry is None:
        return []
    if not isinstance(entry, dict) or entry.get("file") != ITEM7_ENVELOPE:
        return [f"manifest 7.digital must cite {ITEM7_ENVELOPE}"]
    if entry.get("content_hash"):
        return ["manifest 7.digital pins content_hash, which the envelope cannot carry"]
    pub_path = REPO_ROOT / ITEM7_PUBLICATION
    env_path = REPO_ROOT / ITEM7_ENVELOPE
    if not pub_path.is_file() or not env_path.is_file():
        return [f"{ITEM7_ENVELOPE} / {ITEM7_PUBLICATION} not both present"]
    return item7_problems(json.loads(pub_path.read_text()), json.loads(env_path.read_text()))


#: T1 item 7 (analog): the native `klt pex` response over ring1's layout
#: (layout/rings/ro_ring11/ro_ring11.gds), published by
#: signoff/publish_item7_analog.py. Unlike the digital citation this envelope
#: does carry provenance.input.content_hash (the GDS), so the manifest pins it.
#: That pin covers the layout only: the envelope fingerprints neither its
#: testbench request, its testbench body nor its schematic DUT. The sidecar
#: below pins those, plus the extracted netlist the run wrote, and
#: verify_item7_analog_publication() re-checks them on every run.
ITEM7A_DIR = "signoff/evidence/post-layout"
ITEM7A_ENVELOPE = f"{ITEM7A_DIR}/ro_ring11.pex.json"
ITEM7A_PUBLICATION = f"{ITEM7A_DIR}/publication.json"
ITEM7A_NETLIST = f"{ITEM7A_DIR}/ro_ring11.extracted.spice"
ITEM7A_TB_DIR = "sim/tb/ro-ring11-pex"
ITEM7A_INPUTS = (
    f"{ITEM7A_TB_DIR}/request.json",
    f"{ITEM7A_TB_DIR}/tb_ro_ring11_pex.sp",
    f"{ITEM7A_TB_DIR}/ro_ring11_schematic.spice",
)
#: {tt, ff, ss} x {2.97, 3.30, 3.63} V x {-40, 27, 125} C -- DR-0006's grid.
ITEM7A_CORNERS = 27


#: Ring2 (#423): a separate, NOT-cited native comparison for the separately
#: sized oscillator, produced by `publish_item7_analog.py --ring ring2`. It
#: shares build_dut.py (one module, one ring selector) with ring1 but has its
#: own request/testbench/DUT, extracted netlist, envelope and sidecar, so its
#: freshness is judged independently of ring1's and the manifest's `7.analog`
#: citation stays ring1's.
RING2_TB_DIR = "sim/tb/ro-ring11-ring2-pex"
RING2_DIR = f"{ITEM7A_DIR}/ring2"
RING2_ENVELOPE = f"{RING2_DIR}/ro_ring11_ring2.pex.json"
RING2_PUBLICATION = f"{RING2_DIR}/publication.json"
RING2_NETLIST = f"{RING2_DIR}/ro_ring11_ring2.extracted.spice"
RING2_GDS = "layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds"
RING2_INPUTS = (
    f"{RING2_TB_DIR}/request.json",
    f"{RING2_TB_DIR}/tb_ro_ring11_ring2_pex.sp",
    f"{RING2_TB_DIR}/ro_ring11_ring2_schematic.spice",
)
RING2_PUBLICATION_SCHEMA = "gf180-trng/ring2-pex-publication/1"


def _ring_port_check(netlist: Path, ring: str = "ring1") -> str | None:
    """Re-derive the extracted netlist's ring positions with the producer's
    own build_dut.py and require they match the schematic DUT's header."""
    mod = _load_build_dut()
    r = mod.RINGS[ring]
    try:
        got = mod.extraction_port_map(netlist.read_text(), r)
        want = mod.dut_header(r.dut.read_text(), r)
    except mod.BuildError as exc:
        return str(exc)
    if got != want:
        return f"extracted ring positions {got} != schematic DUT header {want}"
    return None


def _load_build_dut():
    path = REPO_ROOT / ITEM7A_TB_DIR / "build_dut.py"
    return load_module_from_path("ro_ring11_pex_build_dut", path)


def item7_analog_dut_source_problems(pub: dict | None = None, ring: str = "ring1") -> list[str]:
    """The generated schematic DUT must be what build_dut.py renders from the
    current design source (stdlib only; no klt, ngspice or PDK).

    Scope: the consumed circuit sections (ro_ring11, ro_nand2, ro_stage and
    ring1's xr1 sizing), not the whole design file -- see build_dut.py. When
    the publication records `source_sha256` it must equal today's identity;
    publications that predate the field are not retro-fitted with one.
    """
    mod = _load_build_dut()
    r = mod.RINGS[ring]
    publisher = "signoff/publish_item7_analog.py" + ("" if ring == "ring1" else f" --ring {ring}")
    out: list[str] = []
    problem = mod.dut_source_problem(ring=r)
    if problem:
        out.append(f"schematic DUT vs source: {problem}")
    recorded = (pub or {}).get("source_sha256")
    if recorded is not None or (pub is not None and ring != "ring1"):
        try:
            current = mod.source_identity(ring=r)
        except mod.BuildError as exc:
            out.append(f"source identity: {exc}")
        else:
            if recorded != current:
                out.append(
                    f"source identity: STALE -- the publication recorded {recorded}, the "
                    f"consumed sections of design/ro_array_core.spice hash to {current} today; "
                    f"re-run {publisher}"
                )
    return out


def item7_analog_problems(pub: dict, envelope: dict, ring: str = "ring1") -> list[str]:
    """Every reason the ring's native-pex publication must not be treated as
    current (ring1: the 7.analog citation; ring2: the uncited #423 coverage)."""
    if ring == "ring1":
        files = dict(netlist=ITEM7A_NETLIST, inputs=ITEM7A_INPUTS, envelope=ITEM7A_ENVELOPE,
                     gds=None, publisher="signoff/publish_item7_analog.py")
    else:
        files = dict(netlist=RING2_NETLIST, inputs=RING2_INPUTS, envelope=RING2_ENVELOPE,
                     gds=RING2_GDS, publisher=f"signoff/publish_item7_analog.py --ring {ring}")
    out: list[str] = item7_analog_dut_source_problems(pub, ring)
    if ring != "ring1":
        if pub.get("schema") != RING2_PUBLICATION_SCHEMA:
            out.append(f"publication schema is {pub.get('schema')!r}, not {RING2_PUBLICATION_SCHEMA!r}")
        layout = envelope.get("layout") or {}
        if layout.get("path") != files["gds"]:
            out.append(f"envelope layout is {layout.get('path')!r}, not {files['gds']}")
        gds = REPO_ROOT / files["gds"]
        if not gds.is_file() or sha256_file(gds) != pinned_input_hash(envelope):
            out.append(f"{files['gds']} is not the layout this klt pex run extracted (re-run and re-publish)")
        if pub.get("layout_content_hash") != pinned_input_hash(envelope):
            out.append("publication layout_content_hash differs from the envelope's")
    strict = ring == "ring1"  # the cited run must be complete; ring2 states its verdict
    if strict and envelope.get("status") != "pass":
        out.append(f"klt pex status is {envelope.get('status')!r}, not 'pass'")
    # The 0.6.0 release predates `measurement` (klayout-tools#2478); absent
    # means testbench mode. A caller-measured run is not what this cites.
    if (envelope.get("measurement") or {}).get("mode", "testbench") != "testbench":
        out.append("klt pex measurement.mode is not 'testbench'")
    for key in ("pin_count_mismatch", "flat_dut_mismatch"):
        if envelope.get(key) is not None:
            out.append(f"klt pex reports {key}")
    if strict:
        if envelope.get("corner_count") != ITEM7A_CORNERS:
            out.append(f"corner_count is {envelope.get('corner_count')}, not {ITEM7A_CORNERS}")
        names = [n for tb in envelope.get("testbenches") or [] for n in tb.get("measurement_names") or []]
        delta = envelope.get("delta") or []
        if not names or len(delta) != ITEM7A_CORNERS * len(names):
            out.append(f"delta has {len(delta)} rows, expected {ITEM7A_CORNERS} x {len(names)}")
        for row in delta:
            if row.get("status") != "pass" or row.get("schematic_value") is None or row.get("extracted_value") is None:
                out.append(f"delta row {row.get('corner_id')}/{row.get('spec_row')} is not a two-sided pass")
    else:
        # Not a citation: an incomplete or failing run is still current evidence
        # of that result, provided the recorded verdict is exactly what the
        # envelope and request yield today (every declared corner/row accounted).
        out += ring2_request_problems()
        req = REPO_ROOT / RING2_INPUTS[0]
        if req.is_file():
            verdict = combiner_sampler_verdict(envelope, json.loads(req.read_text()))
            if pub.get("verdict") != verdict:
                out.append("recorded verdict is not what the envelope and request yield today")
            out += [f"verdict: {p}" for p in verdict["consistency_problems"]]
    bias = envelope.get("body_bias")
    if not isinstance(bias, dict) or "status" not in bias:
        out.append("envelope carries no body_bias block")
    elif pub.get("body_bias_status") != bias["status"]:
        out.append(
            f"publication.json states body_bias_status {pub.get('body_bias_status')!r}, "
            f"the envelope says {bias['status']!r}"
        )
    netlist = REPO_ROOT / files["netlist"]
    if not netlist.is_file():
        out.append(f"{files['netlist']} is missing")
    else:
        recorded = (envelope.get("extraction") or {}).get("netlist_sha256")
        if sha256_file(netlist) != f"sha256:{recorded}":
            out.append(f"{files['netlist']} is not the netlist this klt pex run extracted")
        problem = _ring_port_check(netlist, ring)
        if problem:
            out.append(f"ring port positions: {problem}")
    pinned = pub.get("inputs_sha256") or {}
    for rel in files["inputs"]:
        path = REPO_ROOT / rel
        if rel not in pinned or not path.is_file():
            out.append(f"input {rel}: not pinned or missing")
        elif sha256_file(path) != pinned[rel]:
            out.append(
                f"input {rel}: STALE -- the run used {pinned[rel]}, it hashes to "
                f"{sha256_file(path)} today; re-run {files['publisher']}"
            )
    env_path = REPO_ROOT / files["envelope"]
    if env_path.is_file() and (pub.get("envelope") or {}).get("sha256") != sha256_file(env_path):
        out.append("published envelope differs from the sha256 in publication.json")
    return out


def ring2_request_problems() -> list[str]:
    """The ring2 request must declare the same 27-point grid and the same
    measurements as ring1's, and point at ring2's own testbench (stdlib only)."""
    out: list[str] = []
    try:
        r1 = json.loads((REPO_ROOT / ITEM7A_INPUTS[0]).read_text())
        r2 = json.loads((REPO_ROOT / RING2_INPUTS[0]).read_text())
    except (OSError, ValueError) as exc:
        return [f"ring2 request: {exc}"]
    if len(request_corner_ids(r2)) != ITEM7A_CORNERS:
        out.append(f"ring2 request declares {len(request_corner_ids(r2))} corners, not {ITEM7A_CORNERS}")
    strip = lambda r: {k: v for k, v in r.items() if k != "netlist"}  # noqa: E731
    if strip(r1) != strip(r2):
        out.append("ring2 request differs from ring1's beyond its testbench name "
                   "(the pair must share the grid, analysis and measurements)")
    if r2.get("netlist") != Path(RING2_INPUTS[1]).name:
        out.append(f"ring2 request names testbench {r2.get('netlist')!r}, not {Path(RING2_INPUTS[1]).name!r}")
    return out


def verify_ring2_pex_publication(manifest: dict | None = None) -> list[str]:
    """Freshness gate for the ring2 comparison, independent of ring1 and the
    manifest. The fixture (DUT vs source, request, testbench xdut line) is
    always held; the publication only once committed -- an unrun fixture is a
    valid state, a half-committed publication is not."""
    out = [f"fixture: {p}" for p in item7_analog_dut_source_problems(None, "ring2")]
    for key, entry in ((manifest or {}).get("evidence") or {}).items():
        if isinstance(entry, dict) and str(entry.get("file", "")).startswith(RING2_DIR):
            out.append(f"manifest {key} cites ring2 evidence; ring2 is not part of any citation "
                       f"without a separately reviewed change")
    out += [f"fixture: {p}" for p in ring2_request_problems()]
    mod = _load_build_dut()
    try:
        mod.check_testbench(mod.dut_header(mod.RING2.dut.read_text(), mod.RING2), mod.RING2)
    except (mod.BuildError, OSError) as exc:
        out.append(f"fixture: {exc}")
    pub_path, env_path = REPO_ROOT / RING2_PUBLICATION, REPO_ROOT / RING2_ENVELOPE
    if not pub_path.is_file() and not env_path.is_file():
        return out
    if not pub_path.is_file() or not env_path.is_file():
        return out + [f"{RING2_ENVELOPE} / {RING2_PUBLICATION} not both present"]
    return out + item7_analog_problems(
        json.loads(pub_path.read_text()), json.loads(env_path.read_text()), "ring2"
    )


def verify_item7_analog_publication(manifest: dict) -> list[str]:
    """Freshness gate for the `7.analog` citation (stdlib only, always runs)."""
    entry = (manifest.get("evidence") or {}).get("7.analog")
    if entry is None:
        return []
    if not isinstance(entry, dict) or entry.get("file") != ITEM7A_ENVELOPE:
        return [f"manifest 7.analog must cite {ITEM7A_ENVELOPE}"]
    if not entry.get("content_hash"):
        return ["manifest 7.analog must pin the envelope's provenance.input.content_hash"]
    pub_path = REPO_ROOT / ITEM7A_PUBLICATION
    env_path = REPO_ROOT / ITEM7A_ENVELOPE
    if not pub_path.is_file() or not env_path.is_file():
        return [f"{ITEM7A_ENVELOPE} / {ITEM7A_PUBLICATION} not both present"]
    return item7_analog_problems(
        json.loads(pub_path.read_text()), json.loads(env_path.read_text())
    )


#: Additional post-layout coverage, NOT a manifest citation (#418): the native
#: `klt pex` response over the assembled combiner/sampler block
#: (layout/blocks/combiner_sampler/combiner_sampler.gds) under a deterministic
#: clock/reset/two-input schedule, published by
#: signoff/publish_combiner_sampler_pex.py. The 7.analog citation above stays
#: ring1's; this sidecar is held to the same freshness discipline so its
#: committed artifacts cannot silently rot, and its recorded verdict is
#: recomputed from the envelope so it cannot be hand-edited into a pass.
CS_TB_DIR = "sim/tb/combiner-sampler-pex"
CS_DIR = f"{ITEM7A_DIR}/combiner_sampler"
CS_ENVELOPE = f"{CS_DIR}/combiner_sampler.pex.json"
CS_PUBLICATION = f"{CS_DIR}/publication.json"
CS_NETLIST = f"{CS_DIR}/combiner_sampler.extracted.spice"
CS_GDS = "layout/blocks/combiner_sampler/combiner_sampler.gds"
CS_REQUEST = f"{CS_TB_DIR}/request.json"
CS_INPUTS = (
    CS_REQUEST,
    f"{CS_TB_DIR}/tb_combiner_sampler_pex.sp",
    f"{CS_TB_DIR}/combiner_sampler_schematic.spice",
)
CS_PUBLICATION_SCHEMA = "gf180-trng/combiner-sampler-pex-publication/1"


def _load_tb_module(tb_dir: str, name: str):
    path = REPO_ROOT / tb_dir / f"{name}.py"
    return load_module_from_path(f"{Path(tb_dir).name.replace('-', '_')}_{name}", path)


def request_corner_ids(request: dict) -> list[str]:
    """`klt sim`'s corner ids (`tt/2.970V/-40C`) for every corner a request declares."""
    corners = request.get("corners") or {}
    supplies = [v for vs in (corners.get("supply_v") or {}).values() for v in vs]
    return [
        f"{p['name']}/{v:.3f}V/{t:g}C"
        for p in corners.get("process") or []
        for v in supplies
        for t in corners.get("temperature_c") or []
    ]


def _within(value: float, limits: dict) -> bool:
    lo, hi = limits.get("min"), limits.get("max")
    return (lo is None or value >= lo) and (hi is None or value <= hi)


def combiner_sampler_verdict(envelope: dict, request: dict) -> dict:
    """Classify every declared (corner, measurement) of the combiner/sampler run.

    `klt pex` grades only the extracted side's limits (a delta row's `status`
    is the extracted measurement's own); the schematic value is reported,
    never graded. Both sides are held to the request's limits here. A row is

    * `pass` -- measured on both sides, both inside the limits;
    * `fail` -- measured on both sides, at least one side outside them (the
      failing side(s) are named);
    * `measured` -- an informational row (no limits), measured on both sides;
    * `unmeasured` -- missing from the response, missing a value on either
      side, or errored. Never a pass.

    The overall verdict is `incomplete` if any declared row is unmeasured,
    else `fail` if any row fails, else `pass`.
    """
    specs = {m["name"]: m.get("limits") or None for m in request.get("measurements") or []}
    corners = request_corner_ids(request)
    rows = {}
    for r in envelope.get("delta") or []:
        rows.setdefault((r.get("corner_id"), r.get("spec_row")), r)
    counts = {"pass": 0, "fail": 0, "measured": 0, "unmeasured": 0}
    failures: list[dict] = []
    unmeasured: list[str] = []
    problems: list[str] = []
    for corner in corners:
        for name, limits in specs.items():
            row = rows.get((corner, name))
            sv = None if row is None else row.get("schematic_value")
            ev = None if row is None else row.get("extracted_value")
            if row is None or row.get("status") == "error" or not isinstance(sv, (int, float)) \
                    or not isinstance(ev, (int, float)):
                counts["unmeasured"] += 1
                unmeasured.append(f"{corner}/{name}")
                continue
            if not limits:
                counts["measured"] += 1
                continue
            bad = [side for side, v in (("schematic", sv), ("extracted", ev)) if not _within(v, limits)]
            if ("extracted" in bad) != (row.get("status") == "fail"):
                problems.append(
                    f"{corner}/{name}: klt pex status {row.get('status')!r} disagrees with the "
                    f"request's limits on the extracted value {ev!r}"
                )
            if bad:
                counts["fail"] += 1
                failures.append({"corner_id": corner, "row": name, "sides": bad,
                                 "schematic_value": sv, "extracted_value": ev, "limits": limits})
            else:
                counts["pass"] += 1
    extra = sorted({c for c, _n in rows} - set(corners))
    if extra:
        problems.append(f"response carries undeclared corners: {extra}")
    verdict = "incomplete" if counts["unmeasured"] else ("fail" if counts["fail"] else "pass")
    return {
        "verdict": verdict,
        "declared_corners": len(corners),
        "declared_rows_per_corner": len(specs),
        "limited_rows_per_corner": sum(1 for v in specs.values() if v),
        "counts": counts,
        "failures": failures,
        "unmeasured": unmeasured,
        "consistency_problems": problems,
    }


def combiner_sampler_dut_source_problems(pub: dict | None = None) -> list[str]:
    """The generated DUT and testbench must be current with their sources
    (stdlib only; no klt, ngspice or PDK)."""
    out: list[str] = []
    bd = _load_tb_module(CS_TB_DIR, "build_dut")
    problem = bd.dut_source_problem()
    if problem:
        out.append(f"schematic DUT vs source: {problem}")
    st = _load_tb_module(CS_TB_DIR, "stimulus")
    for path, want in ((st.TESTBENCH, st.render_testbench()), (st.REQUEST, st.render_request_text())):
        if not path.is_file() or path.read_text() != want:
            out.append(
                f"{path.relative_to(REPO_ROOT)} is not what {CS_TB_DIR}/stimulus.py renders; "
                f"re-run stimulus.py"
            )
    recorded = (pub or {}).get("source_sha256")
    if pub is not None:
        try:
            current = bd.source_identity()
        except bd.BuildError as exc:
            out.append(f"source identity: {exc}")
        else:
            if recorded != current:
                out.append(
                    f"source identity: STALE -- the publication recorded {recorded}, the consumed "
                    f"design sections hash to {current} today; re-run "
                    f"signoff/publish_combiner_sampler_pex.py"
                )
    return out


def combiner_sampler_problems(pub: dict, envelope: dict) -> list[str]:
    """Every reason the combiner/sampler publication is not current evidence.

    Freshness, not success: a run whose verdict is `fail` or `incomplete` is
    still current evidence of that result. What is checked is that every
    committed artifact is the one the run used, that the recorded verdict is
    exactly what the envelope and request yield today, and that the
    extracted netlist's ports re-derive to the DUT header.
    """
    out = combiner_sampler_dut_source_problems(pub)
    if pub.get("schema") != CS_PUBLICATION_SCHEMA:
        out.append(f"publication schema is {pub.get('schema')!r}, not {CS_PUBLICATION_SCHEMA!r}")
    if (envelope.get("measurement") or {}).get("mode", "testbench") != "testbench":
        out.append("klt pex measurement.mode is not 'testbench'")
    for key in ("pin_count_mismatch", "flat_dut_mismatch"):
        if envelope.get(key) is not None:
            out.append(f"klt pex reports {key}")
    layout = envelope.get("layout") or {}
    if layout.get("path") != CS_GDS:
        out.append(f"envelope layout is {layout.get('path')!r}, not {CS_GDS}")
    gds = REPO_ROOT / CS_GDS
    if not gds.is_file() or sha256_file(gds) != pinned_input_hash(envelope):
        out.append(f"{CS_GDS} is not the layout this klt pex run extracted (re-run and re-publish)")
    if pub.get("layout_content_hash") != pinned_input_hash(envelope):
        out.append("publication layout_content_hash differs from the envelope's")
    bias = envelope.get("body_bias")
    if not isinstance(bias, dict) or "status" not in bias:
        out.append("envelope carries no body_bias block")
    elif pub.get("body_bias_status") != bias["status"]:
        out.append(
            f"publication.json states body_bias_status {pub.get('body_bias_status')!r}, "
            f"the envelope says {bias['status']!r}"
        )
    netlist = REPO_ROOT / CS_NETLIST
    if not netlist.is_file():
        out.append(f"{CS_NETLIST} is missing")
    else:
        recorded = (envelope.get("extraction") or {}).get("netlist_sha256")
        if sha256_file(netlist) != f"sha256:{recorded}":
            out.append(f"{CS_NETLIST} is not the netlist this klt pex run extracted")
        bd = _load_tb_module(CS_TB_DIR, "build_dut")
        try:
            dut_text = bd.DUT.read_text()
            got = bd.extraction_port_map(netlist.read_text(), dut_text)
            want = bd.dut_header(dut_text)
        except (bd.BuildError, OSError) as exc:
            out.append(f"port map: {exc}")
        else:
            if got != want:
                out.append(f"port map: extracted ports resolve to {got}, DUT header is {want}")
            header = bd.extracted_graph(netlist.read_text())[1]
            if pub.get("port_map") != dict(zip(header, got)):
                out.append("publication port_map differs from the one the committed netlist yields")
    pinned = pub.get("inputs_sha256") or {}
    for rel in CS_INPUTS:
        path = REPO_ROOT / rel
        if rel not in pinned or not path.is_file():
            out.append(f"input {rel}: not pinned or missing")
        elif sha256_file(path) != pinned[rel]:
            out.append(
                f"input {rel}: STALE -- the run used {pinned[rel]}, it hashes to "
                f"{sha256_file(path)} today; re-run signoff/publish_combiner_sampler_pex.py"
            )
    req_path = REPO_ROOT / CS_REQUEST
    if req_path.is_file():
        verdict = combiner_sampler_verdict(envelope, json.loads(req_path.read_text()))
        if pub.get("verdict") != verdict:
            out.append("recorded verdict is not what the envelope and request yield today")
        for p in verdict["consistency_problems"]:
            out.append(f"verdict: {p}")
    env_path = REPO_ROOT / CS_ENVELOPE
    if not env_path.is_file() or (pub.get("envelope") or {}).get("sha256") != sha256_file(env_path):
        out.append("published envelope differs from the sha256 in publication.json")
    return out


def verify_combiner_sampler_publication() -> list[str]:
    """Freshness gate for the combiner/sampler coverage (stdlib only, always
    runs once the publication is committed)."""
    pub_path = REPO_ROOT / CS_PUBLICATION
    env_path = REPO_ROOT / CS_ENVELOPE
    if not pub_path.is_file() and not env_path.is_file():
        return []
    if not pub_path.is_file() or not env_path.is_file():
        return [f"{CS_ENVELOPE} / {CS_PUBLICATION} not both present"]
    return combiner_sampler_problems(
        json.loads(pub_path.read_text()), json.loads(env_path.read_text())
    )


def project_item6_digital_spec(readme_text: str) -> dict:
    """Deterministic JSON projection of README.md's ratified target-spec
    table -- the `spec` document of the item-6 digital `not_applicable` form.

    This projection exists only because the 0.8.0 grader pin has no
    markdown-table spec source (klayout-tools#4793, 0.9.2): it carries every
    ratified row's four cells verbatim, so the rendering stays honest, and
    nothing else. When the grader pin moves to a release with the native
    source, retire this document for the grader's own markdown-table input.

    Row ids: the trailing backticked identifier when the parameter cell
    carries one (the DR-0033 style "Ring period under mismatch
    (`period_r1`)"), else a slug of the parameter text. Raises ValueError on
    a table this parser cannot read whole -- a partial projection would be
    worse than none.
    """
    lines = readme_text.splitlines()
    try:
        start = lines.index(ITEM6D_SPEC_HEADING)
    except ValueError:
        raise ValueError(f"README.md carries no {ITEM6D_SPEC_HEADING!r} heading") from None
    rows: list[dict] = []
    seen_table = False
    for line in lines[start + 1:]:
        stripped = line.strip()
        if not stripped:
            if seen_table:
                break
            continue
        if not stripped.startswith("|"):
            if seen_table:
                break
            continue
        seen_table = True
        cells = [c.strip() for c in stripped[1:-1].split("|")] if stripped.endswith("|") else []
        if len(cells) != 4:
            raise ValueError(
                f"target-spec table row does not have exactly four cells: {stripped[:60]!r}"
            )
        if all(set(c) <= set("-: ") and c for c in cells):
            continue  # the header/separator rule of the markdown table
        if [c.lower() for c in cells] == ["parameter", "target", "stretch", "status"]:
            continue  # the header row
        parameter, target, stretch, status = cells
        backticked = re.findall(r"`([a-z][a-z0-9_]+)`", parameter)
        row_id = backticked[-1] if backticked else re.sub(
            r"[^a-z0-9]+", "_", parameter.lower()
        ).strip("_")
        if not row_id:
            raise ValueError(f"target-spec row has no derivable id: {parameter!r}")
        rows.append(
            {
                "id": row_id,
                "parameter": parameter,
                "target": target,
                "stretch": stretch,
                "status": status,
            }
        )
    if not rows:
        raise ValueError("no data rows found under the target-spec heading")
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError(f"target-spec rows project duplicate ids: {sorted(ids)}")
    return {"status": "ratified", "rows": rows}


def _item6d_doc_problems(label: str, path: Path, pinned: str | None) -> list[str]:
    """Hash-bind one `not_applicable` document to its bytes on disk."""
    if not path.is_file():
        return [f"{label}: {path.relative_to(REPO_ROOT)} is missing"]
    actual = sha256_file(path)
    if pinned != actual:
        return [
            f"{label}: STALE -- the manifest pins {pinned!r}, "
            f"{path.relative_to(REPO_ROOT)} hashes to {actual} today; re-run "
            f"'python3 signoff/check.py --write' to re-pin"
        ]
    return []


def verify_item6_digital_publication(manifest: dict) -> list[str]:
    """Freshness gate for the `6.digital` `not_applicable` citation (stdlib
    only, always runs once the entry is cited).

    The grader hash-checks both documents and scans them itself, but it
    stops at the first refusal: on this tree the spec scan refuses at the
    first DR-0033 row (`not_applicable_statistical_row`, the recorded
    outcome), which returns before the statement's coverage is ever looked
    at. So this step re-checks, independently of the grader and of where
    the grader stopped: both document hashes against file bytes, the spec
    document against a fresh projection of README's ratified table (so it
    cannot drift from the table it renders), and the statement's rows --
    one entry per ratified row, id for id, each with a nonempty class and
    reason, the two statistical rows classified as statistical and pointing
    at the `6.analog` citation that evidences them, and no other row
    claiming to be statistical.
    """
    entry = (manifest.get("evidence") or {}).get("6.digital")
    if entry is None:
        return []
    form = entry.get("not_applicable") if isinstance(entry, dict) else None
    if not isinstance(form, dict):
        return ["manifest 6.digital must be a 'not_applicable' object citing the "
                "spec and statement documents"]
    out: list[str] = []
    refs: dict[str, dict] = {}
    for label, want in (("spec", ITEM6D_SPEC), ("statement", ITEM6D_STATEMENT)):
        ref = form.get(label)
        if not isinstance(ref, dict) or ref.get("file") != want:
            out.append(f"manifest 6.digital not_applicable.{label} must cite {want}")
        else:
            refs[label] = ref
            out += _item6d_doc_problems(label, REPO_ROOT / want, ref.get("content_hash"))
    try:
        readme = (REPO_ROOT / "README.md").read_text()
    except OSError as exc:
        return out + [f"README.md: unreadable ({exc})"]
    try:
        projection = project_item6_digital_spec(readme)
    except ValueError as exc:
        return out + [f"README.md target-spec table: {exc}"]
    ids = [row["id"] for row in projection["rows"]]
    if "spec" in refs and (REPO_ROOT / ITEM6D_SPEC).is_file():
        try:
            committed = json.loads((REPO_ROOT / ITEM6D_SPEC).read_text())
        except (OSError, ValueError) as exc:
            out.append(f"spec: {ITEM6D_SPEC} is unreadable ({exc})")
        else:
            if committed != projection:
                out.append(
                    "spec: the committed document is not the current projection of "
                    "README.md's ratified target-spec table; regenerate it with "
                    "'python3 signoff/check.py --write'"
                )
    statement_rows: list[dict] = []
    if "statement" in refs and (REPO_ROOT / ITEM6D_STATEMENT).is_file():
        try:
            doc = json.loads((REPO_ROOT / ITEM6D_STATEMENT).read_text())
            statement_rows = doc.get("rows") if isinstance(doc, dict) else None
        except (OSError, ValueError) as exc:
            out.append(f"statement: {ITEM6D_STATEMENT} is unreadable ({exc})")
            statement_rows = []
        if statement_rows is None or not all(
            isinstance(row, dict)
            and all(isinstance(row.get(k), str) and row[k].strip() for k in ("id", "class", "reason"))
            for row in statement_rows
        ):
            out.append("statement: 'rows' must be a list of objects each with a "
                       "nonempty string id, class and reason")
            statement_rows = []
    if statement_rows:
        statement_ids = [row["id"] for row in statement_rows]
        uncovered = [rid for rid in ids if rid not in statement_ids]
        unknown = [rid for rid in statement_ids if rid not in ids]
        if uncovered or unknown or len(set(statement_ids)) != len(statement_ids):
            out.append(
                f"statement: does not account for exactly the ratified rows "
                f"(uncovered: {uncovered}, unknown: {unknown}, duplicated: "
                f"{sorted({r for r in statement_ids if statement_ids.count(r) > 1})})"
            )
        for row in statement_rows:
            is_statistical = row["id"] in ITEM6D_STATISTICAL_ROWS
            claims = row["class"].strip().lower() == "statistical"
            if is_statistical and not claims:
                out.append(
                    f"statement: row {row['id']} is one of the two DR-0033 statistical "
                    f"rows but is classified {row['class']!r}"
                )
            if is_statistical and "6.analog" not in row["reason"]:
                out.append(
                    f"statement: row {row['id']} is statistical and must say it is "
                    f"evidenced under 6.analog (analog partition)"
                )
            if claims and not is_statistical:
                out.append(
                    f"statement: row {row['id']} claims to be statistical, but the "
                    f"ratified table's only statistical rows are "
                    f"{sorted(ITEM6D_STATISTICAL_ROWS)}"
                )
    return out


sha256_file = inventories.sha256_file


def pinned_input_hash(envelope: dict) -> str | None:
    return ((envelope.get("provenance") or {}).get("input") or {}).get("content_hash")


def resolve_artifact(envelope_path: Path, named: str) -> Path | None:
    """Resolve an input-artifact path an envelope names.

    `klt drc`/`klt extract` write `file` relative to the repo root they ran
    from; `klt lvs` writes `layout` relative to the report's own directory.
    Both shapes are committed here, so try both and take whichever exists.
    """
    for candidate in (REPO_ROOT / named, envelope_path.parent / named):
        if candidate.is_file():
            return candidate
    return None


#: (field naming the input artifact, field carrying its digest) -- the one
#: definition of what makes a JSON file an envelope, shared by
#: check_envelope_against_its_input() and envelope_names_an_input().
ENVELOPE_INPUT_KINDS = [
    ("file", "provenance.input.content_hash"),
    ("layout", "environment.layout_sha256"),
    ("source", "provenance.input.content_hash"),
    # `klt sta` (schema 2) names its DEF as a `{path, scope}` object.
    ("def_path", "provenance.input.content_hash"),
]


def check_envelope_against_its_input(
    envelope_path: Path, envelope: dict, failures: list[str]
) -> bool:
    """True when this envelope's recorded input digest matches disk today.

    Returns False when the envelope names no checkable input at all, so the
    caller can count what was actually verified rather than what was seen.
    """
    rel = envelope_path.relative_to(REPO_ROOT)
    for name_field, digest_field in ENVELOPE_INPUT_KINDS:
        named = envelope.get(name_field)
        if isinstance(named, dict):
            # `klt pex` (schema 2) writes `layout` (and `klt sta` its
            # `def_path`) as a `{path, scope}` object and pins the file it read
            # in provenance.input.content_hash.
            named = named.get("path") if named.get("scope") == "repo" else None
            digest_field = "provenance.input.content_hash"
        if not isinstance(named, str) or not named:
            continue

        if digest_field == "environment.layout_sha256":
            raw = (envelope.get("environment") or {}).get("layout_sha256")
            recorded = f"sha256:{raw}" if raw else None
        else:
            recorded = pinned_input_hash(envelope)

        if not recorded:
            failures.append(
                f"{rel}: names its input as {name_field}={named!r} but records no "
                f"{digest_field} -- an unrecorded input digest cannot be "
                f"verified fresh against anything"
            )
            return False

        artifact = resolve_artifact(envelope_path, named)
        if artifact is None:
            failures.append(
                f"{rel}: names input {named!r}, which does not exist in this tree"
            )
            return False

        actual = sha256_file(artifact)
        if actual != recorded:
            failures.append(
                f"{rel}: records {digest_field}={recorded} for {named!r}, but "
                f"{artifact.relative_to(REPO_ROOT)} hashes to {actual} today -- "
                f"the cited evidence describes a different revision of its own "
                f"input than the one committed here. Re-run the check that "
                f"produced this envelope."
            )
            return False
        return True

    failures.append(
        f"{rel}: names no input artifact (no 'file', 'layout' or 'source' "
        f"field), so its freshness cannot be verified"
    )
    return False


def envelope_names_an_input(envelope: dict) -> bool:
    """True when this JSON names an input artifact, i.e. it is an envelope.

    The same naming rule check_envelope_against_its_input() verifies, so the
    step-1 sweep selector and the checker can never disagree about what an
    envelope is: a `file`, `source`, `layout` or `def_path` field carrying a
    non-empty path, directly or as a `{path, scope: "repo"}` object.
    """
    if not isinstance(envelope, dict):
        return False
    for name_field, _digest_field in ENVELOPE_INPUT_KINDS:
        named = envelope.get(name_field)
        if isinstance(named, dict):
            named = named.get("path") if named.get("scope") == "repo" else None
        if isinstance(named, str) and named:
            return True
    return False


def manifest_entries(manifest: dict):
    """Yield (item key, entry dict) for every object-shaped evidence entry."""
    for key, entry in sorted((manifest.get("evidence") or {}).items()):
        parts = entry if isinstance(entry, list) else [entry]
        for part in parts:
            if isinstance(part, dict):
                yield key, part


#: Documents that restate the current T1 verdict. Each must carry exactly one
#: block fenced by the marker comments below; only that block is read, so
#: historical narrative elsewhere in the same file is never treated as a
#: current claim.
CURRENT_STATUS_DOCS = ("README.md", "signoff/README.md")
CURRENT_STATUS_BEGIN = "<!-- current-t1-status:begin -->"
CURRENT_STATUS_END = "<!-- current-t1-status:end -->"
_STATUS_TIER = re.compile(r"`tier:\s*(null|T\d+)`")
_STATUS_COUNT = re.compile(r"T1\s+(\d+)\s+of\s+(\d+)\s+items\s+met")
#: The unmet-row composition: the literal `none`, or a comma-separated list of
#: backticked `<item>.<partition>` row names (a row the report grades without a
#: partition is named by its item number alone).
_STATUS_ROW_RE = r"`\d+(?:\.[a-z]+)?`"
_STATUS_UNMET = re.compile(
    rf"unmet:\s*(none|{_STATUS_ROW_RE}(?:\s*,\s*{_STATUS_ROW_RE})*)", re.IGNORECASE
)
_STATUS_ROW = re.compile(r"`(\d+(?:\.[a-z]+)?)`", re.IGNORECASE)


def t1_unmet_rows(report: dict) -> list[str] | None:
    """Names of every T1 row the report does not grade `met`, (item, partition)-sorted.

    ``None`` means the report carries no readable ``items`` array, which is
    itself a problem: a record that cannot name its own composition is exactly
    the blind spot the composition clause exists to close.

    Only ``tier == "T1"`` entries are rows. The record also carries one
    summary entry per higher tier (T2/T3/T4) with ``id`` and ``partition``
    null and ``status`` ``unmet``; counting those would invent rows that no
    checklist has.
    """
    items = report.get("items")
    if not isinstance(items, list):
        return None
    rows: list[tuple[int, str, str]] = []
    for entry in items:
        if not isinstance(entry, dict) or entry.get("tier") != "T1":
            continue
        if entry.get("status") == "met":
            continue
        ident, partition = entry.get("id"), entry.get("partition")
        name = f"{ident}.{partition}" if partition else f"{ident}"
        rows.append((ident if isinstance(ident, int) else -1, partition or "", name))
    return [name for _, _, name in sorted(rows)]


def format_unmet_rows(rows: list[str]) -> str:
    """Render row names as the composition clause's block text."""
    return ", ".join(f"`{name}`" for name in rows) if rows else "none"


def current_status_problems(report: dict, docs: dict[str, str]) -> list[str]:
    """Compare designated current-status text with the committed report.

    ``docs`` maps a display name to document text. The expected numerator,
    denominator, tier and unmet-row names come from ``report`` (never
    hard-coded). A document with no block, more than one block, or a block
    lacking a parseable tier, count or unmet clause is a problem, as is any
    disagreement.

    The unmet clause must list the rows in the canonical order
    `format_unmet_rows` renders, so one graded state has exactly one valid
    block text.
    """
    want_tier = report.get("tier")
    want_met = report.get("t1_met_count")
    want_total = report.get("t1_item_count")
    want_unmet = t1_unmet_rows(report)
    problems: list[str] = []
    if want_unmet is None:
        problems.append(
            "the report carries no readable items[] array, so no document's "
            "unmet-row composition can be verified"
        )
    for name, text in docs.items():
        begins = text.count(CURRENT_STATUS_BEGIN)
        ends = text.count(CURRENT_STATUS_END)
        if begins != 1 or ends != 1:
            problems.append(
                f"{name}: expected exactly one {CURRENT_STATUS_BEGIN} ... "
                f"{CURRENT_STATUS_END} block, found {begins} begin / {ends} end"
            )
            continue
        head, _, rest = text.partition(CURRENT_STATUS_BEGIN)
        block, _, _ = rest.partition(CURRENT_STATUS_END)
        tier_m = _STATUS_TIER.findall(block)
        count_m = _STATUS_COUNT.findall(block)
        unmet_m = _STATUS_UNMET.findall(block)
        if len(tier_m) != 1 or len(count_m) != 1 or len(unmet_m) != 1:
            problems.append(
                f"{name}: current-status block must state one "
                f"`tier: <null|Tn>`, one 'T1 N of M items met' and one "
                f"'unmet: <row names|none>'"
            )
            continue
        got_tier = None if tier_m[0] == "null" else tier_m[0]
        got_met, got_total = int(count_m[0][0]), int(count_m[0][1])
        got_unmet = (
            [] if unmet_m[0].lower() == "none" else _STATUS_ROW.findall(unmet_m[0])
        )
        if got_tier != want_tier:
            problems.append(f"{name}: tier states {got_tier!r}, report says {want_tier!r}")
        if got_met != want_met:
            problems.append(f"{name}: states {got_met} items met, report says {want_met}")
        if got_total != want_total:
            problems.append(f"{name}: states {got_total} T1 items, report says {want_total}")
        if want_unmet is not None and got_unmet != want_unmet:
            problems.append(
                f"{name}: states unmet rows {format_unmet_rows(got_unmet)}, "
                f"report says {format_unmet_rows(want_unmet)}"
            )
    return problems


def verify_current_status() -> list[str]:
    """Read-only, offline: committed report vs the designated README text."""
    try:
        report = json.loads(RECORD.read_text())
    except (OSError, ValueError) as exc:
        return [f"{RECORD.relative_to(REPO_ROOT)}: unreadable ({exc})"]
    docs = {}
    for name in CURRENT_STATUS_DOCS:
        try:
            docs[name] = (REPO_ROOT / name).read_text()
        except OSError as exc:
            return [f"{name}: unreadable ({exc})"]
    return current_status_problems(report, docs)


#: The envelopes freshness_gate() step 1 exempts from the generic
#: envelope-vs-input sweep, named once so the cited filter below and
#: committed_envelopes() exempt the same set. Each carries no checkable input
#: digest by design (see the constants above) and has its own freshness step
#: keyed on its manifest citation (steps 1b/1b'/1c). The exemption is BY
#: NAME on purpose: their current payloads happen to fail the envelope shape
#: test, but that is an accident -- a later `klt yield` writing
#: `source.scope == "repo"` would otherwise silently pull one into the sweep
#: and fail the gate on an envelope step 1 is written to skip.
STEP1_EXEMPT = (ITEM7_ENVELOPE, PNR_ENVELOPE, ITEM6_ENVELOPE)


def committed_envelopes(evidence_dir: Path) -> set[Path]:
    """Every committed envelope under evidence_dir, at any depth.

    Step 1's committed set must reach subdirectories: an envelope committed
    under signoff/evidence/*/, cited by no manifest entry, is invisible to
    every other freshness step (each of those is gated on a manifest key
    that is absent by assumption), so only this sweep can catch it going
    stale -- the uncited half of the #885 gap.

    A file counts as an envelope when envelope_names_an_input() says it
    names an input artifact. That rule keeps the sidecars sharing these
    directories out of the sweep: requests, limits, sample sets and
    publication.json sidecars name no input, which is exactly what makes
    them sidecars rather than envelopes. inventory-*.json files are the
    item 1/2/9/10 inventories, not envelopes, at any depth, and the three
    STEP1_EXEMPT envelopes are excluded by name. Malformed JSON propagates,
    exactly as the loop consuming this set has always let it.

    Accepted trade-off: a committed, uncited JSON that was meant to be an
    envelope but forgot its input-naming field is skipped here rather than
    failing -- every envelope carrying a signoff claim is cited, and the
    cited path still fails loudly in check_envelope_against_its_input()
    with "names no input artifact".
    """
    envelopes: set[Path] = set()
    for path in evidence_dir.rglob("*.json"):
        if path.name.startswith("inventory-"):
            continue
        if path.relative_to(REPO_ROOT).as_posix() in STEP1_EXEMPT:
            continue
        envelope = json.loads(path.read_text())
        if envelope_names_an_input(envelope):
            envelopes.add(path)
    return envelopes


def freshness_gate(manifest: dict) -> int:
    failures: list[str] = []
    verified = 0

    # Step 1: every cited envelope, and every generic envelope committed under
    # signoff/evidence/ whether cited or not, must still describe its input.
    cited: list[Path] = []
    for _key, part in manifest_entries(manifest):
        named = part.get("file")
        if named and named not in STEP1_EXEMPT:
            cited.append(REPO_ROOT / named)
    # The item 1/2/9/10 inventories are not envelopes (they name no input);
    # their freshness is the member-by-member re-derivation in step 1e.
    committed = committed_envelopes(EVIDENCE_DIR)
    for path in sorted(set(cited) | committed):
        if not path.is_file():
            failures.append(
                f"{path.relative_to(REPO_ROOT)}: cited by the manifest but not "
                f"present in this tree"
            )
            continue
        envelope = json.loads(path.read_text())
        if check_envelope_against_its_input(path, envelope, failures):
            verified += 1

    # Step 2: the manifest's pin and the envelope's own pin must agree, so a
    # half-finished re-pin fails loudly instead of rendering stale_evidence.
    for key, part in manifest_entries(manifest):
        pinned = part.get("content_hash")
        named = part.get("file")
        if not pinned or not named:
            continue
        path = REPO_ROOT / named
        if not path.is_file():
            continue
        own = pinned_input_hash(json.loads(path.read_text()))
        if own != pinned:
            failures.append(
                f"manifest item {key}: pins {pinned} for {named!r}, but that "
                f"envelope's own provenance.input.content_hash is {own}"
            )

    # Step 1b: the item-7 citation (no provenance block; see ITEM7_*).
    item7 = verify_item7_publication(manifest)
    failures += [f"7.digital: {p}" for p in item7]
    if (manifest.get("evidence") or {}).get("7.digital") and not item7:
        verified += 1

    # Step 1b': the item-6 citation (no provenance block; see ITEM6_ENVELOPE).
    if (manifest.get("evidence") or {}).get("6.analog"):
        # Loaded by path, deferred to here: publish_item6 imports this module
        # at import time, so a module-level import would be a cycle. By path
        # rather than `import publish_item6` because that bare name only
        # resolves when check.py is run as a script (which puts `signoff/` on
        # sys.path); a caller that loads check.py by path -- every test in
        # sim/tests/test_signoff_freshness.py -- has no `signoff/` on the path
        # and would raise ModuleNotFoundError the moment 6.analog is cited.
        publish_item6 = load_module_from_path(  # noqa: PLC0415 -- see above
            "signoff_publish_item6", REPO_ROOT / "signoff" / "publish_item6.py"
        )
        item6 = publish_item6.publication_problems()
        failures += [f"6.analog: {p}" for p in item6]
        if not item6:
            verified += 1

    # Step 1b'': the item-6 digital `not_applicable` documents (see ITEM6D_*).
    # Nested document refs, invisible to the manifest_entries loops of steps
    # 1 and 2, and covered independently of where the grader's own scan
    # stopped.
    item6d = verify_item6_digital_publication(manifest)
    failures += [f"6.digital: {p}" for p in item6d]
    if (manifest.get("evidence") or {}).get("6.digital") and not item6d:
        verified += 1

    # Step 1c: the 7.analog citation's testbench-side pins (see ITEM7A_*). Its
    # layout pin is already covered by steps 1 and 2 above.
    failures += [f"7.analog: {p}" for p in verify_item7_analog_publication(manifest)]

    # Step 1c': the separately sized ring2 comparison (#423; see RING2_*).
    failures += [f"ring2 pex: {p}" for p in verify_ring2_pex_publication(manifest)]

    # Step 1d: uncited combiner/sampler post-layout coverage (#418; see CS_*).
    failures += [f"combiner_sampler pex: {p}" for p in verify_combiner_sampler_publication()]

    # Step 1e: the artifact-anchored citations for items 1, 2, 9 and 10 (see
    # signoff/inventories.py): every inventory is re-derived from the live tree.
    for item, partition in inventories.all_units():
        problems = inventories.verify_item(REPO_ROOT, item, partition, manifest)
        failures += [f"T1 item {item} {partition}: {p}" for p in problems]
        if not problems:
            verified += 1

    if failures:
        print("signoff/check.py: freshness verification FAILED", file=sys.stderr)
        for line in failures:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(
        f"signoff/check.py: {verified} cited envelope(s) still match the input "
        f"artifact each one names"
    )
    return 0


class GraderUnavailable(Exception):
    """`klt` is not installed here -- distinct from `klt` running and failing."""


def run_grader() -> dict | None:
    klt = shutil.which("klt")
    if klt is None:
        raise GraderUnavailable(
            "`klt` is not on PATH, so the T1 verdict of record cannot be "
            f"re-graded. Install the pinned grader with: {KLT_INSTALL_HINT} "
            "-- it needs no PDK and no KLayout GUI, it only reads the JSON "
            "envelopes already committed here."
        )

    proc = subprocess.run(
        [klt, "signoff", "--manifest", str(MANIFEST), "--format", "json"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if proc.returncode not in CLEAN_EXITS:
        print(
            f"signoff/check.py: `klt signoff --manifest` failed (exit "
            f"{proc.returncode}) -- the manifest or the tier doc could not be "
            f"read at all.",
            file=sys.stderr,
        )
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return None
    return json.loads(proc.stdout)


def canonical_bytes_problems() -> list[str]:
    """The two JSON files this script writes must stay byte-equal to what it
    writes: `json.dumps(json.loads(raw), indent=2) + "\\n"`, the form
    `write_record` and `write_inventories` produce. Anything else -- a hand
    edit, an editor re-save, a copy through a lossy channel -- would otherwise
    pass as grader output. `signoff/evidence/**` is deliberately out of scope:
    it has other writers (publish_*.py, klt responses) and is append-only."""
    problems: list[str] = []
    for path in (MANIFEST, RECORD):
        if not path.is_file():
            # A missing file already has its own failure in main() and
            # compare_record(); do not shadow it with a canonical-form one.
            continue
        raw = path.read_bytes()
        try:
            canonical = (json.dumps(json.loads(raw), indent=2) + "\n").encode("utf-8")
        except (UnicodeDecodeError, ValueError):
            problems.append(
                f"{path.relative_to(REPO_ROOT)} is not readable JSON -- "
                "regenerate it with 'python3 signoff/check.py --write' and commit it"
            )
            continue
        if raw != canonical:
            problems.append(
                f"{path.relative_to(REPO_ROOT)} is not byte-equal to the canonical "
                "form this script writes (json.dumps(json.loads(raw), indent=2) + "
                "'\\n') -- regenerate it with 'python3 signoff/check.py --write' "
                "and commit it"
            )
    return problems


def write_record(report: dict) -> int:
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(report, indent=2) + "\n")
    print(f"signoff/check.py: wrote {RECORD.relative_to(REPO_ROOT)}")
    return 0


def compare_record(report: dict) -> int:
    if not RECORD.is_file():
        print(
            f"signoff/check.py: {RECORD.relative_to(REPO_ROOT)} is missing -- "
            f"regenerate it with 'python3 signoff/check.py --write' and commit it",
            file=sys.stderr,
        )
        return 1

    committed = json.loads(RECORD.read_text())
    if committed != report:
        fresh_build = (report.get("build") or {}).get("version")
        record_build = (committed.get("build") or {}).get("version")
        print(
            "signoff/check.py: the committed T1 verdict of record is stale.\n"
            "  A fresh `klt signoff --manifest` run no longer matches\n"
            f"  {RECORD.relative_to(REPO_ROOT)}. That is not a tool bug: either\n"
            "  this block's evidence moved, or the checklist did, or the grader\n"
            f"  did (record: klt {record_build}, this run: klt {fresh_build};\n"
            f"  the pin this repo grades against is klt {KLT_GRADER_PIN}).\n"
            "  Regenerate with\n"
            "    python3 signoff/check.py --write\n"
            "  commit the result, and update signoff/README.md's reading of any\n"
            "  item whose status, reason or citation changed.",
            file=sys.stderr,
        )
        _print_item_diff(committed, report)
        return 1

    met = report.get("t1_met_count")
    total = report.get("t1_item_count")
    print(
        f"signoff/check.py: verdict of record is current -- T1 {met}/{total} "
        f"items met, tier={report.get('tier')!r}"
    )
    return 0


def _print_item_diff(committed: dict, fresh: dict) -> None:
    def index(report: dict) -> dict:
        return {
            (i.get("tier"), i.get("id"), i.get("partition")): (
                i.get("status"),
                i.get("reason"),
            )
            for i in report.get("items", [])
        }

    old, new = index(committed), index(fresh)
    for key in sorted(set(old) | set(new), key=lambda k: (str(k[0]), k[1] or 0, str(k[2]))):
        if old.get(key) != new.get(key):
            print(
                f"    {key[0]} item {key[1]} ({key[2]}): "
                f"{old.get(key)} -> {new.get(key)}",
                file=sys.stderr,
            )


def write_inventories(manifest: dict) -> dict | None:
    """Rebuild the item 1/2/9/10 inventories and envelopes and re-pin their
    manifest citations (`--write`). Returns the updated manifest, or None when
    the tree does not support the claims (nothing is written in that case)."""
    try:
        pins = inventories.write_all(REPO_ROOT)
    except inventories.AuditError as exc:
        print(f"signoff/check.py: inventory audit FAILED: {exc}", file=sys.stderr)
        return None
    evidence = manifest.setdefault("evidence", {})
    for (item, partition), pin in pins.items():
        evidence[inventories.manifest_key(item, partition)] = {
            "file": inventories.envelope_path(item, partition),
            "content_hash": pin,
        }
    manifest["evidence"] = dict(sorted(evidence.items()))
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"signoff/check.py: wrote {len(pins)} inventories, envelopes and manifest pins "
        "for T1 items 1, 2, 9 and 10"
    )
    return manifest


def write_item6_digital(manifest: dict) -> dict | None:
    """Re-project README's ratified table into the item-6 digital spec
    document and re-pin both `not_applicable` hashes (`--write`).

    The statement is hand-written, never generated: `--write` re-pins its
    hash from bytes, and the freshness gate's content checks (coverage,
    nonempty class/reason, the two statistical rows classified honestly)
    are what keep a re-pin from blessing a bad one. Returns the updated
    manifest, or None (nothing written) when the projection cannot be read
    or the statement is not committed.
    """
    try:
        projection = project_item6_digital_spec((REPO_ROOT / "README.md").read_text())
    except (OSError, ValueError) as exc:
        print(f"signoff/check.py: item-6 digital spec projection FAILED: {exc}", file=sys.stderr)
        return None
    statement = REPO_ROOT / ITEM6D_STATEMENT
    if not statement.is_file():
        print(
            f"signoff/check.py: {ITEM6D_STATEMENT} is missing -- it is hand-written, "
            f"not generated; commit it before re-pinning",
            file=sys.stderr,
        )
        return None
    spec_path = REPO_ROOT / ITEM6D_SPEC
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(json.dumps(projection, indent=2) + "\n")
    evidence = manifest.setdefault("evidence", {})
    evidence["6.digital"] = {
        "not_applicable": {
            "spec": {"file": ITEM6D_SPEC, "content_hash": sha256_file(spec_path)},
            "statement": {"file": ITEM6D_STATEMENT, "content_hash": sha256_file(statement)},
        }
    }
    manifest["evidence"] = dict(sorted(evidence.items()))
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"signoff/check.py: wrote {ITEM6D_SPEC} ({len(projection['rows'])} ratified "
        f"rows) and the 6.digital not_applicable document pins"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--write",
        action="store_true",
        help="rebuild the item 1/2/9/10 inventories, the item-6 digital spec projection "
        "and its manifest pins, then regenerate signoff/records/t1-tier-report.json "
        "instead of diffing it",
    )
    parser.add_argument(
        "--require-tools",
        action="store_true",
        help="fail instead of self-skipping when `klt` is not installed",
    )
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text())
    if not manifest.get("block"):
        print(
            "signoff/check.py: the manifest declares no 'block' -- it is "
            "required, and is how this block's row is identified in the fleet "
            "roll-up that consumes this file",
            file=sys.stderr,
        )
        return 1

    # Canonical-form gate: verify mode only. `--write` is the remedy for a
    # non-canonical file -- write_inventories and write_record rewrite MANIFEST
    # and RECORD in exactly this form -- so the gate must not stand in its own
    # way. It runs before everything else, including the grader's self-skip,
    # so a mangled file cannot pass merely because klt is absent.
    canonical = [] if args.write else canonical_bytes_problems()
    if canonical:
        for problem in canonical:
            print(f"signoff/check.py: {problem}", file=sys.stderr)
        return 1

    if args.write:
        manifest = write_inventories(manifest)
        if manifest is None:
            return 1
        manifest = write_item6_digital(manifest)
        if manifest is None:
            return 1

    rc = freshness_gate(manifest)
    if rc:
        return rc

    status_problems = verify_current_status()
    if status_problems:
        for problem in status_problems:
            print(f"signoff/check.py: current T1 status: {problem}", file=sys.stderr)
        return 1

    try:
        report = run_grader()
    except GraderUnavailable as exc:
        if args.require_tools or args.write:
            print(f"signoff/check.py: {exc}", file=sys.stderr)
            return 1
        print(
            f"signoff/check.py: SKIPPED the re-grade -- {exc}\n"
            "signoff/check.py: the freshness gate above ran and passed; "
            "re-run with --require-tools to make this a failure."
        )
        return 0
    if report is None:
        return 1

    if args.write:
        return write_record(report)
    return compare_record(report)


if __name__ == "__main__":
    sys.exit(main())
