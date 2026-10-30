"""The inventory-levers table and its candidate RTL patch stay current (#709)."""
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "sim" / "tools"))
sys.path.insert(0, str(REPO / "sim"))

import inventory_levers as il  # noqa: E402


class InventoryLeversTest(unittest.TestCase):
    def test_patch_applies_to_the_shipped_rtl(self):
        r = subprocess.run(["git", "apply", "--check", str(il.PATCH)], cwd=REPO,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_candidates_only_lower_area_and_flops(self):
        from harness import pdk as pdk_mod
        try:
            root = pdk_mod.find_pdk().path
        except pdk_mod.PdkNotFound:
            self.skipTest("gf180mcu PDK not available")
        base, rows = il.build_rows(root)
        for label, r, _note, _ in rows[1:1 + len(il.CANDIDATES)]:
            self.assertLessEqual(r["area"], base["area"], label)
            self.assertLessEqual(r["flops"], base["flops"], label)


if __name__ == "__main__":
    unittest.main()
