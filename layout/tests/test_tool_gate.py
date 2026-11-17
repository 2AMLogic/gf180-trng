#!/usr/bin/env python3
"""Unit tests for the klt/PDK availability gate (issue #902).

Before #902, seven entry points hand-rolled the same gate: four inline
copies (`layout/cells/_build_cli.py`'s `make_pdk_main`, `layout/verify.py`,
`layout/floorplan/floorplan.py`,
`layout/blocks/combiner_sampler/build.py`) printing the two canonical
reason strings and a SKIP-or-FAIL verdict, and three `_check_environment()`
collectors (`design/synth.py`, `layout/digital/build.py`,
`layout/digital/gen_sdf.py`) joining their own copies into one raised
error. The copies had drifted -- two skip wordings; `gen_sdf` probing one
tool fewer. #902 moved the gate into `layout/_klt.py`'s `missing_tools()` /
`report_missing()`; these tests pin the behaviour the refactor had to
preserve, and the one question it had to settle deliberately: `gen_sdf`
stamps `klt_version` into its report without ever requiring the tool.

Mostly the absent-probe branches -- the point `check:ci` cannot cover, since
on a tool-equipped runner the gates never enter their skip path at all.
`layout/tests/test_build_cli.py` already pins `make_pdk_main`'s four gate
branches against injected hooks; this file covers the helpers directly and
the three hand-written `main()`s and three `_check_environment()` functions
that had no test at all before #902.

No `klt`, yosys, OpenROAD, docker or PDK is needed: every probe is patched,
the same no-tool-needed pattern `layout/tests/test_klt.py` uses.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

LAYOUT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAYOUT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from sim.tools.pathload import load_module_from_path  # noqa: E402

from layout._klt import (  # noqa: E402
    KLT_MISSING_REASON,
    PDK_MISSING_REASON,
    missing_tools,
    report_missing,
)
from layout.floorplan import erc_supply, floorplan  # noqa: E402

verify = load_module_from_path(
    "layout_tests_tool_gate_verify", LAYOUT_DIR / "verify.py"
)
combiner = load_module_from_path(
    "layout_tests_tool_gate_combiner", LAYOUT_DIR / "blocks" / "combiner_sampler" / "build.py"
)
digital_build = load_module_from_path(
    "layout_tests_tool_gate_digital_build", LAYOUT_DIR / "digital" / "build.py"
)
gen_sdf = load_module_from_path(
    "layout_tests_tool_gate_gen_sdf", LAYOUT_DIR / "digital" / "gen_sdf.py"
)
synth = load_module_from_path(
    "layout_tests_tool_gate_synth", REPO_ROOT / "design" / "synth.py"
)

YOSYS_REASON = (
    "yosys is not on PATH (`klt synthesize` shells out to it as a "
    "subprocess -- install Yosys and put it on PATH)"
)
OPENROAD_MARKER = "openroad unreachable (gate-test marker)"

#: A repo-root-relative path that does not exist -- `is_file()` is False and
#: `relative_to(REPO_ROOT)` still works, which is what the netlist reason
#: lines compute.
ABSENT_NETLIST = REPO_ROOT / "layout" / "tests" / "_gate_test_absent.netlist.v"


def run(fn, *args, **kwargs):
    """Call `fn`, returning (return code, stdout lines)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = fn(*args, **kwargs)
    return rc, out.getvalue().splitlines()


def run_err(fn):
    """Call `fn()` with no arguments, returning (return code, stderr lines)."""
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = fn()
    return rc, err.getvalue().splitlines()


class MissingToolsTests(unittest.TestCase):
    """`missing_tools()` maps probe results to the canonical reasons."""

    def test_no_probes_requested_means_nothing_missing(self):
        self.assertEqual(missing_tools(), [])

    def test_tools_present_means_nothing_missing(self):
        self.assertEqual(missing_tools(klt_version="klt 0.6.0", pdk=object()), [])

    def test_klt_absent(self):
        self.assertEqual(missing_tools(klt_version=None, pdk=object()), [KLT_MISSING_REASON])

    def test_pdk_absent(self):
        self.assertEqual(missing_tools(klt_version="klt 0.6.0", pdk=None), [PDK_MISSING_REASON])

    def test_both_absent_lists_klt_first(self):
        self.assertEqual(
            missing_tools(klt_version=None, pdk=None),
            [KLT_MISSING_REASON, PDK_MISSING_REASON],
        )


