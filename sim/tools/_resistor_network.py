#!/usr/bin/env python3
"""A stdlib-only DC resistor-network solver (issue #464).

`sim/tools/vss_trunk_ir_drop.py` (#234) prices the shared `vss` return as a
series chain, which is exact for that analog trunk and deliberately refuses
the digital section's power grid: a mesh of rails, straps and via arrays
with many parallel paths. This module is the general linear solve that mesh
needs, kept separate from any geometry so it can be tested on hand-checkable
synthetic networks (`sim/tests/test_resistor_network.py`) before it is
trusted on the real one (`sim/tools/digital_supply_ir_drop.py`).

Model
-----
Nodes are arbitrary hashable keys; resistors are two-terminal, positive and
finite. One node is the reference (the chip pin): its potential is held at
zero. Current *injections* are what a load pushes into the network at a
node (a `vss` return), or equivalently -- with every sign flipped -- what it
pulls out (a `vddd` feed); either way the solved potential at a node is the
magnitude of the IR offset that node sees relative to the pin.

The solve is Gaussian elimination on the reduced nodal-conductance
(Laplacian) matrix, kept sparse as dict-of-dicts and ordered greedily by
minimum degree, so a few-hundred-node power grid factors in well under a
second without numpy. Once factored, every further right-hand side is one
forward and one back substitution -- which is what makes the per-node
effective resistances of an allocation-free bound affordable.

What it refuses
---------------
- A zero, negative or non-finite resistance (`NetworkError`). A zero-ohm
  connection is the same node, and the caller should give it the same key.
- An injection at a node the reference cannot reach (`DisconnectedError`).
  The solver never quietly reports such a node at zero offset: that would
  turn a missing connection into a perfect one.
"""

from __future__ import annotations

import heapq
import math
from typing import Hashable, Iterable

Node = Hashable


class NetworkError(ValueError):
    """An invalid resistor or reference."""


class DisconnectedError(NetworkError):
    """Part of the network cannot reach the reference node."""

    def __init__(self, message: str, islands: list[Node]):
        super().__init__(message)
        self.islands = islands


class ResistorNetwork:
    """An undirected network of resistors between hashable node keys."""

    def __init__(self) -> None:
        self._g: dict[Node, dict[Node, float]] = {}
        self._order: list[Node] = []

    def add_node(self, node: Node) -> None:
        if node not in self._g:
            self._g[node] = {}
            self._order.append(node)

    def add_resistor(self, a: Node, b: Node, ohms: float) -> None:
        """Connect `a` and `b` through `ohms`. A second resistor between the
        same pair is in parallel with the first."""
        if a == b:
            raise NetworkError(f"resistor from {a!r} to itself")
        if not (isinstance(ohms, (int, float)) and math.isfinite(ohms) and ohms > 0):
            raise NetworkError(
                f"resistance between {a!r} and {b!r} must be positive and finite, got {ohms!r}"
            )
        self.add_node(a)
        self.add_node(b)
        g = 1.0 / ohms
        self._g[a][b] = self._g[a].get(b, 0.0) + g
        self._g[b][a] = self._g[b].get(a, 0.0) + g

    @property
    def nodes(self) -> list[Node]:
        return list(self._order)

    def __contains__(self, node: Node) -> bool:
        return node in self._g

    def reachable(self, ref: Node) -> set[Node]:
        if ref not in self._g:
            raise NetworkError(f"reference node {ref!r} is not in the network")
        seen = {ref}
        stack = [ref]
        while stack:
            n = stack.pop()
            for m in self._g[n]:
                if m not in seen:
                    seen.add(m)
                    stack.append(m)
        return seen

    def islands(self, ref: Node) -> list[Node]:
        """Every node the reference cannot reach, in insertion order."""
        seen = self.reachable(ref)
        return [n for n in self._order if n not in seen]

    def require_connected(self, ref: Node) -> None:
        """Raise `DisconnectedError` unless every node reaches `ref`."""
        lost = self.islands(ref)
        if lost:
            preview = ", ".join(repr(n) for n in lost[:5])
            more = f" (+{len(lost) - 5} more)" if len(lost) > 5 else ""
            raise DisconnectedError(
                f"{len(lost)} node(s) cannot reach the reference {ref!r}: {preview}{more}",
                lost,
            )

    def factor(self, ref: Node) -> "Factorization":
        return Factorization(self, ref)


