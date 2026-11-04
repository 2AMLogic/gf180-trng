#!/usr/bin/env python3
"""Unit tests for ``harness.report.fleet_provenance``: the one derivation of
record provenance (job ids, simulating PDK and ngspice, klt version) shared by
the sim/tools record renderers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness.report import fleet_provenance  # noqa: E402

BANNER = "******\n** ngspice-46 : Circuit level simulation program\n** The U. C. Berkeley"


def _worker(stamp="open_pdks abc123", banner=BANNER):
    return {"pdk": {"stamp_text": stamp}, "simulator": {"version_banner": banner}}


def _report(remote, **extra):
    return {
        "environment": {"remote": remote, "engine_version": "46", **extra},
        "provenance": {"klt_version": "0.9.1", "pdk": {"version": "host-ver"}},
    }


class FleetProvenanceTest(unittest.TestCase):
    def test_fleet_report(self):
        fp = fleet_provenance(_report({"fleet": [
            {"job_id": "j1", "worker_environment": _worker()},
            {"job_id": "j2", "worker_environment": _worker()},
        ]}))
        self.assertEqual(fp, {
            "jobs": ["j1", "j2"], "pdk_ver": "abc123",
            "ngspice": "ngspice-46 : Circuit level simulation program",
            "klt_ver": "0.9.1"})

    def test_one_line_banner_falls_back_without_error(self):
        fp = fleet_provenance(_report({"fleet": [
            {"job_id": "j1", "worker_environment": _worker(banner="ngspice-46")}]}))
        self.assertEqual(fp["ngspice"], "ngspice-46")  # engine_version fallback

    def test_non_fleet_remote_is_a_one_entry_fleet(self):
        fp = fleet_provenance(_report({"job_id": "solo", "worker_environment": _worker()}))
        self.assertEqual(fp["jobs"], ["solo"])
        self.assertEqual(fp["pdk_ver"], "abc123")

    def test_disagreeing_workers_join_stamps(self):
        fp = fleet_provenance(_report({"fleet": [
            {"worker_environment": _worker(stamp="open_pdks b")},
            {"worker_environment": _worker(stamp="open_pdks a")}]}))
        self.assertEqual(fp["pdk_ver"], "open_pdks a; open_pdks b")
        self.assertEqual(fp["jobs"], [])

    def test_local_run_uses_host_fallbacks(self):
        fp = fleet_provenance({"environment": {}, "provenance": {}})
        self.assertEqual(fp, {"jobs": [], "pdk_ver": "unknown",
                              "ngspice": "ngspice-unknown", "klt_ver": "unknown"})
        fp = fleet_provenance(_report(None))
        self.assertEqual((fp["pdk_ver"], fp["ngspice"]), ("host-ver", "ngspice-46"))


if __name__ == "__main__":
    unittest.main()
