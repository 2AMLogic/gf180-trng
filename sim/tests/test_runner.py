#!/usr/bin/env python3
"""Unit tests for sim/harness/runner.py deck composition and output parsing.

No PDK and no ngspice required -- deck composition is tested against a fake
PDK layout; actual ngspice execution is exercised by sim/selftest.sh instead.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import corners, runner, testbench  # noqa: E402
from harness.pdk import Pdk  # noqa: E402


def fake_pdk(root: Path) -> Pdk:
    (root / "libs.tech" / "ngspice").mkdir(parents=True, exist_ok=True)
    (root / "libs.tech" / "ngspice" / "sm141064.ngspice").write_text("* fake\n")
    (root / "libs.tech" / "ngspice" / "design.ngspice").write_text("* fake\n")
    (root / "SOURCES").write_text("open_pdks deadbeef\n")
    return Pdk(path=root, variant=root.name, source="test")


class DeckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        (root / "tb").mkdir()
        (root / "tb" / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (root / "tb" / "tb.json").write_text(
            json.dumps(
                {
                    "name": "x",
                    "netlist": "x.spice",
                    "measure": {"vout": "v(out)", "iq": "-i(v1)"},
                    "params": {"cload": "1p"},
                    "options": ["reltol=1e-5"],
                }
            )
        )
        self.tb = testbench.load(root / "tb")
        self.pdk = fake_pdk(root / "gf180mcuD")
        self.point = corners.build_grid(corners.resolve_corners(["ss"]), (125,), [3.63])[0]

    def test_deck_sets_the_pvt_point(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point)
        self.assertIn(".param vdd_val=3.63", deck)
        self.assertIn(".param vdd_nom=3.3", deck)
        self.assertIn(".temp 125", deck)

    def test_deck_includes_design_switches_before_model_sections(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point)
        design_at = deck.index("design.ngspice")
        lib_at = deck.index("sm141064.ngspice")
        self.assertLess(design_at, lib_at)

    def test_deck_selects_every_section_of_the_corner(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point)
        for section in self.point.corner.sections:
            self.assertIn(f'sm141064.ngspice" {section}', deck)

    def test_deck_carries_manifest_params_and_options(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point)
        self.assertIn(".param cload=1p", deck)
        self.assertIn(".options reltol=1e-5", deck)

    def test_deck_emits_one_measurement_vector_per_measure_entry(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point)
        self.assertIn("let m_vout = v(out)", deck)
        self.assertIn("let m_iq = -i(v1)", deck)
        self.assertIn("print m_vout", deck)
        self.assertTrue(deck.rstrip().endswith(".end"))

    def test_seed_only_emitted_when_given(self):
        deck_no_seed = runner.compose_deck(self.tb, self.pdk, self.point, seed=None)
        self.assertNotIn(".option seed=", deck_no_seed)
        deck_seeded = runner.compose_deck(self.tb, self.pdk, self.point, seed=7)
        self.assertIn(".option seed=7", deck_seeded)


class AnalysisContextSubstitutionTests(unittest.TestCase):
    """``analyses`` entries get {vdd_val}-style fields substituted in Python
    before ngspice ever sees them (see ``runner._analysis_context``): the
    interactive control-block ``dc``/``meas`` commands ``compose_deck``
    inserts these lines as do not evaluate ``.param`` symbols in a numeric
    argument position, so a voltage-swept testbench has no other way to make
    its sweep bounds track the PVT point's own supply."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        (root / "tb").mkdir()
        (root / "tb" / "x.spice").write_text("v1 out 0 dc 0\n")
        (root / "tb" / "tb.json").write_text(
            json.dumps(
                {
                    "name": "x",
                    "netlist": "x.spice",
                    "measure": {"dtrip": "dtrip"},
                    "analyses": [
                        "dc v1 0 {vdd_val} 0.01",
                        "meas dc dtrip when v(out)={vdd_half} fall=1",
                    ],
                }
            )
        )
        self.tb = testbench.load(root / "tb")
        self.pdk = fake_pdk(root / "gf180mcuD")
        self.point = corners.build_grid(corners.resolve_corners(["ss"]), (125,), [3.63])[0]

    def test_vdd_val_and_vdd_half_substituted_from_the_pvt_point(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point)
        self.assertIn("dc v1 0 3.63 0.01", deck)
        self.assertIn("meas dc dtrip when v(out)=1.815 fall=1", deck)
        # The unsubstituted placeholders must not survive into the deck --
        # ngspice cannot evaluate them (that is the whole reason this
        # substitution exists).
        self.assertNotIn("{vdd_val}", deck)
        self.assertNotIn("{vdd_half}", deck)


