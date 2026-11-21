#!/bin/bash
# decl-e221 (Q235) step 0d: two more read paths the frozen predictors open in the repo (MM1-v3.2's energy_v32.py reads
# tools/claims-v3/e214/proposal/src (E214's arms and tiles, its F3 tables); MM1-v3.1's t7_v31.py can read tools/claims-v3/e213/points-e213.csv),
# by git archive of the SAME commit as step 0a (work/lab-commit.txt) under the lab-git lock into work/lab/. Reads LAB only.
set -u
. <W>/out/decl-e221/scripts/env.sh
echo "start $(ts)"
BASE=$(cat "$L/work/lab-commit.txt")
for p in tools/claims-v3/e214 tools/claims-v3/e213/points-e213.csv; do
  if [ -e "$L/work/lab/$p" ]; then echo "$p exists already: skipped"; continue; fi
  flock -w 600 "$W/locks/lab-git.lock" nice -n 10 ionice -c 3 git -C "$LAB" archive --format=tar "$BASE" "$p" | tar -x -C "$L/work/lab"
  echo "$p archive rc ${PIPESTATUS[0]}: $(find "$L/work/lab/$p" -type f | wc -l) files; last change $(git -C "$LAB" log -1 --format='%h %ci' "$BASE" -- "$p")"
done
echo "end $(ts)"
