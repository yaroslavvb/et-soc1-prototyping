#!/usr/bin/env bash
# E185, the runbook's step 2 (the desk check), v4: the kit's dated note 3 (KIT.md.dated-note-3.md, Sun 8 Nov 2026, before any E185 datum).
# It is step 2 v3 (s03_desk_e185_v3.sh, 408a9a9e, which stays as committed and runs unchanged inside it) with the day-2 check
# (check_day2_v1.py) before it, so that no repository code runs on a tree the check has not passed:
#   1. RB_OUT and RB_LOCK set, RB_OUT outside the repo, and the window written today (as v3 refuses: 10, before any call);
#   2. the day-2 check with its own pull: the lab clone's `git pull --ff-only` (bounded at 600 s; a failure named as the network's or
#      not), then HEAD descends from 6860643c, every list the day reads at its count, its own bytes and every entry, no change but an
#      addition since 6860643c on the day's paths, no shadowing addition and no uncommitted change (16 names what failed);
#   3. step 2 v3, unchanged, on the same tree (its own pull then reads "Already up to date"); its exit status is this step's;
#   4. HEAD unchanged across step 2 v3, else 16: the lab moved during the step, so run step 2 v4 again.
# It closes, for E185's day, verify-d2b's faults 2 and 3 (M11's scorer and both briefs rewritten with their list lines, or under a copied
# line, passed v3) and the uncommitted-E183-brief gap v3 left (its status read E185's paths only). Exit codes are the runbook's.
#
#   bash tools/claims-v3/e185/rb/s03_desk_e185_v4.sh
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=${RB_REPO:-$(cd "$D/../../../.." && pwd)}
PY=${RB_PY:-/usr/bin/python3}
STEP=s03_desk_v4_e185
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
# 2. the day-2 check, with its own pull, before any other repository code runs
dry=(); [ -n "${RB_DRY:-}" ] && dry=(--dry)
"$PY" -I -B "$D/check_day2_v1.py" tree --pull --repo "$REPO" --log "$RB_OUT/runbook.log" --step "$STEP" ${dry[@]+"${dry[@]}"}
rc=$?
[ "$rc" -eq 0 ] || { echo "[$STEP] STOP: the day-2 check exited $rc (its STOP line above names why)"; exit "$rc"; }
h1=""; [ -z "${RB_DRY:-}" ] && h1=$(git -C "$REPO" rev-parse HEAD 2>/dev/null)
# 3. step 2 v3, unchanged, on the same tree
bash "$D/s03_desk_e185_v3.sh"
rc=$?
[ "$rc" -eq 0 ] || { echo "[$STEP] STOP: step 2 v3 exited $rc (its STOP line above names why)"; exit "$rc"; }
# 4. the tree did not move during step 2 v3
if [ -z "${RB_DRY:-}" ]; then
  h2=$(git -C "$REPO" rev-parse HEAD 2>/dev/null)
  [ -n "$h1" ] && [ "$h1" = "$h2" ] || die 16 "the lab clone moved during step 2 v3 (${h1:0:12} to ${h2:0:12}): run step 2 v4 again"
fi
[ -z "${RB_DRY:-}" ] && echo "$(date '+%F %T %Z') step=$STEP desk check v4 passed at $h1" >> "$RB_OUT/runbook.log"
say "desk check v4: the day-2 check passed at ${h1:0:12}${RB_DRY:+<HEAD>} (pulled; HEAD descends from 6860643c; the day's lists at their counts, own bytes and entries; no change but an addition since 6860643c on the day's paths; no shadowing addition; nothing uncommitted), then step 2 v3 passed on the same HEAD (its line above)"
