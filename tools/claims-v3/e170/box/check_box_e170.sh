#!/usr/bin/env bash
# E170 box step 3 (after the sync; NO device opened): the harness and binaries, the device-command preflight, the tiles and frozen inputs, pool 7's
# SHA256SUMS, and a dry pass on the box (the toy card: the die stop-path test and the smoke, run_e170.py --dry). Never during a session of ours on
# aifoundry1. From the Intel (box/step_e170.sh check):
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 'bash -s' < tools/claims-v3/e170/box/check_box_e170.sh
# SPDX-License-Identifier: Apache-2.0
cd ~/nekko || exit 1
date '+%F %T %Z'
echo "== check_e170 (harness + binaries)"; python3 -B tools/claims-v3/e170/check_e170.py; echo "rc=$?"
echo "== preflight"; bash tools/claims-v3/e170/preflight_e170.sh > build/e170-preflight.txt 2>&1; echo "rc=$? $(grep -m1 '^dmcmd_audit:' build/e170-preflight.txt)"
echo "== tiles and frozen inputs"; python3 -B tools/claims-v3/e170/e170_common.py | head -2; echo "rc=${PIPESTATUS[0]}"
echo "== pool 7's SHA256SUMS: $( (cd tools/claims-v3/kinds/blind7 && sha256sum -c SHA256SUMS 2>&1 | grep -c ': OK$') ) OK (want 91)"
echo "== dry pass on the box (the toy card; no device)"
rm -rf build/e170-dry; mkdir -p build/e170-dry
ET_DEVICES=0 V3_DEVICE=0 timeout 120 python3 -B tools/claims-v3/e170/run_e170.py --protocol tools/claims-v3/e170/protocol-stoptest-die-dry.json \
  --out build/e170-dry/stoptest-die --dry --only STOPTEST > build/e170-dry/stoptest-die.out 2>&1; echo "stoptest-die dry rc=$? (want 4)"
ET_DEVICES=0 V3_DEVICE=0 timeout 180 python3 -B tools/claims-v3/e170/run_e170.py --protocol tools/claims-v3/e170/protocol-dry.json \
  --out build/e170-dry/smoke --dry --only SMOKE > build/e170-dry/smoke.out 2>&1; echo "smoke dry rc=$? (want 0)"
ET_DEVICES=0 V3_DEVICE=0 timeout 60 python3 -B tools/claims-v3/e170/run_e170.py --protocol tools/claims-v3/e170/protocol.json --out build/e170-dry/list \
  --dry --list > build/e170-dry/list.out 2>&1; echo "list rc=$? ($(grep -c 'BURST-' build/e170-dry/list.out) BURST runs listed; want 135)"
timeout 20 et-who 2>&1 | tail -3
