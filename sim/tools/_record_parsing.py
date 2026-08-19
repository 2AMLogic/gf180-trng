#!/usr/bin/env python3
"""Shared evidence-record parsing for ``sim/tools/*.py`` (issue #104).

Every script under ``sim/tools/`` that reads a committed ``sim/records/*.md``
evidence record parses the same two things out of its frontmatter and body:
the ``- `key`: value`` bullet lines, and the ``process:``/``temperature:``/
``voltage:`` corner triplet. Before this module existed, six scripts
(``array_sizing.py``, ``time_to_first_valid.py``, ``power_rollup.py``,
``starved_cell_jitter_energy.py``, ``raw_min_entropy_estimate.py``,
``jitter_energy_law.py``) each carried their own copy of the bullet regex
and/or the corner triplet, plus their own "``re.search``, raise if
``None``, return ``group(1)``" helper -- four different call conventions
(``@staticmethod``, instance method, module function, closure) for the same
shape. ``jitter_estimator_calibration_check.py`` duplicated the bullet
regex too, without the corner triplet.

This module is that one place. It is deliberately NOT a ``Record`` base
class: the seven callers' record shapes differ too much for that (plain
bullets vs. multi-seed ``mean ... over N seeds (sd ...)`` bullets, whether a
``netlist:`` block is read, whether the corner is even parsed) -- only the
low-level field extraction is common, and that is what is factored out
here. Each caller keeps its own ``Record``/``BitstreamRecord`` class and its
own module-level ``RecordError`` (where it has one); this module never
raises its own exception type by default, so those ``except RecordError``
call sites elsewhere in ``sim/tools/`` (and in scripts that import
``RecordError`` from one of the seven) keep working unchanged.
"""

from __future__ import annotations

import re

#: A bullet line of the form "- `key`: [mean ]value", exactly as every
#: sim/records/*.md result section writes one. ``(?:mean\s+)?`` skips past
#: the "mean" of a multi-seed bullet so its point estimate is still
#: captured; a caller that also needs the seed count / standard deviation
#: (``starved_cell_jitter_energy.py``, ``raw_min_entropy_estimate.py``)
#: parses those itself -- that shape is not common enough across all seven
#: callers to belong here.
VALUE_RE = re.compile(r"^- `([a-z0-9_]+)`:\s*(?:mean\s+)?(-?[\d.]+(?:e[-+]?\d+)?)", re.M)

_PROCESS_PATTERN = r"process:\s*(\w+)"
_TEMPERATURE_PATTERN = r"temperature:\s*(-?[\d.]+)"
_VOLTAGE_PATTERN = r"voltage:\s*([\d.]+)"


def parse_values(text: str) -> dict[str, float]:
    """Every ``- `key`: value`` bullet in ``text``, keyed by ``key``."""
    return {m.group(1): float(m.group(2)) for m in VALUE_RE.finditer(text)}


def field(
    text: str,
    pattern: str,
    *,
    label: str = "",
    error_cls: type[Exception] = RuntimeError,
) -> str:
    """The first capture group of ``pattern`` in ``text``, or raise.

    This is the "``re.search``, raise if ``None``, return ``group(1)``"
    helper all seven ``sim/tools/*.py`` record parsers used to reimplement
    independently. ``label`` (typically the record's stem or path) is
    folded into the error message so a failure names which record was
    unparsable. ``error_cls`` lets a caller raise its own module's
    ``RecordError`` instead of a bare ``RuntimeError``, so a caller's
    existing ``except RecordError`` handling (its own, or a downstream
    script's, e.g. ``array_coupling_buffer_variant.py`` importing
    ``RecordError`` from ``starved_cell_jitter_energy``) keeps catching the
    same exception type it always did.

    ``re.MULTILINE`` is used for the search: none of the patterns the seven
    callers pass rely on ``^``/``$`` matching only the absolute start/end of
    ``text`` (only ``raw_min_entropy_estimate.py``'s ``seeds:`` field
    anchors on ``^`` at all, and it needs line-start semantics), so this is
    safe for every existing caller.
    """
    m = re.search(pattern, text, re.M)
    if m is None:
        prefix = f"{label}: " if label else ""
        raise error_cls(f"{prefix}cannot find {pattern!r} in the frontmatter")
    return m.group(1)


def parse_corner(
    text: str,
    *,
    label: str = "",
    error_cls: type[Exception] = RuntimeError,
) -> tuple[str, float, float]:
    """``(process, temp_c, vdd)`` from a record's ``process:``/
    ``temperature:``/``voltage:`` frontmatter lines -- the corner triplet
    every one of the seven callers parses identically.
    """
    process = field(text, _PROCESS_PATTERN, label=label, error_cls=error_cls)
    temp_c = float(field(text, _TEMPERATURE_PATTERN, label=label, error_cls=error_cls))
    vdd = float(field(text, _VOLTAGE_PATTERN, label=label, error_cls=error_cls))
    return process, temp_c, vdd


def format_corner(process: str, temp_c: float, vdd: float) -> str:
    """The canonical ``process/temp_c/vdd`` corner label, e.g. ``tt/27/3.30``.

    Before issue #104, ``power_rollup.py`` and ``time_to_first_valid.py``
    formatted this as ``process/temp_cC/vddV`` (with units) while the other
    five callers formatted it as plain ``process/temp_c/vdd`` -- the same
    logical corner rendered two different ways depending which script
    computed it. This is the plain form: every hardcoded
    ``CORNER``/``POWER_CORNER``/``PREDICTED_MIN_Q_CORNER``/
    ``MEASURED_MIN_Q_CORNER`` constant elsewhere in ``sim/tools/`` that
    compares against a parsed record's ``.corner`` was already written
    against it, so standardizing on the with-units form would have meant
    touching more call sites, not fewer.
    """
    return f"{process}/{temp_c:.0f}/{vdd:.2f}"
