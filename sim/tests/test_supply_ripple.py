#!/usr/bin/env python3
"""Offline tests for ``sim/tools/supply_ripple.py`` (issue #414).

No ngspice, no PDK, no ``klt`` and no network. They cover:

1. tone extraction on synthetic signals: amplitude/phase recovery under a
   polynomial drift, a zero-amplitude control, and a deterministic tone told
   apart from a seeded stochastic residual;
2. the ring-edge and beat-phase wrappers on synthetic edge trains whose
   displacement is known by construction;
3. the declared campaign: the committed requests match the grid, the zipped
   ``supply_v`` axes are consistent, the control leads every request, and the
   PVT corners' ring frequencies still match the records they cite;
4. ``analyse_report`` on a hand-built report in ``klt sim``'s JSON shape.
"""

from __future__ import annotations

import json
import math
import random
import re
import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR / "tools"))

import supply_ripple as sr  # noqa: E402


def sine_series(f, n, span, amp, phase=0.0, drift=(0.0, 0.0, 0.0), t0=100e-9, noise=0.0, seed=1):
    rnd = random.Random(seed)
    t = [t0 + span * i / (n - 1) for i in range(n)]
    mid, half = t0 + span / 2, span / 2
    y = []
    for ti in t:
        s = (ti - mid) / half
        v = drift[0] + drift[1] * s + drift[2] * s * s + amp * math.sin(2 * math.pi * f * ti + phase)
        if noise:
            v += rnd.gauss(0.0, noise)
        y.append(v)
    return t, y


def edge_train(period, f_mod, disp_amp, phase=0.0, n_edges=300, start=3e-9):
    """Edges t_n = start + n*period + X sin(w t_n + phase), solved by iteration."""
    w = 2 * math.pi * f_mod
    out = []
    for n in range(n_edges):
        t = start + n * period
        for _ in range(20):
            t = start + n * period + disp_amp * math.sin(w * t + phase)
        out.append(t)
    return out


class ToneFitTests(unittest.TestCase):
    def test_recovers_amplitude_and_phase_under_drift(self):
        f = 4e6
        t, y = sine_series(f, 400, 4 / f, amp=2.5e-12, phase=0.7, drift=(5e-9, 3e-12, -2e-12))
        fit = sr.fit_tone(t, y, f)
        self.assertAlmostEqual(fit["amp"], 2.5e-12, delta=1e-15)
        self.assertAlmostEqual(fit["phase_rad"], 0.7, places=6)
        self.assertLess(fit["resid_rms"], 1e-15)
        self.assertGreater(fit["frac_explained"], 0.999999)

    def test_zero_amplitude_control_is_negligible(self):
        f = 4e6
        t, y = sine_series(f, 400, 4 / f, amp=0.0, drift=(5e-9, 3e-12, -2e-12))
        fit = sr.fit_tone(t, y, f)
        self.assertLess(fit["amp"], 1e-18)
        self.assertFalse(sr.tone_detected(fit) and fit["amp"] > 1e-15)

    def test_wrong_frequency_does_not_alias_into_the_tone(self):
        # A tone at 5 MHz, looked for at 4 MHz over a whole number of 4 MHz
        # cycles: the response is orthogonal-ish, far below the true amplitude.
        t, y = sine_series(5e6, 400, 4 / 4e6, amp=1e-12)
        fit = sr.fit_tone(t, y, 4e6)
        self.assertLess(fit["amp"], 0.4e-12)

    def test_deterministic_tone_versus_stochastic_residual(self):
        f = 4e6
        t, y = sine_series(f, 600, 4 / f, amp=1e-12, noise=0.3e-12, seed=11)
        fit = sr.fit_tone(t, y, f)
        # The injected tone is recovered to within a few standard errors ...
        self.assertAlmostEqual(fit["amp"], 1e-12, delta=4 * fit["sigma_amp"])
        self.assertTrue(sr.tone_detected(fit))
        # ... and the residual is the stochastic part, close to the noise sigma.
        self.assertAlmostEqual(fit["resid_rms"], 0.3e-12, delta=0.03e-12)
        self.assertLess(fit["frac_explained"], 0.9)

    def test_pure_noise_is_not_called_a_tone(self):
        f = 4e6
        t, y = sine_series(f, 600, 4 / f, amp=0.0, noise=0.3e-12, seed=5)
        fit = sr.fit_tone(t, y, f)
        self.assertFalse(sr.tone_detected(fit))
        self.assertLess(fit["amp"], 4 * fit["sigma_amp"])

    def test_noise_free_variation_is_entirely_deterministic(self):
        f = 4e6
        t, y = sine_series(f, 400, 4 / f, amp=1e-12)
        fit = sr.fit_tone(t, y, f)
        self.assertGreater(fit["frac_explained"], 1 - 1e-9)

    def test_rejects_short_or_degenerate_input(self):
        with self.assertRaises(ValueError):
            sr.fit_tone([0.0, 1.0], [0.0, 1.0], 1.0)
        with self.assertRaises(ValueError):
            sr.fit_tone([1.0] * 10, [0.0] * 10, 1.0)


