#!/usr/bin/env bash
# E198, box step 9, THE SITTING'S LAUNCH (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): E193's step 9
# (tools/claims-v3/e193/rb/s11_a3_session_e193.sh, unchanged beside it) for aifoundry1 card 1. Its remote script, in order: k6's guard
# text UNCHANGED (no runbook job running, no session of ours on the box, and THE REBOOT GATE: aifoundry1 booted before E82's firmware read
# of 2026-10-31 13:45:24 PDT, else IDENTITY-STOP); THE REST RULE, E191's (tools/claims-v3/e191/rb/rest_rule_e191.sh, unchanged: every
# session-log form of ours on aifoundry1 in every tree of ours, E190 arm B's, E191's and E198's own build/e198/T<T0>/session.log among them;
# at least 40 minutes since the last real session of ours on either card); today's dry pass of this sitting (step 8's job a1-dry-e198-<S>)
# and today's build (step 6's a1-build-e198, X04-BUILT, the record in E198's root); the box's tree files at their pins (harness --tree);
# no second try of a sitting on the day its smoke gate failed (E198.md 13); NO FURTHER SITTING (A or B) after an earlier E198 sitting on
# the box with a watch hit (its holderd/WATCH-STOP, or the session's "the watch: " / WATCH-HIT line) or with a device process that did
# not finish (the runner's "tell the lab admin" stops: an exit 1 or other unexpected status, killed by timeout; three incomplete launches;
# "device process not ended" or "still running" in its logs): a dated note decides first (CARD-LANE-BRIEF.md section 4; added before the
# land and before any datum, Mon 16 Nov 2026, Q191 lane fix-e198: verify-e198's finding 3); for sitting B, a real sitting A on the box
# whose main run started and ended, and none that crashed; then session_e198.sh detached (setsid nohup), DRY unset, with E198_T0, the
# window's last end and harness-e198.json's sha256 from the lab clone. The window's last start and the sitting's cap before its last end
# are read first.
#   RB_OUT=<dir> RB_LOCK=<file> bash tools/claims-v3/e198/rb/s11_a1_session_e198.sh A|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e198.sh"
rb_init s11_a1_session
sit=${1:-}
cap=$(e198_cap_s "$sit") || rb_die $RB_E_USAGE "usage: s11_a1_session_e198.sh A|B (the sitting this RB_OUT's window names)"
e198_window "$sit"
rb_need_start
rb_need_end "$cap"
[ -n "${RB_DRY:-}" ] || e198_built_today || rb_die $RB_E_USAGE "x04clock was not built today (RB_OUT/e198-built.txt, step 6's wait): run step 6 first"
hs=$(e198_harness_sha); [ -n "${RB_DRY:-}" ] && hs=${hs:-HARNESS-SHA256}
[ -n "$hs" ] || rb_die $RB_E_USAGE "harness-e198.json's sha256 could not be read in the lab clone"
f=$(rb_file e198)
{ rb_prelude aifoundry1
  echo "SIT=$sit; ROOT=$E198_ROOT; HSHA=$hs; DEADLINE=${RB_LAST_END_EPOCH:-0}; LAST_START=$(printf '%q' "${RB_LAST_START:-}"); LAST_END=$(printf '%q' "${RB_LAST_END:-}")"
  rb_guard_text
  cat "$RB_E198_DIR/../../e191/rb/rest_rule_e191.sh"
  cat <<'EOF2'
job_ok_today "a1-dry-e198-$SIT" || { echo "REFUSED: E198 sitting $SIT's dry pass (step 8's job a1-dry-e198-$SIT) has not ended rc 0 today"; exit 3; }
echo "dry pass: a1-dry-e198-$SIT ended rc 0 today"
fresh build/q141k/jobs/a1-build-e198.out && grep -q '^X04-BUILT rc=0' build/q141k/jobs/a1-build-e198.out ||
  { echo "REFUSED: x04clock was not built today (step 6's job a1-build-e198)"; exit 3; }
fresh "$ROOT/build/x04clock-built.txt" || { echo "REFUSED: E198's root holds no build record written today"; exit 3; }
echo "build: X04-BUILT today"
python3 -I -B "$ROOT/tools/claims-v3/e198/harness_e198.py" --tree --root "$ROOT" | tail -n 1 | grep '^TREE OK: ' ||
  { echo "REFUSED: the box's tree files (E191's guard, the reader) are not at their pins: run step 5 again"; exit 3; }
today=$(date +%F)
for L in build/e198/T[0-9]*/session.log; do
  [ -f "$L" ] || continue
  case "$L" in *-dry*) continue ;; esac
  grep -q "E198 sitting $SIT" "$L" || continue
  if grep -qE "^$today [0-9]{2}:[0-9]{2}:[0-9]{2} [A-Z]+ GATE-STOP: the smoke gate failed" "$L"; then
    echo "REFUSED: E198 sitting $SIT ended at its smoke gate today (${L%/session.log}): no sitting that day (E198.md 13)"; exit 3
  fi
