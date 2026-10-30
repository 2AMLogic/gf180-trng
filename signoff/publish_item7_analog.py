#!/usr/bin/env python3
"""Run `klt pex` over ring1's layout and publish it as T1 item 7's analog citation.

    python3 signoff/publish_item7_analog.py                 # run klt pex, then publish
    python3 signoff/publish_item7_analog.py --envelope F    # publish an existing run's stdout
    python3 signoff/check.py --write                        # then regenerate the verdict

    python3 signoff/publish_item7_analog.py --ring ring2 --backend batch
                                                            # the separate, uncited ring2 comparison (#423)

The run is one `klt pex` invocation (KLT_PEX_ARGS below): extract
layout/rings/ro_ring11/ro_ring11.gds with parasitics, run
sim/tb/ro-ring11-pex/request.json against the schematic DUT and against the
extracted netlist at every corner of DR-0006's 27-point grid, and report the
per-corner, per-row delta. Use the DR-0026 producer build
(`pip install "klayout-tools==0.8.0" "klayout==0.30.10"`). A 27-corner grid
on each side is a SPICE grid: on a host that exports `KLT_SIM_BACKEND=batch`
it goes to the batch fleet; elsewhere it runs on the local backend.
`--envelope` publishes a run already made with exactly these arguments (its
`-o` netlist must already be at ITEM7A_NETLIST).

What it does, and refuses to do:

* The published envelope is the **native** `klt pex` JSON response, byte for
  byte. Nothing is added to it or derived into it.
* `publication.json` beside it pins what the envelope cannot: the testbench
  request, the testbench body and the schematic DUT, by sha256, plus the
  envelope itself and the envelope's own `body_bias.status`, copied verbatim
  so nobody can read the citation without meeting it.
* `source_sha256` records the identity of the consumed design-source sections
  (ro_ring11, ro_nand2, ro_stage and xr1's sizing -- not the whole file; see
  build_dut.py) the DUT was rendered from. It is checked against current
  source; it is never attached to older evidence.
* It refuses to run or publish unless the committed DUT equals
  build_dut.render_dut() of the current source, and refuses to publish unless check.item7_analog_problems() is empty: a
  `pass` status, no pin-count or flat-DUT mismatch, all 27 corners, every
  delta row measured on both sides, the committed extracted netlist is the
  one the run hashed, and its ring positions re-derive to the schematic
  DUT's header (sim/tb/ro-ring11-pex/build_dut.py).
* `--ring ring2` runs the same machinery over ring2's layout
  (layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds, sim/tb/ro-ring11-ring2-pex/)
  and publishes under signoff/evidence/post-layout/ring2/. It is **not** a
  manifest citation: `7.analog` stays ring1's, the manifest is never touched,
  and the sidecar's `verdict` (check.combiner_sampler_verdict() over the
  envelope and request: every declared corner/row accounted for, an
  unmeasured row is `incomplete`, never a pass) is recomputed by check.py on
  every run. An `incomplete` verdict is refused unless `--allow-incomplete`.
  A `fail` is published as it stands. The ring2 fixture is judged by
  check.py independently of ring1's; until a ring2 run is committed it is an
  explicitly unrun fixture (see sim/tb/ro-ring11-ring2-pex/README.md).
* `body_bias` is **not** a refusal condition. It is reported, never graded,
  by both `klt pex` and `klt signoff`; this repository states it in
  signoff/README.md instead. Every PMOS body in this layout is untapped, so
  the status is expected to read "unbiased".
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402
import publish_common as common  # noqa: E402

TAG = "publish_item7_analog"
REPO_ROOT = check.REPO_ROOT
SCRATCH = REPO_ROOT / "sim" / ".work" / "ro-ring11-pex"

KLT_PEX_ARGS = [
    "pex", "layout/rings/ro_ring11/ro_ring11.gds", f"{check.ITEM7A_TB_DIR}/request.json",
    "--deck", "gf180mcu", "--pdk", "gf180mcuD", "--top", "ro_ring11",
    "-o", check.ITEM7A_NETLIST, "--outdir", "sim/.work/ro-ring11-pex", "--format", "json",
]
RING2_SCRATCH = REPO_ROOT / "sim" / ".work" / "ro-ring11-ring2-pex"
RING2_KLT_PEX_ARGS = [
    "pex", check.RING2_GDS, check.RING2_INPUTS[0],
    "--deck", "gf180mcu", "--pdk", "gf180mcuD", "--top", "ro_ring11_ring2",
    "-o", check.RING2_NETLIST, "--outdir", "sim/.work/ro-ring11-ring2-pex", "--format", "json",
]

RING2_COVERAGE_EXCLUSIONS = [
    "scope: ring2 alone (the separately sized oscillator, xr2); ring1, the buffers, the XOR "
    "combiner, the samplers and every inter-region net are outside this run",
    "isolation: one ring free-running on its own supply, `en` tied to that supply; no "
    "coupling to the other ring or to neighbouring blocks",
    "loads: the ring output is unloaded (no ro_buf); absolute periods differ from the "
    "array-level records",
    "determinism: noiseless transient, no device noise or mismatch; nothing here estimates "
    "entropy, bias or jitter",
    "bodies: every PMOS body in the extraction is an untapped floating n-well (body_bias "
    "below); the schematic side ties PMOS bulk to vddr. The extracted-side result is a "
    "diagnosis under that limitation (#339/#411), not a prediction of fabricated silicon",
    "timing and silicon: no full-chip timing or silicon-performance claim",
]


def _build_dut():
    return check._load_build_dut()


def run_pex(ring: str = "ring1", backend: str | None = None) -> Path:
    scratch, pex_args = (SCRATCH, KLT_PEX_ARGS) if ring == "ring1" else (RING2_SCRATCH, RING2_KLT_PEX_ARGS)
    return common.run_pex(REPO_ROOT, scratch, pex_args, backend, TAG)


def build_ring2_publication(envelope: dict, raw_sha: str, backend: str | None) -> dict:
    bd = _build_dut()
    ring = bd.RING2
    netlist_text = (REPO_ROOT / check.RING2_NETLIST).read_text()
    return common.build_publication(
        REPO_ROOT, envelope, raw_sha, backend,
        schema=check.RING2_PUBLICATION_SCHEMA,
        scope="separate native schematic-vs-extracted comparison of ring2; not a manifest citation",
        pex_args=RING2_KLT_PEX_ARGS,
        source_sha256=bd.source_identity(ring=ring),
        inputs=check.RING2_INPUTS,
        port_map=bd.extraction_port_map(netlist_text, ring),
        exclusions=RING2_COVERAGE_EXCLUSIONS,
        envelope_file=check.RING2_ENVELOPE,
        request_rel=check.RING2_INPUTS[0],
    )


def publish_ring2(args) -> int:
    stale = check.item7_analog_dut_source_problems(None, "ring2") + check.ring2_request_problems()
    if stale:
        return common.fail(f"{TAG}: ring2 fixture is stale -- nothing run", stale)
    loaded = common.load_envelope(args.envelope, lambda: run_pex("ring2", args.backend), TAG)
    if loaded is None:
        return 1
    raw, envelope = loaded
    refusals = common.envelope_refusals(REPO_ROOT, envelope, check.RING2_NETLIST)
    if refusals:
        return common.fail(f"{TAG}: refusing to publish ring2", refusals)
    backend = None if args.envelope else args.backend
    pub = common.publish_envelope(
        f"{TAG}: refusing to publish ring2",
        REPO_ROOT / check.RING2_ENVELOPE, raw,
        lambda sha: build_ring2_publication(envelope, sha, backend),
        lambda pub: check.item7_analog_problems(pub, envelope, "ring2"),
        args.allow_incomplete,
        REPO_ROOT / check.RING2_PUBLICATION,
    )
    if pub is None:
        return 1
    v = pub["verdict"]
    print(f"{TAG}: published ring2 (not a manifest citation); verdict "
          f"{v['verdict']!r} {v['counts']} (body_bias.status: {pub['body_bias_status']!r})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--envelope", type=Path, help="an existing `klt pex` stdout to publish")
    ap.add_argument("--ring", choices=("ring1", "ring2"), default="ring1",
                    help="ring1 (default): the cited 7.analog publication; ring2: the separate "
                         "uncited comparison")
    ap.add_argument("--backend", default=None,
                    help="klt sim backend for both sides (default: klt's own, i.e. $KLT_SIM_BACKEND)")
    ap.add_argument("--allow-incomplete", action="store_true",
                    help="(ring2) publish even if some declared corner/row was not measured")
    args = ap.parse_args()
    if args.ring == "ring2":
        return publish_ring2(args)
    # Refuse before spending a 27-corner grid on a fixture that no longer
    # represents the design source.
    stale = check.item7_analog_dut_source_problems()
    if stale:
        return common.fail(f"{TAG}: schematic DUT is stale -- nothing run", stale)
    loaded = common.load_envelope(args.envelope, lambda: run_pex("ring1", args.backend), TAG)
    if loaded is None:
        return 1
    raw, envelope = loaded

    pub = common.publish_envelope(
        f"{TAG}: refusing to publish",
        REPO_ROOT / check.ITEM7A_ENVELOPE, raw,
        lambda sha: {
            "schema": "gf180-trng/item7-analog-publication/1",
            "producer": "klt " + shlex.join(KLT_PEX_ARGS),
            "producer_build": (envelope.get("provenance") or {}).get("klt_version"),
            "layout_content_hash": check.pinned_input_hash(envelope),
            "source_sha256": _build_dut().source_identity(),
            "inputs_sha256": {rel: check.sha256_file(REPO_ROOT / rel) for rel in check.ITEM7A_INPUTS},
            "body_bias_status": (envelope.get("body_bias") or {}).get("status"),
            "envelope": {"file": check.ITEM7A_ENVELOPE, "sha256": sha},
        },
        lambda pub: check.item7_analog_problems(pub, envelope),
        False,
        REPO_ROOT / check.ITEM7A_PUBLICATION,
    )
    if pub is None:
        return 1
    manifest = json.loads(check.MANIFEST.read_text())
    manifest["evidence"]["7.analog"] = {
        "file": check.ITEM7A_ENVELOPE,
        "content_hash": pub["layout_content_hash"],
    }
    manifest["evidence"] = dict(sorted(manifest["evidence"].items()))
    check.MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"publish_item7_analog: published as 7.analog (body_bias.status: "
        f"{pub['body_bias_status']!r}); now run signoff/check.py --write"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
