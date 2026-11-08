#!/usr/bin/env bash
# E185, the runbook's step 2 (the desk check), v5: the kit's dated note 4 (KIT.md.dated-note-4.md, Sun 8 Nov 2026, before any E185 datum).
# It is step 2 v4 (s03_desk_e185_v4.sh, 1e74546a, which stays as committed and runs unchanged inside it) with the day-2 check v2
# (check_day2_v2.py) before it, so that no repository code runs on a tree v2 has not passed:
#   1. RB_OUT and RB_LOCK set, RB_OUT outside the repo, and the window written today (as v4 refuses: 10, before any call);
#   2. the day-2 check v2 with its own pull: v1's check at its committed bytes, on v2's perimeter (v1's 32 lists and 15 more, among them
#      the closure list of the 168 lab files E185's scorer and collector load that v1 did not name), and no untracked module in any of the
#      day's directories (16 names what failed);
#   3. step 2 v4, unchanged, on the same tree (its day-2 check v1 and step 2 v3 then pull "Already up to date"); its exit status is this
#      step's;
#   4. HEAD unchanged across step 2 v4, else 16: the lab moved during the step, so run step 2 v5 again.
# It closes, for E185's day, verify-fx's faults 1 (a committed change to a file M11's scorer v5, arms_e185.py or the collector loads
# outside v1's perimeter passed v4) and 2 (an untracked module beside a named file outside the core directories passed v4). Exit codes are
# the runbook's.
#
#   bash tools/claims-v3/e185/rb/s03_desk_e185_v5.sh
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=${RB_REPO:-$(cd "$D/../../../.." && pwd)}
PY=${RB_PY:-/usr/bin/python3}
STEP=s03_desk_v5_e185
say() { if [ -n "${RB_DRY:-}" ]; then echo "[$STEP] (dry listing; a real run would say:) $*"; else echo "[$STEP] $*"; fi; }
die() { local c=$1; shift; echo "[$STEP] STOP: $*"; echo "$(date '+%F %T %Z') step=$STEP exit=$c $*" >> "$RB_OUT/runbook.log"; exit "$c"; }
[ -n "${RB_OUT:-}" ] || { echo "[$STEP] RB_OUT is not set (this card day's own directory, outside the repo)"; exit 10; }
[ -n "${RB_LOCK:-}" ] || { echo "[$STEP] RB_LOCK is not set (the lock file a login check is appended to)"; exit 10; }
mkdir -p "$RB_OUT" || exit 10
o=$(cd "$RB_OUT" && pwd -P); r=$(cd "$REPO" && pwd -P)
case "$o/" in "$r/"*) echo "[$STEP] RB_OUT is inside the lab repo: refused"; exit 10 ;; esac
[ -n "${RB_DRY:-}" ] && echo "=== [$STEP] dry listing: nothing below is run"
if [ -z "${RB_DRY:-}" ]; then
  [ -f "$RB_OUT/window.env" ] || die 10 "no window yet: run s02_window_e185.sh with his go's day, last start and last end"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    die 10 "the window in RB_OUT was not written today: run s02_window_e185.sh with his go's day, last start and last end first"
fi
# 2. the day-2 check v2, with its own pull, before any other repository code runs
dry=(); [ -n "${RB_DRY:-}" ] && dry=(--dry)
"$PY" -I -B "$D/check_day2_v2.py" tree --pull --repo "$REPO" --log "$RB_OUT/runbook.log" --step "$STEP" ${dry[@]+"${dry[@]}"}
rc=$?
[ "$rc" -eq 0 ] || { echo "[$STEP] STOP: the day-2 check v2 exited $rc (its STOP line above names why)"; exit "$rc"; }
h1=""; [ -z "${RB_DRY:-}" ] && h1=$(git -C "$REPO" rev-parse HEAD 2>/dev/null)
# 3. step 2 v4, unchanged, on the same tree
bash "$D/s03_desk_e185_v4.sh"
rc=$?
[ "$rc" -eq 0 ] || { echo "[$STEP] STOP: step 2 v4 exited $rc (its STOP line above names why)"; exit "$rc"; }
# 4. the tree did not move during step 2 v4
if [ -z "${RB_DRY:-}" ]; then
  h2=$(git -C "$REPO" rev-parse HEAD 2>/dev/null)
  [ -n "$h1" ] && [ "$h1" = "$h2" ] || die 16 "the lab clone moved during step 2 v4 (${h1:0:12} to ${h2:0:12}): run step 2 v5 again"
fi
[ -z "${RB_DRY:-}" ] && echo "$(date '+%F %T %Z') step=$STEP desk check v5 passed at $h1" >> "$RB_OUT/runbook.log"
say "desk check v5: the day-2 check v2 passed at ${h1:0:12}${RB_DRY:+<HEAD>} (pulled; v1 at its committed bytes; the day's 47 lists at their counts, own bytes and entries; no change but an addition since 6860643c on the day's paths; no shadowing addition; nothing uncommitted; no untracked module in the day's directories), then step 2 v4 passed on the same HEAD (its line above)"