class ExtraLibSectionsTests(unittest.TestCase):
    """extra_lib_sections replaces the plain corner sections entirely (a
    section like "statistical" redefines the same subckts)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        (root / "tb").mkdir()
        (root / "tb" / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (root / "tb" / "tb.json").write_text(
            json.dumps(
                {
                    "name": "x",
                    "netlist": "x.spice",
                    "measure": {"vout": "v(out)"},
                    "analysis_type": "mc",
                    "default_runs": 2,
                    "design_params": {"sw_stat_mismatch": 1},
                    "extra_lib_sections": ["statistical"],
                }
            )
        )
        self.tb = testbench.load(root / "tb")
        self.pdk = fake_pdk(root / "gf180mcuD")
        self.point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]

    def test_extra_sections_replace_corner_sections(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point, seed=1)
        self.assertIn('sm141064.ngspice" statistical', deck)
        self.assertNotIn('sm141064.ngspice" typical', deck)

    def test_design_params_override_after_design_include(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point, seed=1)
        design_at = deck.index("design.ngspice")
        override_at = deck.index(".param sw_stat_mismatch=1")
        self.assertLess(design_at, override_at)


class ParseTests(unittest.TestCase):
    def test_parses_print_output(self):
        text = "\n".join(
            [
                "Circuit: * x",
                "m_vout = 1.2003456789e+00",
                "m_iq = -4.5e-05",
                "v(other) = 9.9",
                "m_bad = not_a_number",
            ]
        )
        self.assertEqual(
            runner.parse_measurements(text), {"vout": 1.2003456789, "iq": -4.5e-05}
        )


class RunPointContractTests(unittest.TestCase):
    """run_point enforces the 'no seed, no evidence' rule at the API level
    (before ever invoking ngspice)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        (root / "tb").mkdir()
        (root / "tb" / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (root / "tb" / "tb.json").write_text(
            json.dumps(
                {
                    "name": "x",
                    "netlist": "x.spice",
                    "measure": {"vout": "v(out)"},
                    "analysis_type": "mc",
                    "default_runs": 1,
                }
            )
        )
        self.tb = testbench.load(root / "tb")
        self.point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]

    def test_stochastic_testbench_without_seeds_is_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            runner.run_point(self.tb, None, self.point, Path("/nonexistent"), seeds=None)
        self.assertIn("no seed, no evidence", str(ctx.exception))


def _install_fake_ngspice(bin_dir: Path, script: str) -> None:
    """Drop an executable named ``ngspice`` on ``bin_dir``.

    Standing in for a real ngspice invocation lets these tests exercise
    ``run_one()``'s actual subprocess/timeout plumbing (``Popen``,
    ``timeout(1)`` wrapping, process-group kill) without requiring ngspice
    or the PDK -- consistent with this module's "no PDK and no ngspice
    required" promise above; the real thing is exercised by
    ``sim/selftest.sh`` instead.
    """
    path = bin_dir / "ngspice"
    path.write_text(script)
    path.chmod(0o755)


