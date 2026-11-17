#!/usr/bin/env bash
# E210 (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; ported from kit-e207's E207 kit, its local commit 4bd6e38c): the device-command preflight, the lab's checker v2
# (tools/claims-v3/dmcmd_audit_v2.py with its table dmcmd_table_v2.json, Q188; E210.md 6 names it) on every file E210's session runs, builds or
# sends a command from, with NO --allow (no WRITE of any kind: not even the statistics reset) and no exception: the runner and its two modules
# (e210_ident.py's identity reads are et-who, which only stats the nodes, and /proc of our own processes: it opens no node), the session's
# wrapper, the build, the harness check, E210's guard (the only way the runner reads a card: `config`, and `sample` with --seconds and
# --every-ms only, refusing --reset-ms before the device opens) and the host's source (it opens the ops node only). E206's preflight's form.
# The runner runs it on the box before its first device access and opens nothing unless it reads GO. Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e210/preflight_e210.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
exec python3 tools/claims-v3/dmcmd_audit_v2.py "$@" \
  tools/claims-v3/e210/run_e210.py tools/claims-v3/e210/e210_common.py tools/claims-v3/e210/e210_ident.py \
  tools/claims-v3/e210/session_e210.sh tools/claims-v3/e210/build_e210.sh tools/claims-v3/e210/check_e210.py \
  tools/claims-v3/e210/ettelem_guard_e210.sh tools/claims-v3/e136/rgm136/host/main.cpp
