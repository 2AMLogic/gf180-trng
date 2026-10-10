#!/usr/bin/env python3
"""Unit tests for the stdlib DC resistor-network solver
(``sim/tools/_resistor_network.py``, issue #464), on synthetic networks with
hand-computed or independently computed answers. No geometry, no records."""

from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR / "tools"))

import _resistor_network as rn  # noqa: E402


def dense_solve(edges, ref, injections):
    """Independent check: plain Gauss-Jordan on the full reduced Laplacian."""
    nodes = sorted({n for a, b, _ in edges for n in (a, b)} - {ref})
    idx = {n: i for i, n in enumerate(nodes)}
    m = len(nodes)
    a = [[0.0] * (m + 1) for _ in range(m)]
    for p, q, r in edges:
        g = 1.0 / r
        for u, v in ((p, q), (q, p)):
            if u in idx:
                a[idx[u]][idx[u]] += g
                if v in idx:
                    a[idx[u]][idx[v]] -= g
    for n, amps in injections.items():
        a[idx[n]][m] += amps
    for c in range(m):
        piv = max(range(c, m), key=lambda r: abs(a[r][c]))
        a[c], a[piv] = a[piv], a[c]
        for r in range(m):
            if r != c and a[r][c]:
                f = a[r][c] / a[c][c]
                a[r] = [x - f * y for x, y in zip(a[r], a[c])]
    return {n: a[idx[n]][m] / a[idx[n]][idx[n]] for n in nodes}


def network(edges):
    net = rn.ResistorNetwork()
    for a, b, r in edges:
        net.add_resistor(a, b, r)
    return net


class HandComputed(unittest.TestCase):
    def test_series_chain(self):
        # pin --10-- B --20-- C, 1 mA drawn at C: 10 mV at B, 30 mV at C.
        phi = network([("pin", "B", 10.0), ("B", "C", 20.0)]).factor("pin").solve({"C": 1e-3})
        self.assertAlmostEqual(phi["B"], 0.010, places=12)
        self.assertAlmostEqual(phi["C"], 0.030, places=12)
        self.assertEqual(phi["pin"], 0.0)

    def test_parallel_pair_halves(self):
        net = network([("pin", "X", 10.0), ("pin", "X", 10.0)])
        self.assertAlmostEqual(net.factor("pin").effective_resistance(["X"])["X"], 5.0, places=12)

    def test_series_parallel_combination(self):
        # pin --2-- A, then A--X two paths: 3+3 and 6 -> 6 || 6 = 3; total 5.
        net = network([("pin", "A", 2.0), ("A", "M", 3.0), ("M", "X", 3.0), ("A", "X", 6.0)])
        fac = net.factor("pin")
        self.assertAlmostEqual(fac.effective_resistance(["X"])["X"], 5.0, places=12)
        phi = fac.solve({"X": 1.0})
        # Half the current through each 6-ohm branch: M sits 1.5 V above A.
        self.assertAlmostEqual(phi["M"] - phi["A"], 1.5, places=12)

    def test_balanced_bridge_carries_no_current(self):
        # Wheatstone bridge, balanced: the 7-ohm bridge resistor is idle,
        # so R(pin, X) = (1+2) || (1+2) = 1.5.
        net = network([("pin", "A", 1.0), ("pin", "B", 1.0), ("A", "X", 2.0),
                       ("B", "X", 2.0), ("A", "B", 7.0)])
        phi = net.factor("pin").solve({"X": 1.0})
        self.assertAlmostEqual(phi["X"], 1.5, places=12)
        self.assertAlmostEqual(phi["A"], phi["B"], places=12)


