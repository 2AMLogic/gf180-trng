"""The one skip gate for unit tests that need an external simulator (#618).

Several test classes carry real verification that can only run with an
external tool on PATH: the RTL/model equivalence and fault-injection checks
need Icarus Verilog (``iverilog`` + ``vvp``), and two runner probes need
``ngspice``. On a contributor machine without the tool those tests SKIP, with
a message saying what was not checked -- they never silently pass.

A skip is the right answer on a laptop and the wrong answer in the one CI
environment that is supposed to exercise the RTL: there, a missing tool would
turn every RTL check into a green skip. So this gate has a strict switch:

* ``REQUIRE_RTL_TOOLS`` unset (or anything but ``1``): identical to
  ``unittest.skipUnless(all tools on PATH, reason)`` -- same skip, same
  message.
* ``REQUIRE_RTL_TOOLS=1``: a missing tool is a FAILURE naming each missing
  tool. A decorated class fails in ``setUpClass`` (one error per class); a
  decorated test method fails in the method.

The nightly workflow (``.github/workflows/pdk-nightly.yml``) installs the
tools and runs ``npm run test`` with the switch set. Every tool-gated skip in
the unit-test trees must go through :func:`requires_tools`; this is enforced
by ``sim/tests/test_tool_gate_discipline.py``, so a new RTL test cannot opt
out of the strict mode by writing its own ``skipUnless(shutil.which(...))``.
"""

from __future__ import annotations

import functools
import inspect
import os
import shutil
import unittest
from collections.abc import Callable, Mapping

#: Environment switch that turns a missing tool from a skip into a failure.
STRICT_ENV = "REQUIRE_RTL_TOOLS"

#: Tools whose gates must go through :func:`requires_tools` (checked by the
#: discipline test). Adding a tool here widens that check.
GATED_TOOLS = frozenset({"iverilog", "vvp", "ngspice"})


def strict_mode(environ: Mapping[str, str] | None = None) -> bool:
    """True when the strict switch is set to exactly ``1``."""
    env = os.environ if environ is None else environ
    return env.get(STRICT_ENV) == "1"


def missing_tools(names, which: Callable[[str], str | None] = shutil.which) -> list[str]:
    """The subset of ``names`` not found on PATH, in the order given."""
    return [name for name in names if not which(name)]


def strict_failure_message(missing, reason: str) -> str:
    return (
        f"{STRICT_ENV}=1 but required tool(s) not on PATH: "
        f"{', '.join(missing)} (without {STRICT_ENV} this test would be "
        f"skipped: {reason})"
    )


def requires_tools(
    *names: str,
    reason: str,
    environ: Mapping[str, str] | None = None,
    which: Callable[[str], str | None] = shutil.which,
):
    """Decorator for a test class or method that needs ``names`` on PATH.

    ``environ`` and ``which`` exist for this module's own tests; real callers
    pass only the tool names and the skip reason.
    """
    if not names:
        raise ValueError("requires_tools needs at least one tool name")
    missing = missing_tools(names, which)
    if not missing:
        return lambda obj: obj
    if not strict_mode(environ):
        return unittest.skip(reason)
    message = strict_failure_message(missing, reason)

    def fail_loudly(obj):
        if inspect.isclass(obj):
            def setUpClass(cls):  # noqa: N802 -- unittest's hook name
                raise unittest.TestCase.failureException(message)

            obj.setUpClass = classmethod(setUpClass)
            return obj

        @functools.wraps(obj)
        def wrapper(self, *args, **kwargs):
            self.fail(message)

        return wrapper

    return fail_loudly
