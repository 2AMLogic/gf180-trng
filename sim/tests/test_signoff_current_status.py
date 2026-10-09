"""Current T1 status statements must agree with the committed verdict of record.

current_status_problems() compares the designated current-status block of each
public document with the report's tier, met count and item count. Expected
values are taken from the (synthetic) report, never hard-coded, so a changed
report count is exercised directly.
"""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("signoff_check", ROOT / "signoff" / "check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

B, E = check.CURRENT_STATUS_BEGIN, check.CURRENT_STATUS_END


def doc(met=8, total=22, tier="null", historical="T1 3 of 22 items met earlier."):
    return (f"{historical}\nNow {B}`tier: {tier}`, T1 {met} of {total} items met{E}.\n")


def report(met=8, total=22, tier=None):
    return {"tier": tier, "t1_met_count": met, "t1_item_count": total}


class CurrentStatus(unittest.TestCase):
    def problems(self, text, rep=None):
        return check.current_status_problems(rep or report(), {"d.md": text})

    def test_agreement_ignores_historical_text(self):
        self.assertEqual(self.problems(doc()), [])

    def test_wrong_numerator(self):
        self.assertTrue(any("items met" in p for p in self.problems(doc(met=3))))

    def test_wrong_denominator(self):
        self.assertTrue(any("T1 items" in p for p in self.problems(doc(total=11))))

    def test_wrong_tier(self):
        self.assertTrue(any("tier" in p for p in self.problems(doc(tier="T1"))))

    def test_changed_report_count_fails_previously_good_doc(self):
        self.assertTrue(self.problems(doc(), report(met=9)))
        self.assertEqual(self.problems(doc(met=9), report(met=9)), [])

    def test_tier_non_null_agrees(self):
        self.assertEqual(self.problems(doc(met=22, tier="T1"), report(22, 22, "T1")), [])

    def test_missing_block(self):
        self.assertTrue(self.problems("T1 8 of 22 items met, `tier: null`\n"))

    def test_malformed_block(self):
        self.assertTrue(self.problems(f"{B}eight of 22{E}"))

    def test_duplicate_block(self):
        self.assertTrue(self.problems(doc() + doc()))

    def test_committed_docs_agree_with_committed_report(self):
        self.assertEqual(check.verify_current_status(), [])


if __name__ == "__main__":
    unittest.main()
