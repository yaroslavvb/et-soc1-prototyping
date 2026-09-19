#!/usr/bin/env bash
# Log ET-SoC-1 board power as CSV lines "epoch_ms,watts" until killed.
#
#   scripts/et-power-log.sh [device=0] [interval_s=0.1] > power.csv
#
# Each sample is one DM_CMD_GET_MODULE_POWER query to the service processor through
# /dev/et<N>_mgmt, which takes about 15 ms. The mgmt node allows only one opener, so
# quit et-powertop (or any other dev_mngt_service user) first. The benchmark
# launchers only open /dev/et<N>_ops, so they run alongside this logger.
set -u
dev=${1:-0}
interval=${2:-0.1}
dms=${ET:-/opt/et}/bin/dev_mngt_service

echo "epoch_ms,watts"
while :; do
  t=$(date +%s%3N)
  w=$("$dms" -m DM_CMD_GET_MODULE_POWER -n "$dev" -u 2000 2>&1 |
      sed -n 's/.*Module Power Output: \([0-9.]*\) W.*/\1/p')
  if [ -n "$w" ]; then
    echo "$t,$w"
  fi
  sleep "$interval"
done
