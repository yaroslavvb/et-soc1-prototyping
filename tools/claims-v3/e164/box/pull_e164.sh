#!/usr/bin/env bash
# E164, ON THE INTEL after the session ends: copy the raw passes and the session's logs from aifoundry1 into the Intel clone's
# build/e164-raw/ (gitignored), then reduce and score them there (collect_e164.sh). Never reduce on the box.
#   bash tools/claims-v3/e164/box/pull_e164.sh
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." || exit 1
R="ssh -o BatchMode=yes -o ConnectTimeout=10"
mkdir -p build/e164-raw/logs
for m in e164 e164-smoke e164-stoptest; do
  rsync -a -e "$R" "aifoundry1:nekko/build/claims-v3/aifoundry1-c1/$m/" "build/e164-raw/$m/" || echo "rsync $m failed"
done
rsync -a -e "$R" "aifoundry1:nekko/build/e164/" "build/e164-raw/logs/" || echo "rsync logs failed"
du -sh build/e164-raw build/e164-raw/*
ls build/e164-raw/e164/ build/e164-raw/logs/
