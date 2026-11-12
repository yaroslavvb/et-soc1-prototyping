#!/usr/bin/env bash
# E188 (Q165, the kit): the collector, at the desk, after the runbook's step 11 has copied the session back BY NAME and read it COPY-BACK
# EXACT against the session's manifest. A port of tools/claims-v3/e186/collect_e186_v2.sh (E186's, run on 9 Nov 2026; itself E182's
# collector with E186's kit note 1), with E188's changes:
#   1. the check of C over every listed session (ccsessions_e188.listed_sessions: the smoke, every train block, every kinds pass with a
#      launch record), each session's C log copied ONCE, gzipped, to ccheck/c-log-<session>.jsonl.gz; the session directories are copied
#      WITHOUT their c-log.jsonl (kit v5's lesson);
#   2. the trains 18810-18816 reduced by reduce_e188.py trains (E182's reduce_train, unchanged) and, for the session's float scale s, the
#      trains' anchors by reduce_e188.py anchors on E182's registered footing (E188.md section 4.2); the kinds passes - FULL's 18820/18821
#      or the fallback's 18830-18834, whichever ran (one family a session) - by reduce_e188.py (E78's reduction unchanged) on the
#      registered primary footing only;
#   3. score_e188.py with the trains, the anchors' and the kinds passes' reductions; it reads the pairing check (E188-SCHED) itself.
#
#   PY=/usr/bin/python3 E188_DATE=<day> nice -n 10 bash tools/claims-v3/e188/collect_e188.sh <raw copy, repo-relative>
# The output is build/e188-out/<day>-e188-one-number-r4-aifoundry3/ (the data directory's name: docs/reports/data/<day>-e188-one-number-r4-
# aifoundry3/).
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
TOPD=$PWD
PY=${PY:-/usr/bin/python3}
RAW=${1:?the raw copy (repo-relative)}
case "$RAW" in /*) echo "the raw copy must be repo-relative (build/e188-raw), not $RAW: reduce_e78.py records it as given"; exit 2 ;; esac
NAME=${E188_DATE:-$(date +%F)}-e188-one-number-r4-aifoundry3
OUT=build/e188-out/$NAME
AW=build/e188-anchors-work
E=tools/claims-v3/e188
KF=0.20563713796102187
CCHECK=tools/claims-v3/ccheck/ccheck.py
if [ -n "${E188_CCHECK_STANDIN:-}" ]; then
  [ "${E188_DESKTEST:-}" = 1 ] || { echo "E188_CCHECK_STANDIN is a desk-test stand-in, read only with E188_DESKTEST=1: unset it"; exit 10; }
  CCHECK=$E188_CCHECK_STANDIN
fi
KU=$("$PY" -B - <<'PYEOF'
import sys
sys.path.insert(0, "docs/reports/data/2026-11-03-q139u-footing")
import reduce_footing as RF
print(repr(RF.K_FROZEN["a3"]))
PYEOF
)
[ "$KU" = "$KF" ] || { echo "reduce_footing.K_FROZEN['a3'] is '$KU', not the registered $KF: refusing to reduce"; exit 9; }
rm -rf "${TOPD:?}/$OUT" "${TOPD:?}/$AW"
mkdir -p "$OUT/aifoundry3/e188" "$OUT/logs" "$OUT/ccheck"
ok=(); tr=(); fl=()
for d in "$RAW"/e188/p188[23][0-9] "$RAW"/e188/p1881[0-6]; do
  [ -d "$d" ] || continue
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  b=$(basename "$d")
  case "$b" in
    p188[23]*) ok+=("$d") ;;
    *) tr+=("$d"); fl+=("$d") ;;                 # every E188 train is fp32: each one's anchors serve the scale
  esac
done
echo "kinds passes reduced: ${#ok[@]} (${ok[*]##*/}); trains reduced: ${#tr[@]} (${tr[*]##*/}); trains for the scale: ${#fl[@]}"
# 1. the check of C over every listed session (E188 change 1)
SESS=$("$PY" -B - "$RAW" <<'PYEOF'
import os, sys
sys.path.insert(0, "tools/claims-v3/e188")
import ccsessions_e188 as C
print("\n".join(os.path.relpath(d, sys.argv[1]) for d in C.listed_sessions("E188", sys.argv[1])))
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
# 2. the reductions (E188 change 2)
PRIM=()
if [ ${#ok[@]} -gt 0 ]; then
  "$PY" -B $E/reduce_e188.py "${ok[@]}" --leak "$KF" --no-refit --drop-dips --out "$OUT/e188.json" --csv "$OUT/runs.csv" \
    --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1
  echo "kinds passes rc=$?"; tail -3 "$OUT/reduce.log"
  PRIM=(--reduction "$OUT/e188.json" --runs-csv "$OUT/runs.csv")
fi
TRA=()
if [ ${#tr[@]} -gt 0 ]; then
  "$PY" -B $E/reduce_e188.py trains "${tr[@]}" --out "$OUT/trains-e188.json" > "$OUT/reduce-trains.log" 2>&1
  echo "trains rc=$?"; cat "$OUT/reduce-trains.log"
  TRA=(--trains "$OUT/trains-e188.json")
fi
ANC=()
if [ ${#fl[@]} -gt 0 ]; then
  "$PY" -B $E/reduce_e188.py anchors "${fl[@]}" --work "$AW" --leak "$KF" --no-refit --drop-dips --out "$OUT/e188-anchors.json" \
    --csv "$OUT/runs-anchors.csv" --txt "$OUT/reduce-anchors.txt" > "$OUT/reduce-anchors.log" 2>&1
  echo "the trains' anchors rc=$?"; tail -3 "$OUT/reduce-anchors.log"
  [ -s "$OUT/e188-anchors.json" ] && ANC=(--anchors "$OUT/e188-anchors.json")
fi
# 3. score
"$PY" -B $E/score_e188.py score ${PRIM[@]+"${PRIM[@]}"} ${TRA[@]+"${TRA[@]}"} ${ANC[@]+"${ANC[@]}"} --raw "$RAW" \
  --ccheck "$OUT/ccheck/ccheck-all.json" --json "$OUT/scored-e188.json" --md "$OUT/results-e188.md" > "$OUT/score.log" 2>&1; src=$?
if [ "$src" -eq 0 ]; then echo "results-e188.md written"; cat "$OUT/score.log"; else echo "score_e188 rc=$src"; tail -20 "$OUT/score.log"; fi
# the session directories, each without its C log (E188 change 1: the ccheck/ copy is the one copy)
for d in "$RAW"/e188/p188[0-9][0-9]*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && [ "${b#*.attempt-}" = "$b" ]; then dst="$OUT/aifoundry3/e188/$b"
  else dst="$OUT/aifoundry3/e188/notok-$b"; fi
  rsync -a --exclude 'c-log.jsonl' --exclude 'c-log.jsonl.gz' "$d/" "$dst/"
done
for m in smoke stoptest; do for d in "$RAW"/e188-$m/p188*; do [ -d "$d" ] && mkdir -p "$OUT/aifoundry3/e188-$m" && rsync -a --exclude 'c-log.jsonl' --exclude 'c-log.jsonl.gz' "$d" "$OUT/aifoundry3/e188-$m/"; done; done
[ -d "$RAW/logs" ] && rsync -a "$RAW/logs/" "$OUT/logs/"
K=tools/claims-v3/kinds
( shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/tiles/*/*.bin \
    tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json tools/claims-v3/ccheck/*.py \
    tools/claims-v3/ccheck/*.sh tools/claims-v3/p8-600/ccsessions_p8.py tools/claims-v3/hpl/watcher_q142s.py tools/claims-v3/e178/score_e178.py \
    tools/claims-v3/e182/reduce_e182.py tools/claims-v3/e182/e182_stats.py tools/claims-v3/e182/patch_host_e182.py \
    tools/claims-v3/e182/check_inputs_e182.py tools/claims-v3/e186/e186_stats.py tools/claims-v3/m12/m12_common.py \
    $E/*.py $E/*.sh $E/*.json $E/E188.md $E/SHA256SUMS-* $E/tiles/*/*.bin ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
