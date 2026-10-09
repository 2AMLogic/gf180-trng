#!/usr/bin/env python3
"""Run `klt pex` over the assembled combiner/sampler block and publish the result.

    python3 signoff/publish_combiner_sampler_pex.py --backend batch   # run klt pex, then publish
    python3 signoff/publish_combiner_sampler_pex.py --envelope F      # publish an existing run's stdout
    python3 signoff/check.py                                          # then re-verify freshness

Additional post-layout coverage (#418), not a manifest citation: T1 item 7's
analog citation stays ring1's (signoff/publish_item7_analog.py). This adds
the signal path that actually delivers raw samples -- the two ring-output
buffers, the XOR combiner and the four sampling flip-flops -- under the
deterministic clock/reset/two-input schedule in
sim/tb/combiner-sampler-pex/stimulus.py, compared schematic vs. extracted at
DR-0006's 27-point grid.

The run is one `klt pex` invocation (KLT_PEX_ARGS). Use DR-0026's producer
build: set `KLT` to e.g. `uvx --from klayout-tools==0.6.0 --with
klayout==0.30.10 klt`, or install it. klt 0.6.0 does not read
`KLT_SIM_BACKEND`, so the backend is passed explicitly (`--backend`, default
the `KLT_SIM_BACKEND` environment variable, else `local`); a 27-corner grid
on each side belongs on a batch backend where one is configured. The backend
does not enter the evidence: `klt pex` 0.6.0 drops each side's `klt sim`
environment, batch job ids included (klayout-tools#2876), so
publication.json records which backend was requested and nothing more.

What it does, and refuses to do:

* The published envelope is the **native** `klt pex` JSON response, byte for
  byte. Nothing is added to it or derived into it.
* `publication.json` beside it pins what the envelope does not: the request,
  testbench body and schematic DUT (sha256), the consumed design-source
  identity, the extracted netlist's port map, the PDK/deck provenance, the
  envelope's own `body_bias` status and PMOS count, and the coverage
  exclusions. Its `verdict` is check.combiner_sampler_verdict() over the
  envelope and request -- both sides held to the request's limits, every
  declared corner and row accounted for -- and check.py recomputes it on
  every run.
* It refuses to run or publish unless the DUT, testbench and request are
  current with their sources; refuses a response from any klt but the pin;
  refuses a pin-count or flat-DUT mismatch, or a netlist whose ports do not
  re-derive to the DUT header; and refuses an `incomplete` verdict (a corner
  or row unmeasured) unless `--allow-incomplete` is given, in which case the
  verdict says so.
* A `fail` verdict is published as it stands. Failures are evidence.
* `body_bias` is reported, never a refusal condition, exactly as for ring1:
  the layout draws no n-well ties, so every PMOS body is a floating well.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402

REPO_ROOT = check.REPO_ROOT
SCRATCH = REPO_ROOT / "sim" / ".work" / "combiner-sampler-pex"

KLT_PEX_ARGS = [
    "pex", check.CS_GDS, check.CS_REQUEST,
    "--deck", "gf180mcu", "--pdk", "gf180mcuD", "--top", "combiner_sampler",
    "-o", check.CS_NETLIST, "--outdir", "sim/.work/combiner-sampler-pex", "--format", "json",
]

COVERAGE_EXCLUSIONS = [
    "rings: rn1/rn2 are driven by deterministic logic steps at vdd level, not by the "
    "oscillators; ring layout, ring supplies (vddr1/vddr2) and the ring-to-buffer "
    "inter-region nets are outside this layout and this run",
    "randomness: deterministic stimuli; nothing here estimates entropy, bias or jitter",
    "boundary timing: data and reset change only far from clock edges (see stimulus.py "
    "settling windows); setup/hold, recovery/removal and metastability are not exercised",
    "bodies: every PMOS body in the extraction is an untapped floating n-well "
    "(body_bias below); the schematic side ties PMOS bulk to vdd and NMOS bulk to vss. "
    "The extracted-side result is a diagnosis under that limitation (#339/#411/#412), "
    "not a prediction of fabricated silicon",
    "loads: the four flip-flop outputs and xo/ro1/ro2 are unloaded (the downstream "
    "digital block is not included); the *n monitors draw no current",
    "noise and mismatch: transient without device noise or Monte Carlo mismatch",
    "full chip: block-level extraction of combiner_sampler.gds only; no top-level "
    "routing, supply network or neighbouring blocks",
]


def run_pex(backend: str) -> Path:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    out = SCRATCH / "klt_pex_response.json"
    klt = shlex.split(os.environ.get("KLT", "klt"))
    argv = [*klt, *KLT_PEX_ARGS, "--backend", backend]
    print(f"publish_combiner_sampler_pex: {shlex.join(argv)}", file=sys.stderr)
    with out.open("w") as fh:
        subprocess.run(argv, cwd=REPO_ROOT, stdout=fh, check=True)
    return out


def build_publication(envelope: dict, raw_envelope_sha: str, backend: str | None) -> dict:
    bd = check._load_tb_module(check.CS_TB_DIR, "build_dut")
    netlist_text = (REPO_ROOT / check.CS_NETLIST).read_text()
    header = bd.extracted_graph(netlist_text)[1]
    ports = bd.extraction_port_map(netlist_text, bd.DUT.read_text())
    request = json.loads((REPO_ROOT / check.CS_REQUEST).read_text())
    prov = envelope.get("provenance") or {}
    bias = envelope.get("body_bias") or {}
    return {
        "schema": check.CS_PUBLICATION_SCHEMA,
        "scope": "additional post-layout coverage of combiner_sampler; not a manifest citation",
        "producer": "klt " + shlex.join(KLT_PEX_ARGS),
        "producer_build": prov.get("klt_version"),
        "klayout_build": prov.get("klayout_version"),
        "pdk": prov.get("pdk"),
        "deck": prov.get("deck"),
        "backend_requested": backend,
        "layout_content_hash": check.pinned_input_hash(envelope),
        "source_sha256": bd.source_identity(),
        "inputs_sha256": {rel: check.sha256_file(REPO_ROOT / rel) for rel in check.CS_INPUTS},
        "port_map": dict(zip(header, ports)),
        "body_bias_status": bias.get("status"),
        "body_bias_unbiased_device_count": bias.get("unbiased_device_count"),
        "coverage_exclusions": COVERAGE_EXCLUSIONS,
        "verdict": check.combiner_sampler_verdict(envelope, request),
        "envelope": {"file": check.CS_ENVELOPE, "sha256": raw_envelope_sha},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--envelope", type=Path, help="an existing `klt pex` stdout to publish")
    ap.add_argument("--backend", default=os.environ.get("KLT_SIM_BACKEND", "local"),
                    help="klt sim backend for both sides (default: $KLT_SIM_BACKEND or local)")
    ap.add_argument("--allow-incomplete", action="store_true",
                    help="publish even if some declared corner/row was not measured")
    args = ap.parse_args(argv)

    stale = check.combiner_sampler_dut_source_problems()
    if stale:
        print("publish_combiner_sampler_pex: fixture is stale -- nothing run", file=sys.stderr)
        for f in stale:
            print(f"  - {f}", file=sys.stderr)
        return 1
    try:
        src = args.envelope.resolve() if args.envelope else run_pex(args.backend)
    except subprocess.CalledProcessError as exc:
        # klt pex prints its error envelope on stdout/stderr; nothing is published.
        print(f"publish_combiner_sampler_pex: klt pex failed (exit {exc.returncode}); "
              f"nothing published", file=sys.stderr)
        return 1
    raw = src.read_bytes()
    envelope = json.loads(raw)

    refusals: list[str] = []
    build = (envelope.get("provenance") or {}).get("klt_version")
    if build != check.KLT_PIN:
        refusals.append(f"response is from klt {build!r}, not the producer pin {check.KLT_PIN}")
    for key in ("pin_count_mismatch", "flat_dut_mismatch"):
        if envelope.get(key) is not None:
            refusals.append(f"klt pex reports {key}: {envelope[key]!r}")
    if not (REPO_ROOT / check.CS_NETLIST).is_file():
        refusals.append(f"{check.CS_NETLIST} is missing (the run's -o netlist)")
    if refusals:
        print("publish_combiner_sampler_pex: refusing to publish", file=sys.stderr)
        for f in refusals:
            print(f"  - {f}", file=sys.stderr)
        return 1

    dest = REPO_ROOT / check.CS_ENVELOPE
    dest.parent.mkdir(parents=True, exist_ok=True)
    previous = dest.read_bytes() if dest.is_file() else None
    dest.write_bytes(raw)
    try:
        pub = build_publication(envelope, check.sha256_file(dest), args.backend if not args.envelope else None)
    except Exception as exc:  # noqa: BLE001 -- restore, then report
        pub, failures = None, [f"{type(exc).__name__}: {exc}"]
    else:
        failures = check.combiner_sampler_problems(pub, envelope)
        if pub["verdict"]["verdict"] == "incomplete" and not args.allow_incomplete:
            failures.append(
                f"verdict is incomplete ({pub['verdict']['counts']['unmeasured']} declared "
                f"row(s) unmeasured); re-run, or pass --allow-incomplete to publish it as such"
            )
    if failures:
        if previous is None:
            dest.unlink()
        else:
            dest.write_bytes(previous)
        print("publish_combiner_sampler_pex: refusing to publish -- envelope not written", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    (REPO_ROOT / check.CS_PUBLICATION).write_text(json.dumps(pub, indent=2) + "\n")
    v = pub["verdict"]
    print(
        f"publish_combiner_sampler_pex: published; verdict {v['verdict']!r} {v['counts']} "
        f"(body_bias.status: {pub['body_bias_status']!r})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
