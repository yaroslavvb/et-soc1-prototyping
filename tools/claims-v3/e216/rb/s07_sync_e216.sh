#!/usr/bin/env bash
# E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum; E209's kit's rb/s07_sync_e209.sh form): runbook step 5, THE SYNC: every file of the box root from this lab
# clone at HEAD (step 2 checked it) at its sha256 (make_box_e216.py sync <root>: E208's kit unchanged, E216's box files, inputs and list, E211's
# rgm211 sources, fwgate and its records); on a new box root it runs BEFORE step 4 (E209's kit note 1, section 4), read back after the copy. Refused (10) unless THE QUIET DESK FLAG is up and the card lane's; refused
# by the sync itself (3 -> 10) while a session, a build or a dry pass of the kit runs in the box root.
#   RB_OUT=... E216_ROOT=... RB_QUIET=... RB_LANE=... bash tools/claims-v3/e216/rb/s07_sync_e216.sh
# Exits: 0 SYNCED; 10 refused; 14 a file not at its sha256 after the copy (run it again; never by hand).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e216.sh"
rb_init s07_sync
e216_window
e216_quiet_ours
rb_root
OUT=$(timeout 300 "$PY" -I -B "$RB_REPO/$E216_REL/make_box_e216.py" sync "$E216_ROOT" 2>&1); rc=$?
echo "$OUT" | tee "$RB_OUT/sync.txt"
case "$rc" in 0) rb_ok "$(echo "$OUT" | tail -n 1 | cut -c1-160)" ;; 3) rb_die 10 "the sync refused" ;; *) rb_die 14 "the sync ended rc $rc" ;; esac
