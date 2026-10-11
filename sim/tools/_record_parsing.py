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

import math
import re
from collections.abc import Iterator
from typing import NamedTuple

#: The numeric token of a result bullet: the one definition of "what a number
#: may look like" among the sim tools. Embed it (unparenthesised) in a larger
#: pattern; do not re-type it.
NUMBER_PATTERN = r"-?[\d.]+(?:e[-+]?\d+)?"

#: A bullet line of the form "- `key`: [mean ]value", exactly as every
#: sim/records/*.md result section writes one. ``(?:mean\s+)?`` skips past
#: the "mean" of a multi-seed bullet so its point estimate is still
#: captured; the seed count / standard deviation of that form are read by
#: :data:`SEED_SUMMARY_RE` / :func:`iter_seed_summaries`.
#:
#: Group 2 is the numeric *candidate*: a signed run of digits and dots,
#: followed by any number of ``e``/``E`` groups, each with an optional sign
#: and a run of digits and dots. It is deliberately looser than a valid
#: number so a malformed token (``1e+``, ``1.2.3``, ``1e2.3``, ``1e2e3``) is
#: captured whole and rejected by :func:`parse_values` rather than silently
#: matching its valid prefix. The token ends at the first character that
#: cannot continue a number; anything after it (a unit suffix such as ``ns``)
#: is ignored and never scaled.
VALUE_RE = re.compile(
    r"^- `([a-z0-9_]+)`:\s*(?:mean\s+)?([-+]?[\d.]+(?:[eE][-+]?[\d.]*)*)", re.M
)

#: A multi-seed bullet "- `key`: mean X over N seeds (sd Y": groups are
#: key, mean, seed count, standard deviation (``None`` when the bullet has no
#: ``(sd`` clause). Mean and sd are loose candidates like :data:`VALUE_RE`
#: group 2, and the count is any non-blank run, so a malformed token is
#: captured whole and rejected by :func:`iter_seed_summaries` instead of
#: making the bullet silently vanish.
SEED_SUMMARY_RE = re.compile(
    r"^- `([a-z0-9_]+)`:\s*mean\s+([-+]?[\d.]+(?:[eE][-+]?[\d.]*)*)"
    r"\s+over\s+([^\s]+)\s+seeds"
    r"(?:\s*\(sd\s+([-+]?[\d.]+(?:[eE][-+]?[\d.]*)*))?",
    re.M,
)

#: A complete numeric token: digits with an optional fraction (``1``, ``1.``,
#: ``1.5``, ``.5``), then an optional ``e``/``E`` exponent with at least one
#: digit.
_NUMBER_TOKEN_RE = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")

_FRONTMATTER_RE = re.compile(r"---[ \t]*\n(.*?)^---[ \t]*$", re.S | re.M)
_NUMBER = r"[-+]?\d+(?:\.\d+)?"
#: An optional trailing parenthetical remark, e.g. ``(nominal 3.3 V, -10%)``.
_REMARK = r"(?:[ \t]+\(.*\))?"
_PROCESS_RE = re.compile(r"(\w+)" + _REMARK)
_TEMPERATURE_RE = re.compile(rf"({_NUMBER})(?:[ \t]*(?:°C|C))?" + _REMARK)
_VOLTAGE_RE = re.compile(rf"({_NUMBER})(?:[ \t]*V)?" + _REMARK)


def parse_values(
    text: str,
    *,
    label: str = "",
    error_cls: type[Exception] = ValueError,
) -> dict[str, float]:
    """Every ``- `key`: value`` bullet in ``text``, keyed by ``key``.

    The numeric token of each value must be complete (digits, optional
    fraction, optional ``e``/``E`` exponent with digits) and finite. A
    malformed token (``1.2.3``, ``1e+``) or an overflow (``1e999``) raises
    ``error_cls`` naming ``label`` (typically the record's stem) and the
    bullet's key; it never falls back to a valid-looking prefix. A unit
    suffix after the number is ignored, not scaled.
    """
    prefix = f"{label}: " if label else ""
    values: dict[str, float] = {}
    for m in VALUE_RE.finditer(text):
        key, token = m.group(1), m.group(2)
        if _NUMBER_TOKEN_RE.fullmatch(token) is None:
            raise error_cls(f"{prefix}malformed number `{token}` in `{key}`")
        number = float(token)
        if not math.isfinite(number):
            raise error_cls(f"{prefix}non-finite number `{token}` in `{key}`")
        values[key] = number
    return values


class SeedSummary(NamedTuple):
    """The ``mean X over N seeds (sd Y`` shape of one multi-seed bullet."""

    mean: float
    n_seeds: int
    sd: float


def _finite_token(token: str, what: str, key: str, prefix: str, error_cls: type[Exception]) -> float:
    if _NUMBER_TOKEN_RE.fullmatch(token) is None:
        raise error_cls(f"{prefix}malformed {what} `{token}` in `{key}`")
    number = float(token)
    if not math.isfinite(number):
        raise error_cls(f"{prefix}non-finite {what} `{token}` in `{key}`")
    return number


