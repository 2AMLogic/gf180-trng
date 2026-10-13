#!/usr/bin/env python3
"""Offline tests: guard against duplicated trnoise realizations (#605)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import corners, runner, testbench  # noqa: E402


def _tb(analysis_type: str) -> testbench.Testbench:
    tmp = tempfile.TemporaryDirectory()
    d = Path(tmp.name)
    (d / "x.spice").write_text("r1 out 0 1k\n")
    (d / "tb.json").write_text(json.dumps({
        "name": "x", "netlist": "x.spice", "measure": {"v": "v(out)"},
        "analysis_type": analysis_type, "analyses": ["tran 1n 1u"],
    }))
    tb = testbench.load(d)
    tmp.cleanup()
    return tb


def _res(seed, value, pid, status="ok"):
    point = corners.build_grid(corners.resolve_corners(None)[:1], [27.0], [1.0])[0]
    return runner.RunResult(
        point=point, seed=seed, status=status,
        measurements={"v": value} if value is not None else {}, pid=pid,
    )


class DuplicateRealizationTests(unittest.TestCase):
    def test_distinct_pids_and_values_pass(self):
        tb = _tb("tran-noise")
        self.assertEqual(
            runner.duplicate_realization_problem(
                tb, [_res(1, 0.1, 100), _res(2, 0.2, 101)]), "")

    def test_shared_pid_flagged(self):
        tb = _tb("tran-noise")
        msg = runner.duplicate_realization_problem(
            tb, [_res(1, 0.1, 1), _res(2, 0.2, 1)])
        self.assertIn("same process id 1", msg)
        self.assertIn("seeds 1, 2", msg)

    def test_identical_measurements_flagged(self):
        tb = _tb("tran-noise")
        msg = runner.duplicate_realization_problem(
            tb, [_res(1, 0.1, 10), _res(2, 0.1, 11)])
        self.assertIn("bit-identical", msg)

    def test_single_run_and_failed_runs_ignored(self):
        tb = _tb("tran-noise")
        self.assertEqual(runner.duplicate_realization_problem(tb, [_res(1, 0.1, 1)]), "")
        self.assertEqual(runner.duplicate_realization_problem(
            tb, [_res(1, 0.1, 1), _res(2, None, 1, status="failed")]), "")

    def test_other_analysis_types_not_checked(self):
        tb = _tb("mc")
        self.assertEqual(runner.duplicate_realization_problem(
            tb, [_res(1, 0.1, 1), _res(2, 0.1, 1)]), "")


if __name__ == "__main__":
    unittest.main()
