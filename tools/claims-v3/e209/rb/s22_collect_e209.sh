#!/usr/bin/env bash
# E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum; fix-e209: the collect span): runbook step 11, THE COLLECTION, inside
# THE ONE-LAB RULE's collect span (onelab collect right before this step; uncollect right after the data commit's push, and on every stop path): collect_e209.py (THE
# BOX-TREE GATE, COPY-BACK EXACT, E208's data checker unchanged, THE SCRUB, the data directory in LAB with its README and SHA256SUMS),
# then THE QUIET DESK FLAG lowered (the copy-back is done: nothing more reads the box root's session). Nothing is committed here: step 12
# is the card lane's data commit (commit_lab.sh with LAB_QUIET_HOLD_OWNER, THE QUIET HOLD standing). Outside a desk test it refuses (10)
# unless RB_W's onelab.sh shows the lane's collect span (fix-e209, Q202c, verify-e209's finding 8; in a desk test the span is reported).
#   RB_OUT=... E209_ROOT=... RB_QUIET=... RB_LANE=... RB_W=... bash tools/claims-v3/e209/rb/s22_collect_e209.sh
# Exits: 0 the data directory written and the flag lowered (its path last); 10 refused (the gate: the session not ended, a desk test's
# session, the data directory there already); 14 the copy-back not exact (run it again into a new RB_OUT/copy name only after reading
# why); 16 the scrub found a private string (nothing written in LAB; the flag stays up until rb/end_e209.sh lowers it: tell the
# orchestrator).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e209.sh"
rb_init s22_collect
e209_quiet_ours
rb_root
[ -f "$RB_OUT/e209-session.txt" ] || rb_die 10 "no session started in this RB_OUT (step 9)"
# shellcheck disable=SC1091
. "$RB_OUT/e209-session.txt"
if [ "${RB_DESKTEST:-}" = 1 ]; then
  echo "THE ONE-LAB RULE: the collect span is not required in a desk test"
else
  rb_need RB_W
  [ -f "$RB_W/onelab.sh" ] || rb_die 10 "RB_W ($RB_W) holds no onelab.sh"
  bash "$RB_W/onelab.sh" show 2>/dev/null | grep -qx "  collect-$RB_LANE" || rb_die 10 "THE ONE-LAB RULE: $RB_LANE is not in its collect span (bash \$W/onelab.sh collect $RB_LANE right before step 11)"
  echo "THE ONE-LAB RULE: collect-$RB_LANE held"
fi
OUT=$(nice -n 10 timeout 900 "$PY" -I -B "$RB_REPO/$E209_REL/collect_e209.py" --root "$E209_ROOT" --sid "$SID" --rb-out "$RB_OUT" \
  --lab "${RB_DATA_LAB:-$RB_REPO}" ${RB_DESKTEST:+--desktest} 2>&1); rc=$?
echo "$OUT" | tee "$RB_OUT/collect.txt"
case "$rc" in
  0) ;;
  10) rb_die 10 "$(echo "$OUT" | tail -n 1)" ;;
  16) rb_die 16 "$(echo "$OUT" | tail -n 1)" ;;
  *) rb_die 14 "$(echo "$OUT" | tail -n 1)" ;;
esac
DD=$(echo "$OUT" | grep '^DATA DIR ' | awk '{print $3}')
echo "DD=$DD" > "$RB_OUT/e209-datadir.txt"
bash "$RB_E209_DIR/quiet_e209.sh" lower "$RB_LANE" | tail -n 1
rb_ok "DATA DIR $DD written; THE QUIET DESK FLAG lowered after the copy-back; next: the data commit (step 12)"
