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
   - an `lvs` envelope produced by klt 0.4.0 (which is what this repo's
     committed LVS reports are) leaves `provenance.input` null but still
     records the same digest as `environment.layout_sha256`, so the freshness
     claim is checkable here even though `klt signoff`'s own pin cannot reach
     it -- see signoff/README.md, "Item 4 is cited without a pin";
   - a `generic` envelope names its backing record in `source` and pins it in
     `provenance.input.content_hash`.

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
KLT_INSTALL_HINT = f'pip install "klayout-tools=={KLT_PIN}"'

#: `klt signoff` exit codes that mean "the grader ran fine".
#: 0 = every T1 item met; 3 = ran fine, not yet T1.
CLEAN_EXITS = (0, 3)


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
        if named:
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
