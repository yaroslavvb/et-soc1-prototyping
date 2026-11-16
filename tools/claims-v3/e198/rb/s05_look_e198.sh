#!/usr/bin/env bash
# E198, box step 4, THE LOOK ON aifoundry1, BOTH CARDS (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): E191's look
# (tools/claims-v3/e191/rb/s05_look_e191.sh, unchanged beside it) for E198, every line its own but the runbook file it sources:
#   the reboot gate by continuity (the host booted before E82's firmware read of 2026-10-31 13:45:24 PDT; aifoundry1 booted
#   2026-10-26 15:02:04 PDT when read on Sun 15 Nov 2026); et-who as counts by card and login class (card 1's lines, card 0's lines,
#   ours and another login's), ps (our device processes and other users'), our sessions or queues (ours_live: session_e198.sh among them)
#   and runbook jobs; FREE only when nothing holds EITHER card and nothing of ours runs; --wait polls (30 s) within one bounded call; held
#   for 30 minutes in all: skip E198 today (15). It writes RB_OUT/box-login-aifoundry1.txt (the collection's scrub reads it). Card 0 is
#   never opened: et-who and ps only.
#   RB_OUT=<dir> RB_LOCK=<file> bash tools/claims-v3/e198/rb/s05_look_e198.sh [--wait]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e198.sh"
rb_init s05_look
mode=${1:-}
case "$mode" in ""|--wait) ;; *) rb_die $RB_E_USAGE "the only option is --wait" ;; esac
box=aifoundry1
rb_probe "$box"
f=$(rb_file look)
{ rb_prelude "$box"
  echo "MODE=$(printf '%q' "$mode")"
  echo "LIM=$RB_WAIT_LOOP_S; POLL=$RB_HOLD_POLL_S"
  cat <<'EOF'
date '+%F %T %Z'; uptime; echo "booted $(uptime -s)"
echo "login $(id -un)"
boot=$(date -d "$(uptime -s)" +%s); e82=$(date -d '2026-10-31 13:45:24 PDT' +%s)
if [ "$boot" -lt "$e82" ]; then echo "identity: the host booted $(uptime -s), before E82's firmware read of 2026-10-31 13:45:24 PDT: ok"
else echo "identity: the host booted $(uptime -s), AFTER E82's firmware read: STOP"; fi
both_read() {  # counts by card and login class; FREE2=1 when nothing blocks either card (the module header's rule)
  W=$(timeout 20 et-who 2>&1); WRC=$?
  ME=$(id -un)
  cnt() { printf '%s\n' "$W" | awk -v me="$ME" -v want="$1" -v who="$2" '
    ($1 ~ /^\/dev\/et/ || $1 ~ /^lock:/) {
      c = "?"; if ($1 ~ /^\/dev\/et0_/ || $1 == "lock:etsoc-shire0.lock") c = "0"; if ($1 ~ /^\/dev\/et1_/ || $1 == "lock:etsoc-shire1.lock") c = "1"
      if (c == want && ((who == "ours" && $2 == me) || (who == "other" && $2 != me))) n++ }
    END { print n + 0 }'; }
  C1O=$(cnt 1 ours); C1X=$(cnt 1 other); C0O=$(cnt 0 ours); C0X=$(cnt 0 other); CQ=$(cnt '?' ours); CQX=$(cnt '?' other)
  PO=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n+0}')
  PX=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
  OL=$(ours_live); JL=$(jobs_live); LG=$(who | wc -l | tr -d ' ')
  FREE2=0
  [ "$WRC" -eq 0 ] && [ $((C1O + C1X + C0O + C0X + CQ + CQX)) -eq 0 ] && [ "$PO" -eq 0 ] && [ "$PX" -eq 0 ] && [ "$OL" -eq 0 ] && [ "$JL" -eq 0 ] && FREE2=1
  echo "both cards: et-who rc $WRC; card 1 holder lines: ours $C1O, another login's $C1X; card 0 holder lines: ours $C0O, another login's $C0X; other lines: ours $CQ, another login's $CQX; our device processes $PO, other users' device processes $PX; our sessions or queues $OL, runbook jobs $JL; logins $LG (an idle login does not block)"
}
both_read
while [ "$FREE2" -eq 0 ] && [ "$MODE" = --wait ] && [ "$SECONDS" -lt "$LIM" ]; do   # the box's clock bounds the loop
  sleep "$POLL"; both_read
done
echo "HOLDER-RULE-BOTH-CARDS: $([ "$FREE2" -eq 1 ] && echo FREE || echo HELD) after $SECONDS s of polls"
EOF
} > "$f"
rb_remote $([ "$mode" = --wait ] && echo wait || echo read) "$box" "look first, both cards: the identity by continuity, et-who as counts by card, ps, our sessions and jobs; the holder rule" "$f"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the look on $box exited $RB_RC"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^identity: .*: STOP$' && rb_die $RB_E_GATE "aifoundry1 booted after E82's firmware read: its firmware build is not carried by continuity: no launch on aifoundry1"
rb_has '^identity: the host booted .*: ok$' || rb_die $RB_E_GATE "the look gave no identity line that reads ok: the identity is not shown, so no launch on aifoundry1"
lg=$(rb_val '^login ([^ ]+)$'); [ -n "$lg" ] && echo "$lg" > "$RB_OUT/box-login-$box.txt"
grep -m1 '^both cards: ' "$RB_CAP" | sed 's/^/    /'
st="$RB_OUT/hold-$box.since"
if rb_has '^HOLDER-RULE-BOTH-CARDS: FREE'; then rm -f "$st"; rb_say "$box: FREE on both cards (nothing of ours on either; card 0 not opened)"; exit 0; fi
[ -f "$st" ] || date +%s > "$st"
held=$(( $(date +%s) - $(cat "$st") ))
if [ "$held" -ge "$RB_HOLD_MAX_S" ]; then
  rb_die $RB_E_SKIP "$box held for $((held / 60)) minutes in all: skip E198 today (the holder rule)"
fi
if [ "$mode" = --wait ]; then
  rb_say "$box: still HELD after $((held / 60)) minutes in all: call again (skip at $((RB_HOLD_MAX_S / 60)))"
else
  rb_say "$box: HELD (a holder on either card, a device process, or a session or job of ours): poll with --wait, at most $((RB_HOLD_MAX_S / 60)) minutes in all"
fi
exit $RB_E_AGAIN
