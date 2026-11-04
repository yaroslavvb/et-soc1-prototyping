#!/usr/bin/env bash
# E163 (Q141): check C, reduce and score every finished pass and E151 block of the session with the registered code, and assemble the data
# directory. Desk compute: run it on the Intel over a copy of the raw passes, never on the card's host. A port of
# tools/claims-v3/e153/collect_e153.sh (E153's layout: e163/, e163-smoke/, e163-stoptest/ under build/claims-v3/aifoundry3/), with the
# E151 blocks' reduction added (E163):
#
#   PY=<python with numpy> nice -n 10 bash tools/claims-v3/e163/collect_e163.sh <raw copy> [<Q141(t)'s arm as {tile: D_w} json>]
#
# <raw copy> holds e163/, e163-smoke/ and e163-stoptest/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/, and logs/. Only
# passes and blocks whose block.json says "ok" are reduced; an `.attempt-*` directory is never read; nothing is chosen after the fact.
#   1. the C check (Q139(k)'s ccheck.py check, unchanged, --jobs 2): every pass's, every E151 block's and the smoke's c-log.jsonl, copied
#      under distinct names, in one call -> ccheck/ccheck-all.json, ccheck/ccheck.txt
#   2. the REGISTERED PRIMARY, Q139(u)'s one footing, on the kinds passes (16310-16329): reduce_e163.py --leak 0.20563713796102187
#      --no-refit --drop-dips (E82 A2 once) -> e163.json, runs.csv
#   3. beside it, the session-own footing: leakage auto (fitted on this session), dips kept -> e163-session.json
#   4. the arms: leakage auto with dips removed; k frozen with dips kept; leakage 0.1994, 0.3803 and 0 with dips removed; pass gates
#      opened on the footing
#   5. E163: the E151 blocks (16350-16359): reduce_e163.py --e151 --drop-dips --rail-filter (E151's registered primary) -> e163-e151.json,
#      runs-e151.csv
#   6. score_e163.py on the primary with every arm beside, the E151 blocks and (if given) Q141(t)'s 27-point arm -> scored.json,
#      results.md; the session-own footing scored alone (reported, never the verdict) -> scored-session.json, results-session.md
# Output: build/e163-out/<E163_DATE, default today>-e163-blind7-aifoundry3/.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
RAW=${1:?the raw copy}
ARM27=${2:-}
NAME=${E163_DATE:-$(date +%F)}-e163-blind7-aifoundry3
OUT=$ROOT/build/e163-out/$NAME
K=tools/claims-v3/kinds
E=tools/claims-v3/e163
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
rm -rf "${ROOT:?}/build/e163-out"
mkdir -p "$OUT/aifoundry3/e163" "$OUT/logs" "$OUT/ccheck"
ok=(); okb=()
for d in "$RAW"/e163/p163[1-5][0-9]; do
  case "$d" in *.attempt-*) continue ;; esac
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  case "$(basename "$d")" in p1631[0-9]|p1632[0-9]) ok+=("$d") ;; p1635[0-9]) okb+=("$d") ;; esac
done
echo "kinds passes reduced: ${#ok[@]} (${ok[*]##*/}); E151 blocks: ${#okb[@]} (${okb[*]##*/})"
# 1. the C check, at the desk
logs=()
for d in "$RAW"/e163/p163[0-9][0-9] "$RAW"/e163-smoke/p16301; do
  [ -s "$d/c-log.jsonl" ] || continue
  cp "$d/c-log.jsonl" "$OUT/ccheck/c-log-$(basename "$d").jsonl"
  logs+=("$OUT/ccheck/c-log-$(basename "$d").jsonl")
