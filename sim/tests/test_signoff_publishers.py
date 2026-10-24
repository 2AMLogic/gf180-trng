"""Signoff publishers: refusal paths, `--backend` argv and the publication fields check.py reads (#611).

Offline: `subprocess.run` is mocked, every destination is redirected into a
temporary directory (nothing is written under signoff/evidence/), and neither
klt, ngspice nor the PDK is needed.
"""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
from sim.tools.pathload import load_module_from_path  # noqa: E402  (#553)
item7 = load_module_from_path("signoff_publish_item7_analog", ROOT / "signoff" / "publish_item7_analog.py")
cs = load_module_from_path("signoff_publish_combiner_sampler_pex", ROOT / "signoff" / "publish_combiner_sampler_pex.py")
check = item7.check
common = item7.common

VERDICT = {"verdict": "pass", "counts": {"unmeasured": 0}}


def _envelope(build=None, **extra):
    env = {
        "provenance": {"klt_version": build or check.KLT_PIN, "klayout_version": "0.30.10",
                       "pdk": "gf180mcuD", "deck": "gf180mcu",
                       "input": {"content_hash": "sha256:" + "ab" * 32}},
        "body_bias": {"status": "unbiased", "unbiased_device_count": 7},
    }
    env.update(extra)
    return env


class Scratch(unittest.TestCase):
    """A temporary REPO_ROOT; the real repository tree is never written."""

    mod = None

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for target, value in ((self.mod, "REPO_ROOT"), (self.mod, "SCRATCH")):
            p = mock.patch.object(target, value, self.root if value == "REPO_ROOT" else self.root / "scratch")
            p.start()
            self.addCleanup(p.stop)

    def write(self, rel, text="x"):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def run_quiet(self, fn, *args, **kw):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            return fn(*args, **kw), err.getvalue()


class CommonSteps(Scratch):
    """The shared publisher steps directly (signoff/publish_common.py)."""

    mod = item7  # Scratch needs a module with REPO_ROOT/SCRATCH; common takes `root` explicitly

    def test_envelope_refusals_lists_every_gate(self):
        env = _envelope("0.0.1", pin_count_mismatch={"d": 1}, flat_dut_mismatch={"d": 2})
        got = common.envelope_refusals(self.root, env, "n.spice")
        self.assertEqual(len(got), 4)
        for text, line in zip(("not the producer pin", "pin_count_mismatch", "flat_dut_mismatch", "n.spice is missing"), got):
            self.assertIn(text, line)

    def test_envelope_refusals_clean(self):
        self.write("n.spice")
        self.assertEqual(common.envelope_refusals(self.root, _envelope(), "n.spice"), [])

    def publish(self, build, validate, dest, allow=False):
        pub_path = self.root / "pub.json"
        return self.run_quiet(common.publish_envelope, "x: refusing", dest, b"new", build, validate, allow, pub_path)

    def test_failure_restores_previous_and_removes_new(self):
        old = self.write("old.json", "previous")
        pub, err = self.publish(lambda sha: {}, lambda p: ["bad"], old)
        self.assertIsNone(pub)
        self.assertEqual(old.read_text(), "previous")
        self.assertIn("x: refusing -- envelope not written", err)
        new = self.root / "sub" / "new.json"
        pub, _ = self.publish(lambda sha: (_ for _ in ()).throw(KeyError("k")), lambda p: [], new)
        self.assertIsNone(pub)
        self.assertFalse(new.exists())
        self.assertFalse((self.root / "pub.json").exists())

    def test_success_writes_envelope_and_publication_with_sha(self):
        dest = self.root / "e.json"
        pub, _ = self.publish(lambda sha: {"sha": sha}, lambda p: [], dest)
        self.assertEqual(dest.read_bytes(), b"new")
        self.assertEqual(pub["sha"], check.sha256_file(dest))
        self.assertEqual(json.loads((self.root / "pub.json").read_text()), pub)


