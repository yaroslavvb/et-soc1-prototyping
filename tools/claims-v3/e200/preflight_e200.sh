#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): the device-command preflight, the audit v2's checker
# tools/claims-v3/dmcmd_audit_v2.py with its table (tools/claims-v3/dmcmd_table_v2.json: the firmware-revisions query READ by the owner's
# rulings of Sun 15 Nov 2026, 15:07:01 and 15:09:49 PST), NO --allow (no WRITE of any kind, not even the statistics reset) and NO --except,
# over every file whose commands E200's sittings send to the card or its management node (E200.md 8 and 19.2):
#   - the kit's session wrapper, watch, checker, build and harness (session_e200.sh, watch_e200.py, check_e200.py, build_e200.sh,
#     harness_e200.py: they send nothing themselves but through E200's guard; the build runs the host only to refusals before the device
#     layer); the wrapper's die gate reads the shires' mean through E200's guard (`sample --seconds 1 --every-ms 200`);
#   - E197's reference session as registered: proposal/src/run_session.sh (the one sampler, "$ETTELEM" sample --seconds T --every-ms 100,
#     ETTELEM being E200's guard below; et-who --check; flock on the existing lock file), proposal/src/stopwatch.py (reads the telemetry
#     file), and E197's lab runner lab/run_trains.py (departure D1: `timeout 10` around every host process), from which E200's runner is
#     made by W1 (two "--window" words changed: no command added or changed, E200.md 4);
#   - the host's and the kernel's source (E197's proposal/src/host/main.cpp: createPcieDeviceLayer(true, false), the ops node only;
#     proposal/src/regfile_args.h; proposal/src/kernel/regfile.c);
#   - E200's guard (tools/claims-v3/e200/ettelem_guard_e200.sh): the session's sampler and the die gate (`sample --seconds --every-ms`
#     only) and step 7's config read (`config` only), the reader build/ettelem-hpl/ettelem (the table's reviewed variant for that build
#     folder); it refuses --reset-ms and every other word, any box but aifoundry2 and any ET_DEVICES or V3_DEVICE setting, before the
#     device opens;
#   - E194's common module (tools/claims-v3/e194/e194_common.py: step 7 reads the config read's object with its --config-line; it sends
#     nothing);
#   - the lab's firmware gate (tools/claims-v3/fwgate/fwgate.py: look and guard send nothing; read sends DM_CMD_GET_MODULE_FIRMWARE_REVISIONS
#     once, a READ in the table v2, id 14, only on a boot later than the card's newest record, never again on that boot once a read has not
#     ended EQUAL).
# et-who reads /proc (et-holders: fuser stats the nodes, never opens them) and sends no device command.
# Run from the repository's top (at the desk) or from E200's root on the box (which holds the same paths). Prints the checker's lines, then
# "dmcmd_audit: GO ..." on its first line (the checker's own). Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e200/preflight_e200.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
F=(tools/claims-v3/e200/session_e200.sh tools/claims-v3/e200/watch_e200.py tools/claims-v3/e200/check_e200.py
   tools/claims-v3/e200/build_e200.sh tools/claims-v3/e200/harness_e200.py tools/claims-v3/e200/ettelem_guard_e200.sh
   tools/claims-v3/e197/proposal/src/run_session.sh tools/claims-v3/e197/proposal/src/stopwatch.py tools/claims-v3/e197/lab/run_trains.py
   tools/claims-v3/e197/proposal/src/host/main.cpp tools/claims-v3/e197/proposal/src/regfile_args.h
   tools/claims-v3/e197/proposal/src/kernel/regfile.c tools/claims-v3/e194/e194_common.py tools/claims-v3/fwgate/fwgate.py)
python3 tools/claims-v3/dmcmd_audit_v2.py "${F[@]}"
