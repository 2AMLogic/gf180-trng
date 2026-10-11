#!/usr/bin/env python3
"""Current rollups must not select ``status: superseded`` evidence (#425).

Every fixture is written to a temporary directory that the loaders' module
``RECORDS`` path is pointed at; no committed record is read or modified.
"""

from __future__ import annotations

import re
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
import raw_min_entropy_estimate as rme  # noqa: E402
import starved_cell_jitter_energy as scje  # noqa: E402
import time_to_first_valid as ttfv  # noqa: E402


def record(status: str | None, temp: float = 27, extra: str = "") -> str:
    lines = ["---", "record: fixture"]
    if status is not None:
        lines.append(f"status: {status}")
    lines += ["corner:", "  process: tt", f"  temperature: {temp}", "  voltage: 3.30 V",
              "---", "", "## Result", "", "- `i_avdd`: 1e-6", extra]
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

    def test_duplicate_status_is_rejected(self):
        text = "---\nrecord: x\nstatus: valid\nstatus: superseded\n---\nbody\n"
        with self.assertRaisesRegex(RuntimeError, "rec-g: .*2 `status:` fields"):
            rp.parse_status(text, label="rec-g")

    def test_unclosed_frontmatter(self):
        with self.assertRaisesRegex(RuntimeError, "rec-h: no frontmatter"):
            rp.parse_status("---\nstatus: valid\n", label="rec-h")

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


def frontmatter(status: str | None, temp: float = 27) -> str:
    lines = ["---", "record: fixture"]
    if status is not None:
        lines.append(f"status: {status}")
    lines += ["corner:", "  process: tt", f"  temperature: {temp}", "  voltage: 3.30 V"]
    return "\n".join(lines + ["---", "", "## Result"]) + "\n\n"


def mean_bullet(key: str, mean: float, sd: float = 0.0, seeds: int = 4) -> str:
    return f"- `{key}`: mean {mean!r} over {seeds} seeds (sd {sd!r})\n"


class RawMinEntropyTests(_Fixture):
    """``raw_min_entropy_estimate.load_records`` reads bitstream records by
    its own glob, so it filters lifecycle itself rather than via a loader."""

    def write_bits(self, name: str, status: str | None, bits: list[int],
                   temp: float = 27) -> None:
        text = frontmatter(status, temp) + "seeds: [1, 2]\n\n"
        for i, b in enumerate(bits):
            text += mean_bullet(f"b{i}_v", 3.3 if b else 0.0)
        (self.dir / name).write_text(text)

    def load(self, **kw):
        with mock.patch.object(rme, "RECORDS", self.dir):
            return rme.load_records(**kw)

    def test_superseded_record_does_not_contribute(self):
        self.write_bits("2026-01-01-sampler-array-digitize-01.md", "valid", [1, 0])
        self.write_bits("2026-02-01-sampler-array-digitize-01.md", "superseded", [1, 1])
        recs = self.load()
        self.assertEqual([(r.stem[:10], r.bits) for r in recs], [("2026-01-01", [1, 0])])

    def test_superseded_only_corner_is_missing(self):
        self.write_bits("2026-01-01-sampler-array-digitize-01.md", "valid", [1, 0])
        self.write_bits("2026-01-01-sampler-array-digitize-02.md", "superseded", [1, 0],
                        temp=85)
        self.assertEqual({r.corner for r in self.load()}, {"tt/27/3.30"})

    def test_explicit_historical_read_includes_superseded(self):
        self.write_bits("2026-01-01-sampler-array-digitize-01.md", "superseded", [1, 0])
        self.assertEqual(len(self.load(include_superseded=True)), 1)

    def test_missing_lifecycle_raises_named_record(self):
        self.write_bits("2026-01-01-sampler-array-digitize-01.md", None, [1, 0])
        with self.assertRaisesRegex(rme.RecordError, "2026-01-01-sampler-array-digitize-01"):
            self.load()


