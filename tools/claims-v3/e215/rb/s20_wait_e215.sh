#!/usr/bin/env bash
# E215 (Q224, lane kit-e215, Thu 19 Nov 2026, before any E215 datum), the box step "the wait" (this file is s20; step 10): E211's step 10
# (tools/claims-v3/e211/rb/s20_wait_e211.sh, landed in 2b7f261f) for E215's arm: one bounded wait (k6's wait class) on the T0 this RB_OUT
# launched (RB_OUT/e215-T0-<arm>.txt and the box's build/q141k/e215<arm>.T0, written today), reading the session log until it ends, hangs or
# the wait's bound passes; the words it prints:
#   - HUNG (a device process did not end after its timeout's TERM): 16, KILL NOTHING, reset nothing, keep the booking and the hold;
#   - K1-STOPPED, CRASHED, GATE-STOPPED: 16 (each read and collected as CARD-LANE-BRIEF.md 3 says);
#   - RUN-ENDED with MANIFEST-WRITTEN and RUNNER-RC 0 (a stop line, a holder, a kernel stop, an identity gate failure or two failed 'rgm136 gemmL'
#     processes end a session rc 0: read its "STOP: ..." line among the lines printed): 0;
#   - RUN-RUNNING 17; RUN-GONE (no session process and no session end) 14; MANIFEST-ABSENT 14; runner.rc not written 10 s after the end 14;
#     RUN-UNKNOWN (the box's T0 not written today, or not this RB_OUT's) 10.
#   bash tools/claims-v3/e215/rb/s20_wait_e215.sh A|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e215.sh"
rb_init s20_wait
e215_arm "${1:-}"
want=; [ -f "$RB_OUT/e215-T0-$ARM.txt" ] && want=$(cat "$RB_OUT/e215-T0-$ARM.txt")
[ -n "${RB_DRY:-}" ] || [ -n "$want" ] || rb_die $RB_E_USAGE "RB_OUT holds no e215-T0-$ARM.txt: step 9 has not launched E215 from this RB_OUT"
rb_probe "$BOX"
f=$(rb_file "wait-e215$ARM")
{ rb_prelude "$BOX"
  echo "ARM=$ARM; LIM=$RB_WAIT_LOOP_S; WANT='${want:-DRY}'"
  cat <<'EOF2'
fresh "build/q141k/e215$ARM.T0" || { echo "RUN-UNKNOWN e215 arm $ARM: not launched today by the runbook (no T0 written today)"; exit 3; }
T0=$(cat "build/q141k/e215$ARM.T0")
[ "$WANT" = DRY ] || [ "$T0" = "$WANT" ] || { echo "RUN-UNKNOWN e215 arm $ARM: the box's last launch T0 $T0 is not this runbook's $WANT"; exit 3; }
SD=build/e215/T$T0-$ARM; L=$SD/session.log
ended() { grep -q 'session end' "$L" 2>/dev/null; }
hung() { grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ HUNG: ' "$L" 2>/dev/null; }
while ! ended && ! hung && [ "$SECONDS" -lt "$LIM" ]; do
  [ "$(ours_live 'session_e215.sh')" -gt 0 ] || { sleep 2; ended || { echo "RUN-GONE e215 arm $ARM: no session process and no session end"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
grep -E 'session start|box and the build|first card command|config|identity|sampler|smoke|stop-path|run [0-9]+-|STOP|HUNG|K1|CRASH|no device opened|session end' "$L" 2>/dev/null | cut -c1-240 | tail -n 40
if hung; then echo "HUNG e215 arm $ARM"; fi
if ended; then
  echo "RUN-ENDED e215 arm $ARM"
  sleep 2
  if [ -s "$SD/MANIFEST.sha256" ]; then echo "MANIFEST-WRITTEN $(grep -c . "$SD/MANIFEST.sha256") files"; else echo "MANIFEST-ABSENT"; fi
  k=0; while [ ! -s "$SD/runner.rc" ] && [ "$k" -lt 10 ]; do sleep 1; k=$((k + 1)); done
  if [ -s "$SD/runner.rc" ]; then echo "RUNNER-RC $(cat "$SD/runner.rc")"; else echo "RUNNER-RC-ABSENT"; fi
else echo "RUN-RUNNING e215 arm $ARM after $t s"; fi
if grep -qE '^[0-9-]+ [0-9:]+ [A-Z]+ (STOP: )?K1: |STOP: K1: ' "$L" 2>/dev/null; then echo "K1-STOPPED e215 arm $ARM"; fi
if grep -qE '^[0-9-]+ [0-9:]+ [A-Z]+ CRASH' "$L" 2>/dev/null; then echo "CRASHED e215 arm $ARM"; fi
if grep -qE 'refused, no device opened|stop-path test failed|smoke gate failed|the gate, no launch|would not start' "$L" 2>/dev/null; then echo "GATE-STOPPED e215 arm $ARM"; fi
EOF2
} > "$f"
rb_remote wait "$BOX" "one bounded wait on e215 arm $ARM" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on e215 arm $ARM exited $RB_RC"
rb_has '^HUNG ' && rb_die $RB_E_GATE "e215 arm $ARM: a device process did not end after its timeout's TERM (the HUNG line above): KILL NOTHING, reset nothing; keep the booking, the hold and the card as they are; collect what is written (step 11), write it up and escalate to the owner (CARD-LANE-BRIEF.md 3)"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "e215 arm $ARM is not running and recorded no end: read the box's logs (read-only) before anything else; the rest rule then counts it at its run's latest write"
rb_has '^MANIFEST-ABSENT' && rb_die $RB_E_FAIL "e215 arm $ARM has ended but its MANIFEST.sha256 is not written: wait once more, then read the box (read-only) before step 11"
rb_has '^K1-STOPPED' && rb_die $RB_E_GATE "e215 arm $ARM stopped by K1 (a launch did not finish: it may leave a hung hart): collect it (step 11), never reset the card, write it up and escalate to the owner"
rb_has '^CRASHED' && rb_die $RB_E_GATE "e215 arm $ARM: the runner crashed (its CRASH line above): read runner.out read-only, report it, then collect (step 11)"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "e215 arm $ARM ended at a gate (the lines above): step 11 still collects it (a gate stop's record)"
if rb_has '^RUN-ENDED'; then
  rb_has '^RUNNER-RC-ABSENT' && rb_die $RB_E_FAIL "e215 arm $ARM: runner.rc not written 10 s after the session's end: wait once more, then read the box read-only"
  rc=$(rb_val '^RUNNER-RC ([0-9]+)$')
  [ "$rc" = 0 ] || rb_die $RB_E_GATE "e215 arm $ARM: the runner exited ${rc:-?} after the session's end and stopped at no gate the log names: read runner.out read-only, report it, then collect"
  rb_say "e215 arm $ARM has ended ($(grep -m1 '^MANIFEST-WRITTEN' "$RB_CAP"); runner rc 0)$(rb_has '^[0-9-]+ [0-9:]+ [A-Z]+ STOP: ' && echo '; read its STOP line above')"
  exit 0
fi
rb_say "e215 arm $ARM still runs: call again"
exit $RB_E_AGAIN