class EdgeWrapperTests(unittest.TestCase):
    def test_integer_cycle_window(self):
        f = 4e6
        edges = [i * 6.7e-9 for i in range(400)]
        sel = sr.integer_cycle_window(edges, f, 100e-9)
        span = (100e-9 + math.floor((edges[-1] - 100e-9) * f) / f)
        self.assertTrue(all(100e-9 <= e <= span + 1e-18 for e in sel))
        self.assertGreater(len(sel), 100)
        self.assertEqual(sr.integer_cycle_window(edges, f, 1.0), [])

    def test_ring_displacement_recovers_known_edge_displacement(self):
        f = 4e6
        edges = edge_train(6.7e-9, f, 12e-12, phase=0.4, n_edges=450)
        fit = sr.ring_displacement_fit(edges, f)
        self.assertAlmostEqual(fit["amp"], 12e-12, delta=0.05e-12)
        self.assertAlmostEqual(fit["ffm_amp"], 2 * math.pi * f * 12e-12, delta=2e-6)

    def test_ring_displacement_zero_for_a_perfect_ring(self):
        edges = edge_train(6.7e-9, 4e6, 0.0, n_edges=450)
        fit = sr.ring_displacement_fit(edges, 4e6)
        self.assertLess(fit["amp"], 1e-16)

    def test_beat_phase_tracks_the_difference_not_the_common_mode(self):
        f = 4e6
        p1, p2 = 6.7e-9, 6.25e-9
        only1 = sr.beat_phase_fit(edge_train(p1, f, 10e-12, n_edges=460),
                                  edge_train(p2, f, 0.0, n_edges=490), f)
        # Ring 1 displaced by x moves its cycle phase by x/p1.
        self.assertAlmostEqual(only1["amp"], 10e-12 / p1, delta=0.05 * 10e-12 / p1)
        both = sr.beat_phase_fit(edge_train(p1, f, 10e-12, n_edges=460),
                                 edge_train(p2, f, 10e-12, n_edges=490), f)
        # Equal edge-time displacement on both rails cancels to the extent the
        # periods are alike; here they differ by 7 %, so a 7 % residue remains.
        self.assertLess(both["amp"], 0.2 * only1["amp"])
        self.assertGreater(both["amp"], 0.0)

    def test_interpolate_phase(self):
        edges = [0.0, 1.0, 3.0]
        self.assertAlmostEqual(sr.interpolate_phase(edges, 0.5), 0.5)
        self.assertAlmostEqual(sr.interpolate_phase(edges, 2.0), 1.5)
        self.assertIsNone(sr.interpolate_phase(edges, 4.0))


