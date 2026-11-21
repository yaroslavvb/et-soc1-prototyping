#!/bin/bash
# mask-mesh (Q238) s00: a read-only snapshot of the files this lane reads, from the shared lab clone at ONE commit (GitHub main at the
# lane's start, cfd7e641: E222's data commit), by 'git archive' (a git READ; no checkout, no fetch, nothing written in LAB). The lab-git
# lock is held for the read only. Output: work/lab/ (the repository's layout for the archived paths) and work/lab-SNAPSHOT.txt.
set -u
W=<W>
LAB=<LAB>
L=$W/out/mask-mesh
C=cfd7e6415d0da2af17c8078ea68a7bac8acd5c5b
mkdir -p "$L/work/lab"
PATHS=(
  tools/matmul/mm1
  tools/claims-v3/e220/score_e220.py
  tools/claims-v3/e220/points-e220.json
  tools/claims-v3/e222/points-e222.json
  tools/claims-v3/e224/points-e224.json
  tools/claims-v3/e208/proposal/src/reduce_mms.py
  docs/reports/data/2026-11-20-e220-blind-matmul-aifoundry1-c1/scores-e220-A.json
  docs/reports/data/2026-11-20-e220-blind-matmul-aifoundry2/scores-e220.json
  docs/reports/data/2026-11-21-e222-blind-matmul-aifoundry3/data-e222.json
  docs/reports/data/2026-11-21-e224-blind-matmul-aifoundry1-c1/data-e224a.json
  docs/reports/data/2026-11-21-e224-blind-matmul-aifoundry2/session
  docs/reports/data/2026-11-21-e224-blind-matmul-aifoundry2/README.md
  docs/reports/data/2026-11-21-e224-blind-matmul-aifoundry1-c1/README.md
  docs/reports/data/2026-11-21-e222-blind-matmul-aifoundry3/README.md
  docs/et-soc1-notes.md
)
/usr/bin/flock -w 600 "$W/locks/lab-git.lock" /usr/bin/nice -n 10 /usr/bin/ionice -c 3 git -C "$LAB" archive --format=tar "$C" "${PATHS[@]}" > "$L/work/lab-snapshot.tar"
rc=$?
echo "archive rc $rc"
[ $rc -eq 0 ] || exit $rc
tar -x -f "$L/work/lab-snapshot.tar" -C "$L/work/lab"
echo "extract rc $?"
{
  echo "snapshot of $LAB at commit $C (git archive), $(TZ=America/Los_Angeles date '+%F %T %Z')"
  echo "tar sha256 $(sha256sum "$L/work/lab-snapshot.tar" | cut -d' ' -f1)"
  for p in "${PATHS[@]}"; do echo "path $p"; done
} > "$L/work/lab-SNAPSHOT.txt"
rm -f "$L/work/lab-snapshot.tar"
du -sh "$L/work/lab"
