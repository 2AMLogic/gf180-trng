#!/usr/bin/env python3
"""Offline tests for ``sim/tools/mc_yield_campaign.py`` (issue #1025).

No ngspice, no PDK, no ``klt`` and no network. They cover the declared
campaign, because the campaign's correctness is decided before any run:

1. sizing is read from the committed ``klt yield`` response (``required_n``),
   and the headroom arithmetic keeps the verdict ``sufficient`` through one
   stray failure at the default target;
2. the eight committed requests match the declaration byte-for-byte
   (``emit --check``), carry distinct recorded seeds, the DR-0033 limits on
   the graded measurements, the mismatch switch in ``corners.params``, and
   the known-bad knob only where the control requests belong;
3. sharding: every request's declared ``batch.max_units_per_job`` keeps the
   conservative whole-job bound inside the fleet's 3600 s ceiling;
4. the measurement cards: concrete ``val=`` literals per corner, the
   TRIG/TARG + ``param=`` four-period averaging forms, and ngspice-legal
   measurement names (``[A-Za-z_][A-Za-z0-9_]*`` -- a name with ``@`` cannot
   be a request measurement, which is why the DR-0033 ``name@corner`` keys
   are applied by ``signoff/publish_item6.py``, not here);
5. ``analyze`` on a hand-built report in ``klt sim``'s JSON shape.
"""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR / "tools"))

import mc_yield_campaign as mc  # noqa: E402

NAME_RE = __import__("re").compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class Sizing(unittest.TestCase):
    def test_required_n_read_from_report(self):
        # The committed report's four measurements all say 183 today; the
        # campaign must size itself against the file, not a constant.
        doc = json.loads(mc.YIELD_RESPONSE.read_text())
        self.assertEqual(mc.required_n(), max(m["sample_size"]["required_n"] for m in doc["measurements"]))

    def test_nominal_draw_covers_required_and_one_failure(self):
        n = mc.n_nominal()
        self.assertGreaterEqual(n, mc.required_n())
        self.assertEqual(n % 5, 0)
        # zero failures: the exact Clopper-Pearson form
        self.assertGreaterEqual(n, math.log(0.025) / math.log(0.98))
        # one stray failure: the normal-approximation form at p = (n-1)/n
        p = (n - 1) / n
        required_one = 1.96 ** 2 * p * (1 - p) / 0.01 ** 2
        self.assertGreaterEqual(n, required_one)

    def test_control_draw_detects_all_fail(self):
        # Exact two-sided 95% Clopper-Pearson bounds at zero and all successes.
        self.assertLess(mc.N_CONTROL, mc.n_nominal())
        control_upper = 1 - 0.025 ** (1 / mc.N_CONTROL)
        nominal_lower = 0.025 ** (1 / mc.n_nominal())
        self.assertLess(control_upper, nominal_lower)


class Requests(unittest.TestCase):
    def setUp(self):
        self.all = mc.all_requests()

    def test_emit_check_clean(self):
        for (tb, name), req in self.all.items():
            path = mc.request_path(tb, name)
            self.assertTrue(path.exists(), path)
            self.assertEqual(path.read_text(), mc.render(req), f"{path} drifted")

    def test_distinct_seeds_and_declared_counts(self):
        seeds = [req["monte_carlo"]["seed"] for req in self.all.values()]
        self.assertEqual(len(seeds), len(set(seeds)))
        # every seed is one of the recorded constants, so the declaration and
        # the fleet reports' environment.monte_carlo agree by construction
        recorded = set(mc.SEEDS.values())
        self.assertTrue(set(seeds) <= recorded)
        for (tb, name), req in self.all.items():
            want = mc.N_CONTROL if name.startswith("mc-control") else mc.n_nominal()
            self.assertEqual(req["monte_carlo"]["n"], want, f"{tb}/{name}")
            self.assertEqual(req["monte_carlo"]["vary"], "mismatch")

    def test_mismatch_switch_is_a_params_row(self):
        # The bodies ship sw_stat_mismatch=0; every request must switch the
        # deck's own Pelgrom model on per sample.
        for req in self.all.values():
            self.assertEqual(req["corners"]["params"]["sw_stat_mismatch"], [1])

    def test_known_bad_knobs_only_on_controls(self):
        for (tb, name), req in self.all.items():
            params = req["corners"]["params"]
            is_control = name.startswith("mc-control")
            self.assertEqual("ro_lstv" in params, is_control and tb == "ro")
            if is_control and tb == "ro":
                self.assertEqual(params["ro_lstv"], [mc.RO_CONTROL_LSTV_M])
            supply = req["corners"]["supply_v"]
            self.assertEqual("voff" in supply, is_control and tb == "sampler")
            if is_control and tb == "sampler":
                self.assertEqual(supply["voff"], [mc.SAM_VOFF_V])
                # the widened sweep keeps the shifted crossing measurable
                lo, hi, _ = (float(x) for x in req["analysis"]["args"].split()[1:])
                self.assertEqual((lo, hi), (2.5, 5.0))

    def test_dr0033_limits_on_graded_measurements(self):
        lim = mc.limits()
        ro = self.all[("ro", "mc-tt")]
        ro_ss = self.all[("ro", "mc-ss")]
        got = {m["name"]: m.get("limits") for m in ro["measurements"]}
        got_ss = {m["name"]: m.get("limits") for m in ro_ss["measurements"]}
        self.assertEqual(got["m_period_r1"], {"max": lim["period_r1@tt_27c_3.30v"]["max"]})
        self.assertEqual(got_ss["m_period_r1"], {"max": lim["period_r1@ss_125c_3.63v"]["max"]})
        self.assertIsNone(got["m_t4_r1"])
        sam = self.all[("sampler", "mc-tt")]
        got_sam = {m["name"]: m.get("limits") for m in sam["measurements"]}
        # the rail window's exclusivity is a yield-side refinement; the
        # request carries the inclusive bounds, the publisher attaches the
        # ratified exclusive form from limits.json
        self.assertEqual(got_sam["m_dtrip_v"], {"min": 0.0, "max": 3.3})

    def test_measurement_names_are_request_legal(self):
        for req in self.all.values():
            for m in req["measurements"]:
                self.assertRegex(m["name"], NAME_RE)

    def test_ro_cards_concrete_val_per_corner(self):
        tt = {m["name"]: m["spice"] for m in self.all[("ro", "mc-tt")]["measurements"]}
        ss = {m["name"]: m["spice"] for m in self.all[("ro", "mc-ss")]["measurements"]}
        self.assertIn("val=1.65", tt["m_t4_r1"])
        self.assertIn("val=1.815", ss["m_t4_r1"])
        self.assertIn("param='m_t4_r1/4'", tt["m_period_r1"])
        self.assertIn("trig v(ro1)", tt["m_t4_r1"])
        self.assertIn("targ v(ro1) val=1.65 rise=6", tt["m_t4_r1"])

    def test_sampler_card_tracks_corner_supply(self):
        tt = self.all[("sampler", "mc-tt")]["measurements"][0]["spice"]
        ss = self.all[("sampler", "mc-ss")]["measurements"][0]["spice"]
        self.assertIn("when v(xdut.mb)=1.65", tt)
        self.assertIn("when v(xdut.mb)=1.815", ss)


