#!/usr/bin/env python3
"""Unit tests for the hand-rolled GDSII writer, `layout/testcells/gdsii.py`.

The fixture freshness gate (`npm run check:fixtures`) only proves that
regenerating the fixtures reproduces the committed bytes. That is a
self-consistency check: an encoding bug committed once stays "fresh"
forever. These tests check the encoding against independently derived
expectations instead (hand-computed vectors, an independent decoder, and a
minimal record reader), so they need no `klt` and no PDK.

Helpers covered: `_real8`, `_to_dbu`, `_record`, `_no_data`, `_int2`,
`_int4`, `_ascii`, `_units_record`, `_boundary`, `_text`, `write_gds`, and
the `Rect` dataclass's degenerate-rectangle validation.
"""

from __future__ import annotations

import importlib.util
import sys
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_GDSII_PATH = Path(__file__).resolve().parents[1] / "testcells" / "gdsii.py"
_SPEC = importlib.util.spec_from_file_location("_gdsii_under_test", _GDSII_PATH)
gdsii = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = gdsii  # dataclasses resolves annotations via sys.modules
_SPEC.loader.exec_module(gdsii)  # type: ignore[union-attr]

UNITS_HEX = ("3e4189374bc6a7f0", "3944b82fa09b5a54")  # 1e-3 and 1e-9


def decode_real8(raw: bytes) -> float:
    """Independent reference decoder for a GDSII 8-byte real."""
    assert len(raw) == 8
    sign = -1.0 if raw[0] & 0x80 else 1.0
    exponent = (raw[0] & 0x7F) - 64
    mantissa = int.from_bytes(raw[1:], "big")
    return sign * (mantissa / 2**56) * 16.0**exponent


def read_records(stream: bytes) -> list[tuple[int, int, bytes]]:
    """Minimal record reader: [(record_type, data_type, payload), ...]."""
    records = []
    pos = 0
    while pos < len(stream):
        length, rec_type, data_type = struct.unpack_from(">HBB", stream, pos)
        assert length >= 4 and length % 2 == 0
        records.append((rec_type, data_type, stream[pos + 4 : pos + length]))
        pos += length
    assert pos == len(stream)
    return records


class Real8Tests(unittest.TestCase):
    def test_known_vectors(self) -> None:
        vectors = {
            1.0: "4110000000000000",
            0.5: "4080000000000000",
            1e-3: UNITS_HEX[0],
            1e-9: UNITS_HEX[1],
        }
        for value, expected in vectors.items():
            with self.subTest(value=value):
                self.assertEqual(gdsii._real8(value).hex(), expected)

    def test_round_trip_through_independent_decoder(self) -> None:
        for value in (1.0, 0.5, 1e-3, 1e-9, 0.07, 3.0, 123456.789, 1e-30, 1e30):
            with self.subTest(value=value):
                decoded = decode_real8(gdsii._real8(value))
                self.assertLess(abs(decoded - value) / value, 2.0**-52)

    def test_non_positive_rejected(self) -> None:
        for value in (0.0, -1.0, -1e-9):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    gdsii._real8(value)

    def test_exponent_out_of_range_rejected(self) -> None:
        with self.assertRaises(ValueError):
            gdsii._real8(1e300)
        with self.assertRaises(ValueError):
            gdsii._real8(1e-300)

    def test_largest_double_below_one(self) -> None:
        # Top of the [1/16, 1) mantissa range; must not overflow the field.
        value = 1.0 - 2.0**-53
        raw = gdsii._real8(value)
        self.assertEqual(raw[0], 64)
        self.assertEqual(decode_real8(raw), value)

    def test_renormalise_branch(self) -> None:
        # Every double in [1/16, 1) scales to an exactly representable
        # integer, so ordinary inputs cannot round up to 2**56. Force the
        # rounding result to exercise the branch: it must carry into the
        # next exponent and encode the same value as 1.0.
        with mock.patch.object(gdsii, "round", lambda _x: 1 << 56, create=True):
            raw = gdsii._real8(0.5)
        self.assertEqual(raw.hex(), "4110000000000000")
        self.assertEqual(decode_real8(raw), 1.0)


