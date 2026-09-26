#!/usr/bin/env bash
# Copy every campaign card's data into one directory laid out like DATA_ROOT, for the reducers (smoke blocks left out):
#   tools/claims-v3/collect.sh <dest>
# Run from aifoundry2's checkout: aifoundry2's data is local, the other hosts' trees are ~/nekko. Read-only on the hosts.
set -eu
dest=${1:?destination directory}
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
mkdir -p "$dest"
rsync -a --exclude '*-smoke' build/claims-v3/aifoundry2/ "$dest/aifoundry2/"
rsync -a --exclude '*-smoke' aifoundry3:nekko/build/claims-v3/aifoundry3/ "$dest/aifoundry3/"
rsync -a --exclude '*-smoke' aifoundry1:nekko/build/claims-v3/aifoundry1-c1/ "$dest/aifoundry1-c1/"
du -sh "$dest"/*
