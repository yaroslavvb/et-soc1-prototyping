#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): THE DEVICE-COMMAND PREFLIGHT, Q136(w)'s checker
# tools/claims-v3/dmcmd_audit.py with the stock table (tools/claims-v3/dmcmd_table.json), NO --allow (no WRITE of any kind, not even the
# statistics reset) and NO --except, over every file whose commands E196's day sends to the card:
#   the session's wrapper (session_e196.sh: et-who --check, the lock probe; it sets ETTELEM to E128's guard), the lab port
#   (run_session_e196.sh: `"$ETTELEM" config` and `"$ETTELEM" sample --seconds --every-ms 100` through the guard; run_block_e196.py: the
#   two hosts, under timeout 10; stops_e196.py and e196_lines.py: no device), the proposal's stopwatch.py and make_x14.py (no device), the
#   request's host and kernel sources (proposal/src/host/main.cpp, kernel/sparsity.c: the ops node only), the lab's unchanged sparsity host's
#   source (workloads/sparsity/host/main.cpp: createPcieDeviceLayer(true, false), the ops node only), the build (build_e196.sh: the hosts
#   run only to their refusals, ET_DEVICES=99 and no card node read), and E128's guard (tools/claims-v3/e128/ettelem_guard.sh: config and
#   sample only; --reset-ms and every other word refused before the device opens), whose own lines classify every ettelem call.
# et-who reads /proc and sends no command; flock and timeout send none. Run from the repository's top (at the desk) or from E196's root on
# the box (which holds the same paths). Prints the audit, then "E196-PREFLIGHT: GO" or "E196-PREFLIGHT: NO-GO (rc <n>)" last.
# Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e196/preflight_e196.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
K=tools/claims-v3/e196
F=($K/session_e196.sh $K/run_session_e196.sh $K/run_block_e196.py $K/stops_e196.py $K/e196_lines.py $K/build_e196.sh
   $K/proposal/src/stopwatch.py $K/proposal/src/make_x14.py $K/proposal/src/host/main.cpp $K/proposal/src/kernel/sparsity.c
   workloads/sparsity/host/main.cpp tools/claims-v3/e128/ettelem_guard.sh)
for f in "${F[@]}"; do [ -f "$f" ] || { echo "preflight_e196: no $f"; echo "E196-PREFLIGHT: NO-GO (a file is missing)"; exit 2; }; done
echo "== dmcmd_audit, the stock table (tools/claims-v3/dmcmd_table.json), no --allow, no --except, ${#F[@]} files"
python3 tools/claims-v3/dmcmd_audit.py "${F[@]}"; r=$?
if [ "$r" -eq 0 ]; then echo "E196-PREFLIGHT: GO (the stock table, no --allow, no --except)"; exit 0; fi
echo "E196-PREFLIGHT: NO-GO (rc $r)"
[ "$r" -eq 2 ] && exit 2
exit 3
