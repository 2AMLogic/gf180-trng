#!/usr/bin/env python3
"""The transistor-derived raw-bit input for the top-level smoke demonstration.

DR-0009 rule 4: "A behavioural record must name its input source." This one
uses the **transistor-derived** option DR-0009 §2 prefers whenever a stream
exists and is long enough: the ten raw bits ``sim/tb/sampler-array-digitize/``
already captured from the shipped entropy source and the shipped sampler, at
the nominal corner (``tt`` / 27 C / 3.30 V), in the append-only record
``sim/records/2026-08-01-sampler-array-digitize-03.md``.

This module does **not** re-run ngspice -- that record is already committed
evidence, and re-simulating it would cost the better part of an hour
(``wall_time: 50.9m`` in that record's own frontmatter) for bits this module
can read straight out of the record's own Result section. Ten bits is far
too short to exercise a DR-0002 start-up window (1024 samples) or an APT
window (1024 samples) -- deliberately: this is the top-level assembly's
smoke input, proving the chain produces bits end to end, not a re-run of
the entropy or health-test characterization those longer, PVT-swept
testbenches already own (see design/trng_top/README.md).

The ten voltage means are parsed directly out of the record's committed
Markdown (its own numbers, not re-derived) and thresholded against the
nominal 3.3 V supply the record itself ran at -- the same logic
``tb_sampler_array_digitize.sp``'s own ``level``/``railerr`` measurements
use, restated here in Python so this module's bit values are mechanically
traceable to that record rather than hand-copied from its prose.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

#: The cited record. Append-only: never edited, never re-run by this module.
SOURCE_RECORD = REPO_ROOT / "sim" / "records" / "2026-08-01-sampler-array-digitize-03.md"

#: The nominal corner that record ran at (its own `corner:` frontmatter).
SOURCE_CORNER = {"process": "tt", "temperature_c": 27, "voltage_v": 3.30}

_MEAN_RE = re.compile(r"^- `(b\d)_v`: mean (\S+) over")


def raw_bits() -> list[int]:
    """The ten raw bits (``b0``..``b9``), in sample order, thresholded at
    mid-supply against :data:`SOURCE_CORNER`'s 3.30 V."""
    text = SOURCE_RECORD.read_text()
    means: dict[str, float] = {}
    for line in text.splitlines():
        m = _MEAN_RE.match(line)
        if m:
            means[m.group(1)] = float(m.group(2))
    if len(means) != 10:
        raise RuntimeError(
            f"expected 10 b0..b9 measurements in {SOURCE_RECORD}, found {len(means)}"
        )
    half = SOURCE_CORNER["voltage_v"] / 2
    return [1 if means[f"b{i}"] > half else 0 for i in range(10)]
