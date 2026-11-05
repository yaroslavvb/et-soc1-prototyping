#!/usr/bin/env bash
# E174 (Q142(kg)): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E174's session runs or imports,
# with no WRITE allowed (no --allow) and one reviewed exception, E170's (and E165's): run_hpl.py:622's residency query, which run_e119.py rewrites
# to raw states 1 2 3 and which E170's guard (ettelem_guard_e170.sh, unchanged) refuses with exit 97 before the reader starts, so it is never sent
# (E170: residency_rc 97 in all 135 runs). The files are named one by one: E174's runner, queue, common module, harness check and box scripts;
# E170's common module and guard; E173's common module; the watcher fix (no send site); E84's card-0 runner and the chain under it (E80's
# run_kspeed.py, E101's run_e101s.py and e101_common.py, E105's run_e105.py, E119's run_e119.py, E111's idle-login rule, E64's run_hpl.py);
# E165's common module; Q139(k)'s C-logging wrapper, host patch and build script; the workload's host and kernel sources; M9's aifoundry2
# predictor. On the box it also scans the patched host source the C-logging build compiled (build/ccheck/src/host/main.cpp) when it exists.
# Exit 0 = GO; 3 = NO-GO (no device opens); 2 = a usage error.
#
#   bash tools/claims-v3/e174/preflight_e174.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
EXTRA=()
[ -f build/ccheck/src/host/main.cpp ] && EXTRA=(build/ccheck/src/host/main.cpp)
EXC=(--except "tools/claims-v3/hpl/run_hpl.py:622:SP_ERROR_LOG=run_e119.py patch_residency rewrites this command to residency 1 2 3, and E170's ettelem_guard_e170.sh refuses residency (exit 97) before build/ettelem-e84/ettelem starts: never sent")
[ "${E174_NO_EXCEPT:-}" = 1 ] && EXC=()
python3 -B tools/claims-v3/dmcmd_audit.py "$@" ${EXC[@]+"${EXC[@]}"} \
  tools/claims-v3/e174/run_e174.py tools/claims-v3/e174/queue_e174.py tools/claims-v3/e174/e174_common.py tools/claims-v3/e174/check_e174.py \
  tools/claims-v3/e174/box/look_e174.sh tools/claims-v3/e174/box/check_box_e174.sh tools/claims-v3/e174/box/launch_e174.sh tools/claims-v3/e174/box/wait_e174.sh \
  tools/claims-v3/e170/e170_common.py tools/claims-v3/e170/ettelem_guard_e170.sh tools/claims-v3/e173/e173_common.py tools/claims-v3/hpl/watcher_q142s.py \
  tools/claims-v3/kspeed/e84/run_e84.py tools/claims-v3/kspeed/run_kspeed.py tools/claims-v3/kspeed/e101/run_e101s.py tools/claims-v3/kinds/e101_common.py \
  tools/claims-v3/kspeed/e105/run_e105.py tools/claims-v3/e119/run_e119.py tools/claims-v3/e111/idle_logins_e111.py tools/claims-v3/hpl/run_hpl.py \
  tools/claims-v3/e165/e165_common.py tools/claims-v3/ccheck/sparsity_ccheck.sh tools/claims-v3/ccheck/patch_host_ccheck.py \
  tools/claims-v3/ccheck/build_host_ccheck.sh workloads/sparsity/host/main.cpp workloads/sparsity/kernel/sparsity.c \
  docs/reports/data/2026-11-04-q140l-a2-session-terms/predict_m9_a2.py ${EXTRA[@]+"${EXTRA[@]}"}
rc=$?
[ "$rc" -eq 0 ] && exit 0
[ "$rc" -eq 2 ] && exit 2
exit 3
