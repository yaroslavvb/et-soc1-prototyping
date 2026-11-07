#!/bin/bash
# Q153(m10acc): one tile's trace (called by run_traces_m10acc.sh): <type> <sha256> <N1,N2,...>
# SPDX-License-Identifier: Apache-2.0
t=$1; sha=$2; ns=$3
[ -s "out/$sha.json" ] && exit 0
./acctrace_m10acc "$t" "tiles/$sha.bin" "$ns" > "out/$sha.json.part" && mv "out/$sha.json.part" "out/$sha.json"
