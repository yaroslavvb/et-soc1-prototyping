#!/bin/bash
# E198 desk check (a check of code on committed records; nothing measured, no device): the chain the card day will run,
# on aifoundry3's own data. From the repository's top, with R an empty folder outside the repository:
#   bash tools/claims-v3/e198/desk/chain_e198.sh R
# For each E193 sitting: the committed raw records (x04/runs.jsonl and the unpacked x04/telemetry.jsonl.gz), checked against
# the box's manifest; the registered reducer (proposal/src/reduce_x04.py, unchanged) run on them; its output compared byte
# for byte with E193's committed x04-e193-<S>.json; then score_e198.py scoring the re-made outputs as card 1's against the
# frozen forecast (aifoundry3 against itself through the whole chain: PASS and PASS, stated before the run).
set -u
R=${1:?an empty folder outside the repository}
E=tools/claims-v3/e193
for S in A B; do
  s=$(echo "$S" | tr AB ab)
  D=docs/reports/data/2026-11-15-e193-x04-clock-sitting-$s-aifoundry3
  mkdir -p "$R/$S/x04"
  cp "$D/x04/runs.jsonl" "$R/$S/x04/" && gzip -dc "$D/x04/telemetry.jsonl.gz" > "$R/$S/x04/telemetry.jsonl"
  for p in runs.jsonl telemetry.jsonl; do
    want=$(awk -v p="x04/$p" '$2 == p {print $1}' "$D/session/MANIFEST.sha256")
    got=$(sha256sum "$R/$S/x04/$p" | cut -c1-64)
    [ "$want" = "$got" ] && echo "sitting $S x04/$p: the box's bytes" || { echo "sitting $S x04/$p: NOT the box's bytes"; exit 3; }
  done
  /usr/bin/python3 -I -B "$E/proposal/src/reduce_x04.py" "$R/$S/x04" --out "$R/x04-$S.json" > "$R/x04-$S.txt" 2>&1
  echo "sitting $S reducer rc $?"
  cmp -s "$R/x04-$S.json" "$D/x04-e193-$S.json" && echo "sitting $S: the re-made output equals x04-e193-$S.json byte for byte" \
    || { echo "sitting $S: the re-made output DIFFERS from x04-e193-$S.json"; exit 4; }
  cmp -s "$R/x04-$S.txt" "$D/x04-e193-$S.txt" && echo "sitting $S: its printed lines equal x04-e193-$S.txt byte for byte" \
    || echo "sitting $S: its printed lines differ from x04-e193-$S.txt"
done
/usr/bin/python3 -I -B tools/claims-v3/e198/score_e198.py score --a "$R/x04-A.json" --b "$R/x04-B.json" --out "$R/scores.json" \
  > "$R/scores.txt" 2>&1
echo "score_e198.py score rc $?"
tail -n 9 "$R/scores.txt"
grep -q '^VERDICTS: E198-T1 PASS, E198-T2 PASS$' "$R/scores.txt" && echo "CHAIN PASS" || echo "CHAIN FAIL"
