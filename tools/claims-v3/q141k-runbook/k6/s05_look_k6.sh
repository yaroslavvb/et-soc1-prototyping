#!/usr/bin/env bash
# Q141(k), go checklist step 5: look first, read-only, on one box: et-who, who, uptime (and on aifoundry1 the kit's own
# box/look_e164.sh: card 1's lines, nothing of ours on card 0, the host's identity since E82's read). Then the holder rule:
# a holder of a device node or a card lock blocks (on aifoundry1, a holder of card 1's nodes or lock, or anything of ours on
# either card); an idle login does not block (the owner's ruling of 1 Nov 2026).
#
#   bash tools/claims-v3/q141k-runbook/s05_look.sh <aifoundry1|aifoundry2|aifoundry3>          # one read
#   bash tools/claims-v3/q141k-runbook/s05_look.sh <box> --wait                                # one bounded poll (at most 520 s)
#
# With --wait, a held card is polled every 30 s on the box inside one bounded call; the minutes add up across calls in
# $RB_OUT/hold-<box>.since, and after 30 minutes in all the step says skip that card (15). Nothing here opens a device, takes a
# lock or prints a name: et-who's holder lines are counted on the box, and any line it prints is masked by rb_run.py.
# Exit 0 FREE; 17 held (with --wait: still held, call again); 15 held 30 minutes in all: skip that card; 16 the host's identity
# fails (aifoundry1: booted after E82's firmware read).
#
# v3 (Q142(s)): on aifoundry1 the identity read fails closed: look_e164.sh must exit 0 and print its "identity: ...: ok" line, else
# 16 (v2 stopped only on a printed STOP) (fault 12; every launch on aifoundry1 and aifoundry2 also checks it, rb_guard_text). The
# --wait loop stops by the box's clock ($SECONDS), not by the sum of its sleeps: each et-who read may take up to 20 s, so v2's loop
# could pass the call's 600 s bound and be killed (13) instead of reading 17 or 15 (fault 9).
#   bash tools/claims-v3/q141k-runbook/v3/s05_look.sh <box> [--wait]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s05_look
box=${1:-}; mode=${2:-}
rb_tree "$box" > /dev/null || rb_die $RB_E_USAGE "usage: s05_look.sh <aifoundry1|aifoundry2|aifoundry3> [--wait]"
case "$mode" in ""|--wait) ;; *) rb_die $RB_E_USAGE "the only option is --wait" ;; esac
rb_probe "$box"
if [ "$box" = aifoundry1 ] && [ -z "$mode" ]; then
  # k6: the kit's own look (E172 box step 1): it prints et-who's lines; rb_run.py masks every holder's login and command
  rb_remote read aifoundry1 "box/look_e172.sh (E172 box step 1)" "$RB_REPO/tools/claims-v3/e172/box/look_e172.sh"
  if [ -z "${RB_DRY:-}" ]; then
    rb_has 'identity: .*: STOP' && rb_die $RB_E_GATE "aifoundry1 booted after E82's firmware read: STOP (E172.md, Device commands sent)"
    [ "$RB_RC" -eq 0 ] && rb_has '^identity: the host booted .*: ok$' ||
      rb_die $RB_E_GATE "look_e172.sh gave no identity line that reads ok (rc $RB_RC): the identity is not shown, so no launch on aifoundry1"
  fi
fi
f=$(rb_file look)
{ rb_prelude "$box"
  echo "MODE=$(printf '%q' "$mode")"
  echo "LIM=$RB_WAIT_LOOP_S; POLL=$RB_HOLD_POLL_S"
  cat <<'EOF'
date '+%F %T %Z'; uptime; echo "booted $(uptime -s)"
echo "login $(id -un)"
hold_read
while [ "$FREE" -eq 0 ] && [ "$MODE" = --wait ] && [ "$SECONDS" -lt "$LIM" ]; do   # v3: the box's clock bounds the loop
  sleep "$POLL"; hold_read
done
echo "HOLDER-RULE: $([ "$FREE" -eq 1 ] && echo FREE || echo HELD) after $SECONDS s of polls"
EOF
} > "$f"
rb_remote $([ "$mode" = --wait ] && echo wait || echo read) "$box" "look first: et-who, who, uptime; the holder rule" "$f"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the look on $box exited $RB_RC"
[ -n "${RB_DRY:-}" ] && exit 0
lg=$(rb_val '^login ([^ ]+)$'); [ -n "$lg" ] && echo "$lg" > "$RB_OUT/box-login-$box.txt"   # our own login there, for the logs' scrub check
st="$RB_OUT/hold-$box.since"
if rb_has '^HOLDER-RULE: FREE'; then rm -f "$st"; rb_say "$box: FREE"; exit 0; fi
[ -f "$st" ] || date +%s > "$st"          # the 30 minutes count from the first reading that found the card held
held=$(( $(date +%s) - $(cat "$st") ))
if [ "$held" -ge "$RB_HOLD_MAX_S" ]; then
  rb_die $RB_E_SKIP "$box held for $((held / 60)) minutes in all: skip that card today (the holder rule)"
fi
if [ "$mode" = --wait ]; then
  rb_say "$box: still HELD after $((held / 60)) minutes in all: call again (skip at $((RB_HOLD_MAX_S / 60)))"
else
  rb_say "$box: HELD (a holder of a device node or a lock): poll with --wait, at most $((RB_HOLD_MAX_S / 60)) minutes in all"
fi
exit $RB_E_AGAIN
