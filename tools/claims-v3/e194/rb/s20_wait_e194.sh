#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum), the box step "the wait" (this file
# is s20): one bounded wait on E194 (aifoundry2: the session log of the T0 the runbook launched today); each call ends within the remote
# loop's 520 s; call again while it says 17. It never touches the card. E191's step 10 (tools/claims-v3/e191/rb/s20_wait_e191.sh,
# unchanged beside it) with E194's box and its lessons carried in:
#   - THE SESSION'S NAME (E183's lesson): the session is found by its OWN script, `ours_live session_e194.sh` (E194's ours_live, by each
#     process's own script: the name step 9 launches, whose runner runs as its child so its command line names it to the end); the
#     runbook desk test runs this step on the real script (rb/selftest_wait_e194.py);
#   - THE GATE-STOP PATTERN (E190's lesson): GATE-STOPPED holds only the runner's gate-stop phrases ("stop-path test failed", "smoke gate
#     failed", "no device opened", "the gate, no launch", "would not start"); the identity gate's pass lines ("identity (a): ...",
#     "identity (b): ...") and the passes' clock words ("the clock ok", "the clock off", "SET ASIDE: the clock: ...") hold none of them;
#   - a host that outlived the runner's 30 s bound (the line "BOUND:") is BOUND-SEEN: 16, read the message (report it at once, kill
#     nothing, keep the booking), then step 11 still collects the session;
#   - THE CLOCK RULE's second off-clock pass ends the queue as a stop ("STOP: a second pass off 800 MHz after its climb"): the session ends
#     normally (0), with that line among the lines printed;
#   - THE RUNNER'S EXIT STATUS (fix-e194, verify-e194's finding 3): once the session has ended, this step waits (at most 10 s) for runner.rc,
#     which session_e194.sh writes after the runner exits, and prints it; a runner that exited with anything but 0 and stopped at no gate
#     (a crash after the gate: its finally block still writes "session end" and the manifest) is 16, "the runner exited <rc>: read
#     runner.out"; runner.rc not written 10 s after the end is 14 (wait once more). Step 11 still collects either, and reports runner.rc.
# The T0 is the launch's own (build/q141k/e194.T0, written today, the same as RB_OUT's e194-T0.txt), its log build/e194/T<T0>/session.log;
# when the session has ended, the wait also says whether its MANIFEST.sha256 is written. A gate-stopped session is 16, and step 11 still
# collects it. Each pass's line carries its reading in words (PASS, SHORT k of K launches, FAILED RUN) and the clock rule's verdict.
#   bash tools/claims-v3/e194/rb/s20_wait_e194.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e194.sh"
rb_init s20_wait
run=e194; box=aifoundry2
want=; [ -f "$RB_OUT/e194-T0.txt" ] && want=$(cat "$RB_OUT/e194-T0.txt")
[ -n "${RB_DRY:-}" ] || [ -n "$want" ] || rb_die $RB_E_USAGE "RB_OUT holds no e194-T0.txt: step 9 has not launched E194 from this RB_OUT"
rb_probe "$box"
f=$(rb_file "wait-$run")
{ rb_prelude "$box"
  echo "RUN=$run; LIM=$RB_WAIT_LOOP_S; WANT='${want:-DRY}'"
  cat <<'EOF2'
fresh build/q141k/$RUN.T0 || { echo "RUN-UNKNOWN $RUN: not launched today by the runbook (no T0 written today)"; exit 3; }
T0=$(cat build/q141k/$RUN.T0)
[ "$WANT" = DRY ] || [ "$T0" = "$WANT" ] || { echo "RUN-UNKNOWN $RUN: the box's last launch T0 $T0 is not this runbook's $WANT"; exit 3; }
SD=build/$RUN/T$T0; L=$SD/session.log
ended() { grep -q 'session end' "$L" 2>/dev/null; }
while ! ended && [ "$SECONDS" -lt "$LIM" ]; do
  [ "$(ours_live "session_$RUN.sh")" -gt 0 ] || { sleep 2; ended || { echo "RUN-GONE $RUN: no session process and no session end"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
grep -E 'session start|box check|holder rule|config|identity|stop-path|smoke|pass [0-9]+:|anchor|STOP|BOUND|no device opened|session end' "$L" 2>/dev/null | cut -c1-280 | tail -n 46
if ended; then
  echo "RUN-ENDED $RUN"
  sleep 2
  if [ -s "$SD/MANIFEST.sha256" ]; then echo "MANIFEST-WRITTEN $(grep -c . "$SD/MANIFEST.sha256") files"; else echo "MANIFEST-ABSENT"; fi
  w=0; while [ ! -s "$SD/runner.rc" ] && [ "$w" -lt 10 ]; do sleep 1; w=$((w + 1)); done
  if [ -s "$SD/runner.rc" ]; then echo "RUNNER-RC $(tr -dc '0-9' < "$SD/runner.rc")"; else echo "RUNNER-RC-ABSENT after $w s"; fi
else echo "RUN-RUNNING $RUN after $t s"; fi
if grep -qE 'stop-path test failed|smoke gate failed|no device opened|the gate, no launch|would not start' "$L" 2>/dev/null; then echo "GATE-STOPPED $RUN"; fi
if grep -q 'BOUND: ' "$L" 2>/dev/null; then echo "BOUND-SEEN $RUN"; fi
EOF2
} > "$f"
rb_remote wait "$box" "one bounded wait on $run" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on $run exited $RB_RC"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "$run is not running and recorded no end: read the box's logs (read-only) before anything else; the rest rule then counts it at its run's latest write"
rb_has '^BOUND-SEEN' && rb_die $RB_E_GATE "$run: a host process outlived the runner's 30 s bound (the BOUND line above): report it at once, kill nothing, keep the booking; the queue stopped; step 11 still collects the session once it has ended"
rb_has '^MANIFEST-ABSENT' && rb_die $RB_E_FAIL "$run has ended but its MANIFEST.sha256 is not written: wait once more, then read the box (read-only) before step 11"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "$run ended at a gate (the lines above): then step 11 still collects it"
if rb_has '^RUN-ENDED'; then                                    # fix-e194 (finding 3): the runner's own exit status
  rrc=$(rb_val '^RUNNER-RC ([0-9]+)$')
  rb_has '^RUNNER-RC-ABSENT' && rb_die $RB_E_FAIL "$run has ended but its runner.rc is not written: wait once more, then read the box (read-only) before step 11"
  [ "$rrc" = 0 ] || rb_die $RB_E_GATE "the runner exited ${rrc:-unread} after the session's end and stopped at no gate: read runner.out in the session's directory (read-only), report it; step 11 still collects the session"
  rb_say "$run has ended ($(grep -m1 '^MANIFEST-WRITTEN' "$RB_CAP"); the runner exited 0)"; exit 0
fi
rb_say "$run still runs: call again"
exit $RB_E_AGAIN
