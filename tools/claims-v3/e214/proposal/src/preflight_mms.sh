#!/usr/bin/env bash
# 1118-mmsweep3: the preflight looks before a card's session (read-only: opens no device; prints counts, never a login).
#   bash ~/claude/work/ee-1118-mmsweep3/src/preflight_mms.sh <card>                the looks, then the device-command audit
#   bash ~/claude/work/ee-1118-mmsweep3/src/preflight_mms.sh <card> --audit-only   the audit alone (the runner's own call)
# The audit is the lab repo's checker (tools/claims-v3/dmcmd_audit.py with its table, copied unchanged into src/dmcmd/), with
# no --allow and no exception, on every file of the kit a session runs: it must read GO, every send site a READ.
# The looks: the host; uptime; the box's one-minute load (/proc/loadavg, recorded in run/preflight-load.txt: 6 or more is a
# NO-GO, the lab's host rule since aifoundry2's crash of 17 Nov keeps the box's load under 6); how many logins; et-who (holder
# lines by card: ours, others'; et-who --check); et-usage over 30 minutes (only when the card is free); device processes and
# CI jobs (counts); the card's lock (present, root's, not a link) and nodes; /opt/et; the kit folder's free disk; the build
# record; the harness; no session of this kit running on this box (run/box.lock free); run/STOP absent; at least 2 GB free.
# The last line is PREFLIGHT GO, or PREFLIGHT NO-GO: <reasons>.
# Run it before the build and the dry pass as well as before a claim: they too load the box's CPU.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
CARD=${1:-}
case "$CARD" in a2c0) N=0; WANT=aifoundry2 ;; a1c1) N=1; WANT=aifoundry1 ;; a1c0) N=0; WANT=aifoundry1 ;;
  *) echo "usage: preflight_mms.sh a2c0|a1c1|a1c0 [--audit-only]"; exit 2 ;; esac
audit() {
  python3 -B src/dmcmd/dmcmd_audit.py src/run_mms.py src/mms_common.py src/mms_ident.py src/session_mms.sh src/start_mms.sh \
    src/status_mms.sh src/stop_mms.sh src/build_mms.sh src/guard_ettelem.sh src/rgm136/host/main.cpp
}
if [ "${2:-}" = "--audit-only" ]; then audit; exit $?; fi
NO=""
nogo() { NO="$NO; $*"; }
BOX=$(hostname | cut -d. -f1)
echo "host $BOX (card $CARD wants $WANT); $(TZ=America/Los_Angeles date '+%F %T %Z')"
[ "$BOX" = "$WANT" ] || nogo "this is $BOX"
echo "uptime: $(uptime)"
LOAD1=$(cut -d ' ' -f 1 /proc/loadavg 2>/dev/null)
echo "load (one minute, /proc/loadavg): ${LOAD1:-unread} (NO-GO at 6 or more)"
mkdir -p run
echo "$(date +%s) $CARD ${LOAD1:-unread}" >> run/preflight-load.txt
if [ -z "$LOAD1" ]; then nogo "the box's one-minute load is unread (/proc/loadavg)"
elif awk -v l="$LOAD1" 'BEGIN { exit !(l + 0 >= 6) }'; then nogo "the box's one-minute load is $LOAD1 (6 or more: the lab's host rule)"; fi
echo "logins: $(who | wc -l)"
ME=$(id -un)
EW=$(timeout 20 et-who 2>/dev/null); EWRC=$?
timeout 20 et-who --check > /dev/null 2>&1; CHK=$?
echo "$EW" | awk -v me="$ME" -v n="$N" '
  $1 ~ /^\/dev\/et/ || $1 ~ /^lock:/ { c = $1; sub(/^\/dev\/et/, "", c); sub(/^lock:etsoc-shire/, "", c); sub(/[^0-9].*$/, "", c);
    if ($2 == me) ours[c]++; else other[c]++ }
  END { for (k = 0; k < 2; k++) printf "et-who card %d: ours %d, others %d\n", k, ours[k] + 0, other[k] + 0 }'
