#!/usr/bin/env bash
# E173 (Q142(kg)): the device-command preflight, Q136(w)'s checker tools/claims-v3/dmcmd_audit.py on every file E173's session runs or imports,
# with no WRITE allowed (no --allow) and one reviewed exception, E165's and E160's: run_hpl.py:622's residency query, which run_e119.py rewrites to
# raw states 1 2 3 and which this ettelem build (build/ettelem-hpl) refuses at its argument check before it opens the device, so it is never sent
# (E160: 160 attempts, every one rc 2, no record; E165 the same). The files are named one by one: E173's runner, queue, common module and harness
# check; the watcher fix (no send site); E119's chain (run_e119.py, E105's run_e105.py, E101's run_e101s.py and e101_common.py, E80's
# run_kspeed.py, E111's idle-login rule, E64's run_hpl.py); E165's common module; Q139(k)'s C-logging wrapper, host patch and build script; the
# workload's host and kernel sources; M9's aifoundry2 predictor. On the box it also scans the patched host source the C-logging build compiled
# (build/ccheck/src/host/main.cpp) when it exists. The desk files (the scorer, the predictions and protocol writers, the collector) never run on the
# box and are scanned at the desk (the kit's README). Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#
#   bash tools/claims-v3/e173/preflight_e173.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
EXTRA=()
[ -f build/ccheck/src/host/main.cpp ] && EXTRA=(build/ccheck/src/host/main.cpp)
EXC=(--except "tools/claims-v3/hpl/run_hpl.py:622:SP_ERROR_LOG=run_e119.py patch_residency rewrites this command to residency 1 2 3, which build/ettelem-hpl/ettelem refuses at its argument check (rc 2) before it opens the device: never sent (E160, E165)")
[ "${E173_NO_EXCEPT:-}" = 1 ] && EXC=()
python3 -B tools/claims-v3/dmcmd_audit.py "$@" ${EXC[@]+"${EXC[@]}"} \
  tools/claims-v3/e173/run_e173.py tools/claims-v3/e173/queue_e173.py tools/claims-v3/e173/e173_common.py tools/claims-v3/e173/check_e173.py \
  tools/claims-v3/hpl/watcher_q142s.py tools/claims-v3/e119/run_e119.py tools/claims-v3/kspeed/e105/run_e105.py tools/claims-v3/kspeed/e101/run_e101s.py \
  tools/claims-v3/kinds/e101_common.py tools/claims-v3/kspeed/run_kspeed.py tools/claims-v3/hpl/run_hpl.py tools/claims-v3/e111/idle_logins_e111.py \
  tools/claims-v3/e165/e165_common.py tools/claims-v3/ccheck/sparsity_ccheck.sh tools/claims-v3/ccheck/patch_host_ccheck.py \
  tools/claims-v3/ccheck/build_host_ccheck.sh workloads/sparsity/host/main.cpp workloads/sparsity/kernel/sparsity.c \
  docs/reports/data/2026-11-04-q140l-a2-session-terms/predict_m9_a2.py ${EXTRA[@]+"${EXTRA[@]}"}
rc=$?
[ "$rc" -eq 0 ] && exit 0
[ "$rc" -eq 2 ] && exit 2
exit 3
