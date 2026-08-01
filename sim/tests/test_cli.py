#!/usr/bin/env python3
"""Unit tests for sim/harness/cli.py's cmd_check_env() -- in particular the
"shadowed PDK variant" note added in #39."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import cli  # noqa: E402
from harness.pdk import Pdk  # noqa: E402


def _make_variant(root: Path, name: str = "gf180mcuD") -> Path:
    variant = root / name
    (variant / "libs.tech" / "ngspice").mkdir(parents=True)
    (variant / "libs.tech" / "ngspice" / "sm141064.ngspice").write_text("* fake\n")
    return variant


class CheckEnvTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # Every test here cares only about the PDK section of --check-env
        # output, so stub ngspice_version to a fixed, always-OK value.
        patcher = mock.patch.object(cli.runner, "ngspice_version", return_value="ngspice-42")
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_single_variant_dir_prints_no_shadow_note(self):
        variant = _make_variant(self.root, "gf180mcuD")
        pdk = Pdk(path=variant, variant="gf180mcuD", source=f"search_root:{self.root}")
        with mock.patch.object(cli, "find_pdk", return_value=pdk):
            with mock.patch.object(cli, "find_all_variant_dirs", return_value=[(variant, pdk.source)]):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    status = cli.cmd_check_env()
        output = buf.getvalue()
        self.assertEqual(status, cli.EXIT_OK)
        self.assertIn("PDK     : OK", output)
        self.assertNotIn("note:", output)

    def test_shadowed_variant_dir_prints_note(self):
        ciel_root = self.root / "ciel_store"
        volare_root = self.root / "volare_store"
        winner = _make_variant(ciel_root, "gf180mcuD")
        loser = _make_variant(volare_root, "gf180mcuD")
        pdk = Pdk(path=winner, variant="gf180mcuD", source=f"search_root:{ciel_root}")
        with mock.patch.object(cli, "find_pdk", return_value=pdk):
            with mock.patch.object(
                cli,
                "find_all_variant_dirs",
                return_value=[
                    (winner, f"search_root:{ciel_root}"),
                    (loser, f"search_root:{volare_root}"),
                ],
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    status = cli.cmd_check_env()
        output = buf.getvalue()
        self.assertEqual(status, cli.EXIT_OK)
        self.assertIn("PDK     : OK", output)
        self.assertIn(
            f"note: gf180mcuD also found under {volare_root} (search_root:{volare_root}) -- shadowed, not used",
            output,
        )
        # The winning path must never be reported as shadowing itself.
        self.assertNotIn(f"under {ciel_root}", output)

    def test_pdk_not_found_reports_missing_without_note(self):
        with mock.patch.object(cli, "find_pdk", side_effect=cli.PdkNotFound("not found")):
            buf = io.StringIO()
            with redirect_stdout(buf):
                status = cli.cmd_check_env()
        output = buf.getvalue()
        self.assertEqual(status, cli.EXIT_ENVIRONMENT)
        self.assertIn("PDK     : MISSING", output)
        self.assertNotIn("note:", output)


if __name__ == "__main__":
    unittest.main()
