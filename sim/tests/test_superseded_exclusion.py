#!/usr/bin/env python3
"""Current rollups must not select ``status: superseded`` evidence (#425).

Every fixture is written to a temporary directory that the loaders' module
``RECORDS`` path is pointed at; no committed record is read or modified.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SIM_DIR / "tools"))

import _record_parsing as rp  # noqa: E402
import array_sizing as asz  # noqa: E402
import power_rollup as pr  # noqa: E402
import time_to_first_valid as ttfv  # noqa: E402


def record(status: str | None, temp: float = 27, extra: str = "") -> str:
    lines = ["---", "record: fixture"]
    if status is not None:
        lines.append(f"status: {status}")
    lines += ["---", "", f"process: tt", f"temperature: {temp}", "voltage: 3.30",
              "", "- `i_avdd`: 1e-6", extra]
    return "\n".join(lines) + "\n"


class ParseStatusTests(unittest.TestCase):
    def test_valid_and_superseded(self):
        self.assertEqual(rp.parse_status(record("valid")), "valid")
        self.assertEqual(rp.parse_status(record("superseded")), "superseded")

    def test_missing_names_record(self):
        with self.assertRaisesRegex(RuntimeError, "rec-a: .*no `status:`"):
            rp.parse_status(record(None), label="rec-a")

    def test_unknown_names_record(self):
        with self.assertRaisesRegex(RuntimeError, "rec-b: unknown `status: stale`"):
            rp.parse_status(record("stale"), label="rec-b")

    def test_empty_value_is_unknown(self):
        with self.assertRaisesRegex(RuntimeError, "rec-c: unknown"):
            rp.parse_status(record(""), label="rec-c")

    def test_body_status_line_is_ignored(self):
        text = record(None, extra="status: valid")
        with self.assertRaises(RuntimeError):
            rp.parse_status(text, label="rec-d")

    def test_no_frontmatter(self):
        with self.assertRaisesRegex(RuntimeError, "rec-e: no frontmatter"):
            rp.parse_status("process: tt\n", label="rec-e")


class _Fixture(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def write(self, name: str, status: str | None, temp: float = 27) -> None:
        (self.dir / name).write_text(record(status, temp))


class PowerRollupTests(_Fixture):
    GLOBS = ("*-ro-array-core-power-[0-9]*.md", "*-ro-array-core-pvt-q-[0-9]*.md")

    def load(self, **kw):
        with mock.patch.object(pr, "RECORDS", self.dir):
            return pr.load(self.GLOBS, **kw)

    def test_superseded_preferred_family_does_not_displace_replacement(self):
        # Superseded full-grid record sorts LATER and is the preferred family.
        self.write("2026-01-01-ro-array-core-power-01.md", "valid")
        self.write("2026-02-01-ro-array-core-pvt-q-01.md", "superseded")
        chosen = pr.by_corner(self.load(), prefer="pvt-q")
        self.assertEqual([r.stem for r in chosen.values()],
                         ["2026-01-01-ro-array-core-power-01"])

    def test_superseded_only_corner_is_absent(self):
        self.write("2026-01-01-ro-array-core-pvt-q-01.md", "valid", temp=27)
        self.write("2026-01-01-ro-array-core-pvt-q-02.md", "superseded", temp=85)
        chosen = pr.by_corner(self.load(), prefer="pvt-q")
        self.assertEqual(list(chosen), ["tt/27/3.30"])

    def test_all_superseded_gives_empty_missing_evidence_result(self):
        self.write("2026-01-01-ro-array-core-pvt-q-01.md", "superseded")
        self.assertEqual(pr.by_corner(self.load(), prefer="pvt-q"), {})

    def test_older_valid_record_remains_available(self):
        self.write("2026-01-01-ro-array-core-pvt-q-01.md", "valid")
        self.write("2026-02-01-ro-array-core-pvt-q-01.md", "valid")
        self.assertEqual(len(self.load()), 2)

    def test_explicit_historical_read_includes_superseded(self):
        self.write("2026-01-01-ro-array-core-pvt-q-01.md", "superseded")
        self.assertEqual(len(self.load(include_superseded=True)), 1)

    def test_bad_lifecycle_raises_named_record(self):
        self.write("2026-01-01-ro-array-core-pvt-q-01.md", "bogus")
        with self.assertRaisesRegex(RuntimeError, "2026-01-01-ro-array-core-pvt-q-01"):
            self.load()


class StartupTests(_Fixture):
    def load(self, **kw):
        with mock.patch.object(ttfv, "RECORDS", self.dir):
            return ttfv.load_startup_records(**kw)

    def test_superseded_startup_corner_excluded(self):
        glob = ttfv.STARTUP_GLOB
        self.assertTrue(glob.startswith("*"))
        stem = glob.lstrip("*").replace("[0-9]*", "01").replace("*", "")
        self.write(f"2026-01-01{stem}", "valid", temp=27)
        self.write(f"2026-02-01{stem}", "superseded", temp=27)
        self.write(f"2026-03-01{stem}", "superseded", temp=85)
        recs = ttfv.dedupe_by_corner(self.load())
        self.assertEqual([(r.stem[:10], r.corner) for r in recs],
                         [("2026-01-01", "tt/27/3.30")])
        self.assertEqual(len(self.load(include_superseded=True)), 3)


class ArraySizingTests(_Fixture):
    def test_load_excludes_superseded(self):
        self.write("2026-01-01-ro-array-core-power-01.md", "valid")
        self.write("2026-02-01-ro-array-core-power-02.md", "superseded", temp=85)
        with mock.patch.object(asz, "RECORDS", self.dir):
            cur = asz.load("*-ro-array-core-power-[0-9]*.md")
            hist = asz.load("*-ro-array-core-power-[0-9]*.md", include_superseded=True)
        self.assertEqual([r.corner for r in cur], ["tt/27/3.30"])
        self.assertEqual(len(hist), 2)


if __name__ == "__main__":
    unittest.main()
