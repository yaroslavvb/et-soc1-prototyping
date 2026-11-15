#!/usr/bin/env bash
# E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum), the box step "the wait" (this file is s20): one bounded wait on E192
# (aifoundry3: the session log of the T0 the runbook launched today); each call ends within the remote loop's 520 s; call again while it
# says 17. It never touches the card. E189's step 10's form, with THE SESSION-NAME PATTERN MATCHING THE REAL SCRIPT: the session process is
# looked for as `session_e192(_v[0-9]+)?\.sh` (the wrapper's own name, session_e192.sh, and any later dated version), never a name the kit
# does not launch (E183's and E190's step 10 defects: a pattern for another name read a running session as gone, or every gate as a stop).
# Whether the session has ended is read only from its own T0's log (build/e192/T<T0>/session.log, "session end (T0 <T0>)"); then the wait
# says whether MANIFEST.sha256 is written (the collection's exact copy-back reads it). A session that stopped before any pass (a refusal or
# the card not free: "no device opened"; the smoke failed, or a gate or a live stop came before pass 0 completed: "stopped before any pass
# completed") is 16, and step 11 still collects it. A session that ran passes and then stopped (a live stop, a holder between passes, the cap, a stop by hand) has ended: 0, the
# STOP line shown.
#   bash tools/claims-v3/e192/rb/s20_wait_e192.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e192.sh"
rb_init s20_wait
run=e192; box=aifoundry3
want=; [ -f "$RB_OUT/e192-T0.txt" ] && want=$(cat "$RB_OUT/e192-T0.txt")
[ -n "${RB_DRY:-}" ] || [ -n "$want" ] || rb_die $RB_E_USAGE "RB_OUT holds no e192-T0.txt: step 9 has not launched E192 from this RB_OUT"
rb_probe "$box"
f=$(rb_file "wait-$run")
{ rb_prelude "$box"
  echo "RUN=$run; LIM=$RB_WAIT_LOOP_S; WANT='${want:-DRY}'"
  cat <<'EOF2'
fresh build/q141k/$RUN.T0 || { echo "RUN-UNKNOWN $RUN: not launched today by the runbook (no T0 written today)"; exit 3; }
T0=$(cat build/q141k/$RUN.T0)
[ "$WANT" = DRY ] || [ "$T0" = "$WANT" ] || { echo "RUN-UNKNOWN $RUN: the box's last launch T0 $T0 is not this runbook's $WANT"; exit 3; }
SD=build/$RUN/T$T0; L=$SD/session.log
ended() { grep -q "session end (T0 $T0)" "$L" 2>/dev/null; }
while ! ended && [ "$SECONDS" -lt "$LIM" ]; do
  pgrep -u "$(id -u)" -f 'session_e192(_v[0-9]+)?\.sh' > /dev/null || { sleep 2; ended || { echo "RUN-GONE $RUN: no session process and no session end"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
grep -E 'session start|checked|sampler:|first card command|running:|STOP|refused|not free|stopped before|passes complete|session end' "$L" 2>/dev/null | cut -c1-240 | tail -n 20
tail -n 4 "$SD/run/session.log" 2>/dev/null | cut -c1-200
if ended; then
  echo "RUN-ENDED $RUN"
  sleep 2
  if [ -s "$SD/MANIFEST.sha256" ]; then echo "MANIFEST-WRITTEN $(grep -c . "$SD/MANIFEST.sha256") files"; else echo "MANIFEST-ABSENT"; fi
else echo "RUN-RUNNING $RUN after $t s"; fi
if grep -qE 'no device opened|stopped before any pass completed' "$L" 2>/dev/null; then echo "GATE-STOPPED $RUN"; fi
EOF2
} > "$f"
rb_remote wait "$box" "one bounded wait on $run" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on $run exited $RB_RC"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "$run is not running and recorded no end: read the box's logs (read-only) before anything else; the rest rule then counts it at its run's latest write"
rb_has '^MANIFEST-ABSENT' && rb_die $RB_E_FAIL "$run has ended but its MANIFEST.sha256 is not written: wait once more, then read the box (read-only) before step 11"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "$run stopped before any pass (the lines above): step 11 still collects it"
rb_has '^RUN-ENDED' && { rb_say "$run has ended ($(grep -m1 '^MANIFEST-WRITTEN' "$RB_CAP"); $(grep -m1 -o 'passes complete: [0-9]* of 9' "$RB_CAP"))"; exit 0; }
rb_say "$run still runs: call again"
exit $RB_E_AGAIN
