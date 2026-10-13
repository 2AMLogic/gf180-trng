#!/usr/bin/env python3
"""Seeded workloads for the post-route switching-activity campaign (#453).

DR-0023 made the digital power term a gate-level measurement but priced it at
a *uniform* declared activity. This module declares the per-cycle stimulus for
the workloads whose activity that uniform number cannot distinguish, so the
same post-route netlist can be simulated under each and its per-net toggling
handed to OpenSTA (``sim/tb/digital-sta-power/run_sta.py --activity``).

Every workload is a plain list of per-cycle rows in the shape
``scenarios.cycle`` returns (plus ``rst_n``), built from the same seeded
source models ``scenarios.py`` reuses. No simulator, no netlist: importable
and cheap. The raw bits are synthetic -- they exercise the logic and make no
entropy claim.

Each workload declares **capture windows** as half-open cycle ranges, because
reset, DR-0002's 1024-sample start-up window and steady operation are
different activity regimes and a single whole-run average would blur them:

* ``reset``   -- ``rst_n`` low; the first cycles only.
* ``startup`` -- from reset release through the end of the start-up window
  (the conditioned path is still gated for most of it).
* ``steady``  -- everything after, i.e. the regime a long-running block lives
  in. For ``alarm-gated`` it begins only after the latched health alarm is
  asserted, so it is the alarm-gated steady state and not the onset.

The workloads:

``conditioned-streaming``  default CTRL (conditioned), ``str_ready`` held 1.
``raw-streaming``          CTRL.OUT_MODE = raw, ``str_ready`` held 1.
``backpressure``           conditioned, consumer stalled (str_ready never
                           asserts): the FIFO fills and later words overflow.
``alarm-gated``            ring 1 goes stuck after start-up; DR-0016 latches
                           ``ht_alarm`` and gates the conditioned path while
                           the raw tap keeps running.
``disabled-clock-running`` CTRL.EN = 0, raw tap idle, clock running -- the
                           "disabled but clocked" case, which is NOT the same
                           thing as a stopped clock (leakage only).
"""

from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass, field
from pathlib import Path

TB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TB_DIR))

import scenarios as sc  # noqa: E402

#: Cycles with rst_n low at the start of every workload.
RESET_CYCLES = 8
#: DR-0002's start-up window plus a little slack for the registered handoffs.
STARTUP_CYCLES = sc.STARTUP_SAMPLES + 16
#: Steady-state cycles captured after the start-up window.
STEADY_CYCLES = 1024
#: Cycles between ring-1 going stuck and the steady window opening in the
#: alarm-gated workload: C_LIVE to latch plus slack for the handoffs.
ALARM_SETTLE_CYCLES = sc.C_LIVE + 16

#: Declared seed of every workload (recorded in the manifest). One base seed;
#: each workload derives its own labels so streams are independent.
BASE_SEED = 453

#: The clock period the campaign is simulated at, ns. 1 MHz is DR-0003's
#: ratified raw rate, i.e. the operating point DR-0023's active-power row is
#: priced at, so observed activity in transitions per second is directly
#: comparable with the uniform baseline at that rate.
SIM_CLOCK_NS = 1000.0


@dataclass(frozen=True)
class Workload:
    name: str
    why: str
    seed: int
    build: object  # () -> (rows, windows)
    #: What the clock does. Always running in this campaign; a stopped clock
    #: is the leakage-only case and is reported from the leakage column.
    clock: str = "running, 50 % duty, 1 MHz"
    notes: tuple[str, ...] = field(default_factory=tuple)


def _row(**kw) -> dict:
    row = sc.cycle(**{k: v for k, v in kw.items() if k != "rst_n"})
    row["rst_n"] = int(kw.get("rst_n", 1))
    return row


def _reset_rows() -> list[dict]:
    return [_row(rst_n=0) for _ in range(RESET_CYCLES)]


def _windows(reset_end: int, startup_end: int, total: int) -> dict[str, tuple[int, int]]:
    return {
        "reset": (0, reset_end),
        "startup": (reset_end, startup_end),
        "steady": (startup_end, total),
    }


def _streaming(label: str, seed: int, *, raw_mode: bool, ready) -> tuple[list[dict], dict]:
    n = STARTUP_CYCLES + STEADY_CYCLES
    bits, _p, _t = sc.source_model.biased_bits(label, seed, n, sc.DECLARED_H)
    rows = _reset_rows()
    for i in range(n):
        if raw_mode and i == 0:
            rows.append(_row(reg_sel=True, reg_write=True, reg_addr=sc.CTRL,
                             reg_wdata=sc.CTRL_OUT_MODE_RAW, raw_bit=bits[i],
                             raw_valid=True, str_ready=ready(i)))
        else:
            rows.append(_row(raw_bit=bits[i], raw_valid=True, str_ready=ready(i)))
    body = sc.with_healthy_rings(rows[RESET_CYCLES:], label, seed + 10)
    rows = rows[:RESET_CYCLES] + [dict(r) for r in body]
    for r in rows[RESET_CYCLES:]:
        r["rst_n"] = 1
    return rows, _windows(RESET_CYCLES, RESET_CYCLES + STARTUP_CYCLES, len(rows))


