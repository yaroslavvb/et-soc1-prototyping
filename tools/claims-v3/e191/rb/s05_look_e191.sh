#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum), the box step "the look" (this file is
# s05), FIRST on the box, read-only: k6's look (tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh, unchanged beside it) for aifoundry1,
# covering BOTH CARDS (E191.md 2 and 13, dated note 1's item 3(b): never two sessions of ours on aifoundry1; nothing on card 0):
#   - the host's identity by continuity, E172's look's rule (box/look_e172.sh): booted before E82's firmware read of 2026-10-31 13:45:24
#     PDT, else 16 (rb_guard_text checks it again at the launch); the firmware-revisions query is never sent;
#   - et-who, read as COUNTS by card and by login class (ours / another login), never a name: card 1's lines and card 0's lines;
#   - ps, as counts: our device processes (lib.sh's DEV_COMM) and other users'; our sessions and queues (E191's ours_live, by each process's
#     own script) and the runbook's detached jobs (jobs_live);
#   - THE HOLDER RULE, both cards (the runner's own holder rule, e191_ident.foreign_lines, reads the same before its first card command):
#     FREE only when et-who answers (rc 0) with no holder line on EITHER card (another login's on card 0 blocks too: the runners count
#     openers and the driver's use count across both cards), no device process of anyone's, no session or queue of ours and no runbook job;
#     card 0 is never opened, by this step or any other of the kit. An idle login does not block (the owner's ruling of 1 Nov 2026).
# With --wait a held box is polled every 30 s on the box inside one bounded call (the box's clock bounds it); the minutes add up across
# calls in $RB_OUT/hold-aifoundry1.since, and after 30 minutes in all the step says skip that card (15). It writes our own login there to
# RB_OUT/box-login-aifoundry1.txt (the collection's scrub of the login reads it). Nothing here opens a device or takes a lock.
# Exit 0 FREE; 17 held (with --wait: still held, call again); 15 held 30 minutes in all: skip; 16 the host's identity fails.
#   bash tools/claims-v3/e191/rb/s05_look_e191.sh [--wait]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e191.sh"
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
  rb_die $RB_E_SKIP "$box held for $((held / 60)) minutes in all: skip E191 today (the holder rule)"
fi
if [ "$mode" = --wait ]; then
  rb_say "$box: still HELD after $((held / 60)) minutes in all: call again (skip at $((RB_HOLD_MAX_S / 60)))"
else
  rb_say "$box: HELD (a holder on either card, a device process, or a session or job of ours): poll with --wait, at most $((RB_HOLD_MAX_S / 60)) minutes in all"
fi
exit $RB_E_AGAIN
