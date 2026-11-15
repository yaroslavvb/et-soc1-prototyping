#!/usr/bin/env bash
# E191's kit, dated note 2 (Q184, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after
# E191's first session stopped at its smoke gate by a kit defect (1a4bc1e3), before any E191 pass datum; KIT.md.dated-note-2.md):
# step 10 v2: rb/s20_wait_e191.sh (unchanged beside it), whose session pattern names v1's script alone ('session_e191.sh': it reads session v2 as
# RUN-GONE, E183's lesson again), with the pattern 'session_e191*.sh' (E191's ours_live by each process's own script: session_e191.sh and
# session_e191_v2.sh), and one more reading: NOTE2-SESSION, whether the session log's start line names "kit note 2" (a T0 whose log names
# it not is refused, 10: step 9 v2 launches session v2 only). Every other line is v1's. v1's header: E191, the box step "the wait" (this file
# is s20): one bounded wait on E191 (aifoundry1: the session log of the T0 the runbook launched today); each call ends within the remote
# loop's 520 s; call again while it says 17. It never touches the card. E189's step 10 (tools/claims-v3/e189/rb/s20_wait_e189.sh,
# unchanged beside it) with E191's box and two lessons carried in:
#   - THE SESSION'S NAME (E183's lesson: its wait grepped a v1 name and read every v2 session as gone): the session is found by its OWN
#     script, `ours_live session_e191.sh` (E191's ours_live, by each process's own script: the name step 9 launches, session_e191.sh,
#     whose runner runs as its child so its command line names it to the end); the runbook desk test runs this step on the real script;
#   - THE GATE-STOP PATTERN (E190's lesson: its step 10 v2 read the identity gate's PASS line as a gate stop): GATE-STOPPED holds only the
#     runner's gate-stop phrases ("stop-path test failed", "smoke gate failed", "no device opened", "the gate, no launch", "would not
#     start"); the identity gate's pass lines ("identity (a): ...", "identity (b): ...") hold none of them, and every identity failure line
#     ends "the gate, no launch" (rb/selftest_wait_e191.py tests both on stand-in logs and on E189's and E190 arm B's committed logs);
#   - a host that outlived the runner's 30 s bound (the line "BOUND:") is BOUND-SEEN: 16, read the message (report it at once, kill
#     nothing, keep the booking), then step 11 still collects the session.
# The T0 is the launch's own (build/q141k/e191.T0, written today, the same as RB_OUT's e191-T0.txt), its log build/e191/T<T0>/session.log;
# when the session has ended, the wait also says whether its MANIFEST.sha256 is written. A gate-stopped session is 16, and step 11 still
# collects it. Each pass's line carries its reading in words (PASS, SHORT k of K launches, FAILED RUN).
#   bash tools/claims-v3/e191/rb/s20_wait_e191.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e191.sh"
rb_init s20_wait_v2
run=e191; box=aifoundry1
want=; [ -f "$RB_OUT/e191-T0.txt" ] && want=$(cat "$RB_OUT/e191-T0.txt")
[ -n "${RB_DRY:-}" ] || [ -n "$want" ] || rb_die $RB_E_USAGE "RB_OUT holds no e191-T0.txt: step 9 has not launched E191 from this RB_OUT"
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
while ! ended && [ "$SECONDS" -lt "$LIM" ]; do
  [ "$(ours_live "session_${RUN}*.sh")" -gt 0 ] || { sleep 2; ended || { echo "RUN-GONE $RUN: no session process and no session end"; break; }; }
  sleep 15
done
t=$SECONDS
date '+%F %T %Z'
grep -E 'session start|box check|config|identity|stop-path|smoke|pass [0-9]+:|anchor|STOP|BOUND|no device opened|session end' "$L" 2>/dev/null | cut -c1-260 | tail -n 44
if ended; then
  echo "RUN-ENDED $RUN"
  sleep 2
  if [ -s "$SD/MANIFEST.sha256" ]; then echo "MANIFEST-WRITTEN $(grep -c . "$SD/MANIFEST.sha256") files"; else echo "MANIFEST-ABSENT"; fi
else echo "RUN-RUNNING $RUN after $t s"; fi
if grep -qE 'stop-path test failed|smoke gate failed|no device opened|the gate, no launch|would not start' "$L" 2>/dev/null; then echo "GATE-STOPPED $RUN"; fi
if grep -q 'BOUND: ' "$L" 2>/dev/null; then echo "BOUND-SEEN $RUN"; fi
if [ -f "$L" ]; then if grep -q 'plan FULL; kit note 2;' "$L"; then echo "NOTE2-SESSION yes"; else echo "NOTE2-SESSION no"; fi; fi
EOF2
} > "$f"
rb_remote wait "$box" "one bounded wait on $run" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^RUN-UNKNOWN' && rb_die $RB_E_USAGE "$(grep -m1 '^RUN-UNKNOWN' "$RB_CAP")"
rb_has '^NOTE2-SESSION no' && rb_die $RB_E_USAGE "the session at this T0 is not kit note 2's (its start line does not name it): step 10 v2 reads session v2 only"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the wait on $run exited $RB_RC"
rb_has '^RUN-GONE' && rb_die $RB_E_FAIL "$run is not running and recorded no end: read the box's logs (read-only) before anything else; the rest rule then counts it at its run's latest write"
rb_has '^BOUND-SEEN' && rb_die $RB_E_GATE "$run: a host process outlived the runner's 30 s bound (the BOUND line above): report it at once, kill nothing, keep the booking; the queue stopped; step 11 still collects the session once it has ended"
rb_has '^MANIFEST-ABSENT' && rb_die $RB_E_FAIL "$run has ended but its MANIFEST.sha256 is not written: wait once more, then read the box (read-only) before step 11"
rb_has '^GATE-STOPPED' && rb_die $RB_E_GATE "$run ended at a gate (the lines above): then step 11 still collects it"
rb_has '^RUN-ENDED' && { rb_say "$run has ended ($(grep -m1 '^MANIFEST-WRITTEN' "$RB_CAP"))"; exit 0; }
rb_say "$run still runs: call again"
exit $RB_E_AGAIN
