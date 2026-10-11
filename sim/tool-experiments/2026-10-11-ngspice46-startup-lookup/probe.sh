#!/usr/bin/env bash
# PDK-free probe of which ngspice startup files batch mode reads on the
# ngspice >= 46 baseline the repository requires. Companion to
# ../2026-10-11-ngspice-startup-config/ (ngspice-42): the deck directory and
# the process working directory are varied independently, and each startup
# file carries its own sentinel, so the lookup order is measured rather than
# assumed (issue #584: ngspice-46 was observed to read the deck-directory
# .spiceinit even when the working directory contained none).
#
# Everything lives in a mktemp directory; no machine-wide file is touched.
# Usage: probe.sh [outdir]   (one log per variant -> outdir/, plus
#        00_version.log, commands.txt, fixture-tree.log)
#
# Set SPINIT_SRC to the spinit of the build under test when it is not the
# installed default next to the ngspice binary on PATH.
set -u
out=${1:-.}
mkdir -p "$out"
t=$(mktemp -d)
trap 'rm -rf "$t"' EXIT

: "${SPINIT_SRC:=$(dirname "$(command -v ngspice)")/../share/ngspice/scripts/spinit}"

# -- Fixture tree: one sentinel per startup source. -------------------------
mkdir "$t/home" "$t/ddir" "$t/cwdh" "$t/cleand" "$t/nowork" "$t/scripts"
printf 'echo SENTINEL_USER\n'   >"$t/home/.spiceinit"   # $HOME/.spiceinit
printf 'echo SENTINEL_DECK\n'   >"$t/ddir/.spiceinit"   # deck directory
printf 'echo SENTINEL_CWD\n'    >"$t/cwdh/.spiceinit"   # process cwd
cp "${SPINIT_SRC}" "$t/scripts/spinit"
printf 'echo SENTINEL_SYSTEM\n' >>"$t/scripts/spinit"   # $SPICE_SCRIPTS/spinit
printf '* probe\nV1 a 0 1\nR1 a 0 1k\n.op\n.end\n' >"$t/ddir/d.cir"
cp "$t/ddir/d.cir" "$t/cleand/d.cir"                     # deck dir with no .spiceinit
mkdir -p "$t/lib/scripts"                                # $SPICE_LIB_DIR relocation
printf 'echo SENTINEL_LIBDIR\n' >"$t/lib/scripts/spinit"
(cd "$t" && find . | sort) >"$out/fixture-tree.log"

# -- Version / build of the simulator under test. ---------------------------
{
  printf 'ngspice on PATH: %s\n' "$(command -v ngspice)"
  ngspice --version 2>&1
  sha256sum "$(command -v ngspice)"
  printf 'SPINIT_SRC: %s\n  ' "${SPINIT_SRC}"
  sha256sum "${SPINIT_SRC}"
} >"$out/00_version.log" 2>&1

# -- Variants: each is one `ngspice -b <abs-deck>` process. -----------------
# run NAME CWD CMD...  (env assignments ride on the command, like env(1);
# HOME is hostile unless the variant overrides it; SPICE_SCRIPTS and
# SPICE_LIB_DIR are unset unless a variant sets them). Every variant's
# command and exit status are appended to commands.txt.
cmds="$out/commands.txt"
: >"$cmds"
run() {
  local name=$1 cwd=$2
  shift 2
  printf '%s\n' "(cd $cwd && $*)" >>"$cmds"
  (cd "$cwd" && env -u SPICE_SCRIPTS -u SPICE_LIB_DIR HOME="$t/home" "$@") \
    >"$out/$name.log" 2>&1
  echo "$name exit=$?" | tee -a "$cmds"
}
pinned=$(cd "$(dirname "$0")/../../harness/ngspice_scripts" && pwd)

# Which sources are reachable at all, and from which cwd?
run 01_all_deckdir_cwd    "$t/ddir"   ngspice -b "$t/ddir/d.cir"
run 02_all_cleancwd       "$t/nowork" ngspice -b "$t/ddir/d.cir"
run 03_deck_and_cwd       "$t/cwdh"   ngspice -b "$t/ddir/d.cir"
run 04_cwd_only           "$t/cwdh"   ngspice -b "$t/cleand/d.cir"
run 05_user_only          "$t/nowork" ngspice -b "$t/cleand/d.cir"
run 06_user_only_dash_n   "$t/nowork" ngspice -n -b "$t/cleand/d.cir"
run 07_dash_n_all         "$t/ddir"   ngspice -n -b "$t/ddir/d.cir"
run 07b_dash_n_scripts    "$t/ddir"   env SPICE_SCRIPTS="$t/scripts" ngspice -n -b "$t/ddir/d.cir"
# The harness policy: -n plus SPICE_SCRIPTS at the checked-in pinned
# directory, SPICE_LIB_DIR hostile, every .spiceinit fixture hostile.
run 08_policy_deckdir     "$t/ddir"   env SPICE_LIB_DIR="$t/lib" SPICE_SCRIPTS="$pinned" ngspice -n -b "$t/ddir/d.cir"
run 09_policy_cleancwd    "$t/nowork" env SPICE_LIB_DIR="$t/lib" SPICE_SCRIPTS="$pinned" ngspice -n -b "$t/ddir/d.cir"
# SPICE_LIB_DIR relocates the default scripts directory (<dir>/scripts/spinit).
run 10_lib_dir            "$t/nowork" env SPICE_LIB_DIR="$t/lib" ngspice -b "$t/cleand/d.cir"
