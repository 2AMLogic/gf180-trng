"""Stored evidence: raw run output goes to the artifact store, git keeps a manifest.

``run_corners.py`` stages each point's raw output (decks, logs, snapshots) in
a git-ignored scratch directory, stores it with ``klt artifact put`` and
commits only ``manifests/artifacts/<stem>.manifest.json`` plus the record
``.md``, whose ``stored_evidence`` table lists name, size and sha256 per
object. See ``spec/decision-records/DR-0032-*`` and ``sim/README.md``.

Fail closed: if ``$KLT_ARTIFACT_BROKER`` is unset, ``klt`` lacks
``artifact put`` or the broker cannot be reached, nothing is published under
``manifests/`` or ``sim/records/`` and the staged bytes are kept. There is no
fallback that commits the bytes instead.

The broker URL comes only from the environment and is never written into the
repository or echoed in an error message.

Stdlib only; the manifest schema checks here are shared with
``sim/tools/verify_artifact_manifests.py``.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path, PurePosixPath

from .report import sha256_file

BROKER_ENV = "KLT_ARTIFACT_BROKER"
MANIFEST_SUFFIX = ".manifest.json"
MANIFEST_SUBDIR = "manifests/artifacts"
URI_SCHEME = "artifact:"
SCHEMA_VERSION = 1
STAGE_DIRNAME = ".stage"

#: Strings that name a storage location; none may appear anywhere in
#: ``manifests/``.
FORBIDDEN_MARKERS = ("s3://", "arn:aws:")

_HEX = set("0123456789abcdef")
_PUT_TIMEOUT_S = 600

#: One stored object as the record table lists it: (name, size, sha256).
Entry = tuple[str, int, str]


class EvidenceStoreError(RuntimeError):
    """Evidence could not be stored; nothing was published."""


def _scrub(text: str) -> str:
    """Drop the broker URL from tool output before it reaches a message."""
    broker = os.environ.get(BROKER_ENV, "").strip()
    return text.replace(broker, "<broker>") if broker else text


def _klt() -> str:
    klt = shutil.which("klt")
    if klt is None:
        raise EvidenceStoreError("`klt` is not on PATH; cannot store evidence")
    return klt


def preflight() -> None:
    """Refuse before any simulation if evidence could not be stored.

    Tests for the capability (``klt artifact put --help``), not for a klt
    version. Broker reachability is only known at put time; a put failure is
    just as fatal and equally leaves nothing published.
    """
    if not os.environ.get(BROKER_ENV, "").strip():
        raise EvidenceStoreError(
            f"${BROKER_ENV} is unset; evidence is stored through the artifact "
            "broker and is never committed as bytes. Run on a fleet worker, or "
            "pass --no-write for a run that records nothing."
        )
    klt = _klt()
    try:
        proc = subprocess.run(
            [klt, "artifact", "put", "--help"],
            capture_output=True, text=True, check=False, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise EvidenceStoreError(f"cannot run `klt artifact put --help`: {exc}") from exc
    if proc.returncode != 0:
        raise EvidenceStoreError(
            "this `klt` has no `artifact put` verb (needs klayout-tools with the "
            "artifact client); refusing to commit evidence bytes instead"
        )


def ensure_stage_ignored(stage_root: Path, repo_root: Path) -> None:
    """Refuse a staging directory git would track.

    A stage root outside the checkout is fine. Inside it, git must say the
    path is ignored; any other answer (not ignored, or git cannot tell) is a
    refusal, so raw bytes can never be committed by accident.
    """
    try:
        stage_root.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return
    probe = stage_root / "x"
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "check-ignore", "-q", "--", str(probe)],
            capture_output=True, check=False,
        )
    except OSError as exc:
        raise EvidenceStoreError(f"cannot run git to check {stage_root} is ignored: {exc}") from exc
    if proc.returncode != 0:
        raise EvidenceStoreError(
            f"staging directory {stage_root} is inside the repository and not "
            "git-ignored; refusing to stage raw output where it could be committed"
        )


def manifest_path(manifests_dir: Path, stem: str) -> Path:
    return manifests_dir / f"{stem}{MANIFEST_SUFFIX}"


def validate_manifest(data: object) -> list[str]:
    """Schema problems of a parsed manifest; empty means well formed."""
    if not isinstance(data, dict):
        return ["manifest is not a JSON object"]
    problems: list[str] = []
    if data.get("schema_version") != SCHEMA_VERSION:
        problems.append(f"schema_version must be {SCHEMA_VERSION}, got {data.get('schema_version')!r}")
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        return problems + ["entries must be a non-empty list"]
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        where = f"entries[{index}]"
        if not isinstance(entry, dict):
            problems.append(f"{where}: not an object")
            continue
        name = entry.get("name")
        pure = PurePosixPath(name) if isinstance(name, str) else None
        if (pure is None or not name or pure.is_absolute() or ".." in pure.parts
                or "\\" in name):
            problems.append(f"{where}: name {name!r} must be a relative path without '..'")
        elif name in seen:
            problems.append(f"{where}: duplicate name {name!r}")
        else:
            seen.add(name)
        sha = entry.get("sha256")
        if not (isinstance(sha, str) and len(sha) == 64 and set(sha) <= _HEX):
            problems.append(f"{where}: sha256 must be 64 lowercase hex digits")
            sha = None
        size = entry.get("size")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            problems.append(f"{where}: size must be a non-negative integer")
        if entry.get("kind") != "evidence":
            problems.append(f"{where}: kind must be 'evidence', got {entry.get('kind')!r}")
        uri = entry.get("uri")
        if not isinstance(uri, str) or not uri.startswith(URI_SCHEME):
            problems.append(f"{where}: uri must start with {URI_SCHEME!r}, got {uri!r}")
        elif sha and sha not in uri:
            problems.append(f"{where}: uri does not name the object's sha256")
        for marker in FORBIDDEN_MARKERS:
            if marker in json.dumps(entry):
                problems.append(f"{where}: contains a storage location ({marker!r})")
    return problems


def manifest_table(data: dict) -> list[Entry]:
    """The ``(name, size, sha256)`` rows of a validated manifest, by name."""
    return sorted((e["name"], e["size"], e["sha256"]) for e in data["entries"])


def load_manifest(path: Path) -> tuple[dict | None, list[str]]:
    """Parse and schema-check a manifest file."""
    try:
        data = json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return None, [f"cannot read manifest {path.name}: {exc}"]
    problems = validate_manifest(data)
    return (data if not problems else None), problems


def store_files(
    stage_dir: Path, names: list[str], dest: Path, *, repo_root: Path
) -> list[Entry]:
    """Store ``names`` (files under ``stage_dir``) and publish ``dest``.

    Each file is put with ``klt artifact put --name <name>`` into a partial
    manifest kept beside the staged bytes. Only once every put succeeded and
    the manifest matches the local files byte for byte is it published to
    ``dest`` (exclusive create; an existing manifest is never replaced).
    Returns the table rows. Raises ``EvidenceStoreError`` with nothing
    published otherwise; the staged bytes are always kept.
    """
    if dest.exists():
        raise EvidenceStoreError(f"{dest} already exists; manifests are append-only")
    if not names:
        raise EvidenceStoreError("no files to store")
    local: dict[str, Entry] = {}
    for name in names:
        path = stage_dir / name
        if not path.is_file():
            raise EvidenceStoreError(f"staged file {path} is missing")
        local[name] = (name, path.stat().st_size, sha256_file(path))
        if local[name][1] == 0:
            # The store takes 1 byte to 5 GiB per object; refuse before any
            # put so a half-stored point is never left behind.
            raise EvidenceStoreError(
                f"staged file {name} is empty and the artifact store cannot hold an "
                "empty object; nothing was stored"
            )

    klt = _klt()
    partial = stage_dir.parent / f"{dest.name}.partial"
    partial.unlink(missing_ok=True)
    for name in names:
        try:
            proc = subprocess.run(
                [klt, "artifact", "put", "--manifest", str(partial), "--kind", "evidence",
                 "--name", name, str(stage_dir / name)],
                cwd=repo_root, capture_output=True, text=True, check=False,
                timeout=_PUT_TIMEOUT_S,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise EvidenceStoreError(f"`klt artifact put` did not complete for {name}: {_scrub(str(exc))}") from exc
        if proc.returncode != 0:
            detail = _scrub((proc.stderr or proc.stdout or "").strip()) or "no output"
            raise EvidenceStoreError(
                f"`klt artifact put` failed for {name} (exit {proc.returncode}): {detail}"
            )

    data, problems = load_manifest(partial)
    if data is None:
        raise EvidenceStoreError("klt produced an invalid manifest: " + "; ".join(problems))
    table = manifest_table(data)
    expected = sorted(local.values())
    if table != expected:
        raise EvidenceStoreError(
            "stored manifest does not match the staged files "
            f"(manifest {table!r} != staged {expected!r}); not publishing"
        )
    text = partial.read_text()
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with dest.open("x") as handle:
            handle.write(text)
    except FileExistsError as exc:
        raise EvidenceStoreError(f"{dest} appeared while storing; manifests are append-only") from exc
    partial.unlink(missing_ok=True)
    return table


def unpublish(dest: Path) -> None:
    """Remove a manifest this process just published (record write failed)."""
    dest.unlink(missing_ok=True)
