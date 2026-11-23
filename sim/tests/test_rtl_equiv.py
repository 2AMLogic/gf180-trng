#!/usr/bin/env python3
"""Unit tests for ``sim/tests/_rtl_equiv.py`` (#1055): the one Icarus Verilog
runner behind the five RTL/model equivalence test modules.

The runner's contracts are pinned here with a stand-in for ``subprocess.run``,
so nothing depends on what this machine has installed:

* the argv is the one every ``tb_rtl_equivalence.v`` expects: ``iverilog
  -g2012``, ``-I <dir>`` per include directory, ``-o <image>``, then the
  sources; and ``+stim`` / ``+out`` / ``+nvec`` for the equivalence protocol;
* every tool call is made with ``check=True, capture_output=True,
  text=True``, and a non-zero exit of either tool propagates as the genuine
  ``CalledProcessError``;
* ``FATAL`` on ``vvp``'s stdout -- how a harness says it could not run while
  still exiting 0 -- is an ``AssertionError`` carrying that stdout;
* the result is the stripped, non-blank lines of the ``+out`` file, and
  ``[]`` when that file is empty or was never written.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _rtl_equiv as equiv  # noqa: E402

SOURCES = [Path("/rtl/dut.v"), Path("/tb/tb_rtl_equivalence.v")]
INCLUDES = [Path("/rtl/include")]
RUN_KWARGS = {"check": True, "capture_output": True, "text": True}

#: What the five harnesses print before ``$finish`` when they cannot run.
HARNESS_FATAL_LINES = (
    "FATAL: +nvec=<n> is required\n",
    "FATAL: +stim=<path> is required\n",
    "FATAL: +out=<path> is required\n",
    "FATAL: nvec 200000 exceeds MAX_VEC 1048576\n",
    "FATAL: cannot open output file\n",
)


class FakeRun:
    """Stands in for ``subprocess.run``.

    Records every argv and keyword arguments. ``stdout`` is replayed per
    tool. A tool named in ``failing`` is swapped for a real command that
    exits non-zero and run through the real ``subprocess.run`` with the
    caller's keyword arguments, so the ``check=True`` path under test is the
    genuine article. When ``vvp`` is run, the contents of the ``+stim`` file
    are recorded in ``stimulus``, and if ``out_text`` is not ``None`` it is
    written to the ``+out`` path -- by default nothing is written there, so
    the file does not exist afterwards.
    """

    def __init__(self, stdout=(), failing=(), out_text=None):
        self.stdout = dict(stdout)
        self.failing = set(failing)
        self.out_text = out_text
        self.calls: list[list[str]] = []
        self.kwargs: list[dict] = []
        self.stimulus: str | None = None

    def __call__(self, argv, **kwargs):
        argv = [str(arg) for arg in argv]
        self.calls.append(argv)
        self.kwargs.append(kwargs)
        tool = argv[0]
        if tool in self.failing:
            return subprocess.run([sys.executable, "-c", "raise SystemExit(3)"], **kwargs)
        if tool == "vvp":
            for arg in argv:
                if arg.startswith("+stim="):
                    self.stimulus = Path(arg[len("+stim="):]).read_text()
                elif arg.startswith("+out=") and self.out_text is not None:
                    Path(arg[len("+out="):]).write_text(self.out_text)
        return subprocess.CompletedProcess(argv, 0, self.stdout.get(tool, ""), "")


def image_path(run: FakeRun) -> str:
    """The ``-o`` argument of the recorded ``iverilog`` call."""
    return run.calls[0][run.calls[0].index("-o") + 1]


def plusargs(run: FakeRun) -> dict[str, str]:
    """The recorded ``vvp`` call's plusargs as ``{name: value}``."""
    return dict(arg[1:].split("=", 1) for arg in run.calls[1][2:])


def run_equivalence(run: FakeRun, **overrides) -> list[str]:
    options = dict(stimulus="0101\n", nvec=4, include_dirs=INCLUDES, run=run)
    return equiv.run_rtl_equivalence(SOURCES, **{**options, **overrides})


