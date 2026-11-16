#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum), the box step "the reads" (this file is s09): k6's reads
# (tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh) on aifoundry1 for card 1, READ only, in E191's form (tools/claims-v3/e191/rb/
# s09_a1_reads_e191.sh, unchanged beside it): ET_DEVICES=1 (and V3_DEVICE=1) exported and card 1's lock taken for the read, never card 0's.
# E199's one change, made before anything else (the round's lesson of Sun 15 Nov 2026: "step 7's config read only after the rest opens"):
#   0. THE REST RULE first (rb/rest_rule_e199.sh, the lines step 9 sends): the config read is a card command, so it is refused (10, nothing
#      read) until 40 minutes after our last real session on aifoundry1, either card;
# then E191's reads:
#   - et-lab-manifest (sysfs and files; it never opens /dev/et*), kept on the box under build/q141k/;
#   - card 1's static config through E199's guard (E199's root, tools/claims-v3/e199/ettelem_guard_e199.sh: `ettelem config` only,
#     aifoundry1 and ET_DEVICES=1 only), under card 1's lock (flock -n /run/lock/etsoc-shire1.lock), timeout 10, its stderr KEPT on the box
#     (build/q141k/e199-reads-config-<time>.err), read by ident_e199.py (aifoundry1's runtime line dropped wherever it falls): the step
#     requires /dev/et1_mgmt, device ID 1, TDP 65 W, threshold 65 C, minion 600 MHz and minion_mv in (450, 510) (THE IDENTITY GATE (a)'s
#     form; the session reads it again as its first card command) - never set;
#   - the holder rule on both cards (E191's, counts only).
# "No config read came back" (16) may be our own live collector holding card 1's management node for a moment: E191's brief allows ONE
# re-run of this step after the look (step 4) reads FREE again; a second, or any other 16, is no session that day.
# Card 0 is never opened: no command here names its node or its lock, and the reader opens card 1 only with ET_DEVICES=1.
#   bash tools/claims-v3/e199/rb/s09_a1_reads_e199.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e199.sh"
rb_init s09_a1_reads
e199_window
rb_need_start
rb_probe aifoundry1
f=$(rb_file reads)
{ rb_prelude aifoundry1
  echo "ER=$E199_R"
  cat "$RB_E199_DIR/rest_rule_e199.sh"
  cat <<'EOF'
export ET_DEVICES=1 V3_DEVICE=1
export LD_LIBRARY_PATH=/opt/et/lib
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on aifoundry1: the config read waits (it opens card 1)"; exit 3; fi
[ -f "$ER/tools/claims-v3/e199/ettelem_guard_e199.sh" ] || { echo "REFUSED: E199's files are not synced (step 5)"; exit 3; }
mkdir -p build/q141k
TS=$(date +%Y%m%dT%H%M%S)
et-lab-manifest > build/q141k/et-lab-manifest-$TS.txt 2>&1; echo "MANIFEST rc $? (kept on the box: build/q141k/et-lab-manifest-$TS.txt)"
ERR=build/q141k/e199-reads-config-$TS.err; OUT=build/q141k/e199-reads-config-$TS.out
flock -n /run/lock/etsoc-shire1.lock timeout 10 bash "$ER/tools/claims-v3/e199/ettelem_guard_e199.sh" config < /dev/null > "$OUT" 2> "$ERR"; echo "READ rc $?"
python3 -I -B "$ER/tools/claims-v3/e199/ident_e199.py" config "$OUT" "$ERR" | sed 's/^/IDENT-READ /'
grep -E '^(PCIe target|Physical device ID):' "$ERR" | sed 's/  */ /g; s/^/IDENT /'
W=$(timeout 20 et-who 2>&1); WRC=$?
NH=$(printf '%s\n' "$W" | awk '$1 ~ /^\/dev\/et/ || $1 ~ /^lock:/ {n++} END {print n+0}')
PO=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n+0}')
PX=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
echo "holders, both cards: et-who rc $WRC, holder lines $NH; our device processes $PO, other users' device processes $PX"
echo "HOLDER-RULE-BOTH-CARDS: $([ "$WRC" -eq 0 ] && [ "$NH" -eq 0 ] && [ "$PO" -eq 0 ] && [ "$PX" -eq 0 ] && echo FREE || echo HELD)"
EOF
} > "$f"
rb_remote read aifoundry1 "the rest rule first; then et-lab-manifest, card 1's config read through E199's guard (ET_DEVICES=1, card 1's lock, stderr kept), et-who" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_refused
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^IDENT-READ IDENT-A OK: ' || rb_die $RB_E_GATE "card 1's config read did not read OK ($(grep -m1 '^IDENT-READ ' "$RB_CAP" | cut -c1-200)): if no config came back (card 1's lock held, the guard refused, or our own live collector held the management node for a moment) and the look (step 4) reads FREE again, run this step ONCE more; a second time, or a read that names another card: no session"
rb_has '^IDENT PCIe target: /dev/et1_mgmt' && ! rb_has '^IDENT PCIe target: /dev/et0_' || rb_die $RB_E_GATE "the read's stderr does not name /dev/et1_mgmt alone: the card cannot be told: no launch"
rb_has '^IDENT Physical device ID: 1 ' && ! rb_has '^IDENT Physical device ID: [02-9]' || rb_die $RB_E_GATE "the read's stderr does not give physical device ID 1 alone: no launch"
rb_has '^HOLDER-RULE-BOTH-CARDS: FREE' || rb_die $RB_E_AGAIN "a holder or a device process on aifoundry1 (either card): look again (s05_look_e199.sh --wait)"
rb_say "aifoundry1 card 1, after the rest opened: manifest kept on the box (build/q141k/), $(grep -m1 '^IDENT-READ IDENT-A OK: ' "$RB_CAP" | cut -c23-200) (read, nothing set); both cards free"
