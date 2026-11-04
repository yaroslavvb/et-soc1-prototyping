#!/usr/bin/env bash
# E164 box step 3 (after the sync; no device opened): the harness and binaries, the device-command preflight, the tiles, pool 7's
# SHA256SUMS, and the dry pass on the box (a pass, the smoke, the stop-path test, as E157's boxcheck did). From the Intel:
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 'bash -s' < tools/claims-v3/e164/box/check_box_e164.sh
cd ~/nekko || exit 1
date '+%F %T %Z'
echo "== check_e164 (with the binaries)"; python3 -B tools/claims-v3/e164/check_e164.py; echo "rc=$?"
echo "== preflight"; bash tools/claims-v3/e164/preflight_e164.sh > build/e164-preflight.txt 2>&1; echo "rc=$? $(head -1 build/e164-preflight.txt)"
echo "== tiles"; python3 -B tools/claims-v3/e164/e164_common.py --verify; echo "rc=$?"
echo "== pool 7's SHA256SUMS"; ( cd tools/claims-v3/kinds/blind7 && sha256sum -c SHA256SUMS 2>&1 | grep -c ': OK$' )
echo "== dry pass 16410"; V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e164/block_e164.sh 16410 > build/e164-dry-pass.txt 2>&1; echo "rc=$? (want 0) $(grep -c 'DRY hold10' build/e164-dry-pass.txt) device calls printed"
echo "== dry smoke 16401"; V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e164/block_e164.sh 16401 --smoke > build/e164-dry-smoke.txt 2>&1; echo "rc=$? (want 0)"
echo "== dry stop-path test 16402"; V3_DEVICE=1 V3_DRY=1 timeout 300 bash tools/claims-v3/e164/block_e164.sh 16402 --stoptest > build/e164-dry-stoptest.txt 2>&1; echo "rc=$? (a dry run ends 1: its stops need live samples)"
rm -rf build/claims-v3-dry/aifoundry1-c1/e164 build/claims-v3-dry/aifoundry1-c1/e164-smoke build/claims-v3-dry/aifoundry1-c1/e164-stoptest
timeout 20 et-who 2>&1 | tail -3
