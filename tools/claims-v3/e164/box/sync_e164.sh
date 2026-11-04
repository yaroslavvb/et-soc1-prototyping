#!/usr/bin/env bash
# E164 box step 2, run ON THE INTEL from the top of the lab tree (after the approvals): copy E164's files into aifoundry1's ~/nekko (an
# rsynced copy, no git). Only new files: tools/claims-v3/e164/ and pool 7; pool 6 and Q139(k)'s ccheck/ are already there from E157 and
# are checked by sha256 on the box (check_e164.py), never overwritten here. No compiled source changes, so nothing is rebuilt.
#   bash tools/claims-v3/e164/box/sync_e164.sh
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." || exit 1
R="ssh -o BatchMode=yes -o ConnectTimeout=10"
rsync -a --exclude __pycache__ --exclude dry/ -e "$R" tools/claims-v3/e164/ aifoundry1:nekko/tools/claims-v3/e164/ || { echo "rsync e164 failed"; exit 1; }
rsync -a --exclude __pycache__ -e "$R" tools/claims-v3/kinds/blind7/ aifoundry1:nekko/tools/claims-v3/kinds/blind7/ || { echo "rsync blind7 failed"; exit 1; }
echo "synced: tools/claims-v3/e164/ and tools/claims-v3/kinds/blind7/"
