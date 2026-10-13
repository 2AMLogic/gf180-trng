# ngspice-46 startup-file lookup order (2026-10-11)

Append-only evidence. This directory records one small, PDK-free experiment
establishing **where** batch-mode ngspice >= 46 (the build the README
requires) looks for `.spiceinit`: the deck's directory, the process working
directory, or `$HOME`. It backs the hostile-fixture test in
`sim/tests/test_runner.py` (`StartupPolicyTests`) and the start-up policy in
`sim/harness/startup.py` (issue #584). It is a simulator-behaviour probe,
not a harness run, so it is not a `sim/records/` record and has no PVT
grid. Do not edit the files here; a later experiment gets its own dated
directory.

## Question

The ngspice-42 measurement
([`2026-10-11-ngspice-startup-config/`](../2026-10-11-ngspice-startup-config/README.md))
found that batch mode reads `.spiceinit` from the *working directory*, else
`$HOME`. On ngspice-46 that assumption broke
`test_hostile_init_fixtures_affect_plain_batch_but_not_the_policy`: with the
deck inside a hostile directory but run from a clean working directory, the
work-directory sentinel still fired. Which directory is actually searched —
and in what order — was unmeasured. This experiment measures it, varying the
deck directory and the working directory independently.

## Setup

- Simulator: ngspice **46** built from the release tarball pinned in
  `.github/workflows/pdk-nightly.yml`
  (`ngspice-46.tar.gz`, SHA-256
  `a0d1699af1940b06649276dcd6ff5a566c8c0cad01b2f7b5e99dedbb4d64c19b`,
  digest-verified before extraction), configured exactly as that workflow
  does: `./configure --with-x=no --with-readline=no --enable-xspice
  --disable-debug`. Created `Sun Oct 11 15:38:06 UTC 2026` on
  `x86_64` Linux (Ubuntu 24.04, gcc from `build-essential`); `00_version.log`
  records the binary's self-reported version, absolute path and SHA-256.
  The tarball digest, not the binary digest, is the reproducibility anchor:
  the binary digest pins this one local build.
- `probe.sh` builds everything in a `mktemp -d` directory
  (`fixture-tree.log`): a `$HOME` whose `.spiceinit` prints
  `SENTINEL_USER`, a *deck directory* `ddir/` holding the deck `d.cir` and a
  `.spiceinit` printing `SENTINEL_DECK`, a working-directory fixture `cwdh/`
  whose `.spiceinit` prints `SENTINEL_CWD`, a clean deck copy in `cleand/`
  (no `.spiceinit`), an empty `nowork/`, a `SPICE_SCRIPTS` directory whose
  `spinit` (installed default plus an append) prints `SENTINEL_SYSTEM`, and
  a `SPICE_LIB_DIR` tree whose `scripts/spinit` prints `SENTINEL_LIBDIR`.
  No machine-wide file is read for writing or modified.
- Run: `./probe.sh logs` from this directory. Each variant is one
  `ngspice -b <absolute deck path>` process; `commands.txt` records every
  command and its exit status (all exit 0), combined output is in
  `logs/<n>_<name>.log`, and `SHA256SUMS` hashes both.

## Results

`grep SENTINEL logs/*.log` shows which sentinels ran; every variant leaves
`HOME` hostile unless named otherwise.

| Variant | cwd | Deck directory | Command additions | Sentinels printed |
|---|---|---|---|---|
| 01 all, cwd = deck dir | `ddir/` (hostile) | hostile | — | DECK |
| 02 all, clean cwd | `nowork/` (clean) | hostile | — | DECK |
| 03 deck + cwd hostile | `cwdh/` (hostile) | hostile | — | DECK |
| 04 cwd only | `cwdh/` (hostile) | clean | — | CWD |
| 05 user only | `nowork/` (clean) | clean | — | USER |
| 06 user only + `-n` | `nowork/` (clean) | clean | `-n` | none |
| 07 all + `-n` | `ddir/` (hostile) | hostile | `-n` | none |
| 07b all + `-n` + hostile `SPICE_SCRIPTS` | `ddir/` (hostile) | hostile | `-n`, `SPICE_SCRIPTS=<hostile>` | SYSTEM |
| 08 policy, cwd = deck dir | `ddir/` (hostile) | hostile | `-n`, `SPICE_SCRIPTS=<pinned>`, `SPICE_LIB_DIR=<hostile>` | none |
| 09 policy, clean cwd | `nowork/` (clean) | hostile | `-n`, `SPICE_SCRIPTS=<pinned>`, `SPICE_LIB_DIR=<hostile>` | none |
| 10 `SPICE_LIB_DIR` | `nowork/` (clean) | clean | `SPICE_LIB_DIR=<hostile>` | LIBDIR, USER |

Conclusions for ngspice-46 batch mode:

1. **The deck's directory is searched first.** `SENTINEL_DECK` fires with
   the working directory clean (02) and wins over a hostile working
   directory (03): exactly one of the three `.spiceinit` locations is read
   per launch in every variant.
2. Fallback order, each level only when the previous one has no
   `.spiceinit`: deck directory (01–03) → working directory (04) →
   `$HOME` (05).
3. `-n` (`--no-spiceinit`) suppresses all three `.spiceinit` lookups
   (06, 07) but does **not** suppress the system `spinit` (07b) — unchanged
   from ngspice-42.
4. `SPICE_SCRIPTS` (07b) and the `SPICE_LIB_DIR/scripts` fallback (10)
   behave as measured on ngspice-42.
5. The harness policy — `-n` plus `SPICE_SCRIPTS` at the checked-in pinned
   directory whose `spinit` is inert — leaves no sentinels reachable even
   with a hostile `$HOME`, hostile deck-directory and working-directory
   `.spiceinit`, and hostile `SPICE_LIB_DIR` (08, 09). The policy itself
   needs no change on ngspice-46; the ngspice-42 test fixture was the only
   thing that encoded the outdated lookup rule.

What differs from ngspice-42, explicitly version-scoped: ngspice-42 read
`.spiceinit` from the *working directory*, else `$HOME`, and never looked at
the deck's directory; ngspice-46 looks at the *deck's directory* first, then
the working directory, then `$HOME`. The suppression behaviour (`-n` scope,
`SPICE_SCRIPTS`/`SPICE_LIB_DIR`) is the same on both measured builds. Both
measurements are pinned to their versions; neither is generalized to other
builds. The hostile-fixture test
(`test_hostile_init_fixtures_affect_plain_batch_but_not_the_policy`) is
written so its plain-launch sanity assertions hold under **either** lookup
rule: each names one startup source and leaves only that source reachable.
