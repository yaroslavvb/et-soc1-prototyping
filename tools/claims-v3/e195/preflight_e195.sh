#!/usr/bin/env bash
# E195's kit (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): THE DEVICE-COMMAND PREFLIGHT, Q136(w)'s checker
# tools/claims-v3/dmcmd_audit.py (unchanged, with its table dmcmd_table.json) on EVERY file E195's session runs, sources, builds or
# reads: the kit's session (session_e195.sh), its blocks (block_e195.sh, lib_e195.sh), its runner (runitems_e195.py), its checker and
# harness, its build; the registered source's lib_x09.sh, watch_x09.py, smoke_gate_x09.py, make_x09.py and the host's main.cpp and kernel;
# the lab's lib.sh, text_hash.sh and E128's guard (the only way any of them reaches the telemetry reader: `config`, and `sample` with
# --seconds and --every-ms only, refusing --reset-ms and every other word before the device opens). NO --allow. One reviewed exception,
# the lab's own for E180, E183 and the registered preflight_x09.sh: lib.sh's start_sampler (line 154) forwards its "$@" into
# `ettelem sample`, which could carry a statistics reset; block_e195.sh's sampler is lib_e195.sh's start_sampler, which forwards no
# argument, and lib.sh's is never called. The holder check (et-who --check), et-holders and the card lock send no device command.
# Run from the repository's top, or on the box from E195's root (<tree>/build/claims-v3/aifoundry3/e195, the same layout).
# Exit 0 = GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e195/preflight_e195.sh [--json | --markdown]
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
E=tools/claims-v3/e195
S=$E/proposal/src
exec python3 -B tools/claims-v3/dmcmd_audit.py "$@" \
  --except "tools/claims-v3/lib.sh:154:STATS_RESET=E195 never forwards a --reset-ms: block_e195.sh's sampler is lib_e195.sh's start_sampler, which passes the file and the duration alone; lib.sh's is overridden and never called" \
  $E/session_e195.sh $E/block_e195.sh $E/lib_e195.sh $E/runitems_e195.py $E/check_e195.py $E/harness_e195.py $E/build_e195.sh \
  $S/lib_x09.sh $S/watch_x09.py $S/smoke_gate_x09.py $S/make_x09.py $S/host/main.cpp $S/x09mem_args.h $S/kernel/x09mem.c \
  tools/claims-v3/lib.sh tools/claims-v3/text_hash.sh tools/claims-v3/e128/ettelem_guard.sh
