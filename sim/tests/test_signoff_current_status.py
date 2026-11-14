"""Current T1 status statements must agree with the committed verdict of record.

current_status_problems() compares the designated current-status block of each
public document with the report's tier, met count, item count and the names of
its `unmet` T1 rows. Expected values are taken from the (synthetic) report,
never hard-coded, so a changed report count or composition is exercised
directly.

The composition clause is why a count is not enough: a sum cannot name a
composition, so two rows changing in opposite directions would leave a
count-only block valid and unchanged (#881).
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
from sim.tools.pathload import load_module_from_path  # noqa: E402  (#553)
check = load_module_from_path("signoff_check", ROOT / "signoff" / "check.py")

B, E = check.CURRENT_STATUS_BEGIN, check.CURRENT_STATUS_END


def rows(met=8, total=22):
    """Synthetic T1 rows: the first `met` of `total` read `met`, the rest `unmet`.

    Rows are laid out as the real record lays them out -- item N renders as
    `N.analog` then `N.digital` -- and the three tier-summary entries the
    record also carries (T2/T3/T4, `id` and `partition` null, `status`
    `unmet`) are appended. Those three are not rows: a parser that forgets to
    filter on `tier == "T1"` would invent three phantom unmet rows, so every
    case here exercises the filter.
    """
    out = [
        {
            "tier": "T1",
            "id": n // 2 + 1,
            "partition": "analog" if n % 2 == 0 else "digital",
            "status": "met" if n < met else "unmet",
        }
        for n in range(total)
    ]
    out += [
        {"tier": tier, "id": None, "partition": None, "status": "unmet"}
        for tier in ("T2", "T3", "T4")
    ]
    return out


def report(met=8, total=22, tier=None, items=None):
    return {
        "tier": tier,
        "t1_met_count": met,
        "t1_item_count": total,
        "items": rows(met, total) if items is None else items,
    }


def unmet_text(met=8, total=22):
    """The composition clause the matching report demands."""
    return check.format_unmet_rows(check.t1_unmet_rows(report(met, total)))


def doc(met=8, total=22, tier="null", historical="T1 3 of 22 items met earlier.",
        unmet=None):
    clause = unmet_text(met, total) if unmet is None else unmet
    return (
        f"{historical}\nNow {B}`tier: {tier}`, T1 {met} of {total} items met, "
        f"unmet: {clause}{E}.\n"
    )


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
        # The all-rows-met edge case: no unmet row, so the clause reads `none`.
        # Also the sharpest test of the tier filter -- the T2/T3/T4 summary
        # entries are `unmet`, so a parser that counted them would fail here.
        self.assertEqual(unmet_text(22, 22), "none")
        self.assertEqual(self.problems(doc(met=22, tier="T1"), report(22, 22, "T1")), [])

    def test_missing_block(self):
        self.assertTrue(self.problems("T1 8 of 22 items met, `tier: null`\n"))

    def test_malformed_block(self):
        self.assertTrue(self.problems(f"{B}eight of 22{E}"))

    def test_duplicate_block(self):
        self.assertTrue(self.problems(doc() + doc()))

    def test_committed_docs_agree_with_committed_report(self):
        self.assertEqual(check.verify_current_status(), [])

    # -- the composition clause (#881) ------------------------------------

    def test_row_swap_moves_the_block_text_though_the_count_does_not(self):
        """An equal-and-opposite row swap must change the block, not just pass.

        This is the failure the count-only format permitted: `3.digital` going
        `met` -> `unmet` while `5.digital` goes `unmet` -> `met` leaves
        `t1_met_count` untouched.
        """
        before = report(items=[
            {"tier": "T1", "id": 3, "partition": "digital", "status": "met"},
            {"tier": "T1", "id": 5, "partition": "digital", "status": "unmet"},
        ])
        after = report(items=[
            {"tier": "T1", "id": 3, "partition": "digital", "status": "unmet"},
            {"tier": "T1", "id": 5, "partition": "digital", "status": "met"},
        ])
        # The aggregate the old format compared is identical across the swap...
        aggregate = lambda r: (r["tier"], r["t1_met_count"], r["t1_item_count"])  # noqa: E731
        self.assertEqual(aggregate(before), aggregate(after))
        # ...but the block text each report demands is not.
        self.assertEqual(check.t1_unmet_rows(before), ["5.digital"])
        self.assertEqual(check.t1_unmet_rows(after), ["3.digital"])

        good_before = doc(unmet="`5.digital`")
        self.assertEqual(self.problems(good_before, before), [])
        # The document that was correct before the swap is a problem after it.
        after_problems = self.problems(good_before, after)
        self.assertTrue(any("unmet rows" in p for p in after_problems), after_problems)
        self.assertEqual(self.problems(doc(unmet="`3.digital`"), after), [])

    def test_wrong_unmet_row(self):
        problems = self.problems(doc(unmet=unmet_text().replace("5.analog", "4.analog")))
        self.assertTrue(any("unmet rows" in p for p in problems), problems)

    def test_unmet_clause_must_be_in_canonical_order(self):
        """One graded state has exactly one valid block text."""
        shuffled = ", ".join(reversed(unmet_text().split(", ")))
        self.assertNotEqual(shuffled, unmet_text())
        self.assertTrue(any("unmet rows" in p for p in self.problems(doc(unmet=shuffled))))

    def test_block_without_an_unmet_clause_is_malformed(self):
        """The pre-#881 count-only block no longer satisfies the parser."""
        old_format = f"{B}`tier: null`, T1 8 of 22 items met{E}\n"
        self.assertTrue(any("unmet" in p for p in self.problems(old_format)))

    def test_claiming_none_while_rows_are_unmet_fails(self):
        self.assertTrue(any("unmet rows" in p for p in self.problems(doc(unmet="none"))))

    def test_claiming_rows_while_none_are_unmet_fails(self):
        rep = report(22, 22, "T1")
        problems = check.current_status_problems(
            rep, {"d.md": doc(met=22, tier="T1", unmet="`3.digital`")}
        )
        self.assertTrue(any("unmet rows" in p for p in problems), problems)

    def test_tier_summary_rows_are_not_t1_rows(self):
        """T2/T3/T4 entries carry `status: unmet` and are not checklist rows."""
        rep = report(items=[
            {"tier": "T1", "id": 1, "partition": "analog", "status": "met"},
            {"tier": "T2", "id": None, "partition": None, "status": "unmet"},
            {"tier": "T3", "id": None, "partition": None, "status": "unmet"},
        ])
        self.assertEqual(check.t1_unmet_rows(rep), [])

    def test_report_without_items_is_itself_a_problem(self):
        """A record that cannot name its composition fails loudly, not quietly."""
        rep = {"tier": None, "t1_met_count": 8, "t1_item_count": 22}
        self.assertIsNone(check.t1_unmet_rows(rep))
        problems = check.current_status_problems(rep, {"d.md": doc()})
        self.assertTrue(any("items[]" in p for p in problems), problems)
        # The tier and count comparisons still run against such a report.
        self.assertTrue(any("items met" in p for p in
                            check.current_status_problems(rep, {"d.md": doc(met=3)})))

    def test_single_partition_report(self):
        """A block graded once (no partition) names its rows by item alone."""
        rep = {
            "tier": None, "t1_met_count": 1, "t1_item_count": 2,
            "items": [
                {"tier": "T1", "id": 1, "partition": None, "status": "met"},
                {"tier": "T1", "id": 2, "partition": None, "status": "unmet"},
            ],
        }
        self.assertEqual(check.t1_unmet_rows(rep), ["2"])
        text = f"{B}`tier: null`, T1 1 of 2 items met, unmet: `2`{E}\n"
        self.assertEqual(check.current_status_problems(rep, {"d.md": text}), [])

    def test_committed_report_composition_is_consistent_with_its_count(self):
        """Guards the real record: met + unmet must exhaust the T1 rows."""
        import json
        rep = json.loads((ROOT / "signoff" / "records" / "t1-tier-report.json").read_text())
        unmet = check.t1_unmet_rows(rep)
        self.assertIsNotNone(unmet)
        self.assertEqual(len(unmet) + rep["t1_met_count"], rep["t1_item_count"])


if __name__ == "__main__":
    unittest.main()
