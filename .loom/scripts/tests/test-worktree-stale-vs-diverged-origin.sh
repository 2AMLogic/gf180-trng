#!/usr/bin/env bash
# test-worktree-stale-vs-diverged-origin.sh - Regression tests for issue #68
#
# The "worktree already exists" staleness check in worktree.sh used to decide
# "stale, reset to $BASE_REF (origin/main)" using ONLY ahead/behind counts
# relative to $BASE_REF — it never looked at origin/$BRANCH_NAME, the
# worktree's own remote feature branch. If a local worktree branch ever
# reached 0-commits-ahead-of-main parity (for any reason: a prior reset, a
# squash-merge elsewhere, etc.) while origin/$BRANCH_NAME still held real,
# pushed, unmerged commits, the next `worktree.sh <issue-number>` invocation
# hard-reset the worktree straight to origin/main WITHOUT ever fetching or
# checking origin/$BRANCH_NAME — silently discarding the local worktree's
# view of those pushed commits (origin itself was untouched, but a Judge/
# Doctor/re-dispatched Builder trusting the worktree's checked-out state
# would review/edit the wrong code).
#
# Fix: before treating a worktree as stale, also fetch and compare against
# origin/$BRANCH_NAME. If it has commits not in local HEAD, do not reset to
# $BASE_REF — fast-forward to origin/$BRANCH_NAME when safe, otherwise warn
# and leave the worktree as-is.
#
# Coverage:
#   1. Local branch at 0-ahead-of-main parity, origin/$BRANCH_NAME has real
#      unmerged commits reachable as a fast-forward from local HEAD -> the
#      pushed commits are NOT discarded (local worktree is fast-forwarded to
#      match origin/$BRANCH_NAME, not reset to main).
#   2. Local branch diverged from origin/$BRANCH_NAME (not a fast-forward
#      ancestor) -> the script warns and leaves the worktree exactly as it
#      is (no reset to main, no forced overwrite of local history either).
#   3. origin/$BRANCH_NAME does not exist yet (never pushed) -> degrades
#      gracefully to today's behavior: stale-reset to $BASE_REF, no error.
#
# Pattern follows test-worktree-sentinel-reinvoke.sh: throwaway bare origin +
# repo copy of worktree.sh (+ lib/) in a mktemp dir.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../.." && pwd)"

WORKTREE_SH="$SCRIPTS_DIR/worktree.sh"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

pass() { TESTS_RUN=$((TESTS_RUN + 1)); TESTS_PASSED=$((TESTS_PASSED + 1)); echo -e "  ${GREEN}PASS${NC}: $1"; }
fail() { TESTS_RUN=$((TESTS_RUN + 1)); TESTS_FAILED=$((TESTS_FAILED + 1)); echo -e "  ${RED}FAIL${NC}: $1"; }

# Resolve to the physical path (pwd -P): on macOS /tmp is a symlink to
# /private/tmp, and worktree.sh's orphan-cleanup compares `git worktree list`
# paths (physical) against a resolved path. A symlinked temp root would make
# registered worktrees look unregistered and get spuriously recreated.
TMP_ROOT=$(cd "$(mktemp -d /tmp/loom-stale-vs-diverged.XXXXXX)" && pwd -P)
trap 'rm -rf "$TMP_ROOT"; cd "$REPO_ROOT" 2>/dev/null || true' EXIT

