"""The ring1 well-tie rewiring generator (issue #339): count, stability, failure."""

import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "build_welltied", ROOT / "sim/tb/ro-ring11-pex-welltied/build_welltied.py"
)
bw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bw)

BODY_BIAS = {
    "status": "unbiased",
    "unbiased_device_count": 2,
    "unbiased_nets": ["\\$9"],
    "unbiased_pmos_body_nets": [
        {"device": "$1", "net": "\\$9"},
        {"device": "$2", "net": "\\$9"},
    ],
}
NETLIST = (
    "* device instance $1 r0 *1 0,0 pfet\n"
    "X$1 d1 g1 vddr__t1 \\$9 pfet_03v3 L=2U W=0.22U\n"
    "+ PS=2.28U PD=1.24U\n"
    "* device instance $2 r0 *1 1,0 pfet\n"
    "X$2 d2 g2 s2 \\$9 pfet_03v3 L=0.28U W=0.44U\n"
    "X$3 d3 g3 s3 vsubs nfet_03v3 L=0.28U W=0.44U\n"
    "Cx a b 1e-15\n"
)


class Rewire(unittest.TestCase):
    def test_rewires_only_the_listed_bodies(self):
        out, n = bw.rewire(NETLIST, BODY_BIAS)
        self.assertEqual(n, 2)
        self.assertIn("X$1 d1 g1 vddr__t1 vddr pfet_03v3 L=2U W=0.22U\n+ PS=2.28U PD=1.24U", out)
        self.assertIn("X$2 d2 g2 s2 vddr pfet_03v3", out)
        self.assertIn("X$3 d3 g3 s3 vsubs nfet_03v3", out)
        self.assertNotIn("\\$9", out)

    def test_deterministic(self):
        self.assertEqual(bw.rewire(NETLIST, BODY_BIAS), bw.rewire(NETLIST, BODY_BIAS))

    def test_missing_device_raises(self):
        with self.assertRaisesRegex(bw.BuildError, "no card"):
            bw.rewire(NETLIST.replace("X$2 ", "Y$2 "), BODY_BIAS)

    def test_count_mismatch_raises(self):
        bb = copy.deepcopy(BODY_BIAS)
        bb["unbiased_device_count"] = 3
        with self.assertRaisesRegex(bw.BuildError, "unbiased_device_count"):
            bw.rewire(NETLIST, bb)

    def test_body_not_matching_envelope_raises(self):
        with self.assertRaisesRegex(bw.BuildError, "body is"):
            bw.rewire(NETLIST.replace("g2 s2 \\$9", "g2 s2 \\$7"), BODY_BIAS)

    def test_unlisted_pfet_raises(self):
        with self.assertRaisesRegex(bw.BuildError, "not in the envelope"):
            bw.rewire(NETLIST + "X$4 d g s \\$11 pfet_03v3 L=1U W=1U\n", BODY_BIAS)

    def test_listed_nfet_raises(self):
        with self.assertRaisesRegex(bw.BuildError, "model is"):
            bw.rewire(NETLIST.replace("s2 \\$9 pfet_03v3", "s2 \\$9 nfet_03v3"), BODY_BIAS)

    def test_well_still_referenced_raises(self):
        with self.assertRaisesRegex(bw.BuildError, "still referenced"):
            bw.rewire(NETLIST + "Cw \\$9 0 1e-15\n", BODY_BIAS)

    def test_not_unbiased_raises(self):
        bb = copy.deepcopy(BODY_BIAS)
        bb["status"] = "biased"
        with self.assertRaisesRegex(bw.BuildError, "status"):
            bw.rewire(NETLIST, bb)


