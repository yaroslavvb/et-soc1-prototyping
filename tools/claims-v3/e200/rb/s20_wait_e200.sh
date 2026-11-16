#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum), the box step "the wait" (this file is s20), one sitting a call: one
# bounded wait on E200's sitting (aifoundry2: the session log of the T0 the runbook launched today); each call ends within the remote loop's
# 520 s; call again while it says 17. It never touches the card. E197's step 10 (tools/claims-v3/e197/rb/s20_wait_e197.sh, unchanged
# beside it) on this box, with E194's reading of our processes:
#   - THE SESSION'S PROCESS IS FOUND BY ITS REAL SCRIPT NAME, session_e200.sh, AS ITS OWN SCRIPT (E194's ours_live: an interpreter whose
#     script argument's base name is session_e200.sh; never a command string's text, since on this box the desk's own commands, which name
#     the script in their text, run beside the session): the launch runs `bash <E200's root>/tools/claims-v3/e200/session_e200.sh`; the
#     runbook's desk test runs this step against the real session_e200.sh running on a stand-in box (RUN-RUNNING) and against finished
#     real-path logs; THE QUIET DESK FLAG must be up (e200_quiet);
#   - A GATE STOP IS READ ONLY FROM THE WRAPPER'S OWN GATE LINES, "<time> GATE-STOP: ...", which session_e200.sh writes only when the
#     sitting ended before any block of trains.tsv began (a refusal, the card not free, the die gate, the smoke gate, the kit's smoke check
#     with the smoke's clock, a holder or the lock before block A); a registered stop after the trains began ("stop: ...") is not a gate:
#     the trains done stand;
#   - A CRASH IS NOT A REGISTERED STOP: "<time> the trains ended without a registered stop: ..." (the wrapper's exit 9) is read as CRASHED
#     and stops the day (16): kill nothing, collect it (step 11), report it; a dated note decides whether its trains are reduced, and no
#     sitting 2 runs before that note (steps 7 and 9 refuse);
#   - A HUNG DEVICE PROCESS (the kit's watch: "<time> HUNG: ...": a host still running after its timeout's TERM; departure D1, no KILL) is
#     read as HUNG at once, ended or not (16): kill nothing, keep the booking, the hold, the quiet desk flag and the card lock as they are,
#     write it up and escalate to the owner (CARD-LANE-BRIEF.md 3); never reset the card.
# The T0 is the launch's own (build/q141k/e200-<n>.T0, written today, the same as RB_OUT's e200-<n>-T0.txt), its log
# build/e200/T<T0>/session.log; when the session has ended, the wait also says whether its MANIFEST.sha256 is written (the collection's
# exact copy-back reads it). Exit: 0 ended (manifest written; "STOPPED" reported if a registered stop ended it after the trains began);
# 16 ended at a gate (step 11 still collects it, as a gate stop's record), or CRASHED, or HUNG; 17 still running; 14 gone without
# "session end", or no manifest yet; 10 not launched from this RB_OUT.
#   RB_QUIET=<the flag file> bash tools/claims-v3/e200/rb/s20_wait_e200.sh 1|2
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e200.sh"
rb_init s20_wait
sit=${1:-}
e200_sit_ok "$sit" || rb_die $RB_E_USAGE "usage: s20_wait_e200.sh 1|2"
e200_quiet
run=e200-$sit; box=aifoundry2
want=; [ -f "$RB_OUT/e200-$sit-T0.txt" ] && want=$(cat "$RB_OUT/e200-$sit-T0.txt")
[ -n "${RB_DRY:-}" ] || [ -n "$want" ] || rb_die $RB_E_USAGE "RB_OUT holds no e200-$sit-T0.txt: step 9 has not launched sitting $sit from this RB_OUT"
rb_probe "$box"
f=$(rb_file "wait-$run")
{ rb_prelude "$box"
  echo "RUN=$run; LIM=$RB_WAIT_LOOP_S; WANT='${want:-DRY}'"
  cat <<'EOF2'
fresh build/q141k/$RUN.T0 || { echo "RUN-UNKNOWN $RUN: not launched today by the runbook (no T0 written today)"; exit 3; }
T0=$(cat build/q141k/$RUN.T0)
[ "$WANT" = DRY ] || [ "$T0" = "$WANT" ] || { echo "RUN-UNKNOWN $RUN: the box's last launch T0 $T0 is not this runbook's $WANT"; exit 3; }
SD=build/e200/T$T0; L=$SD/session.log
ended() { grep -q 'session end' "$L" 2>/dev/null; }
hung() { grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ HUNG: ' "$L" 2>/dev/null; }
while ! ended && ! hung && [ "$SECONDS" -lt "$LIM" ]; do
  [ "$(ours_live session_e200.sh)" -gt 0 ] || { sleep 2; ended || { echo "RUN-GONE $RUN: no session_e200.sh process and no session end"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
grep -E 'session start|checked:|first card command|running:|smoke|train blocks|the deadline|stop:|SITTING-RESULT|GATE-STOP|HUNG|without a registered stop|card time|session end' "$L" 2>/dev/null | cut -c1-260 | tail -n 30
tail -n 2 "$SD/run/session.log" 2>/dev/null | cut -c1-200 | sed 's/^/reference: /'
if hung; then echo "HUNG $RUN"; fi
if ended; then
  echo "RUN-ENDED $RUN"
  sleep 2
  if [ -s "$SD/MANIFEST.sha256" ]; then echo "MANIFEST-WRITTEN $(grep -c . "$SD/MANIFEST.sha256") files"; else echo "MANIFEST-ABSENT"; fi
else echo "RUN-RUNNING $RUN after $t s"; fi
if grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ GATE-STOP: ' "$L" 2>/dev/null; then echo "GATE-STOPPED $RUN"; fi
if grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ stop: [^n]' "$L" 2>/dev/null; then echo "STOPPED $RUN"; fi
if grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ the trains ended without a registered stop: ' "$L" 2>/dev/null; then echo "CRASHED $RUN"; fi
EOF2
} > "$f"
rb_remote wait "$box" "one bounded wait on $run" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on $run exited $RB_RC"
rb_has '^HUNG ' && rb_die $RB_E_GATE "$run: a device process did not end after its timeout's TERM (the HUNG line above): KILL NOTHING, reset nothing; keep the booking, the hold, the quiet desk flag and the card lock as they are; write it up and escalate to the owner (CARD-LANE-BRIEF.md 3)"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "$run is not running and recorded no end: read the box's logs (read-only) before anything else; the rest rule then counts it at its run's latest write"
rb_has '^MANIFEST-ABSENT' && rb_die $RB_E_FAIL "$run has ended but its MANIFEST.sha256 is not written: wait once more, then read the box (read-only) before step 11"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "$run ended at a gate before any block of trains.tsv began (the lines above): step 11 still collects it, as a gate stop's record (no train block, no data: E200.md 13)"
rb_has '^RUN-ENDED' && rb_has '^CRASHED' && rb_die $RB_E_GATE "$run's trains ended WITHOUT a registered stop (a crash: the lines above; E200.md 13 lists no such end): kill nothing; collect it (step 11, its data directory) and report it; a dated note decides whether its trains are reduced, and no sitting 2 runs before that note"
if rb_has '^RUN-ENDED'; then
  rb_has '^STOPPED' && rb_say "$run ended at a registered stop after its trains began (the lines above): the trains done stand, reduced as they stand (E200.md 13)"
  rb_say "$run has ended ($(grep -m1 '^MANIFEST-WRITTEN' "$RB_CAP"))"
  exit 0
fi
rb_say "$run still runs: call again"
exit $RB_E_AGAIN
