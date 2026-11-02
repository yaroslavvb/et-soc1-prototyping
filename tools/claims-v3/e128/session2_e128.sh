#!/usr/bin/env bash
# E128 (Q136), amendment A2: the second session's only access to aifoundry1 card 1. No launch, no sampler, no set: the registered session-end
# config read the first session could not make (ssh to the host was blocked from about 08:40 PST), preceded by a session-start read. Run on aifoundry1
# from ~/nekko, one call at a time:
#
#   bash tools/claims-v3/e128/session2_e128.sh look start|end     # host side only: the time, uptime, whether et-who shows aifoundry1 free, the
#                                                                 # login count, et-lab-manifest (sysfs and files; it never opens /dev/et*)
#   bash tools/claims-v3/e128/session2_e128.sh config start|end   # card 1's configuration: ettelem_guard.sh config only (commands 25, 21, 23,
#                                                                 # 53, 32, all READ at BL2 0.22.0), under card 1's lock, timeout 10
#
# `config` refuses (exit 3) unless et-who shows no process holding a device node or card lock on either card of the host. Files go to
# build/e128-logs/ (config-session2-<when>.json and .time, look-session2-<when>.txt, manifest-session2-<when>.txt). No login name is written.
set -u
cd ~/nekko || exit 9
mkdir -p build/e128-logs
M=${1:?look|config}
WHEN=${2:?start|end}
case "$WHEN" in start|end) ;; *) echo "usage: session2_e128.sh look|config start|end" >&2; exit 2 ;; esac
who_out=$(timeout 20 et-who 2>&1)
if printf '%s' "$who_out" | grep -q 'No process holds'; then free=yes; else free=no; fi
case "$M" in
  look)
    F=build/e128-logs/look-session2-$WHEN.txt
    { date '+%F %T %Z'; uptime; echo "et-who: aifoundry1 free: $free"; echo "logins: $(who | wc -l)"; } > "$F"
    timeout 30 et-lab-manifest > "build/e128-logs/manifest-session2-$WHEN.txt" 2>&1
    echo "manifest rc=$?"
    cat "$F" ;;
  config)
    [ "$free" = yes ] || { echo "NOT FREE: et-who shows a holder on aifoundry1; no read" >&2; exit 3; }
    F=build/e128-logs/config-session2-$WHEN.json
    date '+%F %T %Z' > "$F.time"
    ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config 2> "$F.err" < /dev/null \
      | grep '^{' | tail -1 > "$F"
    rc=${PIPESTATUS[0]}
    date '+%F %T %Z' >> "$F.time"
    echo "config rc=$rc"
    cat "$F" "$F.time"
    [ -s "$F" ] || { echo "no config read" >&2; head -5 "$F.err" >&2; exit 4; }
    [ "$rc" -eq 0 ] || exit 4 ;;
  *) echo "usage: session2_e128.sh look|config start|end" >&2; exit 2 ;;
esac
