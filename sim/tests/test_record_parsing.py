#!/usr/bin/env python3
"""Direct unit tests for ``sim/tools/_record_parsing.py`` (issue #345).

That module is the shared evidence-record parser behind seven
``sim/tools/*.py`` derivation scripts (issue #104). Those scripts are checked
end to end against the committed records by ``npm run check:spec``, but an
end-to-end check only shows that today's records parse to today's numbers;
it does not pin the parser's own extraction and error contracts. These tests
do, against small synthetic fixtures whose expected values are written out by
hand here, plus a verbatim excerpt of one committed evidence record.

The contracts pinned are the module's *current* behaviour, including the
parts a reader might not expect:

- ``parse_values`` converts the numeric prefix of a bullet value and ignores
  any unit suffix -- ``2.5ns`` parses to ``2.5``, with no SI scaling.
- ``field`` returns the raw capture string and raises only when the pattern
  does not match; numeric validation is the caller's job.
- ``parse_corner`` converts temperature and supply with ``float``, so a
  malformed capture raises ``ValueError`` regardless of ``error_cls``.
- ``format_corner`` rounds temperature to zero decimal places and supply to
  two, so it is not a lossless inverse of ``parse_corner``.

Everything here is stdlib-only: no ngspice and no PDK.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent

sys.path.insert(0, str(SIM_DIR / "tools"))

from _record_parsing import (  # noqa: E402
    field,
    format_corner,
    parse_corner,
    parse_values,
)

#: The committed record the excerpt below is copied from (read only).
RECORD_PATH = SIM_DIR / "records" / "2026-07-31-ro-inv-05stage-jitter-01.md"

#: Verbatim lines from RECORD_PATH: its corner block and two of its
#: multi-seed result bullets. Embedded rather than read at test time so the
#: expected values below are specified independently of the file; the
#: provenance test checks the lines are still present in the record.
RECORD_EXCERPT = """\
corner:
  process: tt
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: -40

- `period`: mean 5.951232e-10 over 4 seeds (sd 5.590174e-15, 0.0% of mean; min 5.951178e-10, max 5.951289e-10)
- `f_osc`: mean 1.680324e+09 over 4 seeds (sd 15783.8, 0.0% of mean; min 1.680308e+09, max 1.680340e+09)
"""


class CustomRecordError(Exception):
    """Stand-in for a calling tool's own module-level ``RecordError``."""


class CustomRecordErrorSubclass(CustomRecordError):
    """A caller-defined subclass, to check ``error_cls`` is used as given."""


def _corner_text(
    process: str | None = "tt",
    temperature: str | None = "27",
    voltage: str | None = "3.30",
) -> str:
    """A minimal frontmatter corner block; pass ``None`` to omit a line."""
    lines = ["corner:"]
    if process is not None:
        lines.append(f"  process: {process}")
    if voltage is not None:
        lines.append(f"  voltage: {voltage} V")
    if temperature is not None:
        lines.append(f"  temperature: {temperature}")
    return "\n".join(lines) + "\n"


class ParseValuesTests(unittest.TestCase):
    def test_plain_number(self) -> None:
        self.assertEqual(parse_values("- `count`: 42\n"), {"count": 42.0})

    def test_decimal_number(self) -> None:
        self.assertEqual(parse_values("- `ratio`: 0.125\n"), {"ratio": 0.125})

    def test_negative_number(self) -> None:
        self.assertEqual(parse_values("- `offset`: -3.5\n"), {"offset": -3.5})

    def test_lowercase_scientific_notation(self) -> None:
        text = "- `small`: 1.5e-12\n- `large`: 2e+09\n- `bare_exp`: 4e3\n"
        self.assertEqual(
            parse_values(text),
            {"small": 1.5e-12, "large": 2e9, "bare_exp": 4000.0},
        )

    def test_optional_mean_prefix(self) -> None:
        text = "- `sigma_1`: mean 9.5e-14 over 4 seeds (sd 3.2e-15)\n"
        self.assertEqual(parse_values(text), {"sigma_1": 9.5e-14})

    def test_unit_suffix_is_not_scaled(self) -> None:
        # Only the numeric prefix is converted: "ns" is not applied as 1e-9.
        self.assertEqual(parse_values("- `delay`: 2.5ns\n"), {"delay": 2.5})

    def test_unmatched_bullets_are_omitted(self) -> None:
        text = (
            "- `kept`: 1.0\n"
            "- `Upper`: 2.0\n"  # key must be [a-z0-9_]
            "- `text_value`: abc\n"  # value must start numeric
            "- plain bullet: 3.0\n"  # key must be backtick-delimited
            "  - `indented`: 4.0\n"  # bullet must start the line
            "prose `inline`: 5.0\n"
        )
        self.assertEqual(parse_values(text), {"kept": 1.0})

    def test_empty_text(self) -> None:
        self.assertEqual(parse_values(""), {})

    def test_repeated_key_takes_last_value(self) -> None:
        text = "- `x`: 1.0\n- `y`: 7\n- `x`: 2.0\n"
        self.assertEqual(parse_values(text), {"x": 2.0, "y": 7.0})

    def test_malformed_captured_number_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            parse_values("- `bad`: 1.2.3\n")

    def test_record_excerpt(self) -> None:
        self.assertEqual(
            parse_values(RECORD_EXCERPT),
            {"period": 5.951232e-10, "f_osc": 1.680324e9},
        )


