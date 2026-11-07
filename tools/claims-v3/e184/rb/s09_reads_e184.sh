#!/usr/bin/env bash
# E184 (Q153), kit note 1 (../KIT.md.dated-note-1.md section 3), step 7: an arm's reads before its session, READ only: et-lab-manifest (sysfs
# and files; it never opens /dev/et*) kept on the box, the card's static config through the arm's telemetry guard (`ettelem config` only, under
# the card's lock, timeout 10), and et-who's holder rule. Arm S: ../../q141k-runbook/k6/s09_a3_reads_k6.sh's lines, unchanged (aifoundry3 card
# 0 must read TDP 0 W / 65 C / 600 MHz). Arm B: the same on aifoundry1 card 1 (V3_DEVICE=1, ET_DEVICES=1, lock etsoc-shire1) through E184's
# guard: 600 MHz required, its TDP and threshold recorded as read (its own, never set), in $RB_OUT/config-B-reads.json.
#
#   bash tools/claims-v3/e184/rb/s09_reads_e184.sh S|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e184.sh"
rb_init s09_reads
e184_arm "${1:-}" || rb_die $RB_E_USAGE "usage: s09_reads_e184.sh S|B"
rb_probe "$E184_BOX"
f=$(rb_file reads)
{ rb_prelude "$E184_BOX"
  echo "ARMV=$E184_ARM"
  cat <<'EOF2'
export LD_LIBRARY_PATH=/opt/et/lib
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: the config read waits (it opens the card)"; exit 3; fi
mkdir -p build/q141k
et-lab-manifest | tee build/q141k/et-lab-manifest-$(date +%Y%m%dT%H%M%S).txt
if [ "$ARMV" = S ]; then
  unset V3_DEVICE ET_DEVICES
  c=$(flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>/dev/null | grep '^{' | tail -1)
else
  export V3_DEVICE=1 ET_DEVICES=1
  c=$(flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e184/ettelem_guard_e184.sh config < /dev/null 2>/dev/null | grep '^{' | tail -1)
fi
echo "CONFIG $c"
hold_read
echo "HOLDER-RULE: $([ "$FREE" -eq 1 ] && echo FREE || echo HELD)"
EOF2
} > "$f"
rb_remote read "$E184_BOX" "et-lab-manifest, the card config read through the guard, et-who" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_refused
cfg=$(rb_val '^CONFIG (\{.*\})$')
[ -n "$cfg" ] || rb_die $RB_E_GATE "no config read came back (the lock was held, or the guard refused): read the output above"
if [ "$E184_ARM" = S ]; then
  echo "$cfg" | grep -q '"tdp_w":0,' && echo "$cfg" | grep -q '"temp_threshold_c":65,' && echo "$cfg" | grep -q '"minion_mhz":600,' ||
    rb_die $RB_E_GATE "aifoundry3's config is not TDP 0 W / 65 C / 600 MHz: $cfg"
else
  echo "$cfg" | grep -q '"minion_mhz":600,' || rb_die $RB_E_GATE "aifoundry1 card 1's config is not 600 MHz: $cfg"
  echo "$cfg" > "$RB_OUT/config-B-reads.json"
fi
rb_has '^HOLDER-RULE: FREE' || rb_die $RB_E_AGAIN "et-who is not clean on $E184_BOX: look again (s05_look_k6.sh $E184_BOX --wait)"
rb_say "$E184_BOX: manifest kept on the box (build/q141k/), config read ($([ "$E184_ARM" = S ] && echo 'TDP 0 W / 65 C / 600 MHz' || echo '600 MHz; its TDP and threshold recorded')), et-who clean"
