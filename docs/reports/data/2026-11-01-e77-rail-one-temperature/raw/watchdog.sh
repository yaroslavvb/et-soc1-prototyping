#!/usr/bin/env bash
# E77 deadline watchdog (E72's): put TDP 65 W back if the session has not released by the deadline.
set -u
REL='<tree>/build/e77/run/release'
end=$(( $(date +%s) + 4500 ))
while [ "$(date +%s)" -lt "$end" ]; do
  [ -e "$REL" ] && { echo "$(date -Is) released by the session, nothing to do" >> '<tree>/build/e77/run/watchdog.log'; exit 0; }
  sleep 5
done
echo "$(date -Is) DEADLINE reached, restoring TDP 65 W" >> '<tree>/build/e77/run/watchdog.log'
/usr/bin/flock -w 120 '/run/lock/etsoc-shire0.lock' env LD_LIBRARY_PATH=/opt/et/lib timeout 20 /opt/et/bin/dev_mngt_service \
  -m DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -n 0 -l 65 -u 5000 >> '<tree>/build/e77/run/watchdog.log' 2>&1
echo "$(date -Is) set rc=$?" >> '<tree>/build/e77/run/watchdog.log'
env LD_LIBRARY_PATH=/opt/et/lib timeout 20 '<tree>/build/ettelem-e77/ettelem' config >> '<tree>/build/e77/run/watchdog.log' 2>&1