# Build a fresh throwaway repo with a bare origin/main and a copy of
# worktree.sh, returning its path via stdout.
make_repo() {
    local name="$1"
    local base="$TMP_ROOT/$name"
    git init -q -b main "$base/origin.git" --bare
    git init -q -b main "$base/repo"
    (
        cd "$base/repo"
        git config user.email t@t
        git config user.name t
        # Gitignore .loom-managed and .loom/worktrees/ (as real Loom repos
        # do, see this repo's own .gitignore) so the sentinel worktree.sh
        # writes into each worktree doesn't itself show up as an
        # "uncommitted change" and short-circuit the staleness check we're
        # exercising here. ".loom/" alone would NOT be enough: the sentinel
        # lives at the worktree ROOT (e.g. .loom/worktrees/issue-51/.loom-managed),
        # a sibling of ".loom/", not nested under it.
        printf '.loom-managed\n.loom/worktrees/\n' > .gitignore
        git add .gitignore
        git commit -q -m init
        git remote add origin "$base/origin.git"
        git push -q origin main
        mkdir -p .loom/scripts/lib
        cp "$WORKTREE_SH" .loom/scripts/worktree.sh
        if [[ -d "$SCRIPTS_DIR/lib" ]]; then
            cp -R "$SCRIPTS_DIR"/lib/* .loom/scripts/lib/ 2>/dev/null || true
        fi
        chmod +x .loom/scripts/worktree.sh
    )
    echo "$base/repo"
}

# --- Test 1: origin/$BRANCH_NAME ahead (fast-forward case) is preserved ---
echo "Test 1: local at main-parity + origin/<branch> holds a real unmerged FF commit"
REPO=$(make_repo t1)
(
    cd "$REPO"
    WT=".loom/worktrees/issue-51"

    # Create the worktree, add a commit, push it (simulates a builder that
    # pushed real PR work to origin/feature/issue-51).
    ./.loom/scripts/worktree.sh 51 >/dev/null 2>&1
    (
        cd "$WT"
        echo "pr work" > pr-work.txt
        git add pr-work.txt
        git commit -q -m "pr work"
        git push -q -u origin feature/issue-51
    )
    PUSHED_SHA=$(git -C "$WT" rev-parse HEAD)

    # Simulate the local worktree's branch pointer reverting to 0-ahead-of-main
    # parity (the exact symptom reported in #68) while origin/feature/issue-51
    # still holds the pushed commit.
    git -C "$WT" reset --hard origin/main >/dev/null 2>&1

    # Re-invoke worktree.sh for the same issue.
    ./.loom/scripts/worktree.sh 51 >"$TMP_ROOT/t1.out" 2>&1

    # Assert the pushed commit is NOT discarded: local HEAD must still contain it.
    if git -C "$WT" cat-file -e "$PUSHED_SHA" 2>/dev/null && \
       [[ "$(git -C "$WT" rev-parse HEAD)" == "$PUSHED_SHA" ]]; then
        echo "PRESERVED" > "$TMP_ROOT/t1.result"
    else
        echo "DISCARDED" > "$TMP_ROOT/t1.result"
    fi
)
if [[ "$(cat "$TMP_ROOT/t1.result" 2>/dev/null)" == "PRESERVED" ]]; then
    pass "pushed origin/feature/issue-51 commit is preserved (fast-forwarded), not silently discarded"
else
    fail "pushed origin/feature/issue-51 commit was DISCARDED by re-invoke (see $TMP_ROOT/t1.out)"
fi
grep -qi "not resetting\|fast-forward" "$TMP_ROOT/t1.out" \
    && pass "re-invoke output signals the diverged-origin-aware path was taken" \
    || fail "re-invoke output does not mention the diverged-origin-aware path (see $TMP_ROOT/t1.out)"

# --- Test 2: origin/$BRANCH_NAME diverged (non-fast-forward) -> warn, leave as-is ---
echo ""
echo "Test 2: local diverged from origin/<branch> (not a fast-forward) -> warn, no reset either way"
REPO=$(make_repo t2)
(
    cd "$REPO"
    WT=".loom/worktrees/issue-52"

    ./.loom/scripts/worktree.sh 52 >/dev/null 2>&1
    (
        cd "$WT"
        echo "v1" > pr-work.txt
        git add pr-work.txt
        git commit -q -m "v1"
        git push -q -u origin feature/issue-52
    )
    # Advance origin/main independently with an unrelated commit, so main's
    # new tip is NOT an ancestor of the (older-base) feature branch. Resetting
    # the local worktree to this new origin/main tip therefore makes local
    # HEAD genuinely non-fast-forward-able into origin/feature/issue-52 (a
    # true divergence — an amend-only rewrite wouldn't do this, since HEAD
    # would still trivially be an ancestor of the amended commit's unchanged
    # parent).
    echo "unrelated main work" > main-only.txt
    git add main-only.txt
    git commit -q -m "unrelated main-only commit"
    git push -q origin main
    # Now roll local worktree HEAD to this new, diverged main tip.
    (cd "$WT" && git fetch -q origin main && git reset --hard origin/main)
    LOCAL_SHA_BEFORE=$(git -C "$WT" rev-parse HEAD)

    ./.loom/scripts/worktree.sh 52 >"$TMP_ROOT/t2.out" 2>&1

    LOCAL_SHA_AFTER=$(git -C "$WT" rev-parse HEAD)
    if [[ "$LOCAL_SHA_AFTER" == "$LOCAL_SHA_BEFORE" ]]; then
        echo "UNCHANGED" > "$TMP_ROOT/t2.result"
    else
        echo "CHANGED" > "$TMP_ROOT/t2.result"
    fi
)
if [[ "$(cat "$TMP_ROOT/t2.result" 2>/dev/null)" == "UNCHANGED" ]]; then
    pass "diverged (non-FF) origin/<branch> is not silently reset over — worktree left as-is"
else
    fail "diverged (non-FF) origin/<branch> case unexpectedly changed local HEAD (see $TMP_ROOT/t2.out)"
fi
grep -qi "diverged\|not resetting" "$TMP_ROOT/t2.out" \
    && pass "re-invoke output warns about the diverged origin branch" \
    || fail "re-invoke output does not warn about divergence (see $TMP_ROOT/t2.out)"

# --- Test 3: origin/$BRANCH_NAME never pushed -> degrades gracefully to today's behavior ---
echo ""
echo "Test 3: origin/<branch> does not exist (never pushed) -> stale-reset behaves as before, no error"
REPO=$(make_repo t3)
(
    cd "$REPO"
    WT=".loom/worktrees/issue-53"
    ./.loom/scripts/worktree.sh 53 >/dev/null 2>&1
    # Never push feature/issue-53. Worktree is already at main-parity (fresh
    # branch off origin/main), so it's genuinely stale.
    ./.loom/scripts/worktree.sh 53 >"$TMP_ROOT/t3.out" 2>&1
)
if [[ $? -eq 0 ]] 2>/dev/null; then :; fi
grep -qi "reset to origin/main\|Stale worktree" "$TMP_ROOT/t3.out" \
    && pass "never-pushed branch: re-invoke still takes the ordinary stale-reset path (no error)" \
    || fail "never-pushed branch: re-invoke did not take the stale-reset path (see $TMP_ROOT/t3.out)"
grep -qi "fatal\|error" "$TMP_ROOT/t3.out" \
    && fail "never-pushed branch: unexpected error/fatal in output (see $TMP_ROOT/t3.out)" \
    || pass "never-pushed branch: no error from the best-effort origin/<branch> fetch"

# --- Summary ---
echo ""
echo "Tests run: $TESTS_RUN, Passed: $TESTS_PASSED, Failed: $TESTS_FAILED"
[[ $TESTS_FAILED -eq 0 ]] || exit 1
