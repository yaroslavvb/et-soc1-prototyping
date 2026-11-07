#!/usr/bin/env bash
# E182 (Q153, the kit): the card session on aifoundry3 card 0, detached on the box after the claim is in the day's post. A copy of
# tools/claims-v3/e178/session_e178.sh with E182's files, changes marked E182 (E178's, E171's and E163's kept):
#   1. check_e182.py first (every reused file, every E182 card file, the registration's files, the pinned watcher files, every tile, every
#      binary, the C-check wrapper and, with the trains, the train host and its patched source, byte-identical to harness-e182.json, or no
#      device opens), then the device-command preflight preflight_e182.sh (dmcmd_audit.py on every file the session runs; anything but GO
#      stops it before any device opens);
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 0's lock, timeout 10;
#   3. the stop-path test first (block_e182.sh 18202 --stoptest: no launch), then the smoke (block_e182.sh 18201 --smoke: the ten kinds
#      items, then two processes of T1's train), then the gate smoke_gate_e182.py; the queue starts only if the gate passes the kinds
#      items; if it fails only the train items (or the train host was never built: E182_TRAINS=no), the queue runs E182_PLAN=PASSES, the
#      trains' registered fallback (E182.md section 7), and every train rule reads NOT SCORED;
#   4. the round's time gates, set at his go: E182_LATEST_START (no card session starts after it) and E182_DEADLINE (the queue's latest
#      end) are REQUIRED; E182_PLAN is FULL (default) or PASSES; without them, or past the first, exit 8 and no device opened.
#
#   E182_T0=$(date +%s) E182_LATEST_START='<date>' E182_DEADLINE='<date>' [E182_PLAN=FULL] [E182_TRAINS=yes|no] \
#     setsid nohup bash tools/claims-v3/e182/session_e182.sh > build/e182/session.out 2>&1 < /dev/null &      (from a script file)
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e182/STOP stops the queue before its next item.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
: "${E182_T0:?E182_T0 - the session anchor, epoch seconds}"
export E182_T0
mkdir -p build/e182
LOG=build/e182/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E182_T0" '+%T %Z'); plan ${E182_PLAN:-FULL}; trains ${E182_TRAINS:-yes})"
case "${E182_PLAN:-FULL}" in FULL|PASSES) ;; *) say "E182_PLAN=${E182_PLAN}: only FULL or PASSES: no device opened"; exit 8 ;; esac
export E182_PLAN=${E182_PLAN:-FULL}
case "${E182_TRAINS:-yes}" in yes|no) ;; *) say "E182_TRAINS=${E182_TRAINS}: only yes or no: no device opened"; exit 8 ;; esac
export E182_TRAINS=${E182_TRAINS:-yes}
[ "$E182_TRAINS" = no ] && export E182_PLAN=PASSES
if [ -z "${E182_LATEST_START:-}" ] || [ -z "${E182_DEADLINE:-}" ]; then                                         # E182 change 4
  say "E182_LATEST_START and E182_DEADLINE are required (the round's time gates, set at his go): no device opened"; exit 8
fi
latest=$(date -d "$E182_LATEST_START" +%s) || { say "E182_LATEST_START '$E182_LATEST_START' is not a date: no device opened"; exit 8; }
date -d "$E182_DEADLINE" +%s > /dev/null || { say "E182_DEADLINE '$E182_DEADLINE' is not a date: no device opened"; exit 8; }
export E182_DEADLINE
[ "$(date +%s)" -le "$latest" ] || { say "no new card session after $(date -d @"$latest" '+%F %T %Z'): no device opened"; exit 8; }
CK=(); [ "$E182_TRAINS" = no ] && CK=(--no-trains)
python3 -B tools/claims-v3/e182/check_e182.py ${CK[@]+"${CK[@]}"} >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E182 change 1
bash tools/claims-v3/e182/preflight_e182.sh > build/e182/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e182/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
sha256sum build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/e182host/b/host/sparsity_host build/e182host/src/host/main.cpp \
  build/sparsity/kernel/sparsity.elf tools/claims-v3/ccheck/sparsity_ccheck.sh build/ettelem/ettelem tools/claims-v3/e128/ettelem_guard.sh > build/e182/binaries.sha256 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg build/e182/config-session-start.json                                                                                     # E182 change 2
bash tools/claims-v3/e182/block_e182.sh 18202 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?                                  # E182 change 3
say "stop-path test rc=$st"
if [ "$st" -eq 0 ]; then
  bash tools/claims-v3/e182/block_e182.sh 18201 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no block"
fi
DR=build/claims-v3/aifoundry3
[ -n "${V3_DRY:-}" ] && DR=build/claims-v3-dry/aifoundry3
if [ -n "${V3_DRY:-}" ]; then
  g=0; gt=0; say "DRY: the smoke gate needs a real smoke; not run"
else
  python3 -B tools/claims-v3/e182/smoke_gate_e182.py "$DR/e182-smoke/p18201" "$DR/e182-stoptest/p18202" --part kinds >> "$LOG" 2>&1; g=$?
  gt=1
  if [ "$E182_TRAINS" = yes ]; then
    python3 -B tools/claims-v3/e182/smoke_gate_e182.py "$DR/e182-smoke/p18201" "$DR/e182-stoptest/p18202" --part train >> "$LOG" 2>&1; gt=$?
  fi
fi
if [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no block runs"
else
  if [ "$E182_PLAN" = FULL ] && [ "$gt" -ne 0 ]; then
    say "the train smoke's gate failed (gate $gt) or the trains are off: the queue runs PASSES, the registered fallback; every train rule is NOT SCORED"
    export E182_PLAN=PASSES
  fi
  say "smoke gate passed: queue starts (plan $E182_PLAN)"
  bash tools/claims-v3/e182/queue_e182.sh < /dev/null > build/e182/queue.out 2>&1
  say "queue: $(tail -1 build/e182/queue.out)"
fi
cfg build/e182/config-session-end.json
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
