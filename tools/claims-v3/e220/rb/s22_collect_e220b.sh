#!/usr/bin/env bash
# E220 (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum; E209's kit note 1's rb/s22_collect_e209_n1.sh form, THE MASK registered
# here before any E220 datum): runbook step 11, THE COLLECTION. Inside THE ONE-LAB RULE's collect span (onelab collect right before this step;
# uncollect right after the data commit's push, and on every stop path): collect_e220b.py (THE BOX-TREE GATE, COPY-BACK EXACT, E208's data
# checker unchanged, THE MASK of fwgate's ledger line, THE SCRUB, the data directory in LAB with its README and SHA256SUMS), then THE QUIET
# DESK FLAG lowered (the copy-back is done: nothing more reads the box root's session). Nothing is committed here: step 12 is the data commit
# (commit_lab.sh with LAB_QUIET_HOLD_OWNER, THE QUIET HOLD standing). The collect span it requires outside a desk test is RB_ONELAB_LANE's
# (default RB_LANE), so a lane that re-runs step 11 under its own name may hold the span while THE QUIET DESK FLAG stays the card lane's.
#   RB_OUT=... E220B_ROOT=... RB_QUIET=... RB_LANE=... RB_W=... [RB_ONELAB_LANE=...] [RB_COPY_NAME=copy] \
#     bash tools/claims-v3/e220/rb/s22_collect_e220b.sh
# Exits: 0 the data directory written and the flag lowered (its path last); 10 refused (the gate: the session not ended, a desk test's
# session, the data directory there already, the copy-back's name taken, no collect span); 14 the copy-back not exact (run it again under a
# new RB_COPY_NAME only after reading why); 16 the scrub found a private string, or THE MASK met two ledger lines in one record (nothing
# written in LAB; the flag stays up until rb/end_e220b.sh lowers it: tell the orchestrator).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e220b.sh"
rb_init s22_collect
e220b_quiet_ours
rb_root
[ -f "$RB_OUT/e220b-session.txt" ] || rb_die 10 "no session started in this RB_OUT (step 9)"
# shellcheck disable=SC1091
. "$RB_OUT/e220b-session.txt"
OL=${RB_ONELAB_LANE:-$RB_LANE}
if [ "${RB_DESKTEST:-}" = 1 ]; then
  echo "THE ONE-LAB RULE: the collect span is not required in a desk test"
else
  rb_need RB_W
  [ -f "$RB_W/onelab.sh" ] || rb_die 10 "RB_W ($RB_W) holds no onelab.sh"
  bash "$RB_W/onelab.sh" show 2>/dev/null | grep -qx "  collect-$OL" || rb_die 10 "THE ONE-LAB RULE: $OL is not in its collect span (bash \$W/onelab.sh collect $OL right before step 11)"
  echo "THE ONE-LAB RULE: collect-$OL held"
fi
OUT=$(nice -n 10 timeout 900 "$PY" -I -B "$RB_REPO/$E220B_REL/collect_e220b.py" --root "$E220B_ROOT" --sid "$SID" --rb-out "$RB_OUT" \
  --lab "${RB_DATA_LAB:-$RB_REPO}" --copy-name "${RB_COPY_NAME:-copy}" ${RB_DESKTEST:+--desktest} 2>&1); rc=$?
echo "$OUT" | tee "$RB_OUT/collect.txt"
case "$rc" in
  0) ;;
  10) rb_die 10 "$(echo "$OUT" | tail -n 1)" ;;
  16) rb_die 16 "$(echo "$OUT" | tail -n 1)" ;;
  *) rb_die 14 "$(echo "$OUT" | tail -n 1)" ;;
esac
DD=$(echo "$OUT" | grep '^DATA DIR ' | awk '{print $3}')
echo "DD=$DD" > "$RB_OUT/e220b-datadir.txt"
bash "$RB_E220B_DIR/quiet_e220b.sh" lower "$RB_LANE" | tail -n 1
rb_ok "DATA DIR $DD written; THE QUIET DESK FLAG lowered after the copy-back; next: the data commit (step 12)"
