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
- ``parse_corner`` and ``parse_status`` read only the leading frontmatter
  block, require exactly one of each field, parse temperature and supply as
  complete finite scalars, and raise the caller's ``error_cls`` naming the
  record and field for every failure (issue #443).
- ``format_corner`` rounds temperature to zero decimal places and supply to
  two, so it is not a lossless inverse of ``parse_corner``.

Everything here is stdlib-only: no ngspice and no PDK.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent

sys.path.insert(0, str(SIM_DIR / "tools"))

from _record_parsing import (  # noqa: E402
    field,
    format_corner,
    frontmatter,
    iter_result_seed_summaries,
    iter_seed_summaries,
    parse_corner,
    parse_result_values,
    parse_values,
    result_section,
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


def _wrap(fragment: str) -> str:
    """A fragment placed inside a complete leading frontmatter block."""
    return "---\nrecord: fixture\nstatus: valid\n" + fragment + "---\n\nbody\n"


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
    return "---\nrecord: fixture\nstatus: valid\n" + "\n".join(lines) + "\n---\n\nbody\n"


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

    def test_uppercase_exponent(self) -> None:
        self.assertEqual(parse_values("- `t`: 2.5E-6\n"), {"t": 2.5e-6})

    def test_exponent_with_unit_suffix(self) -> None:
        self.assertEqual(parse_values("- `t`: 2.5e-9s\n"), {"t": 2.5e-9})

    def test_incomplete_exponent_is_rejected(self) -> None:
        for token in ("1e+", "1e-", "1e", "2.5E"):
            with self.subTest(token=token):
                with self.assertRaises(ValueError):
                    parse_values(f"- `t`: {token}\n")

    def test_exponent_continuation_is_rejected(self) -> None:
        for token in ("1e2.3", "1e2e3", "1e2.", "1.5e3.5"):
            with self.subTest(token=token):
                with self.assertRaises(ValueError):
                    parse_values(f"- `t`: {token}\n")

    def test_exponent_continuation_error_names_label_and_key(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            parse_values("- `bad_key`: 1e2e3\n", label="rec-stem", error_cls=RuntimeError)
        self.assertIn("rec-stem", str(ctx.exception))
        self.assertIn("bad_key", str(ctx.exception))
        self.assertIn("1e2e3", str(ctx.exception))

    def test_bare_decimal_forms_are_accepted(self) -> None:
        cases = {".5": 0.5, "-.5": -0.5, "1.": 1.0, "+.5e1": 5.0}
        for token, expected in cases.items():
            with self.subTest(token=token):
                self.assertEqual(parse_values(f"- `t`: {token}\n"), {"t": expected})
                self.assertEqual(parse_values(f"- `t`: {token}ns\n"), {"t": expected})

    def test_lone_dot_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_values("- `t`: .\n")

    def test_overflow_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_values("- `t`: 1e999\n")

    def test_error_names_label_and_key(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            parse_values("- `bad_key`: 1e+\n", label="rec-stem", error_cls=RuntimeError)
        self.assertIn("rec-stem", str(ctx.exception))
        self.assertIn("bad_key", str(ctx.exception))

    def test_committed_corpus_parses(self) -> None:
        records = Path(__file__).resolve().parents[1] / "records"
        for path in sorted(records.glob("*.md")):
            with self.subTest(record=path.name):
                parse_values(path.read_text(), label=path.stem)

    def test_record_excerpt(self) -> None:
        self.assertEqual(
            parse_values(RECORD_EXCERPT),
            {"period": 5.951232e-10, "f_osc": 1.680324e9},
        )


class SeedSummaryTests(unittest.TestCase):
    TEXT = (
        "- `dtrip_v`: mean 1.6e-3 over 8 seeds (sd 2.5e-5, min 1, max 2)\n"
        "- `plain`: 4.5\n"
        "- `other`: mean -0.25 over 4 seeds (sd 0.5\n"
    )

    def test_extracts_key_mean_seed_count_and_sd_in_order(self) -> None:
        got = list(iter_seed_summaries(self.TEXT))
        self.assertEqual([k for k, _ in got], ["dtrip_v", "other"])
        self.assertEqual(tuple(got[0][1]), (1.6e-3, 8, 2.5e-5))
        self.assertEqual(tuple(got[1][1]), (-0.25, 4, 0.5))

    def test_plain_bullet_is_not_a_summary_but_still_a_value(self) -> None:
        self.assertNotIn("plain", [k for k, _ in iter_seed_summaries(self.TEXT)])
        self.assertEqual(parse_values(self.TEXT)["plain"], 4.5)
        self.assertEqual(parse_values(self.TEXT)["dtrip_v"], 1.6e-3)

    def test_requires_sd_clause(self) -> None:
        self.assertEqual(list(iter_seed_summaries("- `k`: mean 1.0 over 3 seeds\n")), [])

    def test_uppercase_exponent_and_zero_sd_accepted(self) -> None:
        got = list(iter_seed_summaries("- `k`: mean 1.5E-3 over 2 seeds (sd 2E-4\n- `z`: mean 1 over 1 seeds (sd 0\n"))
        self.assertEqual([tuple(s) for _, s in got], [(1.5e-3, 2, 2e-4), (1.0, 1, 0.0)])

    def test_boundary_values_raise_with_label_and_key(self) -> None:
        bad = {
            "overflow mean": "- `k`: mean 1e999 over 3 seeds (sd 1\n",
            "malformed sd": "- `k`: mean 1 over 3 seeds (sd 1.2.3\n",
            "malformed mean": "- `k`: mean 1.2.3 over 3 seeds (sd 1\n",
            "zero count": "- `k`: mean 1 over 0 seeds (sd 1\n",
            "malformed count": "- `k`: mean 1 over x seeds (sd 1\n",
            "negative sd": "- `k`: mean 1 over 3 seeds (sd -0.1\n",
            "overflow sd": "- `k`: mean 1 over 3 seeds (sd 1e999\n",
        }
        for name, line in bad.items():
            with self.subTest(name):
                with self.assertRaises(KeyError) as cm:
                    list(iter_seed_summaries(line, label="rec-01", error_cls=KeyError))
                self.assertIn("rec-01", str(cm.exception))
                self.assertIn("`k`", str(cm.exception))

    def test_default_error_is_value_error(self) -> None:
        with self.assertRaises(ValueError):
            list(iter_seed_summaries("- `k`: mean 1 over 0 seeds (sd 1\n"))

    def test_malformed_bullet_among_valid_ones_raises(self) -> None:
        text = (
            "- `a`: mean 1 over 3 seeds (sd 1\n"
            "- `b`: mean 1 over 3 seeds (sd 1.2.3\n"
            "- `c`: mean 1 over 3 seeds (sd 1\n"
        )
        with self.assertRaises(ValueError):
            list(iter_seed_summaries(text))

    def test_consumer_wraps_error_in_its_record_error(self) -> None:
        import starved_cell_jitter_energy as sc

        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "2026-01-01-fixture-01.md"
            path.write_text("## Result\n\n- `dtrip_v`: mean 1 over 3 seeds (sd -0.5\n")
            with self.assertRaises(sc.RecordError) as cm:
                sc.Record(path)
        self.assertIn("2026-01-01-fixture-01", str(cm.exception))
        self.assertIn("`dtrip_v`", str(cm.exception))


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
        self.assertEqual(
            parse_corner(_wrap(RECORD_EXCERPT)), ("tt", -40.0, 2.97)
        )

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

    def test_malformed_numeric_metadata_raises_error_cls(self) -> None:
        bad = ["1.2.3", "125junk", "nan", "inf", "-inf", "1e999", "abc", "",
               "12 5", "n/a (behavioral-level record)"]
        for name in ("temperature", "voltage"):
            for value in bad:
                with self.subTest(field=name, value=value):
                    text = _corner_text(**{name: value})
                    with self.assertRaises(CustomRecordError) as ctx:
                        parse_corner(text, label="rec-z", error_cls=CustomRecordError)
                    self.assertIs(type(ctx.exception), CustomRecordError)
                    message = str(ctx.exception)
                    self.assertTrue(message.startswith("rec-z: "), message)
                    self.assertIn(f"{name}:", message)

    def test_committed_scalar_shapes_parse(self) -> None:
        text = _wrap(
            "corner:\n  process: ss (from the liberty deck)\n"
            "  voltage: 3.00 V (nominal 3.3 V, -10%; binding supply)\n"
            "  temperature: 125\n"
        )
        self.assertEqual(parse_corner(text), ("ss", 125.0, 3.0))

    def test_body_only_corner_is_rejected(self) -> None:
        text = (
            "---\nrecord: fixture\nstatus: valid\n---\n\n"
            "process: ff\ntemperature: 125\nvoltage: 3.63\n"
        )
        with self.assertRaises(CustomRecordError) as ctx:
            parse_corner(text, label="rec-b", error_cls=CustomRecordError)
        self.assertIn("rec-b: ", str(ctx.exception))
        self.assertIn("process:", str(ctx.exception))

    def test_body_does_not_supply_missing_frontmatter_field(self) -> None:
        text = _corner_text(voltage=None).replace("body", "voltage: 3.30")
        with self.assertRaises(CustomRecordError):
            parse_corner(text, error_cls=CustomRecordError)

    def test_duplicate_fields_raise(self) -> None:
        for name in ("process", "temperature", "voltage"):
            with self.subTest(field=name):
                text = _wrap(
                    "corner:\n  process: tt\n  voltage: 3.30 V\n"
                    "  temperature: 27\n" + f"other:\n  {name}: 1\n"
                )
                with self.assertRaises(CustomRecordError) as ctx:
                    parse_corner(text, label="rec-d", error_cls=CustomRecordError)
                self.assertIn(f"`{name}:`", str(ctx.exception))
                self.assertIn("rec-d: ", str(ctx.exception))

    def test_missing_closing_or_leading_frontmatter_raises(self) -> None:
        cases = {
            "unclosed": "---\nprocess: tt\ntemperature: 27\nvoltage: 3.3\n",
            "not leading": "\n" + _corner_text(),
            "absent": "process: tt\ntemperature: 27\nvoltage: 3.3\n",
        }
        for name, text in cases.items():
            with self.subTest(case=name):
                with self.assertRaises(CustomRecordError) as ctx:
                    parse_corner(text, label="rec-f", error_cls=CustomRecordError)
                self.assertTrue(str(ctx.exception).startswith("rec-f: "))


class FrontmatterTests(unittest.TestCase):
    def test_returns_block_body_only(self) -> None:
        self.assertEqual(frontmatter("---\na: 1\n---\nb: 2\n"), "a: 1\n")

    def test_error_cls_and_label(self) -> None:
        with self.assertRaises(CustomRecordError) as ctx:
            frontmatter("a: 1\n", label="rec-q", error_cls=CustomRecordError)
        self.assertTrue(str(ctx.exception).startswith("rec-q: "))


class FormatCornerTests(unittest.TestCase):
    def test_canonical_labels(self) -> None:
        self.assertEqual(format_corner("tt", -40, 2.97), "tt/-40/2.97")
        self.assertEqual(format_corner("ss", 125, 3.3), "ss/125/3.30")

    def test_rounds_temperature_and_supply(self) -> None:
        # Not a lossless inverse of parse_corner: temperature is rounded to
        # zero decimal places and supply to two.
        self.assertEqual(format_corner("ff", 27.4, 3.634), "ff/27/3.63")

    def test_formats_parsed_record_excerpt(self) -> None:
        self.assertEqual(format_corner(*parse_corner(_wrap(RECORD_EXCERPT))), "tt/-40/2.97")


class RecordExcerptProvenanceTests(unittest.TestCase):
    def test_excerpt_lines_are_in_committed_record(self) -> None:
        record_lines = set(RECORD_PATH.read_text().splitlines())
        for line in RECORD_EXCERPT.splitlines():
            if line:
                with self.subTest(line=line):
                    self.assertIn(line, record_lines)


def _record(result: str, *, caveats: str = "", reproduce: str = "", front: str = "") -> str:
    """A record laid out like ``sim/harness/report.py`` emits one."""
    return (
        f"---\nrecord: fixture\nstatus: valid\n{front}---\n\n"
        f"## Result\n\n{result}\n"
        f"## How to reproduce\n\n```sh\n{reproduce}```\n\n"
        f"## Caveats\n\n{caveats}"
    )


class ResultSectionTests(unittest.TestCase):
    """The whole-record boundary (issue #548)."""

    def test_caveats_and_reproduce_examples_do_not_replace_result(self) -> None:
        text = _record(
            "- `p_total_w`: 1e-6\n",
            reproduce="- `p_total_w`: 98\n",
            caveats="- Example only:\n- `p_total_w`: 99\n",
        )
        self.assertEqual(parse_result_values(text, label="r"), {"p_total_w": 1e-6})
        # The snippet primitive keeps its last-value contract on the same text.
        self.assertEqual(parse_values(text), {"p_total_w": 99.0})

    def test_fenced_example_inside_result_is_ignored(self) -> None:
        text = _record(
            "- `x`: 1.5\n\n```\n- `x`: 99\n## Result\n```\n\n~~~\n- `y`: 7\n~~~\n"
        )
        self.assertEqual(parse_result_values(text, label="r"), {"x": 1.5})

    def test_longer_fence_is_not_closed_by_a_shorter_one(self) -> None:
        text = _record("- `x`: 1\n\n````\n```\n- `x`: 2\n````\n")
        self.assertEqual(parse_result_values(text, label="r"), {"x": 1.0})

    def test_subheadings_stay_inside_result(self) -> None:
        text = _record("- `a`: 1\n\n### tt / 27 C\n\n- `b`: 2\n")
        self.assertEqual(parse_result_values(text, label="r"), {"a": 1.0, "b": 2.0})

    def test_other_level_two_section_is_excluded(self) -> None:
        text = _record("- `a`: 1\n\n## Pre/post comparison\n\n- `b`: 2\n")
        self.assertEqual(parse_result_values(text, label="r"), {"a": 1.0})

    def test_frontmatter_is_not_scanned(self) -> None:
        text = _record("- `a`: 1\n", front="note: |\n  ## Result\n")
        self.assertEqual(parse_result_values(text, label="r"), {"a": 1.0})

    def test_duplicate_key_in_result_raises_with_context(self) -> None:
        text = _record("- `x`: 1\n- `y`: 2\n- `x`: 3\n")
        with self.assertRaisesRegex(ValueError, r"rec-a: duplicate measurement `x`"):
            parse_result_values(text, label="rec-a")

    def test_duplicate_key_uses_callers_error_class(self) -> None:
        class MyError(RuntimeError):
            pass

        with self.assertRaises(MyError):
            parse_result_values(_record("- `x`: 1\n- `x`: 2\n"), label="r", error_cls=MyError)
        with self.assertRaises(MyError):
            iter_result_seed_summaries(
                _record("- `x`: mean 1 over 3 seeds (sd 0.1)\n- `x`: 2\n"),
                label="r",
                error_cls=MyError,
            )

    def test_missing_result_section_raises_without_fallback(self) -> None:
        text = "---\nstatus: valid\n---\n\n- `x`: 1\n\n## Caveats\n\n- `x`: 2\n"
        with self.assertRaisesRegex(ValueError, "rec-b: no `## Result` section"):
            parse_result_values(text, label="rec-b")
        with self.assertRaisesRegex(ValueError, "rec-b: no `## Result` section"):
            iter_result_seed_summaries(text, label="rec-b")

    def test_result_heading_only_inside_fence_is_missing(self) -> None:
        text = "---\nstatus: valid\n---\n\n```\n## Result\n- `x`: 1\n```\n"
        with self.assertRaisesRegex(ValueError, "no `## Result` section"):
            result_section(text, label="r")

    def test_ambiguous_result_sections_raise_with_lines(self) -> None:
        text = _record("- `x`: 1\n") + "\n## Result\n\n- `x`: 2\n"
        with self.assertRaisesRegex(ValueError, r"rec-c: ambiguous record: 2 `## Result`"):
            parse_result_values(text, label="rec-c")

    def test_unterminated_fence_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "unterminated fenced"):
            result_section("## Result\n\n```\n- `x`: 1\n", label="r")

    def test_failed_run_diagnostics_are_not_primary_measurements(self) -> None:
        result = (
            "- `x`: 1.0\n\nRuns: 1 of 2 successful.\n\n"
            "Run failures (nonzero exit):\n- seed 2: failed -- boom\n\n"
            "Failed-run diagnostics (values parsed from runs that did not "
            "succeed; NOT included in the summaries above, not evidence "
            "about the device):\n"
            "- seed 2 (failed: boom):\n  - `x`: 55\n  - `z`: 66\n"
            "- `q`: 77\n\n- `w`: 4\n"
        )
        text = _record(result)
        self.assertEqual(parse_result_values(text, label="r"), {"x": 1.0, "w": 4.0})
        self.assertNotIn("55", result_section(text, label="r"))

    def test_seed_summaries_come_from_result_only(self) -> None:
        text = _record(
            "- `s`: mean 2e-12 over 4 seeds (sd 1e-13)\n",
            caveats="- `s`: mean 9 over 2 seeds (sd 1)\n",
        )
        self.assertEqual(
            iter_result_seed_summaries(text, label="r"),
            [("s", next(iter_seed_summaries("- `s`: mean 2e-12 over 4 seeds (sd 1e-13)"))[1])],
        )

    def test_malformed_number_still_names_record_and_key(self) -> None:
        with self.assertRaisesRegex(ValueError, r"rec-d: malformed number `1e\+` in `x`"):
            parse_result_values(_record("- `x`: 1e+\n"), label="rec-d")

    def test_malformed_seed_summary_names_record_and_key(self) -> None:
        """The wrapper forwards ``label``/``error_cls`` to the #547 validator."""

        class MyError(RuntimeError):
            pass

        text = _record("- `s`: mean 1 over 0 seeds (sd 0.1)\n")
        with self.assertRaisesRegex(MyError, r"rec-e: .*`s`"):
            iter_result_seed_summaries(text, label="rec-e", error_cls=MyError)

    def test_committed_records_have_one_parsable_result_section(self) -> None:
        """Durable structural check, valid for records added in future too.

        Every committed record has exactly one ``## Result`` section, and
        its measurement and seed-summary bullets parse without a duplicate
        key or malformed number. This deliberately does not compare against
        the whole-file :func:`parse_values`, so a future record that quotes
        a ``- `key`: N`` example in its Caveats or reproduce section (the
        case issue #548 exists to support) still passes.
        """
        for path in sorted((SIM_DIR / "records").glob("*.md")):
            with self.subTest(record=path.stem):
                text = path.read_text()
                result_section(text, label=path.stem)
                parse_result_values(text, label=path.stem)
                iter_result_seed_summaries(text, label=path.stem)

    def test_frozen_audit_result_reader_matches_whole_file_reader(self) -> None:
        """One-time corpus audit for the records that existed at #548.

        For each of these records the Result-scoped readers return exactly
        what the old whole-file readers did, i.e. moving consumers to the
        Result section changed no recorded value. The audit set is frozen
        (records dated on or before ``AUDIT_CUTOFF``, pinned by count) so a
        later record with value-shaped examples outside its Result section
        is not held to whole-file equivalence.
        """
        audit_cutoff = "2026-10-10"
        audited_count = 1030
        audited = [
            path
            for path in sorted((SIM_DIR / "records").glob("*.md"))
            if path.stem[:10] <= audit_cutoff
        ]
        self.assertEqual(
            len(audited),
            audited_count,
            "the frozen #548 audit set changed; sim/records/ is append-only "
            f"and new records should be dated after {audit_cutoff}",
        )
        for path in audited:
            with self.subTest(record=path.stem):
                text = path.read_text()
                self.assertEqual(
                    parse_result_values(text, label=path.stem),
                    parse_values(text),
                    "a legitimate measurement was excluded or a prose bullet was kept",
                )
                self.assertEqual(
                    iter_result_seed_summaries(text, label=path.stem),
                    list(iter_seed_summaries(text, label=path.stem)),
                )


if __name__ == "__main__":
    unittest.main()
