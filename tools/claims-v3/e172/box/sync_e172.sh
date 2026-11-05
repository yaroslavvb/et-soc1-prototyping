#!/usr/bin/env bash
# E172 box step 2, run ON THE INTEL from the top of the lab tree (after the approvals): copy E172's files into aifoundry1's ~/nekko (an
# rsynced copy, no git). Only new files: tools/claims-v3/e172/, pool 8 and the three pinned watcher files; Q139(k)'s ccheck/ is already there from E164 and
# are checked by sha256 on the box (check_e172.py), never overwritten here. No compiled source changes, so nothing is rebuilt.
#   bash tools/claims-v3/e172/box/sync_e172.sh
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." || exit 1
R="ssh -o BatchMode=yes -o ConnectTimeout=10"
rsync -a --exclude __pycache__ --exclude dry/ -e "$R" tools/claims-v3/e172/ aifoundry1:nekko/tools/claims-v3/e172/ || { echo "rsync e172 failed"; exit 1; }
rsync -a --exclude __pycache__ -e "$R" tools/claims-v3/kinds/blind8/ aifoundry1:nekko/tools/claims-v3/kinds/blind8/ || { echo "rsync blind8 failed"; exit 1; }
rsync -a -R -e "$R" tools/claims-v3/hpl/watcher_q142s.py tools/claims-v3/hpl/run_hpl.py.dated-note.md tools/claims-v3/hpl/run_hpl.py.dated-note-2.md aifoundry1:nekko/ || { echo "rsync watcher files failed"; exit 1; }
echo "synced: tools/claims-v3/e172/, tools/claims-v3/kinds/blind8/ and the three pinned watcher files"