class ReportMissingTests(unittest.TestCase):
    """`report_missing()` prints the gate's verdict and returns its exit."""

    def test_nothing_missing_returns_none_and_prints_nothing(self):
        rc, lines = run(report_missing, [], require_tools=False, what="x")
        self.assertEqual((rc, lines), (None, []))

    def test_one_line_skip_without_hint(self):
        rc, lines = run(report_missing, [KLT_MISSING_REASON], require_tools=False, what="top build")
        self.assertEqual(rc, 0)
        self.assertEqual(
            lines,
            [
                f"  - {KLT_MISSING_REASON}",
                "SKIP: top build -- the tools above are not available.",
            ],
        )

    def test_two_line_skip_with_hint(self):
        rc, lines = run(
            report_missing,
            [KLT_MISSING_REASON, PDK_MISSING_REASON],
            require_tools=False,
            what="layout verification",
            hint="Install them to run the DRC/LVS flow",
        )
        self.assertEqual(rc, 0)
        self.assertEqual(
            lines,
            [
                f"  - {KLT_MISSING_REASON}",
                f"  - {PDK_MISSING_REASON}",
                "SKIP: layout verification -- the tools above are not available.",
                "      Install them to run the DRC/LVS flow (see layout/README.md).",
            ],
        )

    def test_require_tools_fails_with_exit_one(self):
        rc, lines = run(
            report_missing, [PDK_MISSING_REASON], require_tools=True, what="floorplan build"
        )
        self.assertEqual(rc, 1)
        self.assertEqual(
            lines,
            [
                f"  - {PDK_MISSING_REASON}",
                "FAIL: --require-tools was given and the flow cannot run",
            ],
        )


class VerifyMainGateTests(unittest.TestCase):
    """`layout/verify.py`'s gate, driven through the real `main()`.

    The absent-probe branches are the ones a tool-equipped `check:ci` never
    enters, so they are pinned here against patched probes -- exact output,
    exact exit.
    """

    def drive(self, argv, version, pdk):
        with mock.patch.object(verify, "klt_version", return_value=version), \
             mock.patch.object(verify, "resolve_pdk", return_value=pdk):
            return run(verify.main, argv)

    def test_both_absent_skips_with_hint(self):
        rc, lines = self.drive([], None, None)
        self.assertEqual(rc, verify.EXIT_OK)
        self.assertEqual(
            lines,
            [
                f"  - {KLT_MISSING_REASON}",
                f"  - {PDK_MISSING_REASON}",
                "SKIP: layout verification -- the tools above are not available.",
                "      Install them to run the DRC/LVS flow (see layout/README.md).",
            ],
        )

    def test_klt_absent_only(self):
        rc, lines = self.drive([], None, SimpleNamespace(variant="v"))
        self.assertEqual(rc, verify.EXIT_OK)
        self.assertEqual(
            lines[0], f"  - {KLT_MISSING_REASON}"
        )
        self.assertTrue(lines[1].startswith("SKIP: layout verification"))

    def test_pdk_absent_only(self):
        rc, lines = self.drive([], "klt 0.6.0", None)
        self.assertEqual(rc, verify.EXIT_OK)
        self.assertEqual(
            lines[0], f"  - {PDK_MISSING_REASON}"
        )
        self.assertTrue(lines[1].startswith("SKIP: layout verification"))

    def test_require_tools_fails_when_absent(self):
        rc, lines = self.drive(["--require-tools"], None, None)
        self.assertEqual(rc, verify.EXIT_FAIL)
        self.assertEqual(
            lines,
            [
                f"  - {KLT_MISSING_REASON}",
                f"  - {PDK_MISSING_REASON}",
                "FAIL: --require-tools was given and the flow cannot run",
            ],
        )


