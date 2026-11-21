#!/usr/bin/env bash
# E224 (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum): the device-command preflight, the lab's checker v2
# (tools/claims-v3/dmcmd_audit_v2.py with its table dmcmd_table_v2.json, Q188; E224.md 6 names it: "dmcmd_audit_v2 GO with every send site READ
# before the first device access") on every file E224's session runs, builds or sends a command from, with NO --allow (no WRITE of any kind: not
# even the statistics reset) and no exception: the runner and its two modules (e224a_ident.py's identity reads are et-who, which only stats the
# nodes, and /proc of our own processes: it opens no node), the session's wrapper, the build, the harness check, E224's guard (the only way the
# runner reads a card: `config`, and `sample` with --seconds and --every-ms only, refusing --reset-ms before the device opens), the kit's identity
# gate (ident_e224a.py: it reads ELF files only) and both hosts' sources (rgm136's, E136's, and rgm211's, E211's: each opens the ops node only).
# E215 arm A's preflight's form (tools/claims-v3/e215/preflight_e215.sh, landed in 8bde0182), for E224's files.
# The runner runs it on the box before its first device access and opens nothing unless it reads GO. Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e224/preflight_e224a.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
exec python3 tools/claims-v3/dmcmd_audit_v2.py "$@" \
  tools/claims-v3/e224/run_e224a.py tools/claims-v3/e224/e224a_common.py tools/claims-v3/e224/e224a_ident.py \
  tools/claims-v3/e224/session_e224a.sh tools/claims-v3/e224/build_e224a.sh tools/claims-v3/e224/check_e224a.py \
  tools/claims-v3/e224/ettelem_guard_e224a.sh tools/claims-v3/e224/ident_e224a.py tools/claims-v3/e136/rgm136/host/main.cpp \
  tools/claims-v3/e211/rgm211/host/main.cpp
