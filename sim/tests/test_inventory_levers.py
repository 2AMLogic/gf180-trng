"""The inventory-levers table and the adopted interface RTL stay consistent (#709)."""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "sim" / "tools"))
sys.path.insert(0, str(REPO / "sim"))

import inventory_levers as il  # noqa: E402


class InventoryLeversTest(unittest.TestCase):
    def test_adopted_rtl_matches_the_inventory(self):
        rtl = (REPO / "design" / "interface" / "trng_interface.v").read_text()
        # raw_shift has no reset: it is written only by its own un-reset always block.
        self.assertNotRegex(rtl, r"raw_shift\s*<=\s*32'd0")
        self.assertRegex(rtl, r"reg \[RAW_CNT_W-1:0\] raw_bit_count")
        self.assertRegex(rtl, r"RAW_CNT_W\s*=\s*\$clog2\(TRNG_RAW_PACK_BITS\)")
        rows = {r[0]: r[1] for r in il.dpe.INTERFACE_INVENTORY}
        self.assertEqual(rows["raw packing shift register"], {"dffq_1": 32})
        self.assertEqual(rows["raw bit counter"], {"dffrnq_1": 5})

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
