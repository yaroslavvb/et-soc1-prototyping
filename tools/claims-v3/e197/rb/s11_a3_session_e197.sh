#!/usr/bin/env bash
# E197 (Q185, the kit), the box step "the sitting" (this file is s11), ONE SITTING A CALL: E197's sitting on aifoundry3 card 0, launched
# detached on the box (it returns at once), right after step 7's reads (the sitting's first card command, stamped by step 7's wrapper).
# E193's step 9's form (tools/claims-v3/e193/rb/s11_a3_session_e193.sh):
#   - at the desk: the window rule (written today for E197 and this sitting); today's build (RB_OUT/e197-built.txt) and today's dry pass
#     for this sitting (RB_OUT/e197-<n>-dry-ok.txt); THE FIRST CARD COMMAND from RB_OUT/e197-<n>-first.txt (step 7's wrapper: FIRST and
#     the PLAN decided there), written today, at most 120 s ago (E197_FIRST_MAX_S; else 16: its cap counts from it), and the plan's cap from it
#     before the window's last end (else 16);
#   - on the box: k6's guard (no dry pass running, no card session of ours: rb_guard_text), THE REST RULE again (rb/rest_rule_e197.sh;
#     it held at the first card command, step 7), today's dry pass for this sitting (a3-dry-e197-<n> ended rc 0 today), today's build
#     (REGFILE-BUILT in a3-build-e197's output today and E197's root's build/regfile-built.txt written today), NO SECOND TRY OF A
#     SITTING ON THE DAY ITS SMOKE FAILED (a real E197 log of this sitting today reading "the runner's smoke gate: failed" or "the kit's
#     smoke check: FAILED": the kit's reading of E197.md 11, KIT.md 4), and for sitting 2, SITTING 1 HELD FIRST (a real sitting-1 log
#     whose SITTING-RESULT reads smoke passed, at least one train block complete, no card stop: E197.md 6) AND NO CRASHED SITTING 1;
#   - then session_e197.sh detached, DRY unset, with E197_T0, E197_SIT, E197_PLAN, E197_FIRST, the window's last end and
#     harness-e197.json's sha256 from the lab clone; the T0 written on the box (build/q141k/e197-<n>.T0) and in RB_OUT (e197-<n>-T0.txt),
#     which steps 10 and 11 read.
#   bash tools/claims-v3/e197/rb/s11_a3_session_e197.sh 1|2
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e197.sh"
rb_init s11_a3_session
sit=${1:-}
e197_sit_ok "$sit" || rb_die $RB_E_USAGE "usage: s11_a3_session_e197.sh 1|2 (the sitting this RB_OUT's window names)"
e197_window "$sit"
[ -n "${RB_DRY:-}" ] || e197_built_today || rb_die $RB_E_USAGE "regfile was not built today (RB_OUT/e197-built.txt, step 6's wait): run step 6 first"
[ -n "${RB_DRY:-}" ] || [ -f "$RB_OUT/e197-$sit-dry-ok.txt" ] || rb_die $RB_E_USAGE "no dry pass ended rc 0 today for sitting $sit in this RB_OUT: run step 8 first"
if [ -n "${RB_DRY:-}" ]; then
  echo "--- gate: <RB_OUT>/e197-$sit-first.txt (step 7's wrapper) written today: FIRST at most $E197_FIRST_MAX_S s ago, the PLAN's cap from FIRST before the last end"
  first=1794800000; plan=full; [ "$sit" = 2 ] && plan=ext; cap=$(e197_cap_s "$plan")
