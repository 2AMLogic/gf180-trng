#!/usr/bin/env python3
"""Synthetic raw-bitstream source for the conditioner demonstration.

The conditioner's input is the DR-0001 raw tap. No transistor-level raw
bitstream exists yet -- #9 owes the sampler, and DR-0009 records why a
transistor-level stream long enough to fill even one conditioner block is
not affordable today. So the demonstration drives the conditioner from a
**declared** source model instead, and every evidence record says so.

The model is a stationary IID binary source with a chosen per-sample
min-entropy ``H`` (bit/sample), realised as a biased coin::

    p_max = 2**-H          probability of the most-common value
    P(1)  = 1 - p_max      (so the most-common value is 0)

This is deliberately the *simplest* source that has an exactly known
min-entropy: the point of the demonstration is the conditioner, not the
source. It is **not** a model of a jitter-sampled ring oscillator, which is
neither IID nor stationary across corners. Every record produced from it
carries that limitation in its Caveats.

Bit generation is SHA-256 in counter mode rather than :mod:`random`, so a
stream is bit-identical on any Python on any platform forever -- which is
what ``sim/README.md``'s "no seed, no evidence" rule is actually asking for.
"""

from __future__ import annotations

import hashlib
import struct
from decimal import Decimal, getcontext

getcontext().prec = 60

_UINT32 = 1 << 32


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


def uniform_words(label: str, seed: int):
    """Endless stream of uniform 32-bit words from SHA-256 counter mode."""
    counter = 0
    prefix = f"gf180-trng/conditioner-crc32|{label}|{seed}|".encode()
    while True:
        digest = hashlib.sha256(prefix + str(counter).encode()).digest()
        for word in struct.unpack("<8I", digest):
            yield word
        counter += 1


def biased_bits(label: str, seed: int, n_bits: int, h_per_bit):
    """``n_bits`` IID bits whose per-sample min-entropy is ``h_per_bit``."""
    p_one = p_one_for_min_entropy(h_per_bit)
    # Threshold in the 32-bit uniform domain. The quantisation error is
    # < 2**-32 in probability and is reported alongside the stream.
    threshold = int((p_one * _UINT32).to_integral_value())
    stream = uniform_words(label, seed)
    return [1 if next(stream) < threshold else 0 for _ in range(n_bits)], p_one, threshold


def constant_bits(value: int, n_bits: int):
    """A stuck-at source: ``n_bits`` copies of ``value``. Min-entropy 0."""
    return [value & 1] * n_bits


def pack_lsb_first(bits) -> bytes:
    """Pack a bit list into bytes, LSB of each byte first (stream order)."""
    out = bytearray((len(bits) + 7) // 8)
    for i, bit in enumerate(bits):
        if bit:
            out[i >> 3] |= 1 << (i & 7)
    return bytes(out)