class ToDbuTests(unittest.TestCase):
    def test_enclosure_value(self) -> None:
        self.assertEqual(gdsii._to_dbu(0.07), 70)

    def test_non_binary_exact_values(self) -> None:
        cases = {0.001: 1, 0.005: 5, 0.1: 100, 0.29: 290, 0.57: 570, 1.15: 1150, 4.35: 4350}
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(gdsii._to_dbu(value), expected)

    def test_negative_and_zero(self) -> None:
        self.assertEqual(gdsii._to_dbu(0.0), 0)
        self.assertEqual(gdsii._to_dbu(-0.07), -70)

    def test_rounds_to_nearest(self) -> None:
        self.assertEqual(gdsii._to_dbu(0.0704), 70)
        self.assertEqual(gdsii._to_dbu(0.0706), 71)


class RecordTests(unittest.TestCase):
    def test_even_payload_unpadded(self) -> None:
        self.assertEqual(gdsii._record(0x06, 0x06, b"AB"), b"\x00\x06\x06\x06AB")

    def test_odd_payload_padded(self) -> None:
        self.assertEqual(gdsii._record(0x06, 0x06, b"ABC"), b"\x00\x08\x06\x06ABC\x00")

    def test_empty_payload(self) -> None:
        self.assertEqual(gdsii._record(0x04, 0x00, b""), b"\x00\x04\x04\x00")

    def test_largest_payload_accepted(self) -> None:
        # Length is payload + 4 and always even, so the largest framed
        # record is 0xFFFE bytes (payload 0xFFFA).
        out = gdsii._record(0x06, 0x06, b"x" * 0xFFFA)
        self.assertEqual(struct.unpack_from(">H", out)[0], 0xFFFE)
        self.assertEqual(len(out), 0xFFFE)

    def test_oversize_rejected(self) -> None:
        with self.assertRaises(ValueError):
            gdsii._record(0x06, 0x06, b"x" * 0xFFFC)
        # An odd payload that pads over the limit is rejected too.
        with self.assertRaises(ValueError):
            gdsii._record(0x06, 0x06, b"x" * 0xFFFB)

    def test_typed_helpers(self) -> None:
        self.assertEqual(gdsii._no_data(gdsii._ENDEL), b"\x00\x04\x11\x00")
        self.assertEqual(gdsii._int2((0x0D, 0x02), 1, -2), b"\x00\x08\x0d\x02\x00\x01\xff\xfe")
        self.assertEqual(gdsii._int4((0x10, 0x03), -1), b"\x00\x08\x10\x03\xff\xff\xff\xff")
        self.assertEqual(gdsii._ascii((0x06, 0x06), "TOP"), b"\x00\x08\x06\x06TOP\x00")

    def test_non_ascii_rejected(self) -> None:
        with self.assertRaises(UnicodeEncodeError):
            gdsii._ascii((0x06, 0x06), "café")

    def test_units_record(self) -> None:
        rec = gdsii._units_record()
        self.assertEqual(rec[:4], b"\x00\x14\x03\x05")
        self.assertEqual(rec[4:12].hex(), UNITS_HEX[0])
        self.assertEqual(rec[12:].hex(), UNITS_HEX[1])


class ShapeTests(unittest.TestCase):
    def test_degenerate_rect_rejected(self) -> None:
        with self.assertRaises(ValueError):
            gdsii.Rect(1, 0, 0.0, 0.0, 0.0, 1.0)
        with self.assertRaises(ValueError):
            gdsii.Rect(1, 0, 0.0, 1.0, 2.0, 1.0)

    def test_boundary_closed_sorted_corners(self) -> None:
        # Corners given inverted; the writer must normalise them.
        rect = gdsii.Rect(7, 3, 2.0, 1.5, 0.07, 0.5)
        recs = read_records(gdsii._boundary(rect))
        self.assertEqual([r[0] for r in recs], [0x08, 0x0D, 0x0E, 0x10, 0x11])
        self.assertEqual(struct.unpack(">h", recs[1][2])[0], 7)
        self.assertEqual(struct.unpack(">h", recs[2][2])[0], 3)
        x0, x1, y0, y1 = 70, 2000, 500, 1500
        self.assertEqual(
            struct.unpack(">10i", recs[3][2]),
            (x0, y0, x1, y0, x1, y1, x0, y1, x0, y0),
        )

    def test_text_record(self) -> None:
        label = gdsii.Label(34, 10, 1.25, 0.07, "vdd")
        recs = read_records(gdsii._text(label))
        self.assertEqual([r[0] for r in recs], [0x0C, 0x0D, 0x16, 0x10, 0x19, 0x11])
        self.assertEqual(struct.unpack(">h", recs[1][2])[0], 34)
        self.assertEqual(struct.unpack(">h", recs[2][2])[0], 10)
        self.assertEqual(struct.unpack(">2i", recs[3][2]), (1250, 70))
        self.assertEqual(recs[4][2], b"vdd\x00")


