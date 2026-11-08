#!/usr/bin/env bash
# E184 (Q154), kit note 2 (KIT.md.dated-note-2.md section 3): audit_rb_e184.sh (v1, which stays as committed, with its committed log) on the
# runbook as kit note 2 runs it, Q136(w)'s dmcmd_audit, no WRITE allowed: v1's files, kit note 2's runbook steps (s03 v2, s09 v2, s22 v2, the
# dry listing v2 and the desk test v2), and the verifier's nit (c): tools/claims-v3/e172/box/look_e172.sh, the script k6's look
# (s05_look_k6.sh) sends to aifoundry1, which v1 left out. v1's one reviewed exception stands: E184's guard forwards a --reset-ms of 1000
# (its line 30) when a caller passes one; the runbook never does (its calls of that guard are s09_reads_e184.sh's and s09_reads_e184_v2.sh's
# `config`), and the reset's one caller, block_e184b_v2.sh in pass 18441, is audited by preflight_e184_v2.sh B with the statistics reset alone
# allowed.
#   bash tools/claims-v3/e184/audit_rb_e184_v2.sh        # exit 0 = GO
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=tools/claims-v3/e184
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "$D/ettelem_guard_e184.sh:30:STATS_RESET=the runbook calls E184's guard with config only (s09_reads_e184.sh, s09_reads_e184_v2.sh); the reset's one caller is block_e184b_v2.sh, pass 18441, audited by preflight_e184_v2.sh B" \
  $D/rb/rb_e184.sh $D/rb/s02_window_e184.sh $D/rb/s03_desk_e184.sh $D/rb/s07_sync_e184.sh $D/rb/s08_build_e184.sh $D/rb/s09_reads_e184.sh \
  $D/rb/s10_dry_e184.sh $D/rb/s11_session_e184.sh $D/rb/s20_wait_e184.sh $D/rb/s22_collect_e184.sh $D/rb/list_steps_e184.sh \
  $D/rb/selftest_rb_e184.sh $D/rb/s03_desk_e184_v2.sh $D/rb/s09_reads_e184_v2.sh $D/rb/s22_collect_e184_v2.sh $D/rb/list_steps_e184_v2.sh \
  $D/rb/selftest_rb_e184_v2.sh tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh \
  tools/claims-v3/q141k-runbook/k6/rb_common.sh tools/claims-v3/e172/box/look_e172.sh tools/claims-v3/e180/sync_paths_e180.py \
  tools/claims-v3/e128/ettelem_guard.sh $D/ettelem_guard_e184.sh
