#!/usr/bin/env bash
# E178 (Q146; the kit's dated note 1, KIT.md.dated-note-1.md section 4), the collector, v2: collect_e178.sh (which stays as committed)
# line for line, with ONE change, registered before any E178 datum. An arm (the seven reduction arms beside the primary: reported only,
# no verdict reads them) that fails is DROPPED, never left in the output:
#   - an arm whose reduction exits non-zero is not passed to the scorer;
#   - an arm the scorer reports as an error ("arms": {<name>: {"error": ...}} in scored.json) is dropped and the session is scored again
#     without it, once (the primary, its rules and its verdicts are computed the same way both times);
#   - a dropped arm's four files (e178-<arm>.json, runs-<arm>.csv, reduce-<arm>.txt, reduce-<arm>.log) are MOVED out of the output to
#     build/e178-dropped-arms/<arm>/ (ignored by git, never committed: its log's traceback carries this Mac's paths), and one line per
#     dropped arm goes to the output's arms-dropped.txt: the arm's name and why (the reduction's exit status, or the scorer's exception
#     type), never a message text or a path.
# Why (the kit verifier's fault 4): a failed arm's reduce log holds a Python traceback with the lab clone's and this Mac's absolute paths
# (reduce_e178.py puts its own directory on sys.path; numpy sits under the home directory), so step 22's desk-path gate (rb_nopath)
# stopped the whole collection with 16 on an arm that no verdict reads. Everything else is v1's: read v1's header for the steps.
# The desk test (selftest_collect_e178_v2.py) alone sets E178_DESKTEST=1 with E178_CCHECK_STANDIN, E178_DESKTEST_FAIL_REDUCE (an arm
# whose reduction is handed a broken pass directory, so it fails) or E178_DESKTEST_BREAK_JSON (an arm whose reduction is overwritten so
# the scorer fails on it); the card day never sets any of them, and each is refused without E178_DESKTEST=1.
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e178/collect_e178_v2.sh <raw copy, repo-relative>
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
TOPD=$PWD
PY=${PY:-python3}
RAW=${1:?the raw copy (repo-relative)}
case "$RAW" in /*) echo "the raw copy must be repo-relative (build/e178-raw), not $RAW: reduce_e78.py records it as given"; exit 2 ;; esac
NAME=${E178_DATE:-$(date +%F)}-e178-one-number-aifoundry3
OUT=build/e178-out/$NAME
DROP=build/e178-dropped-arms
K=tools/claims-v3/kinds
E=tools/claims-v3/e178
KF=0.20563713796102187
# the desk test's stand-ins (selftest_collect_e178_v2.py): read only with E178_DESKTEST=1; set without it, refused
CCHECK=tools/claims-v3/ccheck/ccheck.py
if [ -n "${E178_CCHECK_STANDIN:-}${E178_DESKTEST_FAIL_REDUCE:-}${E178_DESKTEST_BREAK_JSON:-}" ]; then
  [ "${E178_DESKTEST:-}" = 1 ] || { echo "E178_CCHECK_STANDIN, E178_DESKTEST_FAIL_REDUCE and E178_DESKTEST_BREAK_JSON are desk-test stand-ins, read only with E178_DESKTEST=1: unset them"; exit 10; }
  [ -n "${E178_CCHECK_STANDIN:-}" ] && CCHECK=$E178_CCHECK_STANDIN
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
rm -rf "${TOPD:?}/build/e178-out" "${TOPD:?}/build/e178-dropped-arms"
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
# v2: each arm's name, its file stem (e178-<stem>.json, runs-<stem>.csv, reduce-<stem>.txt, reduce-<stem>.log) and its reduction's exit
an=(); as=(); ar=()
arm_done() {  # arm_done <name> <stem> <rc>: record it; the desk test may break it (E178_DESKTEST=1 only, refused above otherwise)
  an+=("$1"); as+=("$2"); ar+=("$3")
  if [ "${E178_DESKTEST_BREAK_JSON:-}" = "$1" ] && [ "$3" -eq 0 ]; then echo '{"desk_test": "an arm the scorer cannot read"}' > "$OUT/e178-$2.json"; fi
}
dropped=0
drop_arm() {  # drop_arm <name> <stem> <why>: move its four files out of the output; one line in arms-dropped.txt
  local f
  mkdir -p "$DROP/$1"
  for f in "e178-$2.json" "runs-$2.csv" "reduce-$2.txt" "reduce-$2.log"; do [ -e "$OUT/$f" ] && mv "$OUT/$f" "$DROP/$1/"; done
  [ -s "$OUT/arms-dropped.txt" ] || echo "E178 collect_e178_v2.sh: arms dropped (an arm is reported only and no verdict reads it; KIT.md.dated-note-1.md section 4, registered before any datum). Their files are kept on the desk, never committed." > "$OUT/arms-dropped.txt"
  echo "$1: $3" >> "$OUT/arms-dropped.txt"
  echo "arm dropped: $1 ($3)"
  dropped=$((dropped + 1))
}
build_arms() {  # build_arms <names to leave out, space-separated>: ARMS from every arm whose reduction exited 0 and is not left out
  local i
  ARMS=()
  i=0
  while [ "$i" -lt "${#an[@]}" ]; do
    case " $1 " in *" ${an[$i]} "*) ;; *) [ "${ar[$i]}" -eq 0 ] && ARMS+=(--arm "${an[$i]}=$OUT/e178-${as[$i]}.json,$OUT/runs-${as[$i]}.csv") ;; esac
    i=$((i + 1))
  done
}
score() {
  "$PY" -B $E/score_e178.py score --card aifoundry3 --reduction "$OUT/e178.json" --runs-csv "$OUT/runs.csv" --raw "$RAW" \
    --ccheck "$OUT/ccheck/ccheck-all.json" ${ARMS[@]+"${ARMS[@]}"} --json "$OUT/scored.json" --md "$OUT/results.md" > "$OUT/score.log" 2>&1
}
if [ ${#ok[@]} -gt 0 ]; then
  # the desk test's failing reduction: a pass directory the desk test made outside e178/, whose one telemetry line lacks its fields, so
  # reduce_e78.py stops with a Python traceback, as a real failure would
  bad_extra() { if [ "${E178_DESKTEST_FAIL_REDUCE:-}" = "$1" ]; then echo "$RAW/desktest-broken/p17819"; fi; }
  # 2. the registered primary: E171's footing
  "$PY" -B $E/reduce_e178.py "${ok[@]}" --leak "$KF" --no-refit --drop-dips --out "$OUT/e178.json" --csv "$OUT/runs.csv" \
    --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1
  echo "primary rc=$?"; tail -3 "$OUT/reduce.log"
  # 3. the session-own footing, beside
  "$PY" -B $E/reduce_e178.py "${ok[@]}" $(bad_extra session_own) --out "$OUT/e178-session.json" --csv "$OUT/runs-session.csv" \
    --txt "$OUT/reduce-session.txt" > "$OUT/reduce-session.log" 2>&1; r=$?; echo "session-own rc=$r"
  arm_done session_own session "$r"
  # 4. the arms
  "$PY" -B $E/reduce_e178.py "${ok[@]}" $(bad_extra auto_dips_removed) --drop-dips --out "$OUT/e178-auto-nodips.json" \
    --csv "$OUT/runs-auto-nodips.csv" --txt "$OUT/reduce-auto-nodips.txt" > "$OUT/reduce-auto-nodips.log" 2>&1; r=$?
  echo "auto, dips removed rc=$r"; arm_done auto_dips_removed auto-nodips "$r"
  "$PY" -B $E/reduce_e178.py "${ok[@]}" $(bad_extra kfrozen_dips_kept) --leak "$KF" --no-refit --out "$OUT/e178-kfrozen-dips.json" \
    --csv "$OUT/runs-kfrozen-dips.csv" --txt "$OUT/reduce-kfrozen-dips.txt" > "$OUT/reduce-kfrozen-dips.log" 2>&1; r=$?
  echo "k frozen, dips kept rc=$r"; arm_done kfrozen_dips_kept kfrozen-dips "$r"
  for k in 0.1994 0.3803 0; do
    "$PY" -B $E/reduce_e178.py "${ok[@]}" $(bad_extra "leak$k") --leak "$k" --no-refit --drop-dips --out "$OUT/e178-leak$k.json" \
      --csv "$OUT/runs-leak$k.csv" --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; r=$?
    echo "leak-arm $k rc=$r"; arm_done "leak$k" "leak$k" "$r"
  done
  "$PY" -B $E/reduce_e178.py "${ok[@]}" $(bad_extra gates_off) --leak "$KF" --no-refit --drop-dips --gates-off --out "$OUT/e178-gatesoff.json" \
    --csv "$OUT/runs-gatesoff.csv" --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; r=$?
  echo "gates-off arm rc=$r"; arm_done gates_off gatesoff "$r"
  # v2: an arm whose reduction failed is not scored
  i=0
  while [ "$i" -lt "${#an[@]}" ]; do
    [ "${ar[$i]}" -eq 0 ] || drop_arm "${an[$i]}" "${as[$i]}" "its reduction exited ${ar[$i]}"
    i=$((i + 1))
  done
  build_arms ""
  # 5. score: E178.md section 5's rules and A1's E178-S-int8 (the listed sessions' C first)
  score; src=$?
  # v2: an arm the scorer could not read is dropped, and the session scored again without it (once)
  if [ "$src" -eq 0 ]; then
    BAD=$("$PY" -B -c 'import json, sys
a = json.load(open(sys.argv[1])).get("arms", {})
print(" ".join(n + "=" + (str(a[n]["error"]).split(":")[0].split() or ["error"])[0] for n in sorted(a) if "error" in a[n]))' "$OUT/scored.json")
    if [ -n "$BAD" ]; then
      names=""
      for x in $BAD; do
        n=${x%%=*}; names="$names $n"
        i=0
        while [ "$i" -lt "${#an[@]}" ]; do
          [ "${an[$i]}" = "$n" ] && drop_arm "$n" "${as[$i]}" "the scorer could not read it (${x#*=})"
          i=$((i + 1))
        done
      done
      build_arms "$names"
      score; src=$?
      echo "scored again without the dropped arm(s):$names (rc $src)"
    fi
  fi
  if [ "$src" -eq 0 ]; then echo "results.md written"; cat "$OUT/score.log"; else echo "score_e178 rc=$src"; tail -20 "$OUT/score.log"; fi
fi
echo "arms dropped: $dropped"
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
    $E/*.py $E/*.sh $E/*.json $E/*.c $E/E178.md $E/E178.md.dated-note-*.md $E/KIT.md.dated-note-*.md $E/SHA256SUMS-* $E/tiles/*/*.bin ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
