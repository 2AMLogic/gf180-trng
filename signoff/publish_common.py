"""Steps shared by the `klt pex` publishers (publish_item7_analog.py, publish_combiner_sampler_pex.py).

Each publisher keeps only its fixture-specific data (pex arguments, coverage
exclusions, schema, paths, publication fields). The gates that decide what is
published as signoff evidence live here once, so a refusal added to one
publisher cannot silently miss the other:

* run_pex          -- one `klt pex` invocation, stdout to a response file
* load_envelope    -- run (or read) the response; a failed run publishes nothing
* envelope_refusals -- the pin / mismatch / missing-netlist refusals
* publish_envelope -- write the envelope, build and validate the publication,
                      restore the previous envelope on any failure, then write
                      the publication
* build_publication -- the publication dict common to the sidecar publishers

Every function takes `root` (the repository root) explicitly rather than
reading a module global, so each publisher's own REPO_ROOT stays the single
source of truth for where it writes.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402


def fail(header: str, lines: list[str]) -> int:
    """Print `header` and one bullet per line to stderr; the caller returns this exit status."""
    print(header, file=sys.stderr)
    for f in lines:
        print(f"  - {f}", file=sys.stderr)
    return 1


def run_pex(root: Path, scratch: Path, pex_args: list[str], backend: str | None, tag: str) -> Path:
    scratch.mkdir(parents=True, exist_ok=True)
    out = scratch / "klt_pex_response.json"
    klt = shlex.split(os.environ.get("KLT", "klt"))
    argv = [*klt, *pex_args, *(["--backend", backend] if backend else [])]
    print(f"{tag}: {shlex.join(argv)}", file=sys.stderr)
    with out.open("w") as fh:
        subprocess.run(argv, cwd=root, stdout=fh, check=True)
    return out


def load_envelope(path: Path | None, run: Callable[[], Path], tag: str) -> tuple[bytes, dict] | None:
    """The raw response bytes and their parse, from `path` or a fresh `run()`; None if klt pex failed."""
    try:
        src = path.resolve() if path else run()
    except subprocess.CalledProcessError as exc:
        # klt pex prints its error envelope on stdout/stderr; nothing is published.
        print(f"{tag}: klt pex failed (exit {exc.returncode}); nothing published", file=sys.stderr)
        return None
    raw = src.read_bytes()
    return raw, json.loads(raw)


def envelope_refusals(root: Path, envelope: dict, netlist_rel: str) -> list[str]:
    refusals: list[str] = []
    build = (envelope.get("provenance") or {}).get("klt_version")
    if build != check.KLT_PIN:
        refusals.append(f"response is from klt {build!r}, not the producer pin {check.KLT_PIN}")
    for key in ("pin_count_mismatch", "flat_dut_mismatch"):
        if envelope.get(key) is not None:
            refusals.append(f"klt pex reports {key}: {envelope[key]!r}")
    if not (root / netlist_rel).is_file():
        refusals.append(f"{netlist_rel} is missing (the run's -o netlist)")
    return refusals


def publish_envelope(
    refusing: str,
    dest: Path,
    raw: bytes,
    build_pub: Callable[[str], dict],
    validate: Callable[[dict], list[str]],
    allow_incomplete: bool,
    pub_path: Path,
) -> dict | None:
    """Write `raw` to `dest`, then build (from the written file's sha256) and validate the publication.

    On any failure the previous envelope is restored (or the new one removed),
    `<refusing> -- envelope not written` and the failures go to stderr, and
    None is returned. Otherwise the publication is written to `pub_path` and
    returned. A publication whose verdict is `incomplete` fails unless
    `allow_incomplete`.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    previous = dest.read_bytes() if dest.is_file() else None
    dest.write_bytes(raw)
    try:
        pub = build_pub(check.sha256_file(dest))
    except Exception as exc:  # noqa: BLE001 -- restore, then report
        pub, failures = None, [f"{type(exc).__name__}: {exc}"]
    else:
        failures = validate(pub)
        verdict = pub.get("verdict")
        if verdict and verdict["verdict"] == "incomplete" and not allow_incomplete:
            failures.append(
                f"verdict is incomplete ({verdict['counts']['unmeasured']} declared "
                f"row(s) unmeasured); re-run, or pass --allow-incomplete to publish it as such"
            )
    if failures:
        if previous is None:
            dest.unlink()
        else:
            dest.write_bytes(previous)
        fail(f"{refusing} -- envelope not written", failures)
        return None
    pub_path.write_text(json.dumps(pub, indent=2) + "\n")
    return pub


def build_publication(
    root: Path,
    envelope: dict,
    raw_sha: str,
    backend: str | None,
    *,
    schema: str,
    scope: str,
    pex_args: list[str],
    source_sha256: dict,
    inputs: list[str],
    port_map,
    exclusions: list[str],
    envelope_file: str,
    request_rel: str,
) -> dict:
    request = json.loads((root / request_rel).read_text())
    prov = envelope.get("provenance") or {}
    bias = envelope.get("body_bias") or {}
    return {
        "schema": schema,
        "scope": scope,
        "producer": "klt " + shlex.join(pex_args),
        "producer_build": prov.get("klt_version"),
        "klayout_build": prov.get("klayout_version"),
        "pdk": prov.get("pdk"),
        "deck": prov.get("deck"),
        "backend_requested": backend,
        "layout_content_hash": check.pinned_input_hash(envelope),
        "source_sha256": source_sha256,
        "inputs_sha256": {rel: check.sha256_file(root / rel) for rel in inputs},
        "port_map": port_map,
        "body_bias_status": bias.get("status"),
        "body_bias_unbiased_device_count": bias.get("unbiased_device_count"),
        "coverage_exclusions": exclusions,
        "verdict": check.combiner_sampler_verdict(envelope, request),
        "envelope": {"file": envelope_file, "sha256": raw_sha},
    }
