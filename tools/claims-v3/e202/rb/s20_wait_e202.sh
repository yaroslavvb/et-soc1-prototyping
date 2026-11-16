#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum), the box step "the wait" (this file is s20): one bounded wait on E202
# (aifoundry3: the session log of the T0 the runbook launched today); each call ends within the remote loop's 520 s; call again while it
# says 17. It never touches the card. E189's step 10 form, with THE SESSION FOUND BY ITS REAL SCRIPT'S NAME: rb_e202.sh's E202_SESSION_PAT
# (session_e202.sh as a word after a space or a slash: `bash tools/claims-v3/e202/session_e202.sh`, as step 9 launches it; never the
# runner's run_e202.py, never a name that merely ends in it), read against the real launch and decoys in the desk tests. The T0 is the
# launch's own (build/q141k/e202.T0, written today, the same as RB_OUT's e202-T0.txt), its log build/e202/T<T0>/session.log; when the
# session has ended, the wait also says whether its MANIFEST.sha256 is written and its runner.rc. A session that ended at a gate (no burst:
# a "GATE-STOP:" or "refused, no device opened:" line, written only by the runner itself) is 16, and step 11 still collects it, as a gate
# stop's record.
# THE RUNNER'S EXIT STATUS (fix-e202, verify-e202's finding 2; E194's step 10, fix-e194): once the session has ended, this step waits (at
# most 10 s) for runner.rc, which session_e202.sh writes after the runner exits, and prints it; a runner that exited with anything but 0
# and stopped at no gate (a crash: its finally block still writes "session end" and the manifest, and since fix-e202 its log names it,
# "CRASH: <type>: <message>", printed here as CRASHED) is 16, "the runner exited <rc>: read runner.out"; runner.rc not written 10 s after
# the end is 14 (wait once more, then read the box read-only). Step 11 still collects either, and its record names the crash.
#   bash tools/claims-v3/e202/rb/s20_wait_e202.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e202.sh"
rb_init s20_wait
run=e202; box=aifoundry3
want=; [ -f "$RB_OUT/e202-T0.txt" ] && want=$(cat "$RB_OUT/e202-T0.txt")
[ -n "${RB_DRY:-}" ] || [ -n "$want" ] || rb_die $RB_E_USAGE "RB_OUT holds no e202-T0.txt: step 9 has not launched E202 from this RB_OUT"
rb_probe "$box"
f=$(rb_file "wait-$run")
{ rb_prelude "$box"
  echo "RUN=$run; LIM=$RB_WAIT_LOOP_S; WANT='${want:-DRY}'; PAT=$(printf '%q' "$E202_SESSION_PAT")"
  cat <<'EOF2'
fresh build/q141k/$RUN.T0 || { echo "RUN-UNKNOWN $RUN: not launched today by the runbook (no T0 written today)"; exit 3; }
T0=$(cat build/q141k/$RUN.T0)
[ "$WANT" = DRY ] || [ "$T0" = "$WANT" ] || { echo "RUN-UNKNOWN $RUN: the box's last launch T0 $T0 is not this runbook's $WANT"; exit 3; }
SD=build/$RUN/T$T0; L=$SD/session.log
ended() { grep -q 'session end' "$L" 2>/dev/null; }
while ! ended && [ "$SECONDS" -lt "$LIM" ]; do
  pgrep -u "$(id -u)" -f "$PAT" > /dev/null || { sleep 2; ended || { echo "RUN-GONE $RUN: no session process and no session end"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
grep -E 'session start|first card command|config|stop-path|smoke|R rule|burst [0-9]+:|anchor|STOP|GATE-STOP|refused, no device opened|CRASH|closing|session end' "$L" 2>/dev/null | cut -c1-240 | tail -n 40
if ended; then
  echo "RUN-ENDED $RUN"
  sleep 2
  if [ -s "$SD/MANIFEST.sha256" ]; then echo "MANIFEST-WRITTEN $(grep -c . "$SD/MANIFEST.sha256") files"; else echo "MANIFEST-ABSENT"; fi
  w=0; while [ ! -s "$SD/runner.rc" ] && [ "$w" -lt 10 ]; do sleep 1; w=$((w + 1)); done
  if [ -s "$SD/runner.rc" ]; then echo "RUNNER-RC $(tr -dc '0-9' < "$SD/runner.rc")"; else echo "RUNNER-RC-ABSENT after $w s"; fi
else echo "RUN-RUNNING $RUN after $t s"; fi
if grep -qE '^[-0-9]+ [:0-9]+ [A-Z]+ (GATE-STOP: |refused, no device opened: )' "$L" 2>/dev/null; then echo "GATE-STOPPED $RUN"; fi
if grep -qE '^[-0-9]+ [:0-9]+ [A-Z]+ CRASH: ' "$L" 2>/dev/null; then echo "CRASHED $RUN: $(grep -m1 -E '^[-0-9]+ [:0-9]+ [A-Z]+ CRASH: ' "$L" | cut -c25-200)"; fi
EOF2
} > "$f"
rb_remote wait "$box" "one bounded wait on $run" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on $run exited $RB_RC"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "$run is not running and recorded no end: read the box's logs (read-only) before anything else; the rest rule then counts it at its run's latest write"
rb_has '^MANIFEST-ABSENT' && rb_die $RB_E_FAIL "$run has ended but its MANIFEST.sha256 is not written: wait once more, then read the box (read-only) before step 11"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "$run ended at a gate, no burst (the lines above): step 11 still collects it, as a gate stop's record"
if rb_has '^RUN-ENDED'; then                                    # fix-e202 (finding 2): the runner's own exit status, E194's form
  rrc=$(rb_val '^RUNNER-RC ([0-9]+)$')
  rb_has '^RUNNER-RC-ABSENT' && rb_die $RB_E_FAIL "$run has ended but its runner.rc is not written: wait once more, then read the box (read-only) before step 11"
  cr=""; rb_has '^CRASHED ' && cr=" ($(grep -m1 '^CRASHED ' "$RB_CAP" | cut -c1-200))"
  [ "$rrc" = 0 ] || rb_die $RB_E_GATE "the runner exited ${rrc:-unread} after the session's end and stopped at no gate$cr: read runner.out in the session's directory (read-only), report it; step 11 still collects the session (its record names the crash)"
  rb_say "$run has ended ($(grep -m1 '^MANIFEST-WRITTEN' "$RB_CAP"); the runner exited 0)"; exit 0
fi
rb_say "$run still runs: call again"
exit $RB_E_AGAIN
