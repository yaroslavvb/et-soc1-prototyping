#!/usr/bin/env bash
# E185 (M11's session 3): M11's card session on aifoundry3 card 0, detached on the box after this card's clause is in the day's post. One
# call, in a script file run by `ssh aifoundry3 'bash -s'`, from the tree that holds the binaries (~/aifoundry):
#   E185_T0=$(date +%s) E185_LATEST_START='YYYY-MM-DD HH:MM PST' E185_END_GATE='YYYY-MM-DD HH:MM PST' \
#     setsid nohup bash tools/claims-v3/e185/session_e185.sh > build/e185/session-$E185_T0.out 2>&1 < /dev/null &
# E181's session_e181.sh (33cdccf6, which stays as committed) with E185's names and these changes, each marked E185:
#   1. T0-named files: every file the session writes of its own lives in build/e185/T<T0>/ (a V3_DRY session's in build/e185/T<T0>-dry/):
#      session.log (a dry session: session-dry.log, ending "DRY session end"), the two config reads with their .err and .time, the
#      device-command preflight and the smoke gate. A T0 directory that exists already is refused (exit 8, no device opened), so a second
#      session never writes over a first; a real session writes build/e185/LAST_T0 at its start;
#   2. the session's last act is build/e185/T<T0>/MANIFEST.sha256: the sha256 of every file of the T0 directory and of both pass directories
#      (their telemetry.jsonl.raw and tiles/ left out, as the collection leaves them out), written after the "session end" line. The
#      collection copies back exactly these files and checks each one against it (step 22's exact copy-back);
#   3. the budget is 105 card-minutes from T0 (E185.md section 8's cap), the measured pass's deadline T0 + 105 min - 60 s; the passes are
#      18501 (the smoke and its six stop tests) and 18520 (E185.md section 4's six holds);
#   4. the measured pass's exit 6 is a stop line (E171's stops: the pass ended), named in the log.
# Unchanged from E181: the day's gates come from the launch and have no default (none set: exit 8, no device opened); the session starts only
# if T0 + 105 min is at or before the end gate (no subset); the frozen list (exit 9), the device-command preflight (exit 3), et-who, the
# config reads through E128's guard (config only, card 0's lock, timeout 10), the smoke with A6-1's floor mark first (its exit 7 ends the
# session before the smoke's first launch), the smoke gate, the measured pass with F0 from the smoke's floor mark (G0-A6 with A8-4 at R0's
# end), the STOP files.
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# A desk dry pass off the box: V3_DRY=1 E185_DESK=1 (the box-only binaries are listed, not checked; et-who is not run).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
if [ -n "${E185_DESK:-}" ] && [ -z "${V3_DRY:-}" ]; then echo "E185_DESK is for a dry pass only (V3_DRY=1)" >&2; exit 2; fi
: "${E185_T0:?E185_T0 - the session anchor, epoch seconds}"
case "$E185_T0" in ''|*[!0-9]*) echo "E185_T0 must be epoch seconds" >&2; exit 2 ;; esac
mkdir -p build/e185
SD=build/e185/T$E185_T0${V3_DRY:+-dry}                                                                     # E185 change 1
if [ -e "$SD" ]; then echo "$(date '+%F %T %Z') $SD exists already: a second session never writes over a first: no device opened" >&2; exit 8; fi
mkdir -p "$SD"
LOG=$SD/session.log; END="session end"
[ -n "${V3_DRY:-}" ] && { LOG=$SD/session-dry.log; END="DRY session end"; }
[ -z "${V3_DRY:-}" ] && echo "$E185_T0" > build/e185/LAST_T0
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
whoread() { if [ -n "${E185_DESK:-}" ]; then say "DESK: et-who not run off the box"; else timeout 20 et-who >> "$LOG" 2>&1; fi; }
DR=build/claims-v3${V3_DRY:+-dry}/aifoundry3
manifest() {                                                                                               # E185 change 2 (a dry session writes its own, in its -dry directory)
  { find "$SD" -type f ! -name 'MANIFEST.sha256*'
    for p in "$DR/e185-smoke/p18501" "$DR/e185/p18520"; do
      [ -d "$p" ] && find "$p" -type f ! -name telemetry.jsonl.raw ! -path '*/tiles/*'
    done
  } | LC_ALL=C sort | while read -r f; do sha256sum "$f"; done > "$SD/MANIFEST.sha256.tmp" && mv "$SD/MANIFEST.sha256.tmp" "$SD/MANIFEST.sha256"
}
finish() { cfg "$SD/config-session-end.json"; whoread; say "$END"; manifest; }
say "session start (T0 $(date -d @"$E185_T0" '+%T %Z'); its files in $SD)${V3_DRY:+ DRY}"
[ -n "${E185_LATEST_START:-}" ] && [ -n "${E185_END_GATE:-}" ] || { say "the day's gates are not set (E185_LATEST_START, E185_END_GATE): no device opened"; say "$END"; manifest; exit 8; }
latest=$(date -d "$E185_LATEST_START" +%s) && endgate=$(date -d "$E185_END_GATE" +%s) || { say "unreadable gates: no device opened"; say "$END"; manifest; exit 8; }
now=$(date +%s)
BUDGET_S=6300                                                                                              # E185 change 3
[ "$now" -le "$latest" ] || { say "no new card session after $(date -d @"$latest" '+%F %T %Z'): no device opened"; say "$END"; manifest; exit 8; }
[ $((E185_T0 + BUDGET_S)) -le "$endgate" ] || { say "T0 + 105 min passes the end gate $(date -d @"$endgate" '+%T %Z') and there is no subset: no device opened"; say "$END"; manifest; exit 8; }
dl=$((E185_T0 + BUDGET_S - 60))
say "the full design (no subset): budget $BUDGET_S s from T0, the pass's deadline $(date -d @"$dl" '+%T %Z')"
if [ -n "${E185_DESK:-}" ]; then
  sha256sum -c --quiet --ignore-missing tools/claims-v3/e185/frozen-e185.sha256 >> "$LOG" 2>&1; h=$?
  for f in $(awk '{print $2}' tools/claims-v3/e185/frozen-e185.sha256); do [ -e "$f" ] || say "DESK: box-only, not checked here: $f"; done
