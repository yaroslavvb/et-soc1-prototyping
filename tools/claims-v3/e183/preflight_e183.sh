#!/usr/bin/env bash
# E183 (Q155, the kit): the device-command preflight. tools/claims-v3/dmcmd_audit.py (Q136(w), unchanged) on every file E183's box session
# runs, sources or builds the host from (and, on the box after the build, the train host's patched source), before any device opens: GO,
# or the session stops (session_e183.sh). E180's preflight v2
# (preflight_e180_v2.sh) with E183's files, and E180's one reviewed exception, unchanged: lib.sh line 154 forwards its "$@" into
# `ettelem sample`, which could carry a --reset-ms, but block_e183.sh's only start_sampler call passes the file and the duration alone.
#   bash tools/claims-v3/e183/preflight_e183.sh [--json | --markdown]
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
PATCHED=()      # on the box after step 6's build: the train host's patched source, read too (E182's preflight reads its patched host)
[ -f build/enercat-e183-src/host/main.cpp ] && PATCHED=(build/enercat-e183-src/host/main.cpp)
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E183 never forwards a --reset-ms: block_e183.sh's start_sampler call passes the file and the duration only" \
  tools/claims-v3/e183/session_e183.sh tools/claims-v3/e183/queue_e183.sh tools/claims-v3/e183/block_e183.sh \
  tools/claims-v3/e183/run_e183.py tools/claims-v3/e183/e183_common.py tools/claims-v3/e183/check_e183.py \
  tools/claims-v3/e183/build_host_e183.sh tools/claims-v3/e183/check_inputs_e183.py tools/claims-v3/e183/patch_host_e183.py \
  tools/claims-v3/e180/others_d1_e180.sh tools/claims-v3/e180/gen_acc_e180.py \
  tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh workloads/enercat/analyze_catalogue.py workloads/enercat/host/main.cpp \
  ${PATCHED[@]+"${PATCHED[@]}"}
