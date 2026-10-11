#!/usr/bin/env python3
"""Unit tests for ``sim/tests/_tool_gate.py`` (#618): the shared skip gate
for tests that need an external simulator on PATH.

The gate has two contracts and both are pinned here with a fake ``which`` and
a fake environment, so nothing depends on what this machine has installed:

* switch unset: exactly ``unittest.skipUnless`` -- skip with the given
  message when a tool is missing, run normally when all are present;
* ``REQUIRE_RTL_TOOLS=1``: a missing tool fails (class: in ``setUpClass``;
  method: in the method) with a message naming each missing tool, and a
  present tool still runs normally.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _tool_gate as gate  # noqa: E402

STRICT = {gate.STRICT_ENV: "1"}
LAX: dict[str, str] = {}


def which_only(*present):
    return lambda name: f"/fake/bin/{name}" if name in present else None


def run_case(case_cls) -> unittest.TestResult:
    result = unittest.TestResult()
    unittest.defaultTestLoader.loadTestsFromTestCase(case_cls).run(result)
    return result


def gated_class(environ, which, reason="tool missing -- not checked here"):
    @gate.requires_tools("iverilog", "vvp", reason=reason, environ=environ, which=which)
    class Gated(unittest.TestCase):
        ran: list[str] = []

        def test_body(self):
            type(self).ran.append("body")

    Gated.ran = []
    return Gated


def gated_method(environ, which, reason="ngspice missing -- probe skipped"):
    class Holder(unittest.TestCase):
        ran: list[str] = []

        @gate.requires_tools("ngspice", reason=reason, environ=environ, which=which)
        def test_probe(self):
            type(self).ran.append("probe")

    Holder.ran = []
    return Holder


class StrictModeSwitchTests(unittest.TestCase):
    def test_only_exactly_one_enables_strict_mode(self):
        self.assertTrue(gate.strict_mode({gate.STRICT_ENV: "1"}))
        for value in ("", "0", "true", "yes", " 1"):
            self.assertFalse(gate.strict_mode({gate.STRICT_ENV: value}), value)
        self.assertFalse(gate.strict_mode({}))

    def test_missing_tools_keeps_the_requested_order(self):
        self.assertEqual(gate.missing_tools(["iverilog", "vvp", "ngspice"], which_only("vvp")),
                         ["iverilog", "ngspice"])

    def test_no_tool_names_is_a_programming_error(self):
        with self.assertRaises(ValueError):
            gate.requires_tools(reason="x", environ=LAX, which=which_only())


class DefaultSkipBehaviourTests(unittest.TestCase):
    def test_missing_tool_skips_the_class_with_the_given_message(self):
        reason = "Icarus Verilog not installed -- RTL/model equivalence not checked here"
        case = gated_class(LAX, which_only("vvp"), reason)
        result = run_case(case)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual([msg for _, msg in result.skipped], [reason])
        self.assertEqual(result.errors + result.failures, [])
        self.assertEqual(case.ran, [])

    def test_missing_tool_skips_the_method_with_the_given_message(self):
        reason = "ngspice not on PATH; snapshot probe skipped"
        case = gated_method(LAX, which_only(), reason)
        result = run_case(case)
        self.assertEqual([msg for _, msg in result.skipped], [reason])
        self.assertEqual(result.errors + result.failures, [])
        self.assertEqual(case.ran, [])

    def test_skip_matches_plain_skipunless_exactly(self):
        reason = "same words, same skip"

        @unittest.skipUnless(False, reason)
        class Plain(unittest.TestCase):
            def test_body(self):
                pass

        plain = run_case(Plain)
        ours = run_case(gated_class(LAX, which_only(), reason))
        self.assertEqual([m for _, m in plain.skipped], [m for _, m in ours.skipped])

    def test_present_tools_run_the_class_and_the_method(self):
        for environ in (LAX, STRICT):
            cls_case = gated_class(environ, which_only("iverilog", "vvp"))
            res = run_case(cls_case)
            self.assertTrue(res.wasSuccessful(), environ)
            self.assertEqual((res.testsRun, len(res.skipped), cls_case.ran), (1, 0, ["body"]))
            m_case = gated_method(environ, which_only("ngspice"))
            res = run_case(m_case)
            self.assertTrue(res.wasSuccessful(), environ)
            self.assertEqual((res.testsRun, len(res.skipped), m_case.ran), (1, 0, ["probe"]))


class StrictFailureTests(unittest.TestCase):
    def test_missing_tool_fails_the_class_naming_only_the_missing_tool(self):
        case = gated_class(STRICT, which_only("vvp"))
        result = run_case(case)
        self.assertEqual(result.skipped, [])
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(case.ran, [])
        text = "".join(tb for _, tb in result.errors + result.failures)
        self.assertIn(f"{gate.STRICT_ENV}=1", text)
        self.assertIn("not on PATH: iverilog", text)
        self.assertNotIn("vvp (", text)

    def test_every_missing_tool_is_named(self):
        case = gated_class(STRICT, which_only())
        text = "".join(tb for _, tb in run_case(case).errors)
        self.assertIn("not on PATH: iverilog, vvp", text)

    def test_missing_tool_fails_the_method_naming_the_tool(self):
        case = gated_method(STRICT, which_only())
        result = run_case(case)
        self.assertEqual(result.skipped, [])
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(case.ran, [])
        self.assertIn("not on PATH: ngspice", result.failures[0][1])

    def test_failure_message_keeps_the_skip_reason_for_context(self):
        reason = "Icarus Verilog not installed -- trng_top.v is not compile-checked here"
        msg = gate.strict_failure_message(["iverilog"], reason)
        self.assertIn("iverilog", msg)
        self.assertIn(reason, msg)


if __name__ == "__main__":
    unittest.main()
