#!/usr/bin/env bash
# Q142(k6), step 20: one bounded wait on E171 (aifoundry3: the session log after the runbook's own offset) or E172 (aifoundry1:
# box/wait_e172.sh); each call ends within the remote loop's 520 s; call again while it says 17. It never touches the card. A port of
# ../v3.1/s20_wait.sh, its aifoundry3 and aifoundry1 routes only.
#
#   bash tools/claims-v3/q141k-runbook/k6/s20_wait_k6.sh e171 | e172
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s20_wait
run=${1:-}
case "$run" in
  e171) box=aifoundry3 ;;
  e172) box=aifoundry1 ;;
  *) rb_die $RB_E_USAGE "usage: s20_wait_k6.sh <e171|e172>" ;;
esac
rb_probe "$box"
if [ "$run" = e172 ]; then
  rb_remote wait aifoundry1 "box/wait_e172.sh (E172 box step 6)" "$RB_REPO/tools/claims-v3/e172/box/wait_e172.sh"
  [ -n "${RB_DRY:-}" ] && exit 0
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "wait_e172.sh exited $RB_RC"
  if rb_has 'session end'; then
    rb_has 'gate (failed|FAIL|NO-GO)|failed: no pass|no device opened' && rb_die $RB_E_GATE "E172 ended at a gate: read the lines above"
    rb_say "E172's session has ended"; exit 0
  fi
  rb_say "E172 still runs: call again"; exit $RB_E_AGAIN
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
tail -n +"$((off + 1))" "$L" 2>/dev/null | grep -E 'session start|stop-path|smoke|gate|queue|STOP|no device opened|failed|session end' | cut -c1-300 | tail -n 30
[ -f build/$RUN/queue.out ] && tail -n 3 build/$RUN/queue.out | cut -c1-300
if ended; then echo "RUN-ENDED $RUN"; else echo "RUN-RUNNING $RUN after $t s"; fi
if tail -n +"$((off + 1))" "$L" | grep -qE 'smoke gate failed|smoke or its gate failed|stop-path test failed|no device opened'; then echo "GATE-STOPPED $RUN"; fi
EOF
  fi
} > "$f"
rb_remote wait "$box" "one bounded wait on $run" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on $run exited $RB_RC"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "$run is not running and recorded no end: read the box's logs before anything else"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "$run ended at a gate (a smoke or stop test, QUEUE-HALT or no go): read the lines above"
rb_has '^RUN-ENDED' && { rb_say "$run has ended"; exit 0; }
rb_say "$run still runs: call again"
exit $RB_E_AGAIN
