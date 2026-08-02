#!/usr/bin/env python3
"""The TRNG interface block's register map and port map -- the single source.

This module is **normative** for both the behavioural model
(``trng_interface.py``) and the synthesisable RTL (``trng_interface.v``):
every address, bit position and reset value used by either comes from the
tables below. The two committed artifacts

* ``design/interface/trng_regmap.vh`` -- Verilog header, `` `include``d by
  ``trng_interface.v``; and
* ``design/interface/REGMAP.md`` -- the integrator-facing register/port
  tables, which #16 (floorplan) and #27 (top-level integration) read,

are **generated** from these tables and committed, with a staleness guard in
the same spirit as ``design/netlist.py --check``::

    python3 design/interface/regmap.py            # (re-)generate both artifacts
    python3 design/interface/regmap.py --check    # never writes; fails if stale

``--check`` is what makes "the RTL, the model and the documented pinout agree"
a fact rather than a claim: the RTL cannot drift from this file without the
generated header drifting too, and the guard runs in the PR-blocking test set
(``sim/tests/test_interface.py``), so the drift fails the build rather than
being discovered by whoever integrates the block.

The map itself is fixed by
``spec/decision-records/DR-0013-interface-register-map-and-streaming-semantics.md``,
which derives it from DR-0001 (raw/conditioned paths, ``OUT_MODE``,
flush-on-switch) and DR-0002 (latch-and-gate failure behaviour).

Exit codes match ``design/netlist.py``: 0 up to date, 1 stale, 3 environment.
"""

from __future__ import annotations

import argparse
import difflib
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]

#: Register data width. One register is one 32-bit word.
REG_BITS = 32

#: Register address width. Registers are addressed by **word index**; the byte
#: offsets in the generated tables are for an integrator's byte-addressed bus
#: wrapper, which is #27's, not this block's.
ADDR_W = 2

#: Output-FIFO depth, in 32-bit words, for each of the two paths. A parameter
#: of the RTL; this is the default the model and the shipped RTL both use.
FIFO_DEPTH = 8

#: Width of the `*_LEVEL` STATUS fields -- enough for 0..FIFO_DEPTH inclusive.
LEVEL_BITS = 4

#: Raw samples packed into one streaming/`RAW_DATA` word, LSB first.
RAW_PACK_BITS = REG_BITS

EXIT_OK = 0
EXIT_STALE = 1
EXIT_ENVIRONMENT = 3


@dataclass(frozen=True)
class Field:
    """One field of one register."""

    name: str
    lsb: int
    width: int
    access: str  # RW | RO | W1C | W1S
    reset: int
    doc: str

    @property
    def msb(self) -> int:
        return self.lsb + self.width - 1

    @property
    def bits(self) -> str:
        return f"{self.msb}" if self.width == 1 else f"{self.msb}:{self.lsb}"


