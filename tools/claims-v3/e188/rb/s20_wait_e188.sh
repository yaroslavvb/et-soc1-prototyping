#!/usr/bin/env bash
# E188 (Q165, the kit), KIT.md box step 10 (this file is s20): one bounded wait on E188 (aifoundry3: the session log of the T0 the runbook
# launched today); each call ends within the remote loop's 520 s; call again while it says 17. It never touches the card. A port of E186's
# step 10 (tools/claims-v3/e186/rb/s20_wait_e186.sh; itself E182's, k6's s20 aifoundry3 route) with E188's session directory: the T0 is the launch's
# own (build/q141k/e188.T0, written today, the same as RB_OUT's e188-T0.txt), its log build/e188/T<T0>/session.log, its queue's output
# beside it; when the session has ended, the wait also says whether its MANIFEST.sha256 is written (step 11's exact copy-back reads it).
#
#   bash tools/claims-v3/e188/rb/s20_wait_e188.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e188.sh"
rb_init s20_wait
run=e188; box=aifoundry3
want=; [ -f "$RB_OUT/e188-T0.txt" ] && want=$(cat "$RB_OUT/e188-T0.txt")
[ -n "${RB_DRY:-}" ] || [ -n "$want" ] || rb_die $RB_E_USAGE "RB_OUT holds no e188-T0.txt: step 9 (s11_a3_session_e188.sh) has not launched E188 from this RB_OUT"
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
while ! ended && [ "$SECONDS" -lt "$LIM" ]; do      # the box's clock bounds the loop
  pgrep -u "$(id -u)" -f "session_$RUN\.sh" > /dev/null || { sleep 2; ended || { echo "RUN-GONE $RUN: no session process and no session end"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
grep -E 'session start|stop-path|smoke|gate|queue|STOP|no device opened|failed|session end' "$L" 2>/dev/null | cut -c1-300 | tail -n 30
[ -f "$SD/queue.out" ] && tail -n 3 "$SD/queue.out" | cut -c1-300
if ended; then
  echo "RUN-ENDED $RUN"
  sleep 2
  if [ -s "$SD/MANIFEST.sha256" ]; then echo "MANIFEST-WRITTEN $(grep -c . "$SD/MANIFEST.sha256") files"; else echo "MANIFEST-ABSENT"; fi
else echo "RUN-RUNNING $RUN after $t s"; fi
if grep -qE 'smoke gate failed|stop-path test failed|no device opened' "$L" 2>/dev/null; then echo "GATE-STOPPED $RUN"; fi
EOF2
} > "$f"
rb_remote wait "$box" "one bounded wait on $run" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on $run exited $RB_RC"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "$run is not running and recorded no end: read the box's logs before anything else"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "$run ended at a gate (a smoke or stop test, or no go): read the lines above; step 11 still collects it"
rb_has '^MANIFEST-ABSENT' && rb_die $RB_E_FAIL "$run has ended but its MANIFEST.sha256 is not written: wait once more, then read the box (read-only) before step 11"
rb_has '^RUN-ENDED' && { rb_say "$run has ended ($(grep -m1 '^MANIFEST-WRITTEN' "$RB_CAP"))"; exit 0; }
rb_say "$run still runs: call again"
exit $RB_E_AGAIN
