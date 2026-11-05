#!/usr/bin/env bash
# Q143(k), step 5: look first, read-only, on aifoundry3 (or aifoundry2): et-who, who, uptime, and the holder rule: a holder of a device node
# or a card lock blocks; an idle login does not block (the owner's ruling of 1 Nov 2026). k6's s05_look_k6.sh without its aifoundry1 branch
# (M11 runs nothing on aifoundry1). With --wait, a held card is polled every 30 s on the box inside one bounded call; the minutes add up
# across calls in $RB_OUT/hold-<box>.since, and after 30 minutes in all the step says skip that card (15). Nothing here opens a device,
# takes a lock or prints a name. Exit 0 FREE; 17 held (with --wait: still held, call again); 15 held 30 minutes in all.
#
#   bash tools/claims-v3/q143k-runbook/s05_look_q143k.sh <aifoundry3|aifoundry2> [--wait]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s05_look
box=${1:-}; mode=${2:-}
case "$box" in aifoundry3|aifoundry2) ;; *) rb_die $RB_E_USAGE "usage: s05_look_q143k.sh <aifoundry3|aifoundry2> [--wait]" ;; esac
case "$mode" in ""|--wait) ;; *) rb_die $RB_E_USAGE "the only option is --wait" ;; esac
rb_probe "$box"
f=$(rb_file look)
{ rb_prelude "$box"
  echo "MODE=$(printf '%q' "$mode")"
  echo "LIM=$RB_WAIT_LOOP_S; POLL=$RB_HOLD_POLL_S"
  cat <<'EOF2'
date '+%F %T %Z'; uptime; echo "booted $(uptime -s)"
echo "login $(id -un)"
hold_read
while [ "$FREE" -eq 0 ] && [ "$MODE" = --wait ] && [ "$SECONDS" -lt "$LIM" ]; do
  sleep "$POLL"; hold_read
done
echo "OURS-LIVE: $(ours_live) card session(s) of ours on $BOX"
echo "HOLDER-RULE: $([ "$FREE" -eq 1 ] && echo FREE || echo HELD) after $SECONDS s of polls"
EOF2
} > "$f"
rb_remote $([ "$mode" = --wait ] && echo wait || echo read) "$box" "look first: et-who, who, uptime; the holder rule" "$f"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the look on $box exited $RB_RC"
[ -n "${RB_DRY:-}" ] && exit 0
lg=$(rb_val '^login ([^ ]+)$'); [ -n "$lg" ] && echo "$lg" > "$RB_OUT/box-login-$box.txt"
st="$RB_OUT/hold-$box.since"
if rb_has '^HOLDER-RULE: FREE'; then rm -f "$st"; rb_say "$box: FREE ($(rb_val '^OURS-LIVE: ([0-9]+) .*') card session(s) of ours there)"; exit 0; fi
[ -f "$st" ] || date +%s > "$st"
held=$(( $(date +%s) - $(cat "$st") ))
[ "$held" -ge "$RB_HOLD_MAX_S" ] && rb_die $RB_E_SKIP "$box held for $((held / 60)) minutes in all: skip that card today (the holder rule)"
if [ "$mode" = --wait ]; then rb_say "$box: still HELD after $((held / 60)) minutes in all: call again (skip at $((RB_HOLD_MAX_S / 60)))"
else rb_say "$box: HELD (a holder of a device node or a lock): poll with --wait, at most $((RB_HOLD_MAX_S / 60)) minutes in all"; fi
exit $RB_E_AGAIN
