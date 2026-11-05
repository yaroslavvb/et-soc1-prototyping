#!/usr/bin/env bash
# Q141(k), go checklist step 20: one bounded wait on a run (the remote loop stops at 520 s inside the 600 s call), repeated as needed,
# never a long local sleep. It prints the run's own gate lines, so each smoke gate's verdict is read before the session counts as
# started:
#   e163, e166 (aifoundry3): session.log after the launch's offset: the stop-path test, the smoke and its gate, the queue or the pass,
#     "session end"; for E166, G0's refusal (pass 16620 rc=7: the room above 53.0 C, no hold ran);
#   e164 (aifoundry1): the kit's own tools/claims-v3/e164/box/wait_e164.sh (at most 520 s, never touches the card);
#   e165, e167, e168, e169 (aifoundry2): status.json until "ended" or "halted", the smoke and stop-test checks and QUEUE-HALT from
#     queue.jsonl (E167: also run_e167.sh watch).
#
#   bash tools/claims-v3/q141k-runbook/v2/s20_wait.sh <e163|e164|e165|e166|e167|e168|e169>
#
# Exit 0 the run has ended (read the lines it printed); 17 still running: call again; 16 it ended at a gate (G0 refused, a smoke or
# stop test failed, QUEUE-HALT, no go): read why; 14 the run is gone without an end record; 10 (v2) not launched today.
# v2 (Q141(k)'s verifier, nit 5): only today's launch counts. On aifoundry3 the log offset must have been written today (v1 read the
# whole session log when no offset was there, so an earlier day's "session end" read as today's); on aifoundry2 a status.json not
# written today, with no queue process, reads "not launched today".
# v3 (Q142(s), fault 9): the remote loops stop by the box's clock ($SECONDS), not by the sum of their sleeps.
#   bash tools/claims-v3/q141k-runbook/v3/s20_wait.sh <e163|e164|e165|e166|e167|e168|e169>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s20_wait
run=${1:-}
case "$run" in
  e163|e166) box=aifoundry3 ;;
  e164) box=aifoundry1 ;;
  e165|e167|e168|e169) box=aifoundry2 ;;
  *) rb_die $RB_E_USAGE "usage: s20_wait.sh <e163|e164|e165|e166|e167|e168|e169>" ;;
esac
rb_probe "$box"
if [ "$run" = e164 ]; then
  rb_remote wait aifoundry1 "box/wait_e164.sh (E164 box step 6)" "$RB_REPO/tools/claims-v3/e164/box/wait_e164.sh"
  [ -n "${RB_DRY:-}" ] && exit 0
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "wait_e164.sh exited $RB_RC"
  if rb_has 'session end'; then
    rb_has 'gate (failed|FAIL|NO-GO)|failed: no pass|no device opened' && rb_die $RB_E_GATE "E164 ended at a gate: read the lines above"
    rb_say "E164's session has ended"; exit 0
  fi
  rb_say "E164 still runs: call again"; exit $RB_E_AGAIN
fi
f=$(rb_file "wait-$run")
{ rb_prelude "$box"
  echo "RUN=$run; LIM=$RB_WAIT_LOOP_S"
  if [ "$box" = aifoundry3 ]; then cat <<'EOF'
L=build/$RUN/session.log
fresh build/q141k/$RUN.log-offset || { echo "RUN-UNKNOWN $RUN: not launched today by the runbook (no log offset written today)"; exit 3; }
off=$(cat build/q141k/$RUN.log-offset)
ended() { tail -n +"$((off + 1))" "$L" 2>/dev/null | grep -q 'session end'; }
while ! ended && [ "$SECONDS" -lt "$LIM" ]; do      # v3: the box's clock bounds the loop
  pgrep -u "$(id -u)" -f "session_$RUN\.sh" > /dev/null || { sleep 2; ended || { echo "RUN-GONE $RUN: no session process and no session end"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
tail -n +"$((off + 1))" "$L" 2>/dev/null | grep -E 'session start|stop-path|smoke|gate|queue|pass 16620|STOP|no device opened|failed|session end' | cut -c1-300 | tail -n 30
[ -f build/$RUN/queue.out ] && tail -n 3 build/$RUN/queue.out | cut -c1-300
if ended; then echo "RUN-ENDED $RUN"; else echo "RUN-RUNNING $RUN after $t s"; fi
if [ "$RUN" = e166 ] && tail -n +"$((off + 1))" "$L" | grep -q 'pass 16620 rc=7'; then
  echo "G0-REFUSED: the room was above 53.0 C, no hold ran: launch E163 first; a later E166 needs 40 minutes of rest and --later-try"
fi
if tail -n +"$((off + 1))" "$L" | grep -qE 'smoke gate failed|smoke or its gate failed|stop-path test failed|no device opened'; then echo "GATE-STOPPED $RUN"; fi
EOF
  else cat <<'EOF'
R=build/$RUN/runs
fin() { fresh "$R/status.json" && grep -qE '"state": "(ended|halted)"' "$R/status.json" 2>/dev/null; }
if ! fresh "$R/status.json" && ! pgrep -u "$(id -u)" -f "queue_$RUN\.py" > /dev/null; then
  echo "RUN-UNKNOWN $RUN: no queue process and no status.json written today"; exit 3
fi
while ! fin && [ "$SECONDS" -lt "$LIM" ]; do        # v3: the box's clock bounds the loop
  pgrep -u "$(id -u)" -f "queue_$RUN\.py" > /dev/null || { sleep 2; fin || { echo "RUN-GONE $RUN: no queue process and no end in status.json"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'; cat "$R/status.json" 2>/dev/null; echo
[ -e "$R/QUEUE-HALT" ] && { echo "QUEUE-HALT:"; cut -c1-300 "$R/QUEUE-HALT"; }
grep -hE '"kind": "(smoke_check|stoptest_check|queue_halt|go|no_go|go_refused|give_up|stop|gate|s[1-6]_end|queue_end)"' "$R/queue.jsonl" 2>/dev/null | cut -c1-300 | tail -n 14
tail -n 4 build/$RUN/queue.out 2>/dev/null | cut -c1-300
[ "$RUN" = e167 ] && bash tools/claims-v3/e167/run_e167.sh watch | cut -c1-300 | tail -n 20
if fin; then echo "RUN-ENDED $RUN"; else echo "RUN-RUNNING $RUN after $t s"; fi
if [ -e "$R/QUEUE-HALT" ] || grep -qE '"kind": "(no_go|go_refused|give_up)"' "$R/queue.jsonl" 2>/dev/null; then echo "GATE-STOPPED $RUN"; fi
EOF
  fi
} > "$f"
rb_remote wait "$box" "one bounded wait on $run" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on $run exited $RB_RC"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "$run is not running and recorded no end: read the box's logs before anything else"
rb_has '^G0-REFUSED' && rb_die $RB_E_GATE "E166's G0 refused (the room above 53.0 C): run s11_a3_session.sh e163 now; E166 later with --later-try"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "$run ended at a gate (a smoke or stop test, QUEUE-HALT or no go): read the lines above"
rb_has '^RUN-ENDED' && { rb_say "$run has ended"; exit 0; }
rb_say "$run still runs: call again"
exit $RB_E_AGAIN
