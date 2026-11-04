#!/usr/bin/env bash
# E164 (Q141(b)): reduce and score every finished pass of the session with the registered code, check every launch's C, score rank 4's
# pair with E163 when E163's committed files are given, and assemble the data directory. Desk compute: run it on the Intel over a copy
# of the raw passes, never on the card's host:
#
#   PY=<python with numpy> [PYS=<python 3.12+>] [E164_DATE=YYYY-MM-DD] nice -n 10 bash tools/claims-v3/e164/collect_e164.sh <raw dir> \
#       [<E163's primary reduction json> [<E163's C-excluded tiles, comma-joined> [<E163's registered scored.json>]]]
#
# <raw dir> holds e164/, e164-smoke/ and e164-stoptest/ as copied from aifoundry1:nekko/build/claims-v3/aifoundry1-c1/, and logs/ (from
# nekko/build/e164/). Only passes whose block.json says "ok" are reduced; an `.attempt-*` directory is never read for D; no pass is chosen
# after the fact. A port of tools/claims-v3/e157/collect_e157.sh, each change marked E164:
#   1. the primary: reduce_e164.py --leak 0.3134106532552718 --no-refit (Q139(u)'s footing: card 1's frozen slope, E82 A2's dips
#      removed once; E78's gates; card 1's config gate) -> e164.json, runs.csv, reduce.txt
#   2. the arms, --no-refit: leakage auto (the session's own), dips kept at the primary slope, leakage 0.2955 and 0.3320 (Q139(u)'s
#      slope interval), the anchor gates relaxed (reported). E164 has no K1 frame on E142's footing: rank 7's reference, E157, was
#      reduced on Q139(u)'s footing (E164 change 1)
#   3. the C check (Q139(k), at the desk): every pass's C log (ok or not, and the smoke's) gunzipped into build/e164-clog/ and checked in
#      one call, ccheck.py check ... --jobs ${CCHECK_JOBS:-2} -> ccheck/ccheck-session.json, ccheck/ccheck-session.txt
#   4. score_e164.py -> scored.json, results.md (with --other if E163's committed primary reduction of pool 7 on aifoundry3 is given,
#      and --other-drop with the tiles E163's committed scored.json took out of its scored set by its C check; --s-recount with
#      Q141(t)'s committed recount if E164_S_RECOUNT names it)
#   5. (E164) rank 4: pair_rank4_e164.py on E163's registered scored.json and this session's scored.json -> rank4-e163-e164.json, .txt
# Output: build/e164-out/<E164_DATE>-e164-blind7-card1/. CCHECK_CACHE (default build/e164-ccache) holds the engine's cache.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
PYS=${PYS:-$PY}
RAW=${1:?raw dir}
E163=${2:-}
E163_DROP=${3:-}
E163_SCORED=${4:-}
DAY=${E164_DATE:-$(date +%F)}
OUT=$ROOT/build/e164-out/$DAY-e164-blind7-card1
CACHE=${CCHECK_CACHE:-$ROOT/build/e164-ccache}
K=tools/claims-v3/kinds
E=tools/claims-v3/e164
KP=0.3134106532552718
rm -rf "${ROOT:?}/build/e164-out"
mkdir -p "$OUT/aifoundry1-c1/e164" "$OUT/logs" "$OUT/ccheck" "$ROOT/build/e164-clog" "$CACHE"
ok=()
for d in "$RAW"/e164/p164[1-9][0-9]; do
  case "$d" in *.attempt-*) continue ;; esac
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]} (${ok[*]##*/})"
ARMS=()
if [ ${#ok[@]} -gt 0 ]; then
  "$PY" -B $E/reduce_e164.py "${ok[@]}" --leak "$KP" --no-refit --out "$OUT/e164.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
    > "$OUT/reduce.log" 2>&1
  echo "primary rc=$?"; tail -3 "$OUT/reduce.log"
  "$PY" -B $E/reduce_e164.py "${ok[@]}" --leak auto --no-refit --out "$OUT/e164-auto.json" --csv "$OUT/runs-auto.csv" \
    --txt "$OUT/reduce-auto.txt" > "$OUT/reduce-auto.log" 2>&1; echo "auto arm rc=$?"
  ARMS+=(--arm "session_own_slope=$OUT/e164-auto.json")
  "$PY" -B $E/reduce_e164.py "${ok[@]}" --keep-dips --leak "$KP" --no-refit --out "$OUT/e164-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
    --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
  ARMS+=(--arm "dips_kept=$OUT/e164-dipskept.json")
  for k in 0.2955 0.3320; do
    "$PY" -B $E/reduce_e164.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e164-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
      --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
    ARMS+=(--arm "leak$k=$OUT/e164-leak$k.json")
  done
  "$PY" -B $E/reduce_e164.py "${ok[@]}" --relax-anchors --leak "$KP" --no-refit --out "$OUT/e164-relaxed.json" --csv "$OUT/runs-relaxed.csv" \
    --txt "$OUT/reduce-relaxed.txt" > "$OUT/reduce-relaxed.log" 2>&1; echo "relaxed arm rc=$?"
  ARMS+=(--arm "relaxed=$OUT/e164-relaxed.json")
fi
# the C check, every pass the session ran (ok or not) and the smoke, in one call (one engine run per tile covers every n)
LOGS=(); RJ=()
for d in "$RAW"/e164/p164* "$RAW"/e164-smoke/p164*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  [ -s "$d/runs.jsonl" ] && RJ+=(--runs-jsonl "$d/runs.jsonl")
  if [ -s "$d/c-log.jsonl.gz" ]; then gzip -dc "$d/c-log.jsonl.gz" > "$ROOT/build/e164-clog/c-log-$b.jsonl"
  elif [ -s "$d/c-log.jsonl" ]; then cp "$d/c-log.jsonl" "$ROOT/build/e164-clog/c-log-$b.jsonl"
  else continue; fi
  LOGS+=("$ROOT/build/e164-clog/c-log-$b.jsonl")
done
echo "C logs: ${#LOGS[@]}"
CC=()
if [ ${#LOGS[@]} -gt 0 ]; then
  "$PY" -B tools/claims-v3/ccheck/ccheck.py check "${LOGS[@]}" --out "$OUT/ccheck/ccheck-session.json" --jobs "${CCHECK_JOBS:-2}" \
    --cache "$CACHE" > "$OUT/ccheck/ccheck-session.txt" 2>&1; echo "ccheck rc=$? $(tail -1 "$OUT/ccheck/ccheck-session.txt" | cut -c1-300)"
  [ -s "$OUT/ccheck/ccheck-session.json" ] && CC=(--ccheck "$OUT/ccheck/ccheck-session.json")
fi
if [ ${#ok[@]} -gt 0 ]; then
  X=(); [ -n "$E163" ] && [ -f "$E163" ] && X=(--other "$E163" --other-drop "$E163_DROP")
  SR=(); [ -n "${E164_S_RECOUNT:-}" ] && [ -f "${E164_S_RECOUNT:-}" ] && SR=(--s-recount "$E164_S_RECOUNT")
  "$PYS" -B $E/score_e164.py --primary "$OUT/e164.json" --runs "$OUT/runs.csv" ${ARMS[@]+"${ARMS[@]}"} \
    ${CC[@]+"${CC[@]}"} ${RJ[@]+"${RJ[@]}"} ${X[@]+"${X[@]}"} ${SR[@]+"${SR[@]}"} --json "$OUT/scored.json" --md "$OUT/results.md" \
    > "$OUT/score.log" 2>&1 && { echo "results.md written"; cat "$OUT/score.log"; } || { echo "score_e164 failed"; tail -20 "$OUT/score.log"; }
  if [ -n "$E163_SCORED" ] && [ -f "$E163_SCORED" ] && [ -s "$OUT/scored.json" ]; then                                    # E164 change 5
    "$PYS" -B $E/pair_rank4_e164.py --e163 "$E163_SCORED" --e164 "$OUT/scored.json" --out "$OUT/rank4-e163-e164.json" \
      --txt "$OUT/rank4-e163-e164.txt" > "$OUT/rank4.log" 2>&1; echo "rank 4 rc=$? $(head -1 "$OUT/rank4-e163-e164.txt" 2>/dev/null)"
  fi
fi
for d in "$RAW"/e164/p164[0-9][0-9]*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && [ "${b#*.attempt-}" = "$b" ]; then cp -r "$d" "$OUT/aifoundry1-c1/e164/"
  else cp -r "$d" "$OUT/aifoundry1-c1/e164/notok-$b"; fi
done
for m in smoke stoptest; do for d in "$RAW"/e164-$m/p164*; do [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry1-c1/e164-$m-$(basename "$d")"; done; done
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
( cd "$ROOT" && shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/blind7/blind7.json \
    $K/blind7/MANIFEST $K/blind7/SHA256SUMS $K/blind7/predictions-blind7-aifoundry1c1.json $K/blind7/tiles/*/*.bin $K/blind6/blind6.json \
    $K/blind6/SHA256SUMS tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json \
    tools/claims-v3/ccheck/*.py tools/claims-v3/ccheck/*.sh $E/* ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
