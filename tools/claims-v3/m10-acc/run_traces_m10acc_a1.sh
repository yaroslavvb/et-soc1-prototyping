#!/bin/bash
# Q153(m10acc), dated amendment A1: the x_lane traces on the mini, as run_traces_m10acc.sh, into out-a1/:
#   run_remote --host mini --max-gb 4 --timeout 900 --cd <job dir> -- bash run_traces_m10acc_a1.sh joblist.txt 6
# SPDX-License-Identifier: Apache-2.0
set -u
list=${1:?job list}
workers=${2:-6}
if [ ! -x ./acctrace_m10acc_a1 ]; then
  cc -O2 -std=gnu11 -ffp-contract=off '-DACCUM_C="accum.c"' -o acctrace_m10acc_a1 acctrace_m10acc_a1.c -lm || exit 3
fi
mkdir -p out-a1
xargs -P "$workers" -n 3 bash one_trace_m10acc_a1.sh < "$list"
done_n=$(ls out-a1 | grep -c '\.json$')
all_n=$(grep -c . "$list")
echo "TRACES A1: $done_n of $all_n tiles written"
