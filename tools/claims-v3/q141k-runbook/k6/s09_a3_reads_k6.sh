#!/usr/bin/env bash
# Q142(k6), step 9: aifoundry3's reads before E171's claim (E171's README, box step 9), READ only: et-lab-manifest (sysfs and files; it
# never opens /dev/et*) kept on the box, the card's static config through E128's guard (`ettelem config` only, under card 0's lock,
# timeout 10: TDP 0 W, threshold 65 C, 600 MHz as the card holds it, never set), and et-who's holder rule. v3.1's s09_a3_reads.sh,
# unchanged but for its name: E171 runs on the same card and reads the same config.
#
#   bash tools/claims-v3/q141k-runbook/k6/s09_a3_reads_k6.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s09_a3_reads
rb_probe aifoundry3
f=$(rb_file reads)
{ rb_prelude aifoundry3
  cat <<'EOF'
unset V3_DEVICE ET_DEVICES
export LD_LIBRARY_PATH=/opt/et/lib
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on aifoundry3: the config read waits (it opens card 0)"; exit 3; fi
mkdir -p build/q141k
et-lab-manifest | tee build/q141k/et-lab-manifest-$(date +%Y%m%dT%H%M%S).txt
c=$(flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>/dev/null | grep '^{' | tail -1)
echo "CONFIG $c"
hold_read
echo "HOLDER-RULE: $([ "$FREE" -eq 1 ] && echo FREE || echo HELD)"
EOF
} > "$f"
rb_remote read aifoundry3 "et-lab-manifest, the card config read through the guard, et-who" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_refused
cfg=$(rb_val '^CONFIG (\{.*\})$')
[ -n "$cfg" ] || rb_die $RB_E_GATE "no config read came back (the lock was held, or the guard refused): read the output above"
echo "$cfg" | grep -q '"tdp_w":0,' && echo "$cfg" | grep -q '"temp_threshold_c":65,' && echo "$cfg" | grep -q '"minion_mhz":600,' ||
  rb_die $RB_E_GATE "aifoundry3's config is not TDP 0 W / 65 C / 600 MHz: $cfg"
rb_has '^HOLDER-RULE: FREE' || rb_die $RB_E_AGAIN "et-who is not clean on aifoundry3: look again (s05_look_k6.sh aifoundry3 --wait)"
rb_say "aifoundry3: manifest kept on the box (build/q141k/), config TDP 0 W / 65 C / 600 MHz, et-who clean"
