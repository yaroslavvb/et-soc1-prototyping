#!/usr/bin/env bash
# E172, ON THE INTEL after the session ends: copy the raw passes and the session's logs from aifoundry1 into the Intel clone's
# build/e172-raw/ (gitignored), then reduce and score them there (collect_e172.sh). Never reduce on the box.
#   bash tools/claims-v3/e172/box/pull_e172.sh
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." || exit 1
R="ssh -o BatchMode=yes -o ConnectTimeout=10"
mkdir -p build/e172-raw/logs
for m in e172 e172-smoke e172-stoptest; do
  rsync -a -e "$R" "aifoundry1:nekko/build/claims-v3/aifoundry1-c1/$m/" "build/e172-raw/$m/" || echo "rsync $m failed"
done
rsync -a -e "$R" "aifoundry1:nekko/build/e172/" "build/e172-raw/logs/" || echo "rsync logs failed"
du -sh build/e172-raw build/e172-raw/*
ls build/e172-raw/e172/ build/e172-raw/logs/