class TimeoutTests(unittest.TestCase):
    """``run_one()`` bounds ngspice's wall clock two ways at once (issue
    #83, filed after a hung ngspice ran ~4.5h undetected because the
    harness process that launched it had itself been killed): an OS-level
    ``timeout(1)``/``gtimeout`` watchdog that survives this harness process
    dying, plus an in-process ``Popen.communicate(timeout=...)`` guard for
    when no watchdog binary is available. Both must actually kill the whole
    process group, not just the direct child -- an orphaned grandchild is
    exactly what the incident's ngspice was.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        (root / "tb").mkdir()
        (root / "tb" / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (root / "tb" / "tb.json").write_text(
            json.dumps(
                {
                    "name": "x",
                    "netlist": "x.spice",
                    "measure": {"vout": "v(out)"},
                }
            )
        )
        self.tb = testbench.load(root / "tb")
        self.pdk = fake_pdk(root / "gf180mcuD")
        self.tt_point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]
        self.ss_point = corners.build_grid(corners.resolve_corners(["ss"]), (27,), [3.3])[0]
        self.workdir = root / "work"
        self.bin_dir = root / "bin"
        self.bin_dir.mkdir()
        path_patcher = mock.patch.dict(
            os.environ, {"PATH": f"{self.bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
        )
        path_patcher.start()
        self.addCleanup(path_patcher.stop)
        # These tests are about *that* the process group dies and is
        # reported correctly, not about timing precision -- keep the
        # kill-after escalation short so a SIGTERM-ignoring fake ngspice
        # doesn't make the suite slow.
        grace_patcher = mock.patch.object(runner, "KILL_GRACE_S", 1)
        grace_patcher.start()
        self.addCleanup(grace_patcher.stop)

    def _assert_process_is_dead(self, pid: int, within_s: float = 5.0) -> None:
        deadline = time.monotonic() + within_s
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(0.1)
        self.fail(f"pid {pid} is still alive {within_s}s after the timeout should have killed it")

    def test_fast_success_is_not_misclassified_as_a_timeout(self):
        _install_fake_ngspice(self.bin_dir, "#!/usr/bin/env python3\nprint('m_vout = 1.0')\n")
        result = runner.run_one(self.tb, self.pdk, self.tt_point, self.workdir, timeout_s=5)
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.measurements, {"vout": 1.0})

    def test_hung_run_without_a_watchdog_is_killed_by_the_in_process_guard(self):
        pidfile = self.tmp_path_for("child.pid")
        self.workdir.mkdir(parents=True, exist_ok=True)
        _install_fake_ngspice(
            self.bin_dir,
            "#!/usr/bin/env python3\n"
            "import os, signal, time\n"
            "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            f"open({str(pidfile)!r}, 'w').write(str(os.getpid()))\n"
            "time.sleep(120)\n",
        )
        with mock.patch.object(runner, "timeout_bin", return_value=None):
            started = time.monotonic()
            result = runner.run_one(self.tb, self.pdk, self.tt_point, self.workdir, timeout_s=1)
            elapsed = time.monotonic() - started
        self.assertEqual(result.status, "timeout")
        self.assertIn("deck", result.message)
        self.assertLess(elapsed, 15, "in-process guard should not wait past its own bound")
        self.assertIn("TIMEOUT", (self.workdir / result.log_name).read_text())
        # The fake ngspice process itself must actually be dead, not merely
        # unwaited-for -- this is exactly what the incident's ngspice failed
        # to do (it ran ~4.5h with nothing left to enforce a bound).
        self._assert_process_is_dead(int(pidfile.read_text()))

    @unittest.skipUnless(runner.timeout_bin(), "no timeout(1)/gtimeout on PATH")
    def test_watchdog_kills_the_whole_process_group_including_children(self):
        grandchild_pidfile = self.tmp_path_for("grandchild.pid")
        self.workdir.mkdir(parents=True, exist_ok=True)
        _install_fake_ngspice(
            self.bin_dir,
            "#!/usr/bin/env python3\n"
            "import os, signal, time\n"
            "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "pid = os.fork()\n"
            "if pid == 0:\n"
            "    signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            f"    open({str(grandchild_pidfile)!r}, 'w').write(str(os.getpid()))\n"
            "    time.sleep(120)\n"
            "else:\n"
            "    time.sleep(120)\n",
        )
        result = runner.run_one(self.tb, self.pdk, self.tt_point, self.workdir, timeout_s=1)
        self.assertEqual(result.status, "timeout")
        deadline = time.monotonic() + 5.0
        while not grandchild_pidfile.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue(grandchild_pidfile.exists(), "grandchild never even started")
        # A kill of only the direct child (ngspice) would leave this
        # grandchild running -- exactly the AC #2 regression this guards.
        self._assert_process_is_dead(int(grandchild_pidfile.read_text()))

    def test_parallel_hung_and_quick_runs_have_independent_timeouts(self):
        """A hung corner must not delay or extend a sibling's own bound
        (the -j/ThreadPoolExecutor edge case from issue #83's test plan).
        Both share the one fake ``ngspice`` on PATH; it tells the two apart
        by which corner's deck it was asked to run (embedded in the deck
        filename by ``compose_deck``)."""
        _install_fake_ngspice(
            self.bin_dir,
            "#!/usr/bin/env python3\n"
            "import sys, time\n"
            "deck = sys.argv[-1]\n"
            "if 'ss_' in deck:\n"
            "    time.sleep(120)\n"
            "else:\n"
            "    print('m_vout = 1.0')\n",
        )
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            started = time.monotonic()
            slow = pool.submit(
                runner.run_one, self.tb, self.pdk, self.ss_point,
                self.workdir / "ss", timeout_s=2,
            )
            fast = pool.submit(
                runner.run_one, self.tb, self.pdk, self.tt_point,
                self.workdir / "tt", timeout_s=30,
            )
            fast_result = fast.result(timeout=10)
            fast_elapsed = time.monotonic() - started
            slow_result = slow.result(timeout=10)

        self.assertEqual(fast_result.status, "ok")
        self.assertEqual(slow_result.status, "timeout")
        # The fast corner must not have been held up waiting on the slow
        # one's own (much longer) bound.
        self.assertLess(fast_elapsed, 5.0)

    def tmp_path_for(self, name: str) -> Path:
        return Path(self.tmp.name) / name


if __name__ == "__main__":
    unittest.main()
