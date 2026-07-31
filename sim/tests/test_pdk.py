#!/usr/bin/env python3
"""Unit tests for sim/harness/pdk.py -- no hardcoded paths, first-hit-wins
resolution order."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import pdk as pdk_mod  # noqa: E402


def _make_variant(root: Path, name: str = "gf180mcuD") -> Path:
    variant = root / name
    (variant / "libs.tech" / "ngspice").mkdir(parents=True)
    (variant / "libs.tech" / "ngspice" / "sm141064.ngspice").write_text("* fake\n")
    return variant


class ResolutionOrderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_gf180_pdk_path_wins_first(self):
        variant = _make_variant(self.root, "gf180mcuC")
        with mock.patch.dict(
            "os.environ",
            {"GF180_PDK_PATH": str(variant), "PDK_ROOT": "/should/not/be/used"},
            clear=False,
        ):
            with mock.patch.object(pdk_mod, "_load_config", return_value={}):
                found = pdk_mod.find_pdk()
        self.assertEqual(found.path, variant)
        self.assertEqual(found.source, "GF180_PDK_PATH")

    def test_gf180_pdk_path_invalid_raises(self):
        with mock.patch.dict("os.environ", {"GF180_PDK_PATH": str(self.root / "nope")}, clear=False):
            with mock.patch.object(pdk_mod, "_load_config", return_value={}):
                with self.assertRaises(pdk_mod.PdkNotFound):
                    pdk_mod.find_pdk()

    def test_pdk_root_plus_pdk_env_used_when_no_direct_path(self):
        import os

        _make_variant(self.root, "gf180mcuD")
        env = dict(os.environ)
        env.pop("GF180_PDK_PATH", None)
        env["PDK_ROOT"] = str(self.root)
        env["PDK"] = "gf180mcuD"
        with mock.patch.dict("os.environ", env, clear=True):
            with mock.patch.object(pdk_mod, "_load_config", return_value={}):
                found = pdk_mod.find_pdk()
        self.assertEqual(found.source, "PDK_ROOT")
        self.assertEqual(found.variant, "gf180mcuD")

    def test_search_roots_from_committed_config_are_tried(self):
        _make_variant(self.root, "gf180mcuD")
        import os

        env = dict(os.environ)
        env.pop("GF180_PDK_PATH", None)
        env.pop("PDK_ROOT", None)
        with mock.patch.dict("os.environ", env, clear=True):
            with mock.patch.object(
                pdk_mod, "_load_config",
                return_value={"variant": "gf180mcuD", "search_roots": [str(self.root)]},
            ):
                found = pdk_mod.find_pdk()
        self.assertTrue(found.source.startswith("search_root:"))

    def test_not_found_raises_with_a_helpful_message(self):
        import os

        env = dict(os.environ)
        env.pop("GF180_PDK_PATH", None)
        env.pop("PDK_ROOT", None)
        with mock.patch.dict("os.environ", env, clear=True):
            with mock.patch.object(
                pdk_mod, "_load_config", return_value={"variant": "gf180mcuD", "search_roots": []}
            ):
                with mock.patch.object(pdk_mod, "BUILTIN_SEARCH_ROOTS", (str(self.root / "empty"),)):
                    with self.assertRaises(pdk_mod.PdkNotFound) as ctx:
                        pdk_mod.find_pdk()
        self.assertIn("volare", str(ctx.exception))


class PdkPropertiesTests(unittest.TestCase):
    def test_provenance_and_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            variant = _make_variant(root, "gf180mcuD")
            (variant / "libs.tech" / "ngspice" / "design.ngspice").write_text("* fake\n")
            (variant / "SOURCES").write_text("open_pdks abc123\n")
            found = pdk_mod.Pdk(path=variant, variant="gf180mcuD", source="test")
            self.assertEqual(found.version, "abc123")
            self.assertTrue(str(found.model_lib).endswith("sm141064.ngspice"))
            prov = found.provenance()
            self.assertEqual(prov["variant"], "gf180mcuD")
            self.assertEqual(prov["open_pdks_version"], "abc123")


if __name__ == "__main__":
    unittest.main()
