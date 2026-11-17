#!/usr/bin/env bash
# E211 (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum): the device-command preflight, the lab's checker v2
# (tools/claims-v3/dmcmd_audit_v2.py with its table dmcmd_table_v2.json, Q188; E211.md 8 names it) on every file E211's session runs, builds or
# sends a command from, with NO --allow (no WRITE of any kind: not even the statistics reset) and no exception: the runner and its two modules
# (e211_ident.py's identity reads are et-who, which only stats the nodes, and /proc of our own processes: it opens no node), the session's
# wrapper, the build, the harness check, E211's guard (the only way the runner reads a card: `config`, and `sample` with --seconds and
# --every-ms only, refusing --reset-ms before the device opens), the registration's identity gate (ident_e211.py: it reads ELF files only) and
# both hosts' sources (rgm136's, E136's, and rgm211's: each opens the ops node only). E206's preflight's form.
# The runner runs it on the box before its first device access and opens nothing unless it reads GO. Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e211/preflight_e211.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
exec python3 tools/claims-v3/dmcmd_audit_v2.py "$@" \
  tools/claims-v3/e211/run_e211.py tools/claims-v3/e211/e211_common.py tools/claims-v3/e211/e211_ident.py \
  tools/claims-v3/e211/session_e211.sh tools/claims-v3/e211/build_e211.sh tools/claims-v3/e211/check_e211.py \
  tools/claims-v3/e211/ettelem_guard_e211.sh tools/claims-v3/e211/ident_e211.py tools/claims-v3/e136/rgm136/host/main.cpp \
  tools/claims-v3/e211/rgm211/host/main.cpp