def fake_report(f=4e6, amps=((0.0, 0, 0), (0.05, 1, 0), (0.05, 1, 1))):
    corners = []
    for amp, m1, m2 in amps:
        meas = []
        for ring, period, scale in ((1, 6.7e-9, 1.0), (2, 6.25e-9, 0.8)):
            for k, e in enumerate(edge_train(period, f, amp * 0.2e-9 * scale * (m1 if ring == 1 else m2),
                                             n_edges=430), 1):
                meas.append({"name": f"e{ring}_{k}", "value": e, "unit": "s", "status": "pass"})
        for ring, on in ((1, m1), (2, m2)):
            meas += [
                {"name": f"r{ring}_min", "value": 3.63 - amp * on, "unit": "V"},
                {"name": f"r{ring}_max", "value": 3.63 + amp * on, "unit": "V"},
                {"name": f"r{ring}_avg", "value": 3.63, "unit": "V"},
            ]
        corners.append({
            "corner_id": f"ss/{amp}/{m1}{m2}", "status": "pass", "runtime_s": 1.0,
            "supply_v": {"vsupply": 3.63, "vamp": amp, "vfrq": f, "vm1": m1, "vm2": m2},
            "measurements": meas,
        })
    return {"corners": corners, "environment": {"netlist_sha256": "x"}, "provenance": {}}


class AnalyseReportTests(unittest.TestCase):
    def test_control_negligible_and_response_scales_with_amplitude(self):
        an = sr.analyse_report(fake_report())
        ctrl, one, both = an["units"]
        self.assertLess(ctrl["ring1"]["amp"], 1e-16)
        self.assertAlmostEqual(one["ring1"]["amp"], 0.05 * 0.2e-9, delta=0.2e-12)
        # ring 2 is untouched when only ring 1 is perturbed
        self.assertLess(one["ring2"]["amp"], 1e-16)
        self.assertGreater(both["ring2"]["amp"], 1e-12)

    def test_rail_envelope_is_labelled_not_hidden(self):
        an = sr.analyse_report(fake_report())
        ctrl, one, _ = an["units"]
        self.assertTrue(ctrl["rail1"]["in_envelope"])
        self.assertFalse(one["rail1"]["in_envelope"])
        rows = sr.sensitivity_rows(an)
        self.assertTrue(any("OUT" in r for r in rows))

    def test_too_few_edges_is_reported_per_unit(self):
        rep = fake_report(amps=((0.0, 0, 0),))
        rep["corners"][0]["measurements"] = rep["corners"][0]["measurements"][:5]
        an = sr.analyse_report(rep)
        self.assertIn("error", an["units"][0])


