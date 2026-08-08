#!/usr/bin/env python3
"""A lightweight SP 800-22-style statistical battery for a *conditioned*
(post-whitening) bitstream.

    python3 sim/tools/statistical_battery.py <bits-file>            # print
    python3 sim/tools/statistical_battery.py --check                # self-test

This is **not** the SP 800-90B non-IID entropy-source suite DR-0012 §2
forbids running at an unsupported N. It is a different, cheaper standard
(SP 800-22, "A Statistical Test Suite for Random and Pseudorandom Number
Generators") aimed at a different question: does a stream that is *supposed*
to already look uniform (the conditioner's output, not the raw tap) show any
of a handful of classical statistical defects. Four of its tests are
implemented here -- monobit (frequency), block frequency, runs, and longest
run of ones in a block -- each gated on the sample count NIST's own tables
require before the test result means anything; a test below its minimum N is
**omitted with a stated reason**, per this repository's own edge-case rule,
rather than run truncated and reported anyway.

Every p-value uses the regularized incomplete gamma function, implemented
here from scratch (Numerical-Recipes-style series/continued-fraction
evaluation, ``gammaincc``) rather than importing SciPy, matching this
repository's stdlib-only convention (see ``package.json``'s ``lint``
description). ``--check`` cross-validates it against the standard-library
``math.erfc`` via the identity ``Q(1/2, x) = erfc(sqrt(x))``, which holds for
any correctly implemented upper incomplete gamma function and needs no
external reference table.

What a PASS here does and does not show
-----------------------------------------
A pass says the *bits examined* did not trip a classical bias/pattern
detector at the chosen significance level. It says nothing about the
min-entropy of whatever fed the conditioner -- SP 800-22 batteries are
famously satisfiable by low-entropy sources that have merely been whitened
(see ``sim/tb/conditioner-crc32/README.md``'s own worked example, scenario
``h003``). Read every PASS/FAIL below with that in mind; the accompanying
evidence record repeats this caveat next to the numbers, not just here.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

#: Default NIST-recommended significance level (SP 800-22 section 4).
ALPHA = 0.01

#: SP 800-22 Table 2-4 category boundaries and reference probabilities for
#: the "longest run of ones" test's smallest tabulated regime -- the one
#: this module implements. Valid for 128 <= n < 6272 samples, M = 8,
#: K = 3 (4 categories), N = floor(n / 8) blocks.
LONGEST_RUN_M = 8
LONGEST_RUN_PI = (0.2148, 0.3672, 0.2305, 0.1875)
LONGEST_RUN_N_MIN = 128
LONGEST_RUN_N_MAX = 6272  # exclusive; table is not valid at or above this N


class BatteryError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Regularized incomplete gamma function (no SciPy dependency)
# ---------------------------------------------------------------------------


def _gamma_series(a: float, x: float) -> float:
    """Lower regularized incomplete gamma P(a, x), series form (x < a + 1)."""
    if x <= 0.0:
        return 0.0
    gln = math.lgamma(a)
    ap = a
    total = 1.0 / a
    delta = total
    for _ in range(500):
        ap += 1.0
        delta *= x / ap
        total += delta
        if abs(delta) < abs(total) * 1e-15:
            break
    else:  # pragma: no cover - defensive; 500 terms always converges here
        raise BatteryError(f"gamma series did not converge for a={a}, x={x}")
    return total * math.exp(-x + a * math.log(x) - gln)


def _gamma_cf(a: float, x: float) -> float:
    """Upper regularized incomplete gamma Q(a, x), continued-fraction form
    (x >= a + 1). Lentz's algorithm."""
    gln = math.lgamma(a)
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    else:  # pragma: no cover - defensive
        raise BatteryError(f"gamma continued fraction did not converge for a={a}, x={x}")
    return math.exp(-x + a * math.log(x) - gln) * h


def gammaincc(a: float, x: float) -> float:
    """Regularized upper incomplete gamma function ``Q(a, x)``.

    ``a > 0``, ``x >= 0``. ``Q(1/2, x) = erfc(sqrt(x))`` is the identity
    ``--check`` uses to validate this against the standard library.
    """
    if a <= 0.0 or x < 0.0:
        raise BatteryError(f"gammaincc domain error: a={a}, x={x}")
    if x == 0.0:
        return 1.0
    if x < a + 1.0:
        return 1.0 - _gamma_series(a, x)
    return _gamma_cf(a, x)


# ---------------------------------------------------------------------------
# The four tests
# ---------------------------------------------------------------------------