class CommittedFiles(unittest.TestCase):
    def test_ring1_ties_23_of_23(self):
        bb = json.loads(bw.ENVELOPE.read_text())["body_bias"]
        out, n = bw.rewire(bw.SOURCE_NETLIST.read_text(), bb)
        self.assertEqual((n, bb["unbiased_device_count"]), (23, 23))
        self.assertEqual(len(bb["unbiased_nets"]), 11)

    def test_committed_outputs_are_current(self):
        netlist, tb = bw.render()
        self.assertEqual(bw.OUT_NETLIST.read_text(), netlist)
        self.assertEqual(bw.OUT_TB.read_text(), tb)

    def test_request_matches_sibling_except_testbench_and_artifacts(self):
        a = json.loads((ROOT / "sim/tb/ro-ring11-pex/request.json").read_text())
        b = json.loads((bw.HERE / "request.json").read_text())
        for r in (a, b):
            r.pop("netlist")
            r["options"].pop("keep_artifacts")
        self.assertEqual(a, b)


_wr_spec = importlib.util.spec_from_file_location(
    "write_records_welltied", ROOT / "sim/tb/ro-ring11-pex-welltied/write_records.py"
)
wr = importlib.util.module_from_spec(_wr_spec)
_wr_spec.loader.exec_module(wr)


class BatchJobProvenance(unittest.TestCase):
    """Cloud-account details from klt's `environment.remote` never reach a record."""

    REMOTE = {
        "provider": "aws-batch-fleet", "job_id": "klt-sim-0", "bucket": "b-123",
        "region": "r", "instance_id": "i-x", "instance_type": "t", "availability_zone": "z",
        "ami_id": "ami-x", "lifecycle": "spot", "spot": True, "state": "done",
        "exit_code": "0", "concurrency": "2", "physical_cores": "16", "elapsed_seconds": 1,
    }

    def test_allow_list_only(self):
        out = wr.batch_job_provenance(self.REMOTE)
        self.assertEqual(set(out), set(wr.BATCH_JOB_FIELDS))
        for k in ("bucket", "region", "instance_id", "availability_zone", "ami_id"):
            self.assertNotIn(k, out)

    def test_committed_raw_json_is_allow_listed(self):
        raws = sorted((ROOT / "sim/records/raw").glob("*-ro-ring11-pex-welltied-*/*.json"))
        self.assertEqual(len(raws), 27)
        for p in raws:
            job = json.loads(p.read_text())["batch_job"]
            self.assertLessEqual(set(job), set(wr.BATCH_JOB_FIELDS), p.name)
        records = sorted((ROOT / "sim/records").glob("*-ro-ring11-pex-welltied-*.md"))
        self.assertEqual(len(records), 27)
        for p in records:
            self.assertNotRegex(p.read_text(), r"\bi-0[0-9a-f]{8,}|\bami-[0-9a-f]+", p.name)


class ReportGate(unittest.TestCase):
    """write_records refuses anything but a clean pass of all 27 corners."""

    @staticmethod
    def rep(status="pass", passed=27, count=27, entries=27):
        return {"status": status, "passed": passed, "corner_count": count,
                "corners": [{}] * entries}

    def test_clean_27_accepted(self):
        self.assertIsNone(wr.report_problem(self.rep()))

    def test_equal_but_short_refused(self):
        # Regression: `passed != corner_count != 27` let 26/26 through.
        self.assertIsNotNone(wr.report_problem(self.rep(passed=26, count=26, entries=26)))

    def test_partial_pass_refused(self):
        self.assertIsNotNone(wr.report_problem(self.rep(passed=26)))

    def test_corner_list_mismatch_refused(self):
        self.assertIsNotNone(wr.report_problem(self.rep(entries=26)))

    def test_failed_status_refused(self):
        self.assertIsNotNone(wr.report_problem(self.rep(status="fail")))

    def test_main_refuses_26_of_26_before_writing(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "report.json"
            p.write_text(json.dumps(self.rep(passed=26, count=26, entries=26)))
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(wr.main([str(p), d]), 1)
            self.assertIn("26/26", err.getvalue())


if __name__ == "__main__":
    unittest.main()
