#!/usr/bin/env python3
"""Bit-exact behavioural model of the TRNG digital conditioner.

This module is the **normative** description of the conditioner's
input/output behaviour at the level fixed by
``spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md``.
The synthesisable RTL in ``crc32_conditioner.v`` implements the same
function and is checked against this model bit-for-bit
(``sim/tests/test_conditioner.py``).

The conditioning function itself is fixed by
``spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md``:

* a 32-bit Galois LFSR clocked by the sampler clock, one raw bit absorbed
  per valid sample, feedback polynomial CRC-32 (IEEE 802.3) in its
  LSB-first reflected form ``0xEDB88320``;
* the state is cleared to zero at the start of every block, so one output
  word is a function of exactly ``BLOCK_BITS = 32 * K`` raw bits and of
  nothing else;
* ``K = 8`` -- 256 raw bits in, one 32-bit word out;
* the state is flushed (cleared, partial block discarded) whenever the
  conditioned path is gated by a health-test failure or ``OUT_MODE``
  switches (DR-0001, DR-0002).

Nothing in this module estimates entropy. Entropy accounting lives in
DR-0008; evidence lives under ``sim/records/``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: CRC-32 (IEEE 802.3) feedback polynomial, LSB-first (reflected) form.
#: x^32 + x^26 + x^23 + x^22 + x^16 + x^12 + x^11 + x^10 + x^8 + x^7
#:       + x^5 + x^4 + x^2 + x + 1
POLY_CRC32_REFLECTED = 0xEDB88320

#: Output word width in bits. Fixed by DR-0008.
WORD_BITS = 32

#: Compression ratio K -- raw bits in : conditioned bits out. Fixed by DR-0008.
K = 8

#: Raw bits absorbed per conditioned output word.
BLOCK_BITS = WORD_BITS * K

#: LFSR state at reset and at every block boundary. Zero is deliberate: a
#: stuck-at-0 raw source then produces all-zero output words instead of a
#: statistically plausible maximal-length LFSR sequence (DR-0008 Consequences).
INIT_STATE = 0x00000000

_MASK32 = 0xFFFFFFFF


@dataclass
class Conditioner:
    """One instance of the conditioner block.

    Ports, matching ``crc32_conditioner.v`` one-for-one:

    ================  =========================================================
    ``step(...)``     one rising edge of the sampler clock
    ``raw_bit``       the DR-0001 raw tap, one bit per sample
    ``raw_valid``     this cycle carries a new raw sample
    ``en``            conditioned path is ungated and ``OUT_MODE`` is stable
    ``flush``         synchronous flush request (gate assert / mode switch)
    returns           ``(cond_word, cond_valid)`` -- ``cond_word`` is only
                      meaningful in the cycle ``cond_valid`` is true
    ================  =========================================================
    """

    word_bits: int = WORD_BITS
    k: int = K
    poly: int = POLY_CRC32_REFLECTED

    state: int = field(default=INIT_STATE, init=False)
    count: int = field(default=0, init=False)
    cond_word: int = field(default=0, init=False)
    cond_valid: bool = field(default=False, init=False)

    #: Lifetime counters -- model bookkeeping, not hardware.
    raw_absorbed: int = field(default=0, init=False)
    words_out: int = field(default=0, init=False)
    flushes: int = field(default=0, init=False)
    bits_discarded: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.word_bits != 32:
            raise ValueError("only the 32-bit word width of DR-0008 is modelled")
        if self.k < 1:
            raise ValueError("K must be >= 1")

    @property
    def block_bits(self) -> int:
        return self.word_bits * self.k

    def reset(self) -> None:
        """Asynchronous power-on reset (``rst_n`` low)."""
        self.state = INIT_STATE
        self.count = 0
        self.cond_word = 0
        self.cond_valid = False

    def flush_state(self) -> None:
        """Clear the LFSR and drop the partial block.

        This is the conditioner-internal half of the DR-0001 / DR-0002 flush
        rule. The output FIFO and the register/streaming half are #26's.
        """
        self.flushes += 1
        self.bits_discarded += self.count
        self.state = INIT_STATE
        self.count = 0
        self.cond_valid = False

    def step(
        self,
        raw_bit: int = 0,
        raw_valid: bool = False,
        en: bool = True,
        flush: bool = False,
    ) -> tuple[int, bool]:
        """Advance one sampler-clock edge. Returns ``(cond_word, cond_valid)``."""
        self.cond_valid = False

        # flush has priority over absorption: a raw bit presented in the same
        # cycle as a gate assertion belongs to the failing window and must not
        # reach the output (DR-0002 "no bit produced under the failing window
        # can be read afterward").
        if flush or not en:
            if self.count or self.state != INIT_STATE or flush:
                self.flush_state()
            return self.cond_word, False

        if not raw_valid:
            return self.cond_word, False

        self.state = self._absorb(self.state, raw_bit & 1)
        self.count += 1
        self.raw_absorbed += 1

        if self.count == self.block_bits:
            self.cond_word = self.state
            self.cond_valid = True
            self.words_out += 1
            # Per-block clear: one output word is a function of exactly
            # block_bits raw samples and of no earlier sample (DR-0008).
            self.state = INIT_STATE
            self.count = 0

        return self.cond_word, self.cond_valid

    def _absorb(self, state: int, bit: int) -> int:
        fb = (state ^ bit) & 1
        state >>= 1
        if fb:
            state ^= self.poly
        return state & _MASK32


def condition_bits(bits, k: int = K) -> list[int]:
    """Run ``bits`` (an iterable of 0/1) through a fresh conditioner.

    Returns the conditioned words. A trailing partial block produces no
    output word and is simply not consumed -- the conditioner emits only
    whole blocks.
    """
    dut = Conditioner(k=k)
    words: list[int] = []
    for bit in bits:
        word, valid = dut.step(raw_bit=bit, raw_valid=True)
        if valid:
            words.append(word)
    return words


def word_to_bits(word: int, width: int = WORD_BITS):
    """LSB-first serialisation of a conditioned word onto the streaming port."""
    return [(word >> i) & 1 for i in range(width)]
