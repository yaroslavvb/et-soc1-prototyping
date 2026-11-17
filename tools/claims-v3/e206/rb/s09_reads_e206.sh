#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum), the box step "the reads" (this file is s09; STEP 7), MADE SAFE FOR THE
# REST (E202's s09_a3_reads_e202.sh form): the config read below is a CARD COMMAND, and E192's data note 1 (4e964246) found such a read sent
# inside the 40-minute rest. So this step reads THE REST RULE on the arm's box FIRST (rb/rest_rule_e206.sh, in one 60 s read: every
# session-log form of ours there, the activity floor, the model session's folders; no card command) and refuses (10) with nothing read from
# the card while the rest has not run; only then it stamps the time (RB_OUT/e206-step7-<arm>.txt: step 7's config read is reported apart
# from the session's card time, which counts from the session's own first card command) and reads the card:
#   arm A (aifoundry3 card 0): k6's step 7 as it is (tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh, UNCHANGED: et-lab-manifest, the
#     card's config through E128's guard under card 0's lock with a plain timeout 10, et-who's holder rule): TDP 0 W / 65 C / 600 MHz,
#     et-who clean;
#   arm B (aifoundry1 card 1; k6 has no card-1 step 7): in one 60 s read on the box, refused beside a session of ours, the config through
#     E206's guard with ET_DEVICES=1 under card 1's lock (flock -n /run/lock/etsoc-shire1.lock, a plain timeout 10), its stderr's identity
#     lines kept, and the holder rule: k6's for aifoundry1 (no line on card 1, nothing of ours on either card, no device process of ours)
#     AND the kit's start rule (no holder line on card 0 of any login): the config 65 W / 65 C / 600 MHz, the identity /dev/et1_mgmt,
#     physical device ID 1, minion_mv below 510, et-who clean.
# Exits: 10 with "the rest has not run" (wait in bounded chunks and run it again, never around it); 0 the reads as found; 16 (not as found:
# no session that day, set nothing); 17 (et-who not clean: the look with --wait, then step 7 again). Steps 8 and 9 follow without delay.
#   bash tools/claims-v3/e206/rb/s09_reads_e206.sh <A|B>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e206.sh"
rb_init s09_reads
e206_arm "${1:-}"
e206_window
rb_probe "$BOX"
f=$(rb_file rest)
{ rb_prelude "$BOX"
  cat "$RB_E206_DIR/rest_rule_e206.sh"
  echo 'echo "REST-OK: the rest has run on $BOX"'
} > "$f"
rb_remote read "$BOX" "THE REST RULE before any card command (every session-log form of ours on the box, the floor, the model session's folders)" "$f"
if [ -z "${RB_DRY:-}" ]; then
  rb_has '^REFUSED: ' && rb_die $RB_E_USAGE "the rest has not run: $(grep -m1 '^REFUSED: ' "$RB_CAP" | cut -c1-240): no config read sent; call this step again once it has"
  rb_has '^REST-OK: ' || rb_die $RB_E_FAIL "the rest read gave no answer (rc $RB_RC): no config read sent"
  echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
  rb_say "$(grep -m1 '^rest: ' "$RB_CAP" | cut -c1-200): the reads follow"
  date '+%F %T %Z' > "$RB_OUT/e206-step7-$ARM.txt"
fi
if [ "$ARM" = A ]; then
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- then the time stamped in RB_OUT/e206-step7-A.txt and k6's step 7, unchanged: bash tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh (its own listing follows)"
  fi
  exec bash "$RB_REPO/tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh"
fi
f=$(rb_file reads)
{ rb_prelude "$BOX"
  cat <<'EOF2'
unset V3_DEVICE
export LD_LIBRARY_PATH=/opt/et/lib ET_DEVICES=1
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on aifoundry1: the config read waits (it opens card 1)"; exit 3; fi
mkdir -p build/q141k
E=build/q141k/e206-step7-config-$(date +%Y%m%dT%H%M%S).err
c=$(flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e206/ettelem_guard_e206.sh config < /dev/null 2> "$E" | grep '^{' | tail -1)
echo "CONFIG $c"
grep -E '^(PCIe target|Physical device ID):' "$E" | tr -s ' ' | sed 's/^/IDENT /'
hold_read
C0=$(printf '%s\n' "$W" | awk '$1 ~ /^\/dev\/et0_/ || $1 == "lock:etsoc-shire0.lock" {n++} END {print n+0}')
echo "card 0 holder lines (any login): $C0"
echo "HOLDER-RULE: $([ "$FREE" -eq 1 ] && [ "$C0" -eq 0 ] && echo FREE || echo HELD)"
EOF2
} > "$f"
rb_remote read aifoundry1 "card 1's config read through E206's guard (ET_DEVICES=1, card 1's lock), its identity lines, et-who" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_refused
cfg=$(rb_val '^CONFIG (\{.*\})$')
[ -n "$cfg" ] || rb_die $RB_E_GATE "no config read came back (the lock was held, or the guard refused): read the output above"
echo "$cfg" | grep -qE '"tdp_w": ?65,' && echo "$cfg" | grep -qE '"temp_threshold_c": ?65,' && echo "$cfg" | grep -qE '"minion_mhz": ?600,' ||
  rb_die $RB_E_GATE "aifoundry1 card 1's config is not TDP 65 W / 65 C / 600 MHz: $cfg"
mv=$(echo "$cfg" | sed -nE 's/^.*"minion_mv": ?([0-9]+).*$/\1/p')
[ -n "$mv" ] && [ "$mv" -lt 510 ] || rb_die $RB_E_GATE "the config read's minion_mv is '${mv:-none}', not below 510: not card 1 (card 0 reads 519): no session"
rb_has '^IDENT PCIe target: /dev/et1_mgmt *$' && ! rb_has '^IDENT PCIe target: /dev/et0' || rb_die $RB_E_GATE "the config read's PCIe target is not /dev/et1_mgmt alone (the lines above): no session"
rb_has '^IDENT Physical device ID: 1 ' && ! rb_has '^IDENT Physical device ID: 0 ' || rb_die $RB_E_GATE "the config read's physical device ID is not 1 alone (the lines above): no session"
rb_has '^HOLDER-RULE: FREE' || rb_die $RB_E_AGAIN "et-who is not clean for arm B on aifoundry1 (card 1, ours on either card, or any line on card 0): look again (s05_look_k6.sh aifoundry1 --wait), then step 7 again"
rb_say "aifoundry1 card 1: config TDP 65 W / 65 C / 600 MHz, minion_mv $mv; identity /dev/et1_mgmt, physical device ID 1; et-who clean (card 0 too)"
