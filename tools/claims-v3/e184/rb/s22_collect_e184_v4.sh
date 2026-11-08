#!/usr/bin/env bash
# E184 (Q156), kit note 4 (../KIT.md.dated-note-4.md section 1), step 11 v4: s22_collect_e184_v3.sh (v3, which stays as committed) for a
# session its smoke gate stopped (E184.md.dated-note-A3.md, A3-1), the data verifier's fault 3 of Sun 8 Nov 2026: v3's first copy names the
# arm's three pass directories, e184, e184-smoke and e184-stoptest, and only the queue makes e184, so on arm S's gate-stopped session of that
# day rsync exited 23 and the step stopped (14) before the session's own files, the collector and the gates. Two changes, nothing else:
#   - the session's own files (the box's build/e184/, named by T0; the operand images left out) are copied FIRST, and this T0's log is
#     checked there before any pass directory is copied (v3 checked it after both copies; the same words and the same 14);
#   - the pass directories copied are the ones this T0's own log says the session made: all three, exactly v3's copy, unless the log
#     holds the session's gate-stop line, "smoke gate failed (stop test rc N, smoke rc N, gate N): no pass runs" (e184-smoke and
#     e184-stoptest, no e184), or "stop-path test failed: no smoke, no pass" (e184-stoptest alone). So a session that ran its queue is
#     copied, and stops at a missing directory, exactly as under v3, and a pass directory of another session on the box is never copied
#     beside a gate-stopped one.
# The collector (../collect_e184_v3.sh: reduce_e184_v4.py with A4, score_e184_v3.py), its success line, the stop-path test's no-launch
# check, the desk-path gate, the login check LAST and the desk-test stand-in rule (K6E184_COLLECT read only with RB_DESKTEST=1) are v3's,
# unchanged. A gate-stopped session reads NOT SCORED at the reducer's session gate (its log has no "smoke gate passed" line), as A3-1 has it:
# "E184 arm S not run", never a verdict. v3's words follow:
# E184 (Q155), kit note 3 (../KIT.md.dated-note-3.md section 3), step 11 v3: s22_collect_e184_v2.sh (v2, which stays as committed) with kit
# note 3's collector, ../collect_e184_v3.sh (reduce_e184_v4.py: A3-3's session gate with dated amendment A4, which tests the config reads'
# keys, not their truthiness; score_e184_v3.py, unchanged), and nothing else changed: the same copy-back (the arm's passes, smoke and
# stop-path test; the box's build/e184/ with the session's own files and step 7's reads, the operand images left out), the same gates
# (the stop-path test's no-launch check, the session log for the recorded T0, the success line "scored-e184-v3.md written", the desk-path
# gate, the login check LAST), and the same desk-test stand-in rule (K6E184_COLLECT read only with RB_DESKTEST=1). This step commits
# nothing; the data directory is docs/reports/data/<day>-e184-sensor-validation/, after a data verifier.
#
#   bash tools/claims-v3/e184/rb/s22_collect_e184_v4.sh S|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e184.sh"
rb_init s22_collect
e184_arm "${1:-}" || rb_die $RB_E_USAGE "usage: s22_collect_e184_v4.sh S|B"
rb_window
DAY=$RB_DAY
OUT=build/e184-out/$DAY-e184-sensor-validation
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${K6E184_COLLECT:-}" ]; then
  rb_die $RB_E_USAGE "K6E184_COLLECT is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
