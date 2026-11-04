#!/usr/bin/env python3
"""Audited inventories behind T1 items 1, 2, 9 and 10 (both partitions).

`klt signoff` (>= 0.7.0, klayout-tools#2718/#2843) accepts a `kind: generic`
envelope for these four items when it is bound to an audited artifact: the
envelope declares `"t1_item": <n>`, names the artifact in
`provenance.input.path`, and the manifest pins the same `content_hash`. That
binding proves the artifact's *bytes* are fresh. It proves nothing about
whether the artifact is *true*, or whether a file the inventory is about has
moved underneath it.

So the artifacts bound here are inventories that carry the sha256 of every
member file, and this module is both their only writer and their verifier:

* `build_inventory` derives an inventory from the tree and **raises** when
  the audit fails (a schematic with no committed netlist, a layout directory
  with no stream, a testbench directory nobody classified, a gate command the
  named workflow does not run, ...). `check.py --write` therefore cannot
  write a `pass` envelope over a claim the tree does not support.
* `verify_item` rebuilds the same inventory from the live tree and compares
  it with the committed one, member by member, so a changed, deleted or newly
  added file fails with its name -- even though the inventory's own bytes did
  not change.

Pure stdlib; no klt, PDK, xschem, Yosys or ngspice. Nothing here runs a
simulation or a regeneration gate: the gates an inventory names are listed
with where they run, and the ones that need the PDK or an external tool are
marked as not run by `signoff/check.py`. `sim/` is only read.

What a `met` row therefore means: the inventoried files still hash to the
values pinned when the inventory was written, and the inventory's structural
audit (above) held on the tree it was written from. It does not mean the
named gates passed today.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CI_WORKFLOW = ".github/workflows/ci.yml"
NIGHTLY_WORKFLOW = ".github/workflows/pdk-nightly.yml"
SPEC = "spec/ratification-2026-07-31-target-spec.md"
PARTITIONS = ("analog", "digital")
ITEMS = (1, 2, 9, 10)

ITEM_TITLES = {
    1: "Design sources",
    2: "Layout",
    9: "Testbenches shipped",
    10: "Repo hygiene",
}
ITEM_SLUGS = {1: "design-sources", 2: "layout", 9: "testbenches", 10: "repo-hygiene"}


def inventory_path(item: int, partition: str) -> str:
    return f"signoff/evidence/inventory-{item}-{partition}.json"


def envelope_path(item: int, partition: str) -> str:
    return f"signoff/evidence/t1-item-{item}-{partition}.json"


def manifest_key(item: int, partition: str) -> str:
    return f"{item}.{partition}"


def all_units() -> list[tuple[int, str]]:
    return [(item, partition) for item in ITEMS for partition in PARTITIONS]


class AuditError(Exception):
    """The tree does not support the claim an inventory would make."""


# Deliberately not ``sim.harness.report.sha256_file``: this module audits the
# harness's own output, so its digest stays stdlib-only and independent of the
# code being checked. It returns the ``sha256:``-prefixed form the inventories pin.
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def dump_json(data: dict) -> str:
    return json.dumps(data, indent=2) + "\n"


def _member(root: Path, rel: str) -> dict:
    path = root / rel
    if not path.is_file():
        raise AuditError(f"{rel}: listed in an inventory but missing")
    return {"path": rel, "sha256": sha256_file(path)}


def _members(root: Path, rels) -> list[dict]:
    return [_member(root, rel) for rel in sorted(set(rels))]


def _glob(root: Path, *patterns: str) -> list[str]:
    found: set[str] = set()
    for pattern in patterns:
        found.update(
            p.relative_to(root).as_posix()
            for p in root.glob(pattern)
            if p.is_file() and "__pycache__" not in p.parts
        )
    return sorted(found)


def _read(root: Path, rel: str) -> str:
    try:
        return (root / rel).read_text()
    except OSError as exc:
        raise AuditError(f"{rel}: unreadable ({exc})") from exc


# --- gates --------------------------------------------------------------------

#: (command, workflow that runs it, text that must appear in that workflow,
#:  runs without the PDK/external tools, why not / how it runs, extra
#:  (file, text) pairs that must also appear). A gate named in an inventory is
#: audited against the workflow, so an inventory cannot cite a check nobody
#: runs.
_GATES: dict[str, tuple] = {
    "netlist-lint": (
        "python3 design/netlist.py --lint", CI_WORKFLOW, "run: npm run lint", True,
        "pure-Python scan of the schematics' text blocks; runs in the PR-blocking job",
        (("package.json", "design/netlist.py --lint"),),
    ),
    "netlist-check": (
        "python3 design/netlist.py --check", NIGHTLY_WORKFLOW,
        "run: python3 design/netlist.py --check", False,
        "needs xschem and the gf180mcu PDK; runs in pdk-nightly.yml, never in the PR-blocking job",
        (),
    ),
    "regmap-check": (
        "python3 design/interface/regmap.py --check", CI_WORKFLOW,
        "run: npm run check:regmap", True,
        "stdlib only; runs in the PR-blocking job",
        (("package.json", "design/interface/regmap.py --check"),),
    ),
    "synth-check": (
        "python3 design/synth.py --check", NIGHTLY_WORKFLOW,
        "run: python3 design/synth.py --check", False,
        "needs klt synthesize (Yosys); runs in pdk-nightly.yml, never in the PR-blocking job",
        (),
    ),
    "floorplan-netlist-check": (
        "python3 design/floorplan_netlist.py --check", CI_WORKFLOW,
        "run: npm run check:floorplan-netlist", True,
        "stdlib only; runs in the PR-blocking job",
        (("package.json", "design/floorplan_netlist.py --check"),),
    ),
    "layout-verify": (
        "python3 layout/verify.py --require-tools", NIGHTLY_WORKFLOW,
        "run: python3 layout/verify.py --require-tools", False,
        "needs klt and the PDK (DRC/LVS); the PR-blocking job runs `npm run check:layout`, "
        "which self-skips without them",
        (),
    ),
    "floorplan-verify": (
        "python3 layout/floorplan/floorplan.py --require-tools", NIGHTLY_WORKFLOW,
        "run: python3 layout/floorplan/floorplan.py --require-tools", False,
        "needs klt and the PDK; the PR-blocking job runs `npm run check:floorplan`, "
        "which self-skips without them",
        (),
    ),
    "digital-input-check": (
        "python3 layout/digital/build.py --check-input", CI_WORKFLOW,
        "run: npm run check:digital-input", True,
        "stdlib only; runs in the PR-blocking job",
        (("package.json", "layout/digital/build.py --check-input"),),
    ),
    "tap-distance-check": (
        "python3 layout/digital/tap_distance.py --check --require-tools", NIGHTLY_WORKFLOW,
        "run: python3 layout/digital/tap_distance.py --check --require-tools", False,
        "needs klt and the PDK; the PR-blocking job runs `npm run check:digital-tap-distance`, "
        "which self-skips without them",
        (),
    ),
    "harness-env": (
        "python3 sim/run_corners.py --check-env", NIGHTLY_WORKFLOW,
        "run: python3 sim/run_corners.py --check-env", False,
        "needs ngspice and the PDK; runs in pdk-nightly.yml",
        (),
    ),
    "selftest": (
        "sim/selftest.sh --require-pdk", NIGHTLY_WORKFLOW,
        "run: sim/selftest.sh --require-pdk", False,
        "needs ngspice and the PDK; runs in pdk-nightly.yml (the PR-blocking job runs "
        "`sim/selftest.sh`, which self-skips without them)",
        (),
    ),
    "unit-tests": (
        "npm run test", CI_WORKFLOW, "run: npm run test", True,
        "sim/tests, including the behavioural testbench drivers; those that need Icarus "
        "Verilog self-skip when it is absent",
        (),
    ),
    "signoff-check": (
        "python3 signoff/check.py --require-tools", CI_WORKFLOW,
        "run: python3 signoff/check.py --require-tools", True,
        "stdlib freshness gate plus the pinned klt grader; runs in the PR-blocking job",
        (),
    ),
}

_UNIT_GATES: dict[tuple[int, str], tuple[str, ...]] = {
    (1, "analog"): ("netlist-lint", "netlist-check"),
    (1, "digital"): ("regmap-check", "synth-check"),
    (2, "analog"): ("floorplan-netlist-check", "layout-verify", "floorplan-verify"),
    (2, "digital"): ("digital-input-check", "tap-distance-check"),
    (9, "analog"): ("harness-env", "selftest", "unit-tests"),
    (9, "digital"): ("unit-tests", "selftest"),
    (10, "analog"): ("signoff-check",),
    (10, "digital"): ("signoff-check",),
}


def _gate_records(root: Path, item: int, partition: str) -> list[dict]:
    out = []
    for name in _UNIT_GATES[(item, partition)]:
        command, workflow, needle, pdk_free, how, also = _GATES[name]
        if needle not in _read(root, workflow):
            raise AuditError(f"{workflow} does not contain {needle!r}; the gate {command!r} is not run there")
        for rel, text in also:
            if text not in _read(root, rel):
                raise AuditError(f"{rel} does not contain {text!r}; the gate {command!r} is not real")
        out.append(
            {
                "command": command,
                "runs_in": workflow,
                "runs_without_pdk_or_external_tools": pdk_free,
                "note": how,
            }
        )
    return out


def _gate_sentence(gates: list[dict]) -> str:
    """The summary clause naming what was and was not run here."""
    pdk = [g for g in gates if not g["runs_without_pdk_or_external_tools"]]
    free = [g for g in gates if g["runs_without_pdk_or_external_tools"]]
    parts = [
        "signoff/check.py re-derives the inventory from the live tree and runs none of the "
        "gates it names"
    ]
    if free:
        parts.append(
            "PDK-free gates run by the PR-blocking CI job: "
            + ", ".join(f"`{g['command']}`" for g in free)
        )
    if pdk:
        parts.append(
            "gates that need the PDK or an external tool and so are NOT run by the PDK-free "
            "job: "
            + ", ".join(f"`{g['command']}` ({g['runs_in'].rsplit('/', 1)[-1]})" for g in pdk)
        )
    return "; ".join(parts)


# --- item 1: design sources ---------------------------------------------------

def _netlist_top_cells(root: Path) -> list[str]:
    match = re.search(r"^TOP_CELLS = \(([^)]*)\)", _read(root, "design/netlist.py"), re.M)
    if not match:
        raise AuditError("design/netlist.py: no TOP_CELLS tuple")
    return sorted(re.findall(r'"([A-Za-z0-9_]+)"', match.group(1)))


def _build_item1_analog(root: Path) -> dict:
    schematics = _glob(root, "design/xschem/*.sch")
    symbols = _glob(root, "design/xschem/*.sym")
    netlists = _glob(root, "design/*.spice")
    if not schematics:
        raise AuditError("design/xschem/*.sch: no schematics found")
    sch_cells = {Path(p).stem for p in schematics}
    tops = _netlist_top_cells(root)
    missing_sch = sorted(set(tops) - sch_cells)
    if missing_sch:
        raise AuditError(f"design/netlist.py TOP_CELLS without a schematic: {missing_sch}")
    net_cells = sorted(Path(p).stem for p in netlists)
    if net_cells != tops:
        raise AuditError(
            "design/*.spice and design/netlist.py TOP_CELLS disagree: "
            f"netlist only {sorted(set(net_cells) - set(tops))}, "
            f"TOP_CELLS only {sorted(set(tops) - set(net_cells))}"
        )
    return {
        "schematics": _members(root, schematics),
        "symbols": _members(root, symbols),
        "derived_netlists": _members(root, netlists),
        "gate_scripts": _members(root, ["design/netlist.py"]),
    }


def _build_item1_digital(root: Path) -> dict:
    sources = _glob(
        root,
        "design/trng_top/trng_top.v",
        "design/conditioner/*.v",
        "design/health_test/*.v",
        "design/interface/trng_interface.v",
    )
    if not sources:
        raise AuditError("design/**/*.v: no RTL found")
    synth_src = _read(root, "design/synth.py")
    for rel in sources:
        if f'"{rel}"' not in synth_src:
            raise AuditError(f"{rel}: RTL source that design/synth.py does not synthesize")
    for listed in re.findall(r'"(design/[A-Za-z0-9_/]+\.v)"', synth_src):
        if listed.endswith(".synth.v"):
            continue
        if listed not in sources:
            raise AuditError(f"design/synth.py synthesizes {listed}, which the inventory missed")
    generated = _glob(
        root,
        "design/trng_top/*.synth.v",
        "design/trng_top/*.synth.json",
        "design/interface/trng_regmap.vh",
        "design/interface/REGMAP.md",
    )
    return {
        "rtl_sources": _members(root, sources),
        "generated": _members(root, generated),
        "gate_scripts": _members(root, ["design/synth.py", "design/interface/regmap.py"]),
    }


# --- item 2: layout -----------------------------------------------------------

def _layout_dir_files(root: Path, parent: str) -> list[str]:
    dirs = sorted(p for p in (root / parent).iterdir() if p.is_dir() and not p.name.startswith(("_", ".")))
    files: list[str] = []
    for d in dirs:
        rel = d.relative_to(root).as_posix()
        gds = _glob(root, f"{rel}/*.gds")
        if not gds:
            raise AuditError(f"{rel}/: layout directory without a committed GDS stream")
        files += gds + _glob(root, f"{rel}/*.spice", f"{rel}/build.py")
    return files


def _build_item2_analog(root: Path) -> dict:
    groups = {
        "cells": _layout_dir_files(root, "layout/cells"),
        "rings": _layout_dir_files(root, "layout/rings"),
        "blocks": _layout_dir_files(root, "layout/blocks"),
        "floorplan": _glob(
            root, "layout/floorplan/trng_floorplan.gds", "layout/floorplan/trng_floorplan.lvs_reference.spice"
        ),
    }
    for name, files in groups.items():
        if not files:
            raise AuditError(f"layout group {name!r} is empty")
    if not any(f.endswith(".gds") for f in groups["floorplan"]):
        raise AuditError("layout/floorplan/trng_floorplan.gds is missing")
    return {name: _members(root, files) for name, files in groups.items()}


def _build_item2_digital(root: Path) -> dict:
    gds = "layout/digital/trng_top.gds"
    if not (root / gds).is_file():
        raise AuditError(f"{gds} is missing")
    return {
        "stream": _members(root, [gds]),
        "implementation": _members(
            root,
            _glob(
                root,
                "layout/digital/trng_top.def",
                "layout/digital/trng_top.pnr.v",
                "layout/digital/trng_top.sdf",
                "layout/digital/trng_top.lvs_reference.spice",
                "layout/digital/build.py",
            ),
        ),
    }


#: The stream each partition's item 3/4 citations pin. verify_item holds the
#: inventory's member hash to the manifest pin, so the layout this item
#: describes is provably the one DRC/LVS graded.
PINNED_STREAMS = {
    "analog": ("layout/blocks/combiner_sampler/combiner_sampler.gds", ("3.analog", "4.analog")),
    "digital": ("layout/digital/trng_top.gds", ("3.digital",)),
}


# --- item 9: testbenches ------------------------------------------------------

#: `sim/tb/` directories whose bench is behavioural / RTL / gate-level (no
#: ngspice `.sp` deck). Every other directory is an analog bench and must ship
#: one; a new directory that is neither fails the audit.
DIGITAL_TESTBENCHES = frozenset(
    {
        "conditioned-stream-battery",
        "conditioner-crc32",
        "digital-sta-power",
        "health-test-fault-injection",
        "interface-regfile",
        "power-intent",
        "ring-liveness-fault-injection",
        "smoke-trng-top",
        "trng-top-crosscheck",
        "trng-top-post-route",
    }
)

#: Benches with no `tb.json` and no README of their own; each is driven or
#: documented by a named file that must reference the bench directory.
DOCUMENTED_BY = {
    "trng-top-crosscheck": "sim/tests/test_trng_top.py",
    "ro-ring5-starved-jitter-long-batch": "sim/characterization-starved-cell-jitter-energy.md",
}

RUN_CORNERS_DOC = "python3 sim/run_corners.py <testbench-slug>"


def _tb_invocation(root: Path, slug: str, files: list[str]) -> dict:
    tb_json = f"sim/tb/{slug}/tb.json"
    readme = f"sim/tb/{slug}/README.md"
    if tb_json in files:
        if RUN_CORNERS_DOC not in _read(root, "README.md"):
            raise AuditError(f"README.md does not document {RUN_CORNERS_DOC!r}")
        return {"command": f"python3 sim/run_corners.py {slug}", "documented_in": "README.md"}
    documenter = DOCUMENTED_BY.get(slug)
    if documenter is not None:
        if f"sim/tb/{slug}" not in _read(root, documenter):
            raise AuditError(f"{documenter} does not reference sim/tb/{slug}")
        return {"documented_in": documenter}
    if readme not in files:
        raise AuditError(f"sim/tb/{slug}/ has no tb.json, no README.md and no driver; no documented invocation")
    commands = [
        line.strip()
        for line in _read(root, readme).splitlines()
        if line.strip().startswith(("python3 sim/", "klt ", "bash sim/", "sim/"))
    ]
    if not commands:
        text = _read(root, readme)
        drivers = [d for d in re.findall(r"sim/tools/[A-Za-z0-9_]+\.py", text) if (root / d).is_file()]
        if not drivers:
            raise AuditError(f"{readme} documents no command line and names no sim/tools driver")
        return {"driver": drivers[0], "documented_in": readme}
    return {"command": commands[0].split("#")[0].strip(), "documented_in": readme}


def _pdk_pin(root: Path) -> dict:
    match = re.search(r'PDK_VERSION: "([0-9a-f]{40})"', _read(root, NIGHTLY_WORKFLOW))
    if not match:
        raise AuditError(f"{NIGHTLY_WORKFLOW}: no PDK_VERSION open_pdks commit pin")
    commit = match.group(1)
    if commit not in _read(root, "README.md"):
        raise AuditError(f"README.md does not state the open_pdks commit {commit} that {NIGHTLY_WORKFLOW} pins")
    try:
        variant = json.loads(_read(root, "sim/pdk.json"))["variant"]
    except (ValueError, KeyError) as exc:
        raise AuditError(f"sim/pdk.json: no readable variant ({exc})") from exc
    return {
        "open_pdks_commit": commit,
        "pinned_in": NIGHTLY_WORKFLOW,
        "stated_in": "README.md",
        "variant": variant,
        "variant_file": _member(root, "sim/pdk.json"),
    }


def _build_item9(root: Path, partition: str) -> dict:
    experiments: dict[str, dict] = {}
    for tb_dir in sorted(p for p in (root / "sim" / "tb").iterdir() if p.is_dir()):
        slug = tb_dir.name
        if slug.startswith((".", "__")):
            continue
        files = _glob(root, f"sim/tb/{slug}/**/*")
        has_deck = any(f.endswith(".sp") for f in files)
        is_digital = slug in DIGITAL_TESTBENCHES
        if is_digital and has_deck:
            raise AuditError(f"sim/tb/{slug}/: classified digital but ships an ngspice .sp deck")
        if not is_digital and not has_deck:
            raise AuditError(
                f"sim/tb/{slug}/: ships no ngspice .sp deck and is not classified in DIGITAL_TESTBENCHES"
            )
        if not files:
            raise AuditError(f"sim/tb/{slug}/: empty testbench directory")
        if (is_digital) != (partition == "digital"):
            continue
        experiments[slug] = {
            "invocation": _tb_invocation(root, slug, files),
            "files": _members(root, files),
        }
    if not experiments:
        raise AuditError(f"no {partition} testbenches found under sim/tb/")
    out = {
        "pdk": _pdk_pin(root),
        "experiments": experiments,
        "cold_start_docs": _members(root, ["README.md", "sim/README.md"]),
    }
    return out


# --- item 10: repo hygiene ----------------------------------------------------

#: Per partition: README text that documents how that half is reproduced, and
#: the CI text that shows the PR-blocking job exercises it.
_HYGIENE_REPRODUCTION = {
    "analog": (
        ("README.md", "python3 sim/run_corners.py"),
        ("README.md", "design/netlist.py --check"),
    ),
    "digital": (
        ("README.md", "design/interface/regmap.py --check"),
        ("README.md", "layout/digital/build.py --check-input"),
    ),
}
_HYGIENE_CI = {
    "analog": ("run: npm run lint", "run: npm run test"),
    "digital": ("run: npm run check:regmap", "run: npm run check:digital-input"),
}


def _build_item10(root: Path, partition: str) -> dict:
    license_text = _read(root, "LICENSE")
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        raise AuditError("LICENSE: not the Apache-2.0 text CLAUDE.md declares")
    readme = _read(root, "README.md")
    for needle in ("## Target specification", "## Layout", "### `sim/` harness", "### Checks", "## License"):
        if needle not in readme:
            raise AuditError(f"README.md: no {needle!r} section")
    if "spec/" not in readme:
        raise AuditError("README.md does not link the spec")
    if not re.search(r"<a id=\"[a-z0-9-]+\"></a>|^\| ", _read(root, SPEC), re.M):
        raise AuditError(f"{SPEC}: no spec table")
    for rel, text in _HYGIENE_REPRODUCTION[partition]:
        if text not in _read(root, rel):
            raise AuditError(f"{rel} does not document {text!r}")
    ci = _read(root, CI_WORKFLOW)
    for text in ("python3 signoff/check.py --require-tools", *_HYGIENE_CI[partition]):
        if text not in ci:
            raise AuditError(f"{CI_WORKFLOW}: does not run {text!r}")
    return {
        "assertions": [
            "LICENSE contains the Apache License, Version 2.0 text",
            "README.md has Target specification, Layout, sim/ harness, Checks and License sections "
            "and links spec/",
            f"{SPEC} carries the ratified specification table",
            "README.md documents how this partition is reproduced: "
            + ", ".join(f"`{t}`" for _r, t in _HYGIENE_REPRODUCTION[partition]),
            f"{CI_WORKFLOW} runs "
            + ", ".join(f"`{t.removeprefix('run: ')}`" for t in _HYGIENE_CI[partition])
            + " and `python3 signoff/check.py --require-tools`",
        ],
        "ci_status": "not captured: green CI is a property of a run, not of a file. This "
        "inventory hashes the workflow and names the command; whether the last run was green "
        "is not recorded here and is not part of what a `met` row asserts.",
        "files": _members(root, ["README.md", "LICENSE", SPEC, "sim/README.md", CI_WORKFLOW]),
    }


# --- assembly -----------------------------------------------------------------

def build_inventory(root: Path, item: int, partition: str) -> dict:
    if item == 1:
        body = _build_item1_analog(root) if partition == "analog" else _build_item1_digital(root)
    elif item == 2:
        body = _build_item2_analog(root) if partition == "analog" else _build_item2_digital(root)
        stream, pinned_by = PINNED_STREAMS[partition]
        body["pinned_by_citations"] = {"stream": _member(root, stream), "manifest_keys": list(pinned_by)}
    elif item == 9:
        body = _build_item9(root, partition)
    elif item == 10:
        body = _build_item10(root, partition)
    else:
        raise AuditError(f"no inventory for T1 item {item}")
    return {
        "inventory": ITEM_SLUGS[item],
        "t1_item": item,
        "partition": partition,
        "gates": _gate_records(root, item, partition),
        **body,
    }


def _count_members(node) -> int:
    members, _ = _member_map(node)
    return len(members)


def build_envelope(root: Path, item: int, partition: str) -> dict:
    """The generic envelope for (item, partition), derived from the inventory on disk."""
    artifact = inventory_path(item, partition)
    inventory = json.loads(_read(root, artifact))
    n = _count_members(inventory)
    if item == 1:
        what = (
            f"{n} design-source files ("
            + ("xschem schematics and symbols, their derived SPICE netlists" if partition == "analog"
               else "the RTL, its synthesized netlist and the generated register map")
            + ") with their regeneration gates"
        )
    elif item == 2:
        what = (
            f"{n} layout files ("
            + ("hand-drawn cell, ring and block streams with their reference netlists, and the composed floorplan stream"
               if partition == "analog"
               else "the placed-and-routed stream, DEF, as-built netlist, SDF and LVS reference")
            + "); the stream the item 3/4 citations pin ("
            + inventory["pinned_by_citations"]["stream"]["path"]
            + ") is a member and its hash is held to those pins"
        )
    elif item == 9:
        what = (
            f"{len(inventory['experiments'])} {partition} testbench directories under sim/tb/ "
            f"({n} files), each with its documented invocation, and the pinned PDK revision "
            f"(open_pdks {inventory['pdk']['open_pdks_commit'][:12]}, variant {inventory['pdk']['variant']})"
        )
    else:
        what = (
            f"{n} repo-hygiene files (README, LICENSE, the ratified spec table, sim/README.md, "
            "the CI workflow) with the stated assertions"
        )
    summary = (
        f"Audited inventory for T1 item {item} ({ITEM_TITLES[item]}), {partition} partition: {what}. "
        "Every member file is listed with its sha256, so the bound hash proves the inventory is "
        "current and the member hashes prove the files it describes are. "
        + _gate_sentence(inventory["gates"])
        + ". It does not run a simulation, a regeneration gate or DRC/LVS, and it does not "
        "re-derive any measured value."
    )
    if item == 10:
        summary += " CI status is not captured: the workflow file is hashed, whether its last run was green is not."
    return {
        "schema_version": 1,
        "kind": "generic",
        "t1_item": item,
        "status": "pass",
        "summary": summary,
        "source": artifact,
        "provenance": {
            "klt_version": None,
            "klayout_version": None,
            "pdk": None,
            "deck": None,
            "input": {
                "path": {"path": artifact, "scope": "repo"},
                "content_hash": sha256_file(root / artifact),
            },
        },
    }


def write_all(root: Path = REPO_ROOT) -> dict[tuple[int, str], str]:
    """Rebuild every inventory and envelope; returns {(item, partition): pinned content_hash}."""
    # Build everything before writing anything, so a failed audit leaves the
    # previous (honest) files untouched.
    inventories = {unit: build_inventory(root, *unit) for unit in all_units()}
    for unit, inventory in inventories.items():
        (root / inventory_path(*unit)).write_text(dump_json(inventory))
    pins = {}
    for unit in all_units():
        envelope = build_envelope(root, *unit)
        (root / envelope_path(*unit)).write_text(dump_json(envelope))
        pins[unit] = envelope["provenance"]["input"]["content_hash"]
    return pins


def _member_map(node) -> tuple[dict[str, str], object]:
    """Flatten {path,sha256} members to {where:path: hash}; return the rest."""
    members: dict[str, str] = {}

    def walk(value, where: str):
        if isinstance(value, dict):
            if set(value) == {"path", "sha256"}:
                members[f"{where}:{value['path']}"] = value["sha256"]
                return "<member>"
            return {k: walk(v, f"{where}/{k}") for k, v in value.items()}
        if isinstance(value, list):
            return [walk(v, where) for v in value]
        return value

    return members, walk(node, "")


def diff_inventory(committed: dict, rebuilt: dict) -> list[str]:
    old, old_rest = _member_map(committed)
    new, new_rest = _member_map(rebuilt)
    problems = []
    for key in sorted(old.keys() | new.keys()):
        path = key.partition(":")[2]
        if key not in new:
            problems.append(f"{path}: listed in the inventory but no longer in the tree")
        elif key not in old:
            problems.append(f"{path}: in the tree but absent from the inventory")
        elif old[key] != new[key]:
            problems.append(f"{path}: changed since it was inventoried")
    if not problems and old_rest != new_rest:
        problems.append("inventory metadata (gates, invocations, pdk pin, assertions) differs from the tree")
    return problems


def verify_item(root: Path, item: int, partition: str, manifest: dict) -> list[str]:
    """Every reason the (item, partition) citation no longer describes the tree."""
    key = manifest_key(item, partition)
    entry = (manifest.get("evidence") or {}).get(key)
    if not isinstance(entry, dict) or not entry.get("file") or not entry.get("content_hash"):
        return [f"manifest {key}: needs one {{file, content_hash}} citation"]
    problems: list[str] = []
    envelope_rel = envelope_path(item, partition)
    if entry["file"] != envelope_rel:
        problems.append(f"manifest {key}: cites {entry['file']!r}, expected {envelope_rel!r}")
    try:
        committed_env = json.loads(_read(root, entry["file"]))
    except (AuditError, ValueError) as exc:
        return problems + [f"{entry['file']}: unreadable ({exc})"]

    artifact = inventory_path(item, partition)
    if not (root / artifact).is_file():
        return problems + [f"{artifact}: bound inventory is missing"]
    actual = sha256_file(root / artifact)
    if entry["content_hash"] != actual:
        problems.append(f"manifest {key}: pins {entry['content_hash']} but {artifact} hashes to {actual}")
    if committed_env.get("kind") != "generic":
        problems.append(f"{entry['file']}: kind must be 'generic' (no native envelope backs item {item})")
    if committed_env.get("t1_item") != item or isinstance(committed_env.get("t1_item"), bool):
        problems.append(f"{entry['file']}: t1_item is {committed_env.get('t1_item')!r}, expected {item}")
    prov_input = (committed_env.get("provenance") or {}).get("input") or {}
    if committed_env.get("source") != artifact or prov_input.get("path") != {"path": artifact, "scope": "repo"}:
        problems.append(
            f"{entry['file']}: `source` and provenance.input.path must both name {artifact} "
            "(repo scope), so the grader and check.py read the same artifact"
        )
    if prov_input.get("content_hash") != actual:
        problems.append(f"{entry['file']}: provenance.input.content_hash is stale vs {artifact}")

    try:
        rebuilt = build_inventory(root, item, partition)
        committed = json.loads(_read(root, artifact))
        problems += [f"{artifact}: {p}" for p in diff_inventory(committed, rebuilt)]
        if item == 2:
            pinned = rebuilt["pinned_by_citations"]["stream"]
            for cite in rebuilt["pinned_by_citations"]["manifest_keys"]:
                cited = (manifest.get("evidence") or {}).get(cite) or {}
                if cited.get("content_hash") != pinned["sha256"]:
                    problems.append(
                        f"manifest {cite}: pins {cited.get('content_hash')} but {pinned['path']} "
                        f"hashes to {pinned['sha256']}; item 2 describes a different layout than "
                        "the one DRC/LVS graded"
                    )
        expected_env = build_envelope(root, item, partition)
    except (AuditError, ValueError) as exc:
        return problems + [f"item {key}: audit failed: {exc}"]
    if not problems and committed_env != expected_env:
        problems.append(
            f"{entry['file']}: differs from the envelope derived from the inventory "
            "(summary or provenance edited by hand)"
        )
    return problems
