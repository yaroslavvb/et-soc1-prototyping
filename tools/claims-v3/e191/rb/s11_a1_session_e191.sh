#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum), the box step "the session" (this file
# is s11): E191's card session on aifoundry1 card 1, launched detached on the box (it returns at once), ONLY after steps 4-8 read clean (on
# a day with a post, after the post). E189's step 9 (tools/claims-v3/e189/rb/s11_a3_session_e189.sh, unchanged beside it) with E191's box:
# the window rule (written today for E191), the last start, the session's cap of 110 card-minutes before the last end (6,600 s), k6's guard
# (rb_guard_text: no dry pass running, no card session of ours on aifoundry1 by E191's ours_live, either card, and aifoundry1 booted before
# E82's firmware read of record), THE REST RULE (rb/rest_rule_e191.sh: every session-log form of ours in every tree of ours on aifoundry1,
# E190 arm B's among them; a session cut mid-queue counted at its run's latest write), today's dry pass (a1-dry-e191 ended rc 0 today) and
# today's build (the programs in RB_OUT/e191-built.txt, step 6's wait), then session_e191.sh detached (ET_DEVICES=1 in its environment and
# the runner's) with the T0 written on the box (build/q141k/e191.T0) and in RB_OUT (e191-T0.txt), which steps 10 and 11 read.
# --rapl-allowed only when his go allows a read of the host's package counter (default no).
#   bash tools/claims-v3/e191/rb/s11_a1_session_e191.sh FULL [--rapl-allowed]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e191.sh"
rb_init s11_a1_session
plan=${1:-}
[ "$plan" = FULL ] || rb_die $RB_E_USAGE "E191 has one plan: FULL (the registered session; E191.md sections 9-10)"
rapl=""; [ "${2:-}" = --rapl-allowed ] && rapl=yes
e191_window
rb_need_start
rb_need_end "$E191_BUDGET_S"
prog=$(e191_programs)
[ -n "${RB_DRY:-}" ] && prog=${prog:-ledger,spp}
[ -n "$prog" ] || rb_die $RB_E_USAGE "no program was built today (RB_OUT/e191-built.txt, step 6's wait): run step 6 first"
f=$(rb_file e191)
{ rb_prelude aifoundry1
  echo "PROG=$prog; DEADLINE=${RB_LAST_END_EPOCH:-0}; RAPL=$rapl; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E191_DIR/rest_rule_e191.sh"
  cat <<'EOF2'
job_ok_today a1-dry-e191 || { echo "REFUSED: E191's dry pass (step 8's job a1-dry-e191) has not ended rc 0 today"; exit 3; }
echo "dry pass: a1-dry-e191 ended rc 0 today"
for p in ${PROG//,/ }; do
  case "$p" in ledger) w='^LEDGER-BUILT rc=0' ;; spp) w='^SPP-BUILT rc=0' ;; *) echo "REFUSED: unknown program $p"; exit 3 ;; esac
  fresh build/q141k/jobs/a1-build-e191.out && grep -q "$w" build/q141k/jobs/a1-build-e191.out ||
    { echo "REFUSED: $p was not built today (step 6's job a1-build-e191)"; exit 3; }
done
mkdir -p build/e191 build/q141k
T0=$(date +%s)
echo "$T0" > build/q141k/e191.T0
E191_T0=$T0 E191_PROGRAMS="$PROG" E191_DEADLINE_EPOCH="$DEADLINE" E191_RAPL="$RAPL" ET_DEVICES=1 V3_DEVICE=1 setsid nohup bash tools/claims-v3/e191/session_e191.sh > build/e191/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e191 T0 $T0 $(date '+%F %T %Z') (programs $PROG; last start $LAST_START, last end $LAST_END; package counter: ${RAPL:-not read})"
tail -n 6 "build/e191/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry1
rb_remote launch aifoundry1 "launch e191, detached (programs $prog)" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e191
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
t0=$(rb_val '^LAUNCHED e191 T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e191-T0.txt"
rb_say "e191 launched on aifoundry1 card 1 (programs $prog, T0 $t0); wait with s20_wait_e191.sh (bounded), and read its identity lines, stop-path test and smoke gate"
