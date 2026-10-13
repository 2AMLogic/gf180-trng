# ngspice start-up configuration experiment (2026-10-11)

Append-only evidence. This directory records one small, PDK-free experiment
on which initialization files ngspice reads in batch mode and which control
suppresses each. It backs the start-up policy in `sim/harness/startup.py`
(issue #575). It is a simulator-behaviour probe, not a harness run, so it is
not a `sim/records/` record and has no PVT grid. Do not edit the files here;
a later experiment gets its own dated directory.

## Question

Which of the user `~/.spiceinit`, the work-directory `.spiceinit` and the
system `spinit` does `ngspice -b` read, and which command-line option or
environment variable suppresses or redirects each?

## Setup

- Simulator: `ngspice -v` reports `ngspice-42 : Circuit level simulation
  program`, `Compiled with KLU Direct Linear Solver`, creation date
  `Sun Mar 31 20:15:14 UTC 2024` (Ubuntu 24.04 package `42+ds-3build1`).
  This is **not** the ngspice-46 build the seed-control experiment used;
  start-up-file handling on other builds has not been measured here, so the
  conclusions below are pinned to ngspice-42. Re-run `probe.sh` on any other
  build before relying on them.
- `probe.sh` builds everything in a `mktemp -d` directory: a `HOME` holding
  `.spiceinit` (prints `STARTUP_USER`), a work directory holding `.spiceinit`
  (prints `STARTUP_WORK`), a clean work directory, and a scripts directory
  holding a copy of the installed `spinit` plus `echo STARTUP_SYSTEM`, and a
  `SPICE_LIB_DIR` tree whose `scripts/spinit` prints `STARTUP_LIBDIR`. No
  machine-wide file is read for writing or modified. The deck is a one-resistor
  `.op`.
- Run: `./probe.sh logs` from this directory. Each variant is one
  `ngspice -b d.cir` process (all exit 0); combined output is in
  `logs/<n>_<name>.log` and `SHA256SUMS` hashes them.

## Results

`grep STARTUP logs/*.log` shows which sentinels ran:

| Variant | Command (env other than `HOME`) | Sentinels printed |
|---|---|---|
| 1 plain | `ngspice -b` | WORK |
| 2 `-n` | `ngspice -n -b` | none |
| 3 scripts dir | `SPICE_SCRIPTS=<dir> ngspice -b` | SYSTEM, WORK |
| 4 scripts dir + `-n` | `SPICE_SCRIPTS=<dir> ngspice -n -b` | SYSTEM |
| 5 no user file | `HOME=<empty> ngspice -b` | WORK |
| 6 scripts dir missing | `SPICE_SCRIPTS=<none> ngspice -b` | WORK (log: `Note: can't find the initialization file spinit.`) |
| 7 scripts dir missing + `-n` | `SPICE_SCRIPTS=<none> ngspice -n -b` | none |
| 8 user file only | `ngspice -b`, clean work directory | USER |
| 9 user file only + `-n` | `ngspice -n -b`, clean work directory | none |
| 10 `SPICE_LIB_DIR` | `SPICE_LIB_DIR=<tree> ngspice -b`, clean work directory | LIBDIR, USER |
| 11 policy | `SPICE_LIB_DIR=<tree> SPICE_SCRIPTS=<pinned> ngspice -n -b`, hostile work directory | none |
| 12 policy | same, clean work directory (hostile `HOME`) | none |

Conclusions for ngspice-42 batch mode:

1. The work-directory `.spiceinit` is read, and when it exists it **shadows**
   the user `~/.spiceinit` (variants 1, 5 vs 8): only one of the two runs.
2. `-n` (`--no-spiceinit`) suppresses both of those files (2, 9) but does
   **not** suppress the system `spinit` (4).
3. The system `spinit` is read from `$SPICE_SCRIPTS` (3, 4) or, failing that,
   `$SPICE_LIB_DIR/scripts` (10), else the installed default (not shown: it
   is host-specific). Pointing `SPICE_SCRIPTS` at a directory without a
   `spinit` silences it (6, 7) but prints a note and leaves a host-dependent
   run, so the harness points it at a checked-in `spinit` instead.
4. `-n` plus `SPICE_SCRIPTS=<pinned dir>` leaves none of the sentinels
   reachable, even with hostile `HOME`, work-directory file and
   `SPICE_LIB_DIR` (11, 12). One flag alone is insufficient.

The installed `spinit` on the measuring host only defines two aliases,
`set x11lineararcs` (graphics), and conditional `codemodel`/`osdi` loads.
The pinned harness `spinit` carries no commands, so it differs from a typical
installed one only in those; harness decks use built-in device models only.
Unmeasured here: other ngspice builds, Windows, and options read from
`.spiceinit` by the `ngspice` library (shared-library) mode.