done
if [ ${#logs[@]} -gt 0 ]; then
  "$PY" tools/claims-v3/ccheck/ccheck.py check "${logs[@]}" --out "$OUT/ccheck/ccheck-all.json" --jobs 2 > "$OUT/ccheck/ccheck.txt" 2>&1
  echo "ccheck rc=$? ($(tail -1 "$OUT/ccheck/ccheck.txt" | head -c 400))"
  gzip -f "${logs[@]}"
fi
X=(--ccheck "$OUT/ccheck" --passes "$RAW/e163")
if [ ${#okb[@]} -gt 0 ]; then
  # 5. the E151 blocks, E151's registered primary
  "$PY" $E/reduce_e163.py "${okb[@]}" --e151 --drop-dips --rail-filter --out "$OUT/e163-e151.json" --csv "$OUT/runs-e151.csv" \
    --txt "$OUT/reduce-e151.txt" > "$OUT/reduce-e151.log" 2>&1; echo "E151 blocks rc=$?"
  [ -s "$OUT/e163-e151.json" ] && X+=(--e151-block "$OUT/runs-e151.csv,$OUT/e163-e151.json")
fi
[ -n "$ARM27" ] && X+=(--arm27 "$ARM27")
if [ ${#ok[@]} -gt 0 ]; then
  # 2. the registered primary: Q139(u)'s footing
  "$PY" $E/reduce_e163.py "${ok[@]}" --leak "$KF" --no-refit --drop-dips --out "$OUT/e163.json" --csv "$OUT/runs.csv" \
    --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1
  echo "primary rc=$?"; tail -3 "$OUT/reduce.log"
  # 3. the session-own footing, beside
  "$PY" $E/reduce_e163.py "${ok[@]}" --out "$OUT/e163-session.json" --csv "$OUT/runs-session.csv" --txt "$OUT/reduce-session.txt" \
    > "$OUT/reduce-session.log" 2>&1; echo "session-own rc=$?"
  ARMS=(--arm "session_own=$OUT/e163-session.json")
  # 4. the arms
  "$PY" $E/reduce_e163.py "${ok[@]}" --drop-dips --out "$OUT/e163-auto-nodips.json" --csv "$OUT/runs-auto-nodips.csv" \
    --txt "$OUT/reduce-auto-nodips.txt" > "$OUT/reduce-auto-nodips.log" 2>&1; echo "auto, dips removed rc=$?"
  ARMS+=(--arm "auto_dips_removed=$OUT/e163-auto-nodips.json")
  "$PY" $E/reduce_e163.py "${ok[@]}" --leak "$KF" --no-refit --out "$OUT/e163-kfrozen-dips.json" --csv "$OUT/runs-kfrozen-dips.csv" \
    --txt "$OUT/reduce-kfrozen-dips.txt" > "$OUT/reduce-kfrozen-dips.log" 2>&1; echo "k frozen, dips kept rc=$?"
  ARMS+=(--arm "kfrozen_dips_kept=$OUT/e163-kfrozen-dips.json")
  for k in 0.1994 0.3803 0; do
    "$PY" $E/reduce_e163.py "${ok[@]}" --leak "$k" --no-refit --drop-dips --out "$OUT/e163-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
      --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
    ARMS+=(--arm "leak$k=$OUT/e163-leak$k.json")
  done
  "$PY" $E/reduce_e163.py "${ok[@]}" --leak "$KF" --no-refit --drop-dips --gates-off --out "$OUT/e163-gatesoff.json" \
    --csv "$OUT/runs-gatesoff.csv" --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
  ARMS+=(--arm "gates_off=$OUT/e163-gatesoff.json")
  # 6. score
  "$PY" $E/score_e163.py --e163 "$OUT/e163.json" --runs "$OUT/runs.csv" "${ARMS[@]}" "${X[@]}" --json "$OUT/scored.json" \
    --md "$OUT/results.md" > "$OUT/score.log" 2>&1 && { echo "results.md written"; cat "$OUT/score.log"; } ||
    { echo "score_e163 failed"; tail -20 "$OUT/score.log"; }
  "$PY" $E/score_e163.py --e163 "$OUT/e163-session.json" --runs "$OUT/runs-session.csv" "${X[@]}" --json "$OUT/scored-session.json" \
    --md "$OUT/results-session.md" > "$OUT/score-session.log" 2>&1 && echo "results-session.md written (reported beside)" ||
    { echo "score of the session-own footing failed"; tail -20 "$OUT/score-session.log"; }
fi
for d in "$RAW"/e163/p163[0-9][0-9]*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && [ "${b#*.attempt-}" = "$b" ]; then cp -r "$d" "$OUT/aifoundry3/e163/"
  else cp -r "$d" "$OUT/aifoundry3/e163/notok-$b"; fi
done
for m in smoke stoptest; do for d in "$RAW"/e163-$m/p163*; do [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/e163-$m-$(basename "$d")"; done; done
find "$OUT/aifoundry3" -name 'c-log.jsonl' -exec gzip -f {} \;
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
( cd "$ROOT" && shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/blind7/blind7.json \
    $K/blind7/MANIFEST $K/blind7/SHA256SUMS $K/blind7/predictions-blind7-aifoundry3.json $K/blind7/tiles/*/*.bin $K/blind5/blind5.json \
    tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json tools/claims-v3/ccheck/*.py \
    tools/claims-v3/ccheck/*.sh tools/claims-v3/e151/railfilter_e151.py $E/*.py $E/*.sh $E/*.json $E/E163.md ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
