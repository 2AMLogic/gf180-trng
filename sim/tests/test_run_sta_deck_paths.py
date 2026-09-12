#!/usr/bin/env python3
"""Unit tests for ``run_sta.deck_paths()``' OpenRCX rule-deck resolution.

open_pdks stages the OpenRCX interconnect decks under a directory that has
been renamed once already: ``libs.tech/openlane/`` when
``sim/tb/digital-sta-power/run_sta.py`` was first written, and
``libs.tech/librelane/`` in the open_pdks revision ``sim/harness/pdk.py``'s
install hint pins today (OpenLane 2 became LibreLane upstream). A sweep that
resolved only one spelling reports "OpenRCX rule deck not found" against a
perfectly good PDK install, and the natural workaround — assembling a
hand-shimmed PDK copy under ``layout/.work/`` — leaves machine-local paths
baked into every record's ``pdk.models`` provenance block, pointing at a
directory that no longer exists once the worktree is cleaned up. This is
cheap to get right and expensive to discover, so it is tested.

Stdlib only: synthetic directory trees, no PDK and no ``openroad`` needed.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

TB_DIR = Path(__file__).resolve().parents[1] / "tb" / "digital-sta-power"
SIM_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(TB_DIR))

import run_sta  # noqa: E402


@dataclass
class FakePdk:
    """Just the two attributes ``deck_paths``/``rcx_rules_path`` read."""

    path: Path
    variant: str = "gf180mcuD"


def _install(*rcx_dirs: str) -> FakePdk:
    root = Path(tempfile.mkdtemp())
    for name in rcx_dirs:
        (root / "libs.tech" / name).mkdir(parents=True)
        for rc in run_sta.RC_CORNERS:
            (root / "libs.tech" / name / f"rules.openrcx.gf180mcuD.{rc}").write_text("")
    return FakePdk(path=root)


class RcxDeckResolutionTests(unittest.TestCase):
    def test_resolves_the_librelane_spelling(self):
        pdk = _install("librelane")
        self.assertEqual(run_sta.deck_paths(pdk)["rcx_dir"].name, "librelane")
        self.assertTrue(run_sta.rcx_rules_path(pdk, "max").is_file())

    def test_resolves_the_legacy_openlane_spelling(self):
        # The committed 2026-09-12 record family was produced against this
        # one; a checkout that stopped resolving it could not reproduce them.
        pdk = _install("openlane")
        self.assertEqual(run_sta.deck_paths(pdk)["rcx_dir"].name, "openlane")
        self.assertTrue(run_sta.rcx_rules_path(pdk, "min").is_file())

    def test_prefers_the_current_spelling_when_both_exist(self):
        pdk = _install("openlane", "librelane")
        self.assertEqual(run_sta.deck_paths(pdk)["rcx_dir"].name,
                         run_sta.RCX_DIRS[0])

    def test_an_install_with_neither_names_one_concrete_missing_path(self):
        # `check_environment` prints this path at the user. A list of
        # candidates, or a path under a directory that does not exist under
        # any spelling, would be less actionable than one wrong-but-concrete
        # answer -- and the failure must still be a failure, not a silent
        # fallback to no extraction at all.
        pdk = _install()
        (pdk.path / "libs.tech").mkdir(parents=True, exist_ok=True)
        self.assertEqual(run_sta.deck_paths(pdk)["rcx_dir"].name,
                         run_sta.RCX_DIRS[0])
        self.assertFalse(run_sta.rcx_rules_path(pdk, "nom").is_file())

    def test_every_interconnect_corner_resolves_under_one_directory(self):
        pdk = _install("librelane")
        resolved = {run_sta.rcx_rules_path(pdk, rc).parent
                    for rc in run_sta.RC_CORNERS}
        self.assertEqual(len(resolved), 1)


if __name__ == "__main__":
    unittest.main()
