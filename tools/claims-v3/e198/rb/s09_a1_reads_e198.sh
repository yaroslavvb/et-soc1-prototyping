#!/usr/bin/env bash
# E198, box step 7, K6'S READS ON CARD 1 WITH ET_DEVICES=1 (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): E191's reads
# (tools/claims-v3/e191/rb/s09_a1_reads_e191.sh, unchanged beside it, k6's s09 in aifoundry1 card 1's form) for E198, with THE REST RULE
# FIRST (the lesson of the round: step 7's config read opens card 1, so it runs only after the rest opens): the remote script reads E191's
# rest rule (tools/claims-v3/e191/rb/rest_rule_e191.sh, unchanged: every session-log form of ours on aifoundry1 in every tree of ours, E190
# arm B's, E191's and E198's own build/e198/T<T0>/session.log among them, dry and no-device sessions skipped, a cut session at its run's
# latest write) BEFORE anything else; a rest not yet open stops the step with 17 (call again), before the manifest or the config read. Then
# E191's lines, unchanged: et-lab-manifest (kept on the box), card 1's config read through E191's guard (ET_DEVICES=1, card 1's lock,
# timeout 10, its stderr kept: TDP 65 W / 65 C / 600 MHz, minion_mv in (450, 510), PCIe target /dev/et1_mgmt and device ID 1 alone),
# et-who on both cards. Reads only; nothing set.
#   RB_OUT=<dir> RB_LOCK=<file> bash tools/claims-v3/e198/rb/s09_a1_reads_e198.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e198.sh"
rb_init s09_a1_reads
e198_window
rb_need_start
rb_probe aifoundry1
f=$(rb_file reads)
{ rb_prelude aifoundry1
  cat "$RB_E198_DIR/../../e191/rb/rest_rule_e191.sh"
  cat <<'EOF'
export ET_DEVICES=1 V3_DEVICE=1
export LD_LIBRARY_PATH=/opt/et/lib
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on aifoundry1: the config read waits (it opens card 1)"; exit 3; fi
mkdir -p build/q141k
TS=$(date +%Y%m%dT%H%M%S)
et-lab-manifest > build/q141k/et-lab-manifest-$TS.txt 2>&1; echo "MANIFEST rc $? (kept on the box: build/q141k/et-lab-manifest-$TS.txt)"
ERR=build/q141k/e198-reads-config-$TS.err
c=$(flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e191/ettelem_guard_e191.sh config < /dev/null 2>"$ERR" | grep '^{' | tail -1)
echo "CONFIG $c"
grep -E '^(PCIe target|Physical device ID):' "$ERR" | sed 's/  */ /g; s/^/IDENT /'
W=$(timeout 20 et-who 2>&1); WRC=$?
NH=$(printf '%s\n' "$W" | awk '$1 ~ /^\/dev\/et/ || $1 ~ /^lock:/ {n++} END {print n+0}')
PO=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n+0}')
PX=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
echo "holders, both cards: et-who rc $WRC, holder lines $NH; our device processes $PO, other users' device processes $PX"
echo "HOLDER-RULE-BOTH-CARDS: $([ "$WRC" -eq 0 ] && [ "$NH" -eq 0 ] && [ "$PO" -eq 0 ] && [ "$PX" -eq 0 ] && echo FREE || echo HELD)"
EOF
} > "$f"
rb_remote read aifoundry1 "THE REST RULE first; then et-lab-manifest, card 1's config read through E191's guard (ET_DEVICES=1, card 1's lock, stderr kept), et-who" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
if rb_has '^REFUSED: [0-9]+ minutes since '; then
  rb_die $RB_E_AGAIN "THE REST RULE: the 40-minute rest on aifoundry1 has not opened ($(grep -m1 '^REFUSED: ' "$RB_CAP" | cut -c11-200)): no config read before it opens (the reads open card 1): call again after it"
fi
rb_refused
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
cfg=$(rb_val '^CONFIG (\{.*\})$')
[ -n "$cfg" ] || rb_die $RB_E_GATE "no config read came back (card 1's lock was held, or the guard refused, or our own live collector held the management node for a moment): read the output above; if the look (step 4) reads FREE again, run this step ONCE more; a second time: no session"
echo "$cfg" | grep -qE '"tdp_w": ?65[,}]' && echo "$cfg" | grep -qE '"temp_threshold_c": ?65[,}]' && echo "$cfg" | grep -qE '"minion_mhz": ?600[,}]' ||
  rb_die $RB_E_GATE "card 1's config is not TDP 65 W / 65 C / 600 MHz: $cfg"
mv=$(echo "$cfg" | sed -nE 's/.*"minion_mv": ?([0-9]+).*/\1/p')
{ [ -n "$mv" ] && [ "$mv" -lt 510 ] && [ "$mv" -gt 450 ]; } || rb_die $RB_E_GATE "minion_mv ${mv:-none} is not between 450 and 510: this is not card 1's read (card 0 reads 519; a failed read 0): no launch"
rb_has '^IDENT PCIe target: /dev/et1_mgmt' && ! rb_has '^IDENT PCIe target: /dev/et0_' || rb_die $RB_E_GATE "the read's stderr does not name /dev/et1_mgmt alone: the card cannot be told: no launch"
rb_has '^IDENT Physical device ID: 1 ' && ! rb_has '^IDENT Physical device ID: [02-9]' || rb_die $RB_E_GATE "the read's stderr does not give physical device ID 1 alone: no launch"
rb_has '^HOLDER-RULE-BOTH-CARDS: FREE' || rb_die $RB_E_AGAIN "a holder or a device process on aifoundry1 (either card): look again (s05_look_e198.sh --wait)"
rb_say "aifoundry1 card 1: manifest kept on the box (build/q141k/), config TDP 65 W / 65 C / 600 MHz, minion_mv $mv, identity /dev/et1_mgmt and device ID 1 (read, nothing set); both cards free"
