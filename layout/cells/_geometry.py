#!/usr/bin/env python3
"""Shared dog-boned-pad geometry helpers for the hand-drawn ring-stage cells.

`layout/cells/ro_stage/build.py`, `ro_stage_ring2/build.py`,
`ro_nand2/build.py`, `ro_nand2_ring2/build.py`, and `ro_buf/build.py` each
hand-place a two-row (NMOS row, PMOS row) layout in which every contacted
(source/drain) region is widened to a fixed `PAD_H` regardless of the
device's own W -- the "dog-boned" technique `ro_stage/build.py`'s own
docstring documents (a minimum-width diffusion cannot itself satisfy
`comp.enclosing.contact.1` once a contact lands on it). All five cells share
the same `PAD_H` value and the same two small Y-band helpers built from it;
before this module those five `build.py` files carried five byte-identical
copies of the block below (issue #215).

Not the same constant as `layout/cells/_mos_row.py`'s `PAD_H_MIN`
-------------------------------------------------------------------
`_mos_row.py` (the shared engine for `xor2`/`sampler_dff`) defines
`PAD_H_MIN = 0.44`, a *per-device minimum* -- a device whose own W already
exceeds it draws at its own W with no narrowing (`_mos_row._pad_half`). The
`PAD_H` here is different in kind: it is a single *fixed* pad height every
device on a row is widened to, chosen once per cell so it also satisfies
`PAD_H == <the row's own widest switching device's W>` (each of the five
callers asserts this against its own device sizing) and needs no per-device
`max()`. Both constants happen to be 0.44um in this PDK because that is the
contact-safe diffusion floor either way, but they answer different
questions and are kept as distinct names deliberately -- collapsing them
into one shared constant would obscure that `ro_stage`-style cells hand-draw
each device independently while `_mos_row.py`'s callers place an arbitrary
device list generically (see that module's own docstring for why the two
approaches exist side by side rather than one replacing the other).
"""

from __future__ import annotations

PAD_H = 0.44  # comp height at every contacted (source/drain) region


def _pad(y_center: float) -> tuple[float, float]:
    return (y_center - PAD_H / 2, y_center + PAD_H / 2)


def _narrow(y_center: float, w: float) -> tuple[float, float]:
    return (y_center - w / 2, y_center + w / 2)
