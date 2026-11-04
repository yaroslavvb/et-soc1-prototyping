#!/usr/bin/env bash
# E170 (Q141(w)): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E170's session runs or imports, with
# no WRITE allowed (no --allow) and one reviewed exception, E165's: run_hpl.py:622's residency query, which run_e119.py rewrites to raw states 1 2 3
# and which E170's guard (ettelem_guard_e170.sh) then refuses with exit 97 before the reader starts, so it is never sent. The files are named one by
# one: E170's runner, queue, common module, guard, harness check and box scripts; E84's card-0 runner and the chain under it (E80's run_kspeed.py,
# E101's run_e101s.py and e101_common.py, E105's run_e105.py, E119's run_e119.py, E111's idle-login rule, E64's run_hpl.py); E165's common module and
# reduction; Q139(k)'s C-logging wrapper, host patch and build script; the workload's host and kernel sources; the frozen predictor. On the box it
# also scans the patched host source the C-logging build compiled (build/ccheck/src/host/main.cpp) when it exists. E170's desk files (the freeze,
# the protocols' writer, the scorer and its self-test, the collector) never run on the box and are scanned at the desk (the kit's README).
# Exit 0 = GO; 3 = NO-GO (queue_e170.py's launch then opens no device); 2 = a usage error.
#
#   bash tools/claims-v3/e170/preflight_e170.sh            # the verdict and every finding
#   bash tools/claims-v3/e170/preflight_e170.sh --markdown # a "Device commands sent" section
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
EXTRA=()
[ -f build/ccheck/src/host/main.cpp ] && EXTRA=(build/ccheck/src/host/main.cpp)
python3 -B tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/hpl/run_hpl.py:622:SP_ERROR_LOG=run_e119.py patch_residency rewrites this command to residency 1 2 3, and E170's ettelem_guard_e170.sh refuses residency (exit 97) before build/ettelem-e84/ettelem starts: never sent" \
  tools/claims-v3/e170/run_e170.py tools/claims-v3/e170/queue_e170.py tools/claims-v3/e170/e170_common.py tools/claims-v3/e170/ettelem_guard_e170.sh \
  tools/claims-v3/e170/check_e170.py tools/claims-v3/e170/box/look_e170.sh tools/claims-v3/e170/box/check_box_e170.sh \
  tools/claims-v3/e170/box/launch_e170.sh tools/claims-v3/e170/box/wait_e170.sh \
  tools/claims-v3/kspeed/e84/run_e84.py tools/claims-v3/kspeed/run_kspeed.py tools/claims-v3/kspeed/e101/run_e101s.py tools/claims-v3/kinds/e101_common.py \
  tools/claims-v3/kspeed/e105/run_e105.py tools/claims-v3/e119/run_e119.py tools/claims-v3/e111/idle_logins_e111.py tools/claims-v3/hpl/run_hpl.py \
  tools/claims-v3/e165/e165_common.py tools/claims-v3/ccheck/sparsity_ccheck.sh tools/claims-v3/ccheck/patch_host_ccheck.py \
  tools/claims-v3/ccheck/build_host_ccheck.sh workloads/sparsity/host/main.cpp workloads/sparsity/kernel/sparsity.c \
  docs/reports/data/2026-11-04-q140l-a2-session-terms/predict_m9_a2.py ${EXTRA[@]+"${EXTRA[@]}"}
rc=$?
[ "$rc" -eq 0 ] && exit 0
[ "$rc" -eq 2 ] && exit 2
exit 3