class WriteGdsTests(unittest.TestCase):
    STRUCTURES = [
        (
            "CELL_A",
            [gdsii.Rect(1, 0, 0.0, 0.0, 1.0, 2.0), gdsii.Rect(2, 5, 0.5, 0.5, 0.57, 0.9)],
            [gdsii.Label(34, 10, 0.5, 1.0, "A")],
        ),
        ("CELL_B", [], []),
    ]

    def _write(self, directory: str, name: str = "out.gds") -> tuple[Path, bytes]:
        path = Path(directory) / name
        returned = gdsii.write_gds(str(path), "TESTLIB", self.STRUCTURES)
        return path, returned

    def test_returns_bytes_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, returned = self._write(tmp)
            self.assertEqual(path.read_bytes(), returned)

    def test_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _, stream = self._write(tmp)
        recs = read_records(stream)
        self.assertEqual(
            [r[0] for r in recs],
            [0x00, 0x01, 0x02, 0x03]
            # CELL_A: BGNSTR STRNAME, 2 boundaries, 1 text, ENDSTR
            + [0x05, 0x06]
            + [0x08, 0x0D, 0x0E, 0x10, 0x11] * 2
            + [0x0C, 0x0D, 0x16, 0x10, 0x19, 0x11]
            + [0x07]
            # CELL_B
            + [0x05, 0x06, 0x07]
            + [0x04],
        )
        self.assertEqual(struct.unpack(">h", recs[0][2])[0], 600)
        self.assertEqual(struct.unpack(">12h", recs[1][2]), (0,) * 12)
        self.assertEqual(recs[2][2], b"TESTLIB\x00")
        self.assertEqual(
            (decode_real8(recs[3][2][:8]), decode_real8(recs[3][2][8:])),
            (gdsii.USER_UNIT_IN_DBU, gdsii.DBU_M),
        )
        self.assertEqual(struct.unpack(">12h", recs[4][2]), (0,) * 12)
        self.assertEqual(recs[5][2], b"CELL_A")
        # First boundary XY: closed, 5 points.
        self.assertEqual(
            struct.unpack(">10i", recs[9][2]),
            (0, 0, 1000, 0, 1000, 2000, 0, 2000, 0, 0),
        )
        # Second boundary exercises the 0.57 um (non-binary-exact) value.
        self.assertEqual(
            struct.unpack(">10i", recs[14][2]),
            (500, 500, 570, 500, 570, 900, 500, 900, 500, 500),
        )
        # TEXT element.
        self.assertEqual(struct.unpack(">2i", recs[19][2]), (500, 1000))
        self.assertEqual(recs[20][2], b"A\x00")
        self.assertEqual(recs[-4][2], b"CELL_B")

    def test_empty_structure_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stream = gdsii.write_gds(str(Path(tmp) / "e.gds"), "L", [])
        self.assertEqual([r[0] for r in read_records(stream)], [0x00, 0x01, 0x02, 0x03, 0x04])

    def test_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p1, first = self._write(tmp, "a.gds")
            p2, second = self._write(tmp, "b.gds")
            self.assertEqual(first, second)
            self.assertEqual(p1.read_bytes(), p2.read_bytes())

    def test_structure_order_preserved(self) -> None:
        reordered = list(reversed(self.STRUCTURES))
        with tempfile.TemporaryDirectory() as tmp:
            stream = gdsii.write_gds(str(Path(tmp) / "r.gds"), "TESTLIB", reordered)
        names = [r[2] for r in read_records(stream) if r[0] == 0x06]
        self.assertEqual(names, [b"CELL_B", b"CELL_A"])


if __name__ == "__main__":
    unittest.main()
