#!/usr/bin/env bash
# E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): KIT.md box step 10 v2, the wait. It
# is rb/s20_wait_e183.sh (cc597bf2, which stays as committed) with ONE change, marked "note 6": v1 looked for the session's process with
# pgrep -f "session_e183\.sh", which never matches session_e183_v2.sh (step 9 v2's) or any later version, so on aifoundry3 on Fri 13 Nov
# 2026, while the smoke ran, it read RUN-GONE (14: "read the box's logs before anything else") for a session that was running. v2 matches
# E183's session and its queue in every version, "(session|queue)_e183(_v[0-9]+)?\.sh": session_e183.sh, session_e183_v2.sh,
# session_e183_v3.sh and any later one, and queue_e183(_vN).sh beside them (a queue runs only inside its session); not another run's
# session (session_e185_v2.sh), not a name that merely begins so (session_e1830.sh), not a block. Whether the session has ENDED is read,
# as in v1, only from its own T0's log ("session end (T0 <T0>)"); the process is read only to tell RUN-RUNNING (17) from RUN-GONE (14).
# Everything else is v1's, line for line; its name in the runbook's log is s20_wait_v2_e183.
#   bash tools/claims-v3/e183/rb/s20_wait_e183_v2.sh          (again while it says 17)
# v1's words follow:
# E183 (Q155, the kit), KIT.md box step 10: one bounded wait on the session (E180's step 10 v2 with E184 v2's T0 rule): the T0 step 9 wrote
# today (build/q141k/e183.t0), the log build/e183/session-t<T0>.log, whose first line must name that T0, and the run has ended only when
# that log says "session end (T0 <T0>)": no earlier attempt's log, line or "session end" can satisfy it. A gate stop (the stop-path test, the
# smoke gate, or no device opened) stops the step with 16. Call it again while it says 17.
#   bash tools/claims-v3/e183/rb/s20_wait_e183.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e183.sh"
rb_init s20_wait_v2
rb_probe aifoundry3
f=$(rb_file wait-e183)
{ rb_prelude aifoundry3
  echo "LIM=$RB_WAIT_LOOP_S"
  cat <<'EOF2'
TF=build/q141k/e183.t0
fresh "$TF" || { echo "RUN-UNKNOWN e183: not launched today by the runbook (no T0 written today)"; exit 3; }
T0=$(cat "$TF")
L=build/e183/session-t$T0.log
if [ -s "$L" ] && ! head -n 1 "$L" | grep -q "(T0 $T0 "; then echo "RUN-UNKNOWN e183: $L does not open with T0 $T0"; exit 3; fi
ended() { grep -q "session end (T0 $T0)" "$L" 2>/dev/null; }
gone=0
while ! ended && [ "$SECONDS" -lt "$LIM" ]; do      # the box's clock bounds the loop
  pgrep -u "$(id -u)" -f "(session|queue)_e183(_v[0-9]+)?\.sh" > /dev/null || { sleep 2; ended || { gone=1; break; }; }     # note 6
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
echo "T0 $T0, log $L"
grep -E 'session start|stop-path|smoke|gate|queue|STOP|no device opened|failed|session end' "$L" 2>/dev/null | cut -c1-300 | tail -n 30
[ -f "build/e183/queue-t$T0.out" ] && tail -n 3 "build/e183/queue-t$T0.out" | cut -c1-300
if ended; then echo "RUN-ENDED e183"; elif [ "$gone" -eq 1 ]; then echo "RUN-GONE e183: no session process and no session end for T0 $T0"
else echo "RUN-RUNNING e183 after $t s"; fi
if grep -qE 'smoke gate failed|stop-path test failed|no device opened' "$L" 2>/dev/null; then echo "GATE-STOPPED e183"; fi
EOF2
} > "$f"
rb_remote wait aifoundry3 "one bounded wait on e183" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on e183 exited $RB_RC"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "e183 is not running and recorded no end for its T0: read the box's logs before anything else"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "e183 ended at a gate (a smoke or stop test, or no go): read the lines above"
rb_has '^RUN-ENDED' && { rb_say "e183 has ended (its own T0's log says so)"; exit 0; }
rb_say "e183 still runs: call again"
exit $RB_E_AGAIN
