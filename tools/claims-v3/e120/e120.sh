#!/usr/bin/env bash
# E120 (Q134) on aifoundry2 card 0, one stage per call, from the tree that holds the binaries (~/claude/et-soc1-prototyping).
# E77's e77.sh, adapted: no build stage (E120 runs E77's own heater, kernel and no-PMIC-read ettelem-e77, checked by hash).
#
#   bash tools/claims-v3/e120/e120.sh hashes    # SHA-256 of the three binaries against protocol.json; no device
#   bash tools/claims-v3/e120/e120.sh look      # et-who, logins (counts), the lock, the collector; no device
#   KTAG=before bash tools/claims-v3/e120/e120.sh kernlog   # the host kernel log's ET lines (read-only dmesg)
#   bash tools/claims-v3/e120/e120.sh gates     # G0 reads under the card lock (uptime, the two RAM GETs, the LUT floor,
#                                               #   residencies 1-3, the ring); writes $OUT/gates.json; no write
#   bash tools/claims-v3/e120/e120.sh smoke     # the sampler and one 2 s launch of 160 harts at the card's own settings
#   bash tools/claims-v3/e120/e120.sh go        # the session, detached (setsid nohup); log $OUT/session.out
#   bash tools/claims-v3/e120/e120.sh status    # the session's last lines and end.json, if any
#   WAIT_S=500 bash tools/claims-v3/e120/e120.sh wait   # one bounded wait for the session to end, then status
#
# OUT defaults to build/e120/run. Nothing here waits for a person; nothing resets, reloads or sets anything but what
# run_e120.py sets (the static TDP level: 0, then the original 65).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 1
ROOT=$PWD
T=tools/claims-v3/e120
OUT=${OUT:-$ROOT/build/e120/run}
stage=${1:?hashes|look|kernlog|gates|smoke|go|status|wait}
case "$stage" in
hashes)
  python3 -I - "$T/protocol.json" <<'PY'
import hashlib, json, sys
p = json.load(open(sys.argv[1])); want = p["binaries_sha256"]
for k, path in (("heater", p["tools"]["heater"]), ("kernel", p["tools"]["kernel"]), ("ettelem_e77", p["tools"]["ettelem"])):
    try:
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
    except OSError as e:
        h = f"unreadable: {e.strerror}"
    print(f"{k:12s} {h} {'MATCH' if h == want[k] else 'DIFFERS from ' + want[k]}")
PY
  [ -x build/ettelem-e77/ettelem ] && build/ettelem-e77/ettelem profile
  ;;
look)
  date '+%F %T %Z'; uptime
  echo "other logins: $(who | awk -v me="$(id -un)" '$1!=me' | wc -l)"
  timeout 10 et-who 2>&1 | head -5
  pgrep -af live-collector | grep -v pgrep | sed 's/ .*live-collector/ live-collector/' | head -3
  ls -la /run/lock/etsoc-shire0.lock
  grep et_soc1 /proc/modules
  ;;
gates)
  mkdir -p "$OUT"
  python3 -I $T/run_e120.py gates --out "$OUT"
  echo "gates rc=$?"
  ;;
smoke)
  mkdir -p "$OUT/smoke"
  python3 -I $T/run_e120.py smoke --out "$OUT/smoke"
  echo "smoke rc=$?"
  ;;
kernlog)
  # the host kernel log's ET lines (read-only dmesg; no device): KTAG=before|after
  mkdir -p "$OUT/logs"
  f="$OUT/logs/kernlog-${KTAG:-now}.txt"
  { date '+%F %T %Z'; cat /proc/uptime; timeout 10 dmesg 2>&1 | grep -E "Error Event|et_soc1|et-soc1|0000:02:00\.0|Syndrome|Desc" | tail -2000; } > "$f"
  echo "kernlog $f: $(grep -c 'Error Event' "$f") 'Error Event' lines, $(wc -l < "$f") lines"
  ;;
go)
  [ -s "$OUT/gates.json" ] || { echo "no $OUT/gates.json: run the gates first" >&2; exit 2; }
  [ -e "$OUT/session.json" ] && { echo "$OUT already holds a session" >&2; exit 2; }
  setsid nohup python3 -I $T/run_e120.py session --out "$OUT" --gates "$OUT/gates.json" \
    > "$OUT/session.out" 2>&1 < /dev/null &
  echo "E120 session started, pid $!, log $OUT/session.out"
  ;;
status)
  date '+%T %Z'
  tail -n "${N:-12}" "$OUT/session.out" 2>/dev/null
  [ -s "$OUT/end.json" ] && cat "$OUT/end.json"
  [ -e "$OUT/RESTORE_FAILED" ] && echo "*** RESTORE_FAILED present"
  [ -e "$OUT/watchdog.log" ] && tail -3 "$OUT/watchdog.log"
  ;;
wait)
  end=$(( $(date +%s) + ${WAIT_S:-500} ))
  while [ "$(date +%s)" -lt "$end" ] && [ ! -s "$OUT/end.json" ]; do sleep 10; done
  N=${N:-8} bash "$0" status
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
