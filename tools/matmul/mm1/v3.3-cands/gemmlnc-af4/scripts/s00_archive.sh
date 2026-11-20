#!/bin/bash
# s00: a read-only copy of LAB's tools/ tree at its HEAD into this lane's work folder (git archive: a read of LAB's objects, nothing
# written in LAB). Under the clone and lab-git locks, nice and ionice (THE CLONE RULE's spirit; not a full clone).
set -u
W="${ROUND_DIR:?}"
L=$W/out/lnc-form
LAB="${LAB_DIR:?}"
DEST=$L/work/repo
uptime
mkdir -p "$DEST"
HEAD=$(git -C "$LAB" rev-parse HEAD)
echo "LAB HEAD $HEAD"
flock -w 1800 $W/locks/clone.lock flock -w 600 $W/locks/lab-git.lock nice -n 10 ionice -c 3 \
  git -C "$LAB" archive --format=tar "$HEAD" tools | nice -n 10 ionice -c 3 tar -x -C "$DEST"
rc=$?
echo "archive rc $rc"
echo "$HEAD" > "$DEST/ARCHIVED_FROM_LAB_HEAD.txt"
du -sh "$DEST/tools"
exit $rc
