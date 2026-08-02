"""Minimal, deterministic GDSII stream writer (Python standard library only).

Why this exists
---------------
The layout verification flow in this directory needs *fixtures*: a layout
whose geometry is known-good and a layout whose geometry is known-bad, so
that "the DRC deck reported clean" and "the DRC deck reported exactly rule
X" are both demonstrated rather than asserted. `klt gen` produces
PDK-validated cells and deliberately refuses out-of-range parameters, so it
cannot emit a rule-violating fixture (see `layout/README.md`, "Tool
friction"). Nothing else in the flow writes a stream.

So the fixtures are drawn here, from an explicit rectangle list, by a writer
small enough to audit in one sitting. Scope is exactly what the fixtures
need and nothing more:

* one library, one or more flat structures (no SREF/AREF hierarchy),
* axis-aligned rectangles emitted as BOUNDARY elements,
* TEXT elements (used for the Metal1 pin labels the extractor reads),
* a fixed database unit of 1 nm (user unit 1 um), matching what both
  curated `klt` decks are authored against.

Determinism is a requirement, not a nicety: `layout/verify.py --check`
rebuilds the fixtures and compares them byte-for-byte against the committed
`.gds` files, so a silent geometry drift cannot hide behind a stale report.
Every timestamp field is therefore written as zero rather than "now".

Reference: the GDSII Stream Format specification (record header = 2-byte
big-endian record length including the header, 1-byte record type, 1-byte
data type).
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

# Record types used here (GDSII record-type byte, data-type byte).
_HEADER = (0x00, 0x02)
_BGNLIB = (0x01, 0x02)
_LIBNAME = (0x02, 0x06)
_UNITS = (0x03, 0x05)
_ENDLIB = (0x04, 0x00)
_BGNSTR = (0x05, 0x02)
_STRNAME = (0x06, 0x06)
_ENDSTR = (0x07, 0x00)
_BOUNDARY = (0x08, 0x00)
_TEXT = (0x0C, 0x00)
_LAYER = (0x0D, 0x02)
_DATATYPE = (0x0E, 0x02)
_XY = (0x10, 0x03)
_ENDEL = (0x11, 0x00)
_TEXTTYPE = (0x16, 0x02)
_STRING = (0x19, 0x06)

#: Database unit in metres, and user unit in database units. 1 nm / 1 um --
#: the `dbu_um = 0.001` both curated klt decks (`sky130`, `gf180mcu`) are
#: authored against.
DBU_M = 1e-9
USER_UNIT_IN_DBU = 1e-3

#: Every fixture is written with zeroed modification/access timestamps so
#: the byte stream is a pure function of the geometry.
_ZERO_TIME = (0,) * 12


@dataclass(frozen=True)
class Rect:
    """One axis-aligned rectangle, in micrometres, on one (layer, datatype).

    `x0`/`y0` are the lower-left corner and `x1`/`y1` the upper-right; the
    writer normalises the ordering, so a caller cannot silently emit an
    inverted (zero- or negative-area) polygon.
    """

    layer: int
    datatype: int
    x0: float
    y0: float
    x1: float
    y1: float

    def __post_init__(self) -> None:
        if self.x0 == self.x1 or self.y0 == self.y1:
            raise ValueError(f"degenerate rectangle: {self}")


@dataclass(frozen=True)
class Label:
    """One TEXT element, in micrometres, on one (layer, texttype).

    The gf180mcu extraction deck reads net names from Metal1's pin/label
    purpose (34/10); `layout/testcells/build.py` places one of these on each
    port net so the extracted netlist carries readable net names instead of
    the extractor's anonymous `$1`, `$2`, ... numbering.
    """

    layer: int
    texttype: int
    x: float
    y: float
    text: str


def _record(rec_type: int, data_type: int, payload: bytes) -> bytes:
    """Frame one GDSII record. Payload is padded to an even byte count."""
    if len(payload) % 2:
        payload += b"\x00"
    length = len(payload) + 4
    if length > 0xFFFF:
        raise ValueError(f"record too long for GDSII: {length} bytes")
    return struct.pack(">HBB", length, rec_type, data_type) + payload


def _no_data(rec: tuple[int, int]) -> bytes:
    return _record(rec[0], rec[1], b"")


def _int2(rec: tuple[int, int], *values: int) -> bytes:
    return _record(rec[0], rec[1], b"".join(struct.pack(">h", v) for v in values))


def _int4(rec: tuple[int, int], *values: int) -> bytes:
    return _record(rec[0], rec[1], b"".join(struct.pack(">i", v) for v in values))


def _ascii(rec: tuple[int, int], value: str) -> bytes:
    return _record(rec[0], rec[1], value.encode("ascii"))


def _real8(value: float) -> bytes:
    """Encode one GDSII 8-byte real (excess-64, base-16 mantissa).

    Layout: sign bit, 7-bit exponent biased by 64 in powers of 16, then a
    56-bit fraction interpreted as mantissa / 2**56. Only positive finite
    values are ever written by this module (both UNITS fields), so the
    general case is deliberately not implemented.
    """
    if value <= 0:
        raise ValueError(f"_real8 only encodes positive values, got {value}")
    sign = 0
    exponent = 64
    # Normalise into [1/16, 1).
    while value >= 1.0:
        value /= 16.0
        exponent += 1
    while value < 1.0 / 16.0:
        value *= 16.0
        exponent -= 1
    if not 0 <= exponent <= 127:
        raise ValueError(f"_real8 exponent out of range for {value}")
    mantissa = int(round(value * (1 << 56)))
    if mantissa >= (1 << 56):  # rounding pushed it over; renormalise
        mantissa >>= 4
        exponent += 1
    return struct.pack(">B", sign | exponent) + mantissa.to_bytes(7, "big")


def _units_record() -> bytes:
    return _record(_UNITS[0], _UNITS[1], _real8(USER_UNIT_IN_DBU) + _real8(DBU_M))


def _to_dbu(value_um: float) -> int:
    """Micrometres -> database units, rounded to the nearest nanometre.

    Rounding (rather than truncation) keeps a value like 0.07 um, which is
    not exactly representable in binary floating point, from landing one
    database unit short of the enclosure it was written to satisfy.
    """
    return int(round(value_um / USER_UNIT_IN_DBU))


def _boundary(rect: Rect) -> bytes:
    x0, x1 = sorted((_to_dbu(rect.x0), _to_dbu(rect.x1)))
    y0, y1 = sorted((_to_dbu(rect.y0), _to_dbu(rect.y1)))
    # GDSII boundaries are closed: the first point is repeated last.
    points = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    flat: list[int] = [coordinate for point in points for coordinate in point]
    return (
        _no_data(_BOUNDARY)
        + _int2(_LAYER, rect.layer)
        + _int2(_DATATYPE, rect.datatype)
        + _int4(_XY, *flat)
        + _no_data(_ENDEL)
    )


def _text(label: Label) -> bytes:
    return (
        _no_data(_TEXT)
        + _int2(_LAYER, label.layer)
        + _int2(_TEXTTYPE, label.texttype)
        + _int4(_XY, _to_dbu(label.x), _to_dbu(label.y))
        + _ascii(_STRING, label.text)
        + _no_data(_ENDEL)
    )


def write_gds(
    path: str,
    library_name: str,
    structures: list[tuple[str, list[Rect], list[Label]]],
) -> bytes:
    """Write `structures` to `path` as a GDSII stream and return the bytes.

    `structures` is an ordered list of `(cell_name, rectangles, labels)`.
    Order is preserved into the stream, so the output is a pure function of
    the input -- see this module's docstring on why that matters.
    """
    stream = bytearray()
    stream += _int2(_HEADER, 600)  # stream version 6.0.0
    stream += _int2(_BGNLIB, *_ZERO_TIME)
    stream += _ascii(_LIBNAME, library_name)
    stream += _units_record()
    for cell_name, rects, labels in structures:
        stream += _int2(_BGNSTR, *_ZERO_TIME)
        stream += _ascii(_STRNAME, cell_name)
        for rect in rects:
            stream += _boundary(rect)
        for label in labels:
            stream += _text(label)
        stream += _no_data(_ENDSTR)
    stream += _no_data(_ENDLIB)

    payload = bytes(stream)
    with open(path, "wb") as handle:
        handle.write(payload)
    return payload
