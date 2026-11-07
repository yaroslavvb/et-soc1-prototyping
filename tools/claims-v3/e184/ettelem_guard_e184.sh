#!/usr/bin/env bash
# E184 (Q153, the kit): the only way arm B's block calls the lab's telemetry reader. tools/claims-v3/e128/ettelem_guard.sh's allow-list,
# unchanged, plus one word: `sample --reset-ms 1000`, the statistics reset the owner ruled on (31 October 2026; SET_STATS_RUN_CONTROL,
# type 1 control 2, STATS_RESET in dmcmd_table.json), which arm B's pass 18441 alone sends (block_e184b.sh). Any other value of
# --reset-ms is refused. So the commands are exactly E184.md section 4's:
#   ettelem config                                         -> GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
#                                                             GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE (all READ)
#   ettelem sample --seconds <n> --every-ms <n>            -> GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE,
#                                                             GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES (all READ), per sample
#   ettelem sample --seconds <n> --every-ms <n> --reset-ms 1000   -> the same, plus the statistics reset once a second
# Anything else (`loglevel`, `sptrace`, any other word or value) is refused with exit 97 before the device is opened. It execs the
# reader, so the process keeps this PID and its name becomes `ettelem` (lib.sh's ours_running and stop_sampler see it as before).
# SPDX-License-Identifier: Apache-2.0
set -u
REAL=build/ettelem/ettelem
refuse() { echo "ettelem_guard_e184: refused ($*): not in E184's classified command list" >&2; exit 97; }
case "${1:-}" in
  config)
    [ $# -eq 1 ] || refuse "$@"
    exec "$REAL" config ;;
  sample)
    shift
    args=()
    while [ $# -gt 0 ]; do
      case "$1" in
        --seconds|--every-ms)
          [ $# -ge 2 ] || refuse "$1 without a value"
          case "$2" in ''|*[!0-9.]*) refuse "$1 $2" ;; esac
          args+=("$1" "$2"); shift 2 ;;
        --reset-ms)
          [ $# -ge 2 ] && [ "$2" = 1000 ] || refuse "--reset-ms ${2:-}: only 1000"
          args+=("$1" "$2"); shift 2 ;;
        *) refuse "sample $*" ;;
      esac
    done
    exec "$REAL" sample ${args[@]+"${args[@]}"} ;;
  *) refuse "$@" ;;
esac
