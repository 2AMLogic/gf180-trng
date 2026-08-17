#!/usr/bin/env python3
"""Post-route gate-level re-run of the digital functional suite (#147).

    python3 sim/tb/trng-top-post-route/run_demo.py             # run, write a record
    python3 sim/tb/trng-top-post-route/run_demo.py --no-write   # run, print only
    python3 sim/tb/trng-top-post-route/run_demo.py --check-env  # report the environment only

This is the digital half of T1 item 7 ("post-layout verification"). It drives
``layout/digital/trng_top.pnr.v`` -- the **as-built** post-route netlist
``klt place-and-route`` wrote after CTS buffering and cell resizing (#111,
PR #172), not `klt synthesize`'s pre-CTS one -- through `klt
functional-verification` (cocotb 2.0 on Icarus Verilog 13.0) with
``layout/digital/trng_top.sdf``'s cell delays back-annotated by
``$sdf_annotate``, and compares every top-level output, every cycle, against
``design/trng_top/trng_top.py``'s behavioural model: the same model the five
``level: behavioral`` records this re-runs were produced from.

Three files, three jobs:

* ``scenarios.py`` -- the per-cycle stimulus, one scenario per behavioural
  suite member (plus the annotation control). No simulator, no netlist.
* ``post_route_tb.py`` -- the cocotb regression: drives the DUT, steps the
  model, compares, writes ``comparison.json``.
* this file -- environment checks, the `klt` request, and the append-only
  evidence record. It makes no claim the two files above did not produce.

The environment this needs, and why it is not just "klt"
--------------------------------------------------------
``klt functional-verification`` invokes cocotb's first-party Python
``Runner``, so it has to run on an interpreter that can *load* cocotb's
compiled VPI module -- a stricter requirement than being able to ``import
cocotb``. cocotb 2.0.1 ships no wheel for CPython 3.14, and a cp312 wheel
force-installed under 3.14 (which is what a `pipx install klayout-tools` on a
3.14 host can end up with) fails at simulator run time, inside `vvp`, with
``Unexpected sys.executable value`` and no ``results.xml`` -- surfacing four
layers up as `klt`'s generic "the regression did not run to completion".
:func:`probe_klt` therefore checks the *wheel ABI tag* against the
interpreter, and this script refuses to run rather than reporting an
environment failure as a verification result. See
:data:`PROVISIONING_HINT` for the one command that fixes it, and this
directory's README for the whole story.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TB_DIR = Path(__file__).resolve().parent
SIM_DIR = TB_DIR.parents[1]
REPO_ROOT = SIM_DIR.parent

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(TB_DIR))

from harness import report  # noqa: E402
from layout._klt import klt_version, resolve_pdk  # noqa: E402

import scenarios  # noqa: E402

SLUG = "trng-top-post-route"

NETLIST_PATH = REPO_ROOT / "layout" / "digital" / "trng_top.pnr.v"
SDF_PATH = REPO_ROOT / "layout" / "digital" / "trng_top.sdf"
SDF_REPORT_PATH = REPO_ROOT / "layout" / "digital" / "reports" / "sdf_export.json"
MODEL_PATH = REPO_ROOT / "design" / "trng_top" / "trng_top.py"
RTL_PATH = REPO_ROOT / "design" / "trng_top" / "trng_top.v"

#: The RTL the netlist was synthesized from -- the reference leg's sources,
#: in the same order `design/synth.py` hands them to `klt synthesize`.
RTL_SOURCES = (
    RTL_PATH,
    REPO_ROOT / "design" / "conditioner" / "crc32_conditioner.v",
    REPO_ROOT / "design" / "health_test" / "rct_apt.v",
    REPO_ROOT / "design" / "health_test" / "ring_liveness.v",
    REPO_ROOT / "design" / "interface" / "trng_interface.v",
)
#: `trng_interface.v` includes the generated register-map header from here.
RTL_INCLUDES = (REPO_ROOT / "design" / "interface",)

CELL_LIBRARY = "gf180mcu_fd_sc_mcu9t5v0"

#: Scratch directory for the request and everything `klt` writes next to it.
#: Under `sim/.work/`, which `.gitignore` covers -- nothing here is evidence
#: until this script copies it into the record's own raw directory.
WORK_DIR = SIM_DIR / ".work" / SLUG

#: cocotb's own seeded `random` state. Pinned so the run is reproducible even
#: though no scenario here draws from it (every bit of stimulus comes from
#: `scenarios.py`'s SHA-256 counter-mode generators, at fixed seeds).
COCOTB_RANDOM_SEED = 1

EXIT_OK = 0
EXIT_ENVIRONMENT = 3
EXIT_FLOW_FAILURE = 4
EXIT_COMPARISON_FAILED = 5

PROVISIONING_HINT = (
    "provision a cocotb-capable klt once, machine-locally:\n"
    "    python3.13 -m venv ~/.local/venvs/klt-cocotb\n"
    "    ~/.local/venvs/klt-cocotb/bin/pip install 'cocotb==2.0.1' \\\n"
    "        'klayout-tools @ git+https://github.com/2AMLogic/klayout-tools@<pinned-commit>'\n"
    "then re-run with TRNG_POST_ROUTE_KLT=~/.local/venvs/klt-cocotb/bin/klt "
    "(the <pinned-commit> is the one .github/workflows/pdk-nightly.yml installs)."
)


class FlowError(RuntimeError):
    """The run could not produce a trustworthy verdict at all."""


# --------------------------------------------------------------------------- #
# environment
# --------------------------------------------------------------------------- #


def _console_script_interpreter(binary: Path) -> str | None:
    """The interpreter a console script's shebang names.

    Splits the shebang on whitespace: pipx writes ``#!<venv>/bin/python -E``,
    and treating the whole tail as one path is how a provenance probe silently
    returns "unknown" on every pipx install (which is what
    ``layout/_klt.klt_origin()`` does today -- noted here rather than fixed,
    since changing that helper would restate every committed
    ``layout/reports/`` and ``design/`` report's provenance field and belongs
    in its own change).
    """
    try:
        first_line = binary.resolve().read_text(errors="replace").split("\n", 1)[0]
    except OSError:
        return None
    if not first_line.startswith("#!"):
        return None
    parts = first_line[2:].strip().split()
    return parts[0] if parts else None


_PROBE = r"""
import importlib.metadata as m, json, sys
out = {"python": ".".join(str(v) for v in sys.version_info[:3]),
       "abi_tag": "cp%d%d" % sys.version_info[:2]}
try:
    dist = m.distribution("cocotb")
    out["cocotb"] = dist.version
    wheel = dist.read_text("WHEEL") or ""
    tags = [l.split(":", 1)[1].strip() for l in wheel.splitlines()
            if l.startswith("Tag:")]
    out["cocotb_wheel_tags"] = tags
except Exception as exc:
    out["cocotb"] = None
    out["cocotb_error"] = repr(exc)
try:
    dist = m.distribution("klayout-tools")
    out["klt_version"] = dist.version
    url = dist.read_text("direct_url.json")
    out["klt_commit"] = (json.loads(url).get("vcs_info") or {}).get("commit_id") if url else None
except Exception:
    out["klt_version"] = None
    out["klt_commit"] = None
