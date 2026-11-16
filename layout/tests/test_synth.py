#!/usr/bin/env python3
"""Unit tests for `design/synth.py`'s `netlist_path` schema handling
(issue #288) -- that `synthesize()` reaches a verdict against *both* `klt`
netlist_path shapes rather than aborting on whichever one it was not
written for.

Why a test and not a convention
-------------------------------
`klt synthesize`'s JSON envelope reports `netlist_path` two different ways
depending on the installed `klt`:

- **schema v1** (`klt < 0.6.0`, including the build
  `.github/workflows/pdk-nightly.yml` pins per DR-0026): a plain path
  string;
- **schema v2** (`klt >= 0.6.0`, klayout-tools#1844): a
  `{"path": <repo-relative>, "scope": "repo"}` envelope, introduced to
  stop leaking machine-local absolute paths into committed evidence.

The reader has now been wrong in *both* directions within two PRs. Before
#283 it read only the v1 string and crashed with an uncaught `TypeError`
under klt >= 0.6.0 (#278). #283 fixed that by reading only the v2 envelope
-- which made `python3 design/synth.py --check` abort with exit 3
("unrecognized netlist_path shape") under the pinned klt CI actually
installs, so the nightly synthesis staleness guard stopped reaching a
verdict at all (#288).

Nothing in CI caught either direction, because the only exercise
`design/synth.py` had was the PDK/yosys/klt-dependent nightly job itself --
by which point the guard is the thing that is broken. These tests are that
alarm, and they run on the PR-blocking path (`npm run test:layout`, wired
into `npm run check:ci`) with no `klt`, no yosys, no PDK and no network:
`_run_klt` and the environment probe are mocked, the same no-tool-needed
pattern `layout/tests/test_klt.py` already uses.

What is asserted is that both shapes resolve to the same netlist and the
same *committed* report -- the committed artefact must be schema-
independent, since `_committed_view()` restates `netlist_path` to the
committed path regardless -- and that a genuinely unrecognized shape still
raises `SynthError` naming the shape, rather than being silently coerced.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

LAYOUT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAYOUT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from sim.tools.pathload import load_module_from_path  # noqa: E402


def _load(name: str, path: Path):
    """Load a flat top-level driver script as a module.

    `design/synth.py` is a script run by path, not a package member, so
    there is no import path to reach it by; `load_module_from_path` loads it
    from its own file under a unique module name.
    """
    return load_module_from_path(name, path)


synth = _load("design_synth", REPO_ROOT / "design" / "synth.py")

#: A committed file, used as the v2 shape's repo-relative `path` -- it is
#: the very artefact `klt synthesize` reports there in a real run, and it
#: has to exist on disk for `synthesize()`'s own is-a-file check.
COMMITTED_NETLIST_REL = "design/trng_top/trng_top.synth.v"

#: A minimal stand-in for `klt synthesize`'s response, carrying the fields
#: `_committed_view()` and `build()` actually read. `netlist_path` is
#: filled in per-test -- that field is what these tests are about.
BASE_PAYLOAD = {
    "schema_version": 2,
    "hdl_toplevel": "trng_top",
    "instance_count": 1234,
    "area_um2": 5678.9,
    "sequential_area_um2": 1000.0,
    "instance_counts_by_type": {"gf180mcu_fd_sc_mcu9t5v0__nand2_1": 12},
    "timing": None,
    "script_path": "/scratch/.klt/synthesize/trng_top.ys",
    "provenance": {
        "tool": {"name": "klt", "version": "0.5.0"},
        "pdk": {
            "name": "gf180mcuD",
            "version": "open_pdks-1.0.0",
            "source": "search_root:~/.volare",
        },
    },
}


def _payload(netlist_path):
    payload = dict(BASE_PAYLOAD)
    payload["netlist_path"] = netlist_path
    return payload


class _SynthesizeHarness(unittest.TestCase):
    """Runs `synthesize()` against a mocked `klt`, with no tool or PDK."""

    def run_synthesize(self, netlist_path):
        """`synthesize()` with `klt` returning `netlist_path` in its payload.

        Returns `(committed_report, netlist_path)`; raises whatever
        `synthesize()` raises.
        """
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(synth, "_check_environment", return_value=[]), \
                 mock.patch.object(synth, "resolve_pdk", return_value=None), \
                 mock.patch.object(
                     synth, "_run_klt", return_value=_payload(netlist_path)
                 ):
                return synth.synthesize(Path(tmp))


class NetlistPathSchemaTests(_SynthesizeHarness):
    """Both `klt` netlist_path schemas must reach a verdict (#288)."""

    def test_v1_plain_string_is_accepted(self):
        """klt < 0.6.0 (the build pdk-nightly.yml pins) reports a plain,
        absolute path string -- the regression case: #283 narrowed the
        reader to dicts only, so this aborted with exit 3."""
        with tempfile.TemporaryDirectory() as tmp:
            netlist = Path(tmp) / "trng_top_synth.v"
            netlist.write_text("// gate-level netlist\n")
            report, resolved = self.run_synthesize(str(netlist))
        self.assertEqual(resolved, netlist)
        self.assertEqual(report["netlist_path"], COMMITTED_NETLIST_REL)

    def test_v2_path_scope_envelope_is_accepted(self):
        """klt >= 0.6.0 (klayout-tools#1844) reports `{path, scope}` with a
        repo-relative path -- #283's case, which must keep working."""
        report, resolved = self.run_synthesize(
            {"path": COMMITTED_NETLIST_REL, "scope": "repo"}
        )
        self.assertEqual(resolved, REPO_ROOT / COMMITTED_NETLIST_REL)
        self.assertEqual(report["netlist_path"], COMMITTED_NETLIST_REL)

    def test_both_schemas_produce_the_same_committed_report(self):
        """The committed artefact is schema-independent: `_committed_view()`
        restates `netlist_path` to the committed path either way, so which
        `klt` ran must not show up in `trng_top.synth.json`."""
        with tempfile.TemporaryDirectory() as tmp:
            netlist = Path(tmp) / "trng_top_synth.v"
            netlist.write_text("// gate-level netlist\n")
            v1_report, _ = self.run_synthesize(str(netlist))
        v2_report, _ = self.run_synthesize(
            {"path": COMMITTED_NETLIST_REL, "scope": "repo"}
        )
        self.assertEqual(v1_report, v2_report)
        # And the two fields naming a scratch location are restated, not
        # committed as klt returned them (the "Determinism" docstring).
        self.assertIsNone(v1_report["script_path"])
        self.assertEqual(v1_report["netlist_path"], COMMITTED_NETLIST_REL)


class UnrecognizedShapeTests(_SynthesizeHarness):
    """Widening the accepted set must not widen it to *everything*."""

    def test_null_netlist_path_raises_with_the_shape_in_the_message(self):
        with self.assertRaises(synth.SynthError) as ctx:
            self.run_synthesize(None)
        message = str(ctx.exception)
        self.assertIn("unrecognized netlist_path shape", message)
        self.assertIn("None", message)

    def test_list_netlist_path_raises_with_the_shape_in_the_message(self):
        with self.assertRaises(synth.SynthError) as ctx:
            self.run_synthesize(["a.v", "b.v"])
        message = str(ctx.exception)
        self.assertIn("unrecognized netlist_path shape", message)
        self.assertIn("'a.v'", message)

    def test_external_scope_envelope_still_raises(self):
        """v2's own "no usable repo-relative path" case is unchanged."""
        with self.assertRaises(synth.SynthError) as ctx:
            self.run_synthesize({"path": None, "scope": "external"})
        self.assertIn("scope='external'", str(ctx.exception))

    def test_empty_string_raises_rather_than_resolving_to_the_repo_root(self):
        """A falsy v1 path must not silently become `REPO_ROOT` itself."""
        with self.assertRaises(synth.SynthError) as ctx:
            self.run_synthesize("")
        self.assertIn("no usable path", str(ctx.exception))

    def test_missing_file_still_raises_for_the_v1_string_shape(self):
        """Accepting the shape is not accepting a path that isn't there."""
        with tempfile.TemporaryDirectory() as tmp:
            absent = Path(tmp) / "never_written.v"
            with self.assertRaises(synth.SynthError) as ctx:
                self.run_synthesize(str(absent))
        self.assertIn("does not exist", str(ctx.exception))


class RunBookkeepingTests(unittest.TestCase):
    """klt >= 0.6.0's per-invocation `run_id`/`run_script_path` (#281)."""

    def _view(self, **extra):
        payload = _payload({"path": COMMITTED_NETLIST_REL, "scope": "repo"})
        payload.update(extra)
        with mock.patch.object(synth, "_rtl_sources", return_value=[]):
            return synth._committed_view(payload)

    def test_two_runs_differing_only_in_run_scoped_names_commit_identically(self):
        """Two runs of one request mint different run ids; the committed
        report must not see that, or `--check` can never pass."""
        a = self._view(
            run_id="run-aaaa",
            run_script_path={
                "path": "design/.work/.klt/synthesize/run-aaaa/x.run.ys",
                "scope": "repo",
            },
        )
        b = self._view(
            run_id="run-bbbb",
            run_script_path={
                "path": "design/.work/.klt/synthesize/run-bbbb/x.run.ys",
                "scope": "repo",
            },
        )
        self.assertEqual(a, b)
        self.assertIsNone(a["run_id"])
        self.assertIsNone(a["run_script_path"])

    def test_absent_bookkeeping_keys_are_not_added(self):
        """A klt that emits none of them commits no new keys."""
        view = self._view()
        self.assertNotIn("run_id", view)
        self.assertNotIn("run_script_path", view)

    def test_verdict_bearing_fields_still_differ(self):
        """Restating bookkeeping must not hide a real change."""
        a = self._view(run_id="run-aaaa", instance_count=1)
        b = self._view(run_id="run-bbbb", instance_count=2)
        self.assertNotEqual(a, b)


class MachineLocalAndRunScopedFieldTests(unittest.TestCase):
    """Fields klt >= 0.9.0 added that describe the *machine* or the *run*
    rather than the synthesis, and that `--check` would otherwise trip on
    forever (#866).
    """

    def _view(self, **extra):
        payload = _payload({"path": COMMITTED_NETLIST_REL, "scope": "repo"})
        payload.update(extra)
        with mock.patch.object(synth, "_rtl_sources", return_value=[]):
            return synth._committed_view(payload)

    def _provenance(self, pdk):
        provenance = dict(BASE_PAYLOAD["provenance"])
        provenance["pdk"] = pdk
        return provenance

    def test_ambiguous_pdk_sources_are_dropped(self):
        """A host with two PDK search roots must commit what a host with
        one commits -- otherwise a workstation-generated report can never
        match CI's fresh run."""
        two_roots = self._view(provenance=self._provenance({
            "name": "gf180mcuD",
            "version": "open_pdks-1.0.0",
            "source": "search root: ~/.ciel",
            "ambiguous_sources": ["search root: ~/.volare"],
        }))
        one_root = self._view(provenance=self._provenance({
            "name": "gf180mcuD",
            "version": "open_pdks-1.0.0",
            "source": "search root: ~/.ciel",
        }))
        self.assertEqual(two_roots, one_root)
        self.assertNotIn("ambiguous_sources", two_roots["provenance"]["pdk"])

    def test_the_pdk_identity_still_differs(self):
        """Dropping the search roots must not collapse *which* PDK."""
        a = self._view(provenance=self._provenance(
            {"name": "gf180mcuD", "version": "open_pdks-1.0.0"}))
        b = self._view(provenance=self._provenance(
            {"name": "gf180mcuD", "version": "open_pdks-2.0.0"}))
        self.assertNotEqual(a, b)

    def test_memory_mapping_script_path_is_restated(self):
        """`memory_mapping.script_path` names a file inside the
        per-invocation `.klt/synthesize/<run_id>/` directory, so two runs of
        one request disagree on it by construction."""
        a = self._view(memory_mapping={
            "status": "none_detected",
            "reason": None,
            "modules": [],
            "script_path": {
                "path": "design/.work/.klt/synthesize/run-aaaa/mem.ys",
                "scope": "repo",
            },
        })
        b = self._view(memory_mapping={
            "status": "none_detected",
            "reason": None,
            "modules": [],
            "script_path": {
                "path": "design/.work/.klt/synthesize/run-bbbb/mem.ys",
                "scope": "repo",
            },
        })
        self.assertEqual(a, b)
        self.assertIsNone(a["memory_mapping"]["script_path"])

    def test_memory_mapping_verdict_still_differs(self):
        """Restating the script path must not hide a real memory mapping."""
        a = self._view(memory_mapping={"status": "none_detected", "modules": []})
        b = self._view(memory_mapping={"status": "mapped", "modules": ["fifo"]})
        self.assertNotEqual(a, b)

    def test_absent_blocks_commit_no_new_keys(self):
        """A klt that emits neither must not grow either."""
        view = self._view()
        self.assertNotIn("memory_mapping", view)
        self.assertNotIn("ambiguous_sources", view["provenance"]["pdk"])


class CommittedEngineVersionMatchesTheNightlyPinTests(unittest.TestCase):
    """The committed synthesis report must name the Yosys the nightly pins.

    This is the alarm for the failure #866 is: PR #729 regenerated
    `design/trng_top/trng_top.synth.{v,json}` on a workstation whose `yosys`
    was a local 0.67+post source build, while
    `.github/workflows/pdk-nightly.yml` installs
    `yowasp-yosys==0.69.0.0.post1233`. Nothing on the pull-request path could
    see it: `design/synth.py --check` needs Yosys, the PDK and the
    standard-cell library, so it only runs in the nightly -- which then went
    red at that guard for nine consecutive scheduled runs, skipping every
    later step (the layout and floorplan freshness checks) with it.

    So this test asks the cheap half of the same question with no tool at
    all: does the committed report *claim* to come from the pinned engine?
    It cannot tell whether re-synthesizing would reproduce the netlist --
    only the nightly's guard can -- but a regeneration outside the pin now
    fails on the pull request that commits it, instead of on the next
    nightly.

    The pin is read from the workflow, never restated here: one pin, one
    place (the same discipline `sim/tools/klt_pin_sites.py` applies to the
    klt and KLayout pins).
    """

    WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pdk-nightly.yml"
    REPORT = REPO_ROOT / "design" / "trng_top" / "trng_top.synth.json"

    #: `yowasp-yosys` versions its wheels `<yosys release>.<yowasp
    #: revision>[.postN]` -- `0.69.0.0.post1233` is Yosys 0.69 -- and that
    #: leading release is what `yosys -V` prints and what `klt synthesize`
    #: records as `engine_version`.
    PIN_RE = re.compile(r"yowasp-yosys==(\d+\.\d+)(?:[.0-9a-z+]*)")

    def pinned_engine_version(self) -> str:
        text = self.WORKFLOW.read_text()
        matches = self.PIN_RE.findall(text)
        self.assertTrue(
            matches,
            f"{self.WORKFLOW.name} installs no `yowasp-yosys==<version>` -- "
            "this test reads the pin from the workflow and must be updated "
            "with it, not given a second copy of the version",
        )
        self.assertEqual(
            len(set(matches)), 1,
            f"{self.WORKFLOW.name} pins more than one yowasp-yosys version: "
            f"{sorted(set(matches))}",
        )
        return matches[0]

    def test_the_workflow_pin_is_readable(self):
        self.assertRegex(self.pinned_engine_version(), r"^\d+\.\d+$")

    def test_committed_report_names_the_pinned_engine(self):
        want = self.pinned_engine_version()
        report = json.loads(self.REPORT.read_text())
        got = report.get("engine_version")
        self.assertEqual(
            got, want,
            f"design/trng_top/trng_top.synth.json records engine_version "
            f"{got!r}, but .github/workflows/pdk-nightly.yml installs Yosys "
            f"{want}. The nightly's `python3 design/synth.py --check` "
            f"re-synthesizes with {want} and will report the committed "
            f"netlist STALE. Regenerate from a toolchain built out of the "
            f"nightly's own install lines (pip install "
            f'"yowasp-yosys==..." and a tagged "klayout-tools" release), '
            f"or move the pin with a decision record.",
        )

    def test_a_report_off_the_pin_fails(self):
        """The guard's own alarm: the exact condition #866 reports -- a
        committed report naming the 0.67+post local build -- must fail."""
        report = json.loads(self.REPORT.read_text())
        report["engine_version"] = "0.67+post"
        with tempfile.TemporaryDirectory() as tmp:
            stand_in = Path(tmp) / "trng_top.synth.json"
            stand_in.write_text(json.dumps(report))
            with mock.patch.object(
                CommittedEngineVersionMatchesTheNightlyPinTests,
                "REPORT", stand_in,
            ):
                with self.assertRaises(AssertionError) as ctx:
                    self.test_committed_report_names_the_pinned_engine()
        self.assertIn("0.67+post", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
