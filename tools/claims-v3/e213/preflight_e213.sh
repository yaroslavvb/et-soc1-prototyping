#!/usr/bin/env bash
# E213 (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum): the device-command preflight, the lab's checker v2
# (tools/claims-v3/dmcmd_audit_v2.py with its table dmcmd_table_v2.json, Q188; E213.md 6 names it: "dmcmd_audit_v2 GO with every send site READ
# before the first device access") on every file E213's session runs, builds or sends a command from, with NO --allow (no WRITE of any kind: not
# even the statistics reset) and no exception: the runner and its two modules (e213_ident.py's identity reads are et-who, which only stats the
# nodes, and /proc of our own processes: it opens no node), the session's wrapper, the build, the harness check, E213's guard (the only way the
# runner reads a card: `config`, and `sample` with --seconds and --every-ms only, refusing --reset-ms before the device opens), the kit's identity
# gate (ident_e213.py: it reads ELF files only) and both hosts' sources (rgm136's, E136's, and rgm211's, E211's: each opens the ops node only).
# E211's preflight's form, for both arms (the same files on both boxes).
# The runner runs it on the box before its first device access and opens nothing unless it reads GO. Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e213/preflight_e213.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
exec python3 tools/claims-v3/dmcmd_audit_v2.py "$@" \
  tools/claims-v3/e213/run_e213.py tools/claims-v3/e213/e213_common.py tools/claims-v3/e213/e213_ident.py \
  tools/claims-v3/e213/session_e213.sh tools/claims-v3/e213/build_e213.sh tools/claims-v3/e213/check_e213.py \
  tools/claims-v3/e213/ettelem_guard_e213.sh tools/claims-v3/e213/ident_e213.py tools/claims-v3/e136/rgm136/host/main.cpp \
  tools/claims-v3/e211/rgm211/host/main.cpp
