#!/usr/bin/env bash
# E209's kit note 1 (Q212, lane note-e209, Tue 17 Nov 2026 PST, after E209's session and before its data commit): runbook step 11 again,
# THE COLLECTION with THE MASK of KIT.md.dated-note-1.md. It is rb/s22_collect_e209.sh (unchanged beside it, sha256 f047b758...) but for
# three things: it runs collect_e209_n1.py (THE MASK, then THE SCRUB as before; the copy-back under RB_OUT/<RB_COPY_NAME>/, default copy-n1,
# so card-e209's first copy-back RB_OUT/copy/ stays as it is) in place of collect_e209.py; it writes the collector's words to
# RB_OUT/collect-n1.txt (card-e209's RB_OUT/collect.txt stays); and THE ONE-LAB RULE's collect span it requires outside a desk test is
# RB_ONELAB_LANE's (default RB_LANE), so that a lane that re-runs step 11 under its own name holds the span under that name while THE QUIET
# DESK FLAG stays the card lane's (RB_LANE). Inside THE ONE-LAB RULE's collect span (onelab collect right before this step; uncollect right
# after the data commit's push, and on every stop path): collect_e209_n1.py (THE BOX-TREE GATE, COPY-BACK EXACT, E208's data checker
# unchanged, THE MASK, THE SCRUB, the data directory in LAB with its README and SHA256SUMS), then THE QUIET DESK FLAG lowered (the copy-back
# is done: nothing more reads the box root's session). Nothing is committed here: step 12 is the data commit (commit_lab.sh with
# LAB_QUIET_HOLD_OWNER, THE QUIET HOLD standing).
#   RB_OUT=... E209_ROOT=... RB_QUIET=... RB_LANE=... RB_W=... [RB_ONELAB_LANE=...] [RB_COPY_NAME=copy-n1] \
#     bash tools/claims-v3/e209/rb/s22_collect_e209_n1.sh
# Exits: 0 the data directory written and the flag lowered (its path last); 10 refused (the gate: the session not ended, a desk test's
# session, the data directory there already, the copy-back's name taken); 14 the copy-back not exact (run it again under a new
# RB_COPY_NAME only after reading why); 16 the scrub found a private string, or THE MASK met two ledger lines in one record (nothing written
# in LAB; the flag stays up until rb/end_e209.sh lowers it: tell the orchestrator).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e209.sh"
rb_init s22_collect_n1
e209_quiet_ours
rb_root
[ -f "$RB_OUT/e209-session.txt" ] || rb_die 10 "no session started in this RB_OUT (step 9)"
# shellcheck disable=SC1091
. "$RB_OUT/e209-session.txt"
OL=${RB_ONELAB_LANE:-$RB_LANE}
if [ "${RB_DESKTEST:-}" = 1 ]; then
  echo "THE ONE-LAB RULE: the collect span is not required in a desk test"
else
  rb_need RB_W
  [ -f "$RB_W/onelab.sh" ] || rb_die 10 "RB_W ($RB_W) holds no onelab.sh"
  bash "$RB_W/onelab.sh" show 2>/dev/null | grep -qx "  collect-$OL" || rb_die 10 "THE ONE-LAB RULE: $OL is not in its collect span (bash \$W/onelab.sh collect $OL right before step 11)"
  echo "THE ONE-LAB RULE: collect-$OL held"
fi
OUT=$(nice -n 10 timeout 900 "$PY" -I -B "$RB_REPO/$E209_REL/collect_e209_n1.py" --root "$E209_ROOT" --sid "$SID" --rb-out "$RB_OUT" \
  --lab "${RB_DATA_LAB:-$RB_REPO}" --copy-name "${RB_COPY_NAME:-copy-n1}" ${RB_DESKTEST:+--desktest} 2>&1); rc=$?
echo "$OUT" | tee "$RB_OUT/collect-n1.txt"
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
