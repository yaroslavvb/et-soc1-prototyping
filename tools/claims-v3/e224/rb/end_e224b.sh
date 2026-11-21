#!/usr/bin/env bash
# E224 (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum; E209's kit's rb/end_e209.sh form): E, THE END OF EVERY PATH (the card-lane brief's last row): whatever
# step stopped, undo what is ours and only what is ours, each by its own tool, and say what was done:
#   THE QUIET DESK FLAG lowered if it is the card lane's (rb/quiet_e224b.sh lower: never another's);
#   THE ONE-LAB RULE: onelab.sh undesk <lane> if a desk span of ours stands, onelab.sh uncollect <lane> if a collect span of ours stands;
#   THE QUIET HOLD: hold.sh remove <lane> if a line of ours is in it (after the data commit, or on a stop path before it);
#   the booking: book.sh release aifoundry2 <lane> if the booking is ours.
# A session still running in the box root is NOT stopped here (rb/end_e224b.sh never touches a session: step 10 waits for it, and a stop is
# E208's stop_mms.sh, which only touches STOP files); with one running it refuses (17) and does nothing, so nothing is released under it.
# A LEFTOVER keeps everything (E209's fix-e209, Q202c, verify-e209's finding 7): E208's runner releases the card's lock at
# its 600 s bound even while a device process of ours is still alive, so E also refuses (17), releasing nothing, while any process of ours
# whose comm is device-named is alive (THE P2 COUNT's pattern), or while a session of the box root records an unresolved leftover
# (queue.json "leftover" with "resolved" not true): the quiet desk flag, the hold line and the booking stay; the lane writes it up and
# escalates (the brief, section 3), and the orchestrator clears them once the leftover is resolved. Nothing is ever killed.
#   RB_W=<the round's folder with onelab.sh, hold.sh, book.sh> RB_QUIET=... RB_LANE=... [E224B_ROOT=...] bash tools/claims-v3/e224/rb/end_e224b.sh
# Exits: 0 done (each action and its result printed); 10 refused (RB_W, RB_QUIET or RB_LANE missing); 17 a session of ours runs, a
# device-named process of ours is alive, or a leftover is unresolved (nothing released).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e224b.sh"
rb_init end
rb_need RB_W RB_QUIET RB_LANE
[ -f "$RB_W/onelab.sh" ] && [ -f "$RB_W/hold.sh" ] && [ -f "$RB_W/book.sh" ] || rb_die 10 "RB_W does not hold onelab.sh, hold.sh and book.sh"
if [ -n "${E224B_ROOT:-}" ] && [ -d "${E224B_ROOT:-}" ]; then
  e224b_box_free_end() { mkdir -p "$E224B_ROOT/run"; flock -n "$E224B_ROOT/run/box.lock" true; }
  e224b_box_free_end || rb_die 17 "a session, a build or a dry pass of the kit runs in the box root: nothing released under it (step 10 waits)"
fi
[ "$(ours_live session_e224b.sh)" = 0 ] || rb_die 17 "a session_e224b.sh of ours runs: nothing released under it (step 10 waits)"
ND=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n+0}')
[ "$ND" = 0 ] || rb_die 17 "$ND device-named process(es) of ours alive (a LEFTOVER?): the quiet desk flag, the hold line and the booking stay; nothing released (kill nothing; write it up and escalate)"
if [ -n "${E224B_ROOT:-}" ] && [ -d "${E224B_ROOT:-}/sessions" ]; then
  for q in "$E224B_ROOT"/sessions/*/queue.json; do
    [ -f "$q" ] || continue
    LO=$("$PY" -I -B -c 'import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    print("UNREADABLE"); sys.exit(0)
lo = d.get("leftover")
print("UNRESOLVED" if (lo and not (isinstance(lo, dict) and lo.get("resolved") is True)) else "OK")' "$q")
    [ "$LO" = OK ] || rb_die 17 "the session $(basename "$(dirname "$q")") records a leftover $LO in queue.json: the quiet desk flag, the hold line and the booking stay; nothing released (kill nothing; write it up and escalate)"
  done
fi
did=()
if [ -f "$RB_QUIET" ] && [ "$(head -n 1 "$RB_QUIET" | cut -d' ' -f1)" = "$RB_LANE" ]; then
  bash "$RB_E224B_DIR/quiet_e224b.sh" lower "$RB_LANE" > /dev/null && did+=("the quiet desk flag lowered")
else did+=("the quiet desk flag: not ours or down (left)"); fi
OL=$(bash "$RB_W/onelab.sh" show 2>/dev/null)
if echo "$OL" | grep -qx "  desk-$RB_LANE"; then bash "$RB_W/onelab.sh" undesk "$RB_LANE" > /dev/null && did+=("onelab undesk"); fi
if echo "$OL" | grep -qx "  collect-$RB_LANE"; then bash "$RB_W/onelab.sh" uncollect "$RB_LANE" > /dev/null && did+=("onelab uncollect"); fi
HL=$(bash "$RB_W/hold.sh" list 2>/dev/null | tail -n 1)
case " ${HL#HOLD: } " in *" $RB_LANE "*) bash "$RB_W/hold.sh" remove "$RB_LANE" > /dev/null && did+=("the hold line removed") ;; esac
BK=$(bash "$RB_W/book.sh" show 2>/dev/null | grep '^aifoundry2: ' | awk '{print $2}')
[ "$BK" = "$RB_LANE" ] && bash "$RB_W/book.sh" release aifoundry2 "$RB_LANE" > /dev/null && did+=("the booking released")
IFS=";"; rb_ok "E: ${did[*]}"
