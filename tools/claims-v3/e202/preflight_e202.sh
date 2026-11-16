#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): the device-command preflight, the lab's checker v2
# (tools/claims-v3/dmcmd_audit_v2.py with its table dmcmd_table_v2.json, Q188; E202.md 9 names it) on every file E202's session runs,
# builds or sends a command from, with NO --allow (no WRITE of any kind: not even the statistics reset) and no exception: the runner and
# its common module, the session's wrapper, the build, the files step and the host check, the harness check, E128's guard (the only way
# the runner reads the card: `config`, and `sample` with --seconds and --every-ms only, refusing --reset-ms before the device opens),
# and the program's host and kernel sources (the host opens the ops node only). Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e202/preflight_e202.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
exec python3 tools/claims-v3/dmcmd_audit_v2.py "$@" \
  tools/claims-v3/e202/run_e202.py tools/claims-v3/e202/e202_common.py tools/claims-v3/e202/session_e202.sh \
  tools/claims-v3/e202/build_e202.sh tools/claims-v3/e202/files_e202.sh tools/claims-v3/e202/hostcheck_e202.py \
  tools/claims-v3/e202/check_e202.py tools/claims-v3/e128/ettelem_guard.sh \
  workloads/mnistmlp/host/main.cpp workloads/mnistmlp/kernel/mnistmlp.c
