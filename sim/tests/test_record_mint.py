#!/usr/bin/env python3
"""Offline tests for the shared record-minting scaffold (issue #726).

``sim/harness/record_mint.py`` is the one copy of what ``cmd_record`` in
``power_switch.py`` and ``liveness_sampler_power.py`` used to duplicate. The
renderers are stubs here; the tests pin which files land where and that the
raw artifacts are host-path sanitised before they are hashed.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import record_mint  # noqa: E402

REPO = Path("/fake/repo/root")


def _analyse(rep: dict) -> list[dict]:
    return [{"verdict": c["verdict"], "corner": c["name"]} for c in rep["corners"]]


def _measured(stem, row, corner, rep, files, now, git):
    return f"measured {stem} {row['corner']} {[n for n, _ in files]}\n"


def _unmeasured(stem, bad, rep, files, now, git, note):
    return f"unmeasured {stem} {len(bad)} {note} {[n for n, _ in files]}\n"


class MintRecordsTest(unittest.TestCase):
    def test_sanitize_strips_repo_and_home(self) -> None:
        text = f"{REPO}/a {Path.home()}/b"
        self.assertEqual(record_mint.sanitize(text, REPO), "<repo>/a ~/b")

    def test_mints_one_measured_and_one_unmeasured_record(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            deck = tmp / "deck.cir"
            deck.write_text(f"* {REPO}/design/x.spice\n")
            rep = {"environment": {}, "provenance": {}, "corners": [
                {"name": "tt", "verdict": "OK", "artifacts": {"deck": str(deck)}},
                {"name": "ss", "verdict": "BAD", "measurements": {"x": 1}},
            ]}
            rpath = tmp / "report.json"
            rpath.write_text(json.dumps(rep))
            recs = tmp / "records"
            with contextlib.redirect_stdout(io.StringIO()):
                rc = record_mint.mint_records(
                    [str(rpath)], "why", recs, repo_root=REPO, slug="s", slug_attempt="s-attempt",
                    analyse_report=_analyse, render_measured=_measured, render_unmeasured=_unmeasured)
            self.assertEqual(rc, 0)
            mds = sorted(p.name for p in recs.glob("*.md"))
            self.assertEqual(len(mds), 2)
            self.assertTrue(any("-s-attempt-" in m for m in mds))
            good = next(m for m in mds if "-s-attempt-" not in m)
            raw = recs / "raw" / good[:-3]
            self.assertEqual(sorted(p.name for p in raw.iterdir()), ["corner.cir", "report-unit.json"])
            self.assertEqual((raw / "corner.cir").read_text(), "* <repo>/design/x.spice\n")
            bad_raw = next(p for p in (recs / "raw").iterdir() if "attempt" in p.name)
            errored = json.loads((bad_raw / "report-errored.json").read_text())
            self.assertEqual([c["name"] for c in errored["corners"]], ["ss"])
            self.assertNotIn("measurements", errored["corners"][0])


if __name__ == "__main__":
    unittest.main()
