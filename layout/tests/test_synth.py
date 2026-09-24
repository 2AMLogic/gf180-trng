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

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

LAYOUT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAYOUT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load(name: str, path: Path):
    """Load a flat top-level driver script as a module.

    The same `importlib.util.spec_from_file_location` pattern
    `layout/tests/test_digital_reports.py` and `layout/tests/test_verify.py`
    use: `design/synth.py` is a script run by path, not a package member, so
    there is no import path to reach it by.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


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


if __name__ == "__main__":
    unittest.main()
