#!/usr/bin/env bash
# E157 (Q139): reduce and score every finished pass of the session with the registered code, check every launch's C, and assemble the
# data directory. Desk compute: run it on the Intel over a copy of the raw passes, never on the card's host:
#
#   PY=<python with numpy> nice -n 10 bash tools/claims-v3/e157/collect_e157.sh <raw root> [<E153's primary reduction json> [<E153's C-excluded tiles, comma-joined>]]
#
# <raw root> holds e157/, e157-smoke/ and e157-stoptest/ as copied from aifoundry1:nekko/build/claims-v3/aifoundry1-c1/, and logs/. Only
# passes whose block.json says "ok" are reduced; an `.attempt-*` directory is never read for D; no pass is chosen after the fact. A port of
# tools/claims-v3/e142/collect_e142.sh:
#   1. the primary: reduce_e157.py --leak 0.3134106532552718 --no-refit (Q139(u)'s footing: card 1's frozen slope, E82 A2's dips removed
#      once; E78's gates; card 1's config gate) -> e157.json, runs.csv, reduce.txt
#   2. E142's own footing: reduce_e157.py --leak 0.2414 (as E142's primary ran) -> e157-e142footing.json, scored beside the primary
#      with every rule (an arm) and K1 read on it against e142.json
#   3. the arms, --no-refit: leakage auto (the session's own), dips kept at the primary slope, leakage 0.2955 and 0.3320 (Q139(u)'s slope
#      interval), the anchor gates relaxed (reported)
#   4. the C check (Q139(k), at the desk): every pass's C log (ok or not, and the smoke's) gunzipped into the scratch as
#      c-log-p<pass>.jsonl and checked in one call, ccheck.py check ... --jobs 6 -> ccheck/ccheck-session.json, ccheck/ccheck-session.txt
#   5. score_e157.py -> scored.json, results.md (with --e153 if E153's committed primary reduction of pool 6 on aifoundry3 is given, and
#      --e153-drop with the tiles E153's committed scored.json took out of its scored set by its C check)
# Output: build/e157-out/2026-11-03-e157-blind6-card1/. CCHECK_CACHE (default build/e157-ccache) holds the engine's cache.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
RAW=${1:?raw root}
E153=${2:-}
E153_DROP=${3:-}
OUT=$ROOT/build/e157-out/2026-11-03-e157-blind6-card1
CACHE=${CCHECK_CACHE:-$ROOT/build/e157-ccache}
K=tools/claims-v3/kinds
E=tools/claims-v3/e157
KP=0.3134106532552718
rm -rf "${ROOT:?}/build/e157-out"
mkdir -p "$OUT/aifoundry1-c1/e157" "$OUT/logs" "$OUT/ccheck" "$ROOT/build/e157-clog" "$CACHE"
ok=()
for d in "$RAW"/e157/p157[1-9][0-9]; do
  case "$d" in *.attempt-*) continue ;; esac
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]} (${ok[*]##*/})"
if [ ${#ok[@]} -gt 0 ]; then
  "$PY" $E/reduce_e157.py "${ok[@]}" --leak "$KP" --no-refit --out "$OUT/e157.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
    > "$OUT/reduce.log" 2>&1
  echo "primary rc=$?"; tail -3 "$OUT/reduce.log"
  "$PY" $E/reduce_e157.py "${ok[@]}" --leak 0.2414 --out "$OUT/e157-e142footing.json" --csv "$OUT/runs-e142footing.csv" \
    --txt "$OUT/reduce-e142footing.txt" > "$OUT/reduce-e142footing.log" 2>&1; echo "K1 frame (E142's footing) rc=$?"
  ARMS=(--arm "e142_footing=$OUT/e157-e142footing.json")
  "$PY" $E/reduce_e157.py "${ok[@]}" --leak auto --no-refit --out "$OUT/e157-auto.json" --csv "$OUT/runs-auto.csv" \
    --txt "$OUT/reduce-auto.txt" > "$OUT/reduce-auto.log" 2>&1; echo "auto arm rc=$?"
  ARMS+=(--arm "session_own_slope=$OUT/e157-auto.json")
  "$PY" $E/reduce_e157.py "${ok[@]}" --keep-dips --leak "$KP" --no-refit --out "$OUT/e157-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
    --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
  ARMS+=(--arm "dips_kept=$OUT/e157-dipskept.json")
  for k in 0.2955 0.3320; do
    "$PY" $E/reduce_e157.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e157-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
      --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
    ARMS+=(--arm "leak$k=$OUT/e157-leak$k.json")
  done
  "$PY" $E/reduce_e157.py "${ok[@]}" --relax-anchors --leak "$KP" --no-refit --out "$OUT/e157-relaxed.json" --csv "$OUT/runs-relaxed.csv" \
    --txt "$OUT/reduce-relaxed.txt" > "$OUT/reduce-relaxed.log" 2>&1; echo "relaxed arm rc=$?"
  ARMS+=(--arm "relaxed=$OUT/e157-relaxed.json")
fi
# the C check, every pass the session ran (ok or not) and the smoke, in one call (one engine run per tile covers every n)
LOGS=(); RJ=()
for d in "$RAW"/e157/p157* "$RAW"/e157-smoke/p157*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  [ -s "$d/runs.jsonl" ] && RJ+=(--runs-jsonl "$d/runs.jsonl")
  if [ -s "$d/c-log.jsonl.gz" ]; then gzip -dc "$d/c-log.jsonl.gz" > "$ROOT/build/e157-clog/c-log-$b.jsonl"
  elif [ -s "$d/c-log.jsonl" ]; then cp "$d/c-log.jsonl" "$ROOT/build/e157-clog/c-log-$b.jsonl"
  else continue; fi
  LOGS+=("$ROOT/build/e157-clog/c-log-$b.jsonl")
done
echo "C logs: ${#LOGS[@]}"
CC=()
if [ ${#LOGS[@]} -gt 0 ]; then
  "$PY" tools/claims-v3/ccheck/ccheck.py check "${LOGS[@]}" --out "$OUT/ccheck/ccheck-session.json" --jobs 6 --cache "$CACHE" \
    > "$OUT/ccheck/ccheck-session.txt" 2>&1; echo "ccheck rc=$? $(tail -1 "$OUT/ccheck/ccheck-session.txt" | cut -c1-300)"
  [ -s "$OUT/ccheck/ccheck-session.json" ] && CC=(--ccheck "$OUT/ccheck/ccheck-session.json")
fi
if [ ${#ok[@]} -gt 0 ]; then
  X=(); [ -n "$E153" ] && [ -f "$E153" ] && X=(--e153 "$E153" --e153-drop "$E153_DROP")
  "$PY" $E/score_e157.py --e157 "$OUT/e157.json" --k1-e142 "$OUT/e157-e142footing.json" --runs "$OUT/runs.csv" "${ARMS[@]}" \
    ${CC[@]+"${CC[@]}"} ${RJ[@]+"${RJ[@]}"} ${X[@]+"${X[@]}"} --json "$OUT/scored.json" --md "$OUT/results.md" > "$OUT/score.log" 2>&1 &&
    { echo "results.md written"; cat "$OUT/score.log"; } || { echo "score_e157 failed"; tail -20 "$OUT/score.log"; }
fi
for d in "$RAW"/e157/p157[0-9][0-9]*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && [ "${b#*.attempt-}" = "$b" ]; then cp -r "$d" "$OUT/aifoundry1-c1/e157/"
  else cp -r "$d" "$OUT/aifoundry1-c1/e157/notok-$b"; fi
done
for m in smoke stoptest; do for d in "$RAW"/e157-$m/p157*; do [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry1-c1/e157-$m-$(basename "$d")"; done; done
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
( cd "$ROOT" && shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/blind6/blind6.json \
    $K/blind6/MANIFEST $K/blind6/SHA256SUMS $K/blind6/predictions-blind6-aifoundry1c1.json $K/blind6/tiles/*/*.bin $K/blind5/blind5.json \
    $K/blind5/SHA256SUMS tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json \
    tools/claims-v3/ccheck/*.py tools/claims-v3/ccheck/*.sh $E/* ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
