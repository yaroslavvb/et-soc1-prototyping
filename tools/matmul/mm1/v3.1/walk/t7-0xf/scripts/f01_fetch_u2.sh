#!/bin/bash
# t7-0xf (Q221) f01: copy run u2's kept files from aifoundry3 to work/u2 (each scp through a3.sh: book.sh show and the claim file read
# just before), then hash them as fetched (SHA256SUMS.fetched). Nothing is changed here; the scrub is a separate, recorded step.
set -u
L=<W>/out/t7-0xf
D=$L/work/u2
mkdir -p "$D"
for f in summary.json.gz mine.json.gz excerpt-hart0.log.gz excerpt-hart1.log.gz excerpt-hart254.log.gz excerpt-shire4.log.gz \
         excerpt-shire31.log.gz out.json RUN.txt sandbox-check.txt err.log pu_uart0_tx.log pu_uart1_tx.log spio_uart0_tx.log spio_uart1_tx.log; do
  bash "$L/scripts/a3.sh" get "claude/work/q221-t7-0xf/runs/u2/$f" "$D" | tail -1 || exit 3
done
cd "$D" && sha256sum * > "$L/work/u2.SHA256SUMS.fetched" && cat "$L/work/u2.SHA256SUMS.fetched"
du -sh "$D"
