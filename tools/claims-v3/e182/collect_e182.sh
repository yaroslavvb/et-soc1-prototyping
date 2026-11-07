#!/usr/bin/env bash
# E182 (Q153, the kit): the collector, at the desk, after the runbook's step 11 has copied the box's raw tree back. A port of
# tools/claims-v3/e178/collect_e178_v2.sh (its arm-dropping rule kept: an arm whose reduction fails is dropped, never left in the output,
# its files moved to build/e182-dropped-arms/ and one line in arms-dropped.txt), with E182's changes:
#   1. the check of C over every listed session (ccsessions_e182.listed_sessions: the smoke, every train block, every kinds pass with a
#      launch record), each session's C log copied ONCE, gzipped, to ccheck/c-log-<session>.jsonl.gz; the session directories are copied
#      WITHOUT their c-log.jsonl (kit v5's lesson: one copy of each C log; E178's data carried two);
#   2. the kinds passes 18220-18223 reduced by reduce_e182.py (E78's reduction unchanged) on the registered primary footing and E178's
#      seven arms; the trains 18210-18215 reduced by reduce_e182.py trains;
#   3. score_e182.py with the primary, the trains and the arms.
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e182/collect_e182.sh <raw copy, repo-relative>
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
TOPD=$PWD
PY=${PY:-/usr/bin/python3}
RAW=${1:?the raw copy (repo-relative)}
case "$RAW" in /*) echo "the raw copy must be repo-relative (build/e182-raw), not $RAW: reduce_e78.py records it as given"; exit 2 ;; esac
NAME=${E182_DATE:-$(date +%F)}-e182-one-number-r2-aifoundry3
OUT=build/e182-out/$NAME
DROP=build/e182-dropped-arms
K=tools/claims-v3/kinds
E=tools/claims-v3/e182
KF=0.20563713796102187
CCHECK=tools/claims-v3/ccheck/ccheck.py
if [ -n "${E182_CCHECK_STANDIN:-}" ]; then
  [ "${E182_DESKTEST:-}" = 1 ] || { echo "E182_CCHECK_STANDIN is a desk-test stand-in, read only with E182_DESKTEST=1: unset it"; exit 10; }
  CCHECK=$E182_CCHECK_STANDIN
fi
KU=$("$PY" -B - <<'PYEOF'
import sys
sys.path.insert(0, "docs/reports/data/2026-11-03-q139u-footing")
import reduce_footing as RF
print(repr(RF.K_FROZEN["a3"]))
PYEOF
)
[ "$KU" = "$KF" ] || { echo "reduce_footing.K_FROZEN['a3'] is '$KU', not the registered $KF: refusing to reduce"; exit 9; }
rm -rf "${TOPD:?}/build/e182-out" "${TOPD:?}/build/e182-dropped-arms"
mkdir -p "$OUT/aifoundry3/e182" "$OUT/logs" "$OUT/ccheck"
ok=(); tr=()
for d in "$RAW"/e182/p1822[0-9] "$RAW"/e182/p1821[0-5]; do
  [ -d "$d" ] || continue
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  case "$d" in *p1822*) ok+=("$d") ;; *) tr+=("$d") ;; esac
done
echo "kinds passes reduced: ${#ok[@]} (${ok[*]##*/}); trains reduced: ${#tr[@]} (${tr[*]##*/})"
# 1. the check of C over every listed session (E182 change 1)
SESS=$("$PY" -B - "$RAW" <<'PYEOF'
import os, sys
sys.path.insert(0, "tools/claims-v3/e182")
import ccsessions_e182 as C
print("\n".join(os.path.relpath(d, sys.argv[1]) for d in C.listed_sessions("E182", sys.argv[1])))
PYEOF
)
logs=()
while IFS= read -r s; do
  [ -n "$s" ] || continue
  d=$RAW/$s
  if [ -s "$d/c-log.jsonl" ]; then cp "$d/c-log.jsonl" "$OUT/ccheck/c-log-$(basename "$d").jsonl"
  elif [ -s "$d/c-log.jsonl.gz" ]; then gzip -dc "$d/c-log.jsonl.gz" > "$OUT/ccheck/c-log-$(basename "$d").jsonl"
  else echo "no C log: $s (a session that must carry one: the scorer refuses, the runbook's gate stops)"; continue; fi
  logs+=("$OUT/ccheck/c-log-$(basename "$d").jsonl")
done <<< "$SESS"
echo "sessions that must carry a C log: $(printf '%s\n' "$SESS" | grep -c .); C logs found: ${#logs[@]}"
if [ ${#logs[@]} -gt 0 ]; then
  "$PY" -B "$CCHECK" check "${logs[@]}" --out "$OUT/ccheck/ccheck-all.json" --jobs 2 > "$OUT/ccheck/ccheck.txt" 2>&1
  echo "ccheck rc=$? ($(tail -1 "$OUT/ccheck/ccheck.txt" | head -c 400))"
  gzip -f "${logs[@]}"
fi
dropped=0
drop_arm() {  # drop_arm <name> <stem> <why>
  local f
  mkdir -p "$DROP/$1"
  for f in "e182-$2.json" "runs-$2.csv" "reduce-$2.txt" "reduce-$2.log"; do [ -e "$OUT/$f" ] && mv "$OUT/$f" "$DROP/$1/"; done
  [ -s "$OUT/arms-dropped.txt" ] || echo "E182 collect_e182.sh: arms dropped (an arm is reported only and no verdict reads it). Their files are kept on the desk, never committed." > "$OUT/arms-dropped.txt"
  echo "$1: $3" >> "$OUT/arms-dropped.txt"
  echo "arm dropped: $1 ($3)"
  dropped=$((dropped + 1))
}
ARMS=()
arm() {  # arm <name> <stem> <reduce_e182 options...>
  local n=$1 st=$2 r; shift 2
  "$PY" -B $E/reduce_e182.py "${ok[@]}" "$@" --out "$OUT/e182-$st.json" --csv "$OUT/runs-$st.csv" --txt "$OUT/reduce-$st.txt" > "$OUT/reduce-$st.log" 2>&1; r=$?
  echo "arm $n rc=$r"
  if [ "$r" -eq 0 ]; then ARMS+=(--arm "$n=$OUT/e182-$st.json,$OUT/runs-$st.csv"); else drop_arm "$n" "$st" "its reduction exited $r"; fi
}
PRIM=()
if [ ${#ok[@]} -gt 0 ]; then
  # 2. the registered primary (E178's footing), then E178's seven arms
  "$PY" -B $E/reduce_e182.py "${ok[@]}" --leak "$KF" --no-refit --drop-dips --out "$OUT/e182.json" --csv "$OUT/runs.csv" \
    --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1
  echo "primary rc=$?"; tail -3 "$OUT/reduce.log"
  PRIM=(--reduction "$OUT/e182.json" --runs-csv "$OUT/runs.csv")
  arm session_own session
  arm auto_dips_removed auto-nodips --drop-dips
  arm kfrozen_dips_kept kfrozen-dips --leak "$KF" --no-refit
  for k in 0.1994 0.3803 0; do arm "leak$k" "leak$k" --leak "$k" --no-refit --drop-dips; done
  arm gates_off gatesoff --leak "$KF" --no-refit --drop-dips --gates-off
fi
TRA=()
if [ ${#tr[@]} -gt 0 ]; then
  "$PY" -B $E/reduce_e182.py trains "${tr[@]}" --out "$OUT/trains-e182.json" > "$OUT/reduce-trains.log" 2>&1
  echo "trains rc=$?"; cat "$OUT/reduce-trains.log"
  TRA=(--trains "$OUT/trains-e182.json")
fi
# 3. score
"$PY" -B $E/score_e182.py score ${PRIM[@]+"${PRIM[@]}"} ${TRA[@]+"${TRA[@]}"} --raw "$RAW" --ccheck "$OUT/ccheck/ccheck-all.json" \
  ${ARMS[@]+"${ARMS[@]}"} --json "$OUT/scored.json" --md "$OUT/results.md" > "$OUT/score.log" 2>&1; src=$?
if [ "$src" -eq 0 ]; then echo "results.md written"; cat "$OUT/score.log"; else echo "score_e182 rc=$src"; tail -20 "$OUT/score.log"; fi
echo "arms dropped: $dropped"
# the session directories, each without its C log (E182 change 1: the ccheck/ copy is the one copy)
for d in "$RAW"/e182/p182[0-9][0-9]*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && [ "${b#*.attempt-}" = "$b" ]; then dst="$OUT/aifoundry3/e182/$b"
  else dst="$OUT/aifoundry3/e182/notok-$b"; fi
  rsync -a --exclude 'c-log.jsonl' --exclude 'c-log.jsonl.gz' "$d/" "$dst/"
done
for m in smoke stoptest; do for d in "$RAW"/e182-$m/p182*; do [ -d "$d" ] && mkdir -p "$OUT/aifoundry3/e182-$m" && rsync -a --exclude 'c-log.jsonl' --exclude 'c-log.jsonl.gz' "$d" "$OUT/aifoundry3/e182-$m/"; done; done
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
( shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/tiles/*/*.bin \
    tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json tools/claims-v3/ccheck/*.py \
    tools/claims-v3/ccheck/*.sh tools/claims-v3/p8-600/ccsessions_p8.py tools/claims-v3/hpl/watcher_q142s.py tools/claims-v3/e178/score_e178.py \
    $E/*.py $E/*.sh $E/*.json $E/E182.md $E/SHA256SUMS-* $E/tiles/*/*.bin tools/claims-v3/e178/tiles/*/*.bin ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