echo "et-who rc $EWRC; et-who --check rc $CHK (0 free, 1 held, 2 failed)"
OTHERS=$(echo "$EW" | awk -v me="$ME" -v n="$N" -v box="$BOX" '
  ($1 ~ /^\/dev\/et/ || $1 ~ /^lock:/) && $2 != me { c = $1; sub(/^\/dev\/et/, "", c); sub(/^lock:etsoc-shire/, "", c); sub(/[^0-9].*$/, "", c);
    if (box == "aifoundry2" || c == n) k++ } END { print k + 0 }')
OURS=$(echo "$EW" | awk -v me="$ME" '($1 ~ /^\/dev\/et/ || $1 ~ /^lock:/) && $2 == me { k++ } END { print k + 0 }')
[ "$OTHERS" -eq 0 ] || nogo "$OTHERS holder line(s) of another login on the card"
[ "$OURS" -eq 0 ] || nogo "$OURS holder line(s) of ours (a session or a tool of ours holds a card on this box)"
if [ "$CHK" -eq 0 ]; then
  EU=$(timeout 30 et-usage --since 30m 2>/dev/null)
  echo "et-usage --since 30m: $(printf '%s\n' "$EU" | grep -c .) line(s), $(printf '%s\n' "$EU" | grep -Ec "et${N}_|shire${N}") naming card $N (lines not printed: they name logins)"
fi
DEV=$(ps -eo uid=,comm= | awk -v u="$(id -u)" '$2 ~ /(_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$)/ { if ($1 == u) o++; else x++ }
  END { printf "%d %d", o + 0, x + 0 }')
CI=$(ps -eo comm= | grep -c '^Runner\.Worker$')
echo "device processes: ours ${DEV% *}, others' ${DEV#* }; CI jobs $CI"
[ "${DEV% *}" -eq 0 ] || nogo "a device process of ours runs"
[ "$CI" -eq 0 ] || nogo "a CI job runs"
[ "$BOX" = aifoundry2 ] && [ "${DEV#* }" -ne 0 ] && nogo "another user's device process runs on aifoundry2"
L=/run/lock/etsoc-shire$N.lock
if [ -f "$L" ] && [ ! -L "$L" ] && [ "$(stat -c %U "$L")" = root ]; then echo "the card's lock $L: present, root's"
else nogo "the card's lock $L is missing, a link, or not root's"; fi
for k in ops mgmt; do [ -e "/dev/et${N}_$k" ] || nogo "no /dev/et${N}_$k"; done
[ -d /opt/et/lib ] || nogo "no /opt/et"
echo "free disk for the kit: $(df -h . | awk 'NR == 2 {print $4 " of " $2 " (" $5 " used)"}')"
FREE_KB=$(df -Pk . | awk 'NR == 2 {print $4}')
[ "${FREE_KB:-0}" -ge 2097152 ] || nogo "under 2 GB free for the kit's folder ($FREE_KB KB)"
if [ -f build/BUILD-mms.json ]; then
  python3 -B - build/BUILD-mms.json "$(TZ=America/Los_Angeles date +%F)" "$BOX" <<'PY' || nogo "the build record is not today's BUILT on this box"
import json, sys
r = json.load(open(sys.argv[1]))
print(f"build record: {r.get('day')} {r.get('verdict')} on {r.get('box')}; ET_DEVICES: {r.get('et_devices')}")
sys.exit(0 if (r.get("day"), r.get("verdict"), r.get("box")) == (sys.argv[2], "BUILT", sys.argv[3]) else 1)
PY
else nogo "no build record (run src/build_mms.sh)"; fi
python3 -B src/check_mms.py --box | tail -n 1 | grep -q '^HARNESS OK' && echo "harness: HARNESS OK" || nogo "the harness differs"
mkdir -p run
flock -n run/box.lock true || nogo "run/box.lock is held (a session, a build or a dry pass of this kit runs on this box)"
[ -e run/STOP ] && echo "run/STOP present (start_mms.sh moves it aside when no session runs)"
audit > run/preflight-audit.txt 2>&1
ARC=$?
grep '^dmcmd_audit:' run/preflight-audit.txt
[ "$ARC" -eq 0 ] && grep -q '^dmcmd_audit: GO' run/preflight-audit.txt || nogo "the device-command audit is not GO (run/preflight-audit.txt)"
if [ -z "$NO" ]; then echo "PREFLIGHT GO"; exit 0; fi
echo "PREFLIGHT NO-GO: ${NO#; }"
exit 3
