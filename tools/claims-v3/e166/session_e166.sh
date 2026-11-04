#!/usr/bin/env bash
# E166 (Q141(h)): the card session on aifoundry3 card 0, detached on the box after this card's clause is in the day's post. One call, in a
# script file run by `ssh aifoundry3 'bash -s'`, from the tree that holds the binaries (~/aifoundry):
#   E166_T0=$(date +%s) E166_LATEST_START='YYYY-MM-DD HH:MM PST' E166_END_GATE='YYYY-MM-DD HH:MM PST' \
#     setsid nohup bash tools/claims-v3/e166/session_e166.sh > build/e166/session.out 2>&1 < /dev/null &
# E154's session_e154.sh with E166's names and these changes (E166.md D3, D6): the day's gates come from the launch and have no default
# (none set: exit 8, no device opened); the budget is 76 card-minutes from T0 and there is no subset, so the session starts only if
# T0 + 76 min is at or before the end gate (else exit 8, no device opened); the measured pass's deadline is T0 + 76 min - 60 s.
#   0. the gates above;
#   1. sha256sum -c tools/claims-v3/e166/frozen-e166.sha256 (exit 9, no device opened, if any file differs);
#   2. the device-command preflight preflight_e166.sh (anything but GO: exit 3, no device opened);
#   3. et-who, then the session-start config read (E128's guard, config only, under card 0's lock, timeout 10);
#   4. the smoke and the five stop tests on live samples (block_e166.sh 16601 --smoke), then smoke_gate_e166.py on it; the measured pass runs
#      only if both pass;
#   5. the measured pass, block_e166.sh 16620 (Q140(e)'s R5 design; its start gate G0 at R0's end), unless build/e166/STOP or
#      build/claims-v3/STOP exists;
#   6. the session-end config read, et-who.
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# A desk dry pass off the box: V3_DRY=1 E166_DESK=1 (the box-only binaries are listed, not checked; et-who is not run).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
if [ -n "${E166_DESK:-}" ] && [ -z "${V3_DRY:-}" ]; then echo "E166_DESK is for a dry pass only (V3_DRY=1)" >&2; exit 2; fi
: "${E166_T0:?E166_T0 - the session anchor, epoch seconds}"
mkdir -p build/e166
LOG=build/e166/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
whoread() { if [ -n "${E166_DESK:-}" ]; then say "DESK: et-who not run off the box"; else timeout 20 et-who >> "$LOG" 2>&1; fi; }
say "session start (T0 $(date -d @"$E166_T0" '+%T %Z'))"
[ -n "${E166_LATEST_START:-}" ] && [ -n "${E166_END_GATE:-}" ] || { say "the day's gates are not set (E166_LATEST_START, E166_END_GATE): no device opened"; exit 8; }
latest=$(date -d "$E166_LATEST_START" +%s) && endgate=$(date -d "$E166_END_GATE" +%s) || { say "unreadable gates: no device opened"; exit 8; }
now=$(date +%s)
BUDGET_S=4560
[ "$now" -le "$latest" ] || { say "no new card session after $(date -d @"$latest" '+%F %T %Z'): no device opened"; exit 8; }
[ $((E166_T0 + BUDGET_S)) -le "$endgate" ] || { say "T0 + 76 min passes the end gate $(date -d @"$endgate" '+%T %Z') and there is no subset: no device opened"; exit 8; }
dl=$((E166_T0 + BUDGET_S - 60))
say "the full design (no subset): budget $BUDGET_S s from T0, the pass's deadline $(date -d @"$dl" '+%T %Z')"
if [ -n "${E166_DESK:-}" ]; then
  sha256sum -c --quiet --ignore-missing tools/claims-v3/e166/frozen-e166.sha256 >> "$LOG" 2>&1; h=$?
  for f in $(awk '{print $2}' tools/claims-v3/e166/frozen-e166.sha256); do [ -e "$f" ] || say "DESK: box-only, not checked here: $f"; done
else
  sha256sum -c --quiet tools/claims-v3/e166/frozen-e166.sha256 >> "$LOG" 2>&1; h=$?
fi
[ "$h" -eq 0 ] || { say "a registered file differs (frozen-e166.sha256): no device opened"; exit 9; }
say "frozen-e166.sha256: every file as registered"
bash tools/claims-v3/e166/preflight_e166.sh > build/e166/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e166/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "the device-command preflight is not GO: no device opened"; exit 3; }
whoread
cfg build/e166/config-session-start.json
DR=build/claims-v3${V3_DRY:+-dry}/aifoundry3
bash tools/claims-v3/e166/block_e166.sh 16601 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
say "smoke and stop tests rc=$rc"
python3 tools/claims-v3/e166/smoke_gate_e166.py "$DR/e166-smoke/p16601" > build/e166/smoke-gate.json 2>> "$LOG"; g=$?
say "smoke gate rc=$g: $(head -c 600 build/e166/smoke-gate.json)"
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "the smoke or its gate failed: no measured pass"
elif [ -e build/e166/STOP ] || [ -e build/claims-v3/STOP ]; then
  say "STOP file: no measured pass"
else
  say "pass 16620 starts: the full design, deadline $(date -d @"$dl" '+%T %Z')"
  E166_DEADLINE_EPOCH=$dl bash tools/claims-v3/e166/block_e166.sh 16620 < /dev/null >> "$LOG" 2>&1; prc=$?
  case $prc in 7) say "pass 16620 rc=7: the start gate (R0's room above 53.0 C): no hold ran, E166 not started" ;; *) say "pass 16620 rc=$prc" ;; esac
fi
cfg build/e166/config-session-end.json
whoread
say "session end"
