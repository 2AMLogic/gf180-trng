# gf180-trng -- one-command entry points for independent verification.
#
# Written for the Chipalooza Challenge #3 design-review bar (issue #203):
# "a shell script or a Makefile target such that full characterization can
# be done from a single command-line command." See the README's
# "Independent verification (Chipalooza)" section for prerequisites,
# expected wall-clock/core count, and what each target produces.
#
# All three targets below are thin wrappers over the existing sim/ harness
# (sim/run_corners.py, sim/selftest.sh, sim/characterize.py) and package.json
# npm scripts -- they add no new simulation logic of their own.

PYTHON ?= python3
JOBS ?= $(shell $(PYTHON) -c "import os; print(os.cpu_count() or 1)")

.PHONY: help smoke check characterize clean

help:
	@echo "gf180-trng make targets:"
	@echo ""
	@echo "  make check         unit tests + environment check (no PDK needed to start;"
	@echo "                     fails fast and clearly if ngspice/the PDK are missing)."
	@echo "  make smoke         harness acceptance test at one typical corner"
	@echo "                     (sim/selftest.sh) -- minutes, not hours."
	@echo "  make characterize  full ngspice PVT/corner campaign behind"
	@echo "                     docs/chipalooza/challenge-3-proposal.md's spec table;"
	@echo "                     writes evidence under sim/records/ per sim/README.md."
	@echo "                     JOBS=$(JOBS) by default (os.cpu_count()); override with"
	@echo "                     'make characterize JOBS=4'. Try 'make characterize-dry-run'"
	@echo "                     first to see the plan without running anything."
	@echo "  make characterize-dry-run"
	@echo "                     print the run_corners.py invocations 'make characterize'"
	@echo "                     would make, and the spec-table rows it does not cover,"
	@echo "                     without running anything (no PDK/ngspice needed)."
	@echo "  make clean         remove sim/'s scratch working directory (sim/.work/)."
	@echo ""
	@echo "See README.md -> 'Independent verification (Chipalooza)' for prerequisites,"
	@echo "expected wall-clock, and how each proposal spec-table row maps to output files."

# Unit tests (harness + layout, stdlib-only, no PDK needed) plus an explicit
# ngspice/PDK environment report. Deliberately narrower than `npm run
# check:ci`: this is the fast, first-thing-a-reviewer-runs sanity check, not
# the full PR-blocking check suite.
check:
	$(PYTHON) -m unittest discover -s sim/tests -t sim/tests
	$(PYTHON) -m unittest discover -s layout/tests -t layout/tests
	$(PYTHON) sim/run_corners.py --check-env

# One typical corner, minutes not hours: harness unit tests + record-checksum
# integrity + an end-to-end smoke run (sim/tb/smoke-op) + the corner-sanity
# guardrail (sim/tb/corner-sanity-nfet-id). Skips the PDK-dependent stages
# with exit 0 if ngspice/the PDK are not installed -- run `make check` first
# to see why.
smoke:
	sim/selftest.sh

# Full PVT/corner campaign behind the proposal's spec table. Needs ngspice
# and the gf180mcu PDK (see README); writes new, dated evidence records
# under sim/records/ per sim/README.md's append-only format -- it never
# edits or replaces an existing record.
characterize:
	$(PYTHON) sim/characterize.py --jobs $(JOBS)

characterize-dry-run:
	$(PYTHON) sim/characterize.py --dry-run --jobs $(JOBS)

clean:
	rm -rf sim/.work
