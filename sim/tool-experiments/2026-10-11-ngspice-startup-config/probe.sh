#!/usr/bin/env bash
# PDK-free probe of which ngspice startup files batch mode reads.
# Everything lives in a mktemp directory; no machine-wide file is touched.
# Usage: probe.sh [outdir]   (each variant's combined output -> outdir/<name>.log)
set -u
out=${1:-.}
mkdir -p "$out"
t=$(mktemp -d)
trap 'rm -rf "$t"' EXIT
mkdir "$t/home" "$t/work" "$t/clean" "$t/scripts"
printf 'echo STARTUP_USER\n' >"$t/home/.spiceinit"
printf 'echo STARTUP_WORK\n' >"$t/work/.spiceinit"
cp "${SPINIT_SRC:-/usr/share/ngspice/scripts/spinit}" "$t/scripts/spinit"
printf 'echo STARTUP_SYSTEM\n' >>"$t/scripts/spinit"
printf '* probe\nV1 a 0 1\nR1 a 0 1k\n.op\n.end\n' >"$t/work/d.cir"
cp "$t/work/d.cir" "$t/clean/d.cir"
run() { # name, then a command (env assignments via env)
  local name=$1
  shift
  (cd "${WORK:-$t/work}" && env -u SPICE_SCRIPTS -u SPICE_LIB_DIR -u SPICE_NO_DATASEG HOME="$t/home" "$@") \
    >"$out/$name.log" 2>&1
  echo "$name exit=$?"
}
run 1_plain ngspice -b d.cir
run 2_dash_n ngspice -n -b d.cir
run 3_scripts_only env SPICE_SCRIPTS="$t/scripts" ngspice -b d.cir
run 4_scripts_dash_n env SPICE_SCRIPTS="$t/scripts" ngspice -n -b d.cir
run 5_empty_home env HOME="$t/nohome" ngspice -b d.cir
run 6_scripts_empty env SPICE_SCRIPTS="$t/none" ngspice -b d.cir
run 7_scripts_empty_n env SPICE_SCRIPTS="$t/none" ngspice -n -b d.cir
# user ~/.spiceinit alone (this work directory has no .spiceinit)
WORK=$t/clean run 8_user_only ngspice -b d.cir
WORK=$t/clean run 9_user_only_dash_n ngspice -n -b d.cir
# SPICE_LIB_DIR relocates the default scripts directory (<dir>/scripts/spinit).
mkdir -p "$t/lib/scripts"
printf 'echo STARTUP_LIBDIR\n' >"$t/lib/scripts/spinit"
WORK=$t/clean run 10_lib_dir env SPICE_LIB_DIR="$t/lib" ngspice -b d.cir
# The harness policy: -n plus SPICE_SCRIPTS at the checked-in pinned directory.
pinned=$(cd "$(dirname "$0")/../../harness/ngspice_scripts" && pwd)
run 11_policy_work env SPICE_LIB_DIR="$t/lib" SPICE_SCRIPTS="$pinned" ngspice -n -b d.cir
WORK=$t/clean run 12_policy_clean env SPICE_LIB_DIR="$t/lib" SPICE_SCRIPTS="$pinned" ngspice -n -b d.cir
