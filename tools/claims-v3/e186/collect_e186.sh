#!/usr/bin/env bash
# E186 (Q158, the kit): the collector, at the desk, after the runbook's step 11 has copied the session back BY NAME and read it COPY-BACK
# EXACT against the session's manifest. A port of tools/claims-v3/e182/collect_e182.sh (E182's, run on 8 Nov 2026), with E186's changes:
#   1. the check of C over every listed session (ccsessions_e186.listed_sessions: the smoke, every train block, every fallback kinds pass
#      with a launch record), each session's C log copied ONCE, gzipped, to ccheck/c-log-<session>.jsonl.gz; the session directories are
#      copied WITHOUT their c-log.jsonl (kit v5's lesson);
#   2. the trains 18610-18619 reduced by reduce_e186.py trains (E182's reduce_train, unchanged) and, for the session's float scale s in
#      FULL, the float trains' anchors by reduce_e186.py anchors on E182's registered footing (E186.md section 4.2); the fallback's kinds
#      passes 18620-18629, if any ran, by reduce_e186.py (E78's reduction unchanged) on the registered primary footing only (E186
#      registers no reduction arm, so E182's seven are not run);
#   3. score_e186.py with the trains, the anchors' and the kinds passes' reductions.
#
#   PY=/usr/bin/python3 E186_DATE=<day> nice -n 10 bash tools/claims-v3/e186/collect_e186.sh <raw copy, repo-relative>
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
TOPD=$PWD
PY=${PY:-/usr/bin/python3}
RAW=${1:?the raw copy (repo-relative)}
case "$RAW" in /*) echo "the raw copy must be repo-relative (build/e186-raw), not $RAW: reduce_e78.py records it as given"; exit 2 ;; esac
NAME=${E186_DATE:-$(date +%F)}-e186-one-number-r3-aifoundry3
OUT=build/e186-out/$NAME
AW=build/e186-anchors-work
E=tools/claims-v3/e186
KF=0.20563713796102187
CCHECK=tools/claims-v3/ccheck/ccheck.py
if [ -n "${E186_CCHECK_STANDIN:-}" ]; then
  [ "${E186_DESKTEST:-}" = 1 ] || { echo "E186_CCHECK_STANDIN is a desk-test stand-in, read only with E186_DESKTEST=1: unset it"; exit 10; }
  CCHECK=$E186_CCHECK_STANDIN
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
mkdir -p "$OUT/aifoundry3/e186" "$OUT/logs" "$OUT/ccheck"
FLB=$("$PY" -B -c 'import json, sys; print(" ".join(str(t["block"]) for t in json.load(open(sys.argv[1]))["trains"] if t["type"] != "int8"))' "$E/plan-e186.json") ||
  { echo "plan-e186.json unreadable"; exit 2; }
ok=(); tr=(); fl=()
for d in "$RAW"/e186/p1862[0-9] "$RAW"/e186/p1861[0-9]; do
  [ -d "$d" ] || continue
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  b=$(basename "$d")
  case "$b" in
    p1862*) ok+=("$d") ;;
    *) tr+=("$d"); case " $FLB " in *" ${b#p} "*) fl+=("$d") ;; esac ;;   # the float trains (fp32 and fp16): the scale's anchors
  esac
done
echo "fallback kinds passes reduced: ${#ok[@]} (${ok[*]##*/}); trains reduced: ${#tr[@]} (${tr[*]##*/}); float trains for the scale: ${#fl[@]}"
# 1. the check of C over every listed session (E186 change 1)
SESS=$("$PY" -B - "$RAW" <<'PYEOF'
import os, sys
sys.path.insert(0, "tools/claims-v3/e186")
import ccsessions_e186 as C
print("\n".join(os.path.relpath(d, sys.argv[1]) for d in C.listed_sessions("E186", sys.argv[1])))
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
# 2. the reductions (E186 change 2)
PRIM=()
if [ ${#ok[@]} -gt 0 ]; then
  "$PY" -B $E/reduce_e186.py "${ok[@]}" --leak "$KF" --no-refit --drop-dips --out "$OUT/e186.json" --csv "$OUT/runs.csv" \
    --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1
  echo "fallback kinds passes rc=$?"; tail -3 "$OUT/reduce.log"
  PRIM=(--reduction "$OUT/e186.json" --runs-csv "$OUT/runs.csv")
fi
TRA=()
if [ ${#tr[@]} -gt 0 ]; then
  "$PY" -B $E/reduce_e186.py trains "${tr[@]}" --out "$OUT/trains-e186.json" > "$OUT/reduce-trains.log" 2>&1
  echo "trains rc=$?"; cat "$OUT/reduce-trains.log"
  TRA=(--trains "$OUT/trains-e186.json")
fi
ANC=()
if [ ${#fl[@]} -gt 0 ]; then
  "$PY" -B $E/reduce_e186.py anchors "${fl[@]}" --work "$AW" --leak "$KF" --no-refit --drop-dips --out "$OUT/e186-anchors.json" \
    --csv "$OUT/runs-anchors.csv" --txt "$OUT/reduce-anchors.txt" > "$OUT/reduce-anchors.log" 2>&1
  echo "the float trains' anchors rc=$?"; tail -3 "$OUT/reduce-anchors.log"
  [ -s "$OUT/e186-anchors.json" ] && ANC=(--anchors "$OUT/e186-anchors.json")
fi
# 3. score
"$PY" -B $E/score_e186.py score ${PRIM[@]+"${PRIM[@]}"} ${TRA[@]+"${TRA[@]}"} ${ANC[@]+"${ANC[@]}"} --raw "$RAW" \
  --ccheck "$OUT/ccheck/ccheck-all.json" --json "$OUT/scored-e186.json" --md "$OUT/results-e186.md" > "$OUT/score.log" 2>&1; src=$?
if [ "$src" -eq 0 ]; then echo "results-e186.md written"; cat "$OUT/score.log"; else echo "score_e186 rc=$src"; tail -20 "$OUT/score.log"; fi
# the session directories, each without its C log (E186 change 1: the ccheck/ copy is the one copy)
for d in "$RAW"/e186/p186[0-9][0-9]*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && [ "${b#*.attempt-}" = "$b" ]; then dst="$OUT/aifoundry3/e186/$b"
  else dst="$OUT/aifoundry3/e186/notok-$b"; fi
  rsync -a --exclude 'c-log.jsonl' --exclude 'c-log.jsonl.gz' "$d/" "$dst/"
done
for m in smoke stoptest; do for d in "$RAW"/e186-$m/p186*; do [ -d "$d" ] && mkdir -p "$OUT/aifoundry3/e186-$m" && rsync -a --exclude 'c-log.jsonl' --exclude 'c-log.jsonl.gz' "$d" "$OUT/aifoundry3/e186-$m/"; done; done
[ -d "$RAW/logs" ] && rsync -a "$RAW/logs/" "$OUT/logs/"
K=tools/claims-v3/kinds
( shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/tiles/*/*.bin \
    tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json tools/claims-v3/ccheck/*.py \
    tools/claims-v3/ccheck/*.sh tools/claims-v3/p8-600/ccsessions_p8.py tools/claims-v3/hpl/watcher_q142s.py tools/claims-v3/e178/score_e178.py \
    tools/claims-v3/e182/reduce_e182.py tools/claims-v3/e182/e182_stats.py tools/claims-v3/e182/patch_host_e182.py \
    tools/claims-v3/e182/check_inputs_e182.py tools/claims-v3/m12/kinds-m12-e186.json tools/claims-v3/m12/candidates-m12-e186.json \
    tools/claims-v3/m12/tiles/*/*.bin $E/*.py $E/*.sh $E/*.json $E/E186.md $E/SHA256SUMS-* ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