class CompileArgvTests(unittest.TestCase):
    def test_include_dirs_output_and_sources_follow_the_language_flag(self):
        run = FakeRun()
        equiv.compile_and_run_vvp(SOURCES, include_dirs=INCLUDES, run=run)
        self.assertEqual(run.calls[0], [
            "iverilog", "-g2012", "-I", str(INCLUDES[0]),
            "-o", image_path(run), *(str(s) for s in SOURCES),
        ])
        self.assertEqual(run.calls[1], ["vvp", image_path(run)])

    def test_no_include_dirs_means_no_include_flags(self):
        run = FakeRun()
        equiv.compile_and_run_vvp(SOURCES, run=run)
        self.assertEqual(run.calls[0], [
            "iverilog", "-g2012", "-o", image_path(run), *(str(s) for s in SOURCES),
        ])

    def test_every_include_dir_gets_its_own_flag_in_order(self):
        run = FakeRun()
        equiv.compile_and_run_vvp(SOURCES, include_dirs=["/a", "/b"], run=run)
        self.assertEqual(run.calls[0][2:6], ["-I", "/a", "-I", "/b"])

    def test_sources_may_be_given_as_plain_strings(self):
        run = FakeRun()
        equiv.compile_and_run_vvp(["/rtl/dut.v"], run=run)
        self.assertEqual(run.calls[0][-1], "/rtl/dut.v")

    def test_plusargs_are_handed_to_vvp_verbatim(self):
        run = FakeRun()
        equiv.compile_and_run_vvp(SOURCES, plusargs=["+k=8", "+verbose"], run=run)
        self.assertEqual(run.calls[1], ["vvp", image_path(run), "+k=8", "+verbose"])


class VvpStdoutTests(unittest.TestCase):
    def test_vvp_stdout_is_returned_as_is(self):
        run = FakeRun(stdout={"vvp": "done\n"})
        self.assertEqual(equiv.compile_and_run_vvp(SOURCES, run=run), "done\n")

    def test_stdout_is_empty_when_vvp_prints_nothing(self):
        self.assertEqual(equiv.compile_and_run_vvp(SOURCES, run=FakeRun()), "")


class RunKwargsTests(unittest.TestCase):
    def test_both_runners_check_capture_and_decode_every_tool_call(self):
        for name, runner in (
            ("compile_and_run_vvp", lambda run: equiv.compile_and_run_vvp(SOURCES, run=run)),
            ("run_rtl_equivalence", run_equivalence),
        ):
            with self.subTest(runner=name):
                run = FakeRun()
                runner(run)
                self.assertEqual([call[0] for call in run.calls], ["iverilog", "vvp"])
                self.assertEqual(run.kwargs, [RUN_KWARGS, RUN_KWARGS])


class EquivalenceProtocolTests(unittest.TestCase):
    def test_stimulus_is_written_to_the_plus_stim_file(self):
        run = FakeRun(out_text="")
        run_equivalence(run, stimulus="0101\n1100\n")
        self.assertEqual(run.stimulus, "0101\n1100\n")

    def test_stim_out_and_nvec_are_all_passed_and_nothing_else_is(self):
        run = FakeRun(out_text="")
        run_equivalence(run, nvec=19)
        self.assertEqual(set(plusargs(run)), {"stim", "out", "nvec"})
        self.assertEqual(plusargs(run)["nvec"], "19")

    def test_include_dirs_reach_iverilog_through_the_equivalence_runner(self):
        run = FakeRun(out_text="")
        run_equivalence(run, include_dirs=INCLUDES)
        self.assertEqual(run.calls[0][2:4], ["-I", str(INCLUDES[0])])
        self.assertEqual(run.calls[0][6:], [str(s) for s in SOURCES])


class OutputTests(unittest.TestCase):
    def test_returns_the_stripped_non_blank_lines_of_the_out_file(self):
        run = FakeRun(out_text="0000abcd 00000000 10000\n\n  ff 1 0  \n")
        self.assertEqual(run_equivalence(run), ["0000abcd 00000000 10000", "ff 1 0"])

    def test_empty_out_file_is_an_empty_list(self):
        self.assertEqual(run_equivalence(FakeRun(out_text="")), [])

    def test_out_file_never_written_is_an_empty_list(self):
        self.assertEqual(run_equivalence(FakeRun()), [])


class FailureTests(unittest.TestCase):
    def test_non_zero_iverilog_exit_propagates_called_process_error(self):
        run = FakeRun(failing=["iverilog"])
        with self.assertRaises(subprocess.CalledProcessError) as raised:
            run_equivalence(run)
        self.assertEqual(raised.exception.returncode, 3)
        self.assertEqual([call[0] for call in run.calls], ["iverilog"])

    def test_non_zero_vvp_exit_propagates_called_process_error(self):
        run = FakeRun(failing=["vvp"])
        with self.assertRaises(subprocess.CalledProcessError) as raised:
            run_equivalence(run)
        self.assertEqual(raised.exception.returncode, 3)

    def test_every_harness_fatal_line_is_an_assertion_error_carrying_stdout(self):
        for stdout in HARNESS_FATAL_LINES:
            with self.subTest(stdout=stdout):
                run = FakeRun(stdout={"vvp": stdout})
                with self.assertRaises(AssertionError) as raised:
                    run_equivalence(run)
                self.assertEqual(str(raised.exception), stdout)

    def test_fatal_is_also_checked_on_a_bare_vvp_run(self):
        run = FakeRun(stdout={"vvp": "FATAL: cannot open output file\n"})
        with self.assertRaises(AssertionError):
            equiv.compile_and_run_vvp(SOURCES, run=run)


if __name__ == "__main__":
    unittest.main()
