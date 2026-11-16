#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): the only way E200's sittings call the telemetry reader. E194's guard
# (tools/claims-v3/e194/ettelem_guard_e194.sh, unchanged beside it) with E200's words and one difference, the reader's path: E194's guard
# sits in the box tree itself and finds the reader beside its own folder; E200's sits in E200's root on the box
# (<box tree>/build/claims-v3/aifoundry2/e200, the synced files), so the reader is named from the working directory, the box tree
# (E128's guard's form: E200's session wrapper, step 7's reads and the die gate all run from the box tree). The reader is
# build/ettelem-hpl/ettelem of the box tree (~/claude/et-soc1-prototyping): E136's, E146's, E169's, E190 arm A's and E194's sampler on
# this card, the device-command audit's reviewed variant for build/ettelem-hpl; the wrapper and step 7 check its sha256 against its pin
# (77a46171...) before anything opens the card. An allow-list in front of it, so that the commands the sittings send are exactly the
# classified ones (KIT.md section 6):
#   ettelem config                                 -> GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
#                                                     GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE (all READ)
#   ettelem sample --seconds <n> --every-ms <n>    -> GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE,
#                                                     GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES (all READ), per sample
# Anything else - `sample --reset-ms` (the statistics reset), `residency`, `threshold`, `loglevel`, `sptrace`, `uptime`, any other word -
# is refused with exit 97 before the device is opened. E200's one card is aifoundry2's card 0 (E200.md 3): the box must be aifoundry2 and
# ET_DEVICES and V3_DEVICE must be UNSET (E190 arm A's and E194's form on this card; a setting of either is refused before the device
# opens). It execs the reader, so the process keeps this PID (the sampler's /proc fds are the reader's) and its name becomes `ettelem`.
# SPDX-License-Identifier: Apache-2.0
set -u
REAL=build/ettelem-hpl/ettelem
refuse() { echo "ettelem_guard_e200: refused ($*): not in E200's classified command list" >&2; exit 97; }
BOX=$(hostname 2>/dev/null | cut -d. -f1)
[ "$BOX" = aifoundry2 ] || refuse "box '$BOX': E200 runs on aifoundry2 card 0 only"
[ -z "${ET_DEVICES+set}" ] || refuse "ET_DEVICES is set ('${ET_DEVICES}'): aifoundry2's one card is opened with ET_DEVICES unset"
[ -z "${V3_DEVICE+set}" ] || refuse "V3_DEVICE is set ('${V3_DEVICE}'): aifoundry2's one card is opened with V3_DEVICE unset"
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