print(json.dumps(out))
"""


def probe_klt(binary: Path) -> dict:
    """Report whether ``binary`` can actually run a cocotb regression.

    ``usable`` is False -- with a ``reason`` -- when cocotb is missing, or
    when its wheel's ABI tag does not match the interpreter's. The ABI check
    is the load-bearing one: an ABI-mismatched cocotb imports fine and only
    fails inside `vvp`, where the symptom is an empty ``results.xml``.
    """
    info: dict = {"klt": str(binary)}
    interpreter = _console_script_interpreter(binary)
    if interpreter is None:
        return {**info, "usable": False, "reason": "could not read the klt console script"}
    info["interpreter"] = interpreter
    try:
        done = subprocess.run(
            [interpreter, "-c", _PROBE], capture_output=True, text=True, timeout=120
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {**info, "usable": False, "reason": f"could not run {interpreter}: {exc}"}
    if done.returncode != 0:
        return {**info, "usable": False, "reason": f"probe exited {done.returncode}"}
    try:
        info.update(json.loads(done.stdout.strip()))
    except json.JSONDecodeError:
        return {**info, "usable": False, "reason": "probe wrote unparseable output"}

    if not info.get("cocotb"):
        return {**info, "usable": False, "reason": "cocotb is not installed on this interpreter"}
    tags = info.get("cocotb_wheel_tags") or []
    abi = info["abi_tag"]
    if tags and not any(abi in tag for tag in tags):
        return {
            **info,
            "usable": False,
            "reason": (
                f"cocotb {info['cocotb']} is installed as a {', '.join(tags)} wheel on "
                f"CPython {info['python']} ({abi}) -- its VPI module loads the wrong "
                "libpython and the regression never writes results.xml"
            ),
        }
    return {**info, "usable": True, "reason": None}


def klt_candidates() -> list[Path]:
    """Every `klt` worth probing, most explicit first."""
    out: list[Path] = []
    override = os.environ.get("TRNG_POST_ROUTE_KLT")
    if override:
        out.append(Path(os.path.expanduser(override)))
    on_path = shutil.which("klt")
    if on_path:
        out.append(Path(on_path))
    default_venv = Path.home() / ".local" / "venvs" / "klt-cocotb" / "bin" / "klt"
    out.append(default_venv)
    seen: set[str] = set()
    unique = []
    for entry in out:
        key = str(entry)
        if key not in seen and entry.exists():
            seen.add(key)
            unique.append(entry)
    return unique


def iverilog_version() -> str | None:
    if shutil.which("iverilog") is None:
        return None
    try:
        done = subprocess.run(
            ["iverilog", "-V"], capture_output=True, text=True, timeout=60
        )
    except (OSError, subprocess.SubprocessError):
        return None
    first = (done.stdout or done.stderr).strip().split("\n", 1)[0]
    return first or None


def library_verilog(pdk) -> list[Path]:
    """The cell library's timing (non-``FUNCTIONAL``) Verilog models plus the
    UDP primitives they instantiate."""
    verilog_dir = pdk.path / "libs.ref" / CELL_LIBRARY / "verilog"
    return [verilog_dir / f"{CELL_LIBRARY}.v", verilog_dir / "primitives.v"]


def check_environment() -> tuple[dict, list[str]]:
    """Return ``(environment, problems)``. Never raises."""
    problems: list[str] = []
    env: dict = {
        "python": f"{platform.python_version()} ({platform.python_implementation()})",
        "platform": platform.platform(),
        "iverilog": iverilog_version(),
        "klt_on_path": klt_version(),
        "klt_candidates": [],
    }

    for path in (NETLIST_PATH, SDF_PATH, SDF_REPORT_PATH):
        if not path.is_file():
            problems.append(
                f"{path.relative_to(REPO_ROOT)} is missing -- run "
                "`python3 layout/digital/build.py` (#111) and "
                "`python3 layout/digital/gen_sdf.py` (#147) first"
            )

    pdk = resolve_pdk()
    if pdk is None:
        problems.append("no gf180mcu PDK install found (see sim/harness/pdk.py)")
        env["pdk"] = None
    else:
        env["pdk"] = {"name": pdk.variant, "path": str(pdk.path)}
        for path in library_verilog(pdk):
            if not path.is_file():
                problems.append(f"the resolved PDK has no {path}")

    if env["iverilog"] is None:
        problems.append("iverilog is not on PATH (Icarus Verilog 13.0 or newer)")
    else:
        match = re.search(r"(\d+)\.(\d+)", env["iverilog"])
        if match and int(match.group(1)) < 13:
            problems.append(
                f"iverilog is {env['iverilog']} -- SDF back-annotation of a "
                "post-route netlist needs 13.0 or newer (`-ginterconnect`)"
            )

    chosen = None
    for candidate in klt_candidates():
        info = probe_klt(candidate)
        env["klt_candidates"].append(info)
        if chosen is None and info["usable"]:
            chosen = info
    env["klt"] = chosen
    if chosen is None:
        problems.append(
            "no cocotb-capable `klt` found -- "
            + "; ".join(
                f"{c['klt']}: {c['reason']}"
                for c in env["klt_candidates"]
                if c.get("reason")
            )
            + ".\n"
            + PROVISIONING_HINT
        )
    return env, problems


# --------------------------------------------------------------------------- #
# the run
# --------------------------------------------------------------------------- #


def build_request(leg: str, names: list[str], request_path: Path) -> dict:
    """The `klt functional-verification` request for one leg.

    ``rtl`` and ``gate`` differ in exactly three fields -- the sources, the
    include path, and the presence of ``options.sdf``. Everything else
    (toplevel, testbench module, testcase list, timescale, cocotb seed) is
    identical by construction, so the two legs' results are comparable.
    """
    request: dict = {
        "engine": "icarus",
        "hdl_toplevel": "trng_top",
        "testbench": {
            "module": "post_route_tb",
            "search_path": str(TB_DIR),
            "testcase": [name.replace("-", "_") for name in names],
        },
        "options": {
            "timescale": ["1ns", "1ps"],
            "random_seed": COCOTB_RANDOM_SEED,
        },
    }
    if leg == "rtl":
        request["sources"] = [str(p) for p in RTL_SOURCES]
        request["options"]["includes"] = [str(p) for p in RTL_INCLUDES]
    else:
        pdk = resolve_pdk()
        request["sources"] = [
            str(NETLIST_PATH),
            *(str(p) for p in library_verilog(pdk)),
        ]
        request["options"]["sdf"] = {"file": str(SDF_PATH), "corner": "typ"}
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(json.dumps(request, indent=2) + "\n")
    return request


def leg_dir(leg: str) -> Path:
    return WORK_DIR / leg


def digest_transcripts(output_dir: Path) -> dict:
    """Collapse Icarus's transcripts into every *distinct* message and its count.

    The two transcripts are ~600 kB of two repeated messages (12 852
    ``sorry: ifnone with an edge-sensitive path is not supported`` from
    elaborating the cell library, 708 ``SDF WARNING: ... TIMINGCHECK not
    supported`` from annotation), so committing them verbatim as raw evidence
    would bury the one thing a reader needs -- *which* diagnostic classes
    fired and how often. Every distinct line survives here with its count;
    only the repetition is dropped, and the counts are what the record cites.
    """
    digest: dict[str, dict] = {}
    for name in ("build_icarus.log", "test_icarus.log"):
        path = output_dir / name
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        counts: dict[str, int] = {}
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            # Strip absolute paths and simulation timestamps so the same
            # message from two hosts collapses to one key.
            key = re.sub(r"/\S+/", "<path>/", stripped)
            key = re.sub(r"^\s*[\d.]+ns\s+", "", key)
            counts[key] = counts.get(key, 0) + 1
        digest[name] = {
            "total_lines": len(text.splitlines()),
            "distinct_messages": len(counts),
            "messages": dict(sorted(counts.items(), key=lambda kv: -kv[1])),
        }
    return digest


def run_leg(env: dict, leg: str, names: list[str], reference: Path | None) -> dict:
    """Run one leg of the regression.

    Returns ``{"leg", "request", "klt_response", "comparison",
    "comparison_path", "transcripts"}``. Raises :class:`FlowError` for
    anything that stops a trustworthy verdict -- a `klt` request error, an
    unparseable payload, or a run that wrote no comparison file. A *failing
    comparison* is not an error: it comes back as ``klt_response["status"] ==
    "fail"`` and is reported, because "the netlist differs from the RTL" is a
    result, not a broken run.
    """
    work = leg_dir(leg)
    work.mkdir(parents=True, exist_ok=True)
    request_path = work / "request.json"
    result_path = work / "comparison.json"
    if result_path.exists():
        result_path.unlink()
    request = build_request(leg, names, request_path)

    child_env = dict(os.environ)
    child_env["TRNG_POST_ROUTE_RESULT"] = str(result_path)
    child_env["TRNG_POST_ROUTE_LEG"] = leg
    if reference is not None:
        child_env["TRNG_POST_ROUTE_REFERENCE"] = str(reference)
    else:
        child_env.pop("TRNG_POST_ROUTE_REFERENCE", None)

    try:
        done = subprocess.run(
            [
                env["klt"]["klt"], "functional-verification",
                str(request_path), "--format", "json",
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=child_env,
            timeout=7200,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise FlowError(f"could not run klt functional-verification: {exc}") from exc

    payload_text = done.stdout.strip() or done.stderr.strip()
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise FlowError(
            f"[{leg}] klt functional-verification wrote unparseable output "
            f"(exit {done.returncode}): {payload_text[-2000:]}"
        ) from exc
    if "error" in payload:
        raise FlowError(
            f"[{leg}] klt functional-verification refused to produce a verdict: "
            f"{payload['error'].get('message')}"
        )
    if not result_path.is_file():
        raise FlowError(
            f"[{leg}] the regression produced no comparison file -- "
            f"expected {result_path}"
        )
    return {
        "leg": leg,
        "request": request,
        "klt_response": payload,
        "comparison": json.loads(result_path.read_text()),
        "comparison_path": result_path,
        "transcripts": digest_transcripts(work / ".klt" / "functional-verification"),
    }


# --------------------------------------------------------------------------- #
# the record
# --------------------------------------------------------------------------- #


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sdf_coverage() -> dict:
    return json.loads(SDF_REPORT_PATH.read_text())


#: Diagnostic classes counted out of the Icarus transcripts, so the record's
#: coverage statement is derived from the run rather than typed in. Each entry
#: is ``(key, substring)``; the count is the number of transcript lines
#: containing that substring, summed over both transcripts.
DIAGNOSTIC_CLASSES = (
    # Run time: Icarus parsed each of the SDF's TIMINGCHECK sections and
    # discarded it -- the setup/hold/width limits in the SDF are not applied.
    # The needle stops at "TIMINGCHECK" rather than the full "TIMINGCHECK not
    # supported.": `vvp`'s stderr and cocotb's own logger interleave without a
    # flush between them, and one of these lines is reliably cut mid-message by
    # a cocotb log line. Matching the short form counts all of them; matching
    # the long one silently loses the mangled line and reports 707 of 708.
    ("sdf_timingcheck_dropped", ": TIMINGCHECK"),
    # Elaboration: Icarus 13.0 implements no $setup/$hold/$width at all, so
    # the cell models' own timing checks are not applied either. Together with
    # the line above this means NO timing check of any kind ran.
    ("library_timing_checks_dropped", "Timing checks are not supported"),
    # Elaboration: the `ifnone`-qualified edge-sensitive specify paths
    # `xor`/`xnor`/`mux`/`addf`/`addh` use for their select inputs.
    ("ifnone_arcs_unsupported", "ifnone with an edge-sensitive path"),
)


def diagnostic_counts(leg: dict) -> dict[str, int]:
    """Count each :data:`DIAGNOSTIC_CLASSES` entry in one leg's transcripts."""
    counts = {key: 0 for key, _ in DIAGNOSTIC_CLASSES}
    for digest in leg["transcripts"].values():
        for message, occurrences in digest.get("messages", {}).items():
            for key, needle in DIAGNOSTIC_CLASSES:
                if needle in message:
                    counts[key] += occurrences
    return counts


