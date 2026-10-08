#!/usr/bin/env python3
"""Re-grade this block's T1 state and fail when the committed verdict has rotted.

    python3 signoff/check.py                  # verify; self-skips the re-grade if klt is absent
    python3 signoff/check.py --require-tools  # verify; fail instead of skipping (CI, check:all)
    python3 signoff/check.py --write          # regenerate signoff/records/t1-tier-report.json

`signoff/records/t1-tier-report.json` is this block's **verdict of record**
against the klayout-tools design-evidence ladder: the literal output of

    klt signoff --manifest signoff/block-manifest.json --format json

A verdict that is generated once and then never re-run is prose again within a
week, so this script exists to re-run it on every push. It fails on four
separable conditions, in order, so a red build says which one:

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
(structural)", klayout-tools#2025) landed after that release. `KLT_PIN` below
is a published PyPI release so a third party can reproduce the committed
record with one `pip install`, and the record itself carries `build.version`,
`build.grading_ruleset_id` and `source_doc_content_hash`, so a bump is visible
in the diff rather than inferred. Bumping the pin is a real change to the
yardstick: expect the record to move in the same commit, and re-read
signoff/README.md's per-item notes against anything the bump adds or rewords.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "signoff" / "block-manifest.json"
RECORD = REPO_ROOT / "signoff" / "records" / "t1-tier-report.json"
EVIDENCE_DIR = REPO_ROOT / "signoff" / "evidence"

#: The klayout-tools release that grades this block. See the module docstring.
KLT_PIN = "0.6.0"
#: The KLayout engine release KLT_PIN is installed with (DR-0026): the engine
#: the release records it was tested against. Not checked by this script --
#: `klt signoff` does not depend on it -- but it is half of the normative
#: build, so it is defined here next to KLT_PIN. Every `klayout-tools==` /
#: `klayout==` pin restated in workflows, READMEs and docstrings is held to
#: these two constants by sim/tools/klt_pin_sites.py --check (npm run
#: check:spec); a pin bump edits them here first, then the sites it lists.
KLAYOUT_PIN = "0.30.10"
KLT_INSTALL_HINT = f'pip install "klayout-tools=={KLT_PIN}"'

#: `klt signoff` exit codes that mean "the grader ran fine".
#: 0 = every T1 item met; 3 = ran fine, not yet T1.
CLEAN_EXITS = (0, 3)


#: T1 item 7 (digital): the native `klt functional-verification` response of a
#: post-route, SDF-annotated gate run, published by signoff/publish_item7.py.
#: That envelope has no `provenance` block, so the manifest cannot pin it; the
#: sidecar below carries the freshness pins and verify_item7_publication()
#: re-checks them (see its docstring).
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


def _ring_port_check(netlist: Path) -> str | None:
    """Re-derive the extracted netlist's ring positions with the producer's
    own build_dut.py and require they match the schematic DUT's header."""
    import importlib.util

    path = REPO_ROOT / ITEM7A_TB_DIR / "build_dut.py"
    spec = importlib.util.spec_from_file_location("ro_ring11_pex_build_dut", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        got = mod.extraction_port_map(netlist.read_text())
        want = mod.dut_header(mod.DUT.read_text())
    except mod.BuildError as exc:
        return str(exc)
    if got != want:
        return f"extracted ring positions {got} != schematic DUT header {want}"
    return None


def _load_build_dut():
    import importlib.util

    path = REPO_ROOT / ITEM7A_TB_DIR / "build_dut.py"
    spec = importlib.util.spec_from_file_location("ro_ring11_pex_build_dut", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def item7_analog_dut_source_problems(pub: dict | None = None) -> list[str]:
    """The generated schematic DUT must be what build_dut.py renders from the
    current design source (stdlib only; no klt, ngspice or PDK).

    Scope: the consumed circuit sections (ro_ring11, ro_nand2, ro_stage and
    ring1's xr1 sizing), not the whole design file -- see build_dut.py. When
    the publication records `source_sha256` it must equal today's identity;
    publications that predate the field are not retro-fitted with one.
    """
    mod = _load_build_dut()
    out: list[str] = []
    problem = mod.dut_source_problem()
    if problem:
        out.append(f"schematic DUT vs source: {problem}")
    recorded = (pub or {}).get("source_sha256")
    if recorded is not None:
        try:
            current = mod.source_identity()
        except mod.BuildError as exc:
            out.append(f"source identity: {exc}")
        else:
            if recorded != current:
                out.append(
                    f"source identity: STALE -- the publication recorded {recorded}, the "
                    f"consumed sections of design/ro_array_core.spice hash to {current} today; "
                    f"re-run signoff/publish_item7_analog.py"
                )
    return out


def item7_analog_problems(pub: dict, envelope: dict) -> list[str]:
    """Every reason the 7.analog publication must not be treated as current."""
    out: list[str] = item7_analog_dut_source_problems(pub)
    if envelope.get("status") != "pass":
        out.append(f"klt pex status is {envelope.get('status')!r}, not 'pass'")
    # The 0.6.0 release predates `measurement` (klayout-tools#2478); absent
    # means testbench mode. A caller-measured run is not what this cites.
    if (envelope.get("measurement") or {}).get("mode", "testbench") != "testbench":
        out.append("klt pex measurement.mode is not 'testbench'")
    for key in ("pin_count_mismatch", "flat_dut_mismatch"):
        if envelope.get(key) is not None:
            out.append(f"klt pex reports {key}")
    if envelope.get("corner_count") != ITEM7A_CORNERS:
        out.append(f"corner_count is {envelope.get('corner_count')}, not {ITEM7A_CORNERS}")
    names = [n for tb in envelope.get("testbenches") or [] for n in tb.get("measurement_names") or []]
    delta = envelope.get("delta") or []
    if not names or len(delta) != ITEM7A_CORNERS * len(names):
        out.append(f"delta has {len(delta)} rows, expected {ITEM7A_CORNERS} x {len(names)}")
    for row in delta:
        if row.get("status") != "pass" or row.get("schematic_value") is None or row.get("extracted_value") is None:
            out.append(f"delta row {row.get('corner_id')}/{row.get('spec_row')} is not a two-sided pass")
    bias = envelope.get("body_bias")
    if not isinstance(bias, dict) or "status" not in bias:
        out.append("envelope carries no body_bias block")
    elif pub.get("body_bias_status") != bias["status"]:
        out.append(
            f"publication.json states body_bias_status {pub.get('body_bias_status')!r}, "
            f"the envelope says {bias['status']!r}"
        )
    netlist = REPO_ROOT / ITEM7A_NETLIST
    if not netlist.is_file():
        out.append(f"{ITEM7A_NETLIST} is missing")
    else:
        recorded = (envelope.get("extraction") or {}).get("netlist_sha256")
        if sha256_file(netlist) != f"sha256:{recorded}":
            out.append(f"{ITEM7A_NETLIST} is not the netlist this klt pex run extracted")
        problem = _ring_port_check(netlist)
        if problem:
            out.append(f"ring port positions: {problem}")
    pinned = pub.get("inputs_sha256") or {}
    for rel in ITEM7A_INPUTS:
        path = REPO_ROOT / rel
        if rel not in pinned or not path.is_file():
            out.append(f"input {rel}: not pinned or missing")
        elif sha256_file(path) != pinned[rel]:
            out.append(
                f"input {rel}: STALE -- the run used {pinned[rel]}, it hashes to "
                f"{sha256_file(path)} today; re-run signoff/publish_item7_analog.py"
            )
    env_path = REPO_ROOT / ITEM7A_ENVELOPE
    if env_path.is_file() and (pub.get("envelope") or {}).get("sha256") != sha256_file(env_path):
        out.append("published envelope differs from the sha256 in publication.json")
    return out


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


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


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


def check_envelope_against_its_input(
    envelope_path: Path, envelope: dict, failures: list[str]
) -> bool:
    """True when this envelope's recorded input digest matches disk today.

    Returns False when the envelope names no checkable input at all, so the
    caller can count what was actually verified rather than what was seen.
    """
    rel = envelope_path.relative_to(REPO_ROOT)
    kind_hints = [
        # (field naming the input artifact, field carrying its digest)
        ("file", "provenance.input.content_hash"),
        ("layout", "environment.layout_sha256"),
        ("source", "provenance.input.content_hash"),
    ]

    for name_field, digest_field in kind_hints:
        named = envelope.get(name_field)
        if name_field == "layout" and isinstance(named, dict):
            # `klt pex` (schema 2) writes `layout` as a `{path, scope}` object
            # and pins the stream it extracted in provenance.input.content_hash.
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


def manifest_entries(manifest: dict):
    """Yield (item key, entry dict) for every object-shaped evidence entry."""
    for key, entry in sorted((manifest.get("evidence") or {}).items()):
        parts = entry if isinstance(entry, list) else [entry]
        for part in parts:
            if isinstance(part, dict):
                yield key, part


def freshness_gate(manifest: dict) -> int:
    failures: list[str] = []
    verified = 0

    # Step 1: every cited envelope, and every generic envelope committed under
    # signoff/evidence/ whether cited or not, must still describe its input.
    cited: list[Path] = []
    for _key, part in manifest_entries(manifest):
        named = part.get("file")
        if named and named != ITEM7_ENVELOPE:
            cited.append(REPO_ROOT / named)
    for path in sorted(set(cited) | set(EVIDENCE_DIR.glob("*.json"))):
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

    # Step 1c: the 7.analog citation's testbench-side pins (see ITEM7A_*). Its
    # layout pin is already covered by steps 1 and 2 above.
    failures += [f"7.analog: {p}" for p in verify_item7_analog_publication(manifest)]

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
            f"  the pin this repo grades against is klt {KLT_PIN}).\n"
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate signoff/records/t1-tier-report.json instead of diffing it",
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

    rc = freshness_gate(manifest)
    if rc:
        return rc

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
