#!/usr/bin/env bash
# E188 (Q165, the kit): the card session on aifoundry3 card 0, detached on the box after the claim is in the day's post. A port of
# tools/claims-v3/e186/session_e186.sh (E186's, run on this card on 9 Nov 2026; itself E182's) with E188's files, changes marked E188
# (E186's, E182's, E178's, E171's and E163's kept):
#   1. check_e188.py first (every reused file, every E188 card file, E182's files the box calls, the registration's files, the pinned
#      watcher files, every tile, every binary, the C-check wrapper and, with the trains, the train host and its patched source,
#      byte-identical to harness-e188.json, or no device opens), then the device-command preflight preflight_e188.sh (dmcmd_audit.py on
#      every file the session runs; anything but GO stops it before any device opens); with the trains, the train host's change is read
#      from its behaviour (train_check_e188.sh, no device call) before any device opens, and again by every block that runs it;
#   2. the two session config reads go through tools/claims-v3/e128/ettelem_guard.sh (config only), under card 0's lock, timeout 10;
#   3. the stop-path test first (block_e188.sh 18802 --stoptest: no launch), then the smoke (block_e188.sh 18801 --smoke: the thirteen kinds
#      items - the tie, E78's six anchors, E188's six new tiles - then two processes of B05's train), then the gate smoke_gate_e188.py; the
#      queue starts only if the gate passes the kinds items; if it fails only the train items (or the train host was never built:
#      E188_TRAINS=no), the queue runs E188_PLAN=PASSES, the trains' registered fallback (E188.md section 6), and every train rule reads NOT
#      SCORED; the queue's first block heats first (E78's protocol: the first heat);
#   4. the window's gates, set at his go: E188_LATEST_START (no card session starts after it) and E188_DEADLINE (the queue's latest end)
#      are REQUIRED; E188_PLAN is FULL (default) or PASSES; without them, or past the first, exit 8 and no device opened;
#   5. the exact copy-back (E186's): the session's own files go in build/e188/T<T0>/ (session.log, queue.out, the config reads, the
#      preflight, binaries.sha256, blocks.txt), build/e188/LAST_T0 names it, and the session's LAST act, on every path after the session
#      directory exists, is build/e188/T<T0>/MANIFEST.sha256: the sha256 of every file of the session directory and of every block
#      directory blocks.txt names (each block appends its own), which step 11's collection copies back by name and checks file for file
#      (COPY-BACK EXACT, else it stops);
#   6. a box that already holds an E188 block directory (build/claims-v3/aifoundry3/e188/p188*, e188-smoke/p188*, e188-stoptest/p188*)
#      refuses (exit 8, no device opened): a block that exists is skipped by lib.sh's block_begin ("already done"), so an earlier session's
#      smoke would be gated again; a dated note moves such directories aside first.
# The rest rule (no E188 launch within 40 minutes of the end of our last real session on aifoundry3, every session-log form our kits write)
# is the runbook's step 9 (rb/rest_rule_e188.sh), sent to the box before this file is launched.
#
#   E188_T0=$(date +%s) E188_LATEST_START='<date>' E188_DEADLINE='<date>' [E188_PLAN=FULL] [E188_TRAINS=yes|no] \
#     setsid nohup bash tools/claims-v3/e188/session_e188.sh > build/e188/session.out 2>&1 < /dev/null &      (from a script file)
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e188/STOP stops the queue before its next item.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
: "${E188_T0:?E188_T0 - the session anchor, epoch seconds}"
export E188_T0
case "$E188_T0" in *[!0-9]*) echo "E188_T0 must be epoch seconds"; exit 8 ;; esac
SD=build/e188/T$E188_T0${V3_DRY:+-dry}                                                                       # E188 change 5
mkdir -p "$SD"
[ -n "${V3_DRY:-}" ] || echo "$E188_T0" > build/e188/LAST_T0
LOG=$SD/session.log
DR=build/claims-v3/aifoundry3
[ -n "${V3_DRY:-}" ] && DR=build/claims-v3-dry/aifoundry3
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
manifest() {   # E188 change 5: the session's last act; a dry session writes its own, in its -dry directory
  { find "$SD" -type f ! -name 'MANIFEST.sha256*'
    if [ -f "$SD/blocks.txt" ]; then
      while IFS= read -r b; do [ -n "$b" ] && [ -d "$b" ] && find "$b" -type f ! -name telemetry.jsonl.raw; done < "$SD/blocks.txt"
    fi
  } | LC_ALL=C sort -u | while read -r f; do sha256sum "$f"; done > "$SD/MANIFEST.sha256.tmp" && mv "$SD/MANIFEST.sha256.tmp" "$SD/MANIFEST.sha256"
}
stop_now() { say "$1"; say "session end"; manifest; exit "$2"; }
say "session start (budget anchor T0 $(date -d @"$E188_T0" '+%T %Z'); plan ${E188_PLAN:-FULL}; trains ${E188_TRAINS:-yes}; its files in $SD)"
case "${E188_PLAN:-FULL}" in FULL|PASSES) ;; *) stop_now "E188_PLAN=${E188_PLAN}: only FULL or PASSES: no device opened" 8 ;; esac
export E188_PLAN=${E188_PLAN:-FULL}
case "${E188_TRAINS:-yes}" in yes|no) ;; *) stop_now "E188_TRAINS=${E188_TRAINS}: only yes or no: no device opened" 8 ;; esac
export E188_TRAINS=${E188_TRAINS:-yes}
[ "$E188_TRAINS" = no ] && export E188_PLAN=PASSES
if [ -z "${E188_LATEST_START:-}" ] || [ -z "${E188_DEADLINE:-}" ]; then                                       # E188 change 4
  stop_now "E188_LATEST_START and E188_DEADLINE are required (the window's gates, set at his go): no device opened" 8