class StarvedCellJitterEnergyTests(_Fixture):
    """``starved_cell_jitter_energy.load_points`` keys noise records by corner,
    so a superseded noise record sorting later must not win that corner."""

    def setUp(self):
        super().setUp()
        for name, value in (("RECORDS", self.dir),
                            ("window_geometry", lambda *a, **k: (16, 128))):
            p = mock.patch.object(scje, name, value)
            p.start()
            self.addCleanup(p.stop)

    def write_jitter(self, name: str, status: str | None, temp: float = 27) -> None:
        text = frontmatter(status, temp)
        for lag in (1, 2, 4, 8):
            text += mean_bullet(f"sigma_{lag}", 1e-12 * lag ** 0.5, 5e-14)
        text += "- `period`: 2.8e-09\n- `p_active_w`: 1e-04\n"
        (self.dir / name).write_text(text)

    def write_noise(self, name: str, status: str | None, dens: float,
                    temp: float = 27) -> None:
        (self.dir / name).write_text(
            frontmatter(status, temp) + f"- `inoise_dens_1g`: {dens!r}\n"
        )

    def test_superseded_noise_record_does_not_win_corner(self):
        self.write_jitter("2026-01-01-ro-ring5-starved-jitter-long-01.md", "valid")
        self.write_noise("2026-01-01-rostage-noise-01.md", "valid", 1e-8)
        self.write_noise("2026-02-01-rostage-noise-01.md", "superseded", 9e-8)
        points, _ = scje.load_points()
        self.assertEqual([p.noise.stem for p in points], ["2026-01-01-rostage-noise-01"])
        hist, _ = scje.load_points(include_superseded=True)
        self.assertEqual([p.noise.stem for p in hist], ["2026-02-01-rostage-noise-01"])

    def test_superseded_jitter_record_is_excluded(self):
        self.write_jitter("2026-01-01-ro-ring5-starved-jitter-long-01.md", "valid")
        self.write_jitter("2026-01-01-ro-ring5-starved-jitter-long-02.md", "superseded",
                          temp=85)
        self.write_noise("2026-01-01-rostage-noise-01.md", "valid", 1e-8)
        points, skipped = scje.load_points()
        self.assertEqual([p.rec.corner for p in points], ["tt/27/3.30"])
        self.assertEqual(skipped, [])

    def test_all_superseded_jitter_is_missing_evidence(self):
        self.write_jitter("2026-01-01-ro-ring5-starved-jitter-long-01.md", "superseded")
        self.write_noise("2026-01-01-rostage-noise-01.md", "valid", 1e-8)
        with self.assertRaises(scje.RecordError):
            scje.load_points()

    def test_unknown_lifecycle_raises_named_record(self):
        self.write_jitter("2026-01-01-ro-ring5-starved-jitter-long-01.md", "valid")
        self.write_noise("2026-01-01-rostage-noise-01.md", "stale", 1e-8)
        with self.assertRaisesRegex(scje.RecordError, "2026-01-01-rostage-noise-01"):
            scje.load_points()


#: Tools that read a records directory directly, with the reason each is
#: allowed to see every record (``status: superseded`` included) and how many
#: such globs it holds. Anything not listed must go through
#: ``_record_parsing.current_records`` / ``latest_current_record``, which
#: apply the lifecycle filter and the latest-record-wins rule in one place
#: (#554). Adding a line here is the explicit statement "reads historical
#: records on purpose".
DIRECT_GLOB_ALLOWLIST = {
    "tools/_record_parsing.py": (1, "the shared selection helper itself"),
    "tools/verify_record_checksums.py": (1, "checksums every record, superseded included"),
    "tools/corpus_counts.py": (1, "counts the whole corpus by lifecycle status"),
    "harness/report.py": (1, "stem allocation must see every existing stem"),
    "tools/run_array_liveness_tap_phase.py": (
        2, "resume/clean-up logic inspects every attempt's record, not the latest valid one"),
    "tools/power_rollup.py": (
        1, "multi-record rollup: filters by lifecycle but keeps every valid record, "
           "not only the latest"),
}

_DIRECT_GLOB = re.compile(r"\b(?:RECORDS|RECORDS_DIR|records_dir)\s*\.\s*r?glob\s*\(")


