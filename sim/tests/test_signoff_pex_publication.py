"""The freshness checks shared by the `klt pex` publications, offline.

No klt, ngspice or PDK. item7_analog_problems() (ring1, the cited 7.analog
run, and ring2) and combiner_sampler_problems() judge the same kinds of
artifact -- a sidecar publication, its envelope, the extracted netlist and the
pinned testbench inputs -- so every check one of them owns is held here
through each wrapper that owns it: break one committed artifact, name the
diagnostic. Ring1 owns the fewest: it states no schema, layout pin or verdict
(the manifest pins its layout, and the strict completeness check stands in
for a recorded verdict).
"""

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
from sim.tools.pathload import load_module_from_path  # noqa: E402  (#553)

check = load_module_from_path("signoff_check", ROOT / "signoff" / "check.py")

ALL = ("ring1", "ring2", "combiner_sampler")
#: The publications built by publish_common.build_publication, which record a schema,
#: their layout hash and a verdict; ring1's older publication records none.
BUILD_PUBLICATIONS = ("ring2", "combiner_sampler")
DIGEST_PROBLEM = "published envelope differs from the sha256 in publication.json"
OTHER_HASH = "sha256:" + "0" * 64

#: What each wrapper judges. `schema`, `gds` and `request` are None for the
#: checks a wrapper does not own.
FIXTURES = {
    "ring1": dict(
        problems=lambda pub, env: check.item7_analog_problems(pub, env),
        publication=check.ITEM7A_PUBLICATION, envelope=check.ITEM7A_ENVELOPE,
        netlist=check.ITEM7A_NETLIST, inputs=check.ITEM7A_INPUTS,
        publisher="signoff/publish_item7_analog.py",
        schema=None, gds=None, request=None,
    ),
    "ring2": dict(
        problems=lambda pub, env: check.item7_analog_problems(pub, env, "ring2"),
        publication=check.RING2_PUBLICATION, envelope=check.RING2_ENVELOPE,
        netlist=check.RING2_NETLIST, inputs=check.RING2_INPUTS,
        publisher="signoff/publish_item7_analog.py --ring ring2",
        schema=check.RING2_PUBLICATION_SCHEMA, gds=check.RING2_GDS, request=check.RING2_INPUTS[0],
    ),
    "combiner_sampler": dict(
        problems=check.combiner_sampler_problems,
        publication=check.CS_PUBLICATION, envelope=check.CS_ENVELOPE,
        netlist=check.CS_NETLIST, inputs=check.CS_INPUTS,
        publisher="signoff/publish_combiner_sampler_pex.py",
        schema=check.CS_PUBLICATION_SCHEMA, gds=check.CS_GDS, request=check.CS_REQUEST,
    ),
}


def _committed(fixture: dict) -> tuple[dict, dict]:
    pub = json.loads((ROOT / fixture["publication"]).read_text())
    return pub, json.loads((ROOT / fixture["envelope"]).read_text())


def _without_envelope_file(fixture: dict, pub: dict, env: dict) -> list[str]:
    """The wrapper's problems for (pub, env) as if its envelope were not on disk."""
    hidden = ROOT / fixture["envelope"]
    is_file = Path.is_file

    def hiding(self, **kwargs):
        return False if self == hidden else is_file(self, **kwargs)

    with mock.patch.object(Path, "is_file", hiding):
        return fixture["problems"](pub, env)