class Factorization:
    """The network's reduced conductance matrix, eliminated once, solvable
    for any number of injection vectors."""

    def __init__(self, net: ResistorNetwork, ref: Node):
        reach = net.reachable(ref)
        self.ref = ref
        self.nodes = [n for n in net._order if n in reach and n != ref]
        self.index = {n: i for i, n in enumerate(self.nodes)}
        n = len(self.nodes)
        diag = [0.0] * n
        off: list[dict[int, float]] = [dict() for _ in range(n)]
        for node, i in self.index.items():
            for other, g in net._g[node].items():
                diag[i] += g
                j = self.index.get(other)
                if j is not None:
                    off[i][j] = off[i].get(j, 0.0) - g

        # Greedy minimum-degree elimination with lazy heap updates; ties
        # broken by node index, so the order (and so the floating-point
        # result) is deterministic.
        heap = [(len(off[i]), i) for i in range(n)]
        heapq.heapify(heap)
        done = [False] * n
        steps: list[tuple[int, float, list[tuple[int, float]]]] = []
        while heap:
            deg, k = heapq.heappop(heap)
            if done[k] or deg != len(off[k]):
                continue
            done[k] = True
            piv = diag[k]
            if not piv > 0:
                raise NetworkError(f"singular conductance matrix at node {self.nodes[k]!r}")
            row = list(off[k].items())
            for j, a_kj in row:
                del off[j][k]
            for j, a_jk in row:
                diag[j] -= a_jk * a_jk / piv
                for m, a_km in row:
                    if m != j:
                        off[j][m] = off[j].get(m, 0.0) - a_jk * a_km / piv
            for j, _ in row:
                heapq.heappush(heap, (len(off[j]), j))
            off[k] = {}
            steps.append((k, piv, row))
        self._steps = steps

    def solve(self, injections: dict[Node, float]) -> dict[Node, float]:
        """Potential of every reachable node (reference = 0) for the given
        `{node: amps injected}`. Injecting at an unreachable node raises."""
        b = [0.0] * len(self.nodes)
        for node, amps in injections.items():
            if not math.isfinite(amps):
                raise NetworkError(f"non-finite injection {amps!r} at {node!r}")
            if node == self.ref:
                continue
            i = self.index.get(node)
            if i is None:
                raise DisconnectedError(
                    f"injection at {node!r}, which cannot reach the reference {self.ref!r}",
                    [node],
                )
            b[i] += amps
        for k, piv, row in self._steps:
            bk = b[k]
            if bk:
                for j, a in row:
                    b[j] -= a / piv * bk
        x = [0.0] * len(self.nodes)
        for k, piv, row in reversed(self._steps):
            acc = b[k]
            for j, a in row:
                acc -= a * x[j]
            x[k] = acc / piv
        out = {self.ref: 0.0}
        out.update({node: x[i] for node, i in self.index.items()})
        return out

    def effective_resistance(self, nodes: Iterable[Node]) -> dict[Node, float]:
        """Effective resistance from each of `nodes` to the reference."""
        return {n: self.solve({n: 1.0})[n] for n in nodes}


def uniform_segment_peak(v_a: float, v_b: float, r_ohm: float, i_amp: float) -> float:
    """Highest potential along a resistor of `r_ohm` between nodes at `v_a`
    and `v_b` that itself sinks `i_amp` spread uniformly along its length.

    The node potentials already account for the segment's load (half of it
    lumped at each end, which is exact for the rest of the network); this
    adds the parabola the distributed load puts on top of the straight line:
    v(x) = (1-x) v_a + x v_b + (r i / 2) x (1-x), maximised over x in [0, 1].
    """
    if i_amp <= 0 or r_ohm <= 0:
        return max(v_a, v_b)
    x = 0.5 + (v_b - v_a) / (r_ohm * i_amp)
    x = min(1.0, max(0.0, x))
    return (1 - x) * v_a + x * v_b + 0.5 * r_ohm * i_amp * x * (1 - x)


def uniform_tip_peak(v_a: float, r_ohm: float, i_amp: float) -> float:
    """Potential at the free end of a dangling resistor of `r_ohm` hung off a
    node at `v_a`, sinking `i_amp` uniformly along its length: every
    element's current crosses only the stretch nearer the node, so the tip
    sits r i / 2 above it."""
    return v_a + 0.5 * r_ohm * max(i_amp, 0.0)