class AgainstDenseSolve(unittest.TestCase):
    def test_random_grid_matches_dense_elimination(self):
        rng = random.Random(464)
        edges = []
        n = 7
        for i in range(n):
            for j in range(n):
                if i + 1 < n:
                    edges.append(((i, j), (i + 1, j), rng.uniform(0.1, 10)))
                if j + 1 < n:
                    edges.append(((i, j), (i, j + 1), rng.uniform(0.1, 10)))
        edges.append(("pin", (0, 0), 0.5))
        inj = {(rng.randrange(n), rng.randrange(n)): rng.uniform(1e-6, 1e-3) for _ in range(9)}
        got = network(edges).factor("pin").solve(inj)
        want = dense_solve(edges, "pin", inj)
        for node, v in want.items():
            self.assertAlmostEqual(got[node], v, delta=1e-12 + 1e-9 * abs(v))


class Refusals(unittest.TestCase):
    def test_non_positive_or_non_finite_resistance_rejected(self):
        net = rn.ResistorNetwork()
        for bad in (0.0, -1.0, float("inf"), float("nan")):
            with self.assertRaises(rn.NetworkError):
                net.add_resistor("a", "b", bad)
        with self.assertRaises(rn.NetworkError):
            net.add_resistor("a", "a", 1.0)

    def test_injection_on_an_island_is_not_zero_offset(self):
        net = network([("pin", "A", 1.0), ("B", "C", 1.0)])
        fac = net.factor("pin")
        with self.assertRaises(rn.DisconnectedError):
            fac.solve({"C": 1e-3})
        with self.assertRaises(rn.DisconnectedError) as ctx:
            net.require_connected("pin")
        self.assertEqual(sorted(ctx.exception.islands), ["B", "C"])


class Monotonicity(unittest.TestCase):
    def test_raising_any_resistance_never_lowers_the_offset(self):
        # Rayleigh monotonicity: with one load, raising any resistance can
        # only raise the effective resistance it sees. (With several loads a
        # single node's potential is not monotone in every edge -- which is
        # why the allocation-free bound is stated on effective resistance.)
        base = [("pin", "A", 1.0), ("A", "B", 2.0), ("A", "C", 3.0), ("B", "C", 1.0),
                ("B", "D", 2.0), ("C", "D", 2.0)]
        inj = {"D": 1e-3}
        ref = network(base).factor("pin").solve(inj)
        for k in range(len(base)):
            bumped = list(base)
            a, b, r = bumped[k]
            bumped[k] = (a, b, r * 1.5)
            phi = network(bumped).factor("pin").solve(inj)
            self.assertGreaterEqual(phi["D"], ref["D"], f"raising edge {k} lowered D")


class DistributedLoads(unittest.TestCase):
    def _discretised_peak(self, v_a, v_b, r, i, n=400):
        # A uniformly loaded segment as n small resistors with i/n at each
        # interior node, end potentials forced through ideal-ish sources.
        net = rn.ResistorNetwork()
        for k in range(n):
            net.add_resistor(k, k + 1, r / n)
        net.add_resistor("pin", 0, 1e-9)
        net.add_resistor("pin", n, 1e-9)
        # Superpose: the loaded segment between two grounded ends, plus the
        # straight line between the given end potentials.
        phi = net.factor("pin").solve({k: i / n for k in range(1, n)})
        return max(phi[k] + v_a + (v_b - v_a) * k / n for k in range(n + 1))

    def test_segment_peak_matches_fine_discretisation(self):
        for v_a, v_b, r, i in ((0.0, 0.0, 4.0, 1e-3), (1e-3, 1.5e-3, 4.0, 1e-3),
                               (2e-3, 0.0, 1.0, 1e-3)):
            want = self._discretised_peak(v_a, v_b, r, i)
            got = rn.uniform_segment_peak(v_a, v_b, r, i)
            self.assertAlmostEqual(got, want, delta=2e-8)

    def test_equal_ends_peak_is_r_i_over_8(self):
        self.assertAlmostEqual(rn.uniform_segment_peak(0.0, 0.0, 8.0, 1.0), 1.0, places=12)

    def test_tip_peak_is_r_i_over_2(self):
        self.assertAlmostEqual(rn.uniform_tip_peak(0.25, 2.0, 0.5), 0.75, places=12)


if __name__ == "__main__":
    unittest.main()
