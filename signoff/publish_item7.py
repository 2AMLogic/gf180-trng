#!/usr/bin/env python3
"""Publish a successful post-route functional run as T1 item 7's digital citation.

    python3 signoff/publish_item7.py                       # newest trng-top-post-route record
    python3 signoff/publish_item7.py sim/records/raw/<stem>   # a specific raw directory

Cold start (producer needs a cocotb-capable klt; see
sim/tb/trng-top-post-route/README.md):

    TRNG_POST_ROUTE_KLT=<venv>/bin/klt python3 sim/tb/trng-top-post-route/run_demo.py
    python3 signoff/publish_item7.py
    python3 signoff/check.py --write

What it does, and refuses to do:

* It copies the run's **native** ``gate_klt_response.json`` byte for byte to
  ``signoff/evidence/post-route/``. The `klt functional-verification` response
  is the envelope the pinned grader consumes; nothing is added to it or
  derived into it.
* That envelope carries no ``provenance`` block, so the manifest cannot pin a
  ``content_hash`` for it (the grader would render ``unverifiable_provenance``).
  Freshness is therefore carried by ``publication.json`` next to it, which pins
  the post-route netlist **and** the SDF by sha256 together with the raw
  evidence the verdict was derived from, and ``signoff/check.py`` re-verifies
  all of it on every run (``verify_item7_publication``).
* It refuses to publish unless the run's own verdict is a pass, both legs
  passed, the gate leg was SDF-annotated, every annotation control fired, and
  the netlist and SDF the run used still hash to what is on disk now.
* It never edits ``sim/records/``: those are append-only and only read.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402

REPO_ROOT = check.REPO_ROOT


def newest_raw_dir() -> Path:
    candidates = sorted((REPO_ROOT / "sim" / "records" / "raw").glob("*-trng-top-post-route-*"))
    if not candidates:
        raise SystemExit("publish_item7: no sim/records/raw/*-trng-top-post-route-* found")
    return candidates[-1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("raw_dir", nargs="?", type=Path)
    args = ap.parse_args()
    raw = (args.raw_dir or newest_raw_dir()).resolve()
    stem = raw.name

    failures: list[str] = []
    pub = {
        "schema": "gf180-trng/item7-publication/1",
        "record": f"sim/records/{stem}.md",
        "raw_dir": f"sim/records/raw/{stem}",
        "raw_sha256": {
            n: check.sha256_file(raw / n)
            for n in check.ITEM7_RAW_FILES
            if (raw / n).is_file()
        },
        "netlist": {"path": check.ITEM7_NETLIST},
        "sdf": {"path": check.ITEM7_SDF},
        "limits": check.ITEM7_LIMITS,
    }
    # The netlist/SDF the run used, as recorded by the run itself.
    record = (REPO_ROOT / pub["record"]).read_text()
    for key, field in (("netlist", "sha256"), ("sdf", "sdf_sha256")):
        line = next(
            (l.split(":", 1)[1].strip() for l in record.splitlines()
             if l.strip().startswith(f"{field}:")),
            None,
        )
        if not line:
            failures.append(f"{pub['record']}: records no {field}")
        else:
            pub[key]["sha256"] = "sha256:" + line
    envelope_src = raw / "gate_klt_response.json"
    if not envelope_src.is_file():
        failures.append(f"{raw}: no gate_klt_response.json")
    else:
        pub["envelope"] = {
            "file": check.ITEM7_ENVELOPE,
            "sha256": check.sha256_file(envelope_src),
        }
        failures += check.item7_problems(pub, json.loads(envelope_src.read_text()))
    if failures:
        print("publish_item7: refusing to publish -- nothing written", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    dest = REPO_ROOT / check.ITEM7_ENVELOPE
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(envelope_src, dest)
    (REPO_ROOT / check.ITEM7_PUBLICATION).write_text(json.dumps(pub, indent=2) + "\n")

    manifest = json.loads(check.MANIFEST.read_text())
    manifest["evidence"]["7.digital"] = {"file": check.ITEM7_ENVELOPE}
    manifest["evidence"] = dict(sorted(manifest["evidence"].items()))
    check.MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"publish_item7: published {stem} as 7.digital; now run signoff/check.py --write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
