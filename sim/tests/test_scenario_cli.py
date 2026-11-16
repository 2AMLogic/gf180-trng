#!/usr/bin/env python3
"""Unit tests for sim/harness/scenario_cli.py: the shared ``--scenario`` /
``--no-write`` CLI contract every scenario testbench runner depends on (#917).

``run_scenarios`` decides *whether evidence is minted at all* for the four
behavioural runners that call it, so these tests stub all three injected
callables and pin the contract directly: scenario selection and ordering, the
``--no-write`` gate, the exact ``write_record`` arguments, and that
``repo_root`` / ``records_dir`` are used as passed rather than derived from
the helper's own location. No PDK, no ngspice, no simulation.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import report, scenario_cli  # noqa: E402


class _RunScenariosFixture:
    """Stubbed ``run_scenario`` / ``write_record`` / ``print_result``, a
    patched ``report.git_provenance``, and the stdout/stderr capture every
    invocation needs (``run_scenarios`` prints a header and a ``record:``
    line unconditionally; argparse writes usage to stderr).

    The scenario keys are deliberately non-alphabetical: with alphabetical
    keys an order assertion cannot distinguish declaration order from
    ``sorted()`` order -- and ``run_scenarios`` sorts only the argparse
    ``choices``, so an implementation that accidentally ran ``sorted()``
    would pass every green test except the order one.
    """

    SCENARIOS = {"zeta": "z", "alpha": "a", "mid": "m"}

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo_root = Path(tmp.name)
        self.records_dir = self.repo_root / "records"

        self.run_calls: list[str] = []
        self.results: list[dict] = []
        self.write_calls: list[tuple[dict, Path, dict]] = []
        self.provenance_calls: list[Path] = []
        self.git = {"commit": "a" * 40, "dirty": False}

        def fake_run_scenario(name: str) -> dict:
            self.run_calls.append(name)
            result = {"scenario": name, "value": len(self.run_calls)}
            self.results.append(result)
            return result

        def fake_write_record(result: dict, records_dir: Path, git: dict) -> Path:
            self.write_calls.append((result, records_dir, git))
            # The returned path must live under repo_root: run_scenarios
            # prints ``path.relative_to(repo_root)``, which raises ValueError
            # for a path outside it.
            return records_dir / f"{result['scenario']}.md"

        def fake_git_provenance(root: Path) -> dict:
            self.provenance_calls.append(root)
            return self.git

        # scenario_cli imports the module (``from . import report``), so
        # patching harness.report.git_provenance is sufficient.
        patcher = mock.patch.object(
            report, "git_provenance", side_effect=fake_git_provenance
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        self.fake_run_scenario = fake_run_scenario
        self.fake_write_record = fake_write_record

    def _run(self, argv, scenarios=None):
        scenarios = dict(self.SCENARIOS) if scenarios is None else scenarios
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = scenario_cli.run_scenarios(
                argv,
                description="scenario_cli contract tests",
                scenarios=scenarios,
                run_scenario=self.fake_run_scenario,
                write_record=self.fake_write_record,
                print_result=lambda result: None,
                repo_root=self.repo_root,
                records_dir=self.records_dir,
            )
        return rc, out.getvalue(), err.getvalue()


class DefaultRunTests(_RunScenariosFixture, unittest.TestCase):
    """With no ``--scenario``, every declared scenario runs, in order."""

    def test_runs_every_scenario_in_declaration_order(self):
        # ["zeta", "alpha", "mid"] is neither the sorted order
        # ["alpha", "mid", "zeta"] nor a prefix of it, so this fails against
        # a sorted() implementation.
        rc, _out, _err = self._run([])
        self.assertEqual(rc, 0)
        self.assertEqual(self.run_calls, ["zeta", "alpha", "mid"])

    def test_runs_every_scenario_exactly_once_and_prints_headers(self):
        rc, out, _err = self._run([])
        self.assertEqual(rc, 0)
        self.assertEqual(sorted(self.run_calls), sorted(self.SCENARIOS))
        self.assertEqual(len(self.run_calls), len(set(self.run_calls)))
        for name in self.SCENARIOS:
            self.assertIn(f"== {name} ==", out)

    def test_write_record_called_once_per_result_with_exact_args(self):
        self._run([])
        self.assertEqual(len(self.write_calls), 3)
        for i, (result, records_dir, git) in enumerate(self.write_calls):
            self.assertIs(result, self.results[i])
            self.assertEqual(records_dir, self.records_dir)
            # The git dict is the one report.git_provenance returned.
            self.assertIs(git, self.git)


class ScenarioSelectionTests(_RunScenariosFixture, unittest.TestCase):
    """``--scenario`` restricts the run to the names given, in CLI order."""

    def test_single_scenario_runs_only_that_one(self):
        rc, _out, _err = self._run(["--scenario", "alpha"])
        self.assertEqual(rc, 0)
        self.assertEqual(self.run_calls, ["alpha"])
        self.assertEqual(len(self.write_calls), 1)

    def test_repeated_scenario_runs_those_in_cli_order(self):
        # ["mid", "zeta", "alpha"] differs from both declaration order and
        # sorted order, so this pins CLI order specifically.
        argv = ["--scenario", "mid", "--scenario", "zeta", "--scenario", "alpha"]
        rc, _out, _err = self._run(argv)
        self.assertEqual(rc, 0)
        self.assertEqual(self.run_calls, ["mid", "zeta", "alpha"])
        self.assertEqual(len(self.write_calls), 3)

    def test_repeated_same_scenario_runs_it_twice(self):
        # Pin current behaviour: ``--scenario`` is a plain repeatable flag,
        # so naming the same scenario twice runs and mints it twice.
        rc, _out, _err = self._run(["--scenario", "alpha", "--scenario", "alpha"])
        self.assertEqual(rc, 0)
        self.assertEqual(self.run_calls, ["alpha", "alpha"])
        self.assertEqual(len(self.write_calls), 2)

    def test_unknown_scenario_exits_2_without_running(self):
        with self.assertRaises(SystemExit) as cm:
            self._run(["--scenario", "nope"])
        self.assertEqual(cm.exception.code, 2)
        self.assertEqual(self.run_calls, [])
        self.assertEqual(self.write_calls, [])
        self.assertEqual(self.provenance_calls, [])


class NoWriteTests(_RunScenariosFixture, unittest.TestCase):
    """``--no-write`` prints every result but never mints evidence."""

    def test_no_write_prints_every_scenario_but_never_mints(self):
        rc, out, _err = self._run(["--no-write"])
        self.assertEqual(rc, 0)
        self.assertEqual(self.run_calls, ["zeta", "alpha", "mid"])
        self.assertEqual(self.write_calls, [])
        self.assertNotIn("record:", out)


class PassedThroughPathsTests(_RunScenariosFixture, unittest.TestCase):
    """``repo_root`` / ``records_dir`` are used as passed, not derived from
    the helper's own location (scenario_cli.py module docstring, #896).

    Runners resolve these from their own module constants; resolving them
    relative to the harness package instead would change the provenance and
    the record path of every minted record.
    """

    def test_git_provenance_called_with_passed_repo_root(self):
        self._run(["--scenario", "mid"])
        self.assertEqual(self.provenance_calls, [self.repo_root])

    def test_write_record_receives_passed_records_dir(self):
        self._run(["--scenario", "mid"])
        (result, records_dir, git) = self.write_calls[0]
        self.assertEqual(records_dir, self.records_dir)


class EdgeCaseTests(_RunScenariosFixture, unittest.TestCase):
    def test_single_entry_mapping_runs_that_one(self):
        rc, _out, _err = self._run([], scenarios={"only": "o"})
        self.assertEqual(rc, 0)
        self.assertEqual(self.run_calls, ["only"])
        self.assertEqual(len(self.write_calls), 1)

    def test_every_success_path_returns_zero(self):
        success_argv = [
            [],
            ["--scenario", "alpha"],
            ["--scenario", "mid", "--scenario", "alpha"],
            ["--no-write"],
        ]
        for argv in success_argv:
            with self.subTest(argv=argv):
                rc, _out, _err = self._run(argv)
                self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
