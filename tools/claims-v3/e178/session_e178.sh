#!/usr/bin/env bash
# E178 (Q146, the kit): the card session on aifoundry3 card 0, detached on the box after the claim is in the day's post. A copy of
# tools/claims-v3/e171/session_e171.sh with E178's files, changes marked E178 (E171's and E163's kept):
#   1. check_e178.py first (every reused file, every E178 card file, the registration's files, the pinned watcher files, every tile, every
#      binary and the C-check wrapper byte-identical to harness-e178.json, or no device opens), then the device-command preflight
#      preflight_e178.sh (tools/claims-v3/dmcmd_audit.py on every file the session runs; anything but GO stops it before any device opens);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 0's lock, timeout 10;
#   3. the stop-path test first (block_e178.sh 17802 --stoptest: no launch; the guard's die and board stops and the in-run watcher must
#      each fire on a live sample), then the smoke (block_e178.sh 17801 --smoke: E178.md section 7's ten items, 2 s runs, every launch
#      through the C-logging host), then the gate smoke_gate_e178.py on both; the queue is queue_e178.sh, and it starts only if the gate
#      passes;
#   4. the round's time gates, set at his go (E178.md section 7, "Time gates"): E178_LATEST_START (no card session starts after it) and
#      E178_DEADLINE (the queue's latest end) are REQUIRED, and E178_PLAN is FULL (default) or TWO; without them, or past the first,
#      exit 8 and no device opened.
#
#   E178_T0=$(date +%s) E178_LATEST_START='<date>' E178_DEADLINE='<date>' [E178_PLAN=FULL] \
#     setsid nohup bash tools/claims-v3/e178/session_e178.sh > build/e178/session.out 2>&1 < /dev/null &      (from a script file)
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e178/STOP stops the queue before its next item.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
: "${E178_T0:?E178_T0 - the session anchor, epoch seconds}"
export E178_T0
mkdir -p build/e178
LOG=build/e178/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E178_T0" '+%T %Z'); plan ${E178_PLAN:-FULL})"
case "${E178_PLAN:-FULL}" in FULL|TWO) ;; *) say "E178_PLAN=${E178_PLAN}: only FULL or TWO: no device opened"; exit 8 ;; esac
export E178_PLAN=${E178_PLAN:-FULL}
if [ -z "${E178_LATEST_START:-}" ] || [ -z "${E178_DEADLINE:-}" ]; then                                         # E178 change 4
  say "E178_LATEST_START and E178_DEADLINE are required (the round's time gates, set at his go): no device opened"; exit 8
fi
latest=$(date -d "$E178_LATEST_START" +%s) || { say "E178_LATEST_START '$E178_LATEST_START' is not a date: no device opened"; exit 8; }
date -d "$E178_DEADLINE" +%s > /dev/null || { say "E178_DEADLINE '$E178_DEADLINE' is not a date: no device opened"; exit 8; }
export E178_DEADLINE
[ "$(date +%s)" -le "$latest" ] || { say "no new card session after $(date -d @"$latest" '+%F %T %Z'): no device opened"; exit 8; }
python3 -B tools/claims-v3/e178/check_e178.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E178 change 1
bash tools/claims-v3/e178/preflight_e178.sh > build/e178/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e178/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/sparsity/kernel/sparsity.elf tools/claims-v3/ccheck/sparsity_ccheck.sh build/ettelem/ettelem tools/claims-v3/e128/ettelem_guard.sh > build/e178/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e178/config-session-start.json                                                                                     # E178 change 2
bash tools/claims-v3/e178/block_e178.sh 17802 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?                                  # E178 change 3
say "stop-path test rc=$st"
if [ "$st" -eq 0 ]; then
  bash tools/claims-v3/e178/block_e178.sh 17801 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no pass"
fi
DR=build/claims-v3/aifoundry3
[ -n "${V3_DRY:-}" ] && DR=build/claims-v3-dry/aifoundry3
if [ -n "${V3_DRY:-}" ]; then
  g=0; say "DRY: the smoke gate needs a real smoke; not run"
else
  python3 -B tools/claims-v3/e178/smoke_gate_e178.py "$DR/e178-smoke/p17801" "$DR/e178-stoptest/p17802" >> "$LOG" 2>&1; g=$?
fi
if [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts (plan $E178_PLAN)"
  bash tools/claims-v3/e178/queue_e178.sh < /dev/null > build/e178/queue.out 2>&1
  say "queue: $(tail -1 build/e178/queue.out)"
fi
cfg build/e178/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
