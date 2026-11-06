#!/usr/bin/env bash
# E181, step 20: one bounded wait on E181 (aifoundry3: the session log after the runbook's own offset); each call ends within the remote
# loop's 520 s; call again while it says 17. It never touches the card. ../../q143k-runbook/s20_wait_q143k.sh (92a1b27f) ported, with the
# gates read on their own: A6-1-STOPPED (exit 16) when the smoke's floor F0 was above 53.9 C or unreadable (the session ended before the
# smoke's first launch), G0-REFUSED (exit 16) when the measured pass ended at the start gate (G0-A6 with A8-4: no hold ran).
#
#   bash tools/claims-v3/e181/rb/s20_wait_e181.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e181.sh"
rb_init s20_wait
run=e181; box=aifoundry3
rb_probe "$box"
f=$(rb_file "wait-$run")
{ rb_prelude "$box"
  echo "RUN=$run; LIM=$RB_WAIT_LOOP_S"
  cat <<'EOF2'
L=build/$RUN/session.log
fresh build/q141k/$RUN.log-offset || { echo "RUN-UNKNOWN $RUN: not launched today by the runbook (no log offset written today)"; exit 3; }
off=$(cat build/q141k/$RUN.log-offset)
ended() { tail -n +"$((off + 1))" "$L" 2>/dev/null | grep -q 'session end$'; }
while ! ended && [ "$SECONDS" -lt "$LIM" ]; do
  pgrep -u "$(id -u)" -f "session_$RUN\.sh" > /dev/null || { sleep 2; ended || { echo "RUN-GONE $RUN: no session process and no session end"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
tail -n +"$((off + 1))" "$L" 2>/dev/null | grep -E 'session start|smoke|gate|A6-1|pass 18120|STOP|no device opened|failed|session end' | cut -c1-300 | tail -n 30
if ended; then echo "RUN-ENDED $RUN"; else echo "RUN-RUNNING $RUN after $t s"; fi
if tail -n +"$((off + 1))" "$L" | grep -q '^.* A6-1: F0 above 53.9 C or unreadable'; then echo "A61-STOPPED $RUN"; fi
if tail -n +"$((off + 1))" "$L" | grep -qE 'smoke or its gate failed|no device opened|STOP file: no measured pass'; then echo "GATE-STOPPED $RUN"; fi
if tail -n +"$((off + 1))" "$L" | grep -q 'pass 18120 rc=7'; then echo "G0-REFUSED $RUN"; fi
EOF2
} > "$f"
rb_remote wait "$box" "one bounded wait on $run" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on $run exited $RB_RC"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "$run is not running and recorded no end: read the box's logs before anything else"
rb_has '^A61-STOPPED' && rb_die $RB_E_GATE "$run ended at A6-1 (the smoke's floor F0 above 53.9 C or unreadable): no launch, no hold; nothing to score. A later try needs a settled card (s11 --later-try)"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "$run ended at a gate (the smoke, its gate, a STOP file or a session gate): read the lines above"
rb_has '^G0-REFUSED' && rb_die $RB_E_GATE "$run's start gate refused (G0-A6 with A8-4: R0's room above 53.9 C, or its residue less 0.414 C above 0.50 C): no hold ran; a later try needs a rested card (s11 --later-try)"
rb_has '^RUN-ENDED' && { rb_say "$run has ended"; exit 0; }
rb_say "$run still runs: call again"
exit $RB_E_AGAIN
