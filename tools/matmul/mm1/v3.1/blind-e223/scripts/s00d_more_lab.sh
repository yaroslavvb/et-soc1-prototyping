#!/bin/bash
# decl-e223 (Q239) step 0d: two more read paths the frozen code opens in the repo (the committed v01_map.py under
# tools/matmul/mm1/v3.2-terms/layout/controls-e215/, which posimb's f02_private.py and posimb-mask's posimb_mask.py load at import, reads
# workloads/nocbench/analyze.py (its MARTY map) and can read tools/claims-v3/e215/points-e215.csv), by git archive of the SAME commit as
# step 0a (work/lab-commit.txt) under the lab-git lock into work/lab/. Reads LAB only.
set -u
. <W>/out/decl-e223/scripts/env.sh
echo "start $(ts)"
BASE=$(cat "$L/work/lab-commit.txt")
for p in workloads/nocbench/analyze.py tools/claims-v3/e215/points-e215.csv; do
  if [ -e "$L/work/lab/$p" ]; then echo "$p exists already: skipped"; continue; fi
  flock -w 600 "$W/locks/lab-git.lock" nice -n 10 ionice -c 3 git -C "$LAB" archive --format=tar "$BASE" "$p" | tar -x -C "$L/work/lab"
  echo "$p archive rc ${PIPESTATUS[0]}: $(find "$L/work/lab/$p" -type f | wc -l) files; sha256 $(sha256sum "$L/work/lab/$p" | cut -c1-16); last change $(git -C "$LAB" log -1 --format='%h %ci' "$BASE" -- "$p")"
done
echo "end $(ts)"
