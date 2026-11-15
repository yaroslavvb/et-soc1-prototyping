#!/usr/bin/env bash
# E193 (Q177, the kit), the box step "the wait" (this file is s20), one sitting a call: one bounded wait on E193's sitting (aifoundry3:
# the session log of the T0 the runbook launched today); each call ends within the remote loop's 520 s; call again while it says 17. It
# never touches the card. E189's step 10's form, with E183's and E190's step-10 lessons:
#   - THE SESSION'S PROCESS IS FOUND BY ITS REAL SCRIPT NAME, session_e193.sh (`pgrep -f 'session_e193\.sh'`): the launch runs
#     `bash <E193's root>/tools/claims-v3/e193/session_e193.sh <A|B>`, and that command line is what the pattern reads (E183's step 10
#     v1 grepped a name its session v2 never had, and read a running session as gone); the runbook's desk test runs this step against
#     the real session_e193.sh running on a stand-in box (RUN-RUNNING) and against the real-path desk test's own session logs;
#   - A GATE STOP IS READ ONLY FROM THE SESSION'S OWN GATE LINES, "<time> GATE-STOP: ...", which session_e193.sh writes only when it
#     ends a sitting before its main run; no normal line holds that word (E190's step 10 v2 read every session that passed its identity
#     gate as gate-stopped); a registered stop of the main run ("main run stopped: ...") is not a gate: the passes done stand;
#   - A CRASH IS NOT A REGISTERED STOP (fix-e193, verify-e193's finding 5): a main run whose runner exited non-zero with no stop recorded
#     is written "<time> main run ended without a registered stop: ..." by session_e193.sh (its exit 4), and this step reads it as
#     MAIN-CRASHED and stops the day (16): kill nothing, collect it (step 11: its data directory), report it; a dated note decides
#     whether its passes are reduced, and no further sitting runs before that note (step 9 refuses sitting B after a crashed sitting A).
# The T0 is the launch's own (build/q141k/e193-<sitting>.T0, written today, the same as RB_OUT's e193-<sitting>-T0.txt), its log
# build/e193/T<T0>/session.log; when the session has ended, the wait also says whether its MANIFEST.sha256 is written (the collection's
# exact copy-back reads it). Exit: 0 ended (manifest written; "main run stopped" reported if a stop ended the main run); 16 ended at a
# gate (step 11 still collects it, as a gate stop's record: E184's lesson), or ended after a crash of its main run (MAIN-CRASHED; step 11
# collects it into its data directory); 17 still running; 14 gone without "session end", or no manifest yet; 10 not launched from this
# RB_OUT.
#   bash tools/claims-v3/e193/rb/s20_wait_e193.sh A|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e193.sh"
rb_init s20_wait
sit=${1:-}
e193_cap_s "$sit" > /dev/null || rb_die $RB_E_USAGE "usage: s20_wait_e193.sh A|B"
run=e193-$sit; box=aifoundry3
want=; [ -f "$RB_OUT/e193-$sit-T0.txt" ] && want=$(cat "$RB_OUT/e193-$sit-T0.txt")
[ -n "${RB_DRY:-}" ] || [ -n "$want" ] || rb_die $RB_E_USAGE "RB_OUT holds no e193-$sit-T0.txt: step 9 has not launched sitting $sit from this RB_OUT"
rb_probe "$box"
f=$(rb_file "wait-$run")
{ rb_prelude "$box"
  echo "RUN=$run; LIM=$RB_WAIT_LOOP_S; WANT='${want:-DRY}'"
  cat <<'EOF2'
fresh build/q141k/$RUN.T0 || { echo "RUN-UNKNOWN $RUN: not launched today by the runbook (no T0 written today)"; exit 3; }
T0=$(cat build/q141k/$RUN.T0)
[ "$WANT" = DRY ] || [ "$T0" = "$WANT" ] || { echo "RUN-UNKNOWN $RUN: the box's last launch T0 $T0 is not this runbook's $WANT"; exit 3; }
SD=build/e193/T$T0; L=$SD/session.log
ended() { grep -q 'session end' "$L" 2>/dev/null; }
while ! ended && [ "$SECONDS" -lt "$LIM" ]; do
  pgrep -u "$(id -u)" -f 'session_e193\.sh' > /dev/null || { sleep 2; ended || { echo "RUN-GONE $RUN: no session_e193.sh process and no session end"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
grep -E 'session start|HARNESS|preflight|first card command|config read|deadline|smoke|SMOKE|main run|GATE-STOP|session end' "$L" 2>/dev/null | cut -c1-240 | tail -n 30
tail -n 2 "$SD/x04/run.log" 2>/dev/null | cut -c1-200 | sed 's/^/runner: /'
if ended; then
  echo "RUN-ENDED $RUN"
  sleep 2
  if [ -s "$SD/MANIFEST.sha256" ]; then echo "MANIFEST-WRITTEN $(grep -c . "$SD/MANIFEST.sha256") files"; else echo "MANIFEST-ABSENT"; fi
else echo "RUN-RUNNING $RUN after $t s"; fi
if grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ GATE-STOP: ' "$L" 2>/dev/null; then echo "GATE-STOPPED $RUN"; fi
if grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ main run stopped: ' "$L" 2>/dev/null; then echo "MAIN-STOPPED $RUN"; fi
if grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ main run ended without a registered stop: ' "$L" 2>/dev/null; then echo "MAIN-CRASHED $RUN"; fi
EOF2
} > "$f"
rb_remote wait "$box" "one bounded wait on $run" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on $run exited $RB_RC"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "$run is not running and recorded no end: read the box's logs (read-only) before anything else; the rest rule then counts it at its run's latest write"
rb_has '^MANIFEST-ABSENT' && rb_die $RB_E_FAIL "$run has ended but its MANIFEST.sha256 is not written: wait once more, then read the box (read-only) before step 11"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "$run ended at a gate before its main run (the lines above): step 11 still collects it, as a gate stop's record (no sitting, no data: E193.md 11)"
rb_has '^RUN-ENDED' && rb_has '^MAIN-CRASHED' && rb_die $RB_E_GATE "$run's main run ended WITHOUT a registered stop (a crash: the lines above; E193.md 11 lists no such end): kill nothing; collect it (step 11, its data directory) and report it; a dated note decides whether its passes are reduced, and no further sitting runs before that note"
if rb_has '^RUN-ENDED'; then
  rb_has '^MAIN-STOPPED' && rb_say "$run's main run ended at a registered stop (the lines above): the passes done stand (E193.md 11)"
  rb_say "$run has ended ($(grep -m1 '^MANIFEST-WRITTEN' "$RB_CAP"))"
  exit 0
fi
rb_say "$run still runs: call again"
exit $RB_E_AGAIN
