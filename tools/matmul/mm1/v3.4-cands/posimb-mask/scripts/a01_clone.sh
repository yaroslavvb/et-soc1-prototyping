#!/bin/bash
# mask-posimb (Q238) a01: the lane's scratch clone of LAB (THE CLONE RULE, THE LOAD RULE), then GitHub main fetched over HTTPS,
# push URL /dev/null/never-push, hooks off, user name/email from LAB. Read-only use afterwards.
set -u
W=${ROUND_W:?the round folder}
LANE=$W/out/mask-posimb
LAB=~/git/et-soc1-prototyping
DST=$LANE/work/lab
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:
# load rule: wait while the 1-minute load is above 8 (bounded: 8 minutes in this call)
for i in $(seq 1 32); do
  l=$(cut -d' ' -f1 /proc/loadavg)
  if awk -v l="$l" 'BEGIN{exit !(l < 6)}'; then break; fi
  echo "load $l: waiting"; sleep 15
done
if [ -d "$DST/.git" ]; then
  echo "clone exists: fsck + status"
  git -C "$DST" status --short | head -5
else
  flock -w 1800 "$W/locks/clone.lock" flock -w 600 "$W/locks/lab-git.lock" nice -n 10 ionice -c 3 git clone -q --no-hardlinks "$LAB" "$DST"
  echo "clone rc $?"
fi
git -C "$DST" remote set-url origin "${LAB_REMOTE_URL:?the lab repository https URL}"
git -C "$DST" remote set-url --push origin /dev/null/never-push
git -C "$DST" config core.hooksPath /dev/null
git -C "$DST" config user.name "$(git -C "$LAB" config user.name)"
git -C "$DST" config user.email "$(git -C "$LAB" config user.email)"
nice -n 10 git -C "$DST" fetch -q origin main
echo "fetch rc $?"
git -C "$DST" checkout -q --detach origin/main
echo "checkout rc $?"
git -C "$DST" log --oneline -3
git -C "$DST" status --short | head -5
echo "HEAD $(git -C "$DST" rev-parse HEAD)"