fi
COL=${K6E184_COLLECT:-tools/claims-v3/e184/collect_e184_v3.sh}
T0=$(cat "$RB_OUT/t0-$E184_ARM.txt" 2>/dev/null)
[ -n "$T0" ] || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_USAGE "no T0 recorded by step 9 ($RB_OUT/t0-$E184_ARM.txt): collect only a session this runbook launched"
T0=${T0:-T0}
scrub_tree() {  # scrub_tree <output dir> <box>: every directory of the output, --check only (it rewrites nothing)
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  [ -n "$own" ] || rb_say "no box login recorded by s05_look_k6.sh: every login in $d counts as another account's"
  rb_local read local "another account's login or uid in any directory of $d (scrub_tree_e178.py --check)" \
    "$RB_PY" -B tools/claims-v3/e178/scrub_tree_e178.py --check "$d" ${own:+--owner "$own"}
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another account's login or uid is left in $d (the scrub-tree lines above). Every other gate has passed. Before any commit: python3 -B tools/claims-v3/e178/scrub_tree_e178.py $d${own:+ --owner $own} (it rewrites those lines in place), then the same with --check (0 left), and name it in the data README"
}
RAW=build/e184-raw
[ -n "${RB_DRY:-}" ] || mkdir -p "$RAW/$E184_CARD/logs"
rb_probe "$E184_BOX"
# v4: the session's own files first, so this T0's log can say which pass directories the session made
rb_local copy "$E184_BOX" "copy back the session's own files (build/e184/, named by T0; not the operand images), first (v4)" \
  rsync -a --exclude images -e "$RB_RSH" "$E184_BOX:$E184_TREE/build/e184/" "$RAW/$E184_CARD/logs/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the logs' copy exited non-zero"
SL=$RAW/$E184_CARD/logs/session-$E184_ARM-t$T0.log
PASSES="e184 e184-smoke e184-stoptest"
GSTOP=""
if [ -z "${RB_DRY:-}" ]; then
  [ -s "$SL" ] || rb_die $RB_E_FAIL "the copy holds no session-$E184_ARM-t$T0.log: the session step 9 launched is not in it"
  if grep -qE ' stop-path test failed: no smoke, no pass$' "$SL"; then
    PASSES="e184-stoptest"; GSTOP=$(grep -m1 -oE 'stop-path test failed: no smoke, no pass$' "$SL")
  elif grep -qE ' smoke gate failed \(stop test rc [0-9]+, smoke rc [0-9]+, gate [0-9]+\): no pass runs$' "$SL"; then
    PASSES="e184-smoke e184-stoptest"; GSTOP=$(grep -m1 -oE 'smoke gate failed \(stop test rc [0-9]+, smoke rc [0-9]+, gate [0-9]+\): no pass runs$' "$SL")
  fi
  [ -n "$GSTOP" ] && rb_say "this T0's log holds the session's gate stop ('$GSTOP'): no pass ran, so the copy names $PASSES (kit note 4)"
else
  echo "--- v4: the pass directories copied are this T0's log's: all three (v3's copy) unless the log holds 'smoke gate failed (...): no pass runs' (e184-smoke and e184-stoptest) or 'stop-path test failed: no smoke, no pass' (e184-stoptest)"
fi
SRCS=()
for d in $PASSES; do SRCS+=("$E184_BOX:$E184_TREE/build/claims-v3/$E184_CARD/$d"); done
rb_local copy "$E184_BOX" "copy back the pass directories this T0's log says the session made ($PASSES) into build/e184-raw/$E184_CARD/" \
  rsync -a -e "$RB_RSH" "${SRCS[@]}" "$RAW/$E184_CARD/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
if [ -z "${RB_DRY:-}" ]; then
  for f in "$RAW/$E184_CARD"/e184-stoptest/p*/runs.jsonl "$RAW/$E184_CARD"/e184-stoptest/p*/runs.jsonl.gz; do
    [ -s "$f" ] && rb_die $RB_E_FAIL "STOPTEST-LAUNCHED: the stop-path test recorded a launch ($f): nothing is scored as registered"
  done
fi
rb_local desk local "collect_e184_v3.sh (reduce_e184_v4.py with A4, score_e184_v3.py) for T0 $T0" env PY=/usr/bin/python3 E184_DATE="$DAY" "E184_T0_$E184_ARM=$T0" \
  nice -n 10 bash "$COL" "$RAW"
rb_has '^scored-e184-v3\.md written' || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_e184_v3 did not write scored-e184-v3.md: read the collector's output above"
rb_nopath "$OUT"
scrub_tree "$OUT" "$E184_BOX"
[ -n "$GSTOP" ] && rb_say "a gate-stopped session: by A3-1 no rule of arm $E184_ARM has a reading; its scored file reads the reducer's session gate (NOT SCORED)"
rb_say "E184 arm $E184_ARM collected and scored (kit note 4: step 11 v4, the copy by this T0's log; reduce v4 with A4, score v3): $OUT (the data directory is docs/reports/data/$DAY-e184-sensor-validation/)"