else
  E197_SIT=$sit
  e197_first || rb_die $RB_E_USAGE "RB_OUT holds no readable e197-$sit-first.txt: run step 7 (s09_a3_reads_e197.sh $sit) first"
  first=$E197_FIRST; plan=$E197_PLAN_CHOSEN; cap=$(e197_cap_s "$plan")
  case "$sit:$plan" in 1:full|1:short|2:ext) ;; *) rb_die $RB_E_USAGE "sitting $sit with plan $plan: refused" ;; esac
  [ "$(TZ=America/Los_Angeles e197_fmt "$first" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_GATE "the first card command was not today: no sitting"
  now=$(date +%s)
  [ $((now - first)) -le "$E197_FIRST_MAX_S" ] || rb_die $RB_E_GATE "the first card command (step 7) was $((now - first)) s ago, more than $E197_FIRST_MAX_S s: its cap counts from it; no sitting $sit on this RB_OUT today (a new try needs its own RB_OUT and step 7)"
  [ $((first + cap)) -le "$RB_LAST_END_EPOCH" ] || rb_die $RB_E_GATE "the plan's cap ($cap s from the first card command) passes the window's last end: no sitting"
fi
hs=$(e197_harness_sha); [ -n "${RB_DRY:-}" ] && hs=${hs:-HARNESS-SHA256}
[ -n "$hs" ] || rb_die $RB_E_USAGE "harness-e197.json's sha256 could not be read in the lab clone"
f=$(rb_file e197)
{ rb_prelude aifoundry3
  echo "SIT=$sit; PLAN=$plan; FIRST=$first; ROOT=$E197_ROOT; HSHA=$hs; LAST_END_EPOCH=${RB_LAST_END_EPOCH:-0}; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E197_DIR/rest_rule_e197.sh"
  cat <<'EOF2'
job_ok_today "a3-dry-e197-$SIT" || { echo "REFUSED: E197 sitting $SIT's dry pass (step 8's job a3-dry-e197-$SIT) has not ended rc 0 today"; exit 3; }
echo "dry pass: a3-dry-e197-$SIT ended rc 0 today"
fresh build/q141k/jobs/a3-build-e197.out && grep -q '^REGFILE-BUILT rc=0' build/q141k/jobs/a3-build-e197.out ||
  { echo "REFUSED: regfile was not built today (step 6's job a3-build-e197)"; exit 3; }
fresh "$ROOT/build/regfile-built.txt" || { echo "REFUSED: E197's root holds no build record written today"; exit 3; }
echo "build: REGFILE-BUILT today"
today=$(date +%F)
for L in build/e197/T[0-9]*/session.log; do
  [ -f "$L" ] || continue
  case "$L" in *-dry*) continue ;; esac
  grep -q "E197 sitting $SIT," "$L" || continue
  if grep -qE "^$today [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ (the runner's smoke gate: failed|the kit's smoke check: FAILED)" "$L"; then
    echo "REFUSED: E197 sitting $SIT's smoke failed today (${L%/session.log}): no second try that day (KIT.md 4)"; exit 3
  fi
done
if [ "$SIT" = 2 ]; then
  a=""; cr=""; why=""
  for L in build/e197/T[0-9]*/session.log; do
    [ -f "$L" ] || continue
    case "$L" in *-dry*) continue ;; esac
    grep -q 'E197 sitting 1,' "$L" && grep -q 'session end' "$L" || continue
    if grep -q 'the trains ended without a registered stop' "$L"; then cr=$L; continue; fi
    r=$(grep -m1 'SITTING-RESULT: ' "$L" | sed 's/.*SITTING-RESULT: //')
    case "$r" in "smoke passed; train blocks complete "[1-9]*"card stop none") a=$L ;; *) why="$why ${L%/session.log}: ${r:-no SITTING-RESULT}" ;; esac
  done
  [ -z "$cr" ] || { echo "REFUSED: E197 sitting 1 ended without a registered stop (a crash: ${cr%/session.log}): no sitting 2 before a dated note decides"; exit 3; }
  [ -n "$a" ] || { echo "REFUSED: no E197 sitting 1 on this box that ran its smoke and at least one train block with no stop naming the card (E197.md 6:${why:- none found}): sitting 2 needs a dated amendment"; exit 3; }
  echo "sitting 1 held first: ${a%/session.log}"
fi
mkdir -p build/e197 build/q141k
T0=$(date +%s)
echo "$T0" > "build/q141k/e197-$SIT.T0"
env -u DRY E197_T0="$T0" E197_SIT="$SIT" E197_PLAN="$PLAN" E197_FIRST="$FIRST" E197_LAST_END_EPOCH="$LAST_END_EPOCH" E197_HARNESS_SHA256="$HSHA" \
  setsid nohup bash "$ROOT/tools/claims-v3/e197/session_e197.sh" > "build/q141k/e197-$SIT-T$T0.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e197-$SIT T0 $T0 $(date '+%F %T %Z') (sitting $SIT, plan $PLAN; first card command $FIRST; last start $LAST_START, last end $LAST_END)"
tail -n 6 "build/e197/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote launch aifoundry3 "launch E197 sitting $sit, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched "e197-$sit"
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
t0=$(rb_val "^LAUNCHED e197-$sit T0 ([0-9]+) .*\$")
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e197-$sit-T0.txt"
rb_say "E197 sitting $sit launched on aifoundry3 (T0 $t0, plan $plan); wait with s20_wait_e197.sh $sit (bounded)"
