#!/usr/bin/env python3
"""Shared bit-source math for ``sim/tb/*`` testbenches (issue #191).

Every declared synthetic source model under ``sim/tb/`` -- the demonstration
sources that stand in for a not-yet-affordable transistor-level bitstream
(see DR-0009) -- needed the same two pieces of math: converting between a
binary source's per-sample min-entropy and its bias (``p_one_for_min_entropy``
/ ``min_entropy_for_p_one``), and packing a bit list into bytes in the
stream's LSB-first convention (``pack_lsb_first``). Before this module
existed, three modules (``sim/tb/conditioner-crc32/source_model.py``,
``sim/tb/ring-liveness-fault-injection/ring_source_model.py``,
``sim/tb/health-test-fault-injection/fault_injection.py``) each carried a
byte-identical copy of ``pack_lsb_first``, and two of them
(``conditioner-crc32/source_model.py`` and
``health-test-fault-injection/fault_injection.py``) also each carried a
byte-identical copy of the min-entropy/bias conversions.

This is the same category of duplication that #190 consolidated on the
*reading* side (``sim/tools/_record_parsing.py``) -- this module is the
*writing*-side (bit-source math) equivalent, scoped to ``sim/tb/``.

This is pure code motion: every function here is moved verbatim (docstring
included) from ``sim/tb/conditioner-crc32/source_model.py``, with no
behaviour change. Each of the three testbench modules re-exports these names
so existing ``source_model.pack_lsb_first(...)`` / ``fault_injection.<name>``
call sites (via each directory's ``source_model``-aliased import convention)
keep working unchanged.
"""

from __future__ import annotations

from decimal import Decimal, getcontext

getcontext().prec = 60


def p_one_for_min_entropy(h_per_bit) -> Decimal:
    """P(1) of a biased coin whose per-sample min-entropy is ``h_per_bit``."""
    h = Decimal(str(h_per_bit))
    if h < 0 or h > 1:
        raise ValueError("per-sample min-entropy of a binary source is in [0, 1]")
    p_max = Decimal(2) ** (-h)
    return Decimal(1) - p_max


def min_entropy_for_p_one(p_one) -> Decimal:
    """Most-common-value min-entropy of a binary source with the given P(1)."""
    p = Decimal(str(p_one))
    if not (0 <= p <= 1):
        raise ValueError("P(1) must be in [0, 1]")
    p_max = max(p, Decimal(1) - p)
    if p_max == 0:
        raise ValueError("degenerate source")
    return -(p_max.ln() / Decimal(2).ln())


def pack_lsb_first(bits) -> bytes:
    """Pack a bit list into bytes, LSB of each byte first (stream order)."""
    out = bytearray((len(bits) + 7) // 8)
    for i, bit in enumerate(bits):
        if bit:
            out[i >> 3] |= 1 << (i & 7)
    return bytes(out)
