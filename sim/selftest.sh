#!/usr/bin/env bash
#
# Harness acceptance test.
#
#   sim/selftest.sh                 unit tests + record-checksum check + smoke
#                                    run + corner-sanity check (no evidence
#                                    written)
#   sim/selftest.sh --record        also mint real evidence records under sim/records/
#   sim/selftest.sh --require-pdk   fail (instead of skipping) if ngspice/PDK are absent
#
# Exit codes: 0 pass (or skipped sim stage), 1 something failed.

set -uo pipefail

SIM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SIM_DIR}/.." && pwd)"

RECORD=0
REQUIRE_PDK=0
for arg in "$@"; do
  case "${arg}" in
    --record) RECORD=1 ;;
    --require-pdk) REQUIRE_PDK=1 ;;
    -h|--help) sed -n '2,10p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "unknown option: ${arg}" >&2; exit 1 ;;
  esac
done

echo "== 1/5 harness unit tests (no PDK required) =="
if ! python3 -m unittest discover -s "${SIM_DIR}/tests" -t "${SIM_DIR}/tests"; then
  echo "FAIL: harness unit tests"
  exit 1
fi

echo
echo "== 2/5 record integrity (raw.files checksums, no PDK required) =="
# Every committed record must still hash to what it says it does. Catches a
# record whose raw output was overwritten after it was hashed -- e.g. by a
# second concurrent run_corners.py invocation handed an overlapping stem.
# --no-git here: this stage checks integrity, not commit state, so freshly
# minted (not yet `git add`ed) records do not fail an otherwise clean tree.
# The pre-commit form in sim/README.md keeps the commit-state check.
if ! python3 "${SIM_DIR}/tools/verify_record_checksums.py" --quiet --no-git; then
  echo "FAIL: record checksums do not match the raw output on disk"
  exit 1
fi

echo
echo "== 3/5 environment =="
if ! python3 "${SIM_DIR}/run_corners.py" --check-env; then
  if [ "${REQUIRE_PDK}" -eq 1 ]; then
    echo "FAIL: ngspice and/or the gf180mcu PDK are not available"
    exit 1
  fi
  echo
  echo "SKIP: simulation stages -- ngspice and/or the gf180mcu PDK are not available."
  echo "      Unit tests passed. Install the PDK (see the hint above) to run the"
  echo "      end-to-end smoke test and corner-sanity check."
  exit 0
fi

echo
echo "== 4/5 end-to-end smoke run (sim/tb/smoke-op) =="
if [ "${RECORD}" -eq 1 ]; then
  ok=1; python3 "${SIM_DIR}/run_corners.py" smoke-op || ok=0
else
  ok=1; python3 "${SIM_DIR}/run_corners.py" smoke-op --no-write || ok=0
fi
if [ "${ok}" -eq 0 ]; then
  echo "FAIL: smoke run"
  exit 1
fi

echo
echo "== 5/5 corner-sanity check (sim/tb/corner-sanity-nfet-id) =="
# Guards against a wrong or silently-ignored corner mapping (CLAUDE.md:
# a wrong corner mapping would pass a smoke test and contaminate every
# downstream evidence record). Runs tt/ss/ff at nominal supply, one
# temperature, and requires ss < tt < ff in device drive current --
# i.e. that switching the process corner actually moved the device.
if ! python3 "${SIM_DIR}/tools/corner_sanity_check.py"; then
  echo "FAIL: corner-sanity check -- process corner selection is not taking effect"
  exit 1
fi

if [ "${RECORD}" -eq 1 ]; then
  echo
  echo "== bonus: corner-sanity + seed-control evidence records =="
  python3 "${SIM_DIR}/run_corners.py" corner-sanity-nfet-id --corners tt ss ff --temps 27 --supply-tol 0 || exit 1
  python3 "${SIM_DIR}/run_corners.py" nfet-mismatch-seed --corners tt --temps 27 --supply-tol 0 --seeds 1 1 42 || exit 1
fi

echo
echo "PASS: harness is functional end to end."
