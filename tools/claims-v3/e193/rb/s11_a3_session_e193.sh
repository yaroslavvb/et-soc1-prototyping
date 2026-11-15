#!/usr/bin/env bash
# E193 (Q177, the kit), the box step "the session" (this file is s11), ONE SITTING A CALL: E193's sitting on aifoundry3 card 0, launched
# detached on the box (it returns at once), only after steps 5-8 read clean that day. E189's step 9's form
# (tools/claims-v3/e189/rb/s11_a3_session_e189.sh): the window rule (written today for E193 and this sitting), the last start, THE
# SITTING'S CAP BEFORE THE LAST END (sitting A 3,600 s, B 3,000 s), k6's guard (no dry pass running, no card session of ours:
# rb_guard_text), THE REST RULE (rb/rest_rule_e193.sh: every session-log form of ours, E183's, E189's, E192's and E193's own first
# sitting among them, a session cut mid-queue counted at its run's latest write; it refuses before 40 minutes), today's dry pass for
# this sitting (a3-dry-e193-<sitting> ended rc 0 today), today's build (X04-BUILT in a3-build-e193's output today and E193's root's
# build/x04clock-built.txt written today), NO SECOND TRY OF A SITTING ON THE DAY ITS SMOKE GATE FAILED (a real E193 session log of this
# sitting on the box with today's "GATE-STOP: the smoke gate failed" line: E193.md 11, "no sitting that day"; fix-e193), and for
# sitting B, SITTING A HELD FIRST (a real E193 sitting-A session log on the box whose main run started and which reached "session end":
# E193.md 6, "B never runs before A without a dated amendment") AND NO CRASHED SITTING A (a sitting-A log whose main run "ended without
# a registered stop": no further sitting before a dated note decides whether its passes are reduced; fix-e193); then
# session_e193.sh <sitting> detached, DRY unset, with the T0 written on the box (build/q141k/e193-<sitting>.T0) and in RB_OUT
# (e193-<sitting>-T0.txt), which steps 10 and 11 read, the window's last end and harness-e193.json's sha256 from the lab clone.
#   bash tools/claims-v3/e193/rb/s11_a3_session_e193.sh A|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e193.sh"
rb_init s11_a3_session
sit=${1:-}
cap=$(e193_cap_s "$sit") || rb_die $RB_E_USAGE "usage: s11_a3_session_e193.sh A|B (the sitting this RB_OUT's window names)"
e193_window "$sit"
rb_need_start
rb_need_end "$cap"
[ -n "${RB_DRY:-}" ] || e193_built_today || rb_die $RB_E_USAGE "x04clock was not built today (RB_OUT/e193-built.txt, step 6's wait): run step 6 first"
hs=$(e193_harness_sha); [ -n "${RB_DRY:-}" ] && hs=${hs:-HARNESS-SHA256}
[ -n "$hs" ] || rb_die $RB_E_USAGE "harness-e193.json's sha256 could not be read in the lab clone"
f=$(rb_file e193)
{ rb_prelude aifoundry3
  echo "SIT=$sit; ROOT=$E193_ROOT; HSHA=$hs; DEADLINE=${RB_LAST_END_EPOCH:-0}; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E193_DIR/rest_rule_e193.sh"
  cat <<'EOF2'
job_ok_today "a3-dry-e193-$SIT" || { echo "REFUSED: E193 sitting $SIT's dry pass (step 8's job a3-dry-e193-$SIT) has not ended rc 0 today"; exit 3; }
echo "dry pass: a3-dry-e193-$SIT ended rc 0 today"
fresh build/q141k/jobs/a3-build-e193.out && grep -q '^X04-BUILT rc=0' build/q141k/jobs/a3-build-e193.out ||
  { echo "REFUSED: x04clock was not built today (step 6's job a3-build-e193)"; exit 3; }
fresh "$ROOT/build/x04clock-built.txt" || { echo "REFUSED: E193's root holds no build record written today"; exit 3; }
echo "build: X04-BUILT today"
today=$(date +%F)
for L in build/e193/T[0-9]*/session.log; do
  [ -f "$L" ] || continue
  case "$L" in *-dry*) continue ;; esac
  grep -q "E193 sitting $SIT" "$L" || continue
  if grep -qE "^$today [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ GATE-STOP: the smoke gate failed" "$L"; then
    echo "REFUSED: E193 sitting $SIT ended at its smoke gate today (${L%/session.log}): no sitting that day (E193.md 11)"; exit 3
  fi
done
if [ "$SIT" = B ]; then
  a=""; cr=""
  for L in build/e193/T[0-9]*/session.log; do
    [ -f "$L" ] || continue
    case "$L" in *-dry*) continue ;; esac
    grep -q 'E193 sitting A' "$L" && grep -q 'main run start' "$L" && grep -q 'session end' "$L" || continue
    if grep -q 'main run ended without a registered stop' "$L"; then cr=$L; else a=$L; fi
  done
  [ -z "$cr" ] || { echo "REFUSED: E193 sitting A's main run ended without a registered stop (a crash: ${cr%/session.log}): no further sitting before a dated note decides whether its passes are reduced (CARD-LANE-BRIEF.md section 3)"; exit 3; }
  [ -n "$a" ] || { echo "REFUSED: no E193 sitting A on this box whose main run started and ended: B never runs before A (E193.md 6)"; exit 3; }
  echo "sitting A held first: ${a%/session.log}"
fi
mkdir -p build/e193 build/q141k
T0=$(date +%s)
echo "$T0" > "build/q141k/e193-$SIT.T0"
env -u DRY E193_T0="$T0" E193_LAST_END_EPOCH="$DEADLINE" E193_HARNESS_SHA256="$HSHA" setsid nohup bash "$ROOT/tools/claims-v3/e193/session_e193.sh" "$SIT" > "build/q141k/e193-$SIT-T$T0.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e193-$SIT T0 $T0 $(date '+%F %T %Z') (sitting $SIT; last start $LAST_START, last end $LAST_END)"
tail -n 6 "build/e193/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch E193 sitting $sit, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched "e193-$sit"
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
t0=$(rb_val "^LAUNCHED e193-$sit T0 ([0-9]+) .*\$")
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e193-$sit-T0.txt"
rb_say "E193 sitting $sit launched on aifoundry3 (T0 $t0); wait with s20_wait_e193.sh $sit (bounded)"
