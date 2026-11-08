#!/usr/bin/env bash
# E184 (Q154), kit note 2 (../KIT.md.dated-note-2.md section 3), step 7 v2: s09_reads_e184.sh (v1, which stays as committed) with dated
# amendment A3's A3-3 made code, and nothing else changed. The config read the step takes (the same READ, through the same telemetry guard,
# `ettelem config` only, under the card's lock, timeout 10) is also written ON THE BOX, with the box's own clock, as
# build/e184/config-<arm>-step7-<epoch>.json, and printed back ("STEP7-FILE <path>"); step 11's copy-back of build/e184/ brings it to the desk
# with the session's own files, where reduce_e184_v3.py replaces a MISSING session read by it (A3-3: the newest step-7 read in the 90 minutes
# before T0 for the start read, the oldest in the 30 minutes after the end read's attempt for the end read), as a departure.
# It runs twice an arm: as step 7, before the launch (S|B); and again right after step 10 reads this T0's session end, before the release
# (S|B after), when it also refuses unless step 9 recorded a T0 ($RB_OUT/t0-<arm>.txt) and that T0's log on the box ends
# "session end (T0 <T0>)". Like v1, it refuses beside a card session of ours. v1's reads, checks and words are otherwise unchanged:
# et-lab-manifest (sysfs and files; it never opens /dev/et*) kept on the box; arm S's config must read TDP 0 W / 65 C / 600 MHz; arm B's
# 600 MHz, its TDP and threshold recorded as read in $RB_OUT/config-B-reads.json; et-who's holder rule.
#
#   bash tools/claims-v3/e184/rb/s09_reads_e184_v2.sh S|B [after]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e184.sh"
rb_init s09_reads
e184_arm "${1:-}" || rb_die $RB_E_USAGE "usage: s09_reads_e184_v2.sh S|B [after]"
MODE=before
case "${2:-}" in "") ;; after) MODE=after ;; *) rb_die $RB_E_USAGE "usage: s09_reads_e184_v2.sh S|B [after]" ;; esac
T0V=""
if [ "$MODE" = after ]; then
  T0V=$(cat "$RB_OUT/t0-$E184_ARM.txt" 2>/dev/null)
  [ -n "$T0V" ] || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_USAGE "no T0 recorded by step 9 ($RB_OUT/t0-$E184_ARM.txt): the read after a session needs that session"
  T0V=${T0V:-T0}
fi
rb_probe "$E184_BOX"
f=$(rb_file reads)
{ rb_prelude "$E184_BOX"
  echo "ARMV=$E184_ARM; MODEV=$MODE; T0V=$T0V"
  cat <<'EOF2'
export LD_LIBRARY_PATH=/opt/et/lib
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: the config read waits (it opens the card)"; exit 3; fi
if [ "$MODEV" = after ] && ! grep -q "session end (T0 $T0V)" "build/e184/session-$ARMV-t$T0V.log" 2>/dev/null; then
  echo "REFUSED: build/e184/session-$ARMV-t$T0V.log has no 'session end (T0 $T0V)' line: step 10 first (the read after a session follows its end)"; exit 3
fi
mkdir -p build/q141k build/e184
et-lab-manifest | tee build/q141k/et-lab-manifest-$(date +%Y%m%dT%H%M%S).txt
if [ "$ARMV" = S ]; then
  unset V3_DEVICE ET_DEVICES
  c=$(flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>/dev/null | grep '^{' | tail -1)
else
  export V3_DEVICE=1 ET_DEVICES=1
  c=$(flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e184/ettelem_guard_e184.sh config < /dev/null 2>/dev/null | grep '^{' | tail -1)
fi
ep=$(date +%s)
echo "CONFIG $c"
if [ -n "$c" ]; then
  printf '%s\n' "$c" > "build/e184/config-$ARMV-step7-$ep.json"
  echo "STEP7-FILE build/e184/config-$ARMV-step7-$ep.json ($MODEV)"
fi
hold_read
echo "HOLDER-RULE: $([ "$FREE" -eq 1 ] && echo FREE || echo HELD)"
EOF2
} > "$f"
rb_remote read "$E184_BOX" "et-lab-manifest, the card config read through the guard (kept on the box as step 7's read: $MODE), et-who" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_refused
cfg=$(rb_val '^CONFIG (\{.*\})$')
[ -n "$cfg" ] || rb_die $RB_E_GATE "no config read came back (the lock was held, or the guard refused): read the output above"
s7=$(rb_val '^STEP7-FILE ([^ ]+) .*$')
[ -n "$s7" ] || rb_die $RB_E_FAIL "the config read came back but step 7's file was not written on the box: read the output above"
if [ "$E184_ARM" = S ]; then
  echo "$cfg" | grep -q '"tdp_w":0,' && echo "$cfg" | grep -q '"temp_threshold_c":65,' && echo "$cfg" | grep -q '"minion_mhz":600,' ||
    rb_die $RB_E_GATE "aifoundry3's config is not TDP 0 W / 65 C / 600 MHz: $cfg (step 7's read is kept on the box: $s7)"
else
  echo "$cfg" | grep -q '"minion_mhz":600,' || rb_die $RB_E_GATE "aifoundry1 card 1's config is not 600 MHz: $cfg (step 7's read is kept on the box: $s7)"
  echo "$cfg" > "$RB_OUT/config-B-reads.json"
fi
echo "$s7" >> "$RB_OUT/step7-$E184_ARM.txt"
rb_has '^HOLDER-RULE: FREE' || rb_die $RB_E_AGAIN "et-who is not clean on $E184_BOX: look again (s05_look_k6.sh $E184_BOX --wait)"
rb_say "$E184_BOX: manifest kept on the box (build/q141k/), config read ($([ "$E184_ARM" = S ] && echo 'TDP 0 W / 65 C / 600 MHz' || echo '600 MHz; its TDP and threshold recorded')), kept as step 7's read $s7 ($MODE$([ "$MODE" = after ] && echo ", after T0 $T0V's session end")), et-who clean"
