#!/usr/bin/env bash
# E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum; E209's kit's rb/s05_look_e209.sh form): runbook step 4, THE LOOK, right after THE QUIET DESK FLAG is raised
# (it refuses, 10, unless the flag is up and the card lane's) and AFTER step 5's sync on a new box root (E209's kit note 1, section 4: the
# look runs fwgate.py from the box root, which only the sync fills). Reads only; opens no device: the reboot gate's look at the desk (fwgate.py
# look: no device), et-who and et-who --check (counts by card, never a login), the device processes and CI jobs (counts), THE P2 COUNT,
# the box root's lock, the card's lock file, the load. Writes RB_OUT/look.txt.
#   RB_OUT=... E216_ROOT=... RB_QUIET=... RB_LANE=... bash tools/claims-v3/e216/rb/s05_look_e216.sh [--wait]
# Exits: 0 FREE (and the reboot gate's look: CONTINUITY or NEEDS-READ, said); 15 a holder or a device process (--wait: re-read every
# 20 s for up to 520 s first; then call again, at most 30 minutes in all, else no card that day); 16 the reboot gate's look reads STOPPED
# or NO-RECORD (no card command on this boot: tell the orchestrator); 17 THE P2 COUNT is not 0 or a session of the kit runs (call again).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e216.sh"
rb_init s05_look
e216_window
e216_quiet_ours
rb_root
OUTF="$RB_OUT/look.txt"
end=$(( $(rb_now) + E216_BOUND_S ))
while :; do
  : > "$OUTF"
  say() { echo "$*"; echo "$*" >> "$OUTF"; }
  say "look $(rb_pst); uptime: $(uptime)"
  FW=$(e216_fwgate look --box aifoundry2 --card 0 2>&1); FWRC=$?
  say "the reboot gate's look (fwgate.py look, no device): rc $FWRC: $(echo "$FW" | tail -n 1)"
  [ "$FWRC" -eq 16 ] && rb_die 16 "the reboot gate's look: $(echo "$FW" | tail -n 1): no card command on this boot"
  [ "$FWRC" -eq 0 ] || [ "$FWRC" -eq 17 ] || rb_die 16 "the reboot gate's look ended rc $FWRC"
  ME=$(id -un)
  EW=$(timeout 20 et-who 2>/dev/null); EWRC=$?
  timeout 20 et-who --check > /dev/null 2>&1; CHK=$?
  OURS=$(echo "$EW" | awk -v me="$ME" '($1 ~ /^\/dev\/et/ || $1 ~ /^lock:/) && $2 == me {n++} END {print n+0}')
  OTH=$(echo "$EW" | awk -v me="$ME" '($1 ~ /^\/dev\/et/ || $1 ~ /^lock:/) && $2 != me {n++} END {print n+0}')
  say "et-who rc $EWRC: holder lines ours $OURS, others' $OTH; et-who --check rc $CHK (0 free, 1 held, 2 failed)"
  DEV=$(ps -eo uid=,comm= | awk -v u="$(id -u)" -v re="$DEV_COMM" '$2 ~ re { if ($1 == u) o++; else x++ } END { printf "%d %d", o + 0, x + 0 }')
  CI=$(ps -eo comm= | grep -c '^Runner\.Worker$')
  say "device processes: ours ${DEV% *}, others' ${DEV#* }; CI jobs $CI"
  p2_count >> "$OUTF"; tail -n 1 "$OUTF"
  L=/run/lock/etsoc-shire0.lock
  if [ -f "$L" ] && [ ! -L "$L" ]; then say "the card's lock $L: present"; else rb_die 16 "the card's lock $L is missing or a link"; fi
  BOXFREE=yes; e216_box_free || BOXFREE=no
  say "the box root's lock run/box.lock free: $BOXFREE"
  [ "$BOXFREE" = yes ] || rb_die 17 "a session, a build or a dry pass of the kit runs in the box root: call again"
  [ "$P2_N" -eq 0 ] || rb_die 17 "THE P2 COUNT is $P2_N: call again (never kill one)"
  if [ "$OTH" -eq 0 ] && [ "$OURS" -eq 0 ] && [ "$CHK" -eq 0 ] && [ "${DEV#* }" -eq 0 ] && [ "${DEV% *}" -eq 0 ] && [ "$CI" -eq 0 ]; then
    say "FREE"
    rb_ok "FREE; the reboot gate: $( [ "$FWRC" -eq 0 ] && echo CONTINUITY || echo NEEDS-READ)"
  fi
  [ "${1:-}" = --wait ] && [ "$(rb_now)" -lt "$end" ] || rb_die 15 "the card is not free (holder lines ours $OURS, others' $OTH; et-who --check $CHK; device processes ${DEV% *}/${DEV#* }; CI $CI): call again"
  sleep 20
done