def _conditioned_streaming() -> tuple[list[dict], dict]:
    return _streaming("act-conditioned", BASE_SEED, raw_mode=False, ready=lambda i: True)


def _raw_streaming() -> tuple[list[dict], dict]:
    return _streaming("act-raw", BASE_SEED + 1, raw_mode=True, ready=lambda i: True)


def _backpressure() -> tuple[list[dict], dict]:
    # Consumer fully stalled: str_ready never asserts, so the output FIFO
    # fills and later conditioned words overflow (STATUS.OVF_DATA).
    return _streaming("act-backpressure", BASE_SEED + 2, raw_mode=False,
                      ready=lambda i: False)


def _alarm_gated() -> tuple[list[dict], dict]:
    n_lead = STARTUP_CYCLES
    n_fault = ALARM_SETTLE_CYCLES + STEADY_CYCLES
    n = n_lead + n_fault
    bits, _p, _t = sc.source_model.biased_bits("act-alarm", BASE_SEED + 3, n, sc.DECLARED_H)
    healthy = sc.healthy_rings("act-alarm", BASE_SEED + 13, n)
    other = [healthy[i][1] for i in range(n)]
    frozen = healthy[n_lead - 1][0]
    rings = [healthy[i] for i in range(n_lead)] + [(frozen, other[i]) for i in range(n_lead, n)]
    rows = _reset_rows()
    for i in range(n):
        rows.append(_row(raw_bit=bits[i], raw_valid=True, ring_bit=rings[i], str_ready=True))
    startup_end = RESET_CYCLES + n_lead
    steady_start = startup_end + ALARM_SETTLE_CYCLES
    return rows, {
        "reset": (0, RESET_CYCLES),
        "startup": (RESET_CYCLES, startup_end),
        "steady": (steady_start, len(rows)),
    }


def _disabled_clock_running() -> tuple[list[dict], dict]:
    n = STARTUP_CYCLES + STEADY_CYCLES
    rows = _reset_rows()
    rows.append(_row(reg_sel=True, reg_write=True, reg_addr=sc.CTRL, reg_wdata=0))
    body = [_row() for _ in range(n - 1)]
    body = sc.with_healthy_rings(body, "act-disabled", BASE_SEED + 14)
    rows += body
    return rows, _windows(RESET_CYCLES, RESET_CYCLES + STARTUP_CYCLES, len(rows))


WORKLOADS: dict[str, Workload] = {
    "conditioned-streaming": Workload(
        "conditioned-streaming",
        "Default conditioned output, consumer always ready: the nominal "
        "streaming regime.", BASE_SEED, _conditioned_streaming),
    "raw-streaming": Workload(
        "raw-streaming",
        "CTRL.OUT_MODE = raw with the consumer always ready: the raw tap "
        "streamed straight out.", BASE_SEED + 1, _raw_streaming),
    "backpressure": Workload(
        "backpressure",
        "Conditioned output with a stalled consumer (str_ready never "
        "asserts): the output FIFO fills and later words overflow.",
        BASE_SEED + 2, _backpressure),
    "alarm-gated": Workload(
        "alarm-gated",
        "Ring 1 stuck after start-up: DR-0016 latches ht_alarm and gates the "
        "conditioned path while the raw tap keeps running; steady window is "
        "post-latch.", BASE_SEED + 3, _alarm_gated),
    "disabled-clock-running": Workload(
        "disabled-clock-running",
        "CTRL.EN = 0, raw tap idle, clock running: disabled operation with a "
        "running clock, not a stopped clock.", BASE_SEED + 4,
        _disabled_clock_running),
}


def pack_row(row: dict) -> int:
    """One row as a 48-bit word; layout mirrored by ``activity_tb.v``.

    [0] rst_n [1] raw_bit [2] raw_valid [4:3] ring_bit [5] reg_sel
    [6] reg_write [8:7] reg_addr [40:9] reg_wdata [41] str_ready
    """
    r0, r1 = row["ring_bit"]
    return (
        (row["rst_n"] & 1)
        | (row["raw_bit"] << 1)
        | (int(row["raw_valid"]) << 2)
        | (r0 << 3)
        | (r1 << 4)
        | (int(row["reg_sel"]) << 5)
        | (int(row["reg_write"]) << 6)
        | ((row["reg_addr"] & 3) << 7)
        | ((row["reg_wdata"] & 0xFFFFFFFF) << 9)
        | (int(row["str_ready"]) << 41)
    )


def stimulus_hex(rows: list[dict]) -> str:
    return "".join(f"{pack_row(r):012x}\n" for r in rows)


def stimulus_sha256(rows: list[dict]) -> str:
    return hashlib.sha256(stimulus_hex(rows).encode()).hexdigest()


def build(name: str) -> tuple[list[dict], dict[str, tuple[int, int]]]:
    rows, windows = WORKLOADS[name].build()
    return rows, windows


if __name__ == "__main__":  # pragma: no cover
    for name in WORKLOADS:
        rows, win = build(name)
        print(f"{name:26s} {len(rows):5d} cycles  {win}  sha256:{stimulus_sha256(rows)[:16]}")
