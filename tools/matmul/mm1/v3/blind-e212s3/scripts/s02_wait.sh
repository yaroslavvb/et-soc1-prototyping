#!/bin/bash
# blind-v3-e212s3 step 2: one bounded wait chunk (at most 8.5 minutes) for the data commit of E212 a2c0-S3's re-run on GitHub main
# (data-e212s3 commits docs/reports/data/2026-11-18-e212-mmsweep2-a2c0-S3/ through commit_lab.sh in LAB, so the commit is in LAB's object
# store once pushed). Reads only: ls-remote over the environment-only HTTPS rewrite, ls-tree of main's commit, the orchestrator's release
# record and the quiet-desk flag (for the log). Opens no data file. Exit 0 when the folder is on GitHub main; 3 at the bound; 4 past the
# lane's deadline (14:00 PST Thu 19 Nov 2026).
set -u
W=<W>
L=$W/out/blind-v3-e212s3
LAB=<LAB>
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:
ts() { TZ=America/Los_Angeles date '+%F %T %Z'; }
DEADLINE=$(TZ=America/Los_Angeles date -d '2026-11-19 14:00:00' +%s)
end=$(( $(date +%s) + 510 ))
last=""
while :; do
  now=$(date +%s)
  [ "$now" -ge "$DEADLINE" ] && { echo "$(ts) past the lane's deadline (14:00 PST Thu 19 Nov): stop"; exit 4; }
  M=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main 2>/dev/null | cut -f1)
  H=$(git -C "$LAB" rev-parse HEAD)
  flag=absent; [ -e "$W/locks/quiet-desk-aifoundry2" ] && flag="$(head -c 120 "$W/locks/quiet-desk-aifoundry2")"
  claim=absent; [ -e "$W/out/orch/claim-aifoundry2.txt" ] && claim=present
  rel=$(grep -c . "$W/out/orch/e212-releases.txt")
  found=""
  if [ -n "$M" ] && git -C "$LAB" cat-file -e "$M^{commit}" 2>/dev/null; then
    found=$(git -C "$LAB" ls-tree -d --name-only "$M" docs/reports/data/ | grep -E 'e212.*a2c0-S3' | head -n 3 | tr '\n' ' ')
    mk=local
  else
    mk="not-local"
  fi
  state="main ${M:-?} ($mk) LAB ${H:0:10} flag[$flag] claim[$claim] releases[$rel lines] load $(cut -d' ' -f1 /proc/loadavg)"
  if [ "$state" != "$last" ]; then echo "$(ts) $state"; last=$state; fi
  if [ -n "$found" ]; then
    echo "$(ts) FOUND on GitHub main $M: $found"
    for d in $found; do
      git -C "$LAB" log --diff-filter=A --format='  added by %H committer %ci author %ai: %s' "$M" -- "$d" | cut -c1-260
    done
    echo "$M" > "$L/work/main-with-data.txt"
    exit 0
  fi
  [ "$(date +%s)" -ge "$end" ] && { echo "$(ts) not yet (chunk bound)"; exit 3; }
  sleep 60
done
