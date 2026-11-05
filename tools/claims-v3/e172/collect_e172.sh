#!/usr/bin/env bash
# E172 (Q142(k6)): check C, reduce and score every finished pass of the session with the registered code, scrub the logs of other logins
# and assemble the data directory. Desk compute, on the Intel, over the copy box/pull_e172.sh made (build/e172-raw). A port of E164's
# last collector, tools/claims-v3/e164/collect_e164_a1.sh with collect_e164.sh inside it, each change marked E172:
#   1. the check of C (Q139(k)'s ccheck.py check, unchanged, --jobs 2) over the C log of EVERY session that must carry one (E172.md, "The
#      sessions that must carry a C log": the smoke and every pass with a launch record, ok or not; ccsessions_p8.listed_sessions), each
#      copied as c-log-<session>.jsonl, in one call -> ccheck/ccheck-session.json; a listed session WITHOUT a C log is named ("no C log:
#      <session>"), and the scorer then refuses (exit 4) and the runbook's cc_gate stops: never a silent skip (E164 skipped such a pass);
#   2. the REGISTERED PRIMARY, Q139(u)'s footing on card 1: reduce_e172.py --leak 0.3134106532552718 --no-refit (card 1's dips removed
#      once, E164's reducer) -> e172.json, runs.csv; the arms beside it, as E164's: leakage auto; dips kept; leakage 0.2955 and 0.3320;
#      the anchor and tie gates relaxed;
#   3. tools/claims-v3/p8-600/score_p8_600.py score --run E172 on the primary with every arm beside -> scored.json, results.md (it
#      checks the listed sessions' C first: exit 4 writes nothing); E164's rank-4 pair and E163's inputs are not E172's;
#   4. E164's login scrub, unchanged (tools/claims-v3/e164/scrub_etwho_e164.py): logs/ rewritten, then its --check must read OK, else exit 7
#      and nothing may be committed; logs/et-who-summary.txt counts every et-who reading by card, with no names.
#
#   PY=/usr/bin/python3 [E172_DATE=<day>] [E172_OWNER=<the box login of record>] nice -n 10 bash tools/claims-v3/e172/collect_e172.sh build/e172-raw
#
# Output: build/e172-out/<day>-e172-blind8-card1/. Nothing is committed here.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
TOPD=$PWD
PY=${PY:-python3}
RAW=${1:?raw dir (repo-relative, build/e172-raw)}
case "$RAW" in /*) echo "the raw copy must be repo-relative (build/e172-raw), not $RAW: reduce_e78.py records it as given"; exit 2 ;; esac
DAY=${E172_DATE:-$(date +%F)}
OUT=build/e172-out/$DAY-e172-blind8-card1
CACHE=${CCHECK_CACHE:-$TOPD/build/e172-ccache}
K=tools/claims-v3/kinds
E=tools/claims-v3/e172
KP=0.3134106532552718
KU=$("$PY" -B - <<'PYEOF'
import sys
sys.path.insert(0, "docs/reports/data/2026-11-03-q139u-footing")
import reduce_footing as RF
print(repr(RF.K_FROZEN["c1"]))
PYEOF
)
[ "$KU" = "$KP" ] || { echo "reduce_footing.K_FROZEN['c1'] is '$KU', not the registered $KP: refusing to reduce"; exit 9; }
rm -rf "${TOPD:?}/build/e172-out"
mkdir -p "$OUT/aifoundry1-c1/e172" "$OUT/logs" "$OUT/ccheck" "$CACHE"
ok=()
for d in "$RAW"/e172/p172[1-9][0-9]; do
  case "$d" in *.attempt-*) continue ;; esac
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]} (${ok[*]##*/})"
# 1. the check of C over every listed session (E172 change 1)
SESS=$("$PY" -B - "$RAW" <<'PYEOF'
import os, sys
sys.path.insert(0, "tools/claims-v3/p8-600")
import ccsessions_p8 as C
print("\n".join(os.path.relpath(d, sys.argv[1]) for d in C.listed_sessions("E172", sys.argv[1])))
PYEOF
)
logs=()
while IFS= read -r s; do
  [ -n "$s" ] || continue
  d=$RAW/$s
  if [ -s "$d/c-log.jsonl.gz" ]; then gzip -dc "$d/c-log.jsonl.gz" > "$OUT/ccheck/c-log-$(basename "$d").jsonl"
  elif [ -s "$d/c-log.jsonl" ]; then cp "$d/c-log.jsonl" "$OUT/ccheck/c-log-$(basename "$d").jsonl"
  else echo "no C log: $s (a session that must carry one: the scorer refuses, the runbook's gate stops)"; continue; fi
  logs+=("$OUT/ccheck/c-log-$(basename "$d").jsonl")
