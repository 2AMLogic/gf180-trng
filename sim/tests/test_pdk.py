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

    def test_ciel_wins_over_volare_when_both_present(self):
        # Regression test for #37: ~/.ciel must be tried before ~/.volare so a
        # stale volare-installed PDK doesn't shadow a current ciel install.
        ciel_root = self.root / "ciel_store"
        volare_root = self.root / "volare_store"
        _make_variant(ciel_root, "gf180mcuD")
        _make_variant(volare_root, "gf180mcuD")
        import os

        env = dict(os.environ)
        env.pop("GF180_PDK_PATH", None)
        env.pop("PDK_ROOT", None)
        with mock.patch.dict("os.environ", env, clear=True):
            with mock.patch.object(
                pdk_mod, "_load_config", return_value={"variant": "gf180mcuD", "search_roots": []}
            ):
                with mock.patch.object(
                    pdk_mod, "BUILTIN_SEARCH_ROOTS", (str(ciel_root), str(volare_root))
                ):
                    found = pdk_mod.find_pdk()
        self.assertEqual(found.path, ciel_root / "gf180mcuD")
        self.assertEqual(found.source, f"search_root:{ciel_root}")

    def test_volare_only_still_found_when_no_ciel(self):
        # No-regression edge case: a volare-only install (no ~/.ciel) must
        # still resolve -- the escape hatch for existing volare users.
        volare_root = self.root / "volare_store"
        _make_variant(volare_root, "gf180mcuD")
        import os

        env = dict(os.environ)
        env.pop("GF180_PDK_PATH", None)
        env.pop("PDK_ROOT", None)
        with mock.patch.dict("os.environ", env, clear=True):
            with mock.patch.object(
                pdk_mod, "_load_config", return_value={"variant": "gf180mcuD", "search_roots": []}
            ):
                with mock.patch.object(
                    pdk_mod,
                    "BUILTIN_SEARCH_ROOTS",
                    (str(self.root / "ciel_store_absent"), str(volare_root)),
                ):
                    found = pdk_mod.find_pdk()
        self.assertEqual(found.path, volare_root / "gf180mcuD")
        self.assertEqual(found.source, f"search_root:{volare_root}")

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
        message = str(ctx.exception)
        # The hint must lead with ciel (maintained) and still name volare as a
        # recognized alternative for anyone with an existing volare install.
        self.assertIn("ciel enable --pdk-family gf180mcu", message)
        self.assertIn("volare", message)


class FindAllVariantDirsTests(unittest.TestCase):
    """Tests for the all-roots-walk helper (#39) used only by --check-env
    to surface a PDK variant shadowed under a losing search root."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_no_hits_returns_empty_list(self):
        with mock.patch.object(
            pdk_mod, "_load_config", return_value={"variant": "gf180mcuD", "search_roots": []}
        ):
            with mock.patch.object(pdk_mod, "BUILTIN_SEARCH_ROOTS", (str(self.root / "empty"),)):
                found = pdk_mod.find_all_variant_dirs()
        self.assertEqual(found, [])

    def test_single_hit_returns_one_entry(self):
        _make_variant(self.root, "gf180mcuD")
        with mock.patch.object(
            pdk_mod, "_load_config", return_value={"variant": "gf180mcuD", "search_roots": []}
        ):
            with mock.patch.object(pdk_mod, "BUILTIN_SEARCH_ROOTS", (str(self.root),)):
                found = pdk_mod.find_all_variant_dirs()
        self.assertEqual(found, [(self.root / "gf180mcuD", f"search_root:{self.root}")])

    def test_multiple_hits_all_reported_in_search_order(self):
        ciel_root = self.root / "ciel_store"
        volare_root = self.root / "volare_store"
        _make_variant(ciel_root, "gf180mcuD")
        _make_variant(volare_root, "gf180mcuD")
        with mock.patch.object(
            pdk_mod, "_load_config", return_value={"variant": "gf180mcuD", "search_roots": []}
        ):
            with mock.patch.object(
                pdk_mod, "BUILTIN_SEARCH_ROOTS", (str(ciel_root), str(volare_root))
            ):
                found = pdk_mod.find_all_variant_dirs()
        self.assertEqual(
            found,
            [
                (ciel_root / "gf180mcuD", f"search_root:{ciel_root}"),
                (volare_root / "gf180mcuD", f"search_root:{volare_root}"),
            ],
        )

    def test_duplicate_resolved_path_reported_once(self):
        # A root reachable via both sim/pdk.local.json search_roots and
        # BUILTIN_SEARCH_ROOTS (coincidentally the same directory) must only
        # be reported once, keyed off the resolved absolute path.
        _make_variant(self.root, "gf180mcuD")
        with mock.patch.object(
            pdk_mod,
            "_load_config",
            return_value={"variant": "gf180mcuD", "search_roots": [str(self.root)]},
        ):
            with mock.patch.object(pdk_mod, "BUILTIN_SEARCH_ROOTS", (str(self.root),)):
                found = pdk_mod.find_all_variant_dirs()
        self.assertEqual(len(found), 1)

    def test_explicit_tiers_not_included_in_scan(self):
        # GF180_PDK_PATH / PDK_ROOT are single explicit locations, not
        # searched lists -- find_all_variant_dirs() must not consult them,
        # even when set, since only roots-list tiers can have "more than one
        # hit".
        other_variant = _make_variant(self.root / "explicit", "gf180mcuD")
        env = {"GF180_PDK_PATH": str(other_variant), "PDK_ROOT": str(self.root / "explicit")}
        with mock.patch.dict("os.environ", env, clear=False):
            with mock.patch.object(
                pdk_mod, "_load_config", return_value={"variant": "gf180mcuD", "search_roots": []}
            ):
                with mock.patch.object(pdk_mod, "BUILTIN_SEARCH_ROOTS", (str(self.root / "empty"),)):
                    found = pdk_mod.find_all_variant_dirs()
        self.assertEqual(found, [])

    def test_find_pdk_unchanged_first_hit_wins_despite_new_helper(self):
        # find_pdk() itself must still short-circuit on the first hit -- the
        # all-roots walk is additive and does not change its behavior.
        ciel_root = self.root / "ciel_store"
        volare_root = self.root / "volare_store"
        _make_variant(ciel_root, "gf180mcuD")
        _make_variant(volare_root, "gf180mcuD")
        env = dict(__import__("os").environ)
        env.pop("GF180_PDK_PATH", None)
        env.pop("PDK_ROOT", None)
        with mock.patch.dict("os.environ", env, clear=True):
            with mock.patch.object(
                pdk_mod, "_load_config", return_value={"variant": "gf180mcuD", "search_roots": []}
            ):
                with mock.patch.object(
                    pdk_mod, "BUILTIN_SEARCH_ROOTS", (str(ciel_root), str(volare_root))
                ):
                    found = pdk_mod.find_pdk()
        self.assertEqual(found.path, ciel_root / "gf180mcuD")


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
