#!/usr/bin/env python3
"""SP 800-90B conditioning-component output-entropy arithmetic.

This module exists so that the numbers quoted in
``spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md`` are
*computed and re-computable*, not asserted. It implements the output-entropy
expression NIST SP 800-90B (final, January 2018) gives for a conditioning
component, plus the additional cap that applies when the component is
**non-vetted**.

.. warning::

   **Provenance caveat.** This repository holds no offline copy of
   SP 800-90B, and this module was written from the published expression as
   recalled, not transcribed from the PDF in front of the author. DR-0004
   flagged exactly this: "Clause numbering and the exact non-vetted
   output-entropy penalty should be checked against the published
   SP 800-90B before ratification. This DR relies on the vetted/non-vetted
   *distinction*, not on a specific constant."

   The same caveat is inherited here, and is repeated in DR-0008. Before any
   number produced by this module is used in a datasheet or a submission,
   the expression below and the ``0.85`` cap must be checked against the
   published standard. Everything downstream is arranged so that a change to
   the cap moves one constant (:data:`NON_VETTED_CAP`) and re-derives, rather
   than invalidating the design.

Expression implemented (SP 800-90B section 3.1.5.1.2, "Entropy of the output
of a conditioning component"), for ``n_in`` input bits carrying ``h_in`` bits
of min-entropy, ``n_out`` output bits, and a narrowest internal width ``nw``::

    P_high = 2**-h_in
    P_low  = (1 - P_high) / (2**n_in - 1)
    n      = min(n_out, nw)
    psi    = 2**(n_in - n) * P_low + P_high
    U      = 2**(n_in - n) + sqrt(2 * n * 2**(n_in - n) * ln 2)
    omega  = U * P_low
    h_out  = -log2(max(psi, omega))

and (section 3.1.5.2, non-vetted conditioning components)::

    h_out_non_vetted = min(h_out, NON_VETTED_CAP * min(n_out, nw))

All arithmetic is done in :mod:`decimal` at 120 digits, because the
intermediate terms span 2**-256 to 2**256 and float underflows them.
"""

from __future__ import annotations

from decimal import Decimal, getcontext

getcontext().prec = 120

#: The per-output-bit ceiling SP 800-90B places on a non-vetted conditioning
#: component. See the provenance caveat above before quoting this.
NON_VETTED_CAP = Decimal("0.85")

_LN2 = Decimal(2).ln()


def _log2(x: Decimal) -> Decimal:
    return x.ln() / _LN2


def output_entropy(n_in: int, n_out: int, nw: int, h_in) -> Decimal:
    """Output entropy of a conditioning component, before any vetting cap.

    ``h_in`` is the min-entropy (in bits) of the *whole* ``n_in``-bit input,
    not per bit.
    """
    if n_in <= 0 or n_out <= 0 or nw <= 0:
        raise ValueError("n_in, n_out and nw must be positive")
    h_in = Decimal(str(h_in))
    if h_in < 0:
        raise ValueError("h_in must be non-negative")

    n = min(n_out, nw)
    p_high = Decimal(2) ** (-h_in)
    p_low = (Decimal(1) - p_high) / (Decimal(2) ** n_in - 1)
    spread = Decimal(2) ** (n_in - n)

    psi = spread * p_low + p_high
    u = spread + (Decimal(2) * n * spread * _LN2).sqrt()
    omega = u * p_low

    return -_log2(max(psi, omega))


def non_vetted_output_entropy(n_in: int, n_out: int, nw: int, h_in) -> Decimal:
    """Output entropy creditable to a **non-vetted** conditioning component."""
    capped = NON_VETTED_CAP * min(n_out, nw)
    return min(output_entropy(n_in, n_out, nw, h_in), capped)


def break_even_h_in(n_in: int, n_out: int, nw: int, tol=Decimal("1e-9")) -> Decimal:
    """Smallest input min-entropy at which the non-vetted cap is the binding term.

    Below this input entropy the conditioner, not the non-vetted penalty, is
    what limits the output; above it the component delivers the full
    ``NON_VETTED_CAP * min(n_out, nw)`` and extra input entropy is discarded.
    """
    target = NON_VETTED_CAP * min(n_out, nw)
    lo, hi = Decimal(0), Decimal(n_in)
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if output_entropy(n_in, n_out, nw, mid) < target:
            lo = mid
        else:
            hi = mid
    return hi


def break_even_h_per_bit(n_in: int, n_out: int, nw: int) -> Decimal:
    """:func:`break_even_h_in` expressed per raw input bit."""
    return break_even_h_in(n_in, n_out, nw) / n_in


if __name__ == "__main__":  # pragma: no cover - convenience only
    for k in (2, 4, 8, 16):
        n_in = 32 * k
        be = break_even_h_per_bit(n_in, 32, 32)
        h_out = non_vetted_output_entropy(n_in, 32, 32, Decimal("0.5") * n_in)
        print(
            f"K={k:2d}  n_in={n_in:4d}  break-even H={be:.6f} bit/raw bit  "
            f"h_out@H0=0.5 -> {h_out:.4f} bit/word ({h_out / 32:.4f} bit/bit)"
        )
