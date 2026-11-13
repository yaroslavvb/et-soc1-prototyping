#!/usr/bin/env bash
# E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): the device-command preflight, v3.
# It is preflight_e183_v2.sh (24b9b99e, which stays as committed) with note 6's box files in the audited set: session_e183_v3.sh,
# queue_e183_v3.sh, block_e183_v3.sh and harness_e183_v3.py, beside v2's files (v1's and v2's session, queue and block stay in the set: the
# same audit reads them as before). E180's one reviewed exception is v1's, unchanged: block v3's only start_sampler call is v2's, line for
# line. Run by session_e183_v3.sh.
# v2's words follow:
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): the device-command preflight, v2. It is
# preflight_e183.sh (cc597bf2, which stays as committed) with note 4's box files in the audited set: session_e183_v2.sh, queue_e183_v2.sh,
# block_e183_v2.sh, build_host_e183_v2.sh, train_check_e183.sh and harness_e183_v2.py, beside v1's files (v1's session, queue, block and
# build stay in the set: the same audit reads them as before). E180's one reviewed exception is v1's, unchanged. Run by session_e183_v2.sh
# and rb/s08_a3_build_e183_v2.sh.
# v1's words follow:
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
  tools/claims-v3/e183/session_e183_v2.sh tools/claims-v3/e183/queue_e183_v2.sh tools/claims-v3/e183/block_e183_v2.sh \
  tools/claims-v3/e183/build_host_e183_v2.sh tools/claims-v3/e183/train_check_e183.sh tools/claims-v3/e183/harness_e183_v2.py \
  tools/claims-v3/e183/session_e183_v3.sh tools/claims-v3/e183/queue_e183_v3.sh tools/claims-v3/e183/block_e183_v3.sh \
  tools/claims-v3/e183/harness_e183_v3.py \
  tools/claims-v3/e183/run_e183.py tools/claims-v3/e183/e183_common.py tools/claims-v3/e183/check_e183.py \
  tools/claims-v3/e183/build_host_e183.sh tools/claims-v3/e183/check_inputs_e183.py tools/claims-v3/e183/patch_host_e183.py \
  tools/claims-v3/e180/others_d1_e180.sh tools/claims-v3/e180/gen_acc_e180.py \
  tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh workloads/enercat/analyze_catalogue.py workloads/enercat/host/main.cpp \
  ${PATCHED[@]+"${PATCHED[@]}"}
