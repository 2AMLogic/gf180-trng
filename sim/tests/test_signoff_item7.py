"""Item 7 (digital) publication gate: stale or failing evidence is rejected."""

import contextlib
import copy
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("signoff_check", ROOT / "signoff" / "check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

pub_spec = importlib.util.spec_from_file_location(
    "signoff_publish_item7", ROOT / "signoff" / "publish_item7.py"
)
publish = importlib.util.module_from_spec(pub_spec)
sys.modules.setdefault("check", check)  # publish_item7 does `import check`
pub_spec.loader.exec_module(publish)

TB = ROOT / "sim" / "tb" / "trng-top-post-route"
inv_spec = importlib.util.spec_from_file_location(
    "input_inventory", TB / "input_inventory.py"
)
input_inventory = importlib.util.module_from_spec(inv_spec)
inv_spec.loader.exec_module(input_inventory)

STEM = "2099-01-01-trng-top-post-route-01"
STEM_OLD = "2098-01-01-trng-top-post-route-01"


class Item7Publication(unittest.TestCase):
    def setUp(self):
        self.pub = json.loads((ROOT / check.ITEM7_PUBLICATION).read_text())
        self.env = json.loads((ROOT / check.ITEM7_ENVELOPE).read_text())

    def test_committed_publication_is_current(self):
        self.assertEqual(check.item7_problems(self.pub, self.env), [])

    def test_stale_netlist_rejected(self):
        pub = copy.deepcopy(self.pub)
        pub["netlist"]["sha256"] = "sha256:" + "0" * 64
        self.assertTrue(any("netlist: STALE" in p for p in check.item7_problems(pub, self.env)))

    def test_stale_sdf_rejected(self):
        pub = copy.deepcopy(self.pub)
        pub["sdf"]["sha256"] = "sha256:" + "0" * 64
        self.assertTrue(any("sdf: STALE" in p for p in check.item7_problems(pub, self.env)))

    def test_unannotated_or_failed_response_rejected(self):
        env = copy.deepcopy(self.env)
        env["environment"]["sdf"]["annotated"] = False
        self.assertTrue(check.item7_problems(self.pub, env))
        env = copy.deepcopy(self.env)
        env["status"] = "fail"
        self.assertTrue(check.item7_problems(self.pub, env))

    def test_changed_raw_evidence_rejected(self):
        pub = copy.deepcopy(self.pub)
        pub["raw_sha256"]["verdict.json"] = "sha256:" + "0" * 64
        self.assertTrue(any("verdict.json" in p for p in check.item7_problems(pub, self.env)))


class Item7SourcePinning(unittest.TestCase):
    """RTL / header / stimulus / model freshness, on a scratch repository."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        r = self.tmp
        for rel, text in {
            check.ITEM7_NETLIST: "module n; endmodule\n",
            check.ITEM7_SDF: "(DELAYFILE)\n",
            "design/interface/trng_interface.v": '`include "trng_regmap.vh"\nmodule i; endmodule\n',
            "design/interface/trng_regmap.vh": "`define REG 1\n",
            "design/trng_top/trng_top.v": "module t; endmodule\n",
            "design/trng_top/trng_top.py": "MODEL = 1\n",
            "sim/tb/trng-top-post-route/scenarios.py": "SCEN = 1\n",
        }.items():
            (r / rel).parent.mkdir(parents=True, exist_ok=True)
            (r / rel).write_text(text)
        self.rel_sources = [
            "design/interface/trng_interface.v",
            "design/interface/trng_regmap.vh",
            "design/trng_top/trng_top.v",
            "design/trng_top/trng_top.py",
            "sim/tb/trng-top-post-route/scenarios.py",
        ]
        self.old = {}
        for k, v in (
            ("REPO_ROOT", r), ("MANIFEST", r / "signoff" / "manifest.json"),
        ):
            self.old[k] = getattr(check, k)
            setattr(check, k, v)
        self.old_pub_root = publish.REPO_ROOT
        publish.REPO_ROOT = r
        self.addCleanup(self._restore)
        check.MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        check.MANIFEST.write_text(json.dumps({"evidence": {}}))
        self.run_a = self._make_run(STEM)

    def _restore(self):
        for k, v in self.old.items():
            setattr(check, k, v)
        publish.REPO_ROOT = self.old_pub_root

    def _make_run(self, stem, with_sources=True):
        r = self.tmp
        raw = r / "sim" / "records" / "raw" / stem
        raw.mkdir(parents=True)
        envelope = {
            "status": "pass", "failed_count": 0,
            "environment": {"sdf": {"annotated": True}},
        }
        files = {
            "gate_klt_response.json": envelope,
            "rtl_klt_response.json": {"status": "pass"},
            "verdict.json": {"pass": True, "checks": {"equivalent": True}},
        }
        for name in check.ITEM7_RAW_FILES:
            if name == "sources.json":
                continue
            (raw / name).write_text(json.dumps(files.get(name, {"name": name})))
        if with_sources:
            (raw / "sources.json").write_text(json.dumps({
                "schema": "gf180-trng/post-route-sources/1",
                "files": {rel: check.sha256_file(r / rel) for rel in self.rel_sources},
            }))
        (r / "sim" / "records" / f"{stem}.md").write_text(
            "netlist:\n"
            f"  sha256: {check.sha256_file(r / check.ITEM7_NETLIST)[7:]}\n"
            f"  sdf_sha256: {check.sha256_file(r / check.ITEM7_SDF)[7:]}\n"
        )
        return raw

    def _publish(self, raw):
        err = io.StringIO()
        old_argv = sys.argv
        sys.argv = ["publish_item7.py", str(raw)]
        try:
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                rc = publish.main()
        finally:
            sys.argv = old_argv
        return rc, err.getvalue()

    def _state(self):
        r = self.tmp
        return {
            p: (r / p).read_bytes() if (r / p).exists() else None
            for p in (check.ITEM7_PUBLICATION, check.ITEM7_ENVELOPE, "signoff/manifest.json")
        }

    def _problems(self):
        r = self.tmp
        return check.item7_problems(
            json.loads((r / check.ITEM7_PUBLICATION).read_text()),
            json.loads((r / check.ITEM7_ENVELOPE).read_text()),
        )

    def _publish_ok(self, raw):
        rc, err = self._publish(raw)
        self.assertEqual(rc, 0, err)

    def test_current_publication_passes(self):
        self._publish_ok(self.run_a)
        self.assertEqual(self._problems(), [])

    def test_each_mutated_input_is_stale_with_outputs_unchanged(self):
        self._publish_ok(self.run_a)
        before_pub = self._state()
        for rel in self.rel_sources:  # RTL, included header, model, scenario
            with self.subTest(rel=rel):
                path = self.tmp / rel
                orig = path.read_bytes()
                path.write_bytes(orig + b"// changed\n")
                try:
                    problems = self._problems()
                finally:
                    path.write_bytes(orig)
                self.assertEqual(
                    [p for p in problems if "STALE" in p],
                    [p for p in problems if f"source {rel}: STALE" in p],
                )
                self.assertTrue(any(f"source {rel}: STALE" in p for p in problems))
                # netlist, SDF and raw outputs are untouched by the mutation
                self.assertFalse(any(p.startswith(("netlist", "sdf", "raw")) for p in problems))
        self.assertEqual(self._problems(), [])
        self.assertEqual(self._state(), before_pub)

    def test_missing_source_is_rejected(self):
        self._publish_ok(self.run_a)
        (self.tmp / "design/interface/trng_regmap.vh").unlink()
        self.assertTrue(any("trng_regmap.vh: missing" in p for p in self._problems()))

    def test_publication_without_sources_rejected(self):
        self._publish_ok(self.run_a)
        pub = json.loads((self.tmp / check.ITEM7_PUBLICATION).read_text())
        env = json.loads((self.tmp / check.ITEM7_ENVELOPE).read_text())
        del pub["sources"]
        self.assertTrue(any("no source inventory" in p for p in check.item7_problems(pub, env)))
        pub["sources"] = {}
        self.assertTrue(any("no source inventory" in p for p in check.item7_problems(pub, env)))

    def test_publication_sources_must_match_raw_sources_json(self):
        self._publish_ok(self.run_a)
        pub = json.loads((self.tmp / check.ITEM7_PUBLICATION).read_text())
        env = json.loads((self.tmp / check.ITEM7_ENVELOPE).read_text())
        del pub["sources"][self.rel_sources[0]]
        self.assertTrue(any("sources.json" in p for p in check.item7_problems(pub, env)))

    def test_older_run_after_input_change_is_refused_without_writes(self):
        self._publish_ok(self.run_a)
        before = self._state()
        old_run = self._make_run(STEM_OLD)
        (self.tmp / "design/interface/trng_regmap.vh").write_text("`define REG 2\n")
        rc, err = self._publish(old_run)
        self.assertNotEqual(rc, 0)
        self.assertIn("STALE", err)
        self.assertEqual(self._state(), before)

    def test_run_predating_source_pinning_is_refused(self):
        raw = self._make_run("2097-01-01-trng-top-post-route-01", with_sources=False)
        rc, err = self._publish(raw)
        self.assertNotEqual(rc, 0)
        self.assertIn("sources.json", err)
        self.assertFalse((self.tmp / check.ITEM7_PUBLICATION).exists())

    def test_rerun_and_publish_restores_freshness(self):
        self._publish_ok(self.run_a)
        (self.tmp / "design/trng_top/trng_top.py").write_text("MODEL = 2\n")
        self.assertTrue(self._problems())
        new_run = self._make_run("2099-02-01-trng-top-post-route-01")
        self._publish_ok(new_run)
        self.assertEqual(self._problems(), [])


class Item7InventoryIsDerived(unittest.TestCase):
    """The run's inventory comes from its real inputs, not a second list."""

    def test_real_inventory_follows_includes_and_imports(self):
        d = ROOT
        rtl = [d / "design/trng_top/trng_top.v", d / "design/interface/trng_interface.v"]
        files = input_inventory.collect(
            ROOT, rtl, [d / "design/interface"],
            [d / "design/trng_top/trng_top.py", TB / "scenarios.py"],
            [TB / "run_demo.py"],
        )
        for rel in (
            "design/interface/trng_regmap.vh",      # `include'd header
            "design/interface/regmap.py",           # model import
            "design/conditioner/crc32_conditioner.py",
            "sim/tb/conditioner-crc32/source_model.py",  # scenario import
            "sim/harness/bits.py",
            "sim/tb/trng-top-post-route/run_demo.py",
        ):
            self.assertIn(rel, files)
        self.assertTrue(all(v.startswith("sha256:") for v in files.values()))

    def test_unresolvable_include_is_an_error(self):
        with tempfile.TemporaryDirectory() as t:
            v = Path(t) / "a.v"
            v.write_text('`include "nope.vh"\n')
            with self.assertRaises(FileNotFoundError):
                input_inventory.collect(Path(t), [v], [], [], [])


if __name__ == "__main__":
    unittest.main()
