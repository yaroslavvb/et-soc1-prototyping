#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum): the device-command preflight, the lab's checker v2
# (tools/claims-v3/dmcmd_audit_v2.py with its table dmcmd_table_v2.json, Q188; E206.md 6 names it) on every file E206's session runs, builds
# or sends a command from, with NO --allow (no WRITE of any kind: not even the statistics reset) and no exception: the runner and its two
# modules (e206_ident.py's identity reads are et-who, which only stats the nodes, and /proc of our own processes: it opens no node), the
# session's wrapper, the build, the harness check, E206's guard (the only way the runner reads a card: `config`, and `sample` with
# --seconds and --every-ms only, refusing --reset-ms before the device opens) and the host's source (it opens the ops node only). The
# runner runs it on the box before its first device access and opens nothing unless it reads GO. Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e206/preflight_e206.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
exec python3 tools/claims-v3/dmcmd_audit_v2.py "$@" \
  tools/claims-v3/e206/run_e206.py tools/claims-v3/e206/e206_common.py tools/claims-v3/e206/e206_ident.py \
  tools/claims-v3/e206/session_e206.sh tools/claims-v3/e206/build_e206.sh tools/claims-v3/e206/check_e206.py \
  tools/claims-v3/e206/ettelem_guard_e206.sh tools/claims-v3/e136/rgm136/host/main.cpp
