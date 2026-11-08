#!/usr/bin/env bash
# E183 (the kit's dated note 2, KIT.md.dated-note-2.md, Sun 8 Nov 2026, before any E183 datum): KIT.md box step 2 v3, the desk check before
# any box step, on the Intel only. It is step 2 v2 (s03_desk_e183_v2.sh, 45e514e3, which stays as committed and runs unchanged inside
# it) with the day-2 check (E185's tools/claims-v3/e185/rb/check_day2_v1.py, one check for the whole day) before it, so that no
# repository code runs on a tree the check has not passed:
#   1. RB_OUT and RB_LOCK set, RB_OUT outside the repo, and the window written today (as v2 refuses: 10, before any call);
#   2. the day-2 check with its own pull: the lab clone's `git pull --ff-only` (bounded at 600 s; a failure named as the network's or
#      not), then HEAD descends from 6860643c, every list the day reads at its count, its own bytes and every entry (E183's three lists,
#      its brief's and its M1 list's among them), no change but an addition since 6860643c on the day's paths, no shadowing addition and
#      no uncommitted change (16 names what failed);
#   3. step 2 v2, unchanged, on the same tree (its own pull then reads "Already up to date"); its exit status is this step's;
#   4. HEAD unchanged across step 2 v2, else 16: the lab moved during the step, so run step 2 v3 again.
# It closes, for E183's day, verify-d2b's faults 1 and 3 (no code read SHA256SUMS-e183-brief or SHA256SUMS-e183-m1: a committed edit of the
# brief, or of the M1 reader with its list line, passed v2) and verify-d2's nit 4 (E183's pins were counts: the lists' own bytes are now
# pinned too). Exit codes are k6's.
#
#   bash tools/claims-v3/e183/rb/s03_desk_e183_v3.sh
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=${RB_REPO:-$(cd "$D/../../../.." && pwd)}
PY=${RB_PY:-/usr/bin/python3}
CHECK=$REPO/tools/claims-v3/e185/rb/check_day2_v1.py
STEP=s03_desk_v3_e183
say() { if [ -n "${RB_DRY:-}" ]; then echo "[$STEP] (dry listing; a real run would say:) $*"; else echo "[$STEP] $*"; fi; }
die() { local c=$1; shift; echo "[$STEP] STOP: $*"; echo "$(date '+%F %T %Z') step=$STEP exit=$c $*" >> "$RB_OUT/runbook.log"; exit "$c"; }
[ -n "${RB_OUT:-}" ] || { echo "[$STEP] RB_OUT is not set (this card day's own directory, outside the repo)"; exit 10; }
[ -n "${RB_LOCK:-}" ] || { echo "[$STEP] RB_LOCK is not set (the lock file a login check is appended to)"; exit 10; }
mkdir -p "$RB_OUT" || exit 10
o=$(cd "$RB_OUT" && pwd -P); r=$(cd "$REPO" && pwd -P)
case "$o/" in "$r/"*) echo "[$STEP] RB_OUT is inside the lab repo: refused"; exit 10 ;; esac
[ -n "${RB_DRY:-}" ] && echo "=== [$STEP] dry listing: nothing below is run"
if [ -z "${RB_DRY:-}" ]; then
  [ -f "$RB_OUT/window.env" ] || die 10 "no window in RB_OUT: run s02_window_e183.sh first (kit v5: s02 before s03)"
  [ "$(date -r "$RB_OUT/window.env" +%F)" = "$(date +%F)" ] || die 10 "RB_OUT's window was not written today: run s02_window_e183.sh first"
fi
# 2. the day-2 check, with its own pull, before any other repository code runs
dry=(); [ -n "${RB_DRY:-}" ] && dry=(--dry)
"$PY" -I -B "$CHECK" tree --pull --repo "$REPO" --log "$RB_OUT/runbook.log" --step "$STEP" ${dry[@]+"${dry[@]}"}
rc=$?
[ "$rc" -eq 0 ] || { echo "[$STEP] STOP: the day-2 check exited $rc (its STOP line above names why)"; exit "$rc"; }
h1=""; [ -z "${RB_DRY:-}" ] && h1=$(git -C "$REPO" rev-parse HEAD 2>/dev/null)
# 3. step 2 v2, unchanged, on the same tree
bash "$D/s03_desk_e183_v2.sh"
rc=$?
[ "$rc" -eq 0 ] || { echo "[$STEP] STOP: step 2 v2 exited $rc (its STOP line above names why)"; exit "$rc"; }
# 4. the tree did not move during step 2 v2
if [ -z "${RB_DRY:-}" ]; then
  h2=$(git -C "$REPO" rev-parse HEAD 2>/dev/null)
  [ -n "$h1" ] && [ "$h1" = "$h2" ] || die 16 "the lab clone moved during step 2 v2 (${h1:0:12} to ${h2:0:12}): run step 2 v3 again"
fi
[ -z "${RB_DRY:-}" ] && echo "$(date '+%F %T %Z') step=$STEP desk check v3 passed at $h1" >> "$RB_OUT/runbook.log"
say "desk check v3: the day-2 check passed at ${h1:0:12}${RB_DRY:+<HEAD>} (pulled; HEAD descends from 6860643c; the day's lists at their counts, own bytes and entries; no change but an addition since 6860643c on the day's paths; no shadowing addition; nothing uncommitted), then step 2 v2 passed on the same HEAD (its line above)"
