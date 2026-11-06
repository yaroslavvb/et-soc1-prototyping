#!/usr/bin/env bash
# E180 (Q146(f), the kit), step 20: one bounded wait on E180 (aifoundry3: the session log after the runbook's own offset); each call ends within
# the remote loop's 520 s; call again while it says 17. It never touches the card. A port of ../../q141k-runbook/k6/s20_wait_k6.sh's
# aifoundry3 route, unchanged but for the run's name.
#
#   bash tools/claims-v3/e180/rb/s20_wait_e180.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e180.sh"
rb_init s20_wait
run=e180; box=aifoundry3
rb_probe "$box"
f=$(rb_file "wait-$run")
{ rb_prelude "$box"
  echo "RUN=$run; LIM=$RB_WAIT_LOOP_S"
  cat <<'EOF2'
L=build/$RUN/session.log
fresh build/q141k/$RUN.log-offset || { echo "RUN-UNKNOWN $RUN: not launched today by the runbook (no log offset written today)"; exit 3; }
off=$(cat build/q141k/$RUN.log-offset)
ended() { tail -n +"$((off + 1))" "$L" 2>/dev/null | grep -q 'session end'; }
while ! ended && [ "$SECONDS" -lt "$LIM" ]; do      # the box's clock bounds the loop
  pgrep -u "$(id -u)" -f "session_$RUN\.sh" > /dev/null || { sleep 2; ended || { echo "RUN-GONE $RUN: no session process and no session end"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
tail -n +"$((off + 1))" "$L" 2>/dev/null | grep -E 'session start|stop-path|smoke|gate|queue|STOP|no device opened|failed|session end' | cut -c1-300 | tail -n 30
[ -f build/$RUN/queue.out ] && tail -n 3 build/$RUN/queue.out | cut -c1-300
if ended; then echo "RUN-ENDED $RUN"; else echo "RUN-RUNNING $RUN after $t s"; fi
if tail -n +"$((off + 1))" "$L" | grep -qE 'smoke gate failed|smoke or its gate failed|stop-path test failed|no device opened'; then echo "GATE-STOPPED $RUN"; fi
EOF2
} > "$f"
rb_remote wait "$box" "one bounded wait on $run" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on $run exited $RB_RC"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "$run is not running and recorded no end: read the box's logs before anything else"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "$run ended at a gate (a smoke or stop test, or no go): read the lines above"
rb_has '^RUN-ENDED' && { rb_say "$run has ended"; exit 0; }
rb_say "$run still runs: call again"
exit $RB_E_AGAIN