@dataclass(frozen=True)
class Register:
    """One 32-bit register."""

    name: str
    index: int
    access: str
    doc: str
    fields: tuple[Field, ...] = field(default_factory=tuple)

    @property
    def offset(self) -> int:
        return self.index * (REG_BITS // 8)

    @property
    def reset(self) -> int:
        value = 0
        for f in self.fields:
            value |= (f.reset & ((1 << f.width) - 1)) << f.lsb
        return value


@dataclass(frozen=True)
class Port:
    """One port of ``trng_interface``."""

    name: str
    direction: str  # in | out
    width: int
    group: str
    external: bool  # does this port leave the die at trng_top (#27 / #16)?
    doc: str


# ---------------------------------------------------------------------------
# The register map (DR-0013 §Decision)
# ---------------------------------------------------------------------------

CTRL = Register(
    name="CTRL",
    index=0,
    access="RW",
    doc="Block enable, output-path selection, and soft reset.",
    fields=(
        Field(
            "EN", 0, 1, "RW", 1,
            "Block enable. Reset value 1: the block starts acquiring and runs "
            "its start-up health test at power-on with no software write, "
            "which is what makes the ratified time-to-first-valid figure a "
            "property of the hardware. Writing 0 idles the block and flushes "
            "both paths; writing 1 again restarts the start-up test. This is "
            "an ordinary read/write control, not a lock bit (DR-0001 §4).",
        ),
        Field(
            "OUT_MODE", 1, 1, "RW", 0,
            "Streaming-port source: 0 = conditioned (reset default), "
            "1 = raw (DR-0001 §2). A write that *changes* this bit flushes the "
            "conditioner, both output FIFOs and the partial raw word, so no "
            "bit produced before the switch is readable after it.",
        ),
        Field(
            "SOFT_RESET", 2, 1, "W1S", 0,
            "Write 1 to flush both paths and restart the start-up health "
            "test. Self-clearing; reads 0. Does **not** clear the "
            "HT_FAIL_* latches -- DR-0002 makes write-1-to-clear the only "
            "way to clear those, so a soft reset cannot be used to escape a "
            "latched alarm.",
        ),
    ),
)

STATUS = Register(
    name="STATUS",
    index=1,
    access="RO/W1C",
    doc=(
        "Health-test latches, start-up/ready state, and FIFO occupancy. "
        "Read-only except the W1C bits."
    ),
    fields=(
        Field(
            "HT_FAIL_RCT", 0, 1, "W1C", 0,
            "Repetition Count Test failure, latched (DR-0002 §Failure "
            "behavior 1). Write 1 to clear.",
        ),
        Field(
            "HT_FAIL_APT", 1, 1, "W1C", 0,
            "Adaptive Proportion Test failure, latched. Write 1 to clear. "
            "Clearing the last set HT_FAIL_* bit restarts the noise source "
            "and the start-up health test (DR-0002 §Failure behavior 4).",
        ),
        Field(
            "HT_ALARM", 2, 1, "RO", 0,
            "HT_FAIL_RCT | HT_FAIL_APT | HT_FAIL_RING -- the same signal as "
            "the block-level `ht_alarm` output pin, so a register reader and a "
            "pin observer cannot disagree.",
        ),
        Field(
            "STARTUP", 3, 1, "RO", 1,
            "Start-up health test in progress: the conditioned path is gated "
            "but nothing has failed. Distinct from HT_ALARM by construction, "
            "so a reader can tell 'still starting up' from 'failed and "
            "gated'. Reset value 1.",
        ),
        Field(
            "COND_READY", 4, 1, "RO", 0,
            "Conditioned path is ungated: enabled, start-up test passed, no "
            "latched alarm. DATA reads and conditioned streaming return bits "
            "only while this is 1.",
        ),
        Field("DATA_AVAIL", 5, 1, "RO", 0, "Conditioned output FIFO is non-empty."),
        Field("RAW_AVAIL", 6, 1, "RO", 0, "Raw output FIFO is non-empty."),
        Field(
            "OVF_DATA", 7, 1, "W1C", 0,
            "A conditioned word was dropped because the FIFO was full. "
            "Latched; write 1 to clear. The *incoming* word is dropped, never "
            "a buffered one, so what remains in the FIFO is always a "
            "contiguous run -- and this bit is how a reader learns the run "
            "ended.",
        ),
        Field(
            "OVF_RAW", 8, 1, "W1C", 0,
            "A raw word was dropped because the raw FIFO was full. Latched; "
            "write 1 to clear. This is the bit that makes DR-0001's "
            "'non-consecutive samples silently invalidate the dataset' "
            "hazard detectable rather than silent.",
        ),
        Field(
            "HT_FAIL_RING", 9, 1, "W1C", 0,
            "Per-ring liveness failure, latched: at least one entropy-source "
            "ring's own digitized sample repeated C_LIVE times in a row "
            "(DR-0016). Write 1 to clear. Behaves exactly like HT_FAIL_RCT / "
            "HT_FAIL_APT -- it is a third source of the same latch, the same "
            "HT_ALARM and the same conditioned-path gate, and clearing the "
            "last set HT_FAIL_* bit restarts the noise source and the start-up "
            "health test. It sits at bit 9 rather than bit 2 because bits 0-8 "
            "were already published by DR-0013: a new failure source is an "
            "additive bit in the reserved space, never a renumbering of the "
            "ratified map. Distinct from HT_FAIL_RCT/HT_FAIL_APT because the "
            "observation point differs -- RCT/APT watch the XOR-combined raw "
            "tap, where one dead ring out of the shipped N=2 array is "
            "invisible; this bit is the only one that says 'a ring stopped'.",
        ),
        Field(
            "DATA_LEVEL", 16, LEVEL_BITS, "RO", 0,
            "Conditioned FIFO occupancy in 32-bit words, 0..FIFO_DEPTH.",
        ),
        Field(
            "RAW_LEVEL", 20, LEVEL_BITS, "RO", 0,
            "Raw FIFO occupancy in 32-bit words, 0..FIFO_DEPTH.",
        ),
    ),
)

DATA = Register(
    name="DATA",
    index=2,
    access="RO",
    doc=(
        "Conditioned output FIFO (DR-0001 §3). A read pops one word. Reads 0 "
        "and pops nothing while the conditioned path is gated (COND_READY = 0) "
        "or the FIFO is empty."
    ),
)

RAW_DATA = Register(
    name="RAW_DATA",
    index=3,
    access="RO",
    doc=(
        "Raw output FIFO -- 32 consecutive raw-tap samples per word, LSB "
        "first, undecimated. A read pops one word. Independent of OUT_MODE and "
        "never gated by health-test state (DR-0001 §3-§5). Reads 0 when empty."
    ),
)

REGISTERS: tuple[Register, ...] = (CTRL, STATUS, DATA, RAW_DATA)


# ---------------------------------------------------------------------------
# The port map (what #16 and #27 consume)
# ---------------------------------------------------------------------------

PORTS: tuple[Port, ...] = (
    Port("clk", "in", 1, "clock / reset", True,
         "Sampler clock (DR-0012: fixed external). The whole block, including "
         "the register bus, is synchronous to it."),
    Port("rst_n", "in", 1, "clock / reset", True,
         "Asynchronous power-on reset, active low."),

    Port("raw_bit", "in", 1, "sampler (#9)", False,
         "The DR-0001 raw tap -- `sampler_core.raw_bit`."),
    Port("raw_valid", "in", 1, "sampler (#9)", False,
         "`raw_bit` carries a new sample this cycle."),

    Port("cond_word", "in", REG_BITS, "conditioner (#8)", False,
         "Conditioned output word from `trng_conditioner_crc32`."),
    Port("cond_valid", "in", 1, "conditioner (#8)", False,
         "One-cycle strobe: `cond_word` is a completed block this cycle."),
    Port("cond_en", "out", 1, "conditioner (#8)", False,
         "Conditioned path enabled. Held low for the whole start-up-test "
         "window and while gated, per design/conditioner/README.md."),
    Port("cond_flush", "out", 1, "conditioner (#8)", False,
         "Synchronous flush request: asserted for one sampler clock on a "
         "health-test-failure gate, on an OUT_MODE change, and on any "
         "start-up restart."),

    Port("ht_fail_rct", "in", 1, "health tests (#11)", False,
         "One-cycle RCT failure pulse."),
    Port("ht_fail_apt", "in", 1, "health tests (#11)", False,
         "One-cycle APT failure pulse."),
    Port("ht_fail_ring", "in", 1, "health tests (#11)", False,
         "One-cycle per-ring liveness failure pulse -- "
         "`trng_ring_liveness.ring_stuck_any` (DR-0016). A third source of the "
         "same latch as ht_fail_rct/ht_fail_apt, on a different observation "
         "point (each ring's own digitized sample, not the combined raw tap)."),
    Port("ht_startup_pass", "in", 1, "health tests (#11)", False,
         "One-cycle pulse: 1024 consecutive raw samples passed both tests "
         "(DR-0002 §Failure behavior 4). Ignored unless STATUS.STARTUP."),
    Port("startup_req", "out", 1, "health tests (#11)", False,
         "One-cycle pulse: restart the noise source and the start-up test "
         "window. The health-test block must discard any in-flight window."),
    Port("ht_alarm", "out", 1, "health tests (#11)", True,
         "Block-level alarm output (DR-0002 §Failure behavior 1); mirrors "
         "STATUS.HT_ALARM."),

    Port("reg_sel", "in", 1, "register bus", True, "Register access this cycle."),
    Port("reg_write", "in", 1, "register bus", True, "1 = write, 0 = read."),
    Port("reg_addr", "in", ADDR_W, "register bus", True, "Register word index."),
    Port("reg_wdata", "in", REG_BITS, "register bus", True, "Write data."),
    Port("reg_rdata", "out", REG_BITS, "register bus", True,
         "Read data, combinational in the access cycle. A read with side "
         "effects (DATA, RAW_DATA) pops at the end of that cycle."),

    Port("str_data", "out", REG_BITS, "streaming port", True,
         "Streaming word: conditioned or raw per CTRL.OUT_MODE."),
    Port("str_valid", "out", 1, "streaming port", True,
         "`str_data` is valid. Deasserts immediately on a health-test gate in "
         "conditioned mode (DR-0002 §Failure behavior 2)."),
    Port("str_ready", "in", 1, "streaming port", True,
         "Consumer accepts a word this cycle. Transfer on valid && ready."),
)

MODULE = "trng_interface"

VH_PATH = HERE / "trng_regmap.vh"
MD_PATH = HERE / "REGMAP.md"

_GENERATED_BY = "design/interface/regmap.py"


def _vh_name(register: Register, f: Field) -> str:
    stem = f"TRNG_{register.name}_{f.name}"
    return stem


def verilog_header() -> str:
    """The generated Verilog header included by ``trng_interface.v``."""
    out: list[str] = [
        "// SPDX-License-Identifier: Apache-2.0",
        "//",
        f"// GENERATED by {_GENERATED_BY} -- do not edit by hand.",
        f"// `python3 {_GENERATED_BY} --check` fails if this file and the register",
        "// map disagree; regenerate with `python3 " + _GENERATED_BY + "`.",
        "//",
        "// The map itself is fixed by",
        "// spec/decision-records/DR-0013-interface-register-map-and-streaming-semantics.md.",
        "",
        "`ifndef TRNG_REGMAP_VH",
        "`define TRNG_REGMAP_VH",
        "",
        f"localparam integer TRNG_REG_BITS   = {REG_BITS};",
        f"localparam integer TRNG_ADDR_W     = {ADDR_W};",
        f"localparam integer TRNG_LEVEL_BITS = {LEVEL_BITS};",
        f"localparam integer TRNG_RAW_PACK_BITS = {RAW_PACK_BITS};",
        "",
        "// Register addresses (word index; byte offset = index * 4).",
    ]
    for register in REGISTERS:
        out.append(
            f"localparam [TRNG_ADDR_W-1:0] TRNG_ADDR_{register.name} "
            f"= {ADDR_W}'d{register.index};"
        )
    for register in REGISTERS:
        if not register.fields:
            continue
        out.append("")
        out.append(f"// {register.name} fields.")
        for f in register.fields:
            if f.width == 1:
                out.append(f"localparam integer {_vh_name(register, f)}_BIT = {f.lsb};")
            else:
                out.append(f"localparam integer {_vh_name(register, f)}_LSB = {f.lsb};")
                out.append(f"localparam integer {_vh_name(register, f)}_MSB = {f.msb};")
        out.append(
            f"localparam [TRNG_REG_BITS-1:0] TRNG_{register.name}_RESET "
            f"= {REG_BITS}'h{register.reset:08X};"
        )
    out += ["", "`endif  // TRNG_REGMAP_VH", ""]
    return "\n".join(out)


def _register_tables() -> list[str]:
    out: list[str] = []
    out.append("| Word | Byte offset | Register | Access | Reset | Purpose |")
    out.append("|---|---|---|---|---|---|")
    for r in REGISTERS:
        out.append(
            f"| {r.index} | `0x{r.offset:02X}` | `{r.name}` | {r.access} | "
            f"`0x{r.reset:08X}` | {r.doc} |"
        )
    for r in REGISTERS:
        if not r.fields:
            continue
        out += ["", f"### `{r.name}` (word {r.index}, byte offset `0x{r.offset:02X}`)", ""]
        out.append("| Bits | Field | Access | Reset | Meaning |")
        out.append("|---|---|---|---|---|")
        for f in r.fields:
            out.append(
                f"| `{f.bits}` | `{f.name}` | {f.access} | {f.reset} | {f.doc} |"
            )
        out.append("")
        out.append("Bits not listed are reserved: they read 0 and ignore writes.")
    return out


def _port_tables() -> list[str]:
    out: list[str] = []
    groups: list[str] = []
    for p in PORTS:
        if p.group not in groups:
            groups.append(p.group)
    for group in groups:
        out += ["", f"### {group}", ""]
        out.append("| Port | Dir | Width | Leaves the die | Meaning |")
        out.append("|---|---|---|---|---|")
        for p in PORTS:
            if p.group != group:
                continue
            out.append(
                f"| `{p.name}` | {p.direction} | {p.width} | "
                f"{'yes' if p.external else 'no (block-internal at trng_top)'} | "
                f"{p.doc} |"
            )
    return out


def markdown() -> str:
    """The generated integrator-facing register/port document."""
    external = [p for p in PORTS if p.external]
    lines: list[str] = [
        f"# `{MODULE}` — register map and port map",
        "",
        f"**GENERATED by `{_GENERATED_BY}` — do not edit by hand.**",
        f"`python3 {_GENERATED_BY} --check` fails if this file and the register",
        "map disagree; regenerate with `python3 " + _GENERATED_BY + "`.",
        "",
        "The map is fixed by",
        "[`DR-0013`](../../spec/decision-records/DR-0013-interface-register-map-and-streaming-semantics.md),",
        "which derives it from [`DR-0001`](../../spec/decision-records/DR-0001-raw-and-conditioned-output-paths.md)",
        "(raw/conditioned paths, `OUT_MODE`, flush-on-switch) and",
        "[`DR-0002`](../../spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md)",
        "(latch-and-gate failure behaviour). Nothing here may be changed without a",
        "superseding decision record.",
        "",
        "## Registers",
        "",
    ]
    lines += _register_tables()
    lines += [
        "",
        "## Ports",
        "",
        f"`{MODULE}` has **{len(PORTS)} ports**, of which **{len(external)}** are",
        "expected to leave the die at `trng_top` (#27) and are therefore the",
        "block's contribution to the top-level pinout (#16). The rest are",
        "block-to-block signals inside `trng_top`.",
        "",
    ]
    lines += _port_tables()
    lines += [
        "",
        "## Top-level pinout contribution (#16)",
        "",
        "| Port | Dir | Width |",
        "|---|---|---|",
    ]
    for p in external:
        lines.append(f"| `{p.name}` | {p.direction} | {p.width} |")
    total = sum(p.width for p in external)
    lines += [
        "",
        f"**{total} signal wires** in total, before any bus-width or "
        "pin-multiplexing decision #27 makes. `reg_wdata`/`reg_rdata`/`str_data` "
        "are 32 bits each and dominate the count; an integrator that cannot "
        "afford them is expected to narrow the register bus in its own wrapper, "
        "not to change this block.",
        "",
        "## Parameters",
        "",
        "| Parameter | Value | Meaning |",
        "|---|---|---|",
        f"| `FIFO_DEPTH` | {FIFO_DEPTH} | words in each output FIFO |",
        f"| `REG_BITS` | {REG_BITS} | register / streaming word width |",
        f"| `ADDR_W` | {ADDR_W} | register address width (word index) |",
        f"| `RAW_PACK_BITS` | {RAW_PACK_BITS} | raw samples packed per word, LSB first |",
        "",
    ]
    return "\n".join(lines)


ARTIFACTS = (
    (VH_PATH, verilog_header),
    (MD_PATH, markdown),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="regmap.py",
        description="Generate (or verify) the interface block's register-map artifacts.",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="do not write: regenerate in memory and fail if a committed artifact is stale",
    )
    args = parser.parse_args(argv)

    status = EXIT_OK
    for path, render in ARTIFACTS:
        fresh = render()
        rel = path.relative_to(REPO_ROOT)
        if args.check:
            if not path.is_file():
                print(f"STALE  {rel}: does not exist")
                status = EXIT_STALE
                continue
            current = path.read_text()
            if current != fresh:
                print(f"STALE  {rel}: committed artifact does not match regmap.py")
                sys.stdout.writelines(
                    difflib.unified_diff(
                        current.splitlines(True), fresh.splitlines(True),
                        fromfile=f"committed/{path.name}", tofile=f"regenerated/{path.name}",
                    )
                )
                status = EXIT_STALE
            else:
                print(f"ok     {rel}: matches design/interface/regmap.py")
        else:
            path.write_text(fresh)
            print(f"wrote  {rel}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
