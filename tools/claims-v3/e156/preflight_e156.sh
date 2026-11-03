#!/usr/bin/env bash
# E156 (Q139): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E156's session runs or sources, with no
# WRITE allowed (no --allow) and one reviewed exception. Exit 0 = GO; 3 = NO-GO (session_e156.sh then opens no device); 2 = a usage error.
# A copy of tools/claims-v3/e155/preflight_e155.sh with the names, the files and the exception's line changed.
#
#   bash tools/claims-v3/e156/preflight_e156.sh            # the verdict and every finding
#   bash tools/claims-v3/e156/preflight_e156.sh --markdown # the README's "Device commands sent" section
#
# The exception: lib.sh's start_sampler forwards its extra arguments to `ettelem sample` (lib.sh:154), so the checker reads a possible --reset-ms there
# (the statistics reset, STATS_RESET). E156 never passes one: block_e156.sh's only start_sampler call passes the output file and the duration and
# nothing else, and every telemetry call goes through tools/claims-v3/e128/ettelem_guard.sh, which refuses --reset-ms (and any word but `config` and
# `sample --seconds --every-ms`) before the device opens. E127, E128, E130, E148 and E155 recorded the same line the same way.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E156 never forwards a --reset-ms: block_e156.sh's one start_sampler call passes the file and the duration only, and ettelem_guard.sh refuses --reset-ms before the device opens" \
  tools/claims-v3/e156/ tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/runitems.py tools/claims-v3/text_hash.sh \
  tools/claims-v3/e110/smoke_gate_e110.py tools/claims-v3/dm/build_host.sh tools/claims-v3/dm/make_host_src.py \
  workloads/enercat/host/main.cpp workloads/sparsity/host/main.cpp
