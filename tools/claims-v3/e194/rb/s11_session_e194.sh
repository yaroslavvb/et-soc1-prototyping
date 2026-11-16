#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum), the box step "the session" (this file
# is s11): E194's card session on aifoundry2's own card 0, launched detached on the box (it returns at once), ONLY after steps 4-8 read
# clean. E191's step 9 (tools/claims-v3/e191/rb/s11_a1_session_e191.sh, unchanged beside it) with E194's box, and THE QUIET DESK FLAG's
# count (E190's card-lane brief, dated note 1, section 4) in the same box call as the launch:
#   - the window rule (written today for E194), the last start, the session's cap of 110 card-minutes before the last end (6,600 s);
#   - THE QUIET DESK FLAG raised (e194_quiet);
#   - k6's guard (rb_guard_text: no dry pass running, no card session of ours on aifoundry2 by E194's ours_live, and aifoundry2 booted
#     before E69's firmware read of record, 2026-10-27 13:56:26 PDT, else IDENTITY-STOP: 16, nothing launched);
#   - THE REST RULE (rb/rest_rule_e194.sh: every session-log form of ours in every tree of ours on aifoundry2, E190 arm A's among them);
#   - today's dry pass (a2-dry-e194 ended rc 0 today) and today's build (the programs in RB_OUT/e194-built.txt, step 6's wait);
#   - THE P2 COUNT, right before the launch: device-named processes of ours and session or queue scripts of ours on this box must read 0;
#     read again up to 5 times 2 s apart (our own live collector's `ettelem temp` lives for a moment once a second while nothing holds the
#     card), else REFUSED (10): no launch;
#   - then session_e194.sh detached (ET_DEVICES and V3_DEVICE unset in its environment and the runner's) with the T0 written on the box
#     (build/q141k/e194.T0) and in RB_OUT (e194-T0.txt), which steps 10 and 11 read.
# --rapl-allowed only when his go allows a read of the host's package counter (default no).
#   RB_QUIET=<the flag file> bash tools/claims-v3/e194/rb/s11_session_e194.sh FULL [--rapl-allowed]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e194.sh"
rb_init s11_session
plan=${1:-}
[ "$plan" = FULL ] || rb_die $RB_E_USAGE "E194 has one plan: FULL (the registered session; E194.md sections 9-10)"
rapl=""; [ "${2:-}" = --rapl-allowed ] && rapl=yes
e194_window
rb_need_start
rb_need_end "$E194_BUDGET_S"
e194_quiet
prog=$(e194_programs)
[ -n "${RB_DRY:-}" ] && prog=${prog:-ledger,spp}
[ -n "$prog" ] || rb_die $RB_E_USAGE "no program was built today (RB_OUT/e194-built.txt, step 6's wait): run step 6 first"
f=$(rb_file e194)
{ rb_prelude aifoundry2
  echo "PROG=$prog; DEADLINE=${RB_LAST_END_EPOCH:-0}; RAPL=$rapl; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E194_DIR/rest_rule_e194.sh"
  cat <<'EOF2'
job_ok_today a2-dry-e194 || { echo "REFUSED: E194's dry pass (step 8's job a2-dry-e194) has not ended rc 0 today"; exit 3; }
echo "dry pass: a2-dry-e194 ended rc 0 today"
for p in ${PROG//,/ }; do
  case "$p" in ledger) w='^LEDGER-BUILT rc=0' ;; spp) w='^SPP-BUILT rc=0' ;; *) echo "REFUSED: unknown program $p"; exit 3 ;; esac
  fresh build/q141k/jobs/a2-build-e194.out && grep -q "$w" build/q141k/jobs/a2-build-e194.out ||
    { echo "REFUSED: $p was not built today (step 6's job a2-build-e194)"; exit 3; }
done
i=0
while :; do
  i=$((i + 1)); P2=$(p2_count); echo "quiet desk: $P2 (read $i)"
  case "$P2" in "P2 0 "*) break ;; esac
  [ "$i" -ge 5 ] && { echo "REFUSED: the P2 count is not 0 after $i reads (a device-named process or a session or queue script of ours on aifoundry2): no launch"; exit 3; }
  sleep 2
done
mkdir -p build/e194 build/q141k
T0=$(date +%s)
echo "$T0" > build/q141k/e194.T0
unset ET_DEVICES V3_DEVICE
E194_T0=$T0 E194_PROGRAMS="$PROG" E194_DEADLINE_EPOCH="$DEADLINE" E194_RAPL="$RAPL" setsid nohup bash tools/claims-v3/e194/session_e194.sh > build/e194/session.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e194 T0 $T0 $(date '+%F %T %Z') (programs $PROG; last start $LAST_START, last end $LAST_END; package counter: ${RAPL:-not read})"
tail -n 6 "build/e194/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry2
rb_remote launch aifoundry2 "launch e194, detached (programs $prog)" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e194
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^quiet desk: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep '^quiet desk: ' "$RB_CAP" | tail -n 1)" >> "$RB_LOG"
t0=$(rb_val '^LAUNCHED e194 T0 ([0-9]+) .*$')
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e194-T0.txt"
rb_say "e194 launched on aifoundry2 card 0 (programs $prog, T0 $t0); wait with s20_wait_e194.sh (bounded), and read its identity lines, stop-path test, smoke gate and each pass's clock"
