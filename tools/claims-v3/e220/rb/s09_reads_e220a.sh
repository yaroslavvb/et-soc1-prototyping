#!/usr/bin/env bash
# E220 ARM A (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum), the box step "the reads" (this file is s09; STEP 7), MADE SAFE FOR
# THE REST (E202's s09_a3_reads_e202.sh form; E218's rb/s09_reads_e218.sh, landed in 5582edfc, with E215 ARM B's card-1 read, rb/s09_reads_e215.sh
# landed in 8bde0182, run on aifoundry1 by E215 arm B: k6 has no card-1 step 7): the config read below is a CARD COMMAND, the day's first, and
# E192's data note 1 (4e964246) found such a read sent inside the 40-minute rest. So this step:
#   1. reads THE NEVER-RUN REPORT's time first (RB_OUT/e220a-neverrun-A.txt, step 6n): it must have been written within the last 30 minutes
#      (E220.md section 4: the card lanes repeat the scan right before their first card command), else 10 with nothing read from the card (run
#      step 6n again);
#   2. reads THE REST RULE on aifoundry1 (rb/rest_rule_e220a.sh, in one 60 s read: every session-log form of ours there, the activity floor, the
#      model session's folders ~/claude/work/ee-*/; no card command) and refuses (10) with nothing read from the card while the rest has not run
#      (E220.md 6: "the first card command at least 40 minutes after the last session on aifoundry1 ended, either card, ours or the model
#      session's, and THE REST RULE: no write under the model session's ~/claude/work/ee-*/ on aifoundry1 within the last 40 minutes");
#   3. only then stamps the time (RB_OUT/e220a-step7-A.txt: step 7's config read is reported apart from the session's card time, which counts
#      from the session's own first card command) and reads card 1 by E215 arm B's read: in one 60 s read on the box, refused beside a session of
#      ours, the config through E220 arm A's guard with ET_DEVICES=1 under card 1's lock (flock -n, a plain timeout 10), its stderr's identity
#      lines kept (/dev/et1_mgmt, physical device ID 1, minion_mv below 510), and the holder rule: no line on card 1, nothing of ours on either
#      card, and no line of any login on card 0: TDP 65 W / 65 C / 600 MHz (a threshold of 70 C, or any other value, is not as found: 16).
# Exits: 10 with "the never-run report" or "the rest has not run" (run step 6n again / wait in bounded chunks and run it again, never around it);
# 0 the reads as found; 16 (not as found: no session that day, set nothing); 17 (et-who not clean: the look with --wait, then step 7 again).
# Steps 8 and 9 follow without delay.
#   bash tools/claims-v3/e220/rb/s09_reads_e220a.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e220a.sh"
rb_init s09_reads
e220a_arm "${1:-}"
e220a_window
NRF="$RB_OUT/e220a-neverrun-$ARM.txt"
if [ -n "${RB_DRY:-}" ]; then
  echo "--- gate: RB_OUT/e220a-neverrun-$ARM.txt (step 6n's NEVER-RUN line) written within the last 30 minutes, else 10: run step 6n again"
else
  [ -s "$NRF" ] || rb_die $RB_E_USAGE "no never-run report (RB_OUT/e220a-neverrun-$ARM.txt): run step 6n (s06n_neverrun_e220a.sh $ARM) first: no config read sent"
  age=$(( $(date +%s) - $(date -r "$NRF" +%s) ))
  [ "$age" -le 1800 ] || rb_die $RB_E_USAGE "the never-run report is $((age / 60)) minutes old (more than 30): run step 6n again, then this step: no config read sent"
  rb_say "the never-run report $((age / 60)) minutes old: $(cut -c1-200 "$NRF")"
fi
rb_probe "$BOX"
f=$(rb_file rest)
{ rb_prelude "$BOX"
  cat "$RB_E220A_DIR/rest_rule_e220a.sh"
  echo 'echo "REST-OK: the rest has run on $BOX"'
} > "$f"
rb_remote read "$BOX" "THE REST RULE before any card command (every session-log form of ours on the box, the floor, the model session's folders)" "$f"
if [ -z "${RB_DRY:-}" ]; then
  rb_has '^REFUSED: ' && rb_die $RB_E_USAGE "the rest has not run: $(grep -m1 '^REFUSED: ' "$RB_CAP" | cut -c1-240): no config read sent; call this step again once it has"
  rb_has '^REST-OK: ' || rb_die $RB_E_FAIL "the rest read gave no answer (rc $RB_RC): no config read sent"
  echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
  rb_say "$(grep -m1 '^rest: ' "$RB_CAP" | cut -c1-200): the reads follow"
  date '+%F %T %Z' > "$RB_OUT/e220a-step7-$ARM.txt"
fi
f=$(rb_file reads)
{ rb_prelude "$BOX"
  cat <<'EOF2'
unset V3_DEVICE
export LD_LIBRARY_PATH=/opt/et/lib ET_DEVICES=1
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on aifoundry1: the config read waits (it opens card 1)"; exit 3; fi
mkdir -p build/q141k
E=build/q141k/e220a-step7-config-$(date +%Y%m%dT%H%M%S).err
c=$(flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e220/ettelem_guard_e220a.sh config < /dev/null 2> "$E" | grep '^{' | tail -1)
echo "CONFIG $c"
grep -E '^(PCIe target|Physical device ID):' "$E" | tr -s ' ' | sed 's/^/IDENT /'
hold_read
C0=$(printf '%s\n' "$W" | awk '$1 ~ /^\/dev\/et0_/ || $1 == "lock:etsoc-shire0.lock" {n++} END {print n+0}')
echo "card 0 holder lines (any login): $C0"
echo "HOLDER-RULE: $([ "$FREE" -eq 1 ] && [ "$C0" -eq 0 ] && echo FREE || echo HELD)"
EOF2
} > "$f"
rb_remote read aifoundry1 "card 1's config read through E220 arm A's guard (ET_DEVICES=1, card 1's lock), its identity lines, et-who" "$f"
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
rb_has '^HOLDER-RULE: FREE' || rb_die $RB_E_AGAIN "et-who is not clean for arm A on aifoundry1 (card 1, ours on either card, or any line on card 0): look again (a2/rb/s05_look_e220a_a2.sh A, or k6's look with --wait), then step 7 again"
rb_say "aifoundry1 card 1: config TDP 65 W / 65 C / 600 MHz, minion_mv $mv; identity /dev/et1_mgmt, physical device ID 1; et-who clean (card 0 too)"
