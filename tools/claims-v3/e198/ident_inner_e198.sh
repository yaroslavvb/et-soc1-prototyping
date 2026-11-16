#!/usr/bin/env bash
# E198's kit (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): THE IDENTITY SAMPLER, run by session_e198.sh INSIDE the private
# /dev (privdev_e198.sh) before the smoke's first device process (E198.md 3, item (b): "et-who with the sampler running"). It starts one
# sampler through the guard shim (E191's guard: `sample --seconds 10 --every-ms 100`, ET_DEVICES=1, reads only; never --reset-ms), writes
# its process ID, waits (at most 6 s) for the sampler's first sample (the management node is open then), marks it, and 1 s later asks the
# holder check from inside (holdercheck_e198.sh, through the warden) while the session reads the box's et-who outside; then it waits for
# the sampler's own 10 s end (it is never killed: it ends by its --seconds).
#   ET_DEVICES=1 bash ident_inner_e198.sh <dir> <guard shim> <holder check>
# SPDX-License-Identifier: Apache-2.0
set -u
D=${1:?the identity folder}; G=${2:?the guard shim}; HC=${3:?the holder check}
mkdir -p "$D" || exit 2
"$G" sample --seconds 10 --every-ms 100 > "$D/ident-sampler.jsonl" 2> "$D/ident-sampler.err" < /dev/null &
p=$!
echo "$p" > "$D/ident-sampler.pid"
i=0; while [ "$i" -lt 60 ] && ! grep -q '^{' "$D/ident-sampler.jsonl" 2>/dev/null; do sleep 0.1; i=$((i + 1)); done   # its first sample: the node is open
date +%s.%N > "$D/ident-first-sample"
sleep 1
"$HC" --check > "$D/ident-client.out" 2> "$D/ident-client.err" < /dev/null
echo "$?" > "$D/ident-client.rc"
wait "$p"
echo "$?" > "$D/ident-sampler.rc"
echo "IDENT-INNER done: sampler rc $(cat "$D/ident-sampler.rc"), samples $(grep -c '^{' "$D/ident-sampler.jsonl"), inside holder check rc $(cat "$D/ident-client.rc")"
