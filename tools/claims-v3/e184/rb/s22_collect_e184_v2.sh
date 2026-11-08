#!/usr/bin/env bash
# E184 (Q154), kit note 2 (../KIT.md.dated-note-2.md section 3), step 11 v2: s22_collect_e184.sh (v1, which stays as committed) with kit note 2's
# collector, ../collect_e184_v2.sh (reduce_e184_v3.py: A3-3's session gate, which replaces a missing session config read by step 7's read,
# copied back here with the session's own files; score_e184_v3.py: the governing reading at the top level, A2-4's filter on E184-C), its
# success line "scored-e184-v3.md written", and nothing else changed. v1's words follow:
# E184 (Q153), kit note 1 (../KIT.md.dated-note-1.md sections 2 and 3), step 11: collect and score an arm at the desk, on the Intel (it needs this
# Mac's tree and its ssh to the box), at nice 10, every copy bounded, after the run has ended (s20_wait_e184.sh read this T0's session end) and
# after the post's release. ../../e180/rb/s22_collect_e180_v2.sh's form, for either box, with the exact copy-back the verifier asked for (its
# fault 4): the arm's passes, smoke and stop-path test land at build/e184-raw/<card>/ (aifoundry3 or aifoundry1-c1: the level reduce_e184_v2.py
# reads), the box's build/e184/ (the session's own files, named by T0; the operand images left out) at build/e184-raw/<card>/logs/, and the
# collector is given the T0 step 9 recorded ($RB_OUT/t0-<arm>.txt), so it reads that session's log and config reads and no other. Then the
# stop-path test's no-launch check, the collector (../collect_e184.sh), the desk-path gate, and the login check over every directory of the
# output (../../e178/scrub_tree_e178.py --check, unchanged), LAST. The desk test's stand-in collector (K6E184_COLLECT) is read only with
# RB_DESKTEST=1. This step commits nothing; the data directory is docs/reports/data/<day>-e184-sensor-validation/, after a data verifier.
#
#   bash tools/claims-v3/e184/rb/s22_collect_e184_v2.sh S|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e184.sh"
rb_init s22_collect
e184_arm "${1:-}" || rb_die $RB_E_USAGE "usage: s22_collect_e184_v2.sh S|B"
rb_window
DAY=$RB_DAY
OUT=build/e184-out/$DAY-e184-sensor-validation
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${K6E184_COLLECT:-}" ]; then
  rb_die $RB_E_USAGE "K6E184_COLLECT is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
fi
COL=${K6E184_COLLECT:-tools/claims-v3/e184/collect_e184_v2.sh}
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
rb_local copy "$E184_BOX" "copy back the arm's passes, smoke and stop-path test into build/e184-raw/$E184_CARD/" \
  rsync -a -e "$RB_RSH" "$E184_BOX:$E184_TREE/build/claims-v3/$E184_CARD/e184" "$E184_BOX:$E184_TREE/build/claims-v3/$E184_CARD/e184-smoke" \
  "$E184_BOX:$E184_TREE/build/claims-v3/$E184_CARD/e184-stoptest" "$RAW/$E184_CARD/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
rb_local copy "$E184_BOX" "copy back the session's own files (build/e184/, named by T0; not the operand images)" \
  rsync -a --exclude images -e "$RB_RSH" "$E184_BOX:$E184_TREE/build/e184/" "$RAW/$E184_CARD/logs/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the logs' copy exited non-zero"
if [ -z "${RB_DRY:-}" ]; then
  for f in "$RAW/$E184_CARD"/e184-stoptest/p*/runs.jsonl "$RAW/$E184_CARD"/e184-stoptest/p*/runs.jsonl.gz; do
    [ -s "$f" ] && rb_die $RB_E_FAIL "STOPTEST-LAUNCHED: the stop-path test recorded a launch ($f): nothing is scored as registered"
  done
  [ -s "$RAW/$E184_CARD/logs/session-$E184_ARM-t$T0.log" ] || rb_die $RB_E_FAIL "the copy holds no session-$E184_ARM-t$T0.log: the session step 9 launched is not in it"
fi
rb_local desk local "collect_e184_v2.sh (reduce_e184_v3.py, score_e184_v3.py) for T0 $T0" env PY=/usr/bin/python3 E184_DATE="$DAY" "E184_T0_$E184_ARM=$T0" \
  nice -n 10 bash "$COL" "$RAW"
rb_has '^scored-e184-v3\.md written' || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_e184_v3 did not write scored-e184-v3.md: read the collector's output above"
rb_nopath "$OUT"
scrub_tree "$OUT" "$E184_BOX"
rb_say "E184 arm $E184_ARM collected and scored (kit note 2: reduce v3, score v3): $OUT (the data directory is docs/reports/data/$DAY-e184-sensor-validation/)"