class Item7RunPex(Scratch):
    mod = item7

    def argv(self, env, *args, **kw):
        with mock.patch.dict(os.environ, env), mock.patch.object(common.subprocess, "run") as run:
            self.run_quiet(item7.run_pex, *args, **kw)
        self.assertEqual(run.call_count, 1)
        return run.call_args.args[0], run.call_args.kwargs

    def test_backend_appended_only_when_set(self):
        argv, kw = self.argv({"KLT": "klt"}, "ring1")
        self.assertEqual(argv, ["klt", *item7.KLT_PEX_ARGS])
        self.assertEqual(kw["cwd"], self.root)
        self.assertTrue(kw["check"])
        argv, _ = self.argv({"KLT": "klt"}, "ring1", "batch")
        self.assertEqual(argv, ["klt", *item7.KLT_PEX_ARGS, "--backend", "batch"])

    def test_empty_backend_is_not_appended(self):
        argv, _ = self.argv({"KLT": "klt"}, "ring1", "")
        self.assertNotIn("--backend", argv)

    def test_multi_word_klt_is_split(self):
        argv, _ = self.argv({"KLT": "uvx --from klayout-tools==0.6.0 klt"}, "ring1", "local")
        self.assertEqual(argv[:5], ["uvx", "--from", "klayout-tools==0.6.0", "klt", "pex"])
        self.assertEqual(argv[-2:], ["--backend", "local"])

    def test_ring2_uses_its_own_args_and_scratch(self):
        argv, _ = self.argv({"KLT": "klt"}, "ring2", "batch")
        self.assertEqual(argv, ["klt", *item7.RING2_KLT_PEX_ARGS, "--backend", "batch"])
        self.assertTrue(item7.RING2_SCRATCH.name.endswith("ring2-pex"))

    def test_stdout_goes_to_the_response_file(self):
        with mock.patch.dict(os.environ, {"KLT": "klt"}), mock.patch.object(common.subprocess, "run") as run, \
                mock.patch.object(item7, "RING2_SCRATCH", self.root / "r2"):
            out, _ = self.run_quiet(item7.run_pex, "ring2")
        self.assertEqual(out, self.root / "r2" / "klt_pex_response.json")
        self.assertEqual(run.call_args.kwargs["stdout"].name, str(out))


class Item7Refusals(Scratch):
    mod = item7

    def args(self, **kw):
        base = dict(envelope=None, backend=None, allow_incomplete=False, ring="ring1")
        return SimpleNamespace(**{**base, **kw})

    def test_ring1_stale_dut_runs_nothing(self):
        with mock.patch.object(check, "item7_analog_dut_source_problems", return_value=["stale"]), \
                mock.patch.object(common.subprocess, "run") as run, \
                mock.patch.object(sys, "argv", ["publish_item7_analog.py"]):
            rc, err = self.run_quiet(item7.main)
        self.assertEqual(rc, 1)
        run.assert_not_called()
        self.assertIn("nothing run", err)

    def test_ring2_stale_fixture_runs_nothing(self):
        with mock.patch.object(check, "item7_analog_dut_source_problems", return_value=[]), \
                mock.patch.object(check, "ring2_request_problems", return_value=["old request"]), \
                mock.patch.object(common.subprocess, "run") as run:
            rc, err = self.run_quiet(item7.publish_ring2, self.args(ring="ring2"))
        self.assertEqual(rc, 1)
        run.assert_not_called()
        self.assertIn("nothing run", err)
        self.assertIn("old request", err)

    def ring2(self, envelope, *, netlist=True, **argkw):
        env_file = self.write("in.json", json.dumps(envelope))
        if netlist:
            self.write(check.RING2_NETLIST)
        else:
            (self.root / check.RING2_NETLIST).unlink(missing_ok=True)
        with mock.patch.object(check, "item7_analog_dut_source_problems", return_value=[]), \
                mock.patch.object(check, "ring2_request_problems", return_value=[]):
            return self.run_quiet(item7.publish_ring2, self.args(envelope=env_file, **argkw))

    def test_ring2_pex_failure_publishes_nothing(self):
        boom = subprocess.CalledProcessError(3, ["klt"])
        with mock.patch.object(check, "item7_analog_dut_source_problems", return_value=[]), \
                mock.patch.object(check, "ring2_request_problems", return_value=[]), \
                mock.patch.object(item7, "run_pex", side_effect=boom):
            rc, err = self.run_quiet(item7.publish_ring2, self.args())
        self.assertEqual(rc, 1)
        self.assertIn("nothing published", err)
        self.assertFalse((self.root / check.RING2_ENVELOPE).exists())

    def test_ring2_refuses_wrong_klt_build_mismatch_and_missing_netlist(self):
        for env, netlist, text in (
            (_envelope("0.0.1"), True, "not the producer pin"),
            (_envelope(pin_count_mismatch={"d": 1}), True, "pin_count_mismatch"),
            (_envelope(flat_dut_mismatch={"d": 1}), True, "flat_dut_mismatch"),
            (_envelope(), False, "is missing"),
        ):
            with self.subTest(text=text):
                rc, err = self.ring2(env, netlist=netlist)
                self.assertEqual(rc, 1)
                self.assertIn("refusing to publish ring2", err)
                self.assertIn(text, err)
                self.assertFalse((self.root / check.RING2_ENVELOPE).exists())
                self.assertFalse((self.root / check.RING2_PUBLICATION).exists())

    def test_ring2_failed_check_restores_previous_envelope(self):
        dest = self.write(check.RING2_ENVELOPE, "previous")
        with mock.patch.object(item7, "build_ring2_publication", return_value={"verdict": VERDICT}), \
                mock.patch.object(check, "item7_analog_problems", return_value=["bad"]):
            rc, err = self.ring2(_envelope())
        self.assertEqual(rc, 1)
        self.assertIn("envelope not written", err)
        self.assertEqual(dest.read_text(), "previous")
        self.assertFalse((self.root / check.RING2_PUBLICATION).exists())

    def test_ring2_builder_exception_removes_new_envelope(self):
        with mock.patch.object(item7, "build_ring2_publication", side_effect=KeyError("k")):
            rc, err = self.ring2(_envelope())
        self.assertEqual(rc, 1)
        self.assertIn("KeyError", err)
        self.assertFalse((self.root / check.RING2_ENVELOPE).exists())

    def test_ring2_incomplete_needs_allow_incomplete(self):
        incomplete = {"verdict": {"verdict": "incomplete", "counts": {"unmeasured": 2}}}
        for allow, rc_want in ((False, 1), (True, 0)):
            with self.subTest(allow=allow), \
                    mock.patch.object(item7, "build_ring2_publication", return_value=dict(incomplete, body_bias_status="u")), \
                    mock.patch.object(check, "item7_analog_problems", return_value=[]):
                rc, err = self.ring2(_envelope(), allow_incomplete=allow)
                self.assertEqual(rc, rc_want)
                self.assertEqual((self.root / check.RING2_PUBLICATION).exists(), allow)
                self.assertEqual("incomplete" in err, not allow)
                (self.root / check.RING2_PUBLICATION).unlink(missing_ok=True)

    def test_ring2_backend_recorded_only_for_a_run_not_an_envelope(self):
        seen = []

        def fake(envelope, raw_sha, backend):
            seen.append(backend)
            return {"verdict": VERDICT, "body_bias_status": "u"}

        with mock.patch.object(item7, "build_ring2_publication", side_effect=fake), \
                mock.patch.object(check, "item7_analog_problems", return_value=[]):
            self.assertEqual(self.ring2(_envelope(), backend="batch")[0], 0)
        self.assertEqual(seen, [None])


