#!/usr/bin/env python3
"""Corner-sanity guardrail: does switching the process corner actually move
device behavior, or is the corner selection being silently ignored?

CLAUDE.md and this repo's harness issue: "a wrong process-corner mapping ...
would pass a smoke test and then contaminate every piece of append-only
evidence recorded downstream." This script is the automated check that
catches that failure mode before it reaches sim/records/.

Runs sim/tb/corner-sanity-nfet-id at tt/ss/ff (nominal supply, 27 C) and
asserts:
  1. ss < tt < ff for the drive current (slow corner draws least current,
     fast corner draws most -- the physically expected direction), and
  2. the ff-vs-ss spread exceeds a floor (a corner that "moves" by 0.001%
     is as suspicious as one that does not move at all).

Exit 0 on success, 1 on failure. No PDK/ngspice = this script cannot run
(caller -- sim/selftest.sh -- only invokes it once --check-env has passed).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import corners, testbench, runner  # noqa: E402
from harness.pdk import find_pdk  # noqa: E402

MIN_SPREAD_PCT = 1.0  # ff-vs-ss must differ by at least this fraction of tt


def evaluate(ids: dict[str, float]) -> tuple[bool, str]:
    """Pure pass/fail decision on the ss/tt/ff drive currents (no ngspice).

    Returns ``(ok, message)``. On success the message holds the spread line and
    the PASS line; on failure it holds the FAIL line.
    """
    if not ids["ss"] < ids["tt"] < ids["ff"]:
        return False, (
            f"FAIL: expected Id(ss) < Id(tt) < Id(ff); got "
            f"{ids['ss']:.6e} / {ids['tt']:.6e} / {ids['ff']:.6e} -- "
            "process corner selection does not appear to be taking effect."
        )

    if ids["tt"] <= 0:
        return False, (
            f"FAIL: Id(tt) = {ids['tt']:.6e} is not positive, so the spread "
            "relative to tt is undefined."
        )

    spread_pct = (ids["ff"] - ids["ss"]) / ids["tt"] * 100.0
    if spread_pct < MIN_SPREAD_PCT:
        return False, (
            f"FAIL: ff-vs-ss spread is only {spread_pct:.3f}% of tt "
            f"(floor is {MIN_SPREAD_PCT}%) -- corner selection may be silently "
            "ignored even though the ordering happens to look right."
        )

    return True, (
        f"spread  = {spread_pct:.2f}% (ff vs ss, relative to tt)\n"
        "PASS: process corner selection measurably changes device behavior."
    )


def main() -> int:
    tb = testbench.load(SIM_DIR / "tb" / "corner-sanity-nfet-id")
    pdk = find_pdk()

    ids: dict[str, float] = {}
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        for corner_name in ("tt", "ss", "ff"):
            point = corners.build_grid(
                corners.resolve_corners([corner_name]), (27.0,), [3.3]
            )[0]
            results = runner.run_point(tb, pdk, point, workdir / corner_name, seeds=None)
            result = results[0]
            if result.status != "ok" or "id" not in result.measurements:
                print(f"error: {corner_name} run did not produce an 'id' measurement: "
                      f"{result.status} {result.message}", file=sys.stderr)
                return 1
            ids[corner_name] = result.measurements["id"]

    print(f"Id(ss) = {ids['ss']:.6e} A")
    print(f"Id(tt) = {ids['tt']:.6e} A")
    print(f"Id(ff) = {ids['ff']:.6e} A")

    ok, message = evaluate(ids)
    print(message, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