class SharedPexPublicationChecks(unittest.TestCase):
    def assertReported(self, break_it, expected, *owners):
        """`expected` -- a string, or a callable on (fixture, publication, envelope) --
        is reported by every owner once `break_it` has run."""
        for name in owners:
            fixture = FIXTURES[name]
            with self.subTest(fixture=name):
                pub, env = _committed(fixture)
                break_it(pub, env, fixture)
                want = expected(fixture, pub, env) if callable(expected) else expected
                self.assertIn(want, fixture["problems"](pub, env))

    def test_committed_publications_are_current(self):
        for name in ALL:
            with self.subTest(fixture=name):
                pub, env = _committed(FIXTURES[name])
                self.assertEqual(FIXTURES[name]["problems"](pub, env), [])

    def test_schema_must_be_the_publication_schema(self):
        def break_it(pub, env, fixture):
            pub["schema"] = "gf180-trng/other/1"
        self.assertReported(
            break_it,
            lambda fx, pub, env: f"publication schema is 'gf180-trng/other/1', not {fx['schema']!r}",
            *BUILD_PUBLICATIONS,
        )

    def test_envelope_must_name_the_fixture_layout(self):
        def break_it(pub, env, fixture):
            env["layout"]["path"] = "layout/other.gds"
        self.assertReported(
            break_it, lambda fx, pub, env: f"envelope layout is 'layout/other.gds', not {fx['gds']}", *BUILD_PUBLICATIONS
        )

    def test_envelope_must_pin_the_committed_layout(self):
        def break_it(pub, env, fixture):
            env["provenance"]["input"]["content_hash"] = OTHER_HASH
        self.assertReported(
            break_it,
            lambda fx, pub, env: f"{fx['gds']} is not the layout this klt pex run extracted (re-run and re-publish)",
            *BUILD_PUBLICATIONS,
        )
        self.assertReported(break_it, "publication layout_content_hash differs from the envelope's", *BUILD_PUBLICATIONS)

    def test_publication_layout_hash_must_be_the_envelope_s(self):
        def break_it(pub, env, fixture):
            pub["layout_content_hash"] = OTHER_HASH
        self.assertReported(break_it, "publication layout_content_hash differs from the envelope's", *BUILD_PUBLICATIONS)

    def test_run_must_be_a_testbench_run_without_a_pin_or_flat_dut_mismatch(self):
        def not_testbench(pub, env, fixture):
            env["measurement"]["mode"] = "caller"
        self.assertReported(not_testbench, "klt pex measurement.mode is not 'testbench'", *ALL)
        for key in ("pin_count_mismatch", "flat_dut_mismatch"):

            def mismatched(pub, env, fixture, key=key):
                env[key] = {"detail": "x"}

            self.assertReported(mismatched, f"klt pex reports {key}", *ALL)

    def test_recorded_verdict_must_be_what_the_envelope_and_request_yield(self):
        def reworded(pub, env, fixture):
            pub["verdict"]["verdict"] = "pass" if pub["verdict"]["verdict"] != "pass" else "fail"
        self.assertReported(reworded, "recorded verdict is not what the envelope and request yield today", *BUILD_PUBLICATIONS)

        def undeclared(pub, env, fixture):
            env["delta"].append(dict(env["delta"][0], corner_id="tt/1.800V/27C"))
        self.assertReported(undeclared, "verdict: response carries undeclared corners: ['tt/1.800V/27C']", *BUILD_PUBLICATIONS)

    def test_body_bias_status_must_be_stated_as_the_envelope_does(self):
        def contradicted(pub, env, fixture):
            pub["body_bias_status"] = "unbiased" if env["body_bias"]["status"] == "biased" else "biased"
        self.assertReported(
            contradicted,
            lambda fx, pub, env: (
                f"publication.json states body_bias_status {pub['body_bias_status']!r}, "
                f"the envelope says {env['body_bias']['status']!r}"
            ),
            *ALL,
        )

        def no_block(pub, env, fixture):
            del env["body_bias"]
        self.assertReported(no_block, "envelope carries no body_bias block", *ALL)

    def test_netlist_must_be_the_one_the_run_extracted(self):
        def break_it(pub, env, fixture):
            env["extraction"]["netlist_sha256"] = "0" * 64
        self.assertReported(
            break_it, lambda fx, pub, env: f"{fx['netlist']} is not the netlist this klt pex run extracted", *ALL
        )

    def test_every_input_must_be_pinned_at_its_current_hash(self):
        def stale(pub, env, fixture):
            pub["inputs_sha256"][fixture["inputs"][0]] = OTHER_HASH
        self.assertReported(
            stale,
            lambda fx, pub, env: (
                f"input {fx['inputs'][0]}: STALE -- the run used {OTHER_HASH}, it hashes to "
                f"{check.sha256_file(ROOT / fx['inputs'][0])} today; re-run {fx['publisher']}"
            ),
            *ALL,
        )

        def unpinned(pub, env, fixture):
            del pub["inputs_sha256"][fixture["inputs"][0]]
        self.assertReported(unpinned, lambda fx, pub, env: f"input {fx['inputs'][0]}: not pinned or missing", *ALL)

    def test_published_envelope_must_match_the_pinned_digest(self):
        def break_it(pub, env, fixture):
            pub["envelope"]["sha256"] = OTHER_HASH
        self.assertReported(break_it, DIGEST_PROBLEM, *ALL)

    def test_an_absent_envelope_file_is_a_digest_problem_only_for_the_combiner_sampler(self):
        """The one deliberate difference between the two gates: a ring gate has nothing to
        compare when its envelope is not on disk and stays silent; the combiner/sampler gate
        reports the digest problem."""
        for name in ALL:
            with self.subTest(fixture=name):
                pub, env = _committed(FIXTURES[name])
                got = _without_envelope_file(FIXTURES[name], pub, env)
                self.assertEqual(DIGEST_PROBLEM in got, name == "combiner_sampler", got)

    def test_combiner_sampler_port_map_must_come_from_the_committed_netlist(self):
        pub, env = _committed(FIXTURES["combiner_sampler"])
        pub["port_map"] = {}
        self.assertIn(
            "publication port_map differs from the one the committed netlist yields",
            check.combiner_sampler_problems(pub, env),
        )


if __name__ == "__main__":
    unittest.main()
