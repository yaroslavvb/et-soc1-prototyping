#!/usr/bin/env bash
# E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum; E209's preflight_e209.sh form): the device-command preflight, the lab's
# checker v2 (tools/claims-v3/dmcmd_audit_v2.py with its table dmcmd_table_v2.json, Q188) on every file E216's day runs, builds or sends a
# command from, with NO --allow (no WRITE of any kind: not even the statistics reset) and no exception: E208's registered runner and its two
# modules, E208's guard (the only way the runner reads the card: `config`, and `sample` with --seconds and --every-ms only), its status, stop,
# build and preflight scripts, rgm136's host source (it opens the ops node only); E216's box files (the runner run_e216.py, rgm211's host's
# double, the identity gate, the second build, the start, the session wrapper, the dry pass) and rgm211's host source (E211's: the ops node
# only); the collector; every runbook step but step 2 itself (which calls this file); the never-run tool; and the reboot gate (fwgate.py: its one
# firmware-revisions read, a READ by the owner's rulings of 15:07:01 and 15:09:49 PST Sun 15 Nov 2026). E208's runner also runs E208's own
# preflight (src/preflight_mms.sh --audit-only: the checker v1 and its table, unchanged) in its box check before its first device access and
# opens nothing unless it reads GO. Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e216/preflight_e216.sh            # the verdict and every finding
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
S=tools/claims-v3/e208/proposal/src
E=tools/claims-v3/e216
exec /usr/bin/python3 -I -B tools/claims-v3/dmcmd_audit_v2.py "$@" \
  $S/run_mms.py $S/mms_common.py $S/mms_ident.py $S/guard_ettelem.sh $S/status_mms.sh $S/stop_mms.sh $S/build_mms.sh \
  $S/preflight_mms.sh $S/rgm136/host/main.cpp tools/claims-v3/e211/rgm211/host/main.cpp \
  $E/box/run_e216.py $E/box/fake_card_e216.py $E/box/ident_e216.py $E/box/build_e216.sh $E/box/start_e216.sh $E/box/session_e216.sh \
  $E/box/dry_e216.sh $E/collect_e216.py $E/make_box_e216.py \
  $E/rb/rb_e216.sh $E/rb/s00_sealed_e216.sh $E/rb/s02_window_e216.sh $E/rb/quiet_e216.sh $E/rb/s05_look_e216.sh $E/rb/s07_sync_e216.sh \
  $E/rb/s08_build_e216.sh $E/rb/s08_builds_e216.sh $E/rb/s10_dry_e216.sh $E/rb/s06n_neverrun_e216.sh $E/desk/neverrun_card_e216.py \
  $E/rb/s09_reads_e216.sh $E/rb/rest_rule_e216.py $E/rb/s11_session_e216.sh $E/rb/s20_wait_e216.sh $E/rb/s22_collect_e216.sh \
  $E/rb/s24_score_e216.sh $E/rb/end_e216.sh $E/rb/check_history_e216.py $E/rb/post_e216.py tools/claims-v3/fwgate/fwgate.py
