#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): the device-command preflight. E192's preflight
# (tools/claims-v3/e192/preflight_e192.sh, unchanged beside it) over E199's chain: Q136(w)'s checker tools/claims-v3/dmcmd_audit.py with
# NO --allow (no WRITE of any kind, not even the statistics reset) and no exception, over every file whose commands E199's day sends to
# card 1, read twice. The table is the lab's stock table (et-platform 836a4ab, BL2 0.22.0, "the version all four lab cards report since
# 27-31 Oct 2026"; card 1's running build is E82's read of record of 31 Oct 2026, carried by continuity while aifoundry1 has not booted
# since: the reboot gate):
#   1. THE PLAIN CHAIN, with the stock table (tools/claims-v3/dmcmd_table.json): the session's wrapper, the kit's gate and its identity
#      module (session_e199.sh, gate_e199.py, ident_e199.py, and E191's e191_ident.py, which reads /proc and runs et-who), the config read's
#      guard (ettelem_guard_e199.sh: `ettelem config` only), E192's reference session as committed (run_session.sh: the sampler
#      `"$ETTELEM" sample --seconds --every-ms 100`; run_block.py: the heater and the host; stopwatch.py), the host's source
#      (proposal/src/host/main.cpp: the ops node only) and E78's heater's source (workloads/sparsity/host/main.cpp: the ops node only).
#      et-who reads /proc and sends no command. Every session needs this GO.
#   2. THE PER-SENSOR CHAIN: the same files and E89's per-sensor sampler (tools/claims-v3/e89/pvt_sample.py, the tables' reviewed raw
#      client: six READs a tick and command 74 group 0), with E144's table (tools/claims-v3/e144/dmcmd_table_e144.json: the stock table
#      with command 74 group 0 READ, with the residual E144's README states). The stock table leaves command 74 UNCLASSIFIED: read with it,
#      this chain is NO-GO at that one command and nowhere else (printed too). The session takes SAMPLER=pvt only when this chain is GO and
#      the probe answers; else the plain sampler (E192.md section 4's fallback, E199.md section 4).
# Run from the repository's top (at the desk) or from E199's root on the box (R, which holds the same paths). Prints PLAIN-CHAIN and
# PVT-CHAIN verdict lines last. Exit 0 = the plain chain GO; 3 = NO-GO; 2 = a usage error.
#   bash tools/claims-v3/e199/preflight_e199.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
F=(tools/claims-v3/e199/session_e199.sh tools/claims-v3/e199/gate_e199.py tools/claims-v3/e199/ident_e199.py
   tools/claims-v3/e199/ettelem_guard_e199.sh tools/claims-v3/e191/e191_ident.py
   tools/claims-v3/e192/proposal/src/run_session.sh tools/claims-v3/e192/proposal/src/run_block.py
   tools/claims-v3/e192/proposal/src/stopwatch.py tools/claims-v3/e192/proposal/src/host/main.cpp
   workloads/sparsity/host/main.cpp)
echo "== 1. the plain chain, the stock table (tools/claims-v3/dmcmd_table.json), no --allow, no --except"
python3 tools/claims-v3/dmcmd_audit.py "${F[@]}"; r1=$?
echo "== 2. the per-sensor chain, E144's table (tools/claims-v3/e144/dmcmd_table_e144.json), no --allow, no --except"
python3 tools/claims-v3/dmcmd_audit.py --table tools/claims-v3/e144/dmcmd_table_e144.json "${F[@]}" tools/claims-v3/e89/pvt_sample.py; r2=$?
echo "== 2b. the per-sensor chain read with the stock table (for the record: command 74 is UNCLASSIFIED there)"
python3 tools/claims-v3/dmcmd_audit.py -q "${F[@]}" tools/claims-v3/e89/pvt_sample.py; r3=$?
v() { [ "$1" -eq 0 ] && echo GO || echo "NO-GO (rc $1)"; }
echo "PLAIN-CHAIN: $(v $r1) (the stock table)"
echo "PVT-CHAIN: $(v $r2) (E144's table); with the stock table: $(v $r3)"
[ "$r1" -eq 0 ] && exit 0
[ "$r1" -eq 2 ] && exit 2
exit 3
