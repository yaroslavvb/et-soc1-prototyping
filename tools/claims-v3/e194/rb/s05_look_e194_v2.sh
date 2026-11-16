#!/usr/bin/env bash
# E194, dated amendment A1 (Q187, Sun 15 Nov 2026, before any E194 datum): the box step "the look", v2 (this file is s05 v2), FIRST on the
# box, read-only, on aifoundry2 itself. It is the kit's look (rb/s05_look_e194.sh, f01e1cb2, unchanged beside it) line for line, but for
# THE IDENTITY, which it reads by E194's OWN FIRMWARE GATE (rb/fwgate_e194.sh; E194.md.dated-amendment-A1.md) in place of k6's
# identity by continuity from E69's read:
#   - THE QUIET DESK FLAG first (rb/quiet_e194.sh raise, right before this step; e194_quiet refuses 10 when it is not raised);
#   - the gate's record, ON THE DESK, before anything reaches the box: fwread-e194's firmware read of aifoundry2 card 0 (15cb0fcb,
#     2026-11-15 15:22:02 PST) there as committed and EQUAL to E69's read of record in all seven fields, else 16 and no box call;
#   - the gate's boot rule, ON THE BOX: aifoundry2 booted (uptime -s) strictly before that read, else "identity: ...: STOP" and 16 (the
#     v2 launch checks both again); the firmware-revisions query is never sent here;
#   - et-who, read as COUNTS by card and by login class (ours / another login), never a name;
#   - ps, as counts: our device processes (lib.sh's DEV_COMM) and other users'; our sessions and queues (E194's ours_live, by each process's
#     own script) and the runbook's detached jobs (jobs_live); THE P2 COUNT (device-named processes and session or queue scripts of ours);
#   - THE HOLDER RULE: FREE only when et-who answers (rc 0) with no holder line at all, no device process of anyone's, no session or queue
#     of ours and no runbook job. An idle login does not block (the owner's ruling of 1 Nov 2026). Our own live collector reads the card
#     for a moment once a second while nothing holds it (its `ettelem temp`), so a single look can read HELD: --wait polls again.
# With --wait a held box is polled every 30 s on the box inside one bounded call; the minutes add up across calls in
# $RB_OUT/hold-aifoundry2.since, and after 30 minutes in all the step says skip E194 today (15). It writes our own login to
# RB_OUT/box-login-aifoundry2.txt (the collection's scrub reads it). Nothing here opens a device or takes a lock.
# Exit 0 FREE; 17 held (with --wait: still held, call again); 15 held 30 minutes in all: skip; 16 the gate (the record or the boot) says stop.
#   RB_QUIET=<the flag file> bash tools/claims-v3/e194/rb/s05_look_e194_v2.sh [--wait]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e194.sh"
. "$(dirname "${BASH_SOURCE[0]}")/fwgate_e194.sh"
rb_init s05_look_v2
mode=${1:-}
case "$mode" in ""|--wait) ;; *) rb_die $RB_E_USAGE "the only option is --wait" ;; esac
e194_quiet
e194_fwgate_desk
box=aifoundry2
rb_probe "$box"
f=$(rb_file look)
{ rb_prelude "$box"
  echo "MODE=$(printf '%q' "$mode")"
  echo "LIM=$RB_WAIT_LOOP_S; POLL=$RB_HOLD_POLL_S"
  cat <<'EOF'
date '+%F %T %Z'; uptime; echo "booted $(uptime -s)"
echo "login $(id -un)"
EOF
  e194_fwgate_text look
  cat <<'EOF'
one_read() {  # counts by card and login class; FREE1=1 when nothing blocks the card
  W=$(timeout 20 et-who 2>&1); WRC=$?
  ME=$(id -un)
  cnt() { printf '%s\n' "$W" | awk -v me="$ME" -v want="$1" -v who="$2" '
    ($1 ~ /^\/dev\/et/ || $1 ~ /^lock:/) {
      c = "?"; if ($1 ~ /^\/dev\/et0_/ || $1 == "lock:etsoc-shire0.lock") c = "0"
      if (c == want && ((who == "ours" && $2 == me) || (who == "other" && $2 != me))) n++ }
    END { print n + 0 }'; }
  C0O=$(cnt 0 ours); C0X=$(cnt 0 other); CQ=$(cnt '?' ours); CQX=$(cnt '?' other)
  PO=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n+0}')
  PX=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
  OL=$(ours_live); JL=$(jobs_live); LG=$(who | wc -l | tr -d ' ')
  FREE1=0
  [ "$WRC" -eq 0 ] && [ $((C0O + C0X + CQ + CQX)) -eq 0 ] && [ "$PO" -eq 0 ] && [ "$PX" -eq 0 ] && [ "$OL" -eq 0 ] && [ "$JL" -eq 0 ] && FREE1=1
  echo "the card: et-who rc $WRC; card 0 holder lines: ours $C0O, another login's $C0X; other lines: ours $CQ, another login's $CQX; our device processes $PO, other users' device processes $PX; our sessions or queues $OL, runbook jobs $JL; logins $LG (an idle login does not block)"
  p2_count
}
one_read
while [ "$FREE1" -eq 0 ] && [ "$MODE" = --wait ] && [ "$SECONDS" -lt "$LIM" ]; do   # the box's clock bounds the loop
  sleep "$POLL"; one_read
done
echo "HOLDER-RULE-ONE-CARD: $([ "$FREE1" -eq 1 ] && echo FREE || echo HELD) after $SECONDS s of polls"
EOF
} > "$f"
rb_remote $([ "$mode" = --wait ] && echo wait || echo read) "$box" "look first, the box's one card: the identity by E194's firmware gate (the boot before its read of record), et-who as counts, ps, our sessions and jobs, the P2 count; the holder rule" "$f"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the look on $box exited $RB_RC"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^identity: .*: STOP$' && rb_die $RB_E_GATE "aifoundry2 did not boot before E194's firmware read of record ($E194_FW_AT; E194.md A1): $(grep -m1 '^identity: ' "$RB_CAP" | cut -c1-200): no launch on aifoundry2 (the card may have restarted since the read: a new read of record and a dated note first)"
rb_has '^identity: the host booted .*: ok$' || rb_die $RB_E_GATE "the look gave no identity line that reads ok: the identity is not shown, so no launch on aifoundry2"
grep -m1 '^identity: ' "$RB_CAP" | sed 's/^/    /'
lg=$(rb_val '^login ([^ ]+)$'); [ -n "$lg" ] && echo "$lg" > "$RB_OUT/box-login-$box.txt"
grep -m1 '^the card: ' "$RB_CAP" | sed 's/^/    /'
grep '^P2 ' "$RB_CAP" | tail -n 1 | sed 's/^/    /'
st="$RB_OUT/hold-$box.since"
if rb_has '^HOLDER-RULE-ONE-CARD: FREE'; then rm -f "$st"; rb_say "$box: FREE (nothing holds card 0; no device process of anyone's; no session or job of ours); the identity by E194's firmware gate: ok"; exit 0; fi
[ -f "$st" ] || date +%s > "$st"
held=$(( $(date +%s) - $(cat "$st") ))
if [ "$held" -ge "$RB_HOLD_MAX_S" ]; then
  rb_die $RB_E_SKIP "$box held for $((held / 60)) minutes in all: skip E194 today (the holder rule)"
fi
if [ "$mode" = --wait ]; then
  rb_say "$box: still HELD after $((held / 60)) minutes in all: call again (skip at $((RB_HOLD_MAX_S / 60)))"
else
  rb_say "$box: HELD (a holder, a device process, or a session or job of ours; our live collector's read can hold it for a moment): poll with --wait, at most $((RB_HOLD_MAX_S / 60)) minutes in all"
fi
exit $RB_E_AGAIN