class CombinerSamplerMainGateTests(unittest.TestCase):
    """`layout/blocks/combiner_sampler/build.py`'s gate, same contract."""

    def drive(self, argv, version, pdk):
        with mock.patch.object(combiner, "klt_version", return_value=version), \
             mock.patch.object(combiner, "resolve_pdk", return_value=pdk):
            return run(combiner.main, argv)

    def test_both_absent_skips_one_line(self):
        rc, lines = self.drive([], None, None)
        self.assertEqual(rc, 0)
        self.assertEqual(
            lines,
            [
                f"  - {KLT_MISSING_REASON}",
                f"  - {PDK_MISSING_REASON}",
                "SKIP: combiner_sampler build -- the tools above are not available.",
            ],
        )

    def test_klt_absent_only(self):
        rc, lines = self.drive([], None, SimpleNamespace(variant="v"))
        self.assertEqual(rc, 0)
        self.assertEqual(
            lines,
            [
                f"  - {KLT_MISSING_REASON}",
                "SKIP: combiner_sampler build -- the tools above are not available.",
            ],
        )

    def test_pdk_absent_only(self):
        rc, lines = self.drive([], "klt 0.6.0", None)
        self.assertEqual(rc, 0)
        self.assertEqual(
            lines,
            [
                f"  - {PDK_MISSING_REASON}",
                "SKIP: combiner_sampler build -- the tools above are not available.",
            ],
        )

    def test_require_tools_fails_when_absent(self):
        rc, lines = self.drive(["--require-tools"], None, None)
        self.assertEqual(rc, 1)
        self.assertEqual(
            lines[-1], "FAIL: --require-tools was given and the flow cannot run"
        )


class FloorplanMainGateTests(unittest.TestCase):
    """`layout/floorplan/floorplan.py`'s gate, driven through the real
    `main()` past its tool-free pre-gate checks (stubbed -- they have their
    own coverage; only the tool gate is under test here)."""

    def drive(self, argv):
        netlist_mod = floorplan.floorplan_netlist
        committed_ref = netlist_mod.LVS_REFERENCE_PATH.read_text()
        with mock.patch.object(floorplan, "klt_version", return_value=None), \
             mock.patch.object(floorplan, "resolve_pdk", return_value=None), \
             mock.patch.object(
                 netlist_mod, "validate_inter_region_nets", return_value=[]
             ), \
             mock.patch.object(
                 netlist_mod, "generate_lvs_reference", return_value=committed_ref
             ), \
             mock.patch.object(erc_supply, "freshness_problems", return_value=[]):
            return run(floorplan.main, argv)

    def test_both_absent_skips_with_hint(self):
        rc, lines = self.drive([])
        self.assertEqual(rc, floorplan.EXIT_OK)
        self.assertEqual(
            lines[-4:],
            [
                f"  - {KLT_MISSING_REASON}",
                f"  - {PDK_MISSING_REASON}",
                "SKIP: floorplan build -- the tools above are not available.",
                "      Install them to rebuild the floorplan (see layout/README.md).",
            ],
        )

    def test_require_tools_fails_when_absent(self):
        rc, lines = self.drive(["--require-tools"])
        self.assertEqual(rc, floorplan.EXIT_FAIL)
        self.assertEqual(
            lines[-3:],
            [
                f"  - {KLT_MISSING_REASON}",
                f"  - {PDK_MISSING_REASON}",
                "FAIL: --require-tools was given and the flow cannot run",
            ],
        )


class SynthCheckEnvironmentTests(unittest.TestCase):
    """`design/synth.py` probes klt, yosys, PDK -- in that message order."""

    def test_all_absent_in_order(self):
        with mock.patch.object(synth, "klt_version", return_value=None), \
             mock.patch("shutil.which", return_value=None), \
             mock.patch.object(synth, "resolve_pdk", return_value=None):
            missing = synth._check_environment()
        self.assertEqual(
            missing, [KLT_MISSING_REASON, YOSYS_REASON, PDK_MISSING_REASON]
        )

    def test_all_present_is_empty(self):
        with mock.patch.object(synth, "klt_version", return_value="klt 0.6.0"), \
             mock.patch("shutil.which", return_value="/usr/bin/yosys"), \
             mock.patch.object(synth, "resolve_pdk", return_value=object()):
            missing = synth._check_environment()
        self.assertEqual(missing, [])


