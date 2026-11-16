#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum), the box step "the reads" (this file
# is s09): k6's reads (tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh, unchanged beside it) on aifoundry2 for its one card, READ only,
# in E191's step 7 form (tools/claims-v3/e191/rb/s09_a1_reads_e191.sh) with this box's card and two lessons carried in:
#   - THE REST RULE FIRST (E192's data note 1's lesson, CONTEXT section 112: k6's step 7 read a card's config 1,888 s after our last session
#     there, before step 9's rest rule): the same lines step 9 sends (rb/rest_rule_e194.sh) run on the box before anything here opens the
#     card; REFUSED (the rest not yet open) is 10 here, and nothing is read: run this step again after the rest opens;
#   - OUR OWN LIVE COLLECTOR (E191's verifier's nit 9; KIT.md section 4): it reads the card for a moment once a second while nothing holds
#     it (its `ettelem temp`), and the management node allows one opener, so this step waits (bounded, 6 s) until no device process of ours
#     runs before it takes the card's lock; "no config read came back" (16) is still allowed ONE re-run after the look reads FREE again;
#   - et-lab-manifest (sysfs and files; it never opens /dev/et*), kept on the box under build/q141k/;
#   - the card's static config through E194's guard (`ettelem config` only; aifoundry2 and ET_DEVICES and V3_DEVICE unset only), under card
#     0's lock (flock -n /run/lock/etsoc-shire0.lock), `timeout 10`, its stderr KEPT on the box (build/q141k/e194-reads-config-<time>.err):
#     the identity lines (PCIe target, Physical device ID) are printed here, and the step requires /dev/et0_mgmt alone, device ID 0 alone,
#     TDP 65 W, threshold 65 C, minion 600 MHz at rest and minion_mv between 450 and 600 (the session's own gate reads it again) - never set;
#   - the holder rule on the box's one card (counts only);
#   - fix-e194 (verify-e194's nit 6): the read's stdout is kept on the box (build/q141k/e194-reads-config-<time>.out) and its object is read
#     by e194_common.py --config-line (host_result: the last object beginning '{"tdp_w"', no foreign newline inside it, every dropped span
#     a whole known runtime line), never by the last line that begins with '{'.
#   RB_QUIET=<the flag file> bash tools/claims-v3/e194/rb/s09_reads_e194.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e194.sh"
rb_init s09_reads
e194_window
e194_quiet
rb_probe aifoundry2
f=$(rb_file reads)
{ rb_prelude aifoundry2
  cat <<'EOF'
unset ET_DEVICES V3_DEVICE
export LD_LIBRARY_PATH=/opt/et/lib
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on aifoundry2: the config read waits (it opens the card)"; exit 3; fi
EOF
  echo 'rest_rule_e194() {'
  cat "$RB_E194_DIR/rest_rule_e194.sh"
  echo '}'
  cat <<'EOF'
( rest_rule_e194 ) > build/q141k-rest-e194.tmp 2>&1; rrc=$?
cat build/q141k-rest-e194.tmp; rm -f build/q141k-rest-e194.tmp
[ "$rrc" -eq 0 ] || { echo "REFUSED: the rest has not opened (the lines above): the config read waits until it does (E192's note 1 lesson)"; exit 3; }
mkdir -p build/q141k
TS=$(date +%Y%m%dT%H%M%S)
et-lab-manifest > build/q141k/et-lab-manifest-$TS.txt 2>&1; echo "MANIFEST rc $? (kept on the box: build/q141k/et-lab-manifest-$TS.txt)"
w=0
while [ "$w" -lt 6 ] && [ "$(ps -eo uid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $2 ~ re {n++} END {print n+0}')" -gt 0 ]; do
  sleep 1; w=$((w + 1))
done
echo "SETTLE: waited $w s for no device process of ours (our live collector's read in flight) before the lock"
ERR=build/q141k/e194-reads-config-$TS.err
OUTF=build/q141k/e194-reads-config-$TS.out
flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e194/ettelem_guard_e194.sh config < /dev/null > "$OUTF" 2>"$ERR"; echo "CONFIG-RC $?"
c=$(python3 -I -B tools/claims-v3/e194/e194_common.py --config-line "$OUTF" 2>>"$ERR")
echo "CONFIG $c"
grep -E '^(PCIe target|Physical device ID):' "$ERR" | sed 's/  */ /g; s/^/IDENT /'
W=$(timeout 20 et-who 2>&1); WRC=$?
NH=$(printf '%s\n' "$W" | awk '$1 ~ /^\/dev\/et/ || $1 ~ /^lock:/ {n++} END {print n+0}')
PO=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n+0}')
PX=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
echo "holders, the card: et-who rc $WRC, holder lines $NH; our device processes $PO, other users' device processes $PX"
echo "HOLDER-RULE-ONE-CARD: $([ "$WRC" -eq 0 ] && [ "$NH" -eq 0 ] && [ "$PO" -eq 0 ] && [ "$PX" -eq 0 ] && echo FREE || echo HELD)"
EOF
} > "$f"
rb_remote read aifoundry2 "the rest rule first; et-lab-manifest, card 0's config read through E194's guard (ET_DEVICES unset, card 0's lock, stderr kept), et-who" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_refused
cfg=$(rb_val '^CONFIG (\{.*\})$')
[ -n "$cfg" ] || rb_die $RB_E_GATE "no config read came back (card 0's lock was held, or the guard refused, or our own live collector held the management node for a moment): read the output above; if the look (step 4) reads FREE again, run this step ONCE more; a second time: no session"
echo "$cfg" | grep -qE '"tdp_w": ?65[,}]' && echo "$cfg" | grep -qE '"temp_threshold_c": ?65[,}]' && echo "$cfg" | grep -qE '"minion_mhz": ?600[,}]' ||
  rb_die $RB_E_GATE "card 0's config is not TDP 65 W / 65 C / 600 MHz at rest: $cfg"
mv=$(echo "$cfg" | sed -nE 's/.*"minion_mv": ?([0-9]+).*/\1/p')
{ [ -n "$mv" ] && [ "$mv" -lt 600 ] && [ "$mv" -gt 450 ]; } || rb_die $RB_E_GATE "minion_mv ${mv:-none} is not between 450 and 600 (this card read 519 at rest; a failed read 0): no launch"
rb_has '^IDENT PCIe target: /dev/et0_mgmt' && ! rb_has '^IDENT PCIe target: /dev/et([1-9]|0_ops)' || rb_die $RB_E_GATE "the read's stderr does not name /dev/et0_mgmt alone: the card cannot be told: no launch"
rb_has '^IDENT Physical device ID: 0 ' && ! rb_has '^IDENT Physical device ID: [1-9]' || rb_die $RB_E_GATE "the read's stderr does not give physical device ID 0 alone: no launch"
rb_has '^HOLDER-RULE-ONE-CARD: FREE' || rb_die $RB_E_AGAIN "a holder or a device process on aifoundry2: look again (s05_look_e194.sh --wait)"
rb_say "aifoundry2 card 0: the rest open; manifest kept on the box (build/q141k/), config TDP 65 W / 65 C / 600 MHz, minion_mv $mv, identity /dev/et0_mgmt and device ID 0 (read, nothing set); the card free"
