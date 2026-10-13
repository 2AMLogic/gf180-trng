# gf180-trng — agent instructions

Canary block: a true random number generator on gf180mcu. Apache-2.0.

- **PDK**: gf180mcu (open PDK). Open-source flow: xschem + ngspice for
  design/sim, klayout-tools (`klt`) for layout work.
- **Friction protocol (the canary's job)**: every time klayout-tools is
  awkward, missing a capability, or wrong for what you need, file an issue
  at `2AMLogic/klayout-tools` describing the need generically — describe
  the tool gap, not the design. A tool issue that only makes sense to
  someone who has read this repo's spec is a bad tool issue.
- **Verification is the product**: no claim without a testbench. PVT
  corners on every recorded result. `sim/` results are append-only
  evidence. Find the checks in [`package.json`](package.json) (commands)
  and [`.github/workflows/ci.yml`](.github/workflows/ci.yml) (what CI
  runs). Before review, run the applicable complete cheap suites on the
  final tree, not single tests. New evidence or decision records need
  `check:spec` (corpus counts); geometry changes need the downstream
  consumer suite. `check:ci` ends in `sim/selftest.sh`, which simulates
  when ngspice and the PDK exist; keep simulations opt-in and do not run
  host-mutating suites unasked. Report each command run, its exit status,
  and any unavailable check with its reason; never call an unrun check
  passing.
- **Publication**: this repo is public (the pre-publication audit, #22,
  closed 2026-07-31) — the visibility flip was an operator action, not an
  agent one. Write every commit message, issue, and document here as if a
  stranger will read it, because one will. Nothing about business
  positioning, commercial terms, or the contents of other 2AM Logic
  repositories belongs in this one.
- Spec changes go through `spec/` with a decision record; agents do not
  relax the ratified spec to make results pass.
- Harness: `sim/harness/` was bootstrapped from the `gf180-bandgap`
  sim-harness pattern (#21); extend it in place rather than reinventing.

<!-- BEGIN LOOM ORCHESTRATION -->
This repository uses [Loom](https://github.com/rjwalters/loom) for AI-powered development orchestration — see the Loom repository for the full guide (roles, labels, worktrees, configuration). When installed, Loom also writes a locally-substituted copy of that guide to `.loom/CLAUDE.md`.
<!-- END LOOM ORCHESTRATION -->
<!-- BEGIN REPO-SKILLS -->
This repository has [Repo Skills](https://github.com/rjwalters/repo) v0.19.5 installed —
general repository hygiene and environment commands invoked as `/repo:<command>`. Run
`/repo:help` for the command list, or see `.claude/skills/repo/SKILL.md` for the full
guide. Hygiene commands apply safe, reversible fixes by default and report each
change; run with `--ask` to review first, and `--prune` to allow irreversible
removals. Managed by `install.sh` — edit outside the markers only.
<!-- END REPO-SKILLS -->
