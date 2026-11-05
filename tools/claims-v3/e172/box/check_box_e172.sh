#!/usr/bin/env bash
# E172 box step 3 (after the sync; no device opened): the harness and binaries, the device-command preflight, the tiles, pool 8's
# SHA256SUMS, and the dry pass on the box (a pass, the smoke, the stop-path test, as E157's boxcheck did). From the Intel:
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 'bash -s' < tools/claims-v3/e172/box/check_box_e172.sh
cd ~/nekko || exit 1
date '+%F %T %Z'
echo "== check_e172 (with the binaries)"; python3 -B tools/claims-v3/e172/check_e172.py; echo "rc=$?"
echo "== preflight"; bash tools/claims-v3/e172/preflight_e172.sh > build/e172-preflight.txt 2>&1; echo "rc=$? $(head -1 build/e172-preflight.txt)"
echo "== tiles"; python3 -B tools/claims-v3/e172/e172_common.py --verify; echo "rc=$?"
echo "== pool 8's SHA256SUMS"; ( cd tools/claims-v3/kinds/blind8 && sha256sum -c SHA256SUMS 2>&1 | grep -c ': OK$' )
echo "== dry pass 17210"; V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e172/block_e172.sh 17210 > build/e172-dry-pass.txt 2>&1; echo "rc=$? (want 0) $(grep -c 'DRY hold10' build/e172-dry-pass.txt) device calls printed"
echo "== dry smoke 17201"; V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e172/block_e172.sh 17201 --smoke > build/e172-dry-smoke.txt 2>&1; echo "rc=$? (want 0)"
echo "== dry stop-path test 17202"; V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e172/block_e172.sh 17202 --stoptest > build/e172-dry-stoptest.txt 2>&1; echo "rc=$? (a dry run ends 1: its stops need live samples)"
rm -rf build/claims-v3-dry/aifoundry1-c1/e172 build/claims-v3-dry/aifoundry1-c1/e172-smoke build/claims-v3-dry/aifoundry1-c1/e172-stoptest
timeout 20 et-who 2>&1 | tail -3
