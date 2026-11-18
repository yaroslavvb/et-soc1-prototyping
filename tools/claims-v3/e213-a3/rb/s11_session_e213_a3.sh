#!/usr/bin/env bash
# E213 Amendment A3 (Q219, lane a3-e213, Wed 18 Nov 2026, before any datum of E213's arm B), STEP 9 FOR ARM B AS AMENDED BY A2 AND A3, in place
# of Amendment A2's tools/claims-v3/e213-a2/rb/s11_session_e213_a2.sh (itself in place of the kit's rb/s11_session_e213.sh; both unchanged beside
# this file; arm A keeps the kit's). It is A2's file LINE FOR LINE but for four things, each marked A3:
#   - A3 is arm B's alone (arm A is refused, 10);
#   - before anything reaches the box, A3's row 5b must have passed today in this RB_OUT (RB_OUT/e213-a3-sync-B.txt: "A3-SYNC-B: OK"), beside
#     A2's step 4 (RB_OUT/e213-a2-look-B.txt), else 10;
#   - in the ONE launch call, right after A2's launch guard (k6's two lines, A2's pins, fwgate's guard): A3's three box files at their pinned
#     sha256 on the box ("A3-PINS OK 3 of 3") and A3's order check there (`run_e213_a3.py check`: "A3-ORDER OK: ..."), else "A3-STOP: ...",
#     nothing launched: 16;
#   - the session started is A3's tools/claims-v3/e213-a3/session_e213.sh (the kit's wrapper line for line, but it starts A3's runner wrapper,
#     which runs the kit's run_e213.py unchanged with arm B's order read from sequence-B-a3.json); its file name is the kit's, so steps 10 and 11
#     count it by name as they would the kit's.
# Everything else is A2's and the kit's: the last start (k6's rb_need_start), the cap before the last end (rb_need_end with the arm's
# E213_BUDGET_S), today's build of both kernels (step 6), today's never-run report (step 6n), A2's step 4 from today, then in the ONE launch: A2's
# guard, A3's check, THE REST RULE (rb/rest_rule_e213.sh), THE HUNG MARKER, THE SAME-DAY RULE, today's dry pass and build, then the session
# detached (setsid nohup; ET_DEVICES=1, which the wrapper sets), its T0 on the box and in RB_OUT/e213-T0-B.txt.
#   bash tools/claims-v3/e213-a3/rb/s11_session_e213_a3.sh B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e213_a3.sh"                                                              # A3: A3's file, which sources A2's
rb_init s11_session_a3                                                                                         # A3
e213_arm "${1:-}"
e213a2_only_B
e213a3_only_B                                                                                                  # A3
e213_jobs "$ARM"
e213_window
rb_need_start
rb_need_end "$E213_BUDGET_S"
b=$(e213_built "$ARM")
[ -n "${RB_DRY:-}" ] && b=${b:-rgm}
[ "$b" = rgm ] || rb_die $RB_E_USAGE "rgm136 and rgm211 were not built today (RB_OUT/e213-built-$ARM.txt, step 6's wait): run step 6 first"
if [ -z "${RB_DRY:-}" ]; then      # step 6n's report written today (step 7 needed it under 30 minutes old before the day's first card command)
  [ -s "$RB_OUT/e213-neverrun-$ARM.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e213-neverrun-$ARM.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "no never-run report from today in RB_OUT (step 6n, then step 7, come before the session)"
  lk="$RB_OUT/e213-a2-look-B.txt"
  [ -s "$lk" ] && [ "$(TZ=America/Los_Angeles date -r "$lk" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] && grep -qE 'A2-LOOK-B: (CONTINUITY: |EQUAL fwgate-aifoundry1-c1-[0-9]{8}-[0-9]{6}\.json)' "$lk" ||
    rb_die $RB_E_USAGE "A2's step 4 has not passed today in this RB_OUT (RB_OUT/e213-a2-look-B.txt): run s05_look_e213_a2.sh B first"
  sk="$RB_OUT/e213-a3-sync-B.txt"                                                                              # A3
  [ -s "$sk" ] && [ "$(TZ=America/Los_Angeles date -r "$sk" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] && grep -qE '^[0-9-]+ [0-9:]+ [A-Z]+ A3-SYNC-B: OK; ' "$sk" ||
    rb_die $RB_E_USAGE "A3's row 5b has not passed today in this RB_OUT (RB_OUT/e213-a3-sync-B.txt): run s07b_sync_e213_a3.sh B first"
else
  echo "--- gate: RB_OUT/e213-neverrun-$ARM.txt (step 6n's) written today"
  echo "--- gate (A2): RB_OUT/e213-a2-look-B.txt (A2's step 4) written today, reading CONTINUITY or EQUAL"
  echo "--- gate (A3): RB_OUT/e213-a3-sync-B.txt (A3's row 5b) written today, reading A3-SYNC-B: OK"
fi
f=$(rb_file e213)
{ rb_prelude "$BOX"
  echo "ARM=$ARM; JD=$JOB_DRY; JB=$JOB_BUILD; DEADLINE=${RB_LAST_END_EPOCH:-0}; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  echo "FWDIR=$(printf '%q' "$(e213a2_dir)")"
  e213a2_guard_text
  e213a3_box_text "nothing launched"                                                                           # A3: after A2's guard
  cat "$RB_E213_DIR/rest_rule_e213.sh"
  e213_hung_text
  cat <<'EOF2'
TODAY=$(TZ=America/Los_Angeles date +%F)
opened=0; nodev=0
for L in build/e213/T*-"$ARM"/session.log; do
  [ -f "$L" ] || continue
  [ "$(TZ=America/Los_Angeles date -r "$L" +%F 2>/dev/null)" = "$TODAY" ] || continue
  if grep -q 'the first card command' "$L"; then opened=$((opened + 1)); else nodev=$((nodev + 1)); fi
done
[ "$opened" -eq 0 ] || { echo "REFUSED: the same-day rule: an E213 session opened the card earlier today ($opened): not again today"; exit 3; }
[ "$nodev" -lt 2 ] || { echo "REFUSED: the same-day rule: $nodev E213 sessions that opened no device ran today: a third try is not made"; exit 3; }
echo "same-day: E213 sessions today: $opened that opened the card, $nodev that opened no device"
job_ok_today "$JD" || { echo "REFUSED: E213's dry pass (step 8's job $JD) has not ended rc 0 today"; exit 3; }
echo "dry pass: $JD ended rc 0 today"
fresh "build/q141k/jobs/$JB.out" && grep -q '^RGM-BUILT rc=0' "build/q141k/jobs/$JB.out" ||
  { echo "REFUSED: rgm136 and rgm211 were not built today (step 6's job $JB)"; exit 3; }
mkdir -p build/e213 build/q141k
T0=$(date +%s)
echo "$T0" > "build/q141k/e213$ARM.T0"
E213_T0=$T0 E213_ARM=$ARM E213_DEADLINE_EPOCH="$DEADLINE" setsid nohup bash tools/claims-v3/e213-a3/session_e213.sh > "build/e213/session-$ARM.out" 2>&1 < /dev/null &   # A3: A3's session wrapper
sleep 5
echo "LAUNCHED e213 arm $ARM T0 $T0 $(date '+%F %T %Z') (last start $LAST_START, last end $LAST_END; session_e213.sh, Amendment A3's: tools/claims-v3/e213-a3/)"   # A3
tail -n 6 "build/e213/T$T0-$ARM/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe "$BOX"
rb_remote launch "$BOX" "launch e213 arm $ARM in A3's order, detached, past A2's firmware guard and A3's order check" "$f"   # A3
[ -n "${RB_DRY:-}" ] && exit 0
if rb_has '^IDENTITY-STOP'; then
  echo "$(date '+%F %T %Z') step=$RB_STEP A2 guard: $(grep -m1 '^IDENTITY-STOP' "$RB_CAP" | cut -c1-240)" >> "$RB_LOG"
  rb_die $RB_E_GATE "$(grep -m1 '^IDENTITY-STOP' "$RB_CAP" | cut -c1-300) (Amendment A2: fwgate's guard): nothing launched; no session on this boot; tell the orchestrator"
fi
if rb_has '^A3-STOP'; then                                                                                     # A3: its check's words
  echo "$(date '+%F %T %Z') step=$RB_STEP A3 check: $(grep -m1 '^A3-STOP' "$RB_CAP" | cut -c1-240)" >> "$RB_LOG"
  rb_die $RB_E_GATE "$(grep -m1 '^A3-STOP' "$RB_CAP" | cut -c1-300) (Amendment A3's order check): nothing launched; no session until it passes; tell the orchestrator"
fi
rb_launched "e213 arm $ARM"
for k in A2-PINS A2-GUARD A3-PINS A3-ORDER identity rest note hung same-day; do rb_has "^$k: |^$k " && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 -E "^$k: |^$k " "$RB_CAP" | cut -c1-300)" >> "$RB_LOG"; done   # A3: A3's two lines
t0=$(rb_val "^LAUNCHED e213 arm $ARM T0 ([0-9]+) .*\$")
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e213-T0-$ARM.txt"
rb_say "e213 arm $ARM launched on $BOX (T0 $t0) in A3's order, past A2's firmware guard ($(grep -m1 '^identity: ' "$RB_CAP" | cut -c1-160)) and A3's order check; wait with s20_wait_e213.sh $ARM (bounded), and read its identity gate, identity read, smoke and stop-path test"   # A3
