#!/usr/bin/env bash
# E220 (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum; E209's kit's rb/s07_sync_e209.sh form): runbook step 5, THE SYNC: every file of the box root from this lab
# clone at HEAD (step 2 checked it) at its sha256 (make_box_e220b.py sync <root>: E208's kit unchanged, E220's box files, inputs and list, E211's
# rgm211 sources, fwgate and its records); on a new box root it runs BEFORE step 4 (E209's kit note 1, section 4), read back after the copy. Refused (10) unless THE QUIET DESK FLAG is up and the card lane's; refused
# by the sync itself (3 -> 10) while a session, a build or a dry pass of the kit runs in the box root.
#   RB_OUT=... E220B_ROOT=... RB_QUIET=... RB_LANE=... bash tools/claims-v3/e220/rb/s07_sync_e220b.sh
# Exits: 0 SYNCED; 10 refused; 14 a file not at its sha256 after the copy (run it again; never by hand).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e220b.sh"
rb_init s07_sync
e220b_window
e220b_quiet_ours
rb_root
OUT=$(timeout 300 "$PY" -I -B "$RB_REPO/$E220B_REL/make_box_e220b.py" sync "$E220B_ROOT" 2>&1); rc=$?
echo "$OUT" | tee "$RB_OUT/sync.txt"
case "$rc" in 0) rb_ok "$(echo "$OUT" | tail -n 1 | cut -c1-160)" ;; 3) rb_die 10 "the sync refused" ;; *) rb_die 14 "the sync ended rc $rc" ;; esac
