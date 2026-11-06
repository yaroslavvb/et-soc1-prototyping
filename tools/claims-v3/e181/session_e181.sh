#!/usr/bin/env bash
# E181 (M11's session 2): M11's card session on aifoundry3 card 0, detached on the box after this card's clause is in the day's post. One
# call, in a script file run by `ssh aifoundry3 'bash -s'`, from the tree that holds the binaries (~/aifoundry):
#   E181_T0=$(date +%s) E181_LATEST_START='YYYY-MM-DD HH:MM PST' E181_END_GATE='YYYY-MM-DD HH:MM PST' \
#     setsid nohup bash tools/claims-v3/e181/session_e181.sh > build/e181/session.out 2>&1 < /dev/null &
# E176's session_e176.sh (03582d2f, which stays as committed) with E181's names and these changes, each marked E181:
#   1. a V3_DRY session writes its own log, build/e181/session-dry.log, and ends it with "DRY session end"; only a real session writes
#      build/e181/session.log and its "session end" (E176's runbook note 2, section 1: step 11's rest rule counted a dry session's end);
#   2. the smoke's exit 7 is A6-1's stop (F0 above 53.9 C or unreadable): the session ends there, before the smoke's first launch, with no
#      smoke gate and no measured pass;
#   3. the measured pass reads F0 from the smoke pass's floor mark (E181_FLOOR_MARKS, the smoke's marks.jsonl), for A6-2 with A8-4.
# Unchanged from E176: the day's gates come from the launch and have no default (none set: exit 8, no device opened); the budget is 76
# card-minutes from T0 (REGISTRATION.md section 5's cap) and there is no subset, so the session starts only if T0 + 76 min is at or before
# the end gate (else exit 8, no device opened); the measured pass's deadline is T0 + 76 min - 60 s.
#   0. the gates above;
#   1. sha256sum -c tools/claims-v3/e181/frozen-e181.sha256 (exit 9, no device opened, if any file differs);
#   2. the device-command preflight preflight_e181.sh (anything but GO: exit 3, no device opened);
#   3. et-who, then the session-start config read (E128's guard, config only, under card 0's lock, timeout 10);
#   4. the smoke (A6-1's floor mark first) and the five stop tests on live samples (block_e181.sh 18101 --smoke), then smoke_gate_e181.py
#      on it; the measured pass runs only if both pass;
#   5. the measured pass, block_e181.sh 18120 (M11's section 5 design; G0-A6 with A8-4 at R0's end), unless build/e181/STOP or
#      build/claims-v3/STOP exists;
#   6. the session-end config read, et-who.
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# A desk dry pass off the box: V3_DRY=1 E181_DESK=1 (the box-only binaries are listed, not checked; et-who is not run).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
if [ -n "${E181_DESK:-}" ] && [ -z "${V3_DRY:-}" ]; then echo "E181_DESK is for a dry pass only (V3_DRY=1)" >&2; exit 2; fi
: "${E181_T0:?E181_T0 - the session anchor, epoch seconds}"
mkdir -p build/e181
LOG=build/e181/session.log; END="session end"
[ -n "${V3_DRY:-}" ] && { LOG=build/e181/session-dry.log; END="DRY session end"; }                     # E181 change 1
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
whoread() { if [ -n "${E181_DESK:-}" ]; then say "DESK: et-who not run off the box"; else timeout 20 et-who >> "$LOG" 2>&1; fi; }
say "session start (T0 $(date -d @"$E181_T0" '+%T %Z'))${V3_DRY:+ DRY}"
[ -n "${E181_LATEST_START:-}" ] && [ -n "${E181_END_GATE:-}" ] || { say "the day's gates are not set (E181_LATEST_START, E181_END_GATE): no device opened"; exit 8; }
latest=$(date -d "$E181_LATEST_START" +%s) && endgate=$(date -d "$E181_END_GATE" +%s) || { say "unreadable gates: no device opened"; exit 8; }
now=$(date +%s)
BUDGET_S=4560
[ "$now" -le "$latest" ] || { say "no new card session after $(date -d @"$latest" '+%F %T %Z'): no device opened"; exit 8; }
[ $((E181_T0 + BUDGET_S)) -le "$endgate" ] || { say "T0 + 76 min passes the end gate $(date -d @"$endgate" '+%T %Z') and there is no subset: no device opened"; exit 8; }
dl=$((E181_T0 + BUDGET_S - 60))
say "the full design (no subset): budget $BUDGET_S s from T0, the pass's deadline $(date -d @"$dl" '+%T %Z')"
if [ -n "${E181_DESK:-}" ]; then
  sha256sum -c --quiet --ignore-missing tools/claims-v3/e181/frozen-e181.sha256 >> "$LOG" 2>&1; h=$?
  for f in $(awk '{print $2}' tools/claims-v3/e181/frozen-e181.sha256); do [ -e "$f" ] || say "DESK: box-only, not checked here: $f"; done
else
  sha256sum -c --quiet tools/claims-v3/e181/frozen-e181.sha256 >> "$LOG" 2>&1; h=$?
fi
[ "$h" -eq 0 ] || { say "a registered file differs (frozen-e181.sha256): no device opened"; exit 9; }
say "frozen-e181.sha256: every file as registered"
bash tools/claims-v3/e181/preflight_e181.sh > build/e181/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e181/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "the device-command preflight is not GO: no device opened"; exit 3; }
whoread
cfg build/e181/config-session-start.json
DR=build/claims-v3${V3_DRY:+-dry}/aifoundry3
bash tools/claims-v3/e181/block_e181.sh 18101 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
say "smoke and stop tests rc=$rc"
if [ "$rc" -eq 7 ]; then                                                                                # E181 change 2
  say "A6-1: F0 above 53.9 C or unreadable (the smoke's floor mark): the session ends before the smoke's first launch, no hold (exit 7)"
else
  python3 tools/claims-v3/e181/smoke_gate_e181.py "$DR/e181-smoke/p18101" > build/e181/smoke-gate.json 2>> "$LOG"; g=$?
  say "smoke gate rc=$g: $(head -c 600 build/e181/smoke-gate.json)"
  if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
    say "the smoke or its gate failed: no measured pass"
  elif [ -e build/e181/STOP ] || [ -e build/claims-v3/STOP ]; then
    say "STOP file: no measured pass"
  else
    say "pass 18120 starts: the full design, deadline $(date -d @"$dl" '+%T %Z'), F0 from $DR/e181-smoke/p18101/marks.jsonl"
    E181_FLOOR_MARKS="$DR/e181-smoke/p18101/marks.jsonl" E181_DEADLINE_EPOCH=$dl bash tools/claims-v3/e181/block_e181.sh 18120 < /dev/null >> "$LOG" 2>&1; prc=$?
    case $prc in
      7) say "pass 18120 rc=7: the start gate (G0-A6 with A8-4: R0's room above 53.9 C, or its residue less 0.414 C above 0.50 C): no hold ran, E181 not started" ;;
      *) say "pass 18120 rc=$prc" ;;
    esac
  fi
fi
cfg build/e181/config-session-end.json
whoread
say "$END"
