#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum), the box step "the reads" (this file
# is s09): k6's reads (tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh, unchanged beside it) on aifoundry1 for card 1, READ only, with
# E191's dated note 1, item 1, made in it: where k6's read runs `unset V3_DEVICE ET_DEVICES` and takes card 0's lock, this one exports
# ET_DEVICES=1 (and V3_DEVICE=1) and takes card 1's lock, E164's form (tools/claims-v3/e164/session_e164.sh, its config read):
#   - et-lab-manifest (sysfs and files; it never opens /dev/et*), kept on the box under build/q141k/;
#   - the card's static config through E191's guard (`ettelem config` only; aifoundry1 and ET_DEVICES=1 only), under card 1's lock
#     (flock -n /run/lock/etsoc-shire1.lock), `timeout 10`, its stderr KEPT on the box (build/q141k/e191-reads-config-<time>.err): the
#     identity lines (PCIe target, Physical device ID) are printed here, and the step requires /dev/et1_mgmt, device ID 1, TDP 65 W,
#     threshold 65 C, minion 600 MHz and minion_mv below 510 (note 1, item 3(a); the session's own gate reads it again) and above 450
#     (fix-e191k, the verifier's nit 11: a failed voltage read of 0 is not card 1's) - never set;
#   - the holder rule on both cards (E191's look's read, counts only).
# "No config read came back" (16) may be our own live collector holding card 1's management node for a moment (it allows one opener;
# the verifier's nit 9): the brief allows ONE re-run of this step after the look (step 4) reads FREE again; a second, or any other 16,
# is no session that day.
# Card 0 is never opened: no command here names its node or its lock, and the reader opens card 1 only with ET_DEVICES=1.
#   bash tools/claims-v3/e191/rb/s09_a1_reads_e191.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e191.sh"
rb_init s09_a1_reads
rb_probe aifoundry1
f=$(rb_file reads)
{ rb_prelude aifoundry1
  cat <<'EOF'
export ET_DEVICES=1 V3_DEVICE=1
export LD_LIBRARY_PATH=/opt/et/lib
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on aifoundry1: the config read waits (it opens card 1)"; exit 3; fi
mkdir -p build/q141k
TS=$(date +%Y%m%dT%H%M%S)
et-lab-manifest > build/q141k/et-lab-manifest-$TS.txt 2>&1; echo "MANIFEST rc $? (kept on the box: build/q141k/et-lab-manifest-$TS.txt)"
ERR=build/q141k/e191-reads-config-$TS.err
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
rb_remote read aifoundry1 "et-lab-manifest, card 1's config read through E191's guard (ET_DEVICES=1, card 1's lock, stderr kept), et-who" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_refused
cfg=$(rb_val '^CONFIG (\{.*\})$')
[ -n "$cfg" ] || rb_die $RB_E_GATE "no config read came back (card 1's lock was held, or the guard refused, or our own live collector held the management node for a moment): read the output above; if the look (step 4) reads FREE again, run this step ONCE more; a second time: no session"
echo "$cfg" | grep -qE '"tdp_w": ?65[,}]' && echo "$cfg" | grep -qE '"temp_threshold_c": ?65[,}]' && echo "$cfg" | grep -qE '"minion_mhz": ?600[,}]' ||
  rb_die $RB_E_GATE "card 1's config is not TDP 65 W / 65 C / 600 MHz: $cfg"
mv=$(echo "$cfg" | sed -nE 's/.*"minion_mv": ?([0-9]+).*/\1/p')
{ [ -n "$mv" ] && [ "$mv" -lt 510 ] && [ "$mv" -gt 450 ]; } || rb_die $RB_E_GATE "minion_mv ${mv:-none} is not between 450 and 510: this is not card 1's read (card 0 reads 519; a failed read 0): no launch"
rb_has '^IDENT PCIe target: /dev/et1_mgmt' && ! rb_has '^IDENT PCIe target: /dev/et0_' || rb_die $RB_E_GATE "the read's stderr does not name /dev/et1_mgmt alone: the card cannot be told: no launch"
rb_has '^IDENT Physical device ID: 1 ' && ! rb_has '^IDENT Physical device ID: [02-9]' || rb_die $RB_E_GATE "the read's stderr does not give physical device ID 1 alone: no launch"
rb_has '^HOLDER-RULE-BOTH-CARDS: FREE' || rb_die $RB_E_AGAIN "a holder or a device process on aifoundry1 (either card): look again (s05_look_e191.sh --wait)"
rb_say "aifoundry1 card 1: manifest kept on the box (build/q141k/), config TDP 65 W / 65 C / 600 MHz, minion_mv $mv, identity /dev/et1_mgmt and device ID 1 (read, nothing set); both cards free"
