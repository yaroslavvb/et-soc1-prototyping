#!/usr/bin/env bash
# E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): the device-command preflight, the lab's checker v2
# (tools/claims-v3/dmcmd_audit_v2.py with its table dmcmd_table_v2.json, Q188; E207's preflight_e207.sh form) on every file E209's day runs,
# builds or sends a command from, with NO --allow (no WRITE of any kind: not even the statistics reset) and no exception: E208's registered
# runner and its two modules, E208's guard (the only way the runner reads the card: `config`, and `sample` with --seconds and --every-ms
# only), its status, stop, build and preflight scripts, the host's source (it opens the ops node only); E209's box root scripts (the start,
# the session wrapper, the dry pass), the collector, every runbook step but step 2 itself (which calls this file), and the reboot gate
# (fwgate.py: its one firmware-revisions read, a READ by the owner's rulings of 15:07:01 and 15:09:49 PST Sun 15 Nov 2026). E208's runner
# also runs E208's own preflight (src/preflight_mms.sh --audit-only: the checker v1 and its table, unchanged) in its box check before its
# first device access and opens nothing unless it reads GO. Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
# fix-e209 (Q202c, before any E209 datum) added rb/post_e209.py, step 13's label check and readings (it reads files and sends nothing).
#   bash tools/claims-v3/e209/preflight_e209.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
S=tools/claims-v3/e208/proposal/src
E=tools/claims-v3/e209
exec /usr/bin/python3 -I -B tools/claims-v3/dmcmd_audit_v2.py "$@" \
  $S/run_mms.py $S/mms_common.py $S/mms_ident.py $S/guard_ettelem.sh $S/status_mms.sh $S/stop_mms.sh $S/build_mms.sh \
  $S/preflight_mms.sh $S/rgm136/host/main.cpp \
  $E/box/start_e209.sh $E/box/session_e209.sh $E/box/dry_e209.sh $E/collect_e209.py \
  $E/rb/rb_e209.sh $E/rb/s02_window_e209.sh $E/rb/quiet_e209.sh $E/rb/s05_look_e209.sh $E/rb/s07_sync_e209.sh $E/rb/s08_build_e209.sh \
  $E/rb/s10_dry_e209.sh $E/rb/s06n_neverrun_e209.sh $E/rb/s09_reads_e209.sh $E/rb/rest_rule_e209.py $E/rb/s11_session_e209.sh \
  $E/rb/s20_wait_e209.sh $E/rb/s22_collect_e209.sh $E/rb/s24_score_e209.sh $E/rb/end_e209.sh $E/rb/check_history_e209.py \
  $E/rb/post_e209.py tools/claims-v3/fwgate/fwgate.py