class Item7Publication(Scratch):
    mod = item7

    def test_ring2_publication_fields(self):
        bd = mock.Mock(RING2="r2")
        bd.source_identity.return_value = {"sec": "h"}
        bd.extraction_port_map.return_value = {"a": "b"}
        for rel in check.RING2_INPUTS:
            self.write(rel, rel)
        self.write(check.RING2_NETLIST, "netlist")
        self.write(check.RING2_INPUTS[0], "{}")
        with mock.patch.object(item7, "_build_dut", return_value=bd), \
                mock.patch.object(check, "combiner_sampler_verdict", return_value=VERDICT) as verdict:
            pub = item7.build_ring2_publication(_envelope(), "sha256:feed", "batch")
        verdict.assert_called_once_with(_envelope(), {})
        bd.source_identity.assert_called_once_with(ring="r2")
        self.assertEqual(pub["schema"], check.RING2_PUBLICATION_SCHEMA)
        self.assertEqual(pub["producer"], "klt " + " ".join(item7.RING2_KLT_PEX_ARGS))
        self.assertEqual(pub["producer_build"], check.KLT_PIN)
        self.assertEqual(pub["backend_requested"], "batch")
        self.assertEqual(pub["layout_content_hash"], "sha256:" + "ab" * 32)
        self.assertEqual(set(pub["inputs_sha256"]), set(check.RING2_INPUTS))
        for digest in pub["inputs_sha256"].values():
            self.assertRegex(digest, r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(pub["verdict"], VERDICT)
        self.assertEqual(pub["body_bias_status"], "unbiased")
        self.assertEqual(pub["body_bias_unbiased_device_count"], 7)
        self.assertEqual(pub["envelope"], {"file": check.RING2_ENVELOPE, "sha256": "sha256:feed"})
        self.assertEqual(pub["port_map"], {"a": "b"})
        json.dumps(pub)

    def test_ring2_backend_none_passes_through(self):
        bd = mock.Mock(RING2="r2")
        for rel in check.RING2_INPUTS:
            self.write(rel, "{}")
        self.write(check.RING2_NETLIST)
        with mock.patch.object(item7, "_build_dut", return_value=bd), \
                mock.patch.object(check, "combiner_sampler_verdict", return_value=VERDICT):
            pub = item7.build_ring2_publication({}, "sha256:0", None)
        self.assertIsNone(pub["backend_requested"])
        self.assertIsNone(pub["body_bias_status"])


class CombinerSamplerRunPex(Scratch):
    mod = cs

    def argv(self, env, backend):
        with mock.patch.dict(os.environ, env), mock.patch.object(common.subprocess, "run") as run:
            self.run_quiet(cs.run_pex, backend)
        self.assertEqual(run.call_count, 1)
        return run.call_args.args[0], run.call_args.kwargs

    def test_backend_is_always_appended(self):
        argv, kw = self.argv({"KLT": "klt"}, "local")
        self.assertEqual(argv, ["klt", *cs.KLT_PEX_ARGS, "--backend", "local"])
        self.assertEqual(kw["cwd"], self.root)
        self.assertTrue(kw["check"])

    def test_multi_word_klt_is_split(self):
        argv, _ = self.argv({"KLT": "uvx --from klayout-tools==0.6.0 --with klayout==0.30.10 klt"}, "batch")
        self.assertEqual(argv[:7], ["uvx", "--from", "klayout-tools==0.6.0", "--with", "klayout==0.30.10",
                                    "klt", "pex"])
        self.assertEqual(argv[-2:], ["--backend", "batch"])

    def test_default_klt_when_unset(self):
        env = {k: v for k, v in os.environ.items() if k != "KLT"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(common.subprocess, "run") as run:
            self.run_quiet(cs.run_pex, "local")
        self.assertEqual(run.call_args.args[0][0], "klt")


class CombinerSamplerMain(Scratch):
    mod = cs

    def main(self, argv, env=None, *, stale=(), run_pex=None):
        base = {k: v for k, v in os.environ.items() if k != "KLT_SIM_BACKEND"}
        base.update(env or {})
        with mock.patch.dict(os.environ, base, clear=True), \
                mock.patch.object(check, "combiner_sampler_dut_source_problems", return_value=list(stale)):
            if run_pex is None:
                return self.run_quiet(cs.main, argv)
            with mock.patch.object(cs, "run_pex", run_pex):
                return self.run_quiet(cs.main, argv)

    def test_stale_fixture_runs_nothing(self):
        with mock.patch.object(common.subprocess, "run") as run:
            rc, err = self.main([], stale=["stale dut"])
        self.assertEqual(rc, 1)
        run.assert_not_called()
        self.assertIn("nothing run", err)
        self.assertIn("stale dut", err)

    def test_backend_defaults_to_env_else_local(self):
        boom = subprocess.CalledProcessError(2, ["klt"])
        for env, want in (({}, "local"), ({"KLT_SIM_BACKEND": "batch"}, "batch")):
            with self.subTest(env=env):
                run_pex = mock.Mock(side_effect=boom)
                self.main([], env, run_pex=run_pex)
                run_pex.assert_called_once_with(want)
        run_pex = mock.Mock(side_effect=boom)
        self.main(["--backend", "x"], {"KLT_SIM_BACKEND": "batch"}, run_pex=run_pex)
        run_pex.assert_called_once_with("x")

    def test_pex_failure_publishes_nothing(self):
        run_pex = mock.Mock(side_effect=subprocess.CalledProcessError(4, ["klt"]))
        rc, err = self.main([], run_pex=run_pex)
        self.assertEqual(rc, 1)
        self.assertIn("nothing published", err)
        self.assertFalse((self.root / check.CS_ENVELOPE).exists())

    def with_envelope(self, envelope, argv=(), *, netlist=True):
        env_file = self.write("in.json", json.dumps(envelope))
        if netlist:
            self.write(check.CS_NETLIST)
        else:
            (self.root / check.CS_NETLIST).unlink(missing_ok=True)
        return self.main(["--envelope", str(env_file), *argv])

    def test_refusals_leave_destination_unwritten(self):
        for env, netlist, text in (
            (_envelope("0.0.1"), True, "not the producer pin"),
            (_envelope(pin_count_mismatch={"d": 1}), True, "pin_count_mismatch"),
            (_envelope(flat_dut_mismatch={"d": 1}), True, "flat_dut_mismatch"),
            (_envelope(), False, "is missing"),
        ):
            with self.subTest(text=text):
                rc, err = self.with_envelope(env, netlist=netlist)
                self.assertEqual(rc, 1)
                self.assertIn("refusing to publish", err)
                self.assertIn(text, err)
                self.assertFalse((self.root / check.CS_ENVELOPE).exists())

    def test_failed_check_restores_previous_envelope(self):
        dest = self.write(check.CS_ENVELOPE, "previous")
        with mock.patch.object(cs, "build_publication", return_value={"verdict": VERDICT}), \
                mock.patch.object(check, "combiner_sampler_problems", return_value=["bad"]):
            rc, err = self.with_envelope(_envelope())
        self.assertEqual(rc, 1)
        self.assertIn("envelope not written", err)
        self.assertEqual(dest.read_text(), "previous")
        self.assertFalse((self.root / check.CS_PUBLICATION).exists())

    def test_builder_exception_removes_new_envelope(self):
        with mock.patch.object(cs, "build_publication", side_effect=ValueError("v")):
            rc, err = self.with_envelope(_envelope())
        self.assertEqual(rc, 1)
        self.assertIn("ValueError", err)
        self.assertFalse((self.root / check.CS_ENVELOPE).exists())

    def test_incomplete_needs_allow_incomplete(self):
        pub = {"verdict": {"verdict": "incomplete", "counts": {"unmeasured": 1}}, "body_bias_status": "u"}
        for flags, rc_want in (([], 1), (["--allow-incomplete"], 0)):
            with self.subTest(flags=flags), \
                    mock.patch.object(cs, "build_publication", return_value=dict(pub)), \
                    mock.patch.object(check, "combiner_sampler_problems", return_value=[]):
                rc, _ = self.with_envelope(_envelope(), flags)
                self.assertEqual(rc, rc_want)
                self.assertEqual((self.root / check.CS_PUBLICATION).exists(), rc_want == 0)
                (self.root / check.CS_PUBLICATION).unlink(missing_ok=True)

    def test_backend_recorded_only_for_a_run_not_an_envelope(self):
        seen = []

        def fake(envelope, raw_sha, backend):
            seen.append(backend)
            return {"verdict": VERDICT, "body_bias_status": "u"}

        with mock.patch.object(cs, "build_publication", side_effect=fake), \
                mock.patch.object(check, "combiner_sampler_problems", return_value=[]):
            self.assertEqual(self.with_envelope(_envelope(), ["--backend", "batch"])[0], 0)
            produced = self.write("sim/run.json", json.dumps(_envelope()))
            rc, _ = self.main([], {"KLT_SIM_BACKEND": "batch"}, run_pex=mock.Mock(return_value=produced))
        self.assertEqual(rc, 0)
        self.assertEqual(seen, [None, "batch"])
        self.assertTrue((self.root / check.CS_PUBLICATION).is_file())


class CombinerSamplerPublication(Scratch):
    mod = cs

    def test_publication_fields(self):
        bd = mock.Mock()
        bd.extracted_graph.return_value = (None, ["p1", "p2"])
        bd.extraction_port_map.return_value = ["n1", "n2"]
        bd.DUT.read_text.return_value = "dut"
        bd.source_identity.return_value = {"sec": "h"}
        for rel in check.CS_INPUTS:
            self.write(rel, "{}")
        self.write(check.CS_NETLIST, "netlist")
        with mock.patch.object(check, "_load_tb_module", return_value=bd), \
                mock.patch.object(check, "combiner_sampler_verdict", return_value=VERDICT):
            pub = cs.build_publication(_envelope(), "sha256:feed", "batch")
        bd.extraction_port_map.assert_called_once_with("netlist", "dut")
        self.assertEqual(pub["schema"], check.CS_PUBLICATION_SCHEMA)
        self.assertEqual(pub["producer"], "klt " + " ".join(cs.KLT_PEX_ARGS))
        self.assertEqual(pub["producer_build"], check.KLT_PIN)
        self.assertEqual(pub["backend_requested"], "batch")
        self.assertEqual(pub["layout_content_hash"], "sha256:" + "ab" * 32)
        self.assertEqual(set(pub["inputs_sha256"]), set(check.CS_INPUTS))
        self.assertEqual(pub["port_map"], {"p1": "n1", "p2": "n2"})
        self.assertEqual(pub["verdict"], VERDICT)
        self.assertEqual(pub["body_bias_status"], "unbiased")
        self.assertEqual(pub["body_bias_unbiased_device_count"], 7)
        self.assertEqual(pub["envelope"], {"file": check.CS_ENVELOPE, "sha256": "sha256:feed"})
        json.dumps(pub)


if __name__ == "__main__":
    unittest.main()