class CampaignDefinitionTests(unittest.TestCase):
    def test_committed_requests_match_the_declared_grid(self):
        self.assertEqual(sr.cmd_emit(check=True), 0)

    def test_each_request_is_well_formed(self):
        for name, req in sr.all_requests().items():
            sv = req["corners"]["supply_v"]
            lens = {len(v) for v in sv.values()}
            self.assertEqual(len(lens), 1, name)
            self.assertEqual(sv["vamp"][0], 0.0, f"{name}: control must lead")
            self.assertEqual((sv["vm1"][0], sv["vm2"][0]), (0, 0))
            self.assertEqual(set(sv), {"vsupply", "vamp", "vfrq", "vm1", "vm2"})
            self.assertEqual(len(set(sv["vfrq"])), 1)
            self.assertIn("measureprec", req["options"]["ngspice_init"][0])
            names = [m["name"] for m in req["measurements"]]
            self.assertEqual(len(names), len(set(names)))
            self.assertTrue(any(n.startswith("e1_") for n in names))
            self.assertTrue(any(n.startswith("e2_") for n in names))

    def test_grid_has_controls_two_placements_and_a_low_and_a_beat_frequency(self):
        reqs = sr.all_requests()
        main = {n: r for n, r in reqs.items() if not n.startswith("conv-")}
        for n, r in main.items():
            sv = r["corners"]["supply_v"]
            self.assertEqual(sorted(set(sv["vamp"])), [0.0, *sr.AMPS_V], n)
            self.assertEqual({(a, b) for a, b in zip(sv["vm1"], sv["vm2"])} - {(0, 0)}, {(1, 0), (1, 1)})
        freqs = {n: r["corners"]["supply_v"]["vfrq"][0] for n, r in main.items()}
        self.assertEqual(freqs["nominal-lowf"], sr.LOW_F_HZ)
        self.assertAlmostEqual(freqs["binding-beat"], 7.65e6)

    def test_window_holds_at_least_four_cycles_of_every_ripple_frequency(self):
        for name, corner, fk, _ in sr.REQUESTS:
            f = sr.frequency_hz(corner, fk)
            usable = sr.TSTOP_S[fk] - sr.T_FIT_START_S
            self.assertGreaterEqual(usable * f, 4.0, name)
            # and the edge count requested fits inside the window
            for period, k in zip(sr.CORNERS[corner]["periods_s"], sr.edge_counts(corner, sr.TSTOP_S[fk])):
                self.assertLess(k * period, sr.TSTOP_S[fk])

    def test_pvt_provenance_matches_the_cited_records(self):
        for key, rec in (("nominal", "2026-08-02-ro-array-core-pvt-q-32.md"),
                         ("binding", "2026-08-02-ro-array-core-pvt-q-54.md")):
            text = (REPO_ROOT / "sim" / "records" / rec).read_text()
            f1 = float(re.search(r"^- `f_r1`: (\S+)", text, re.M).group(1))
            f2 = float(re.search(r"^- `f_r2`: (\S+)", text, re.M).group(1))
            c = sr.CORNERS[key]
            self.assertAlmostEqual(1 / c["periods_s"][0], f1, delta=f1 * 1e-6)
            self.assertAlmostEqual(1 / c["periods_s"][1], f2, delta=f2 * 1e-6)
            self.assertAlmostEqual(c["f_beat_hz"], abs(f2 - f1), delta=0.06e6)
            proc = re.search(r"^  process: (\S+)", text, re.M).group(1)
            temp = float(re.search(r"^  temperature: (\S+)", text, re.M).group(1))
            volt = float(re.search(r"^  voltage: (\S+) V", text, re.M).group(1))
            self.assertEqual((proc, temp, volt), (c["process"], c["temp_c"], c["vdd"]))

    def test_deck_defines_every_source_the_requests_alter_and_no_waveform_source(self):
        deck = (sr.TB_DIR / sr.DECK).read_text().lower()
        for src in ("vamp", "vfrq", "vm1", "vm2", "vsupply"):
            self.assertRegex(deck, rf"(?m)^{src} .* dc ")
        # klt rejects `alter` on SIN/PULSE sources; the ripple is a B source.
        self.assertNotRegex(deck, r"(?m)^v\w+ .*\bsin\s*\(")
        self.assertIn(sr.DUT_PATH, deck.replace("../", ""))

    def test_estimate_is_stated_and_ci_runs_nothing_heavy(self):
        text = sr.plan_text()
        self.assertIn("CPU-hours", text)
        self.assertIn("Not run by CI or selftest", text)
        # No harness script invokes the opt-in submit path.
        for script in (SIM_DIR / "selftest.sh",):
            self.assertNotIn("supply_ripple", script.read_text())

    def test_dut_blob_sha_is_a_git_blob_hash(self):
        self.assertRegex(sr.dut_blob_sha(), r"^[0-9a-f]{40}$")

    def test_limits_are_printed_with_every_analysis(self):
        self.assertTrue(any("synthetic" in l.lower() or "ideal series" in l.lower() for l in sr.LIMITS))
        self.assertTrue(any("min-entropy" in l for l in sr.LIMITS))


class CliTests(unittest.TestCase):
    def test_analyze_json_runs_on_a_report_file(self):
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.json"
            p.write_text(json.dumps(fake_report()))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = sr.main(["analyze", str(p)])
            self.assertEqual(rc, 0)
            self.assertIn("Limits of interpretation", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
