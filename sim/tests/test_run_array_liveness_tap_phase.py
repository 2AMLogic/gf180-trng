#!/usr/bin/env python3
"""Unit tests for the stale-record cleanup in
``sim/tools/run_array_liveness_tap_phase.py`` (issue #393).

The launcher deletes records and raw directories it judges stale before each
attempt. ``sim/`` results are append-only evidence, so the guarantee under
test is that ``clean_stale`` never removes a complete record, a record at
another corner, or an unparseable one, and that ``deck_status`` classifies
``complete`` / ``incomplete`` / ``missing`` by the documented bar.

``RECORDS_DIR`` / ``RAW_DIR`` are patched to a tempdir and the records are
tiny synthetic frontmatter fixtures; nothing is simulated and no committed
record is read. ``main_loop``, ``run_deck`` and ``check_env`` are not
exercised.

Stdlib only.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SIM_DIR / "tools"))

import run_array_liveness_tap_phase as rl  # noqa: E402

SLUG = "array-liveness-tap-phase-clocked"
OTHER_SLUG = "array-liveness-tap-phase-static"
CORNER_TEXT = {"process": "tt", "temp": "27", "vdd": "3.300"}


def record_text(*, seeds: int = 4, sigma_1: bool = True, temp: str = "27") -> str:
    """Minimal record: corner frontmatter plus the bullets ``Record`` parses."""
    text = (
        "---\n"
        "corner:\n"
        "  process: tt\n"
        "  voltage: 3.300 V (nominal 3.3 V)\n"
        f"  temperature: {temp}\n"
        "---\n\n"
        "## Result\n\n"
    )
    if sigma_1:
        text += f"- `sigma_1`: mean 1.0e-12 over {seeds} seeds (sd 1.0e-13)\n"
    text += f"- `period`: mean 2.8e-09 over {seeds} seeds (sd 1.0e-11)\n"
    return text


class RunArrayLivenessTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.records = Path(tmp.name) / "records"
        self.raw = self.records / "raw"
        self.raw.mkdir(parents=True)
        for name, value in (("RECORDS_DIR", self.records), ("RAW_DIR", self.raw)):
            p = mock.patch.object(rl, name, value)
            p.start()
            self.addCleanup(p.stop)
        log = mock.patch.object(rl, "_log", lambda msg: None)
        log.start()
        self.addCleanup(log.stop)

    def add(self, stem: str, text: str, *, raw: bool = True) -> Path:
        path = self.records / f"{stem}.md"
        path.write_text(text)
        if raw:
            (self.raw / stem).mkdir()
            (self.raw / stem / "run0.spice").write_text("x\n")
        return path

    def stem(self, n: int, slug: str = SLUG, date: str = "2026-08-01") -> str:
        return f"{date}-{slug}-{n:02d}"


class DeckStatusTests(RunArrayLivenessTestCase):
    def test_no_records_is_missing(self) -> None:
        self.assertEqual(rl.deck_status(SLUG), "missing")

    def test_complete(self) -> None:
        self.add(self.stem(1), record_text())
        self.assertEqual(rl.deck_status(SLUG), "complete")

    def test_three_seeds_is_incomplete(self) -> None:
        self.add(self.stem(1), record_text(seeds=3))
        self.assertEqual(rl.deck_status(SLUG), "incomplete")

    def test_no_sigma_1_is_incomplete(self) -> None:
        self.add(self.stem(1), record_text(sigma_1=False))
        self.assertEqual(rl.deck_status(SLUG), "incomplete")

    def test_other_corner_is_ignored(self) -> None:
        self.add(self.stem(1), record_text(temp="85"))
        self.assertEqual(rl.deck_status(SLUG), "missing")

    def test_other_slug_is_ignored(self) -> None:
        self.add(self.stem(1, OTHER_SLUG), record_text())
        self.assertEqual(rl.deck_status(SLUG), "missing")

    def test_newest_by_stem_wins_over_older_complete(self) -> None:
        self.add(self.stem(1), record_text())
        self.add(self.stem(2), record_text(seeds=2))
        self.assertEqual(rl.deck_status(SLUG), "incomplete")

    def test_newest_by_date_wins(self) -> None:
        self.add(self.stem(9, date="2026-08-01"), record_text(seeds=2))
        self.add(self.stem(1, date="2026-08-02"), record_text())
        self.assertEqual(rl.deck_status(SLUG), "complete")


class CleanStaleTests(RunArrayLivenessTestCase):
    def test_removes_incomplete_record_and_raw(self) -> None:
        stem = self.stem(1)
        path = self.add(stem, record_text(seeds=3))
        removed = rl.clean_stale(SLUG)
        self.assertFalse(path.exists())
        self.assertFalse((self.raw / stem).exists())
        self.assertEqual(removed, [str(path), str(self.raw / stem)])

    def test_removes_record_without_sigma_1(self) -> None:
        path = self.add(self.stem(1), record_text(sigma_1=False))
        rl.clean_stale(SLUG)
        self.assertFalse(path.exists())

    def test_removes_incomplete_record_without_raw_dir(self) -> None:
        path = self.add(self.stem(1), record_text(seeds=2), raw=False)
        self.assertEqual(rl.clean_stale(SLUG), [str(path)])

    def test_complete_record_untouched(self) -> None:
        # Exactly len(SEEDS) seeds is the boundary: ">=" must keep it.
        stem = self.stem(1)
        path = self.add(stem, record_text(seeds=len(rl.SEEDS)))
        self.assertEqual(rl.clean_stale(SLUG), [])
        self.assertTrue(path.exists())
        self.assertTrue((self.raw / stem / "run0.spice").exists())

    def test_other_corner_untouched(self) -> None:
        stem = self.stem(1)
        path = self.add(stem, record_text(seeds=1, temp="85"))
        self.assertEqual(rl.clean_stale(SLUG), [])
        self.assertTrue(path.exists())
        self.assertTrue((self.raw / stem).is_dir())

    def test_other_slug_untouched(self) -> None:
        stem = self.stem(1, OTHER_SLUG)
        path = self.add(stem, record_text(seeds=1))
        orphan = self.raw / self.stem(2, OTHER_SLUG)
        orphan.mkdir()
        self.assertEqual(rl.clean_stale(SLUG), [])
        self.assertTrue(path.exists())
        self.assertTrue((self.raw / stem).is_dir())
        self.assertTrue(orphan.is_dir())

    def test_orphan_raw_removed_but_raw_with_record_kept(self) -> None:
        kept = self.stem(1)
        self.add(kept, record_text())
        orphan = self.raw / self.stem(2)
        orphan.mkdir()
        removed = rl.clean_stale(SLUG)
        self.assertEqual(removed, [str(orphan)])
        self.assertFalse(orphan.exists())
        self.assertTrue((self.raw / kept).is_dir())

    def test_orphan_file_not_directory_is_kept(self) -> None:
        f = self.raw / f"{self.stem(1)}.txt"
        f.write_text("x")
        self.assertEqual(rl.clean_stale(SLUG), [])
        self.assertTrue(f.exists())

    def test_unparseable_record_left_alone(self) -> None:
        stem = self.stem(1)
        path = self.add(stem, "not a record\n")
        self.assertEqual(rl.clean_stale(SLUG), [])
        self.assertTrue(path.exists())
        self.assertTrue((self.raw / stem).is_dir())

    def test_no_raw_dir_at_all(self) -> None:
        self.raw.rmdir()
        path = self.add(self.stem(1), record_text(seeds=1), raw=False)
        self.assertEqual(rl.clean_stale(SLUG), [str(path)])

    def test_mixed_returns_exactly_removed_paths(self) -> None:
        complete = self.add(self.stem(1), record_text())
        stale = self.add(self.stem(2), record_text(seeds=3))
        orphan = self.raw / self.stem(3)
        orphan.mkdir()
        removed = rl.clean_stale(SLUG)
        self.assertEqual(
            sorted(removed),
            sorted([str(stale), str(self.raw / self.stem(2)), str(orphan)]),
        )
        self.assertTrue(complete.exists())
        self.assertEqual(rl.deck_status(SLUG), "complete")

    def test_status_is_missing_after_cleaning_incomplete(self) -> None:
        self.add(self.stem(1), record_text(seeds=3))
        rl.clean_stale(SLUG)
        self.assertEqual(rl.deck_status(SLUG), "missing")


if __name__ == "__main__":
    unittest.main()