def monobit_test(bits: list[int]) -> dict:
    """SP 800-22 section 2.1 -- the frequency (monobit) test."""
    n = len(bits)
    min_n = 100
    if n < min_n:
        return _omitted("monobit (frequency)", n, min_n)
    s = sum(1 if b else -1 for b in bits)
    s_obs = abs(s) / math.sqrt(n)
    p = math.erfc(s_obs / math.sqrt(2.0))
    return _result("monobit (frequency)", n, min_n, statistic=s_obs, p_value=p)


def block_frequency_test(bits: list[int], m: int = 128) -> dict:
    """SP 800-22 section 2.2 -- the block frequency test."""
    n = len(bits)
    min_n = 100
    nblocks = n // m
    if n < min_n or nblocks < 1:
        return _omitted(f"block frequency (M={m})", n, max(min_n, m))
    chi2 = 0.0
    for i in range(nblocks):
        block = bits[i * m : (i + 1) * m]
        pi = sum(block) / m
        chi2 += (pi - 0.5) ** 2
    chi2 *= 4.0 * m
    p = gammaincc(nblocks / 2.0, chi2 / 2.0)
    return _result(
        f"block frequency (M={m})", n, min_n, statistic=chi2, p_value=p, blocks=nblocks
    )


def runs_test(bits: list[int]) -> dict:
    """SP 800-22 section 2.3 -- the runs test.

    Has its own prerequisite (the frequency test must not already show the
    stream is far from balanced); when it does not hold, the runs test is
    "not applicable" rather than given a p-value, per the standard.
    """
    n = len(bits)
    min_n = 100
    if n < min_n:
        return _omitted("runs", n, min_n)
    pi = sum(bits) / n
    if abs(pi - 0.5) >= 2.0 / math.sqrt(n):
        return {
            "name": "runs",
            "n": n,
            "min_n": min_n,
            "omitted": True,
            "reason": (
                f"prerequisite frequency check failed: |pi - 0.5| = {abs(pi - 0.5):.6f} "
                f">= 2/sqrt(n) = {2.0 / math.sqrt(n):.6f} (SP 800-22 section 2.3, step 1) "
                "-- the runs test is not applicable to an unbalanced stream"
            ),
        }
    v = 1 + sum(1 for k in range(1, n) if bits[k] != bits[k - 1])
    denom = 2.0 * math.sqrt(2.0 * n) * pi * (1.0 - pi)
    p = math.erfc(abs(v - 2.0 * n * pi * (1.0 - pi)) / denom)
    return _result("runs", n, min_n, statistic=float(v), p_value=p)


def longest_run_test(bits: list[int]) -> dict:
    """SP 800-22 section 2.4, the smallest tabulated regime only
    (128 <= n < 6272, M = 8). Outside that range the test is omitted with a
    stated reason rather than applied against a table it was not validated
    for -- see the module docstring.
    """
    n = len(bits)
    name = f"longest run of ones (M={LONGEST_RUN_M})"
    if n < LONGEST_RUN_N_MIN:
        return _omitted(name, n, LONGEST_RUN_N_MIN)
    if n >= LONGEST_RUN_N_MAX:
        return {
            "name": name,
            "n": n,
            "min_n": LONGEST_RUN_N_MIN,
            "omitted": True,
            "reason": (
                f"n = {n} is at or above {LONGEST_RUN_N_MAX}, the upper edge of the M=8 "
                "table's validated range (SP 800-22 Table 2-4). Larger N needs the M=128 "
                "or M=10^4 tables, which this module does not implement (see module "
                "docstring) rather than risk a mistranscribed reference table."
            ),
        }
    m = LONGEST_RUN_M
    nblocks = n // m
    counts = [0, 0, 0, 0]
    for i in range(nblocks):
        block = bits[i * m : (i + 1) * m]
        longest = 0
        cur = 0
        for b in block:
            if b:
                cur += 1
                longest = max(longest, cur)
            else:
                cur = 0
        if longest <= 1:
            counts[0] += 1
        elif longest == 2:
            counts[1] += 1
        elif longest == 3:
            counts[2] += 1
        else:
            counts[3] += 1
    chi2 = sum(
        (counts[i] - nblocks * LONGEST_RUN_PI[i]) ** 2 / (nblocks * LONGEST_RUN_PI[i])
        for i in range(4)
    )
    p = gammaincc(1.5, chi2 / 2.0)
    return _result(name, n, LONGEST_RUN_N_MIN, statistic=chi2, p_value=p, blocks=nblocks)


def _omitted(name: str, n: int, min_n: int) -> dict:
    return {
        "name": name,
        "n": n,
        "min_n": min_n,
        "omitted": True,
        "reason": f"n = {n} is below this test's minimum useful sample count ({min_n})",
    }


def _result(name: str, n: int, min_n: int, *, statistic: float, p_value: float, **extra) -> dict:
    out = {
        "name": name,
        "n": n,
        "min_n": min_n,
        "omitted": False,
        "statistic": statistic,
        "p_value": p_value,
        **extra,
    }
    return out


