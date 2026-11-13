#!/usr/bin/env bash
# E189 (Q167, the kit), the box step "the session" (this file is s11): E189's card session on aifoundry3, launched detached on the box (it
# returns at once), ONLY after the day's post names aifoundry3 and steps 5-8 read clean. E188's step 9 v2's form
# (tools/claims-v3/e188/rb/s11_a3_session_e188_v2.sh): the window rule (written today for E189), the last start, the session's cap of 110
# card-minutes before the last end (6,600 s), k6's guard (no dry pass running, no card session of ours: rb_guard_text), THE REST RULE
# (rb/rest_rule_e189.sh: every session-log form of ours, a session cut mid-queue counted at its run's latest write), today's dry pass
# (a3-dry-e189 ended rc 0 today) and today's build (the programs in RB_OUT/e189-built.txt, step 6's wait), then session_e189.sh detached
# with the T0 written on the box (build/q141k/e189.T0) and in RB_OUT (e189-T0.txt), which steps 10 and 11 read. --rapl-allowed only when
# his go allows a read of the host's package counter (default no).
#   bash tools/claims-v3/e189/rb/s11_a3_session_e189.sh FULL [--rapl-allowed]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e189.sh"
rb_init s11_a3_session
plan=${1:-}
[ "$plan" = FULL ] || rb_die $RB_E_USAGE "E189 has one plan: FULL (the registered session; E189.md sections 9-10)"
rapl=""; [ "${2:-}" = --rapl-allowed ] && rapl=yes
e189_window
rb_need_start
rb_need_end "$E189_BUDGET_S"
prog=$(e189_programs)
[ -n "${RB_DRY:-}" ] && prog=${prog:-ledger,spp}
[ -n "$prog" ] || rb_die $RB_E_USAGE "no program was built today (RB_OUT/e189-built.txt, step 6's wait): run step 6 first"
f=$(rb_file e189)
{ rb_prelude aifoundry3
  echo "PROG=$prog; DEADLINE=${RB_LAST_END_EPOCH:-0}; RAPL=$rapl; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E189_DIR/rest_rule_e189.sh"
  cat <<'EOF2'
job_ok_today a3-dry-e189 || { echo "REFUSED: E189's dry pass (step 8's job a3-dry-e189) has not ended rc 0 today"; exit 3; }
echo "dry pass: a3-dry-e189 ended rc 0 today"
for p in ${PROG//,/ }; do
  case "$p" in ledger) w='^LEDGER-BUILT rc=0' ;; spp) w='^SPP-BUILT rc=0' ;; *) echo "REFUSED: unknown program $p"; exit 3 ;; esac
  fresh build/q141k/jobs/a3-build-e189.out && grep -q "$w" build/q141k/jobs/a3-build-e189.out ||
    { echo "REFUSED: $p was not built today (step 6's job a3-build-e189)"; exit 3; }
done
mkdir -p build/e189 build/q141k
T0=$(date +%s)
echo "$T0" > build/q141k/e189.T0
E189_T0=$T0 E189_PROGRAMS="$PROG" E189_DEADLINE_EPOCH="$DEADLINE" E189_RAPL="$RAPL" setsid nohup bash tools/claims-v3/e189/session_e189.sh > build/e189/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e189 T0 $T0 $(date '+%F %T %Z') (programs $PROG; last start $LAST_START, last end $LAST_END; package counter: ${RAPL:-not read})"
tail -n 6 "build/e189/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch e189, detached (programs $prog)" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e189
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
t0=$(rb_val '^LAUNCHED e189 T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e189-T0.txt"
rb_say "e189 launched on aifoundry3 (programs $prog, T0 $t0); wait with s20_wait_e189.sh (bounded), and read its stop-path test and smoke gate"
