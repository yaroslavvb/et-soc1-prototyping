#!/usr/bin/env bash
# E197 (Q185, lane kit-e197, Sun 15 Nov 2026, before any E197 datum): the device-command preflight, Q136(w)'s checker
# tools/claims-v3/dmcmd_audit.py with the stock table (tools/claims-v3/dmcmd_table.json), NO --allow (no WRITE of any kind, not even the
# statistics reset) and NO --except, over every file whose commands E197's sittings send to the card or its management node:
#   - the kit's session wrapper, watch, checker, build and harness (session_e197.sh, watch_e197.py, check_e197.py, build_e197.sh,
#     harness_e197.py: they send nothing themselves; the build runs the host only to refusals before the device layer);
#   - the proposal's reference session as registered: proposal/src/run_session.sh (the one sampler, "$ETTELEM" sample --seconds T
#     --every-ms 100, ETTELEM being E128's guard below; et-who --check; flock on the existing lock file), proposal/src/stopwatch.py
#     (reads the telemetry file), and the lab's runner lab/run_trains.py (departure D1: `timeout 10` around every host process);
#   - the host's and the kernel's source (proposal/src/host/main.cpp: createPcieDeviceLayer(true, false), the ops node only, the
#     runtime's loads, copies, allocations and launches; proposal/src/regfile_args.h; proposal/src/kernel/regfile.c);
#   - E128's guard (tools/claims-v3/e128/ettelem_guard.sh): the session's sampler (`sample --seconds --every-ms` only) and k6's step 7
#     config read (`config` only); it refuses --reset-ms and every other word before the device opens.
# et-who reads /proc (et-holders: fuser stats the nodes, never opens them) and sends no device command.
# Run from the repository's top (at the desk) or from E197's root on the box (which holds the same paths). Prints the checker's lines,
# then "dmcmd_audit: GO ..." on its first line (the checker's own). Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e197/preflight_e197.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
F=(tools/claims-v3/e197/session_e197.sh tools/claims-v3/e197/watch_e197.py tools/claims-v3/e197/check_e197.py
   tools/claims-v3/e197/build_e197.sh tools/claims-v3/e197/harness_e197.py
   tools/claims-v3/e197/proposal/src/run_session.sh tools/claims-v3/e197/proposal/src/stopwatch.py tools/claims-v3/e197/lab/run_trains.py
   tools/claims-v3/e197/proposal/src/host/main.cpp tools/claims-v3/e197/proposal/src/regfile_args.h
   tools/claims-v3/e197/proposal/src/kernel/regfile.c tools/claims-v3/e128/ettelem_guard.sh)
python3 tools/claims-v3/dmcmd_audit.py "${F[@]}"