class Sharding(unittest.TestCase):
    def test_every_request_fits_the_fleet_ceiling(self):
        for (tb, name), req in mc.all_requests().items():
            timeout = req["options"]["timeout_s"]
            cap = req["batch"]["max_units_per_job"]
            self.assertEqual(cap, mc.max_units_per_job(timeout))
            bound = timeout * cap + mc.FLEET_OVERHEAD_S
            self.assertLessEqual(bound, mc.FLEET_CEILING_S, f"{tb}/{name}: {bound}s")
            self.assertEqual(req["batch"]["capacity_wait_s"], 600)

    def test_shard_counts(self):
        # 220 units at 14/job -> 16 shards; 30 at 14 -> 3; 220 at 29 -> 8; 30 -> 2
        self.assertEqual(mc.shards(mc.n_nominal(), mc.RO_TIMEOUT_S), math.ceil(mc.n_nominal() / 14))
        self.assertEqual(mc.shards(30, mc.RO_TIMEOUT_S), 3)
        self.assertEqual(mc.shards(mc.n_nominal(), mc.SAM_TIMEOUT_S), 8 if mc.n_nominal() == 220 else math.ceil(mc.n_nominal() / 29))


def _fake_report(n=5, fail_all=False, seed=10250101, name="m_period_r1", limit_max=9.151e-9):
    corners, values = [], []
    for i in range(n):
        v = limit_max * (1.5 if fail_all else 0.7)
        values.append(v)
        corners.append({
            "corner_id": f"tt/3.300V/27C/mc{i}",
            "monte_carlo": {"sample_index": i, "seed": seed},
            "measurements": [{"name": name, "value": v, "status": "fail" if fail_all else "pass", "unit": "s"}],
        })
    rollup = [{"name": name, "limits": {"max": limit_max}}]
    env = {"monte_carlo": {"seed": seed, "n": n}}
    return {"corners": corners, "measurements": rollup, "environment": env}, values


class Analyze(unittest.TestCase):
    def _run(self, doc):
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".report.json", delete=False) as fh:
            json.dump(doc, fh)
            path = fh.name
        import contextlib
        import io

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = mc.cmd_analyze([path], as_json=True)
        self.assertEqual(rc, 0)
        return json.loads(buf.getvalue())[path]

    def test_nominal_counts_and_stats(self):
        doc, values = _fake_report(n=6)
        info = self._run(doc)
        self.assertEqual(info["seed"], 10250101)
        self.assertEqual(info["declared_n"], 6)
        self.assertEqual(info["samples_seen"], 6)
        e = info["measurements"]["m_period_r1"]
        self.assertEqual(e["n"], 6)
        self.assertEqual(e["errored"], 0)
        self.assertEqual(e["failed_limit"], 0)
        self.assertAlmostEqual(e["min"], min(values))
        self.assertAlmostEqual(e["max"], max(values))

    def test_control_counts_failures_and_nulls(self):
        doc, _ = _fake_report(n=5, fail_all=True)
        doc["corners"][2]["measurements"][0]["value"] = None  # one errored draw
        info = self._run(doc)
        e = info["measurements"]["m_period_r1"]
        self.assertEqual(e["n"], 4)
        self.assertEqual(e["errored"], 1)
        self.assertEqual(e["failed_limit"], 4)


if __name__ == "__main__":
    unittest.main()