def direct_record_globs() -> dict[str, int]:
    found = {}
    for sub in ("tools", "harness"):
        for path in sorted((SIM_DIR / sub).glob("*.py")):
            n = len(_DIRECT_GLOB.findall(path.read_text()))
            if n:
                found[f"{sub}/{path.name}"] = n
    return found


class DirectGlobGuardTests(unittest.TestCase):
    def test_no_unlisted_direct_records_glob(self):
        found = direct_record_globs()
        allowed = {name: n for name, (n, _why) in DIRECT_GLOB_ALLOWLIST.items()}
        unlisted = {k: v for k, v in found.items() if k not in allowed}
        self.assertEqual(
            unlisted, {},
            "direct records-directory glob outside the allowlist; use "
            "_record_parsing.current_records / latest_current_record",
        )
        grown = {k: v for k, v in found.items() if v > allowed.get(k, v)}
        self.assertEqual(grown, {}, "more direct globs than the allowlist records")

    def test_allowlist_has_no_stale_entries(self):
        found = direct_record_globs()
        stale = [k for k in DIRECT_GLOB_ALLOWLIST if found.get(k) != DIRECT_GLOB_ALLOWLIST[k][0]]
        self.assertEqual(stale, [], "allowlist entry no longer matches the source")

    def test_guard_detects_a_bare_glob(self):
        self.assertTrue(_DIRECT_GLOB.search('x = sorted(RECORDS.glob("*.md"))'))
        self.assertTrue(_DIRECT_GLOB.search("records_dir.glob(pat)"))
        self.assertFalse(_DIRECT_GLOB.search("current_records(RECORDS, pat)"))


class SelectionHelperTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def put(self, name, status, temp=27, extra=""):
        (self.dir / name).write_text(record(status, temp, extra))

    def test_filters_and_orders(self):
        self.put("2026-01-02-fx-01.md", "valid")
        self.put("2026-01-01-fx-01.md", "valid")
        self.put("2026-01-03-fx-01.md", "superseded")
        got = rp.current_records(self.dir, "*-fx-*.md")
        self.assertEqual([p.stem for p in got], ["2026-01-01-fx-01", "2026-01-02-fx-01"])
        every = rp.current_records(self.dir, "*-fx-*.md", include_superseded=True)
        self.assertEqual(len(every), 3)

    def test_latest_skips_superseded_and_filters(self):
        self.put("2026-01-01-fx-01.md", "valid", temp=27)
        self.put("2026-01-02-fx-01.md", "valid", temp=85)
        self.put("2026-01-03-fx-01.md", "superseded", temp=27)
        got = rp.latest_current_record(self.dir, "*-fx-*.md", corner="tt/27/3.30")
        self.assertEqual(got.stem, "2026-01-01-fx-01")
        got = rp.latest_current_record(self.dir, "*-fx-*.md", requires=("i_avdd",))
        self.assertEqual(got.stem, "2026-01-02-fx-01")

    def test_three_distinct_errors(self):
        with self.assertRaisesRegex(RuntimeError, "no committed record matches"):
            rp.latest_current_record(self.dir, "*-none-*.md")
        self.put("2026-01-01-fx-01.md", "superseded")
        with self.assertRaisesRegex(RuntimeError, "every match is superseded"):
            rp.latest_current_record(self.dir, "*-fx-*.md")
        self.put("2026-01-02-fx-01.md", "valid")
        with self.assertRaisesRegex(RuntimeError, "no valid .* at tt/85/3.30 carries i_avdd"):
            rp.latest_current_record(
                self.dir, "*-fx-*.md", corner="tt/85/3.30", requires=("i_avdd",))
        self.assertIsNone(rp.latest_current_record(
            self.dir, "*-fx-*.md", corner="tt/85/3.30", required=False))

    def test_unreadable_status_names_record(self):
        self.put("2026-01-01-fx-01.md", None)
        with self.assertRaisesRegex(RuntimeError, "2026-01-01-fx-01"):
            rp.current_records(self.dir, "*-fx-*.md")


if __name__ == "__main__":
    unittest.main()
