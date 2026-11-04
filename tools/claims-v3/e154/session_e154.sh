#!/usr/bin/env bash
# E154 (Q139): the card session on aifoundry3 card 0, detached on the box after this lane's clause is in the day's post. One call:
#   E154_T0=$(date +%s) setsid nohup bash tools/claims-v3/e154/session_e154.sh > build/e154/session.out 2>&1 < /dev/null &
# from the tree that holds the binaries (~/aifoundry). E144's stages (setup, probe, smoke, go) and E153's detached session in one script:
#   0. the round's gates (README.md, "Gates"): no session starts after 21:00 PST on Tue 3 Nov 2026 (exit 8, no device opened); the FULL design
#      if T0 is at or before 20:40 PST (budget 76 card-minutes from T0), else the registered SUBSET (budget 47, departure D3); the measured
#      pass's deadline is min(T0 + budget - 60 s, 21:58 PST), so every run ends by 22:00 PST;
#   1. sha256sum -c tools/claims-v3/e154/frozen-e154.sha256 (every reused file, E154's card files, kinds.json, blind6.json, the five hold tiles,
#      the C-logging host, the kernel, the wrapper, ettelem and the guard as registered; exit 9, no device opened, if any differs);
#   2. the device-command preflight preflight_e154.sh (anything but GO: exit 3, no device opened);
#   3. et-who, then the session-start config read (E128's guard, config only, under card 0's lock, timeout 10);
#   4. the smoke and the five stop tests on live samples (block_e154.sh 15401 --smoke), then smoke_gate_e154.py on it (the stop tests, a launch
#      record for each of the five tiles, a sound C log, the 34 raw codes, 600 MHz, the config reads); the measured pass runs only if both pass;
#   5. the measured pass, block_e154.sh 15420 (Q139(e)'s design), unless build/e154/STOP or build/claims-v3/STOP exists;
#   6. the session-end config read, et-who.
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
: "${E154_T0:?E154_T0 - the session anchor, epoch seconds}"
mkdir -p build/e154
LOG=build/e154/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (T0 $(date -d @"$E154_T0" '+%T %Z'))"
latest=$(date -d "${E154_LATEST_START:-2026-11-03 21:00 PST}" +%s)
full_by=$(date -d "${E154_FULL_BY:-2026-11-03 20:40 PST}" +%s)
endgate=$(date -d "${E154_END_GATE:-2026-11-03 21:58 PST}" +%s)
now=$(date +%s)
[ "$now" -le "$latest" ] || { say "no new card session after $(date -d @"$latest" '+%T %Z'): no device opened"; exit 8; }
if [ "$E154_T0" -le "$full_by" ]; then DESIGN=full; BUDGET_S=4560; else DESIGN=subset; BUDGET_S=2820; fi
dl=$((E154_T0 + BUDGET_S - 60)); [ "$dl" -gt "$endgate" ] && dl=$endgate
say "design $DESIGN: budget $BUDGET_S s from T0, the pass's deadline $(date -d @"$dl" '+%T %Z')"
sha256sum -c --quiet tools/claims-v3/e154/frozen-e154.sha256 >> "$LOG" 2>&1 || { say "a registered file differs (frozen-e154.sha256): no device opened"; exit 9; }
say "frozen-e154.sha256: every file as registered"
bash tools/claims-v3/e154/preflight_e154.sh > build/e154/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e154/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "the device-command preflight is not GO: no device opened"; exit 3; }
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e154/config-session-start.json
bash tools/claims-v3/e154/block_e154.sh 15401 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
say "smoke and stop tests rc=$rc"
python3 tools/claims-v3/e154/smoke_gate_e154.py build/claims-v3/aifoundry3/e154-smoke/p15401 > build/e154/smoke-gate.json 2>> "$LOG"; g=$?
say "smoke gate rc=$g: $(head -c 600 build/e154/smoke-gate.json)"
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "the smoke or its gate failed: no measured pass"
elif [ -e build/e154/STOP ] || [ -e build/claims-v3/STOP ]; then
  say "STOP file: no measured pass"
else
  say "pass 15420 starts: design $DESIGN, deadline $(date -d @"$dl" '+%T %Z')"
  E154_DESIGN=$DESIGN E154_DEADLINE_EPOCH=$dl bash tools/claims-v3/e154/block_e154.sh 15420 < /dev/null >> "$LOG" 2>&1; prc=$?
  say "pass 15420 rc=$prc"
fi
cfg build/e154/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