fi
latest=$(date -d "$E188_LATEST_START" +%s) || stop_now "E188_LATEST_START '$E188_LATEST_START' is not a date: no device opened" 8
date -d "$E188_DEADLINE" +%s > /dev/null || stop_now "E188_DEADLINE '$E188_DEADLINE' is not a date: no device opened" 8
export E188_DEADLINE
[ "$(date +%s)" -le "$latest" ] || stop_now "no new card session after $(date -d @"$latest" '+%F %T %Z'): no device opened" 8
used=$(find "$DR/e188" "$DR/e188-smoke" "$DR/e188-stoptest" -mindepth 1 -maxdepth 1 -name 'p188*' 2>/dev/null | head -n 3 | tr '\n' ' ')
[ -z "$used" ] || stop_now "the box already holds E188 block directories ($used): a dated note moves them aside first: no device opened" 8   # E188 change 6
CK=(); [ "$E188_TRAINS" = no ] && CK=(--no-trains)
python3 -B tools/claims-v3/e188/check_e188.py ${CK[@]+"${CK[@]}"} >> "$LOG" 2>&1 || stop_now "harness check failed: no device opened" 9    # E188 change 1
if [ "$E188_TRAINS" = yes ]; then                                                                            # E188 change 1
  bash tools/claims-v3/e188/train_check_e188.sh build/e188host/b/host/sparsity_host >> "$LOG" 2>&1 ||
    stop_now "the train host does not behave as the train change (train_check_e188.sh): no device opened" 9
fi
bash tools/claims-v3/e188/preflight_e188.sh > "$SD/dmcmd-preflight.txt" 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' "$SD/dmcmd-preflight.txt"))"
[ "$a" -eq 0 ] || stop_now "device-command preflight is not GO: no device opened" 3
sha256sum build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/e188host/b/host/sparsity_host build/e188host/src/host/main.cpp \
  build/sparsity/kernel/sparsity.elf tools/claims-v3/ccheck/sparsity_ccheck.sh build/ettelem/ettelem tools/claims-v3/e128/ettelem_guard.sh > "$SD/binaries.sha256" 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
cfg "$SD/config-session-start.json"                                                                          # E188 change 2
bash tools/claims-v3/e188/block_e188.sh 18802 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?                  # E188 change 3
say "stop-path test rc=$st"
if [ "$st" -eq 0 ]; then
  bash tools/claims-v3/e188/block_e188.sh 18801 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no block"
fi
if [ -n "${V3_DRY:-}" ]; then
  g=0; gt=0; say "DRY: the smoke gate needs a real smoke; not run"
else
  python3 -B tools/claims-v3/e188/smoke_gate_e188.py "$DR/e188-smoke/p18801" "$DR/e188-stoptest/p18802" --part kinds >> "$LOG" 2>&1; g=$?
  gt=1
  if [ "$E188_TRAINS" = yes ]; then
    python3 -B tools/claims-v3/e188/smoke_gate_e188.py "$DR/e188-smoke/p18801" "$DR/e188-stoptest/p18802" --part train >> "$LOG" 2>&1; gt=$?
  fi
fi
if [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no block runs"
else
  if [ "$E188_PLAN" = FULL ] && [ "$gt" -ne 0 ]; then
    say "the train smoke's gate failed (gate $gt) or the trains are off: the queue runs PASSES, the registered fallback; every train rule is NOT SCORED"
    export E188_PLAN=PASSES
  fi
  say "smoke gate passed: queue starts (plan $E188_PLAN)"
  bash tools/claims-v3/e188/queue_e188.sh < /dev/null > "$SD/queue.out" 2>&1
  say "queue: $(tail -1 "$SD/queue.out")"
fi
cfg "$SD/config-session-end.json"
timeout 20 et-who >> "$LOG" 2>&1
say "session end"
manifest
