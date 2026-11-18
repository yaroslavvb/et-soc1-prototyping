#!/usr/bin/env bash
# 1118-mmsweep3: the only way a session calls the telemetry reader (E190's guard form: tools/claims-v3/e190/ettelem_guard_e190.sh
# in the public lab repo). An allow-list in front of the kit's own reader build/ettelem/ettelem (built by src/build_mms.sh
# from src/ettelem, the lab repo's tools/ettelem/ettelem.cpp unchanged), so that the commands a session sends to the card's
# service processor are exactly these, every one a read:
#   guard_ettelem.sh <card> config                               GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS,
#                                                                 GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE
#   guard_ettelem.sh <card> sample --seconds <n> --every-ms <n>  GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE,
#                                                                 GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES
# Everything else (sample --reset-ms, temp, loglevel, sptrace, any other word) is refused with exit 97 before the device opens.
# sample takes exactly `--seconds S --every-ms M`, in that order: S a whole number of seconds from 1 to 86400, M a whole number
# of milliseconds from 100 to 10000 (no sign, no point, no leading zero), so the node is never polled faster than every 100 ms.
# The card must be this box's and ET_DEVICES as the card needs it: aifoundry2 a2c0, ET_DEVICES unset; aifoundry1 a1c1,
# ET_DEVICES=1; aifoundry1 a1c0, ET_DEVICES=0. It execs the reader, so the process keeps this PID.
# SPDX-License-Identifier: Apache-2.0
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
refuse() { echo "guard_ettelem: refused ($*): not in the kit's command list" >&2; exit 97; }
BOX=$(hostname 2>/dev/null | cut -d. -f1)
CARD=${1:-}
shift || true
case "$CARD:$BOX" in
  a2c0:aifoundry2) [ -z "${ET_DEVICES:-}" ] || refuse "ET_DEVICES is '${ET_DEVICES}' on aifoundry2: its one card is opened with it unset" ;;
  a1c1:aifoundry1) [ "${ET_DEVICES:-}" = 1 ] || refuse "ET_DEVICES is '${ET_DEVICES:-unset}', not 1, for card 1 of aifoundry1" ;;
  a1c0:aifoundry1) [ "${ET_DEVICES:-}" = 0 ] || refuse "ET_DEVICES is '${ET_DEVICES:-unset}', not 0, for card 0 of aifoundry1" ;;
  *) refuse "card '$CARD' on box '$BOX'" ;;
esac
R="$ROOT/build/ettelem/ettelem"
[ -x "$R" ] || refuse "no reader at build/ettelem/ettelem"
case "${1:-}" in
  config)
    [ $# -eq 1 ] || refuse "$@"
    exec "$R" config ;;
  sample)
    [ $# -eq 5 ] && [ "$2" = --seconds ] && [ "$4" = --every-ms ] || refuse "$*"
    case "$3" in ''|*[!0-9]*|0*) refuse "--seconds $3" ;; esac
    case "$5" in ''|*[!0-9]*|0*) refuse "--every-ms $5" ;; esac
    [ "${#3}" -le 5 ] && [ "$3" -le 86400 ] || refuse "--seconds $3"
    [ "${#5}" -le 5 ] && [ "$5" -ge 100 ] && [ "$5" -le 10000 ] || refuse "--every-ms $5"
    exec "$R" sample --seconds "$3" --every-ms "$5" ;;
  *) refuse "$@" ;;
esac
