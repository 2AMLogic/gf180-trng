#!/usr/bin/env bash
# The single list of this repository's checks (issue #1000).
#
# `npm run check:ci`, `npm run check:all` and the CI workflow
# (.github/workflows/ci.yml, harness job) all run their checks by calling
# this script with a group name, so the list is written exactly once
# (operator ruling 2AMLogic/2am#7561: when a repository wants the same checks
# to run locally and in CI, the commands are written once, in a script in the
# repository, and the workflow calls that script). Before this script existed
# the list was written out three times -- here, the package.json chains and
# the ci.yml steps -- and sim/tests/test_check_script_parity.py existed only
# to hold the copies together; ci.yml's header records the drift that cost
# (issue #97).
#
# Usage: sim/check.sh <group>
#
#   ci    The PR-blocking set, in the forms that pass on a bare machine:
#         tool-aware steps (shell lint, DRC/LVS, floorplan, tap distance,
#         signoff, selftest) run their documented self-skip behaviour when
#         their tool is missing.
#   all   The local pre-commit gate: the same checks in their strict
#         --require-tools / --require-pdk forms, plus the checks that need
#         those tools outright (schematic netlist, synthesis, inventory
#         levers, SDF export, power intent).
#
# Two steps of the `ci` group have a form only the CI workflow uses; CI
# selects them through the environment rather than by keeping a second copy
# of the list:
#
#   SIM_CHECK_SHELL_STRICT=1        the shell-lint step runs with
#                                   --require-tools (shellcheck ships on the
#                                   CI runner, so a missing binary is a
#                                   failure, not a skip)
#   SIM_CHECK_EVIDENCE_BASE=<rev>   the evidence-history step compares
#                                   sim/records/ against <rev> (CI computes
#                                   it from the event: the PR base SHA or the
#                                   pushed-from SHA; unset, the tool's own
#                                   origin/main default applies)
#
# The individual `npm run check:*` entries stay in package.json: they are the
# named entry points that documentation and signoff/inventories.py cite, and
# every step below that has one invokes it by name.

set -euo pipefail

cd -- "$(dirname -- "$0")/.." || exit 1

# Print the step's banner, then run the step. A failing step exits non-zero
# with its banner as the last header printed, so a log still shows which
# check failed even though the caller (a CI job, an npm chain) shows one step.
step() {
    printf '== %s ==\n' "$1"
    shift
    "$@"
}

# The shell-lint step, in the form CI's environment selects.
shell_lint_step() {
    if [ "${SIM_CHECK_SHELL_STRICT:-0}" = "1" ]; then
        step "python3 -m sim.tools.lint_shell --require-tools" \
            python3 -m sim.tools.lint_shell --require-tools
    else
        step "npm run check:lint-shell" npm run check:lint-shell
    fi
}

# The evidence-history step, against CI's event-derived base when one is
# given and against the tool's origin/main default when not.
evidence_history_step() {
    if [ -n "${SIM_CHECK_EVIDENCE_BASE:-}" ]; then
        step "python3 sim/tools/verify_evidence_history.py --base $SIM_CHECK_EVIDENCE_BASE" \
            python3 sim/tools/verify_evidence_history.py --base "$SIM_CHECK_EVIDENCE_BASE"
    else
        step "npm run check:evidence-history" npm run check:evidence-history
    fi
}

# --- group: ci -- the PR-blocking set; `npm run check:ci` and the CI
# --- workflow's harness job run exactly this list.
ci_group() {
    step "npm run lint" npm run lint
    shell_lint_step
    step "npm run test" npm run test
    step "npm run test:layout" npm run test:layout
    step "npm run check:spec" npm run check:spec
    step "npm run check:record-checksums" npm run check:record-checksums
    step "npm run check:artifact-manifests" npm run check:artifact-manifests
    step "npm run check:regmap" npm run check:regmap
    step "npm run check:floorplan-netlist" npm run check:floorplan-netlist
    step "npm run check:fixtures" npm run check:fixtures
    step "npm run check:digital-input" npm run check:digital-input
    step "npm run check:layout" npm run check:layout
    step "npm run check:floorplan" npm run check:floorplan
    step "npm run check:digital-tap-distance" npm run check:digital-tap-distance
    step "npm run check:signoff" npm run check:signoff
    evidence_history_step
    step "npm run check:no-host-paths" npm run check:no-host-paths
    step "sim/selftest.sh" sim/selftest.sh
}

# --- group: all -- the local pre-commit gate; `npm run check:all` runs
# --- exactly this list.
all_group() {
    step "npm run lint" npm run lint
    step "python3 -m sim.tools.lint_shell --require-tools" \
        python3 -m sim.tools.lint_shell --require-tools
    step "npm run test" npm run test
    step "npm run test:layout" npm run test:layout
    step "npm run check:spec" npm run check:spec
    step "npm run check:record-checksums" npm run check:record-checksums
    step "npm run check:artifact-manifests" npm run check:artifact-manifests
    step "npm run check:regmap" npm run check:regmap
    step "npm run check:floorplan-netlist" npm run check:floorplan-netlist
    step "npm run check:fixtures" npm run check:fixtures
    evidence_history_step
    step "npm run check:no-host-paths" npm run check:no-host-paths
    step "npm run check:netlist" npm run check:netlist
    step "npm run check:digital-netlist" npm run check:digital-netlist
    step "npm run check:inventory-levers" npm run check:inventory-levers
    step "npm run check:digital-input" npm run check:digital-input
    step "npm run check:digital-sdf" npm run check:digital-sdf
    step "python3 layout/verify.py --require-tools" \
        python3 layout/verify.py --require-tools
    step "python3 layout/floorplan/floorplan.py --require-tools" \
        python3 layout/floorplan/floorplan.py --require-tools
    step "python3 layout/digital/tap_distance.py --check --require-tools" \
        python3 layout/digital/tap_distance.py --check --require-tools
    step "python3 signoff/check.py --require-tools" \
        python3 signoff/check.py --require-tools
    step "python3 sim/tools/power_intent_check.py --check --require-tools" \
        python3 sim/tools/power_intent_check.py --check --require-tools
    step "sim/selftest.sh --require-pdk" sim/selftest.sh --require-pdk
}

case "${1:-}" in
    ci) ci_group ;;
    all) all_group ;;
    *)
        echo "usage: sim/check.sh <group>  (groups: ci, all -- see the header of this file)" >&2
        exit 2
        ;;
esac
