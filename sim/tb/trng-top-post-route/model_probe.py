#!/usr/bin/env python3
"""The registered-handoff probe: a hypothesis about why the model diverges.

Kept in its own module, importable **without cocotb**, for two reasons: the
cocotb regression (`post_route_tb.py`) uses it, and so does
`sim/tests/test_post_route_scenarios.py`, which runs on the PR-blocking CI
path where no simulator, no PDK and no cocotb exist. The finding this encodes
is worth a test that runs everywhere, not only on a host that can simulate a
gate netlist.

The finding (#176), in one paragraph
-------------------------------------
``design/trng_top/trng_top.py``'s ``TopLevel.step`` hands the interface *last*
cycle's ``ht_fail_rct`` / ``ht_fail_apt`` / ``ring_stuck_any`` (its ``_last_*``
fields, matching ``rct_apt.v``'s and ``ring_liveness.v``'s ``output reg``
ports) but passes two other cross-block signals **combinationally within the
same cycle**, even though the RTL registers both:

1. ``ht_startup_pass`` -- ``rct_apt.v`` declares it ``output reg``, exactly
   like the three flags the model does delay. So the model un-gates the
   conditioned path one raw sample earlier than the hardware, which shifts the
   first 256-bit conditioner block by one raw bit and therefore changes the
   conditioned word itself.
2. ``cond_word`` / ``cond_valid`` -- ``crc32_conditioner.v`` declares both
   ``output reg`` (a registered one-cycle strobe), so the interface sees a
   conditioned word the cycle *after* the sample that completed the block.

Applying exactly these two delays and nothing else makes the model agree with
both the RTL and the post-route netlist, cycle for cycle, on every scenario --
which is what turns "probably this is why" into a measurement.

Both classes **wrap** a block model rather than reimplementing
``TopLevel.step``: a copy of the model's step function living in a testbench
would silently drift from the model it is supposed to be probing.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

for _path in (
    REPO_ROOT / "design" / "trng_top",
    REPO_ROOT / "design" / "conditioner",
    REPO_ROOT / "design" / "health_test",
    REPO_ROOT / "design" / "interface",
):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import trng_top as top  # noqa: E402


class RegisteredHealthStartup:
    """Delay the health-test model's ``ht_startup_pass`` by one cycle."""

    def __init__(self, inner) -> None:
        self._inner = inner
        self._held = False

    def step(self, **kwargs):
        rct, apt, startup = self._inner.step(**kwargs)
        out = (rct, apt, self._held)
        self._held = startup
        return out

    def __getattr__(self, name):
        return getattr(self._inner, name)


class RegisteredConditionerOutput:
    """Delay the conditioner model's ``(cond_word, cond_valid)`` by one cycle."""

    def __init__(self, inner) -> None:
        self._inner = inner
        self._held: tuple[int, bool] = (0, False)

    def step(self, **kwargs):
        nxt = self._inner.step(**kwargs)
        out, self._held = self._held, nxt
        return out

    def __getattr__(self, name):
        return getattr(self._inner, name)


def registered_handoff_model():
    """A ``TopLevel`` with both cross-block handoffs registered like the RTL's."""
    model = top.TopLevel()
    model.health = RegisteredHealthStartup(model.health)
    model.cond = RegisteredConditionerOutput(model.cond)
    return model


def as_committed_model():
    """A plain ``TopLevel`` -- the model as committed, for the same stimulus."""
    return top.TopLevel()


#: The four `trng_top` outputs both sides are compared on, in a fixed order.
OUTPUT_PORTS = ("reg_rdata", "str_data", "str_valid", "ht_alarm")


def outputs(step_result) -> tuple[int, ...]:
    return (
        int(step_result.reg_rdata),
        int(step_result.str_data),
        int(bool(step_result.str_valid)),
        int(bool(step_result.ht_alarm)),
    )


def diverging_cycles(rows) -> list[int]:
    """Cycles on which the as-committed model and the probe differ on any
    top-level output, over ``rows`` of stimulus.

    Pure Python, no simulator: since the probe is known (from the gate-level
    run) to agree with both the RTL and the netlist exactly, this count is
    also the number of cycles on which the *as-committed model* differs from
    the implementation -- which is how a CI-cheap test can pin a finding that
    was made with a gate-level simulation.
    """
    committed = as_committed_model()
    probe = registered_handoff_model()
    return [
        index
        for index, row in enumerate(rows)
        if outputs(committed.step(**row)) != outputs(probe.step(**row))
    ]