done
wh=""; dp=""
for L in build/e198/T[0-9]*/session.log; do
  [ -f "$L" ] || continue
  case "$L" in *-dry*) continue ;; esac
  grep -q 'E198 sitting [AB]' "$L" || continue
  d=${L%/session.log}
  if [ -e "$d/holderd/WATCH-STOP" ] || grep -qE 'the watch: |WATCH-HIT' "$L"; then wh=$L; fi
  if grep -qsE 'tell the lab admin|three device processes returned an incomplete launch|device process not ended|device process still running' \
       "$L" "$d/x04/STOPPED" "$d/x04/run.log" "$d/runner.out" "$d/smoke/STOPPED" "$d/smoke/run.log"; then dp=$L; fi
done
[ -z "$wh" ] || { echo "REFUSED: an earlier E198 sitting had a watch hit (a process of the sitting held a card node other than card 1's: ${wh%/session.log}): no further E198 sitting before a dated note (CARD-LANE-BRIEF.md section 4)"; exit 3; }
[ -z "$dp" ] || { echo "REFUSED: an earlier E198 sitting stopped on a device process that did not finish or on three incomplete launches (${dp%/session.log}): the day stops, the owner and the lab admin are told, and no further E198 sitting runs before a dated note (E198.md 9; CARD-LANE-BRIEF.md section 4)"; exit 3; }
if [ "$SIT" = B ]; then
  a=""; cr=""
  for L in build/e198/T[0-9]*/session.log; do
    [ -f "$L" ] || continue
    case "$L" in *-dry*) continue ;; esac
    grep -q 'E198 sitting A' "$L" && grep -q 'main run start' "$L" && grep -q 'session end' "$L" || continue
    if grep -q 'main run ended without a registered stop' "$L"; then cr=$L; else a=$L; fi
  done
  [ -z "$cr" ] || { echo "REFUSED: E198 sitting A's main run ended without a registered stop (a crash: ${cr%/session.log}): no further sitting before a dated note decides whether its passes are reduced (CARD-LANE-BRIEF.md section 3)"; exit 3; }
  [ -n "$a" ] || { echo "REFUSED: no E198 sitting A on this box whose main run started and ended: B never runs before A (E198.md 11)"; exit 3; }
  echo "sitting A held first: ${a%/session.log}"
fi
mkdir -p build/e198 build/q141k
T0=$(date +%s)
echo "$T0" > "build/q141k/e198-$SIT.T0"
env -u DRY E198_T0="$T0" E198_LAST_END_EPOCH="$DEADLINE" E198_HARNESS_SHA256="$HSHA" setsid nohup bash "$ROOT/tools/claims-v3/e198/session_e198.sh" "$SIT" > "build/q141k/e198-$SIT-T$T0.out" 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e198-$SIT T0 $T0 $(date '+%F %T %Z') (sitting $SIT; last start $LAST_START, last end $LAST_END)"
tail -n 6 "build/e198/T$T0/session.log" 2>/dev/null | cut -c1-300
EOF2
} > "$f"
rb_probe aifoundry1
rb_remote launch aifoundry1 "launch E198 sitting $sit, detached" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched "e198-$sit"
rb_has '^rest: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^rest: ' "$RB_CAP")" >> "$RB_LOG"
rb_has '^note: ' && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^note: ' "$RB_CAP")" >> "$RB_LOG"
t0=$(rb_val "^LAUNCHED e198-$sit T0 ([0-9]+) .*\$")
[ -n "$t0" ] && echo "$t0" > "$RB_OUT/e198-$sit-T0.txt"
rb_say "E198 sitting $sit launched on aifoundry1 (T0 $t0); wait with s20_wait_e198.sh $sit (bounded)"
