#!/usr/bin/env python3
"""Run `klt pex` over ring1's layout and publish it as T1 item 7's analog citation.

    python3 signoff/publish_item7_analog.py                 # run klt pex, then publish
    python3 signoff/publish_item7_analog.py --envelope F    # publish an existing run's stdout
    python3 signoff/check.py --write                        # then regenerate the verdict

The run is one `klt pex` invocation (KLT_PEX_ARGS below): extract
layout/rings/ro_ring11/ro_ring11.gds with parasitics, run
sim/tb/ro-ring11-pex/request.json against the schematic DUT and against the
extracted netlist at every corner of DR-0006's 27-point grid, and report the
per-corner, per-row delta. Use the DR-0026 producer build
(`pip install "klayout-tools==0.6.0" "klayout==0.30.10"`). A 27-corner grid
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
* It refuses to publish unless check.item7_analog_problems() is empty: a
  `pass` status, no pin-count or flat-DUT mismatch, all 27 corners, every
  delta row measured on both sides, the committed extracted netlist is the
  one the run hashed, and its ring positions re-derive to the schematic
  DUT's header (sim/tb/ro-ring11-pex/build_dut.py).
* `body_bias` is **not** a refusal condition. It is reported, never graded,
  by both `klt pex` and `klt signoff`; this repository states it in
  signoff/README.md instead. Every PMOS body in this layout is untapped, so
  the status is expected to read "unbiased".
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402

REPO_ROOT = check.REPO_ROOT
SCRATCH = REPO_ROOT / "sim" / ".work" / "ro-ring11-pex"

KLT_PEX_ARGS = [
    "pex", "layout/rings/ro_ring11/ro_ring11.gds", f"{check.ITEM7A_TB_DIR}/request.json",
    "--deck", "gf180mcu", "--pdk", "gf180mcuD", "--top", "ro_ring11",
    "-o", check.ITEM7A_NETLIST, "--outdir", "sim/.work/ro-ring11-pex", "--format", "json",
]


def run_pex() -> Path:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    out = SCRATCH / "klt_pex_response.json"
    print(f"publish_item7_analog: klt {shlex.join(KLT_PEX_ARGS)}", file=sys.stderr)
    with out.open("w") as fh:
        subprocess.run(["klt", *KLT_PEX_ARGS], cwd=REPO_ROOT, stdout=fh, check=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--envelope", type=Path, help="an existing `klt pex` stdout to publish")
    args = ap.parse_args()
    src = args.envelope.resolve() if args.envelope else run_pex()
    raw = src.read_bytes()
    envelope = json.loads(raw)

    pub = {
        "schema": "gf180-trng/item7-analog-publication/1",
        "producer": "klt " + shlex.join(KLT_PEX_ARGS),
        "producer_build": (envelope.get("provenance") or {}).get("klt_version"),
        "layout_content_hash": check.pinned_input_hash(envelope),
        "inputs_sha256": {rel: check.sha256_file(REPO_ROOT / rel) for rel in check.ITEM7A_INPUTS},
        "body_bias_status": (envelope.get("body_bias") or {}).get("status"),
        "envelope": {"file": check.ITEM7A_ENVELOPE},
    }
    dest = REPO_ROOT / check.ITEM7A_ENVELOPE
    dest.parent.mkdir(parents=True, exist_ok=True)
    previous = dest.read_bytes() if dest.is_file() else None
    dest.write_bytes(raw)
    pub["envelope"]["sha256"] = check.sha256_file(dest)
    failures = check.item7_analog_problems(pub, envelope)
    if failures:
        if previous is None:
            dest.unlink()
        else:
            dest.write_bytes(previous)
        print("publish_item7_analog: refusing to publish -- envelope not written", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    (REPO_ROOT / check.ITEM7A_PUBLICATION).write_text(json.dumps(pub, indent=2) + "\n")
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
