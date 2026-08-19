#!/usr/bin/env python3
"""Declared synthetic raw-bitstream sources for the health-test fault-injection
demonstration.

The health tests observe the DR-0001 raw tap. No transistor-level raw
bitstream exists yet -- #9 owes the sampler, and
``spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md``
records why a transistor-level stream long enough to fill even one 1024-
sample start-up window is not affordable today (~7.4 days extrapolated).
So this demonstration drives ``design/health_test/rct_apt.py`` from
**declared** source models instead, and every evidence record says so.

This module deliberately mirrors
``sim/tb/conditioner-crc32/source_model.py``'s API and SHA-256-counter-mode
bit generation (bit-identical on any platform forever -- what
``sim/README.md``'s "no seed, no evidence" rule asks for), kept as its own
copy per the convention that each behavioural testbench directory is
self-contained. Named ``fault_injection.py`` rather than ``source_model.py``
so that ``sys.path``-based imports of the two testbench directories never
collide on a shared module name when both are loaded in the same test
process (as ``python3 -m unittest discover -s sim/tests`` does).

Four kinds of stream, matching this issue's acceptance criteria:

* :func:`biased_bits` -- a stationary IID binary source with a declared
  per-sample min-entropy ``H`` (the "healthy" source, and also the "heavily
  biased" fault when driven at a low ``H``).
* :func:`constant_bits` -- a stuck-at source (the "stuck output" fault).
* :func:`oscillator_lockup_bits` -- a very-low-frequency deterministic square
  wave, standing in for two array rings that have injection-locked into a
  common (near-)period: from the health tests' point of view this looks like
  a long run of a repeated value, exactly what an injection-locked or
  stalled oscillator would present at the XOR-combined node (the "injection-
  locked / oscillator lock-up" fault).
"""

from __future__ import annotations

import hashlib
import struct

from harness.bits import (  # noqa: F401 -- re-exported for source_model.<name> callers
    min_entropy_for_p_one,
    p_one_for_min_entropy,
    pack_lsb_first,
)

_UINT32 = 1 << 32


def uniform_words(label: str, seed: int):
    """Endless stream of uniform 32-bit words from SHA-256 counter mode."""
    counter = 0
    prefix = f"gf180-trng/health-test-fault-injection|{label}|{seed}|".encode()
    while True:
        digest = hashlib.sha256(prefix + str(counter).encode()).digest()
        for word in struct.unpack("<8I", digest):
            yield word
        counter += 1


def biased_bits(label: str, seed: int, n_bits: int, h_per_bit):
    """``n_bits`` IID bits whose per-sample min-entropy is ``h_per_bit``."""
    p_one = p_one_for_min_entropy(h_per_bit)
    # Threshold in the 32-bit uniform domain. The quantisation error is
    # < 2**-32 in probability, negligible next to the alpha values in play.
    threshold = int((p_one * _UINT32).to_integral_value())
    stream = uniform_words(label, seed)
    return [1 if next(stream) < threshold else 0 for _ in range(n_bits)], p_one, threshold


def constant_bits(value: int, n_bits: int):
    """A stuck-at source: ``n_bits`` copies of ``value``. Min-entropy 0."""
    return [value & 1] * n_bits


def oscillator_lockup_bits(n_bits: int, half_period: int = 2000, start_value: int = 0):
    """A deterministic square wave standing in for an injection-locked pair
    of rings.

    Two array rings that have locked into a common (near-)period present a
    combined node that stops toggling at the sampler's rate and instead
    holds each value for a long, deterministic stretch -- the opposite of
    the intended per-sample independence. ``half_period`` (default 2000,
    chosen to comfortably exceed the ratified C_RCT=81 at H0=0.5, so the
    fault is unambiguous well before either half-period ends) is the number
    of raw samples the node holds one value before flipping.

    Deterministic and seedless: unlike :func:`biased_bits`, this is not a
    statistical model, it is a fixed pathological waveform.
    """
    if half_period < 1:
        raise ValueError("half_period must be >= 1")
    bits: list[int] = []
    value = start_value & 1
    while len(bits) < n_bits:
        bits.extend([value] * min(half_period, n_bits - len(bits)))
        value ^= 1
    return bits
