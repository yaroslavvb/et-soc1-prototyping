#!/usr/bin/env bash
# E184 (Q153), kit note 1 (KIT.md.dated-note-1.md section 3): the device-command audit of the runbook, Q136(w)'s dmcmd_audit, no WRITE
# allowed: every rb/ step, the k6 steps it calls (s05_look_k6.sh, s09_a3_reads_k6.sh) and their common library, E180's sync_paths_e180.py, and
# the two telemetry guards step 7's config reads go through (E128's for arm S, E184's for arm B), scanned so their sends are listed. One
# reviewed exception: E184's guard forwards a --reset-ms of 1000 (its line 30) when a caller passes one; the runbook never does (its only
# call of that guard is s09_reads_e184.sh's `config`), and the reset's one caller, block_e184b_v2.sh in pass 18441, is audited by
# preflight_e184_v2.sh B with the statistics reset alone allowed.
#   bash tools/claims-v3/e184/audit_rb_e184.sh        # exit 0 = GO
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=tools/claims-v3/e184
exec python3 tools/claims-v3/dmcmd_audit.py "$@" \
  --except "$D/ettelem_guard_e184.sh:30:STATS_RESET=the runbook calls E184's guard with config only (s09_reads_e184.sh); the reset's one caller is block_e184b_v2.sh, pass 18441, audited by preflight_e184_v2.sh B" \
  $D/rb/rb_e184.sh $D/rb/s02_window_e184.sh $D/rb/s03_desk_e184.sh $D/rb/s07_sync_e184.sh $D/rb/s08_build_e184.sh $D/rb/s09_reads_e184.sh \
  $D/rb/s10_dry_e184.sh $D/rb/s11_session_e184.sh $D/rb/s20_wait_e184.sh $D/rb/s22_collect_e184.sh $D/rb/list_steps_e184.sh \
  $D/rb/selftest_rb_e184.sh tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh \
  tools/claims-v3/q141k-runbook/k6/rb_common.sh tools/claims-v3/e180/sync_paths_e180.py \
  tools/claims-v3/e128/ettelem_guard.sh $D/ettelem_guard_e184.sh
