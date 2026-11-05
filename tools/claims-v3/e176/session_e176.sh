#!/usr/bin/env bash
# E176 (Q143(k)): M11's card session on aifoundry3 card 0, detached on the box after this card's clause is in the day's post. One call, in
# a script file run by `ssh aifoundry3 'bash -s'`, from the tree that holds the binaries (~/aifoundry):
#   E176_T0=$(date +%s) E176_LATEST_START='YYYY-MM-DD HH:MM PST' E176_END_GATE='YYYY-MM-DD HH:MM PST' \
#     setsid nohup bash tools/claims-v3/e176/session_e176.sh > build/e176/session.out 2>&1 < /dev/null &
# E166's session_e166.sh (c75bc460) with E176's names, unchanged otherwise: the day's gates come from the launch and have no default (none
# set: exit 8, no device opened); the budget is 76 card-minutes from T0 (REGISTRATION.md section 5's cap) and there is no subset, so the
# session starts only if T0 + 76 min is at or before the end gate (else exit 8, no device opened); the measured pass's deadline is
# T0 + 76 min - 60 s.
#   0. the gates above;
#   1. sha256sum -c tools/claims-v3/e176/frozen-e176.sha256 (exit 9, no device opened, if any file differs);
#   2. the device-command preflight preflight_e176.sh (anything but GO: exit 3, no device opened);
#   3. et-who, then the session-start config read (E128's guard, config only, under card 0's lock, timeout 10);
#   4. the smoke and the five stop tests on live samples (block_e176.sh 17601 --smoke), then smoke_gate_e176.py on it; the measured pass runs
#      only if both pass;
#   5. the measured pass, block_e176.sh 17620 (M11's section 5 design; E166's start gate G0 at R0's end), unless build/e176/STOP or
#      build/claims-v3/STOP exists;
#   6. the session-end config read, et-who.
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# A desk dry pass off the box: V3_DRY=1 E176_DESK=1 (the box-only binaries are listed, not checked; et-who is not run).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
if [ -n "${E176_DESK:-}" ] && [ -z "${V3_DRY:-}" ]; then echo "E176_DESK is for a dry pass only (V3_DRY=1)" >&2; exit 2; fi
: "${E176_T0:?E176_T0 - the session anchor, epoch seconds}"
mkdir -p build/e176
LOG=build/e176/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
whoread() { if [ -n "${E176_DESK:-}" ]; then say "DESK: et-who not run off the box"; else timeout 20 et-who >> "$LOG" 2>&1; fi; }
say "session start (T0 $(date -d @"$E176_T0" '+%T %Z'))"
[ -n "${E176_LATEST_START:-}" ] && [ -n "${E176_END_GATE:-}" ] || { say "the day's gates are not set (E176_LATEST_START, E176_END_GATE): no device opened"; exit 8; }
latest=$(date -d "$E176_LATEST_START" +%s) && endgate=$(date -d "$E176_END_GATE" +%s) || { say "unreadable gates: no device opened"; exit 8; }
now=$(date +%s)
BUDGET_S=4560
[ "$now" -le "$latest" ] || { say "no new card session after $(date -d @"$latest" '+%F %T %Z'): no device opened"; exit 8; }
[ $((E176_T0 + BUDGET_S)) -le "$endgate" ] || { say "T0 + 76 min passes the end gate $(date -d @"$endgate" '+%T %Z') and there is no subset: no device opened"; exit 8; }
dl=$((E176_T0 + BUDGET_S - 60))
say "the full design (no subset): budget $BUDGET_S s from T0, the pass's deadline $(date -d @"$dl" '+%T %Z')"
if [ -n "${E176_DESK:-}" ]; then
  sha256sum -c --quiet --ignore-missing tools/claims-v3/e176/frozen-e176.sha256 >> "$LOG" 2>&1; h=$?
  for f in $(awk '{print $2}' tools/claims-v3/e176/frozen-e176.sha256); do [ -e "$f" ] || say "DESK: box-only, not checked here: $f"; done
else
  sha256sum -c --quiet tools/claims-v3/e176/frozen-e176.sha256 >> "$LOG" 2>&1; h=$?
fi
[ "$h" -eq 0 ] || { say "a registered file differs (frozen-e176.sha256): no device opened"; exit 9; }
say "frozen-e176.sha256: every file as registered"
bash tools/claims-v3/e176/preflight_e176.sh > build/e176/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e176/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "the device-command preflight is not GO: no device opened"; exit 3; }
whoread
cfg build/e176/config-session-start.json
DR=build/claims-v3${V3_DRY:+-dry}/aifoundry3
bash tools/claims-v3/e176/block_e176.sh 17601 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
say "smoke and stop tests rc=$rc"
python3 tools/claims-v3/e176/smoke_gate_e176.py "$DR/e176-smoke/p17601" > build/e176/smoke-gate.json 2>> "$LOG"; g=$?
say "smoke gate rc=$g: $(head -c 600 build/e176/smoke-gate.json)"
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "the smoke or its gate failed: no measured pass"
elif [ -e build/e176/STOP ] || [ -e build/claims-v3/STOP ]; then
  say "STOP file: no measured pass"
else
  say "pass 17620 starts: the full design, deadline $(date -d @"$dl" '+%T %Z')"
  E176_DEADLINE_EPOCH=$dl bash tools/claims-v3/e176/block_e176.sh 17620 < /dev/null >> "$LOG" 2>&1; prc=$?
  case $prc in 7) say "pass 17620 rc=7: the start gate (R0's room above 53.0 C): no hold ran, E176 not started" ;; *) say "pass 17620 rc=$prc" ;; esac
fi
cfg build/e176/config-session-end.json
whoread
say "session end"
