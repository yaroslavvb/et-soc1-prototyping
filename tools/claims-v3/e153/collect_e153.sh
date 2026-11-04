#!/usr/bin/env bash
# E153 (Q139): check C, reduce and score every finished pass of the session with the registered code, and assemble the data directory.
# Desk compute: run it on the Intel over a copy of the raw passes, never on the card's host. A port of tools/claims-v3/e141/collect_e141.sh
# (E141's layout: e153/, e153-smoke/, e153-stoptest/ under build/claims-v3/aifoundry3/), with the C check and Q139(u)'s footing first:
#
#   PY=<python with numpy> nice -n 10 bash tools/claims-v3/e153/collect_e153.sh <raw root> [<E157 reduction json>]
#
# <raw root> holds e153/, e153-smoke/ and e153-stoptest/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/, and logs/. Only
# passes whose block.json says "ok" are reduced; an `.attempt-*` directory is never read; no pass is chosen after the fact.
#   1. the C check (Q139(k)'s ccheck.py check, unchanged, --jobs 6): every pass's c-log.jsonl and the smoke's, copied under distinct
#      names, in one call (one engine run per tile covers every n) -> ccheck/ccheck-all.json, ccheck/ccheck.txt
#   2. the REGISTERED PRIMARY, Q139(u)'s one footing: reduce_e153.py --leak 0.20563713796102187 --no-refit --drop-dips (E82 A2 once)
#      -> e153.json, runs.csv
#   3. beside it, E141's session-own footing: reduce_e153.py with leakage auto (fitted on this session), dips kept -> e153-session.json
#   4. the arms: leakage auto with dips removed; k frozen with dips kept; leakage 0.1994, 0.3803 and 0 with dips removed; pass gates
#      opened on the footing
#   5. score_e153.py on the primary with every arm beside (and E157's reduction for CS1 when given) -> scored.json, results.md; the
#      session-own footing scored alone (reported, never the verdict) -> scored-session.json, results-session.md
# Output: build/e153-out/2026-11-03-e153-blind6-aifoundry3/.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
RAW=${1:?raw root}
E157J=${2:-}
OUT=$ROOT/build/e153-out/2026-11-03-e153-blind6-aifoundry3
K=tools/claims-v3/kinds
E=tools/claims-v3/e153
KF=0.20563713796102187
# Q139(u)'s frozen aifoundry3 slope, read through its module (reduce_footing.K_FROZEN, from footing.json), must be the registered one
KU=$("$PY" - <<'PYEOF'
import sys
sys.path.insert(0, "docs/reports/data/2026-11-03-q139u-footing")
import reduce_footing as RF
print(repr(RF.K_FROZEN["a3"]))
PYEOF
)
[ "$KU" = "$KF" ] || { echo "reduce_footing.K_FROZEN['a3'] is '$KU', not the registered $KF: refusing to reduce"; exit 9; }
rm -rf "${ROOT:?}/build/e153-out"
mkdir -p "$OUT/aifoundry3/e153" "$OUT/logs" "$OUT/ccheck"
ok=()
for d in "$RAW"/e153/p153[1-9][0-9]; do
  case "$d" in *.attempt-*) continue ;; esac
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]} (${ok[*]##*/})"
# 1. the C check, at the desk
logs=()
for d in "$RAW"/e153/p153[0-9][0-9] "$RAW"/e153-smoke/p15301; do
  [ -s "$d/c-log.jsonl" ] || continue
  cp "$d/c-log.jsonl" "$OUT/ccheck/c-log-$(basename "$d").jsonl"
  logs+=("$OUT/ccheck/c-log-$(basename "$d").jsonl")
done
if [ ${#logs[@]} -gt 0 ]; then
  "$PY" tools/claims-v3/ccheck/ccheck.py check "${logs[@]}" --out "$OUT/ccheck/ccheck-all.json" --jobs 6 > "$OUT/ccheck/ccheck.txt" 2>&1
  echo "ccheck rc=$? ($(tail -1 "$OUT/ccheck/ccheck.txt" | head -c 400))"
  gzip -f "${logs[@]}"
fi
if [ ${#ok[@]} -gt 0 ]; then
  # 2. the registered primary: Q139(u)'s footing
  "$PY" $E/reduce_e153.py "${ok[@]}" --leak "$KF" --no-refit --drop-dips --out "$OUT/e153.json" --csv "$OUT/runs.csv" \
    --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1
  echo "primary rc=$?"; tail -3 "$OUT/reduce.log"
  # 3. E141's session-own footing, beside
  "$PY" $E/reduce_e153.py "${ok[@]}" --out "$OUT/e153-session.json" --csv "$OUT/runs-session.csv" --txt "$OUT/reduce-session.txt" \
    > "$OUT/reduce-session.log" 2>&1; echo "session-own rc=$?"
  ARMS=(--arm "session_own=$OUT/e153-session.json")
  # 4. the arms
  "$PY" $E/reduce_e153.py "${ok[@]}" --drop-dips --out "$OUT/e153-auto-nodips.json" --csv "$OUT/runs-auto-nodips.csv" \
    --txt "$OUT/reduce-auto-nodips.txt" > "$OUT/reduce-auto-nodips.log" 2>&1; echo "auto, dips removed rc=$?"
  ARMS+=(--arm "auto_dips_removed=$OUT/e153-auto-nodips.json")
  "$PY" $E/reduce_e153.py "${ok[@]}" --leak "$KF" --no-refit --out "$OUT/e153-kfrozen-dips.json" --csv "$OUT/runs-kfrozen-dips.csv" \
    --txt "$OUT/reduce-kfrozen-dips.txt" > "$OUT/reduce-kfrozen-dips.log" 2>&1; echo "k frozen, dips kept rc=$?"
  ARMS+=(--arm "kfrozen_dips_kept=$OUT/e153-kfrozen-dips.json")
  for k in 0.1994 0.3803 0; do
    "$PY" $E/reduce_e153.py "${ok[@]}" --leak "$k" --no-refit --drop-dips --out "$OUT/e153-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
      --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
    ARMS+=(--arm "leak$k=$OUT/e153-leak$k.json")
  done
  "$PY" $E/reduce_e153.py "${ok[@]}" --leak "$KF" --no-refit --drop-dips --gates-off --out "$OUT/e153-gatesoff.json" \
    --csv "$OUT/runs-gatesoff.csv" --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
  ARMS+=(--arm "gates_off=$OUT/e153-gatesoff.json")
  # 5. score
  X=(--ccheck "$OUT/ccheck" --passes "$RAW/e153")
  [ -n "$E157J" ] && X+=(--e157 "$E157J")
  "$PY" $E/score_e153.py --e153 "$OUT/e153.json" --runs "$OUT/runs.csv" "${ARMS[@]}" "${X[@]}" --json "$OUT/scored.json" \
    --md "$OUT/results.md" > "$OUT/score.log" 2>&1 && { echo "results.md written"; cat "$OUT/score.log"; } ||
    { echo "score_e153 failed"; tail -20 "$OUT/score.log"; }
  "$PY" $E/score_e153.py --e153 "$OUT/e153-session.json" --runs "$OUT/runs-session.csv" "${X[@]}" --json "$OUT/scored-session.json" \
    --md "$OUT/results-session.md" > "$OUT/score-session.log" 2>&1 && echo "results-session.md written (reported beside)" ||
    { echo "score of the session-own footing failed"; tail -20 "$OUT/score-session.log"; }
fi
for d in "$RAW"/e153/p153[0-9][0-9]*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && [ "${b#*.attempt-}" = "$b" ]; then cp -r "$d" "$OUT/aifoundry3/e153/"
  else cp -r "$d" "$OUT/aifoundry3/e153/notok-$b"; fi
done
for m in smoke stoptest; do for d in "$RAW"/e153-$m/p153*; do [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/e153-$m-$(basename "$d")"; done; done
find "$OUT/aifoundry3" -name 'c-log.jsonl' -exec gzip -f {} \;
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
( cd "$ROOT" && shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/blind6/blind6.json \
    $K/blind6/MANIFEST $K/blind6/SHA256SUMS $K/blind6/predictions-blind6-aifoundry3.json $K/blind6/tiles/*/*.bin $K/blind5/blind5.json \
    tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json tools/claims-v3/ccheck/*.py \
    tools/claims-v3/ccheck/*.sh $E/*.py $E/*.sh $E/*.json ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