done <<< "$SESS"
echo "sessions that must carry a C log: $(printf '%s\n' "$SESS" | grep -c .); C logs found: ${#logs[@]}"
if [ ${#logs[@]} -gt 0 ]; then
  "$PY" -B tools/claims-v3/ccheck/ccheck.py check "${logs[@]}" --out "$OUT/ccheck/ccheck-session.json" --jobs "${CCHECK_JOBS:-2}" \
    --cache "$CACHE" > "$OUT/ccheck/ccheck-session.txt" 2>&1; echo "ccheck rc=$? $(tail -1 "$OUT/ccheck/ccheck-session.txt" | cut -c1-300)"
  gzip -f "${logs[@]}"
fi
ARMS=()
if [ ${#ok[@]} -gt 0 ]; then
  # 2. the registered primary and E164's arms
  "$PY" -B $E/reduce_e172.py "${ok[@]}" --leak "$KP" --no-refit --out "$OUT/e172.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
    > "$OUT/reduce.log" 2>&1
  echo "primary rc=$?"; tail -3 "$OUT/reduce.log"
  "$PY" -B $E/reduce_e172.py "${ok[@]}" --leak auto --no-refit --out "$OUT/e172-auto.json" --csv "$OUT/runs-auto.csv" \
    --txt "$OUT/reduce-auto.txt" > "$OUT/reduce-auto.log" 2>&1; echo "auto arm rc=$?"
  ARMS+=(--arm "session_own_slope=$OUT/e172-auto.json")
  "$PY" -B $E/reduce_e172.py "${ok[@]}" --keep-dips --leak "$KP" --no-refit --out "$OUT/e172-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
    --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
  ARMS+=(--arm "dips_kept=$OUT/e172-dipskept.json")
  for k in 0.2955 0.3320; do
    "$PY" -B $E/reduce_e172.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e172-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
      --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
    ARMS+=(--arm "leak$k=$OUT/e172-leak$k.json")
  done
  "$PY" -B $E/reduce_e172.py "${ok[@]}" --relax-anchors --leak "$KP" --no-refit --out "$OUT/e172-relaxed.json" --csv "$OUT/runs-relaxed.csv" \
    --txt "$OUT/reduce-relaxed.txt" > "$OUT/reduce-relaxed.log" 2>&1; echo "relaxed arm rc=$?"
  ARMS+=(--arm "relaxed=$OUT/e172-relaxed.json")
  # 3. score, pool 8's P8 rules (the listed sessions' C first)
  "$PY" -B tools/claims-v3/p8-600/score_p8_600.py score --run E172 --reduction "$OUT/e172.json" --raw "$RAW" \
    --ccheck "$OUT/ccheck/ccheck-session.json" "${ARMS[@]}" --json "$OUT/scored.json" --md "$OUT/results.md" > "$OUT/score.log" 2>&1
  src=$?
  if [ "$src" -eq 0 ]; then echo "results.md written"; cat "$OUT/score.log"; else echo "score_p8_600 rc=$src"; tail -20 "$OUT/score.log"; fi
fi
for d in "$RAW"/e172/p172[0-9][0-9]*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && [ "${b#*.attempt-}" = "$b" ]; then cp -r "$d" "$OUT/aifoundry1-c1/e172/"
  else cp -r "$d" "$OUT/aifoundry1-c1/e172/notok-$b"; fi
done
for m in smoke stoptest; do for d in "$RAW"/e172-$m/p172*; do [ -d "$d" ] && mkdir -p "$OUT/aifoundry1-c1/e172-$m" && cp -r "$d" "$OUT/aifoundry1-c1/e172-$m/"; done; done
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
( shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/blind8/blind8.json $K/blind8/MANIFEST \
    $K/blind8/SHA256SUMS $K/blind8/predictions-pool8-aifoundry1c1.json $K/blind8/intervals-pool8.json $K/blind8/tiles/*/*.bin \
    tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json tools/claims-v3/ccheck/*.py \
    tools/claims-v3/ccheck/*.sh tools/claims-v3/p8-600/*.py tools/claims-v3/hpl/watcher_q142s.py tools/claims-v3/e164/scrub_etwho_e164.py \
    $E/*.py $E/*.sh $E/*.json $E/E172.md $E/box/*.sh ) > "$OUT/code.sha256" 2>/dev/null
# 4. E164's login scrub, unchanged (E172 change 4)
OWN=(); [ -n "${E172_OWNER:-}" ] && OWN=(--owner "$E172_OWNER")
python3 -B tools/claims-v3/e164/scrub_etwho_e164.py "$OUT/logs" ${OWN[@]+"${OWN[@]}"} || { echo "scrub failed: commit nothing"; exit 7; }
python3 -B tools/claims-v3/e164/scrub_etwho_e164.py --check "$OUT/logs" ${OWN[@]+"${OWN[@]}"} || { echo "scrub check failed: commit nothing"; exit 7; }
cat "$OUT/logs/et-who-summary.txt" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
