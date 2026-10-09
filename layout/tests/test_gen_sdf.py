#!/usr/bin/env python3
"""Unit tests for the SDF filter in `layout/digital/gen_sdf.py` (issue #373).

`_tokenize`/`_parse`/`_serialize`/`filter_sdf` are pure string/list code and
need neither openroad nor the PDK, but until now only ran under
`check:digital-sdf`, which does. These tests use small inline synthetic SDF
fragments (not the committed `trng_top.sdf`) so they run on the PR-blocking
path (`npm run test:layout`).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

LAYOUT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAYOUT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


gen_sdf = _load("layout_digital_gen_sdf", LAYOUT_DIR / "digital" / "gen_sdf.py")

LIB = gen_sdf.CELL_LIBRARY
XNOR = f"{LIB}__xnor2_1"
NAND = f"{LIB}__nand2_1"

HEADER = '(SDFVERSION "3.0") (DESIGN "top") (TIMESCALE 1ns)'


def _cell(ctype: str, inst: str, *arcs: str) -> str:
    return (
        f'(CELL (CELLTYPE "{ctype}") (INSTANCE {inst}) '
        f"(DELAY (ABSOLUTE {' '.join(arcs)})))"
    )


def _iopath(frm: str, to: str) -> str:
    return f"(IOPATH {frm} {to} (0.1:0.2:0.3) (0.1:0.2:0.3))"


INTERCONNECT = (
    '(CELL (CELLTYPE "top") (INSTANCE) '
    "(DELAY (ABSOLUTE (INTERCONNECT a/Z b/A1 (0.000:0.000:0.000)))))"
)


class ParseRoundTripTests(unittest.TestCase):
    def test_tokenize_splits_parens_and_atoms(self):
        self.assertEqual(
            gen_sdf._tokenize('(A "q s" (B  c))'),
            ["(", "A", '"q', 's"', "(", "B", "c", ")", ")"],
        )

    def test_round_trip_nested_and_quoted(self):
        text = '(DELAYFILE (DESIGN "top") (CELL (INSTANCE u1/\\x) (DELAY (A (B (C 1))))))'
        tree = gen_sdf._parse(gen_sdf._tokenize(text))
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0][0], "DELAYFILE")
        self.assertEqual(gen_sdf._serialize(tree[0]), text)

    def test_celltype_of(self):
        cell = gen_sdf._parse(gen_sdf._tokenize(_cell(NAND, "u1")))[0]
        self.assertEqual(gen_sdf._celltype_of(cell), NAND)
        self.assertIsNone(gen_sdf._celltype_of(["CELL", ["INSTANCE", "u1"]]))


class FilterSdfTests(unittest.TestCase):
    def setUp(self):
        self.assertIn((XNOR, "A1", "ZN"), gen_sdf._ICARUS_UNSUPPORTED_ARCS)
        self.assertNotIn((NAND, "A1", "ZN"), gen_sdf._ICARUS_UNSUPPORTED_ARCS)

    def _filter(self, *cells: str):
        raw = f"(DELAYFILE {HEADER} {' '.join(cells)})"
        return gen_sdf.filter_sdf(raw)

    def test_interconnect_block_dropped_and_flagged(self):
        out, stats = self._filter(INTERCONNECT, _cell(NAND, "u1", _iopath("A1", "ZN")))
        self.assertTrue(stats["dropped_interconnect_block"])
        self.assertNotIn("INTERCONNECT", out)
        self.assertIn("u1", out)

    def test_no_interconnect_block_not_flagged(self):
        _, stats = self._filter(_cell(NAND, "u1", _iopath("A1", "ZN")))
        self.assertFalse(stats["dropped_interconnect_block"])

    def test_unsupported_iopath_dropped_and_counted(self):
        out, stats = self._filter(
            _cell(XNOR, "u2", _iopath("A1", "ZN"), _iopath("A1", "Z2"))
        )
        self.assertEqual(stats["dropped_iopath_arcs"], 1)
        self.assertEqual(stats["dropped_empty_cells"], 0)
        self.assertNotIn("(IOPATH A1 ZN ", out)
        self.assertIn("(IOPATH A1 Z2 ", out)

    def test_cell_with_no_arcs_left_is_removed_and_counted(self):
        out, stats = self._filter(
            _cell(XNOR, "u2", _iopath("A1", "ZN"), _iopath("A2", "ZN")),
            _cell(NAND, "u1", _iopath("A1", "ZN")),
        )
        self.assertEqual(stats["dropped_iopath_arcs"], 2)
        self.assertEqual(stats["dropped_empty_cells"], 1)
        self.assertNotIn("u2", out)
        self.assertIn("u1", out)

    def test_unrelated_cells_and_header_survive_unchanged(self):
        cell = _cell(NAND, "u1", _iopath("A1", "ZN"), _iopath("A2", "ZN"))
        out, stats = self._filter(cell)
        self.assertEqual(out, f"(DELAYFILE {HEADER} {cell})\n")
        self.assertEqual(
            stats,
            {
                "dropped_interconnect_block": False,
                "dropped_iopath_arcs": 0,
                "dropped_empty_cells": 0,
            },
        )


class MalformedInputTests(unittest.TestCase):
    def test_non_delayfile_raises_sdf_error(self):
        with self.assertRaises(gen_sdf.SdfError):
            gen_sdf.filter_sdf("(NOTSDF (CELL))")

    def test_multiple_top_level_nodes_raise_sdf_error(self):
        with self.assertRaises(gen_sdf.SdfError):
            gen_sdf.filter_sdf("(DELAYFILE) (DELAYFILE)")

    def test_empty_input_raises_sdf_error(self):
        for text in ("", "()"):
            with self.subTest(text=text), self.assertRaises(gen_sdf.SdfError):
                gen_sdf.filter_sdf(text)

    def test_truncated_input_raises_sdf_error(self):
        for text in ("(DELAYFILE (CELL", "(DELAYFILE", "(DELAYFILE (CELL)"):
            with self.subTest(text=text), self.assertRaises(gen_sdf.SdfError):
                gen_sdf.filter_sdf(text)

    def test_stray_tokens_raise_sdf_error(self):
        for text in ("(DELAYFILE) )", "junk (DELAYFILE)"):
            with self.subTest(text=text), self.assertRaises(gen_sdf.SdfError):
                gen_sdf.filter_sdf(text)


if __name__ == "__main__":
    unittest.main()
