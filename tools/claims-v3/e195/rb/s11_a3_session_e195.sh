#!/usr/bin/env bash
# E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum), the box step "the session" (this file is s11): E195's card session on
# aifoundry3, launched detached on the box (it returns at once), ONLY after steps 1-8 read clean. E192's step 9 form
# (rb/s11_a3_session_e192.sh): the window rule (written today for E195), the last start, the session's cap of 45 card-minutes before the
# last end (2,700 s), k6's guard (no dry pass running, no card session of ours: rb_guard_text), THE REST RULE (rb/rest_rule_e195.sh: every
# session-log form of ours on the box; 40 minutes, refused before it), today's dry pass (a3-dry-e195 ended rc 0 today) and today's build
# (a3-build-e195 built today, RB_OUT/e195-built.txt), and the kit's day rules read on the box (before the rest rule: they refuse whatever the rest):
#   - NO STOP FILE LEFT in E195's root (build/x09-STOP, build/claims-v3/STOP: the session refuses them too; a dated note moves one aside);
#   - NO SECOND E195 SESSION THE SAME DAY after one that opened the card: a session of today whose log reached its first card read (a
#     "start config read" line or a GATE-STOP line without "no device opened") is that day's session (E195.md 12: a smoke that fails its
#     gate is "no pass that day"; a session that ran is the day's one); a launch that opened no device ("no device opened" on every gate and
#     refusal line, no start config read) is not a session: it may be launched ONCE more inside the same window once the look reads FREE
#     again (E192's G4 and E191 note 2's relaunch rule; the go confirms it), and RB_OUT then holds e195-relaunch.txt;
# then session_e195.sh detached (setsid nohup) with the T0 written on the box (build/q141k/e195.T0) and in RB_OUT (e195-T0.txt), which steps
# 10 and 11 read, X9_LATEST_START = the window's last start, X9_DEADLINE = the earlier of the window's last end and the launch + 45 minutes
# (E195.md 6), and harness-e195.json's sha256 (the session checks the box's copy against it).
#   bash tools/claims-v3/e195/rb/s11_a3_session_e195.sh FULL
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e195.sh"
rb_init s11_a3_session
plan=${1:-}
[ "$plan" = FULL ] || rb_die $RB_E_USAGE "E195 has one plan: FULL (the registered session: the smoke and passes 910-917; E195.md sections 5 and 11; the shorter variant only by a dated amendment)"
e195_window
rb_need_start
rb_need_end "$E195_CAP_S"
[ -n "${RB_DRY:-}" ] || [ -n "$(e195_built)" ] || rb_die $RB_E_USAGE "E195 was not built today (RB_OUT/e195-built.txt, step 6's wait): run step 6 first"
HS=$(e195_harness_sha)
[ -n "${RB_DRY:-}" ] || [ -n "$HS" ] || rb_die $RB_E_USAGE "no harness-e195.json in the lab clone"
relaunch=""
if [ -z "${RB_DRY:-}" ] && [ -f "$RB_OUT/e195-T0.txt" ]; then
  [ -f "$RB_OUT/e195-relaunch.txt" ] && rb_die $RB_E_USAGE "this RB_OUT already launched twice ($(cat "$RB_OUT/e195-relaunch.txt")): no third launch from it"
  relaunch=$(cat "$RB_OUT/e195-T0.txt")
fi
f=$(rb_file e195)
{ rb_prelude aifoundry3
  echo "ER=$E195_R; LE=${RB_LAST_END_EPOCH:-0}; LS=${RB_LAST_START_EPOCH:-0}; CAP=$E195_CAP_S; HS=$HS; RELAUNCH='$relaunch'; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat <<'EOF2'
job_ok_today a3-dry-e195 || { echo "REFUSED: E195's dry pass (step 8's job a3-dry-e195) has not ended rc 0 today"; exit 3; }
echo "dry pass: a3-dry-e195 ended rc 0 today"
fresh build/q141k/jobs/a3-build-e195.out && grep -q '^X09MEM-BUILT rc=0' build/q141k/jobs/a3-build-e195.out ||
  { echo "REFUSED: E195 was not built today (step 6's job a3-build-e195)"; exit 3; }
for s in "$ER/build/x09-STOP" "$ER/build/claims-v3/STOP"; do
  [ -e "$s" ] && { echo "REFUSED: $s exists in E195's root (a stop file left from before: a dated note moves it aside first)"; exit 3; }
done
TODAY=$(TZ=America/Los_Angeles date +%F)
for L in build/e195/T[0-9]*/session.log; do
  [ -f "$L" ] || continue
  case "$L" in *-dry/*) continue ;; esac
  [ "$(TZ=America/Los_Angeles date -r "$L" +%F)" = "$TODAY" ] || continue
  if grep -q 'start config read: \|GATE-STOP: .*no pass runs\|smoke rc=\|p9[0-9][0-9] rc=' "$L"; then
    echo "REFUSED: today's E195 session $(dirname "$L") opened the card (its log reached its first card read): no second E195 session today (E195.md 12)"; exit 3
  fi
  tl=$(basename "$(dirname "$L")"); tl=${tl#T}
  if [ "$tl" != "$RELAUNCH" ]; then
    echo "REFUSED: today's E195 launch T$tl opened no device but is not this RB_OUT's last launch ($RELAUNCH): launch from the RB_OUT that made it"; exit 3
  fi
  echo "relaunch: T$tl opened no device ($(grep -m1 -E 'refused, no device opened|GATE-STOP' "$L" | cut -c21-200)): this is its one relaunch"
done
EOF2
  cat "$RB_E195_DIR/rest_rule_e195.sh"
  cat <<'EOF2'
mkdir -p build/e195 build/q141k
T0=$(date +%s)
echo "$T0" > build/q141k/e195.T0
DL=$((T0 + CAP)); [ "$LE" -lt "$DL" ] && DL=$LE
E195_T0=$T0 X9_LATEST_START=@$LS X9_DEADLINE=@$DL E195_HARNESS_SHA256=$HS setsid nohup bash "$ER/tools/claims-v3/e195/session_e195.sh" > "build/e195/launch-T$T0.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e195 T0 $T0 $(date '+%F %T %Z') (last start $LAST_START, last end $LAST_END; X9_DEADLINE $(date -d @$DL '+%T %Z'): the earlier of the last end and the launch + $((CAP / 60)) minutes)"
tail -n 8 "build/e195/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e195, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e195
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^relaunch: ' && { grep -m1 '^relaunch: ' "$RB_CAP" > "$RB_OUT/e195-relaunch.txt"; echo "$(date '+%F %T %Z') step=$RB_STEP $(cat "$RB_OUT/e195-relaunch.txt")" >> "$RB_LOG"; }
t0=$(rb_val '^LAUNCHED e195 T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e195-T0.txt"
rb_say "e195 launched on aifoundry3 (T0 $t0); wait with s20_wait_e195.sh (bounded), and read its smoke gates"