else
  sha256sum -c --quiet tools/claims-v3/e185/frozen-e185.sha256 >> "$LOG" 2>&1; h=$?
fi
[ "$h" -eq 0 ] || { say "a registered file differs (frozen-e185.sha256): no device opened"; say "$END"; manifest; exit 9; }
say "frozen-e185.sha256: every file as registered"
bash tools/claims-v3/e185/preflight_e185.sh > "$SD/dmcmd-preflight.txt" 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' "$SD/dmcmd-preflight.txt"))"
[ "$a" -eq 0 ] || { say "the device-command preflight is not GO: no device opened"; say "$END"; manifest; exit 3; }
whoread
cfg "$SD/config-session-start.json"
bash tools/claims-v3/e185/block_e185.sh 18501 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
say "smoke and stop tests rc=$rc"
if [ "$rc" -eq 7 ]; then
  say "A6-1: F0 above 53.9 C or unreadable (the smoke's floor mark): the session ends before the smoke's first launch, no hold (exit 7)"
else
  python3 tools/claims-v3/e185/smoke_gate_e185.py "$DR/e185-smoke/p18501" > "$SD/smoke-gate.json" 2>> "$LOG"; g=$?
  say "smoke gate rc=$g: $(head -c 600 "$SD/smoke-gate.json")"
  if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
    say "the smoke or its gate failed: no measured pass"
  elif [ -e build/e185/STOP ] || [ -e build/claims-v3/STOP ]; then
    say "STOP file: no measured pass"
  else
    say "pass 18520 starts: the full design, deadline $(date -d @"$dl" '+%T %Z'), F0 from $DR/e185-smoke/p18501/marks.jsonl"
    E185_FLOOR_MARKS="$DR/e185-smoke/p18501/marks.jsonl" E185_DEADLINE_EPOCH=$dl bash tools/claims-v3/e185/block_e185.sh 18520 < /dev/null >> "$LOG" 2>&1; prc=$?
    case $prc in
      6) say "pass 18520 rc=6: a stop line ended the pass (E171's stops); the holds after it did not run" ;;               # E185 change 4
      7) say "pass 18520 rc=7: the start gate (G0-A6 with A8-4: R0's room above 53.9 C, or its residue less 0.414 C above 0.50 C): no hold ran, E185 not started" ;;
      *) say "pass 18520 rc=$prc" ;;
    esac
  fi
fi
finish