def _rows(leg: dict) -> dict[str, dict]:
    """``{scenario name: result}`` for one leg, in scenario order."""
    scenario_results = leg["comparison"]["scenarios"]
    return {
        name: scenario_results[name]
        for name in scenarios.ALL_SCENARIOS
        if name in scenario_results
    }


def attribute(legs: dict[str, dict]) -> dict:
    """Attribute every model divergence to the RTL or to what came after it.

    For each scenario: does the post-route netlist's output trace equal the
    RTL's (``preserved``), and how many cycles does each leg differ from the
    behavioural model on (``gate_vs_model`` / ``rtl_vs_model``)? A divergence
    from the model that is present in *both* legs was already in the RTL and
    is not a P&R defect; one present only in the ``gate`` leg is.
    """
    gate, rtl = _rows(legs["gate"]), _rows(legs["rtl"])
    out: dict[str, dict] = {}
    for name in gate:
        g, r = gate[name], rtl.get(name, {})
        if g.get("kind") == "settle-sweep":
            out[name] = {"kind": "settle-sweep"}
            continue
        out[name] = {
            "kind": g.get("kind"),
            "cycles": g["cycles"],
            "preserved_by_pnr": g.get("dut_trace_sha256") == r.get("dut_trace_sha256"),
            "same_stimulus": g.get("model_trace_sha256") == r.get("model_trace_sha256"),
            "gate_vs_model": g["mismatch_cycles"],
            "rtl_vs_model": r.get("mismatch_cycles"),
            "gate_vs_probe": g.get("registered_handoff_probe_mismatch_cycles"),
            "rtl_vs_probe": r.get("registered_handoff_probe_mismatch_cycles"),
            "gate_unresolved": g["unresolved_cycles"],
            "rtl_unresolved": r.get("unresolved_cycles"),
        }
    return out


