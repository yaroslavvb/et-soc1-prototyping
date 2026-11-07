#!/bin/bash
# Q153(m10acc): the traces on the mini (REGISTRATION.md section 8). Run in a job directory holding acctrace_m10acc.c, accum.c
# (rtl-sim/fma_toggle_v2/accum.c, unchanged), one_trace_m10acc.sh, tiles/<sha256>.bin and a job list (lines: type sha256 N1,N2,...):
#   run_remote --host mini --max-gb 4 --timeout 900 --cd <job dir> -- bash run_traces_m10acc.sh joblist.txt 6
# Each tile writes out/<sha256>.json once; a tile already written is skipped, so the call is repeated until every tile has one.
# SPDX-License-Identifier: Apache-2.0
set -u
list=${1:?job list}
workers=${2:-6}
if [ ! -x ./acctrace_m10acc ]; then
  cc -O2 -std=gnu11 -ffp-contract=off '-DACCUM_C="accum.c"' -o acctrace_m10acc acctrace_m10acc.c -lm || exit 3
fi
mkdir -p out
xargs -P "$workers" -n 3 bash one_trace_m10acc.sh < "$list"
done_n=$(ls out | grep -c '\.json$')
all_n=$(grep -c . "$list")
echo "TRACES: $done_n of $all_n tiles written"
