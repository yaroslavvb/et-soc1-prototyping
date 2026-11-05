#!/usr/bin/env bash
# E171 (Q142(k6)): check C, reduce and score every finished pass of the session with the registered code, and assemble the data directory.
# Desk compute: run it on the Intel over a copy of the raw passes, never on the card's host. A port of tools/claims-v3/e163/collect_e163.sh
# (E163's layout: e171/, e171-smoke/, e171-stoptest/ under build/claims-v3/aifoundry3/), with E163's E151 blocks left out and the scorer
# replaced by pool 8's P8 scorer (E171):
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e171/collect_e171.sh <raw copy, repo-relative>
#
# <raw copy> holds e171/, e171-smoke/ and e171-stoptest/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/, and logs/. It must
# be repo-relative (build/e171-raw, the runbook's): reduce_e78.py records the pass directories as given. Only passes whose block.json says
# "ok" are reduced; an `.attempt-*` directory is never read; nothing is chosen after the fact.
#   1. the C check (Q139(k)'s ccheck.py check, unchanged, --jobs 2) over the C log of EVERY session that must carry one (E171.md, "The
#      sessions that must carry a C log": the smoke and every pass with a launch record, ok or not), copied under distinct names
#      (c-log-<session>.jsonl), in one call -> ccheck/ccheck-all.json, ccheck/ccheck.txt; a listed session WITHOUT a C log is named here
#      ("no C log: <session>"), and the scorer then refuses (exit 4) and the runbook's cc_gate stops: never a silent skip;
#   2. the REGISTERED PRIMARY, Q139(u)'s one footing, on the kinds and SHORT passes (17110-17129): reduce_e171.py --leak 0.20563713796102187
#      --no-refit --drop-dips (E82 A2 once) -> e171.json, runs.csv;
#   3. beside it, the session-own footing: leakage auto (fitted on this session), dips kept -> e171-session.json;
#   4. the arms: leakage auto with dips removed; k frozen with dips kept; leakage 0.1994, 0.3803 and 0 with dips removed; pass gates opened
#      on the footing;
#   5. tools/claims-v3/p8-600/score_p8_600.py score --run E171 on the primary with every arm beside -> scored.json, results.md (it checks
#      the listed sessions' C first: exit 4 writes nothing);
# Output: build/e171-out/<E171_DATE, default today>-e171-blind8-aifoundry3/. Nothing is committed here.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
TOPD=$PWD
PY=${PY:-python3}
RAW=${1:?the raw copy (repo-relative)}
case "$RAW" in /*) echo "the raw copy must be repo-relative (build/e171-raw), not $RAW: reduce_e78.py records it as given"; exit 2 ;; esac
NAME=${E171_DATE:-$(date +%F)}-e171-blind8-aifoundry3
OUT=build/e171-out/$NAME
K=tools/claims-v3/kinds
E=tools/claims-v3/e171
KF=0.20563713796102187
# Q139(u)'s frozen aifoundry3 slope, read through its module (reduce_footing.K_FROZEN, from footing.json), must be the registered one
KU=$("$PY" -B - <<'PYEOF'
import sys
sys.path.insert(0, "docs/reports/data/2026-11-03-q139u-footing")
import reduce_footing as RF
print(repr(RF.K_FROZEN["a3"]))
PYEOF
)
[ "$KU" = "$KF" ] || { echo "reduce_footing.K_FROZEN['a3'] is '$KU', not the registered $KF: refusing to reduce"; exit 9; }
rm -rf "${TOPD:?}/build/e171-out"
mkdir -p "$OUT/aifoundry3/e171" "$OUT/logs" "$OUT/ccheck"
ok=()
for d in "$RAW"/e171/p171[12][0-9]; do
  case "$d" in *.attempt-*) continue ;; esac
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]} (${ok[*]##*/})"
# 1. the C check, at the desk, over every listed session (ccsessions_p8.listed_sessions: the registered rule)
SESS=$("$PY" -B - "$RAW" <<'PYEOF'
import os, sys
sys.path.insert(0, "tools/claims-v3/p8-600")
import ccsessions_p8 as C
print("\n".join(os.path.relpath(d, sys.argv[1]) for d in C.listed_sessions("E171", sys.argv[1])))
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
  "$PY" -B tools/claims-v3/ccheck/ccheck.py check "${logs[@]}" --out "$OUT/ccheck/ccheck-all.json" --jobs 2 > "$OUT/ccheck/ccheck.txt" 2>&1
  echo "ccheck rc=$? ($(tail -1 "$OUT/ccheck/ccheck.txt" | head -c 400))"
  gzip -f "${logs[@]}"
fi
if [ ${#ok[@]} -gt 0 ]; then
  # 2. the registered primary: Q139(u)'s footing
  "$PY" -B $E/reduce_e171.py "${ok[@]}" --leak "$KF" --no-refit --drop-dips --out "$OUT/e171.json" --csv "$OUT/runs.csv" \
    --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1
  echo "primary rc=$?"; tail -3 "$OUT/reduce.log"
  # 3. the session-own footing, beside
  "$PY" -B $E/reduce_e171.py "${ok[@]}" --out "$OUT/e171-session.json" --csv "$OUT/runs-session.csv" --txt "$OUT/reduce-session.txt" \
    > "$OUT/reduce-session.log" 2>&1; echo "session-own rc=$?"
  ARMS=(--arm "session_own=$OUT/e171-session.json")
  # 4. the arms
  "$PY" -B $E/reduce_e171.py "${ok[@]}" --drop-dips --out "$OUT/e171-auto-nodips.json" --csv "$OUT/runs-auto-nodips.csv" \
    --txt "$OUT/reduce-auto-nodips.txt" > "$OUT/reduce-auto-nodips.log" 2>&1; echo "auto, dips removed rc=$?"
  ARMS+=(--arm "auto_dips_removed=$OUT/e171-auto-nodips.json")
  "$PY" -B $E/reduce_e171.py "${ok[@]}" --leak "$KF" --no-refit --out "$OUT/e171-kfrozen-dips.json" --csv "$OUT/runs-kfrozen-dips.csv" \
    --txt "$OUT/reduce-kfrozen-dips.txt" > "$OUT/reduce-kfrozen-dips.log" 2>&1; echo "k frozen, dips kept rc=$?"
  ARMS+=(--arm "kfrozen_dips_kept=$OUT/e171-kfrozen-dips.json")
  for k in 0.1994 0.3803 0; do
    "$PY" -B $E/reduce_e171.py "${ok[@]}" --leak "$k" --no-refit --drop-dips --out "$OUT/e171-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
      --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
    ARMS+=(--arm "leak$k=$OUT/e171-leak$k.json")
  done
  "$PY" -B $E/reduce_e171.py "${ok[@]}" --leak "$KF" --no-refit --drop-dips --gates-off --out "$OUT/e171-gatesoff.json" \
    --csv "$OUT/runs-gatesoff.csv" --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
  ARMS+=(--arm "gates_off=$OUT/e171-gatesoff.json")
  # 5. score, pool 8's P8 rules (the listed sessions' C first)
  "$PY" -B tools/claims-v3/p8-600/score_p8_600.py score --run E171 --reduction "$OUT/e171.json" --raw "$RAW" \
    --ccheck "$OUT/ccheck/ccheck-all.json" "${ARMS[@]}" --json "$OUT/scored.json" --md "$OUT/results.md" > "$OUT/score.log" 2>&1
  src=$?
  if [ "$src" -eq 0 ]; then echo "results.md written"; cat "$OUT/score.log"; else echo "score_p8_600 rc=$src"; tail -20 "$OUT/score.log"; fi
fi
for d in "$RAW"/e171/p171[0-9][0-9]*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && [ "${b#*.attempt-}" = "$b" ]; then cp -r "$d" "$OUT/aifoundry3/e171/"
  else cp -r "$d" "$OUT/aifoundry3/e171/notok-$b"; fi
done
for m in smoke stoptest; do for d in "$RAW"/e171-$m/p171*; do [ -d "$d" ] && mkdir -p "$OUT/aifoundry3/e171-$m" && cp -r "$d" "$OUT/aifoundry3/e171-$m/"; done; done
find "$OUT/aifoundry3" -name 'c-log.jsonl' -exec gzip -f {} \;
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
( shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/blind8/blind8.json $K/blind8/MANIFEST \
    $K/blind8/SHA256SUMS $K/blind8/predictions-pool8-aifoundry3.json $K/blind8/intervals-pool8.json $K/blind8/tiles/*/*.bin \
    tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json tools/claims-v3/ccheck/*.py \
    tools/claims-v3/ccheck/*.sh tools/claims-v3/p8-600/*.py tools/claims-v3/hpl/watcher_q142s.py $E/*.py $E/*.sh $E/*.json $E/E171.md ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
