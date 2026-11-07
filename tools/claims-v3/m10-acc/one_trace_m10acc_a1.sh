#!/bin/bash
# Q153(m10acc), dated amendment A1: one tile's x_lane trace (called by run_traces_m10acc_a1.sh): <type> <sha256> <N1,N2,...>
# SPDX-License-Identifier: Apache-2.0
t=$1; sha=$2; ns=$3
[ -s "out-a1/$sha.json" ] && exit 0
./acctrace_m10acc_a1 "$t" "tiles/$sha.bin" "$ns" > "out-a1/$sha.json.part" && mv "out-a1/$sha.json.part" "out-a1/$sha.json"