def iter_seed_summaries(
    text: str,
    *,
    label: str = "",
    error_cls: type[Exception] = ValueError,
) -> Iterator[tuple[str, SeedSummary]]:
    """Every multi-seed bullet in ``text`` as ``(key, SeedSummary)``, in order.

    Mean and sd must be complete, finite numbers (``e``/``E`` exponent
    allowed), the seed count a positive integer, and sd nonnegative (zero is
    valid). A violation raises ``error_cls`` naming ``label`` and the
    bullet's key. A ``mean X over N seeds`` bullet with no ``(sd`` clause is
    a legacy shape (e.g. ``2026-07-31-nfet-mismatch-seed-01.md``) and is
    skipped, as before, once its mean and count have been checked.
    """
    prefix = f"{label}: " if label else ""
    for m in SEED_SUMMARY_RE.finditer(text):
        key, mean_t, count_t, sd_t = m.groups()
        mean = _finite_token(mean_t, "mean", key, prefix, error_cls)
        if re.fullmatch(r"\d+", count_t) is None:
            raise error_cls(f"{prefix}malformed seed count `{count_t}` in `{key}`")
        n_seeds = int(count_t)
        if n_seeds < 1:
            raise error_cls(f"{prefix}seed count `{count_t}` must be >= 1 in `{key}`")
        if sd_t is None:
            continue
        sd = _finite_token(sd_t, "sd", key, prefix, error_cls)
        if sd < 0:
            raise error_cls(f"{prefix}negative sd `{sd_t}` in `{key}`")
        yield key, SeedSummary(mean, n_seeds, sd)


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


def frontmatter(
    text: str,
    *,
    label: str = "",
    error_cls: type[Exception] = RuntimeError,
) -> str:
    """The body of the record's leading ``---`` frontmatter block.

    The block must start on the first line of ``text`` and be closed by a
    second ``---`` line; anything else raises ``error_cls`` naming ``label``.
    Metadata read through this helper can never come from the record's prose.
    """
    m = _FRONTMATTER_RE.match(text)
    if m is None:
        prefix = f"{label}: " if label else ""
        raise error_cls(
            f"{prefix}no complete leading frontmatter block (opening and "
            "closing `---` lines)"
        )
    return m.group(1)


def _unique_field(
    fm: str,
    key: str,
    *,
    indented: bool,
    label: str,
    error_cls: type[Exception],
) -> str:
    """The single value of ``key:`` in frontmatter ``fm``; zero or several raise."""
    lead = r"[ \t]*" if indented else ""
    values = re.findall(rf"^{lead}{key}:[ \t]*(.*?)[ \t]*$", fm, re.M)
    prefix = f"{label}: " if label else ""
    if not values:
        raise error_cls(f"{prefix}frontmatter has no `{key}:` field")
    if len(values) > 1:
        raise error_cls(
            f"{prefix}frontmatter has {len(values)} `{key}:` fields "
            "(exactly one is required)"
        )
    return values[0]


def _scalar(
    fm: str,
    key: str,
    pattern: re.Pattern[str],
    *,
    label: str,
    error_cls: type[Exception],
) -> str:
    value = _unique_field(fm, key, indented=True, label=label, error_cls=error_cls)
    m = pattern.fullmatch(value)
    if m is None:
        prefix = f"{label}: " if label else ""
        raise error_cls(f"{prefix}malformed `{key}: {value}` in the frontmatter")
    return m.group(1)


def parse_corner(
    text: str,
    *,
    label: str = "",
    error_cls: type[Exception] = RuntimeError,
) -> tuple[str, float, float]:
    """``(process, temp_c, vdd)`` from a record's frontmatter corner fields.

    ``text`` is the complete record. Only the leading frontmatter block is
    read; each of ``process:``, ``temperature:`` and ``voltage:`` must occur
    exactly once there. Temperature and voltage are parsed as complete
    scalars -- a decimal number, an optional ``C``/``V`` unit and an optional
    parenthetical remark -- and must be finite. Every failure raises
    ``error_cls`` naming ``label`` and the offending field.
    """
    fm = frontmatter(text, label=label, error_cls=error_cls)
    kw = {"label": label, "error_cls": error_cls}
    process = _scalar(fm, "process", _PROCESS_RE, **kw)
    values = []
    for key, pat in (("temperature", _TEMPERATURE_RE), ("voltage", _VOLTAGE_RE)):
        number = float(_scalar(fm, key, pat, **kw))
        if not math.isfinite(number):
            prefix = f"{label}: " if label else ""
            raise error_cls(f"{prefix}non-finite `{key}:` in the frontmatter")
        values.append(number)
    return process, values[0], values[1]


#: The lifecycle values ``sim/README.md`` defines for a record's ``status:``.
STATUS_VALUES = ("valid", "superseded")


def parse_status(
    text: str,
    *,
    label: str = "",
    error_cls: type[Exception] = RuntimeError,
) -> str:
    """The record's frontmatter ``status:`` (``valid`` or ``superseded``).

    Only the leading ``---`` frontmatter block is read, so a ``status:`` line
    quoted in a record's body can never decide a record's lifecycle. The
    field must occur exactly once; a missing, duplicated, empty or unknown
    value raises ``error_cls`` naming ``label``: a record whose lifecycle
    cannot be established is never guessed at.
    """
    prefix = f"{label}: " if label else ""
    try:
        fm = frontmatter(text, label=label, error_cls=error_cls)
    except error_cls as exc:
        raise error_cls(f"{prefix}no frontmatter block, so no lifecycle `status:`") from exc
    value = _unique_field(fm, "status", indented=False, label=label, error_cls=error_cls)
    if value not in STATUS_VALUES:
        raise error_cls(
            f"{prefix}unknown `status: {value}` (expected one of "
            f"{', '.join(STATUS_VALUES)})"
        )
    return value


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
