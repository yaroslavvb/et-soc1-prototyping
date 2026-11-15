#!/usr/bin/env bash
# E193 (Q177, lane kit-e193, Sat 14 Nov 2026, before any E193 datum): the device-command preflight, Q136(w)'s checker
# tools/claims-v3/dmcmd_audit.py on every file E193's session runs, builds or reads, with NO --allow (no WRITE of any kind: not even the
# statistics reset) and no exception: the session's wrapper; the proposal's runner as committed (its one sampler call runs the program
# the wrapper names with --sampler: E128's guard), host, argument header and kernel; the kit's checker, build and harness; and E128's
# guard (the only way the session calls the telemetry reader: `config`, and `sample` with --seconds and --every-ms only, refusing
# --reset-ms and every other word before the device opens). The holder check (et-who --check) and the card lock send no device command.
# Run from the repository's top, or on the box from E193's root (<tree>/build/claims-v3/aifoundry3/e193, the same layout). Exit 0 = GO;
# 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e193/preflight_e193.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
exec python3 -B tools/claims-v3/dmcmd_audit.py "$@" \
  tools/claims-v3/e193/session_e193.sh tools/claims-v3/e193/proposal/src/run_x04.py tools/claims-v3/e193/check_e193.py \
  tools/claims-v3/e193/build_e193.sh tools/claims-v3/e193/harness_e193.py tools/claims-v3/e128/ettelem_guard.sh \
  tools/claims-v3/e193/proposal/src/host/main.cpp tools/claims-v3/e193/proposal/src/x04_args.h \
  tools/claims-v3/e193/proposal/src/kernel/x04clock.c
