#!/bin/bash
# verify-v31trace (Q217) v08: copy run u1's kept files from aifoundry3 to work/u1 (each scp through a3.sh: book.sh show and the claim
# file read just before), then hash them.
set -u
L=<W>/out/verify-v31trace
D=$L/work/u1
mkdir -p "$D"
for f in summary.json.gz mine.json.gz excerpt-hart0.log.gz excerpt-hart1.log.gz excerpt-hart830.log.gz excerpt-shire1.log.gz \
         excerpt-shire31.log.gz out.json RUN.txt sandbox-check.txt err.log; do
  bash "$L/scripts/a3.sh" get "claude/work/q217-verify-v31trace/runs/u1/$f" "$D" | tail -1 || exit 3
done
cd "$D" && sha256sum * > SHA256SUMS && cat SHA256SUMS
sed -i "s#$HOME#~#g" "$D/RUN.txt"
du -sh "$D"