def verdict(legs: dict[str, dict]) -> dict:
    """The run's own pass/fail, derived from the artefacts rather than from a
    simulator's exit code -- the same discipline `klt
    functional-verification` applies one level down."""
    facts = attribute(legs)
    suite = [n for n in scenarios.SUITE_SCENARIOS if n in facts]
    # Every scenario whose stated expectation is "the two agree". The
    # annotation control is deliberately excluded: it samples the netlist
    # before its outputs can have settled, so it MUST differ from the
    # zero-delay reference -- that is what it is for, and folding it into a
    # blanket "everything matches" check would make the check unsatisfiable
    # and therefore meaningless.
    comparable = [
        n for n in facts
        if scenarios.SCENARIOS[n].expect == "match" and "preserved_by_pnr" in facts[n]
    ]
    checks = {
        "every_scenario_ran": sorted(facts) == sorted(
            n for n in scenarios.ALL_SCENARIOS
        ),
        "pnr_preserved_behaviour": bool(comparable)
        and all(facts[n]["preserved_by_pnr"] for n in comparable),
        "identical_stimulus_both_legs": all(
            facts[n]["same_stimulus"] for n in facts if "same_stimulus" in facts[n]
        ),
        "no_x_reached_a_pin": all(
            facts[n]["gate_unresolved"] == 0 for n in facts if "gate_unresolved" in facts[n]
        ),
        "sdf_annotation_applied": bool(
            legs["gate"]["klt_response"]["environment"]["sdf"]["annotated"]
        ),
        "annotation_control_fired": legs["gate"]["klt_response"]["status"] == "pass",
        # Any model divergence must appear identically in both legs -- that is
        # what makes it attributable to the RTL rather than to layout. Holds
        # trivially (0 == 0) when the three agree, which is the state since
        # #176 was fixed; it is the check that would catch a regression
        # introduced by a *future* re-place-and-route.
        "model_divergence_is_pre_existing": all(
            facts[n]["gate_vs_model"] == facts[n]["rtl_vs_model"]
            for n in suite
            if "gate_vs_model" in facts[n]
        ),
        "netlist_matches_behavioural_model": all(
            facts[n]["gate_vs_model"] == 0
            for n in suite
            if "gate_vs_model" in facts[n]
        ),
        # The registered-handoff probe delays `ht_startup_pass` and
        # `cond_word`/`cond_valid` by a cycle on top of whatever the committed
        # model already does. Since #176 the model registers both, so the probe
        # now double-delays them and MUST break the match on at least one
        # scenario. If it did not, the match above would be insensitive to a
        # cycle of skew on those handoffs -- i.e. this whole comparison would
        # not be able to see the defect #176 was.
        "handoff_skew_would_be_detected": any(
            facts[n].get("gate_vs_probe") for n in suite
        ),
    }
    return {"checks": checks, "pass": all(checks.values()), "facts": facts}


#: Every stimulus seed, per scenario -- `sim/README.md`'s "no seed, no
#: evidence" rule. The generators are SHA-256 counter mode over
#: `(label, seed)`, so the label is as load-bearing as the number.
STIMULUS_SEEDS = {
    "smoke": "n/a (the ten raw bits are read verbatim out of "
    "sim/records/2026-08-01-sampler-array-digitize-03.md; that record carries "
    "its own ngspice seeds)",
    "startup-and-regfile": "raw: biased_bits('interface-regfile-startup', 1); "
    "rings: healthy_ring_bits('interface-regfile-startup-ring{0,1}', 51/52)",
    "conditioner-blocks": "raw: biased_bits('conditioner-crc32-h050', 1); "
    "rings: healthy_ring_bits('conditioner-crc32-h050-ring{0,1}', 61/62)",
    "rct-stuck-output": "lead-in: biased_bits('stuck-output-lead-in', 20); "
    "fault: constant_bits(1) (unseeded by construction); "
    "rings: healthy_ring_bits('stuck-output-ring{0,1}', 71/72)",
    "ring1-stuck": "rings: healthy_ring_bits('ring{0,1}', 41/42) then "
    "stuck_ring_bits(frozen) + healthy_ring_bits('ring1-stuck-other', 141); "
    "raw: biased_bits('ring1-stuck-raw', 41)",
    "reg-read-walk": "raw: biased_bits('reg-read-walk', 7); "
    "rings: healthy_ring_bits('reg-read-walk-ring{0,1}', 81/82)",
    "reg-read-walk-early-sample": "same as reg-read-walk",
    "reg-read-walk-settle-sweep": "same as reg-read-walk",
}


