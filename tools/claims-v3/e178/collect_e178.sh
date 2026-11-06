#!/usr/bin/env bash
# E178 (Q146, the kit): check C, reduce and score every finished pass of the session with the registered code, and assemble the data
# directory. Desk compute: run it on the Intel over a copy of the raw passes, never on the card's host. A port of
# tools/claims-v3/e171/collect_e171.sh (E171's layout: e178/, e178-smoke/, e178-stoptest/ under build/claims-v3/aifoundry3/), with the
# scorer replaced by E178's (score_e178.py):
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e178/collect_e178.sh <raw copy, repo-relative>
#
# <raw copy> holds e178/, e178-smoke/ and e178-stoptest/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/, and logs/. It must
# be repo-relative (build/e178-raw, the runbook's): reduce_e78.py records the pass directories as given. Only passes whose block.json says
# "ok" are reduced; an `.attempt-*` directory is never read; nothing is chosen after the fact.
#   1. the C check (Q139(k)'s ccheck.py check, unchanged, --jobs 2) over the C log of EVERY session that must carry one (E178.md section 7,
#      E171's rule: the smoke and every pass with a launch record, ok or not), copied under distinct names (c-log-<session>.jsonl), in one
#      call -> ccheck/ccheck-all.json, ccheck/ccheck.txt; a listed session WITHOUT a C log is named here ("no C log: <session>"), and the
#      scorer then refuses (exit 4) and the runbook's cc_gate stops: never a silent skip;
#   2. the REGISTERED PRIMARY, E171's footing (E178.md section 5): reduce_e178.py --leak 0.20563713796102187 --no-refit --drop-dips
#      (E82 A2 once) -> e178.json, runs.csv (the per-run values the scorer's couples read);
#   3. beside it, the session-own footing: leakage auto (fitted on this session), dips kept -> e178-session.json;
#   4. the arms, E171's: leakage auto with dips removed; k frozen with dips kept; leakage 0.1994, 0.3803 and 0 with dips removed; pass gates
#      opened on the footing;
#   5. tools/claims-v3/e178/score_e178.py score --card aifoundry3 on the primary with every arm beside -> scored.json, results.md (it
#      checks the listed sessions' C first: exit 4 writes nothing).
# Output: build/e178-out/<E178_DATE, default today>-e178-one-number-aifoundry3/. Nothing is committed here. The desk test
# (selftest_collect_e178.py) alone sets E178_DESKTEST=1 and E178_CCHECK_STANDIN; the card day never sets either.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
TOPD=$PWD
PY=${PY:-python3}
RAW=${1:?the raw copy (repo-relative)}
case "$RAW" in /*) echo "the raw copy must be repo-relative (build/e178-raw), not $RAW: reduce_e78.py records it as given"; exit 2 ;; esac
NAME=${E178_DATE:-$(date +%F)}-e178-one-number-aifoundry3
OUT=build/e178-out/$NAME
K=tools/claims-v3/kinds
E=tools/claims-v3/e178
KF=0.20563713796102187
# the desk test's stand-in for the check of C (selftest_collect_e178.py): read only with E178_DESKTEST=1; set without it, refused
CCHECK=tools/claims-v3/ccheck/ccheck.py
if [ -n "${E178_CCHECK_STANDIN:-}" ]; then
  [ "${E178_DESKTEST:-}" = 1 ] || { echo "E178_CCHECK_STANDIN is a desk-test stand-in, read only with E178_DESKTEST=1: unset it"; exit 10; }
  CCHECK=$E178_CCHECK_STANDIN
fi
# Q139(u)'s frozen aifoundry3 slope, read through its module (reduce_footing.K_FROZEN, from footing.json), must be the registered one
KU=$("$PY" -B - <<'PYEOF'
import sys
sys.path.insert(0, "docs/reports/data/2026-11-03-q139u-footing")
import reduce_footing as RF
print(repr(RF.K_FROZEN["a3"]))
PYEOF
)
[ "$KU" = "$KF" ] || { echo "reduce_footing.K_FROZEN['a3'] is '$KU', not the registered $KF: refusing to reduce"; exit 9; }
rm -rf "${TOPD:?}/build/e178-out"
mkdir -p "$OUT/aifoundry3/e178" "$OUT/logs" "$OUT/ccheck"
ok=()
for d in "$RAW"/e178/p1781[0-9]; do
  case "$d" in *.attempt-*) continue ;; esac
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]} (${ok[*]##*/})"
# 1. the C check, at the desk, over every listed session (ccsessions_e178.listed_sessions: the registered rule)
SESS=$("$PY" -B - "$RAW" <<'PYEOF'
import os, sys
sys.path.insert(0, "tools/claims-v3/e178")
import ccsessions_e178 as C
print("\n".join(os.path.relpath(d, sys.argv[1]) for d in C.listed_sessions("E178", sys.argv[1])))
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
if [ ${#ok[@]} -gt 0 ]; then
  # 2. the registered primary: E171's footing
  "$PY" -B $E/reduce_e178.py "${ok[@]}" --leak "$KF" --no-refit --drop-dips --out "$OUT/e178.json" --csv "$OUT/runs.csv" \
    --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1
  echo "primary rc=$?"; tail -3 "$OUT/reduce.log"
  # 3. the session-own footing, beside
  "$PY" -B $E/reduce_e178.py "${ok[@]}" --out "$OUT/e178-session.json" --csv "$OUT/runs-session.csv" --txt "$OUT/reduce-session.txt" \
    > "$OUT/reduce-session.log" 2>&1; echo "session-own rc=$?"
  ARMS=(--arm "session_own=$OUT/e178-session.json,$OUT/runs-session.csv")
  # 4. the arms
  "$PY" -B $E/reduce_e178.py "${ok[@]}" --drop-dips --out "$OUT/e178-auto-nodips.json" --csv "$OUT/runs-auto-nodips.csv" \
    --txt "$OUT/reduce-auto-nodips.txt" > "$OUT/reduce-auto-nodips.log" 2>&1; echo "auto, dips removed rc=$?"
  ARMS+=(--arm "auto_dips_removed=$OUT/e178-auto-nodips.json,$OUT/runs-auto-nodips.csv")
  "$PY" -B $E/reduce_e178.py "${ok[@]}" --leak "$KF" --no-refit --out "$OUT/e178-kfrozen-dips.json" --csv "$OUT/runs-kfrozen-dips.csv" \
    --txt "$OUT/reduce-kfrozen-dips.txt" > "$OUT/reduce-kfrozen-dips.log" 2>&1; echo "k frozen, dips kept rc=$?"
  ARMS+=(--arm "kfrozen_dips_kept=$OUT/e178-kfrozen-dips.json,$OUT/runs-kfrozen-dips.csv")
  for k in 0.1994 0.3803 0; do
    "$PY" -B $E/reduce_e178.py "${ok[@]}" --leak "$k" --no-refit --drop-dips --out "$OUT/e178-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
      --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
    ARMS+=(--arm "leak$k=$OUT/e178-leak$k.json,$OUT/runs-leak$k.csv")
  done
  "$PY" -B $E/reduce_e178.py "${ok[@]}" --leak "$KF" --no-refit --drop-dips --gates-off --out "$OUT/e178-gatesoff.json" \
    --csv "$OUT/runs-gatesoff.csv" --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
  ARMS+=(--arm "gates_off=$OUT/e178-gatesoff.json,$OUT/runs-gatesoff.csv")
  # 5. score: E178.md section 5's rules and A1's E178-S-int8 (the listed sessions' C first)
  "$PY" -B $E/score_e178.py score --card aifoundry3 --reduction "$OUT/e178.json" --runs-csv "$OUT/runs.csv" --raw "$RAW" \
    --ccheck "$OUT/ccheck/ccheck-all.json" "${ARMS[@]}" --json "$OUT/scored.json" --md "$OUT/results.md" > "$OUT/score.log" 2>&1
  src=$?
  if [ "$src" -eq 0 ]; then echo "results.md written"; cat "$OUT/score.log"; else echo "score_e178 rc=$src"; tail -20 "$OUT/score.log"; fi
fi
for d in "$RAW"/e178/p178[0-9][0-9]*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && [ "${b#*.attempt-}" = "$b" ]; then cp -r "$d" "$OUT/aifoundry3/e178/"
  else cp -r "$d" "$OUT/aifoundry3/e178/notok-$b"; fi
done
for m in smoke stoptest; do for d in "$RAW"/e178-$m/p178*; do [ -d "$d" ] && mkdir -p "$OUT/aifoundry3/e178-$m" && cp -r "$d" "$OUT/aifoundry3/e178-$m/"; done; done
find "$OUT/aifoundry3" -name 'c-log.jsonl' -exec gzip -f {} \;
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
( shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/tiles/*/*.bin \
    tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json tools/claims-v3/ccheck/*.py \
    tools/claims-v3/ccheck/*.sh tools/claims-v3/p8-600/ccsessions_p8.py tools/claims-v3/p8-600/score_p8_600.py tools/claims-v3/hpl/watcher_q142s.py \
    $E/*.py $E/*.sh $E/*.json $E/*.c $E/E178.md $E/E178.md.dated-note-*.md $E/SHA256SUMS-* $E/tiles/*/*.bin ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
