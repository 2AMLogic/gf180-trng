#!/usr/bin/env python3
"""Declared synthetic per-ring bitstream sources for the ring-liveness-monitor
fault-injection demonstration.

The liveness monitor (``design/health_test/ring_liveness.py``) observes an
already-digitized, already-``clk``-synchronized sample of each ring. No
transistor-level per-ring digitizer exists yet -- DR-0016 records that as a
follow-up (the monitor's own electrical tap is bounded in
``sim/tb/ring-liveness-tap-power/`` instead, per DR-0009's split). So this
demonstration drives ``design/health_test/ring_liveness.py`` from **declared**
per-ring source models, and every evidence record says so.

Deliberately mirrors ``sim/tb/health-test-fault-injection/fault_injection.py``'s
API and SHA-256-counter-mode bit generation (bit-identical on any platform
forever), kept as its own copy per the convention that each behavioural
testbench directory is self-contained.

Two kinds of per-ring stream:

* :func:`healthy_ring_bits` -- an IID ``H = 1.0`` bit/sample source for one
  ring. Why H = 1.0 and not DR-0002's H0 = 0.5: a ring's own period is many
  times shorter than one sampler-clock period (DR-0007 §1's independence
  argument -- the sample clock has no rational relationship to either ring),
  so the ring's *phase* at each sampling instant is effectively randomized
  modulo its own period between samples, and the sampled level is
  approximately an unbiased coin -- not "more periods per sample means the
  level is more likely to have flipped" (a live ring's sampled bit does NOT
  become more likely to differ from the previous sample just because many
  ring periods elapsed in between; phase aliasing makes consecutive samples
  approximately *independent*, not anti-correlated). This is a declared,
  conservative modelling choice, not a measurement: no per-ring duty-cycle
  bias has been measured in this repository (see DR-0016 "Consequences" --
  "Negative / accepted cost"), and
  ``design/health_test/ring_liveness.py`` never assumes a duty cycle -- its
  C_LIVE cutoff is independently reused from DR-0002's own C_RCT at H0 = 0.5,
  which is *more* conservative (looser) than what an H = 1.0 source would
  need.
* :func:`stuck_ring_bits` -- a stuck-at source for one ring (the "dead ring"
  fault): ``n_bits`` copies of a fixed value. Min-entropy 0, the signature of
  a ring that has fully stopped oscillating.
"""

from __future__ import annotations

import hashlib
import struct

from harness.bits import pack_lsb_first  # noqa: F401 -- re-exported for source_model.<name> callers

_UINT32 = 1 << 32


def uniform_words(label: str, seed: int):
    """Endless stream of uniform 32-bit words from SHA-256 counter mode."""
    counter = 0
    prefix = f"gf180-trng/ring-liveness-fault-injection|{label}|{seed}|".encode()
    while True:
        digest = hashlib.sha256(prefix + str(counter).encode()).digest()
        for word in struct.unpack("<8I", digest):
            yield word
        counter += 1


def healthy_ring_bits(label: str, seed: int, n_bits: int) -> list[int]:
    """``n_bits`` IID, unbiased (H = 1.0) samples for one healthy ring."""
    stream = uniform_words(label, seed)
    threshold = 1 << 31  # P(1) = 0.5
    return [1 if next(stream) < threshold else 0 for _ in range(n_bits)]


def stuck_ring_bits(value: int, n_bits: int) -> list[int]:
    """A stuck-at source: ``n_bits`` copies of ``value``. Min-entropy 0."""
    return [value & 1] * n_bits