def _frontmatter(stem: str, env: dict, legs: dict, git: dict, raw_files,
                 wall_s: float) -> str:
    sdf_report = _sdf_coverage()
    diagnostics = diagnostic_counts(legs["gate"])
    gate = legs["gate"]
    klt_response = gate["klt_response"]
    comparison = gate["comparison"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sim_ns = sum(t.get("sim_time_ns") or 0 for t in klt_response.get("tests", []))
    rows = _rows(gate)
    total_cycles = sum(
        row.get("cycles", 0) or row.get("cycles_per_pass", 0) * len(row.get("sweep", ()))
        for row in rows.values()
    )
    corner = sdf_report["pdk"]["corner"]
    klt = env["klt"]

    lines = [
        "---",
        f"record: {stem}",
        f"date: {now}",
        "status: valid",
        "",
        "level: gate-simulation (DR-0022, sibling of DR-0021's `level: gate`) "
        "-- a DYNAMIC simulation of the as-built post-route netlist with SDF "
        "cell delays back-annotated, compared cycle by cycle against a "
        "zero-delay RTL run of the same stimulus and against the behavioural "
        "model. Not `behavioral` (there is a netlist, a cell library and a "
        "liberty corner in the loop), not `transistor` (no device model is "
        "instantiated and ngspice is never invoked), and not `gate` (that "
        "level is static analysis and MAY be cited for timing closure; this "
        "one may not -- see Caveats)",
        "",
        "testbench:",
        f"  path: sim/tb/{SLUG}/run_demo.py",
        f"  sha: {report.blob_sha(REPO_ROOT, TB_DIR / 'run_demo.py')}",
        f"  cocotb_module: sim/tb/{SLUG}/post_route_tb.py",
        f"  cocotb_module_sha: {report.blob_sha(REPO_ROOT, TB_DIR / 'post_route_tb.py')}",
        f"  stimulus: sim/tb/{SLUG}/scenarios.py",
        f"  stimulus_sha: {report.blob_sha(REPO_ROOT, TB_DIR / 'scenarios.py')}",
        "netlist:",
        f"  path: {NETLIST_PATH.relative_to(REPO_ROOT)}",
        f"  sha: {report.blob_sha(REPO_ROOT, NETLIST_PATH)}",
        f"  sha256: {sha256_path(NETLIST_PATH)}",
        "  kind: >-",
        "    Post-route gate-level netlist -- klt place-and-route's own",
        "    write_verilog after clock-tree synthesis and cell resizing (#111,",
        "    PR #172), so the CTS buffers and the resized drive strengths are",
        "    in this simulation. NOT design/trng_top/trng_top.synth.v, which is",
        "    the pre-CTS mapped netlist.",
        "reference_leg:",
        "  what: >-",
        "    The same stimulus, the same testbench and the same comparison, run",
        "    against the RTL the netlist was synthesized from, zero-delay, no",
        "    SDF. Present so every difference can be attributed: a divergence",
        "    from the behavioural model that shows up in BOTH legs was already",
        "    in the RTL; one that shows up only in the netlist was introduced",
        "    by synthesis, CTS, resizing or routing.",
        "  sources:",
    ]
    for path in RTL_SOURCES:
        lines.append(
            f"    - {path.relative_to(REPO_ROOT)}  "
            f"sha:{report.blob_sha(REPO_ROOT, path)}"
        )
    lines += [
        "reference_model:",
        "  path: design/trng_top/trng_top.py",
        f"  sha: {report.blob_sha(REPO_ROOT, MODEL_PATH)}",
        "  note: >-",
        "    The behavioural model both legs are compared against every cycle:",
        "    the same model the five `level: behavioral` records this re-runs",
        "    were produced from.",
        "",
        "timing_annotation:",
        f"  sdf: {SDF_PATH.relative_to(REPO_ROOT)}",
        f"  sdf_sha: {report.blob_sha(REPO_ROOT, SDF_PATH)}",
        f"  sdf_sha256: {sdf_report['sdf_sha256']}",
        f"  generated_by: layout/digital/gen_sdf.py (engine: {sdf_report['engine']} "
        f"{sdf_report['engine_version']})",
        "  applied_by: Icarus $sdf_annotate, via klt functional-verification's "
        "options.sdf (generated klt_sdf_annotate elaboration root, "
        "-gspecify -ginterconnect -T typ)",
        f"  corner_selected: {klt_response['environment']['sdf']['corner']}",
        "  klt_reports_annotated: "
        + str(bool(klt_response["environment"]["sdf"]["annotated"])).lower(),
        "  models: >-",
        f"    {sdf_report['coverage']['cell_delay']}",
        "  omits: >-",
        f"    interconnect delay: {sdf_report['coverage']['interconnect_delay']};",
        "    setup/hold/width checking: NONE ran. Icarus 13.0 implements no SDF",
        f"    TIMINGCHECK annotation ({diagnostics['sdf_timingcheck_dropped']}",
        "    'TIMINGCHECK not supported' lines, one per flop) AND no",
        "    $setup/$hold/$width at all",
        f"    ({diagnostics['library_timing_checks_dropped']} 'Timing checks are",
        "    not supported' lines while elaborating the cell library), so this",
        "    run cannot detect a timing violation of any kind -- it models cell",
        "    delay and nothing else;",
        "    IOPATH arcs Icarus cannot elaborate: "
        f"{sdf_report['coverage']['icarus_unsupported_arcs_excluded']} dropped "
        f"({sdf_report['coverage']['icarus_unsupported_cells_dropped_entirely']}"
        " cells lost every arc);",
        "    no parasitic coupling, no IR drop, no on-chip variation, single",
        "    corner. Enumerated in full under Caveats.",
        "",
        f"repo_commit: {report.repo_commit_field(git)}",
        "",
        f"pdk: {sdf_report['pdk']['name']} @ open_pdks {env['pdk_version']}",
        "pdk.models:",
        f"  - libs.ref/{CELL_LIBRARY}/verilog/{CELL_LIBRARY}.v (timing models -- "
        "the non-FUNCTIONAL branch, the one that carries the specify blocks an "
        "SDF annotates)",
        f"  - libs.ref/{CELL_LIBRARY}/verilog/primitives.v (UDPs)",
        f"  - libs.ref/{CELL_LIBRARY}/lib/{CELL_LIBRARY}__{corner}.lib "
        "(read by layout/digital/gen_sdf.py -- the delays in the SDF above come "
        "from this deck)",
        "  - n/a: no ngspice device model card is read by this run at all",
        "",
        "tool:",
        '  ngspice: "n/a (gate-level record -- ngspice is not invoked; the '
        'delays come from the standard-cell liberty deck named above)"',
        f'  iverilog: "{env["iverilog"]}"',
        f'  cocotb: "{klt_response["environment"]["cocotb_version"]}"',
        f'  klt: "{klt["klt_version"]}" (commit {klt["klt_commit"]}, '
        f'interpreter CPython {klt["python"]})',
        f'  klt_binary: "{klt["klt"]}"',
        f'  openroad: "{sdf_report["engine_version"]}" (wrote the SDF, via '
        "layout/digital/gen_sdf.py)",
        f'  python: "{env["python"]}"',
        f"  platform: {env['platform']}",
        "",
        "corner:",
        f"  process: {corner.split('_')[0]} (from the liberty deck's own "
        "operating conditions, per DR-0021's rule for a gate-level corner -- "
        "not an ngspice model card)",
        f"  voltage: {corner.split('_')[2].replace('v', '.')} V (nominal 3.3 V, "
        "-10%; DR-0003's binding supply)",
        f"  temperature: {corner.split('_')[1].rstrip('C')}",
        f"  liberty: {CELL_LIBRARY}__{corner}.lib",
        "  interconnect: n/a -- no parasitics are extracted or annotated at "
        "all (see timing_annotation.omits), so there is no interconnect corner "
        "to name. DR-0021's `level: gate` records DO have one; this run's "
        "delays are cell-only.",
        "  note: >-",
        "    One corner, and it is the corner layout/digital/build.py placed and",
        "    routed against (layout/digital/README.md's 'Corners'). A",
        "    standard-cell library corner is a characterised .lib deck, not a",
        "    transistor model card: this record may be cited for what the",
        "    netlist DOES at that deck's delays, and for nothing about device",
        "    physics. The reference leg has no corner at all (zero-delay RTL).",
        "",
        "analysis:",
        "  type: post-route-gate-level-equivalence",
        f"  tstop: {sim_ns:.1f}ns simulated in the post-route leg across "
        f"{klt_response['test_count']} scenarios ({total_cycles} clock cycles "
        f"at {comparison['clock_period_ns']:g} ns)",
        "  tstep: n/a (event-driven digital simulation)",
        "  tmax: n/a (event-driven)",
        "  noise_params: n/a (no device noise in a gate-level run)",
        "  runs: 1 per leg (2 legs: rtl reference, gate post-route)",
        f"  drive_offset_ns: {comparison['drive_offset_ns']:g} (stimulus applied "
        "this long after each clock edge, clear of the flops' hold windows)",
        f"  sample_offset_ns: {comparison['default_sample_offset_ns']:g} "
        "(outputs compared this long after the stimulus changes, except where a "
        "scenario states otherwise)",
        "  compared_ports: " + ", ".join(comparison["output_ports"]),
        "",
        "seeds:",
        f"  cocotb_random_seed: {klt_response['environment']['random_seed']} "
        "(pinned; no scenario draws from cocotb's own generator)",
        "  stimulus:",
    ]
    for name in scenarios.ALL_SCENARIOS:
        lines.append(f"    {name}: {STIMULUS_SEEDS[name]}")
    lines += [
        "",
        "raw:",
        f"  path: sim/records/raw/{stem}/",
        "  files:",
    ]
    for name, digest in raw_files:
        lines.append(f"    - {name}  sha256:{digest}")
    lines.append(f"wall_time: {wall_s / 60:.1f}m")
    lines.append("---")
    return "\n".join(lines)


def _verdict_rows(legs: dict, facts: dict) -> list[str]:
    gate = _rows(legs["gate"])
    rows = []
    for name, row in gate.items():
        scenario = scenarios.SCENARIOS[name]
        fact = facts[name]
        if row.get("kind") == "settle-sweep":
            rows.append(
                f"| `{name}` | {scenario.counterpart} | "
                f"{len(row['sweep'])} x {row['cycles_per_pass']} | "
                f"settles by {row['smallest_clean_offset_ns']:g} ns, not by "
                f"{row['largest_dirty_offset_ns']:g} ns | — |"
            )
            continue
        preserved = "identical" if fact["preserved_by_pnr"] else "**DIFFERS**"
        if scenario.expect == "mismatch":
            model = (
                f"differs on {fact['gate_vs_model']} cycles (required — see the "
                "control below)"
            )
        elif fact["gate_vs_model"] == 0:
            model = "identical, every cycle"
        else:
            plural = "" if fact["gate_vs_model"] == 1 else "s"
            model = (
                f"differs on {fact['gate_vs_model']} cycle{plural} "
                f"(RTL leg: {fact['rtl_vs_model']})"
            )
        rows.append(
            f"| `{name}` | {scenario.counterpart} | {row['cycles']} | "
            f"{preserved} | {model} |"
        )
    return rows


def _body(env: dict, legs: dict, result: dict) -> str:
    sdf_report = _sdf_coverage()
    diagnostics = diagnostic_counts(legs["gate"])
    facts = result["facts"]
    gate = _rows(legs["gate"])
    rtl = _rows(legs["rtl"])
    sweep = gate.get("reg-read-walk-settle-sweep", {})
    control = gate.get("reg-read-walk-early-sample", {})
    rtl_control = rtl.get("reg-read-walk-early-sample", {})
    rct = gate.get("rct-stuck-output", {})
    ring = gate.get("ring1-stuck", {})
    cond = gate.get("conditioner-blocks", {})
    cond_reads = [r for r in cond.get("bus_reads", ()) if r["reg_addr"] == scenarios.DATA]
    suite = [n for n in scenarios.SUITE_SCENARIOS if n in gate]
    suite_cycles = sum(gate[n]["cycles"] for n in suite)
    suite_diverging = sum(facts[n]["gate_vs_model"] for n in suite)
    table = "\n".join(_verdict_rows(legs, facts))
    sweep_table = "\n".join(
        f"| {entry['sample_offset_ns']:g} | {entry['mismatch_cycles']} | "
        f"{entry['unresolved_cycles']} |"
        for entry in sweep.get("sweep", ())
    )
    checks = "\n".join(
        f"| {name.replace('_', ' ')} | {'yes' if value else '**NO**'} |"
        for name, value in result["checks"].items()
    )
    # Only the reads that actually returned a word: a trailing read of an
    # empty FIFO returns 0 by design and is not a conditioned word.
    cond_words = ", ".join(
        f"`0x{r['dut_reg_rdata']:08x}`" for r in cond_reads if r["dut_reg_rdata"]
    )
    model_words = ", ".join(
        f"`0x{r['model_reg_rdata']:08x}`" for r in cond_reads if r["model_reg_rdata"]
    )
    gate_response = legs["gate"]["klt_response"]

    return f"""
## Result

The verdict a post-layout re-run exists to deliver is the fourth column:
**does the as-built netlist still do what the RTL does, under the annotated
cell delays of the corner it was routed at?**

| Scenario | Behavioural counterpart | Cycles | Post-route netlist vs. RTL | Post-route netlist vs. behavioural model |
|---|---|---|---|---|
{table}

Every one of the checks this run derives from its own artefacts:

| Check | Holds |
|---|---|
{checks}

`klt functional-verification` reported `status: {gate_response['status']}` for the
post-route leg ({gate_response['passed_count']} passed,
{gate_response['failed_count']} failed, {gate_response['skipped_count']}
skipped) and `status: {legs['rtl']['klt_response']['status']}` for the RTL
reference leg.

Two latencies were measured on the netlist rather than inherited from the
model:

| Quantity | Post-route netlist | Behavioural model |
|---|---|---|
| `ht_alarm` rise after a stuck raw source (onset cycle {scenarios.RCT_ONSET_CYCLE}, C_RCT = {scenarios.C_RCT}) | cycle {rct.get('dut_first_alarm_cycle')} | cycle {rct.get('model_first_alarm_cycle')} |
| `ht_alarm` rise after ring 1 freezes (onset cycle {scenarios.RING_ONSET_CYCLE}, C_LIVE = {scenarios.C_LIVE}) | cycle {ring.get('dut_first_alarm_cycle')} | cycle {ring.get('model_first_alarm_cycle')} |

The conditioned words the `conditioner-blocks` scenario read back through
`DATA` were {cond_words} on the netlist, **bit-identical to both the RTL's and
the behavioural model's** ({model_words}). That is the claim that matters for
DR-0007's conditioner: mapping, CTS buffering, cell resizing and routing did
not change a single bit of the word the RTL computes, and the CRC-32 arithmetic
the behavioural records verified is the arithmetic the placed-and-routed gates
perform.

### The annotation is in the loop (control)

A gate-level run whose SDF silently failed to apply looks exactly like a green
zero-delay run, so this record does not take the annotation on trust — twice
over. `klt` scans both Icarus transcripts itself before reporting
`environment.sdf.annotated: {str(bool(gate_response['environment']['sdf']['annotated'])).lower()}`.
Independently of that, `reg-read-walk-early-sample` re-runs the identical
stimulus sampled {control.get('sample_offset_ns')} ns after the inputs change
instead of {legs['gate']['comparison']['default_sample_offset_ns']:g} ns:

- on the **post-route netlist** it differs from the settled trace, and from
  the model on {control.get('mismatch_cycles')} of {control.get('cycles')}
  cycles — annotated cell delay means the outputs cannot possibly be settled
  0.1 ns after their inputs move;
- on the **zero-delay RTL** the same control differs on
  {rtl_control.get('mismatch_cycles')} cycles, because there is no delay to
  wait for.

The same control returning opposite answers on the two legs is what rules out
"the comparison is just noisy". The settle sweep puts a number on it — the
same stimulus compared at a ladder of sampling offsets on the netlist:

| Sampling offset (ns after the stimulus changes) | Cycles differing | Cycles with `x`/`z` |
|---|---|---|
{sweep_table}

So the register-read path is fully settled by
**{sweep.get('smallest_clean_offset_ns')} ns** and is not settled at
{sweep.get('largest_dirty_offset_ns')} ns, under cell delays alone. That is a
**lower bound** on this netlist's combinational delay on that path, not an
Fmax claim: interconnect delay is not modelled at all (see Caveats), so the
real path is slower than this by whatever its routing contributes.

## Pre/post comparison: did any behavioural conclusion change?

**No behavioural-level conclusion was invalidated.** All three descriptions of
the digital partition — the post-route netlist under annotated delay, the RTL
it was synthesized from, and the behavioural model the five
`level: behavioral` records were produced from — agree cycle for cycle on
every one of the {len(suite)} suite scenarios, {suite_cycles} cycles, with
{suite_diverging} cycles differing.

- **Synthesis, CTS, resizing and routing changed nothing.** The netlist's
  complete output trace (SHA-256 over every compared port on every cycle) is
  *identical* to the RTL's. That is the item-7 verdict, and it is exact over
  all {suite_cycles} cycles rather than over a sampled subset.
- **The behavioural conclusions transfer.** The conditioner's CRC-32
  arithmetic, the DR-0002 latch/gate/flush behaviour, the register map's
  read/write semantics, the RCT stuck-source detection latency and the
  DR-0016 per-ring watchdog all reproduce bit-exactly on the as-built netlist.
  Nothing needed a correction and **no record is superseded by this one**:
  they remain valid at their own level, and this is a second, independent
  level of evidence for the same behaviour.
- **Extended, not changed.** Two detection latencies the behavioural records
  could only state in *samples of the model* are now also measured in *clock
  cycles of the netlist*, and agree (the table above).
- **This agreement is not free, and it is one commit old.** The first run of
  this testbench found the netlist and the RTL agreeing with each other and
  **both disagreeing with the behavioural model** on 270 of {suite_cycles}
  cycles — because `trng_top.py`'s `TopLevel.step` passed two cross-block
  handoffs (`ht_startup_pass`, and `cond_word`/`cond_valid`) combinationally
  where `rct_apt.v` and `crc32_conditioner.v` register them, un-gating the
  conditioned path one raw sample early and so shifting the first 256-bit
  conditioner block by one bit. Identical counts in both legs is what
  attributed it to the RTL rather than to layout; a probe that registered
  exactly those two handoffs and nothing else brought the divergence to zero,
  which identified the cause. Filed as **#176** and fixed in **#178** before
  this record was written, so the numbers above are against the corrected
  model. The probe survives in `model_probe.py` as a *sensitivity* check
  (`handoff_skew_would_be_detected` above): applying it now double-delays
  those handoffs and must break the match, which is what proves this
  comparison can still see a cycle of skew on them.
- **What the netlist shows that the model cannot.** 512 of the netlist's 708
  flops (the two 8x32-bit FIFO memories) have no reset port and hold `x` out
  of reset, where the model starts every field at 0. Zero of the
  {suite_cycles} compared cycles saw an `x` reach a pin — the design's own
  `cond_avail ? cond_mem[head] : 32'd0` gating doing its job, which is a
  property the behavioural model *cannot* check because it has no
  uninitialised state to gate.

### What the per-block behavioural suite could not see

Four of the five suite members drive one sub-block each. The post-route
netlist is a single flattened `module trng_top` with no sub-block hierarchy
left to bind to, so every scenario here goes through the top-level ports — and
that surfaced a cross-block interaction none of the four per-block testbenches
can: `trng_top` has DR-0016 per-ring liveness inputs (`ring_bit[1:0]`) that
the conditioner's, the health test's and the interface's own testbenches have
no equivalent of. Leaving them idle is not "no stimulus", it is *two dead
rings*: the watchdog fires at C_LIVE = {scenarios.C_LIVE} cycles, latches
`ht_alarm` and gates the conditioned path. Every scenario here longer than
that drives healthy per-ring taps, and the one that does not (`smoke`, 11
cycles, faithful to its counterpart) is shorter than the cutoff. This is
DR-0016 behaving exactly as ratified, not a defect — it is recorded because an
integrator who ties `ring_bit` to a constant will see an alarm
{scenarios.C_LIVE} cycles after reset and has no other document to find that
in.

## How to reproduce

```sh
python3 sim/tb/{SLUG}/run_demo.py --check-env    # what this flow needs, and whether it is here
python3 sim/tb/{SLUG}/run_demo.py --no-write     # run both legs, print, mint nothing
python3 sim/tb/{SLUG}/run_demo.py                # run both legs and mint a new record
```

`--check-env` first is not ceremony: this flow needs a `klt` whose interpreter
can *load* cocotb's compiled VPI module, which is stricter than "cocotb
imports" — see `run_demo.py`'s docstring, and `--check-env`'s own output for
the exact reason a given `klt` was rejected. On a host where the `klt` on
`$PATH` cannot, point `TRNG_POST_ROUTE_KLT` at one that can. That the
underlying failure surfaces from `klt` as a generic "the regression did not
run to completion" is filed generically upstream as
[klayout-tools#1103](https://github.com/2AMLogic/klayout-tools/issues/1103).

The run is deterministic: every bit of stimulus comes from `scenarios.py`'s
SHA-256 counter-mode generators at the fixed seeds in the frontmatter,
cocotb's own seed is pinned, and the netlist and SDF are committed artefacts
whose hashes are in the frontmatter. Records are append-only: a re-run mints a
new stem, it never overwrites this one.

## Caveats

These are the annotation's coverage limits, enumerated. Each is something this
run did **not** model, and therefore a claim this record cannot support:

- **No interconnect (wire) delay, at all.** `layout/digital/gen_sdf.py` links
  the netlist against the liberty deck with no DEF, no placement and no
  parasitic extraction, so every net is a zero-length, zero-RC lump and every
  `INTERCONNECT` entry would have been zero — which is why the design-scope
  block that would carry them is not in the committed SDF at all. That script
  also explains why the obvious better answer is *worse* here: the only route
  to real routed parasitics extracts them from the DEF→GDS merge, and that
  merge is geometrically wrong by a factor of two
  ([klayout-tools#1090](https://github.com/2AMLogic/klayout-tools/issues/1090)),
  so it would produce interconnect delays wrong by a data-dependent factor
  rather than absent ones. Consequence: every delay here is optimistic by
  whatever the routing contributes, and the settle bound above is a floor, not
  an estimate.
- **No setup/hold/width checking of any kind — not weaker checking, none.**
  Icarus Verilog 13.0 drops it twice over, and both counts come from this
  run's own transcripts (`gate_transcript_digest.json`):
  **{diagnostics['sdf_timingcheck_dropped']}** `TIMINGCHECK not supported`
  lines (one per flop — the SDF's characterised setup/hold limits are parsed
  and discarded) and
  **{diagnostics['library_timing_checks_dropped']}** `Timing checks are not
  supported` lines while elaborating the cell library (Icarus implements no
  `$setup`/`$hold`/`$width` at all, so the models' own placeholder checks do
  not run either). The `notifier` regs those checks would drive therefore
  never fire, and **a timing violation this run did not report is not evidence
  of anything**: the run models cell delay and propagates it, and that is the
  whole of its timing content. Setup/hold signoff stays with OpenROAD's own
  STA (`layout/digital/reports/place_and_route.json`) and #145. That `klt`'s
  response reports `annotated: true` without distinguishing a fully-annotated
  run from one where every `TIMINGCHECK` was dropped is filed generically
  upstream as
  [klayout-tools#1102](https://github.com/2AMLogic/klayout-tools/issues/1102).
- **{sdf_report['coverage']['icarus_unsupported_arcs_excluded']} IOPATH arcs
  are unannotated.** Icarus refused
  {diagnostics['ifnone_arcs_unsupported']} `specify` paths in the cell
  *library* (`sorry: ifnone with an edge-sensitive path`, once per library cell
  definition, in this run's own elaboration transcript); across this netlist's
  instances of those cells that accounts for the
  {sdf_report['coverage']['icarus_unsupported_arcs_excluded']} SDF entries
  `gen_sdf.py` therefore drops — the refused shape is an `ifnone`-qualified
  edge-sensitive path, which is what `xor`/`xnor`/`mux`/`addf`/`addh` use for
  their select/toggle inputs, and `gen_sdf.py`'s docstring derives the exact
  `(cell, from, to)` list mechanically from the library's own Verilog. For
  {sdf_report['coverage']['icarus_unsupported_cells_dropped_entirely']}
  instances every arc they had was in that set, so those instances simulate
  entirely at their *library default* delay rather than at this corner's.
- **One corner, one voltage, one temperature.**
  `{sdf_report['pdk']['corner']}` only. Nothing here says anything about any
  other corner, and the SDF's `min:typ:max` triplets are all identical (one
  deck), so `-T min` and `-T max` would simulate the same numbers as the
  `typ` this run used.
- **No parasitic coupling, no IR drop, no on-chip variation, no SSTA.** The
  power grid is not in this simulation — and per #171 it is not in the
  committed layout yet either.
- **Stimulus is a bounded slice, not the behavioural scenario.** Each scenario
  runs the shortest prefix that exercises the mechanism it is named for; the
  Result table's scenario definitions record the behavioural length each was
  cut down from. This record therefore carries **no statistical claim**: the
  monobit balances, the observed false-positive rates and the SP 800-90B
  arithmetic stay with the behavioural records, which run 8192–131072 samples
  for exactly that reason. What transfers to the netlist is functional
  equivalence on the stimulus actually run, and only that.
- **A narrower observation surface than the behavioural suite has.** Those
  testbenches read a block's internal counters directly; this one sees only
  `trng_top`'s pins. A divergence in internal state that never reaches a pin
  on this stimulus would not be detected here.
- **Not a power, area or Fmax record.** Those are #145's deliverable.
- **The behavioural records keep their level.** Nothing here re-labels them:
  they are `level: behavioral` and remain citable exactly as far as DR-0009
  rule 3 allows. This record adds a level; it does not reclassify one.

---

Written by `sim/tb/{SLUG}/run_demo.py`. Append-only: never edit or delete this
file — a re-run or correction mints a new record and points back here via
`supersedes` (see `sim/README.md`).
"""


def write_record(env: dict, legs: dict, result: dict, records_dir: Path,
                 git: dict, wall_s: float) -> Path:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def render(stem: str, raw_dir: Path) -> str:
        written = []
        for leg_name, leg in legs.items():
            for label, payload in (
                ("klt_response", leg["klt_response"]),
                ("comparison", leg["comparison"]),
                ("request", leg["request"]),
                ("transcript_digest", leg["transcripts"]),
            ):
                name = f"{leg_name}_{label}.json"
                (raw_dir / name).write_text(
                    json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n"
                )
                written.append(name)
        (raw_dir / "environment.json").write_text(
            json.dumps(env, indent=2, sort_keys=True, default=str) + "\n"
        )
        written.append("environment.json")
        (raw_dir / "verdict.json").write_text(
            json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
        )
        written.append("verdict.json")
        raw_files = [
            (name, report.sha256_file(raw_dir / name)) for name in sorted(written)
        ]
        return (
            _frontmatter(stem, env, legs, git, raw_files, wall_s)
            + "\n"
            + _body(env, legs, result)
        )

    return report.finalize_record(records_dir, date, SLUG, render)


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #


def _print_environment(env: dict) -> None:
    print(f"platform: {env['platform']}")
    print(f"python:   {env['python']}")
    print(f"iverilog: {env['iverilog']}")
    print(f"pdk:      {env['pdk']['name'] if env['pdk'] else None}")
    for candidate in env["klt_candidates"]:
        mark = "OK " if candidate["usable"] else "no "
        detail = (
            f"cocotb {candidate.get('cocotb')} on CPython {candidate.get('python')}"
            if candidate["usable"]
            else candidate["reason"]
        )
        print(f"  {mark}{candidate['klt']}: {detail}")


def _print_summary(legs: dict, result: dict) -> None:
    for leg_name, leg in legs.items():
        response = leg["klt_response"]
        sdf = response["environment"]["sdf"]
        print(
            f"[{leg_name}] klt status={response['status']} "
            f"passed={response['passed_count']} failed={response['failed_count']} "
            f"skipped={response['skipped_count']} "
            f"sdf={'annotated' if sdf else 'none (zero-delay)'}"
        )
    print()
    header = f"{'scenario':34s} {'cycles':>7s}  {'vs RTL':>9s}  {'vs model':>9s}"
    print(header)
    for name, fact in result["facts"].items():
        if fact["kind"] == "settle-sweep":
            sweep = _rows(legs["gate"])[name]
            print(
                f"{name:34s} {'sweep':>7s}  settles by "
                f"{sweep['smallest_clean_offset_ns']}ns, dirty at "
                f"{sweep['largest_dirty_offset_ns']}ns"
            )
            continue
        print(
            f"{name:34s} {fact['cycles']:7d}  "
            f"{'identical' if fact['preserved_by_pnr'] else 'DIFFERS':>9s}  "
            f"{fact['gate_vs_model']:9d}  (rtl leg: {fact['rtl_vs_model']}, "
            f"probe: {fact['gate_vs_probe']})"
        )
    print()
    for name, value in result["checks"].items():
        print(f"  {'ok  ' if value else 'FAIL'} {name}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-write", action="store_true",
        help="run the regression and print the results without minting a record",
    )
    parser.add_argument(
        "--check-env", action="store_true",
        help="report what this flow needs and whether it is present, then exit",
    )
    parser.add_argument(
        "--scenario", action="append", choices=sorted(scenarios.ALL_SCENARIOS),
        help="run only this scenario (repeatable); default is all of them. A "
             "partial run still mints a record, which states which scenarios ran",
    )
    args = parser.parse_args(argv)

    env, problems = check_environment()
    if args.check_env:
        _print_environment(env)
        for problem in problems:
            print(f"MISSING: {problem}", file=sys.stderr)
        return EXIT_OK if not problems else EXIT_ENVIRONMENT
    if problems:
        for problem in problems:
            print(f"ERROR  {problem}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    pdk = resolve_pdk()
    env["pdk_version"] = getattr(pdk, "version", None) or "unknown"

    names = args.scenario or list(scenarios.ALL_SCENARIOS)
    started = time.time()
    try:
        # The RTL reference leg first: the post-route leg asserts against its
        # per-scenario trace hashes, so it has to exist before that leg runs.
        rtl = run_leg(env, "rtl", names, reference=None)
        gate = run_leg(env, "gate", names, reference=rtl["comparison_path"])
    except FlowError as exc:
        print(f"ERROR  {exc}", file=sys.stderr)
        return EXIT_FLOW_FAILURE
    wall_s = time.time() - started

    legs = {"rtl": rtl, "gate": gate}
    result = verdict(legs)
    _print_summary(legs, result)

    if not args.no_write:
        path = write_record(
            env, legs, result, SIM_DIR / "records",
            report.git_provenance(REPO_ROOT), wall_s,
        )
        print(f"\nrecord: {path.relative_to(REPO_ROOT)}")

    if not result["pass"]:
        failed = [name for name, ok in result["checks"].items() if not ok]
        print(
            "FAILED: " + ", ".join(failed) + " -- see the record's Result table",
            file=sys.stderr,
        )
        return EXIT_COMPARISON_FAILED
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