class DigitalBuildCheckEnvironmentTests(unittest.TestCase):
    """`layout/digital/build.py` probes klt, PDK, netlist, OpenROAD -- in
    that message order."""

    def test_all_absent_in_order(self):
        expected_netlist = (
            f"{ABSENT_NETLIST.relative_to(REPO_ROOT)} is missing -- run "
            "`python3 design/synth.py` first (#143)"
        )
        with mock.patch.object(digital_build, "klt_version", return_value=None), \
             mock.patch.object(digital_build, "resolve_pdk", return_value=None), \
             mock.patch.object(digital_build, "NETLIST_PATH", ABSENT_NETLIST), \
             mock.patch.object(
                 digital_build,
                 "_ensure_openroad_reachable",
                 return_value=[OPENROAD_MARKER],
             ):
            missing = digital_build._check_environment()
        self.assertEqual(
            missing,
            [
                KLT_MISSING_REASON,
                PDK_MISSING_REASON,
                expected_netlist,
                OPENROAD_MARKER,
            ],
        )

    def test_all_present_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            netlist = Path(tmp) / "netlist.v"
            netlist.write_text("")
            with mock.patch.object(
                digital_build, "klt_version", return_value="klt 0.6.0"
            ), \
                 mock.patch.object(digital_build, "resolve_pdk", return_value=object()), \
                 mock.patch.object(digital_build, "NETLIST_PATH", netlist), \
                 mock.patch.object(
                     digital_build, "_ensure_openroad_reachable", return_value=[]
                 ):
                missing = digital_build._check_environment()
        self.assertEqual(missing, [])


class GenSdfCheckEnvironmentTests(unittest.TestCase):
    """`layout/digital/gen_sdf.py` probes netlist, PDK, OpenROAD -- and
    deliberately never `klt` (#902 settled this explicitly): SDF generation
    never invokes `klt`, so its absence must not block the run even though
    the report stamps `klt_version()` when the tool happens to exist."""

    def test_klt_is_never_probed_and_never_reported_missing(self):
        expected_netlist = (
            f"{ABSENT_NETLIST.relative_to(REPO_ROOT)} is missing -- run "
            "`python3 layout/digital/build.py` first (#111)"
        )
        klt_probe = mock.MagicMock(return_value=None)
        with mock.patch.object(gen_sdf, "klt_version", klt_probe), \
             mock.patch.object(gen_sdf, "resolve_pdk", return_value=None), \
             mock.patch.object(gen_sdf, "NETLIST_PATH", ABSENT_NETLIST), \
             mock.patch.object(
                 gen_sdf,
                 "_ensure_openroad_reachable",
                 return_value=[OPENROAD_MARKER],
             ):
            missing = gen_sdf._check_environment()
        self.assertEqual(
            missing, [expected_netlist, PDK_MISSING_REASON, OPENROAD_MARKER]
        )
        klt_probe.assert_not_called()

    def test_all_present_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            netlist = Path(tmp) / "netlist.v"
            netlist.write_text("")
            with mock.patch.object(gen_sdf, "resolve_pdk", return_value=object()), \
                 mock.patch.object(gen_sdf, "NETLIST_PATH", netlist), \
                 mock.patch.object(
                     gen_sdf, "_ensure_openroad_reachable", return_value=[]
                 ):
                missing = gen_sdf._check_environment()
        self.assertEqual(missing, [])


class DrcOnlyGateTests(unittest.TestCase):
    """`drc_only()`'s own klt gate (the third wording the issue recorded as
    drift): same reason string, `ERROR  `-prefixed to stderr, exit
    EXIT_ENVIRONMENT."""

    def test_klt_absent_fails_to_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            gds = Path(tmp) / "trng_top.gds"
            gds.write_bytes(b"")
            with mock.patch.object(digital_build, "GDS_PATH", gds), \
                 mock.patch.object(digital_build, "klt_version", return_value=None):
                rc, err = run_err(digital_build.drc_only)
        self.assertEqual(rc, digital_build.EXIT_ENVIRONMENT)
        self.assertEqual(err, [f"ERROR  {KLT_MISSING_REASON}"])


if __name__ == "__main__":
    unittest.main()
