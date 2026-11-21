#!/usr/bin/env bash
# E224's arm A in E213's Amendment A2 form (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum; E213's A2 by Q219's lane a2-e213, landed 8b675547, run by card-e213b2 on Wed 18 Nov 2026), STEP 9 FOR ARM A, in place of the kit's
# tools/claims-v3/e224/rb/s11_session_e224a.sh (landed in 6efdb002, unchanged beside this file; arm A keeps it). It is that file LINE FOR LINE but
# for three things, each marked A2:
#   - A2 is arm A's alone (arm A is refused, 10);
#   - before anything reaches the box, A2's step 4 must have passed today in this RB_OUT (RB_OUT/e224a-a2-look-A.txt: "A2-LOOK-A: CONTINUITY" or
#     "A2-LOOK-A: EQUAL <record>"), else 10;
#   - THE LAUNCH GUARD in the ONE launch call is A2's (rb/rb_e224a_a2.sh, e224a_a2_guard_text) in place of k6's rb_guard_text: k6's two lines (no
#     session during a dry pass of the runbook, none beside another session of ours) verbatim, then A2's box files at their pinned sha256, then
#     `fwgate.py guard --box aifoundry1 --card 1 --extra build/e224a/fwgate-A-<day>`: "identity: ... ok" (this boot's EQUAL read of today in that
#     folder, or a boot before the newest committed record of card 1) goes on; IDENTITY-STOP (no EQUAL of this boot, a stale EQUAL of an earlier
#     boot or day, any read of this boot that did not end EQUAL in fwgate's ledger or the folder, the pins off) launches nothing: 16.
# Everything else is the kit's: the last start (k6's rb_need_start), the cap before the last end (rb_need_end with the arm's E224A_BUDGET_S),
# today's build of both kernels (step 6), today's never-run report (step 6n), then in the ONE launch: the guard, THE REST RULE
# (rb/rest_rule_e224a.sh), THE HUNG MARKER, THE SAME-DAY RULE, today's dry pass and build, then session_e224a.sh detached (setsid nohup; arm A with
# ET_DEVICES=1, which the wrapper sets), its T0 on the box and in RB_OUT/e224a-T0-A.txt.
#   bash tools/claims-v3/e224/a2/rb/s11_session_e224a_a2.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e224a_a2.sh"
rb_init s11_session_a2
e224a_arm "${1:-}"
e224a_a2_only_A                                                                                                  # A2
e224a_jobs "$ARM"
e224a_window
rb_need_start
rb_need_end "$E224A_BUDGET_S"
b=$(e224a_built "$ARM")
[ -n "${RB_DRY:-}" ] && b=${b:-rgm}
[ "$b" = rgm ] || rb_die $RB_E_USAGE "rgm136 and rgm211 were not built today (RB_OUT/e224a-built-$ARM.txt, step 6's wait): run step 6 first"
if [ -z "${RB_DRY:-}" ]; then      # step 6n's report written today (step 7 needed it under 30 minutes old before the day's first card command)
  [ -s "$RB_OUT/e224a-neverrun-$ARM.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e224a-neverrun-$ARM.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "no never-run report from today in RB_OUT (step 6n, then step 7, come before the session)"
  lk="$RB_OUT/e224a-a2-look-A.txt"                                                                              # A2
  [ -s "$lk" ] && [ "$(TZ=America/Los_Angeles date -r "$lk" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] && grep -qE 'A2-LOOK-A: (CONTINUITY: |EQUAL fwgate-aifoundry1-c1-[0-9]{8}-[0-9]{6}\.json)' "$lk" ||
    rb_die $RB_E_USAGE "A2's step 4 has not passed today in this RB_OUT (RB_OUT/e224a-a2-look-A.txt): run s05_look_e224a_a2.sh A first"
else
  echo "--- gate: RB_OUT/e224a-neverrun-$ARM.txt (step 6n's) written today"
  echo "--- gate (A2): RB_OUT/e224a-a2-look-A.txt (A2's step 4) written today, reading CONTINUITY or EQUAL"
fi
f=$(rb_file e224a)
{ rb_prelude "$BOX"
  echo "ARM=$ARM; JD=$JOB_DRY; JB=$JOB_BUILD; DEADLINE=${RB_LAST_END_EPOCH:-0}; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  echo "FWDIR=$(printf '%q' "$(e224a_a2_dir)")"                                                                 # A2
  e224a_a2_guard_text                                                                                            # A2: in place of rb_guard_text
  cat "$RB_E224A_DIR/rest_rule_e224a.sh"
  e224a_hung_text
  cat <<'EOF2'
TODAY=$(TZ=America/Los_Angeles date +%F)
opened=0; nodev=0
for L in build/e224a/T*-"$ARM"/session.log; do
  [ -f "$L" ] || continue
  [ "$(TZ=America/Los_Angeles date -r "$L" +%F 2>/dev/null)" = "$TODAY" ] || continue
  if grep -q 'the first card command' "$L"; then opened=$((opened + 1)); else nodev=$((nodev + 1)); fi
done
[ "$opened" -eq 0 ] || { echo "REFUSED: the same-day rule: an E224 session opened the card earlier today ($opened): not again today"; exit 3; }
[ "$nodev" -lt 2 ] || { echo "REFUSED: the same-day rule: $nodev E224 sessions that opened no device ran today: a third try is not made"; exit 3; }
echo "same-day: E224 sessions today: $opened that opened the card, $nodev that opened no device"
job_ok_today "$JD" || { echo "REFUSED: E224's dry pass (step 8's job $JD) has not ended rc 0 today"; exit 3; }
echo "dry pass: $JD ended rc 0 today"
fresh "build/q141k/jobs/$JB.out" && grep -q '^RGM-BUILT rc=0' "build/q141k/jobs/$JB.out" ||
  { echo "REFUSED: rgm136 and rgm211 were not built today (step 6's job $JB)"; exit 3; }
mkdir -p build/e224a build/q141k
T0=$(date +%s)
echo "$T0" > "build/q141k/e224a$ARM.T0"
E224A_T0=$T0 E224A_ARM=$ARM E224A_DEADLINE_EPOCH="$DEADLINE" setsid nohup bash tools/claims-v3/e224/session_e224a.sh > "build/e224a/session-$ARM.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e224a arm $ARM T0 $T0 $(date '+%F %T %Z') (last start $LAST_START, last end $LAST_END; session_e224a.sh)"
tail -n 6 "build/e224a/T$T0-$ARM/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe "$BOX"
rb_remote launch "$BOX" "launch e224a arm $ARM, detached, past A2's firmware guard" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
if rb_has '^IDENTITY-STOP'; then                                                                              # A2: the guard's words, not k6's
  echo "$(date '+%F %T %Z') step=$RB_STEP A2 guard: $(grep -m1 '^IDENTITY-STOP' "$RB_CAP" | cut -c1-240)" >> "$RB_LOG"
  rb_die $RB_E_GATE "$(grep -m1 '^IDENTITY-STOP' "$RB_CAP" | cut -c1-300) (Amendment A2: fwgate's guard): nothing launched; no session on this boot; tell the orchestrator"
fi
rb_launched "e224a arm $ARM"
for k in A2-PINS A2-GUARD identity rest note hung same-day; do rb_has "^$k: |^$k " && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 -E "^$k: |^$k " "$RB_CAP")" >> "$RB_LOG"; done
t0=$(rb_val "^LAUNCHED e224a arm $ARM T0 ([0-9]+) .*\$")
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e224a-T0-$ARM.txt"
rb_say "e224a arm $ARM launched on $BOX (T0 $t0) past A2's firmware guard ($(grep -m1 '^identity: ' "$RB_CAP" | cut -c1-160)); wait with s20_wait_e224a.sh $ARM (bounded), and read its identity gate, identity read, smoke and stop-path test"
