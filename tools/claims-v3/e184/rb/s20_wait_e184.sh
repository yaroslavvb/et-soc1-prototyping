#!/usr/bin/env bash
# E184 (Q153), kit note 1 (../KIT.md.dated-note-1.md section 3), step 10: one bounded wait on an arm's session; each call ends within the remote
# loop's 520 s; call again while it says 17. It never touches the card. The rest rule (the verifier's fault 4): it reads ONLY the log of the
# T0 step 9 wrote today (build/q141k/e184<s|b>.t0), build/e184/session-<arm>-t<T0>.log, whose first line must name that T0, and the run has
# ended only when that log says "session end (T0 <T0>)": no earlier attempt's log, line or "session end" can satisfy it. A gate stop (the
# smoke, the stop-path test, a refusal) is 16; no session process and no end is 14; still running 17.
#
#   bash tools/claims-v3/e184/rb/s20_wait_e184.sh S|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e184.sh"
rb_init s20_wait
e184_arm "${1:-}" || rb_die $RB_E_USAGE "usage: s20_wait_e184.sh S|B"
rb_probe "$E184_BOX"
f=$(rb_file "wait-e184$E184_LC")
{ rb_prelude "$E184_BOX"
  echo "ARM=$E184_ARM; LC=$E184_LC; SESS=$E184_SESS; LIM=$RB_WAIT_LOOP_S"
  cat <<'EOF2'
TF=build/q141k/e184$LC.t0
fresh "$TF" || { echo "RUN-UNKNOWN e184$LC: not launched today by the runbook (no T0 written today)"; exit 3; }
T0=$(cat "$TF")
L=build/e184/session-$ARM-t$T0.log
if [ -s "$L" ] && ! head -n 1 "$L" | grep -q "budget anchor T0 $T0 "; then echo "RUN-UNKNOWN e184$LC: $L does not open with T0 $T0"; exit 3; fi
ended() { grep -q "session end (T0 $T0)" "$L" 2>/dev/null; }
gone=0
while ! ended && [ "$SECONDS" -lt "$LIM" ]; do      # the box's clock bounds the loop
  if ! pgrep -u "$(id -u)" -f "$SESS" > /dev/null; then sleep 2; ended || { gone=1; break; }; fi
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
echo "T0 $T0, log $L"
grep -E 'session start|stop-path|smoke|gate|queue|STOP|no device opened|failed|session end' "$L" 2>/dev/null | cut -c1-300 | tail -n 30
[ -f "build/e184/queue-$ARM-t$T0.out" ] && tail -n 3 "build/e184/queue-$ARM-t$T0.out" | cut -c1-300
if grep -qE 'smoke gate failed|stop-path test failed|no device opened|not GO' "$L" 2>/dev/null; then echo "GATE-STOPPED e184$LC"; fi
if ended; then echo "RUN-ENDED e184$LC"; elif [ "$gone" -eq 1 ]; then echo "RUN-GONE e184$LC: no session process and no session end for T0 $T0"
else echo "RUN-RUNNING e184$LC after $t s"; fi
EOF2
} > "$f"
rb_remote wait "$E184_BOX" "one bounded wait on e184$E184_LC" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on e184$E184_LC exited $RB_RC"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "e184$E184_LC ended at a gate (a smoke or stop test, a refusal, or no go): read the lines above"
rb_has '^RUN-ENDED' && { rb_say "e184$E184_LC has ended (its own T0's log says so)"; exit 0; }
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "e184$E184_LC is not running and its log records no end: read the box's logs before anything else"
rb_say "e184$E184_LC still runs: call again"
exit $RB_E_AGAIN
