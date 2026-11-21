#!/usr/bin/env bash
# E222 (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; E218's landed kit 5582edfc ported, the kit that ran E218 FULL on aifoundry3 card 0 at 03:11-03:56 PST that day): the device-command preflight, the lab's checker v2
# (tools/claims-v3/dmcmd_audit_v2.py with its table dmcmd_table_v2.json, Q188; E222.md 6 names it: "dmcmd_audit_v2 GO with every send site READ
# before the first device access") on every file E222's session runs, builds or sends a command from, with NO --allow (no WRITE of any kind: not
# even the statistics reset) and no exception: the runner and its two modules (e222_ident.py's identity reads are et-who, which only stats the
# nodes, and /proc of our own processes: it opens no node), the session's wrapper, the build, the harness check, E222's guard (the only way the
# runner reads a card: `config`, and `sample` with --seconds and --every-ms only, refusing --reset-ms before the device opens), the kit's identity
# gate (ident_e222.py: it reads ELF files only) and both hosts' sources (rgm136's, E136's, and rgm211's, E211's: each opens the ops node only).
# E215 arm A's preflight's form (tools/claims-v3/e215/preflight_e215.sh, landed in 8bde0182), for E222's files.
# The runner runs it on the box before its first device access and opens nothing unless it reads GO. Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e222/preflight_e222.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
exec python3 tools/claims-v3/dmcmd_audit_v2.py "$@" \
  tools/claims-v3/e222/run_e222.py tools/claims-v3/e222/e222_common.py tools/claims-v3/e222/e222_ident.py \
  tools/claims-v3/e222/session_e222.sh tools/claims-v3/e222/build_e222.sh tools/claims-v3/e222/check_e222.py \
  tools/claims-v3/e222/ettelem_guard_e222.sh tools/claims-v3/e222/ident_e222.py tools/claims-v3/e136/rgm136/host/main.cpp \
  tools/claims-v3/e211/rgm211/host/main.cpp