class FieldTests(unittest.TestCase):
    TEXT = "header\nvalue: abc\n"

    def test_returns_capture_with_multiline_anchors(self) -> None:
        # ^/$ match at line boundaries: "value:" is not at the start of TEXT.
        result = field(self.TEXT, r"^value:\s*(\w+)$")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "abc")

    def test_capture_is_returned_unvalidated(self) -> None:
        # Numeric validation belongs to callers, not to field().
        result = field(self.TEXT, r"^value:\s*(\S+)$")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "abc")

    def test_numeric_capture_is_still_a_string(self) -> None:
        self.assertEqual(field("n: 12\n", r"^n:\s*(\d+)$"), "12")

    def test_missing_match_raises_runtime_error_by_default(self) -> None:
        pattern = r"^value:\s*(\d+)$"
        with self.assertRaises(RuntimeError) as ctx:
            field(self.TEXT, pattern)
        message = str(ctx.exception)
        self.assertIn(repr(pattern), message)
        self.assertFalse(message.startswith(": "))

    def test_missing_match_message_includes_label(self) -> None:
        pattern = r"^value:\s*(\d+)$"
        with self.assertRaises(RuntimeError) as ctx:
            field(self.TEXT, pattern, label="some-record")
        message = str(ctx.exception)
        self.assertTrue(message.startswith("some-record: "), message)
        self.assertIn(repr(pattern), message)

    def test_missing_match_raises_caller_error_cls(self) -> None:
        pattern = r"^value:\s*(\d+)$"
        with self.assertRaises(CustomRecordErrorSubclass) as ctx:
            field(
                self.TEXT,
                pattern,
                label="some-record",
                error_cls=CustomRecordErrorSubclass,
            )
        self.assertIs(type(ctx.exception), CustomRecordErrorSubclass)
        self.assertNotIsInstance(ctx.exception, RuntimeError)
        message = str(ctx.exception)
        self.assertTrue(message.startswith("some-record: "), message)
        self.assertIn(repr(pattern), message)

    def test_first_match_wins(self) -> None:
        self.assertEqual(field("k: one\nk: two\n", r"^k:\s*(\w+)$"), "one")


class ParseCornerTests(unittest.TestCase):
    def test_record_excerpt(self) -> None:
        self.assertEqual(parse_corner(RECORD_EXCERPT), ("tt", -40.0, 2.97))

    def test_representative_corners(self) -> None:
        cases = [
            (_corner_text("ff", "125", "3.63"), ("ff", 125.0, 3.63)),
            (_corner_text("ss", "27", "3.30"), ("ss", 27.0, 3.30)),
            (_corner_text("ss", "-40", "3.63"), ("ss", -40.0, 3.63)),
            (_corner_text("ff", "85.5", "3.30"), ("ff", 85.5, 3.30)),
        ]
        for text, expected in cases:
            with self.subTest(expected=expected):
                result = parse_corner(text)
                self.assertEqual(result, expected)
                self.assertIsInstance(result[1], float)
                self.assertIsInstance(result[2], float)

    def test_missing_fields_raise_default_error_with_label(self) -> None:
        cases = {
            "process": _corner_text(process=None),
            "temperature": _corner_text(temperature=None),
            "voltage": _corner_text(voltage=None),
        }
        for name, text in cases.items():
            with self.subTest(missing=name):
                with self.assertRaises(RuntimeError) as ctx:
                    parse_corner(text, label="rec-x")
                message = str(ctx.exception)
                self.assertTrue(message.startswith("rec-x: "), message)
                self.assertIn(f"{name}:", message)

    def test_missing_fields_raise_caller_error_cls(self) -> None:
        cases = {
            "process": _corner_text(process=None),
            "temperature": _corner_text(temperature=None),
            "voltage": _corner_text(voltage=None),
        }
        for name, text in cases.items():
            with self.subTest(missing=name):
                with self.assertRaises(CustomRecordError) as ctx:
                    parse_corner(text, label="rec-y", error_cls=CustomRecordError)
                self.assertIs(type(ctx.exception), CustomRecordError)
                message = str(ctx.exception)
                self.assertTrue(message.startswith("rec-y: "), message)
                self.assertIn(f"{name}:", message)

    def test_malformed_numeric_capture_raises_value_error(self) -> None:
        cases = {
            "temperature": _corner_text(temperature="1.2.3"),
            "voltage": _corner_text(voltage="1.2.3"),
        }
        for name, text in cases.items():
            with self.subTest(malformed=name):
                with self.assertRaises(ValueError):
                    parse_corner(text)
                # The custom class covers only a missing match; float()
                # conversion failures still surface as ValueError.
                with self.assertRaises(ValueError) as ctx:
                    parse_corner(text, label="rec-z", error_cls=CustomRecordError)
                self.assertNotIsInstance(ctx.exception, CustomRecordError)


class FormatCornerTests(unittest.TestCase):
    def test_canonical_labels(self) -> None:
        self.assertEqual(format_corner("tt", -40, 2.97), "tt/-40/2.97")
        self.assertEqual(format_corner("ss", 125, 3.3), "ss/125/3.30")

    def test_rounds_temperature_and_supply(self) -> None:
        # Not a lossless inverse of parse_corner: temperature is rounded to
        # zero decimal places and supply to two.
        self.assertEqual(format_corner("ff", 27.4, 3.634), "ff/27/3.63")

    def test_formats_parsed_record_excerpt(self) -> None:
        self.assertEqual(format_corner(*parse_corner(RECORD_EXCERPT)), "tt/-40/2.97")


class RecordExcerptProvenanceTests(unittest.TestCase):
    def test_excerpt_lines_are_in_committed_record(self) -> None:
        record_lines = set(RECORD_PATH.read_text().splitlines())
        for line in RECORD_EXCERPT.splitlines():
            if line:
                with self.subTest(line=line):
                    self.assertIn(line, record_lines)


if __name__ == "__main__":
    unittest.main()
