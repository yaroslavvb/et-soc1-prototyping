#!/usr/bin/env bash
# E128 (Q136): the only way E128's blocks call the lab's telemetry reader. An allow-list in front of build/ettelem/ettelem, so that the device-management
# commands the run sends are exactly the classified ones (E128.md, "Device commands sent"; the owner's rule of Mon 2 Nov 2026: "take more care for writing
# commands"):
#   ettelem config                                  -> GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
#                                                      GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE (all READ)
#   ettelem sample --seconds <n> --every-ms <n>     -> GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE,
#                                                      GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES (all READ), per sample
# Anything else - `sample --reset-ms` (the statistics reset, SET_STATS_RUN_CONTROL), `loglevel` (SET_DM_TRACE_CONFIG), `sptrace`, any other word - is
# refused with exit 97 before the device is opened. It execs the reader, so the process keeps this PID and its name becomes `ettelem` (lib.sh's
# ours_running and stop_sampler see it as before).
set -u
REAL=build/ettelem/ettelem
refuse() { echo "ettelem_guard: refused ($*): not in E128's classified command list" >&2; exit 97; }
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
        *) refuse "sample $*" ;;
      esac
    done
    exec "$REAL" sample ${args[@]+"${args[@]}"} ;;
  *) refuse "$@" ;;
esac
