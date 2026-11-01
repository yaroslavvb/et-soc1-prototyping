#!/usr/bin/env bash
# E118 deadline watchdog: put card 0's TDP back to 65 W unless the session released it first.
set -u
REL='/home/yaroslavvb/nekko/build/e118/release'; LOG='/home/yaroslavvb/nekko/build/e118/watchdog.log'
end=$(( $(date +%s) + 4500 ))
while [ "$(date +%s)" -lt "$end" ]; do
  [ -e "$REL" ] && { echo "$(date -Is) released by the session, nothing to do" >> "$LOG"; exit 0; }
  sleep 10
done
echo "$(date -Is) DEADLINE reached, restoring card 0's TDP 65 W" >> "$LOG"
stop=$(( $(date +%s) + 21600 ))
while [ "$(date +%s)" -lt "$stop" ]; do
  [ -e "$REL" ] && { echo "$(date -Is) released meanwhile" >> "$LOG"; exit 0; }
  /usr/bin/flock -w 120 '/run/lock/etsoc-shire0.lock' /usr/bin/flock -w 120 '/run/lock/etsoc-shire1.lock' env LD_LIBRARY_PATH=/opt/et/lib timeout 20 /opt/et/bin/dev_mngt_service \
    -m DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -n 0 -l 65 -u 5000 >> "$LOG" 2>&1 < /dev/null
  echo "$(date -Is) set rc=$?" >> "$LOG"
  got=$(/usr/bin/flock -w 120 '/run/lock/etsoc-shire0.lock' env LD_LIBRARY_PATH=/opt/et/lib ET_DEVICES=0 timeout 20 '/home/yaroslavvb/nekko/build/ettelem-e118/ettelem' config 2>/dev/null < /dev/null | grep '^{' | tail -1)
  echo "$(date -Is) read back: $got" >> "$LOG"
  case "$got" in *'"tdp_w":65,'*) echo "$(date -Is) restored" >> "$LOG"; touch "$REL"; exit 0 ;; esac
  sleep 30
done
echo "$(date -Is) GAVE UP after 6 h" >> "$LOG"