def run_battery(bits: list[int], alpha: float = ALPHA) -> list[dict]:
    """Run every implemented test, in a fixed order."""
    results = [
        monobit_test(bits),
        block_frequency_test(bits, m=128),
        runs_test(bits),
        longest_run_test(bits),
    ]
    for r in results:
        if not r.get("omitted"):
            r["pass"] = r["p_value"] >= alpha
            r["alpha"] = alpha
    return results


def bits_from_file(path: Path) -> list[int]:
    """Load a packed bitstream (LSB-first within each byte, stream order --
    the same convention ``design/conditioner/crc32_conditioner.py``'s
    ``word_to_bits``/``sim/tb/conditioner-crc32``'s raw-bits files use)."""
    data = path.read_bytes()
    bits: list[int] = []
    for byte in data:
        for i in range(8):
            bits.append((byte >> i) & 1)
    return bits


def _print_results(results: list[dict], alpha: float) -> None:
    print(f"alpha = {alpha:g}\n")
    header = f"{'test':<28} {'n':>8} {'statistic':>12} {'p-value':>10}  result"
    print(header)
    print("-" * len(header))
    for r in results:
        if r.get("omitted"):
            print(f"{r['name']:<28} {r['n']:>8}          --          --  OMITTED ({r['reason']})")
        else:
            verdict = "PASS" if r["pass"] else "FAIL"
            print(
                f"{r['name']:<28} {r['n']:>8} {r['statistic']:12.4f} {r['p_value']:10.6f}  {verdict}"
            )


def _self_check() -> int:
    # 1. gammaincc cross-validated against math.erfc via Q(1/2, x) = erfc(sqrt(x)),
    #    independent of any hand-transcribed reference table.
    worst = 0.0
    for x in (0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 25.0, 60.0):
        got = gammaincc(0.5, x)
        want = math.erfc(math.sqrt(x))
        worst = max(worst, abs(got - want))
    if worst > 1e-9:
        print(f"FAIL: gammaincc vs erfc identity off by {worst:.3e} (tolerance 1e-9)", file=sys.stderr)
        return 1
    print(f"OK: gammaincc(1/2, x) == erfc(sqrt(x)) to within {worst:.2e} over 9 points")

    # 2. The battery applied to a fixed, deterministic, known-good stream
    #    passes every implemented test at alpha=0.01. Deterministic (SHA-256
    #    counter mode, fixed seed string) so this is reproducible rather than
    #    flaky -- see sim/tools/statistical_battery.py --check's docstring
    #    note on why a random re-roll per CI run would be the wrong design.
    import hashlib

    n_bits = 4096
    prefix = b"gf180-trng/statistical_battery/self-check|seed=1|"
    stream = bytearray()
    counter = 0
    while len(stream) * 8 < n_bits:
        stream += hashlib.sha256(prefix + str(counter).encode()).digest()
        counter += 1
    bits = []
    for byte in stream[: (n_bits + 7) // 8]:
        for i in range(8):
            if len(bits) >= n_bits:
                break
            bits.append((byte >> i) & 1)

    results = run_battery(bits)
    failed = [r for r in results if not r.get("omitted") and not r["pass"]]
    omitted = [r for r in results if r.get("omitted")]
    if omitted:
        print(
            f"FAIL: self-check stream omitted {len(omitted)} test(s) unexpectedly: "
            + ", ".join(r["name"] for r in omitted),
            file=sys.stderr,
        )
        return 1
    if failed:
        print(
            "FAIL: self-check stream (SHA-256 counter mode, a known-good PRNG) failed "
            + ", ".join(f"{r['name']} (p={r['p_value']:.4f})" for r in failed),
            file=sys.stderr,
        )
        return 1
    print(f"OK: all {len(results)} tests pass at alpha={ALPHA:g} on the fixed self-check stream")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="statistical_battery.py",
        description="Lightweight SP 800-22-style statistical battery for a conditioned bitstream.",
    )
    parser.add_argument(
        "bits_file", nargs="?", metavar="BITS_FILE",
        help="packed bitstream file (LSB-first bytes) to test",
    )
    parser.add_argument("--alpha", type=float, default=ALPHA, help=f"significance level (default {ALPHA:g})")
    parser.add_argument("--check", action="store_true", help="run the module self-check and exit")
    args = parser.parse_args(argv)

    if args.check:
        return _self_check()

    if not args.bits_file:
        parser.error("BITS_FILE is required unless --check is given")

    bits = bits_from_file(Path(args.bits_file))
    results = run_battery(bits, alpha=args.alpha)
    _print_results(results, args.alpha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
